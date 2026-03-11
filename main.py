from pdf_loader import PDFLoader
from text_chunker import TextChunker
from embedding_generator import EmbeddingGenerator
from vector_store import VectorStore
from query_handler import QueryHandler
from LLM_handler import LLMHandler

link = r"sample.pdf"


load_pdf = PDFLoader(link)
pdf=(load_pdf.load_pdf())


chunk_text=TextChunker(pdf)
chunks=chunk_text.chunking()


make_embeddings=EmbeddingGenerator(chunks)
embeddings=make_embeddings.embed_text()
# print(embeddings)

stored_vector=VectorStore(embeddings)
whole_index=stored_vector.making_faiss()
# print(stored_vector)


q='When was TechNova founded?'
qh=QueryHandler(question=q,container=whole_index,chunks=chunks)
content=qh.get_results()
print(content)

# LLM=LLMHandler(question=q,chunks=content)
# print(LLM.make_chatbot())

# print(len(chunks))  # kitne chunks total?
# print(chunks[1])    # index 1 kya hai?
# print(chunks[16])   # index 16 kya hai?