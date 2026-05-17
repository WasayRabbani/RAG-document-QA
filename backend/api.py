import os
import shutil
import logging
import uuid
import hashlib
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pdf_loader import PDFLoader
from text_chunker import TextChunker
from embedding_generator import EmbeddingGenerator
from vector_store import VectorStore
from query_handler import QueryHandler
from LLM_handler import LLMHandler

# --- LOGGING CONFIG ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Document QA API", version="1.0.0")

# --- CORS SETTINGS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- PATH CONFIGURATION ---
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
STORAGE_DIR = BASE_DIR / "storage"
INDICES_DIR = STORAGE_DIR / "indices"
CHUNKS_DIR = STORAGE_DIR / "chunks"

# Create directories if they don't exist
for folder in [UPLOAD_DIR, INDICES_DIR, CHUNKS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

class QueryRequest(BaseModel):
    session_id: str = Field(default="", description="Single session ID (backward compatible)")
    session_ids: list[str] = Field(default=[], description="List of session IDs for multi-PDF mode")
    question: str = Field(..., min_length=1, description="The user's question")

@app.get("/health")
async def health_check():
    """Endpoint to verify the API is running."""
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Uploads a PDF, generates a content-based ID, and skips processing if already cached."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    # Read file content to generate a hash (fingerprint)
    content = await file.read()
    session_id = hashlib.md5(content).hexdigest()
    
    # Reset file pointer for shutil
    await file.seek(0)
    
    index_file = INDICES_DIR / f"{session_id}.faiss"
    chunks_file = CHUNKS_DIR / f"{session_id}.pkl"
    
    # --- SMART CACHE CHECK ---
    if index_file.exists() and chunks_file.exists():
        logger.info(f"File '{file.filename}' (Hash: {session_id}) found in cache. Skipping processing.")
        return {
            "filename": file.filename, 
            "session_id": session_id, 
            "status": "cached"
        }
    
    # Not in cache, proceed with processing
    safe_filename = f"{session_id[:8]}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename
    
    try:
        # Save uploaded file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Processing NEW PDF: '{file.filename}' (Session: {session_id})")
        
        # 1. Load and parse PDF
        pdf_data = PDFLoader(str(file_path)).load_pdf()
        
        # 2. Split into chunks
        chunks = TextChunker(pdf_data).chunking()
        
        # 3. Generate embeddings and save to FAISS
        embeddings = await EmbeddingGenerator(chunks).embed_text()
        stored_vector = VectorStore(vectors=embeddings, chunks=chunks)
        whole_index = stored_vector.making_faiss()
        stored_vector.save_to_disk(whole_index, str(index_file), str(chunks_file))
            
        return {
            "filename": file.filename, 
            "session_id": session_id, 
            "status": "processed"
        }
    
    except Exception as e:
        logger.error(f"Failed to process upload: {e}")
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/chat")
async def chat(request: QueryRequest):
    """Answers a question by searching across one or more uploaded PDFs."""
    
    # Build list of session IDs (support both single and multi mode)
    ids = request.session_ids if request.session_ids else [request.session_id]
    ids = [sid for sid in ids if sid]  # Remove empty strings
    
    if not ids:
        raise HTTPException(status_code=400, detail="No session IDs provided.")
    
    # Collect chunks from ALL documents
    all_chunks = []
    all_indices = []
    
    for sid in ids:
        index_file = str(INDICES_DIR / f"{sid}.faiss")
        chunks_file = str(CHUNKS_DIR / f"{sid}.pkl")
        
        whole_index, chunks = VectorStore.load_from_disk(index_file, chunks_file)
        
        if whole_index is not None:
            all_indices.append((whole_index, chunks))
        else:
            logger.warning(f"Session {sid} not found, skipping.")
    
    if not all_indices:
        raise HTTPException(status_code=404, detail="No valid document sessions found.")
    
    try:
        # Search each index separately and collect all candidate chunks
        all_candidates = []
        
        for whole_index, chunks in all_indices:
            qh = QueryHandler(
                question=request.question,
                container=whole_index,
                chunks=chunks,
                threshold=2.0
            )
            results = qh.get_results()
            all_candidates.extend(results)
        
        if not all_candidates:
            return {"answer": "I don't know based on the provided documents.", "sources": []}
        
        # If multi-PDF: re-sort all candidates by rerank score globally
        if len(all_indices) > 1:
            all_candidates.sort(key=lambda x: x.get('rerank_score', 0), reverse=True)
            all_candidates = all_candidates[:3]  # Keep top 3 globally
        
        # Generate final answer with LLM
        llm = LLMHandler(question=request.question, chunks=all_candidates)
        answer = llm.make_chatbot()
        
        # Extract source pages
        sources = sorted(list(set([chunk['page'] for chunk in all_candidates])))
        
        return {"answer": answer, "sources": sources}
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

