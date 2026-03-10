from pdf_loader import PDFLoader
from text_chunker import TextChunker
from embedding_generator import EmbeddingGenerator
from vector_store import VectorStore



link = r"sample.pdf"
load_pdf = PDFLoader(link)

pdf=(load_pdf.load_pdf())

chunk_text=TextChunker(pdf)
chunks=chunk_text.chunking()

make_embeddings=EmbeddingGenerator(chunks)
print((make_embeddings.embed_text())[0])



