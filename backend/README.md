---
title: RAG App Backend
emoji: 🧠
colorFrom: purple
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
---

# RAG Application Backend (FastAPI)

This is the containerized FastAPI backend for the production RAG application, designed to run on Hugging Face Spaces using Docker.

## Configuration Details
- **SDK**: Docker
- **Port**: 7860 (Hugging Face Spaces Default)
- **Engine**: FastAPI + Uvicorn
- **Dependencies**: FastEmbed/ONNX Runtime, FlashRank, FAISS, pdfplumber, rank-bm25, Groq API
- **Model footprint**: Uses the compact `BAAI/bge-small-en-v1.5` embedding model and FlashRank's `ms-marco-TinyBERT-L-2-v2` reranker; neither requires PyTorch.
