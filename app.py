import streamlit as st
from embedding_generator import EmbeddingGenerator
from LLM_handler import LLMHandler
from pdf_loader import PDFLoader
from query_handler import QueryHandler
from text_chunker import TextChunker
from vector_store import VectorStore


st.title('RAG Document Q&A')
pdf=st.file_uploader('Upload Document')
question=st.text_input('Enter Question')
st.write('Answer will appear here')

if st.button('Search'):
    st.write('Processing...')
    
    
    load_pdf = PDFLoader(pdf)
    pdf1=(load_pdf.load_pdf())


    chunk_text=TextChunker(pdf1)
    chunks=chunk_text.chunking()


    make_embeddings=EmbeddingGenerator(chunks)
    embeddings=make_embeddings.embed_text()
 

    stored_vector=VectorStore(embeddings)
    whole_index=stored_vector.making_faiss()



    
    qh=QueryHandler(question=question,container=whole_index,chunks=chunks)
    content=qh.get_results()
    

    LLM=LLMHandler(question=question,chunks=content)
    st.write(LLM.make_chatbot())
