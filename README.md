# PDF Brain 🧠 — Production-Ready RAG Document Q&A

PDF Brain is a high-performance RAG (Retrieval-Augmented Generation) application that allows users to upload PDF documents and have laser-focused conversations with them. 

Unlike basic RAG apps, this system uses **local offline embeddings** and **cross-encoder reranking** to ensure zero rate limits and industry-leading accuracy.

---

## 🚀 Key Features

- **Local Embeddings (Offline):** Uses `all-MiniLM-L6-v2` locally via `sentence-transformers`. No Google Gemini API rate limits or costs for embeddings.
- **Cross-Encoder Reranking:** Implements `ms-marco-MiniLM-L-6-v2` to double-check search results, ensuring the AI only sees the absolute most relevant context.
- **Multi-User Session Support:** Every upload generates a unique UUID session, allowing multiple users to chat with different documents simultaneously without data collisions.
- **FastAPI + React (Vite) Architecture:** Modern, decoupled full-stack architecture for production speed and scalability.
- **Groq LLM Acceleration:** Powered by Llama 3.3 70B via Groq for near-instant responses.

---

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI, Uvicorn
- **Frontend:** React, TypeScript, Vite, Axios
- **Vector DB:** FAISS (Facebook AI Similarity Search)
- **Embeddings:** Sentence-Transformers (Local/Offline)
- **Reranker:** Cross-Encoder (Local/Offline)
- **LLM:** Groq (Llama 3.3 70B)
- **Styling:** CSS3 with Dark/Light mode support & animations

---

## 📂 Project Structure

```
rag-document-qa/
├── backend/
│   ├── storage/             # FAISS indices and chunk pickles
│   ├── uploads/             # Temporarily stored PDF files
│   ├── api.py               # FastAPI server & endpoints
│   ├── local_embedder.py    # Singleton for local embedding model
│   ├── local_reranker.py    # Singleton for cross-encoder reranker
│   ├── embedding_generator.py
│   ├── query_handler.py     # Search logic with reranking
│   ├── LLM_handler.py       # Groq integration
│   ├── pdf_loader.py
│   ├── text_chunker.py
│   └── vector_store.py
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main React application
│   │   ├── App.css          # Premium styling & dark mode
│   │   └── main.tsx
│   └── vite.config.ts
├── .env                     # Your GROQ_API_KEY
└── requirements.txt         # Python dependencies
```

---

## ⚙️ Setup — Step by Step

### 1. Clone & Environment
```bash
git clone https://github.com/yourusername/rag-document-qa.git
cd rag-document-qa
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
cd frontend && npm install
```

### 3. Configure Environment
Create a `.env` file in the **root** directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```
Get your free key at [Groq Cloud Console](https://console.groq.com/).

### 4. Run the App
**Start Backend:**
```bash
cd backend
python api.py
```

**Start Frontend:**
```bash
cd frontend
npm run dev
```

---

## 🧠 How the RAG Pipeline Works

1. **PDF Upload:** Generates a unique UUID and extracts text.
2. **Chunking:** Splits text into semantic chunks (500 chars).
3. **Local Embedding:** Encodes chunks using `all-MiniLM-L6-v2` on your CPU.
4. **Storage:** Saves the vector index to `storage/indices/{uuid}.faiss`.
5. **Retrieval:** 
   - **FAISS Search:** Grabs top 10 similar chunks.
   - **Reranking:** Cross-Encoder re-scores those 10 chunks against the user question.
   - **Top-K:** Sends only the top 2 absolute most relevant chunks to the LLM.
6. **Generation:** Llama 3.3 70B generates a concise (1-2 sentence) answer strictly based on the context.

---

## 📝 Author
Built by Wasay — learning Production-Grade Gen AI development.