---
title: PDF Brain
sdk: docker
app_port: 7860
---

# PDF Brain

**Ask questions across your PDFs and get concise answers grounded in the documents, with page references.**

PDF Brain is a full-stack Retrieval-Augmented Generation (RAG) application. It turns uploaded PDFs into searchable, page-aware content, retrieves relevant passages for a question, and uses a language model to compose an answer from that evidence.

## Project highlights

- Built an end-to-end document question-answering application with a React/TypeScript frontend and a Python/FastAPI backend.
- Designed a PDF ingestion pipeline that combines `pypdf` text extraction with conditional `pdfplumber` table extraction, repairs selected technical notation, and preserves page metadata.
- Implemented parent/child chunking, local text embeddings, FAISS vector search, BM25 keyword retrieval, and local cross-encoder reranking.
- Added content-based document caching and multi-document chat so previously indexed PDFs can be reused and questions can search across the currently selected documents.
- Integrated Groq-hosted LLM calls for query expansion and grounded answer generation.

## How it works

```text
Upload PDF
   │
   ├─ Check content/model cache
   │
   └─ If not cached:
       Extract page text ──> Detect likely table pages ──> Format table rows
              │
              ▼
       Split into searchable chunks ──> Create local embeddings
              │
              ▼
       Save FAISS index and chunk metadata

Ask a question
   │
   ├─ Expand the question with a hypothetical answer (HyDE, via Groq)
   ├─ Retrieve semantic matches (FAISS) and keyword matches (BM25)
   ├─ Deduplicate and rerank candidates locally (FlashRank)
   └─ Generate a concise answer from retrieved context (via Groq)
         └─ Return source page numbers to the UI
```

### 1. PDF ingestion and indexing

The `/upload` API accepts PDF uploads. It computes a cache identifier from the PDF contents and embedding-model name. When matching index and chunk files already exist, it reuses them instead of repeating extraction, chunking, and embedding. A cache hit still requires uploading and reading the file to calculate that identifier.

For new documents:

1. [`backend/ingestion/pdf_loader.py`](./backend/ingestion/pdf_loader.py) extracts page text with `pypdf`. It normalizes selected punctuation and attempts to repair certain broken scientific-notation patterns.
2. Pages that appear likely to contain tables—based on text markers or a numeric-character threshold—are additionally processed with `pdfplumber`. Extracted rows are formatted with their headers and marked as `[TABLE ROW]`.
3. [`backend/ingestion/text_chunker.py`](./backend/ingestion/text_chunker.py) preserves each marked table row as a separate chunk. Other page text is split into parent chunks of 2,000 characters with 200-character overlap, and child chunks of 500 characters with 50-character overlap. A short prefix from the parent is added to child search text to provide context.
4. [`backend/retrieval/embedding_generator.py`](./backend/retrieval/embedding_generator.py) creates embeddings for searchable chunk text with the local FastEmbed model `BAAI/bge-small-en-v1.5`.
5. [`backend/retrieval/vector_store.py`](./backend/retrieval/vector_store.py) builds a FAISS L2 index and saves it alongside the chunk metadata for later searches.

### 2. Retrieval and answer generation

When a user asks a question, the backend searches the selected document sessions:

1. **Query expansion:** Groq generates a hypothetical answer (HyDE) to help find semantically relevant document passages. If this expansion call fails, retrieval falls back to the original question.
2. **Candidate retrieval:** FAISS returns up to 20 semantic candidates per document, subject to a configured distance threshold. BM25 contributes up to 20 positive-scoring keyword candidates per document.
3. **Reranking:** Duplicate candidates are removed and FlashRank's `ms-marco-TinyBERT-L-2-v2` model reranks the candidates against the original question. The backend keeps up to three results per document, then selects up to three across the selected documents.
4. **Grounded response:** The Groq-hosted model receives the retrieved parent context (or table-row text) and is instructed to answer concisely from that context. The API returns the answer and source page numbers.

The embeddings, FAISS search, and reranking run locally. HyDE and final answer generation require a connection to Groq.

## User experience

- Upload PDF documents and add multiple documents to the current chat.
- Ask questions across the currently loaded document set.
- See page-number sources alongside answers.
- Remove documents from the current UI session and switch between light and dark themes.
- Receive upload and chat errors through the interface.

The document list and chat history are held in frontend memory; they are not restored after a browser refresh. Removing a document from the UI does not delete its backend files or cached index.

## Technology

| Area | Tools |
| --- | --- |
| Frontend | React 19, TypeScript, Vite, Axios, custom CSS |
| API and orchestration | Python 3.10+, FastAPI, Uvicorn |
| PDF processing | `pypdf`, `pdfplumber` |
| Chunking | LangChain text splitters |
| Embeddings | FastEmbed, `BAAI/bge-small-en-v1.5` |
| Vector search | FAISS |
| Keyword retrieval | BM25 (`rank-bm25`) |
| Reranking | FlashRank, `ms-marco-TinyBERT-L-2-v2` |
| Answer generation | Groq API, default model `openai/gpt-oss-20b` |

## Run locally

### Prerequisites

- Python 3.10 or newer
- Node.js 18 or newer
- A Groq API key

### Configure and install

From the repository root, create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
# Optional; defaults to openai/gpt-oss-20b
GROQ_MODEL=openai/gpt-oss-20b
```

Install backend dependencies in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Install frontend dependencies:

```bash
cd frontend
npm install
```

### Start the application

Start the API from the backend directory:

```bash
cd backend
python api.py
```

The API runs at `http://localhost:8000`. In a separate terminal, start the frontend:

```bash
cd frontend
npm run dev
```

Vite prints the local frontend URL when it starts. To use a non-default API address, configure `VITE_API_URL` for the frontend build/runtime.

## API overview

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Check API health. |
| `POST /upload` | Upload a PDF as multipart form data using the `file` field. Returns the filename, document session ID, and whether it was processed or served from cache. |
| `POST /chat` | Send a question with `session_ids` (or a single `session_id`). Returns an answer and source page numbers. |

The backend Dockerfile runs Uvicorn on port `7860`; running `python api.py` locally uses port `8000`.

## Deploy to Hugging Face Spaces

This repository's root `Dockerfile` builds the frontend and backend into one Docker Space. The app serves the web UI and API from the same Space URL.

1. Create a Hugging Face Space with the **Docker** SDK.
2. Add `GROQ_API_KEY` under the Space's **Settings → Variables and secrets**. Do not put API keys in the repository.
3. Push this repository's contents to the Space. Hugging Face builds the root `Dockerfile` and serves the app on port `7860`.

The backend requires internet access to download its embedding and reranking models on first use. Uploaded PDFs and generated indexes are stored in the container filesystem; configure persistent storage in Space settings if those files must survive container restarts.

## Current scope and limitations

- The PDF loader extracts embedded text; OCR for scanned or image-only pages is not implemented.
- Table extraction is heuristic and depends on PDF text/layout quality; it is not guaranteed to identify every table correctly.
- Groq is required for query expansion and final answers. Local embeddings and reranking do not make the complete chat flow offline.
- Sources identify page numbers, but the chat response does not identify which document each page belongs to.
- The repository does not include benchmark results or measured accuracy/performance figures.

## Repository map

```text
backend/
  api.py                  FastAPI endpoints and pipeline orchestration
  ingestion/              PDF extraction and text chunking
  retrieval/              Embeddings, FAISS storage, search, reranking
  generation/             Groq client and answer generation
  Dockerfile              Backend container configuration
frontend/
  src/App.tsx             Upload, document selection, chat, and UI state
  src/App.css             Application layout and themes
```
