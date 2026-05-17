# 🧠 PDF Brain — Production-Grade RAG Document Q&A

PDF Brain is a high-performance, developer-friendly **Retrieval-Augmented Generation (RAG)** application. It allows users to upload complex PDF documents—such as research papers, legal agreements, and technical manuals—and conduct highly accurate, contextual Q&A with them.

Unlike generic RAG prototypes, **PDF Brain** is built for production-grade speed and accuracy. It features **smart local/offline embeddings**, **keyword + semantic hybrid retrieval (BM25 + FAISS)**, and an offline **Cross-Encoder reranker** that double-checks candidates, ensuring the LLM only sees the absolute most relevant context.

---

## 🚀 Architectural Highlights & Core Capabilities

*   **⚡ Smart Cache Check (0ms Ingestion):** Generates an MD5 content-based checksum fingerprint of uploaded PDFs. If the document has already been processed, it bypasses the entire parser, chunking, and embedding pipelines, launching a session instantly.
*   **📐 Hybrid Table & Math Extraction:** Uses a fast parser (`pypdf`) with built-in mathematical notation repair (e.g., rebuilding exponents like `10 19` into `10^19`), coupled with a layout-aware table parser (`pdfplumber`) to cleanly format tables into `[TABLE ROW]` entities.
*   **🔗 Advanced Parent-Child Chunking:** Prose is split into Parent chunks (2000 chars) for LLM context, and Child chunks (500 chars) for precise vector searching. First-sentence headings or section titles are prepended as a context prefix to children, making numeric-only data fully searchable.
*   **🔍 Multi-Stage Hybrid Search:**
    1.  **HyDE (Hypothetical Document Embeddings):** Generates a hypothetical answer via Groq to improve bi-encoder query semantic mapping.
    2.  **Semantic Search (FAISS):** Searches the local `all-MiniLM-L6-v2` dense vector index for the top 20 matches.
    3.  **Keyword Search (BM25):** Performs a lexical search via the BM25 algorithm for another 20 candidates.
    4.  **Local Cross-Encoder Reranking:** Takes unique candidates from both semantic and lexical streams, and reranks them against the *original* user question using an offline `ms-marco-MiniLM-L-6-v2` cross-encoder to select the absolute top 3.
*   **📂 Multi-PDF Chat Support:** Supports loading and searching across multiple document sessions concurrently, aggregating and globally reranking candidates before generating a response.
*   **🚀 Ultra-Fast LLM Inference:** Powered by Groq's API utilizing the high-speed **Llama 3.3 70B** model.

---

## 🛠️ Tech Stack

*   **Backend:** Python 3.10+, FastAPI, Uvicorn, LangChain (text splitters)
*   **Frontend:** React 19, TypeScript, Vite, Axios, HSL CSS Custom Styling
*   **Vector Engine:** FAISS (Facebook AI Similarity Search)
*   **Local Embeddings:** Sentence-Transformers `all-MiniLM-L6-v2` (Offline)
*   **Local Reranker:** Cross-Encoder `ms-marco-MiniLM-L-6-v2` (Offline)
*   **LLM Generator:** Llama 3.3 70B (via Groq Cloud)

---

## 📂 Repository Structure

```text
rag-document-qa/
├── backend/
│   ├── storage/             # Ignored: Pickled chunks (.pkl) & FAISS indexes (.faiss)
│   ├── uploads/             # Ignored: Locally stored PDF uploads
│   ├── api.py               # FastAPI orchestrator exposing REST endpoints
│   ├── pdf_loader.py        # PDF extraction & clean-up utilities
│   ├── text_chunker.py      # Parent-child chunking & table handler
│   ├── embedding_generator.py # Local batch vector encoder
│   ├── local_embedder.py    # Singleton holding the SentenceTransformer
│   ├── local_reranker.py    # Singleton holding the CrossEncoder model
│   ├── query_handler.py     # HyDE + BM25 + FAISS + Reranking logic
│   └── LLM_handler.py       # Context assembly & Groq inference
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main React App & state manager
│   │   ├── App.css          # Sleek premium styles & dark mode
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── .gitignore               # Excludes secrets, node_modules, .venv, and RAG caches
├── requirements.txt         # Python dependencies
└── README.md
```

---

## ⚙️ Quick Start Setup Guide

### 📋 Prerequisites
Ensure you have the following installed on your machine:
*   [Python 3.10+](https://www.python.org/downloads/)
*   [Node.js (v18+)](https://nodejs.org/)
*   A free [Groq API Key](https://console.groq.com/)

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/WasayRabbani/RAG-document-QA.git
cd RAG-document-QA
```

---

### Step 2: Set Up Backend Environment

Create a `.env` file in the **root directory** of the repository:
```env
GROQ_API_KEY=your_groq_api_key_here
```

#### Windows Configuration
In the root directory, open PowerShell or Command Prompt:
```powershell
# Create Virtual Environment
python -m venv .venv

# Activate Virtual Environment
.venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt
```

#### macOS / Linux Configuration
In the root directory, open your terminal:
```bash
# Create Virtual Environment
python3 -m venv .venv

# Activate Virtual Environment
source .venv/bin/activate

# Install Dependencies
pip install -r requirements.txt
```

---

### Step 3: Set Up Frontend Environment
Open a new shell or terminal in the root directory:
```bash
cd frontend
npm install
```

---

## 🏃 Running the Application

### 1. Launch the Backend Server
Make sure your Python virtual environment (`.venv`) is activated, then run:
```bash
cd backend
python api.py
```
The FastAPI backend will start at: `http://localhost:8000`
*(Note: On the very first run, it will automatically download the embedding and reranking models locally. This might take 1-2 minutes depending on your internet connection. Subsequent launches are instant!)*

### 2. Launch the Frontend Dev Server
In another terminal, navigate to the frontend directory and start the dev server:
```bash
cd frontend
npm run dev
```
The React frontend will spin up at: `http://localhost:5173` (or the port specified in your console). Open this URL in your web browser to start chatting with your PDFs!

---

## 🧠 Behind the Scenes: How a Query Works

```text
[User Question]
       │
       ▼
┌──────────────┐
│  HyDE Answer │ (LLM simulates a technical answer to enrich semantic relevance)
└──────┬───────┘
       │
       ├──────────────────────────────────────┐
       ▼                                      ▼
┌──────────────┐                       ┌──────────────┐
│ FAISS Search │ (Semantic match       │  BM25 Search │ (Lexical keyword
│   (Top 20)   │  using local embeddings)│   (Top 20)   │  matching)
└──────┬───────┘                       └──────┬───────┘
       │                                      │
       └──────────────────┬───────────────────┘
                          ▼
                  ┌──────────────┐
                  │ Merge & Dup  │ (Unifies candidates into a unique list)
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ Cross-Encoder│ (Local reranker evaluates true relevance
                  │  Rerank Top3 │  between original question and chunks)
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ Groq LLM Chat│ (Synthesizes final answer page-by-page
                  │  Synthesis   │  strictly from context)
                  └──────────────┘
```

---

## 🛠️ Troubleshooting & Support

*   **Slow First PDF Upload / Timeout:** The backend downloads the local model files (approx. 400MB total) upon the very first upload or server launch. Please allow a few minutes for this download to complete. Subsequent runs will be lighting-fast and entirely offline.
*   **GROQ_API_KEY Error:** Double-check that your `.env` file is in the **root** folder (not inside the `backend` folder) and contains `GROQ_API_KEY=gsk_...` with no spaces or quotation marks.
*   **Port In Use:** If port `8000` or `5173` is busy, you can custom-assign them:
    *   *Backend:* Change port in `api.py` at `uvicorn.run(app, port=8000)`.
    *   *Frontend:* Vite will automatically assign another port, or you can specify one using `npm run dev -- --port XXXX`.

---

## 📝 Author & Acknowledgements
Built by **Wasay** — developed as a comprehensive practice for production-grade, local hybrid-retrieval GenAI applications. Contributions, bug reports, and suggestions are welcome!