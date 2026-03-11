# RAG Document Q&A

Upload any PDF and ask questions. AI answers using only your document.

Built with Python, Google Gemini API, FAISS, and Streamlit.

---

## What This App Does

- Upload any PDF document
- Ask questions in plain English
- AI finds the most relevant sections from your document
- Answers are generated strictly from your document — no hallucination

---
## Questions to ask

1. When was TechNova founded?
2. Who are the founders of TechNova?
3. How many employees does TechNova have?
4. What is NovaChat and how much does it cost?
5. What is Sara Khan's educational background?
6. How many leave days do employees get?
7. What is TechNova's annual revenue in 2023?
8. Which hospital uses NovaSearch?
9. What technology stack does TechNova use?
10. Where is TechNova's head office located?


## Project Structure

```
rag-document-qa/
├── app.py                    # Streamlit UI — run this
├── main.py                   # CLI version for testing
├── pdf_loader.py             # PDFLoader class — extracts text from PDF
├── text_chunker.py           # TextChunker class — splits text into chunks
├── gemini_client.py          # get_client() — Gemini API connection
├── embedding_generator.py    # EmbeddingGenerator class — creates embeddings
├── vector_store.py           # VectorStore class — stores embeddings in FAISS
├── query_handler.py          # QueryHandler class — searches relevant chunks
├── LLM_handler.py            # LLMHandler class — generates final answer
├── .env                      # Your API key (never share this)
├── .gitignore                # Ignores .env and venv
└── requirements.txt          # All dependencies
```

---

## How It Works

```
PDF Upload
    ↓
Extract Text (pypdf)
    ↓
Split into Chunks (LangChain — 500 chars, 50 overlap)
    ↓
Generate Embeddings (Google Gemini — gemini-embedding-001)
    ↓
Store in FAISS Vector Database
    ↓
User Question → Embed → Search FAISS → Top 4 Chunks
    ↓
Send Question + Chunks to Gemini (gemini-2.5-flash)
    ↓
Answer
```

---

## Setup — Step by Step

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/rag-document-qa.git
cd rag-document-qa
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get Your Google Gemini API Key

1. Go to [https://aistudio.google.com](https://aistudio.google.com)
2. Sign in with your Google account
3. Click **"Get API Key"** in the top left
4. Click **"Create API Key"**
5. Copy the key — it looks like: `AIzaSy...`

> **Note:** The API is free to use with generous daily limits. No credit card required.

### 5. Create Your .env File

In the project root folder, create a file named exactly `.env` (with the dot):

```
GEMINI_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with the key you copied.

**Example:**
```
GEMINI_API_KEY=AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz123456
```

> **Important:** Never share your `.env` file. Never push it to GitHub. It is already listed in `.gitignore` to keep it safe.

### 6. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## How to Use

1. Open the app in your browser
2. Click **"Upload Document"** and select any PDF
3. Type your question in the text box
4. Click **"Search"**
5. Wait a few seconds — the answer will appear below

---

## Requirements

- Python 3.9 or above
- Google Gemini API key (free)
- Internet connection (for Gemini API calls)

---

## Dependencies

```
google-genai
python-dotenv
pypdf
langchain-text-splitters
faiss-cpu
numpy
streamlit
```

Install all at once:
```bash
pip install -r requirements.txt
```

---

## Important Notes

- The app answers **only from your uploaded document**
- If the answer is not in the document, it will say: *"I don't know based on the provided document"*
- Large PDFs may take longer to process (embeddings are generated for each chunk)
- Your API key is stored locally in `.env` — it is never uploaded to GitHub

---

## Built With

| Tool | Purpose |
|------|---------|
| Google Gemini API | Embeddings + Answer Generation |
| FAISS | Vector similarity search |
| LangChain Text Splitters | Chunking documents |
| pypdf | PDF text extraction |
| Streamlit | Web UI |
| python-dotenv | API key management |

---

## Author

Built by Wasay — learning Gen AI development.