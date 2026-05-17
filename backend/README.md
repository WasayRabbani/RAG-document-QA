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
- **Dependencies**: sentence-transformers, FAISS, pdfplumber, cross-encoder, rank-bm25, Groq API
