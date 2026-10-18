# Project Summary

## What this project does

PDF Brain is a web application for asking questions about uploaded PDFs. The React frontend uploads documents and sends chat questions to a FastAPI backend. The backend extracts and chunks PDF text, creates local vector indexes, retrieves relevant chunks from one or more documents, reranks them, and asks a Groq-hosted model to answer from the retrieved context.

## Architecture at a glance

```text
Browser (React + Vite)
  ├── POST /upload  ──> FastAPI
  │                     ├── extract text and table rows from PDF
  │                     ├── split into searchable chunks
  │                     ├── embed locally and persist FAISS + chunks
  │                     └── return a content/model-based session_id
  └── POST /chat    ──> FastAPI
                        ├── retrieve candidates from selected sessions
                        ├── hybrid semantic + BM25 search
                        ├── locally rerank candidates
                        └── generate an answer with Groq
```

The backend's default local URL is `http://localhost:8000`. The frontend uses `VITE_API_URL` when set, otherwise it uses that local URL.

## Backend files

| File | Responsibility |
| --- | --- |
| [`backend/api.py`](./backend/api.py) | FastAPI application and orchestration. Defines `/health`, `/upload`, and `/chat`; validates PDF uploads; derives a session ID from the PDF bytes and embedding model; checks for cached index/chunk files; invokes ingestion, retrieval, and generation modules. Chat accepts either `session_id` or `session_ids` and searches across selected PDF sessions. |
| [`backend/ingestion/pdf_loader.py`](./backend/ingestion/pdf_loader.py) | Extracts page text with `pypdf`, conditionally extracts tables with `pdfplumber`, formats table rows with headers, cleans common symbols, and returns page-numbered text. |
| [`backend/ingestion/text_chunker.py`](./backend/ingestion/text_chunker.py) | Separates marked table rows into individual chunks. Splits remaining page text into parent chunks (2,000 characters, 200 overlap) and child search chunks (500 characters, 50 overlap); stores parent context with each child. |
| [`backend/retrieval/embedding_generator.py`](./backend/retrieval/embedding_generator.py) | Encodes each chunk's searchable text in batches using the shared local embedder. |
| [`backend/retrieval/local_embedder.py`](./backend/retrieval/local_embedder.py) | Lazily initializes a thread-safe FastEmbed model singleton (`BAAI/bge-small-en-v1.5`) and provides document/query encoding. |
| [`backend/retrieval/local_reranker.py`](./backend/retrieval/local_reranker.py) | Lazily initializes a thread-safe FlashRank reranker singleton (`ms-marco-TinyBERT-L-2-v2`). |
| [`backend/retrieval/query_handler.py`](./backend/retrieval/query_handler.py) | Runs retrieval for one document: optional HyDE query expansion through Groq, top-20 FAISS semantic search, top-20 BM25 keyword search, candidate de-duplication, FlashRank reranking, and returns up to three chunks. |
| [`backend/retrieval/vector_store.py`](./backend/retrieval/vector_store.py) | Converts embeddings to NumPy float32 arrays, builds a FAISS L2 index, and saves/loads it alongside pickled chunks. |
| [`backend/generation/LLM_handler.py`](./backend/generation/LLM_handler.py) | Builds a deduplicated context from retrieved parent chunks and calls Groq's OpenAI-compatible chat-completions API. The default model is configured in `groq_client.py`. |
| [`backend/generation/groq_client.py`](./backend/generation/groq_client.py) | Loads backend environment variables, provides a shared Groq OpenAI-compatible client, and selects `GROQ_MODEL` (default `openai/gpt-oss-20b`). |
| [`backend/ingestion/__init__.py`](./backend/ingestion/__init__.py), [`backend/retrieval/__init__.py`](./backend/retrieval/__init__.py), [`backend/generation/__init__.py`](./backend/generation/__init__.py) | Python package markers for the three backend module groups. |
| [`backend/requirements.txt`](./backend/requirements.txt) | Python runtime dependencies for the API, PDF processing, embeddings, FAISS, retrieval, reranking, and Groq client. |
| [`backend/Dockerfile`](./backend/Dockerfile) | Builds the Python 3.10 backend image and starts Uvicorn on port 7860; the backend directory is expected to be the Docker build context. |
| [`backend/.dockerignore`](./backend/.dockerignore) | Excludes local virtual environments, secrets, generated storage/uploads, and miscellaneous local files from the Docker build context. |
| [`backend/README.md`](./backend/README.md) | Hugging Face Spaces deployment metadata and a short backend deployment overview. |
| [`backend/sequence.txt`](./backend/sequence.txt) | Compact, informal outline of the main ingestion and question-answering sequence. |

### Backend API contract

- `GET /health` returns a health status and API version.
- `POST /upload` accepts multipart form data with a `file` PDF. Returns `filename`, `session_id`, and a `status` of `cached` or `processed`.
- `POST /chat` accepts JSON with a non-empty `question` and either `session_id` or `session_ids`. Returns `answer` and a list of source page numbers.

Uploads and derived data are stored under `backend/uploads/` and `backend/storage/{indices,chunks}/`. The storage files are runtime data, not source modules. Cache identity includes the embedding model name, so changing the model changes the session ID.

## Frontend files

| File | Responsibility |
| --- | --- |
| [`frontend/src/main.tsx`](./frontend/src/main.tsx) | React entry point. Loads global CSS and mounts `App` under React Strict Mode. |
| [`frontend/src/App.tsx`](./frontend/src/App.tsx) | Main UI and client state. Uploads PDFs, keeps the current document library and chat transcript in React state, sends questions with selected session IDs, displays answers/sources/errors, and toggles light/dark themes. |
| [`frontend/src/App.css`](./frontend/src/App.css) | Main application layout and component styling, including sidebar, document library, chat messages, and theme variants. |
| [`frontend/src/index.css`](./frontend/src/index.css) | Global/reset and root-level styling loaded by `main.tsx`. |
| [`frontend/src/assets/hero.png`](./frontend/src/assets/hero.png) | Image asset in the frontend source tree. |
| [`frontend/src/assets/react.svg`](./frontend/src/assets/react.svg), [`frontend/src/assets/vite.svg`](./frontend/src/assets/vite.svg) | Default Vite starter assets; not used by the current app entry point. |
| [`frontend/public/favicon.svg`](./frontend/public/favicon.svg), [`frontend/public/icons.svg`](./frontend/public/icons.svg) | Static public SVG assets. |
| [`frontend/index.html`](./frontend/index.html) | Vite HTML shell containing the React mount element. |
| [`frontend/package.json`](./frontend/package.json) | Frontend scripts and dependencies. The app uses React, TypeScript, Vite, and Axios. |
| [`frontend/vite.config.ts`](./frontend/vite.config.ts) | Vite configuration with the React plugin. |
| [`frontend/tsconfig.json`](./frontend/tsconfig.json), [`frontend/tsconfig.app.json`](./frontend/tsconfig.app.json), [`frontend/tsconfig.node.json`](./frontend/tsconfig.node.json) | TypeScript project/build configuration for app and tooling code. |
| [`frontend/eslint.config.js`](./frontend/eslint.config.js) | ESLint configuration for frontend source and build tooling. |
| [`frontend/vercel.json`](./frontend/vercel.json) | Rewrites frontend routes to `index.html` for single-page-app hosting. |
| [`frontend/README.md`](./frontend/README.md) | Vite template documentation; it does not describe the PDF Q&A application. |

### Frontend behavior notes

- The document library and message history live only in React state; refreshing the page clears this UI state. The backend's index/chunk cache can still let an identical PDF upload return quickly.
- Removing a document removes it from the current chat selection; it does not delete backend uploads or cached indexes.
- The UI displays source page numbers returned by the API. The response format does not include document names alongside page numbers.
- Upload and chat errors are shown in a temporary toast.

## Configuration and local development

- Backend settings: `GROQ_API_KEY` is required for final generation; `GROQ_MODEL` is optional and defaults to `openai/gpt-oss-20b`. Both are loaded from the environment / root `.env` by `python-dotenv`. HyDE falls back to the original question if it cannot call Groq.
- Frontend API URL: optional `VITE_API_URL`; defaults to `http://localhost:8000`.
- Install backend dependencies from the repository root with `pip install -r backend/requirements.txt`.
- Install frontend dependencies from `frontend/` with `npm install`.
- Start the backend from `backend/` with `python api.py` (port 8000).
- Start the frontend from `frontend/` with `npm run dev` (Vite's default port is 5173).
- Frontend scripts include `npm run build` (TypeScript build plus Vite build), `npm run lint`, and `npm run preview`.

## Current repository notes

- The backend source currently uses the `ingestion/`, `retrieval/`, and `generation/` package layout. The root [`README.md`](./README.md) still shows the older flat module paths, so use the actual backend files listed above as the source of truth.
- [`backend_architecture_walkthrough.md`](./backend_architecture_walkthrough.md) and [`classes.txt`](./classes.txt) are additional root-level architecture/class notes.
- No test/spec files were found in the current repository file inventory.
- Generated uploads and FAISS/pickle storage are local runtime state and should not be treated as source code.
