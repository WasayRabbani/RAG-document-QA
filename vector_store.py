import faiss
import numpy as np
class VectorStore:
    def __init__(self,vectors):
        self.vectors=vectors
        
    def save_vectors(self):
        
        # Saving as numpy array as faiss uses that
        vector_array=np.array(
            self.vectors,
            dtype=np.float32
        )
        return vector_array
    
    def making_faiss(self):
        self.dimension=3072
        container=faiss.IndexFlatL2(self.dimension)
        return container
    













    
# from pdf_loader import PDFLoader

# load=PDFLoader(r"D:\IDM Files\sample.pdf")  
# text=load.load_pdf()


# from text_chunker import TextChunker 

# make_chunks=TextChunker(text)
# chunk=make_chunks.chunking()


# from embedding_generator import EmbeddingGenerator
# generate_embeddings=EmbeddingGenerator(chunk)
# embeddings=generate_embeddings.embed_text()
# # print(type(embeddings))    
# v1=VectorStore(embeddings) 
# print((v1.making_faiss()[0]))