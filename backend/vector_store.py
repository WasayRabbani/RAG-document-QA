import faiss
import numpy as np
import pickle
import os

class VectorStore:
    def __init__(self, vectors=None, chunks=None):
        self.vectors = vectors
        self.chunks = chunks
        self.vector_array = None
        
    def save_vectors(self):
        if self.vectors is None:
            return None
        # Saving as numpy array as faiss uses that
        self.vector_array = np.array(
            self.vectors,
            dtype=np.float32
        )
        return self.vector_array
    
    def making_faiss(self):
        self.save_vectors() # Calling other funtion also
        self.dimension = len(self.vector_array[0])
        container = faiss.IndexFlatL2(self.dimension)
        container.add(self.vector_array)
        return container

    def save_to_disk(self, index, index_path="index.faiss", chunks_path="chunks.pkl"):
        """Saves the FAISS index and text chunks to local files."""
        faiss.write_index(index, index_path)
        with open(chunks_path, "wb") as f:
            pickle.dump(self.chunks, f)
        print(f"Index saved to {index_path} and chunks to {chunks_path}")

    @staticmethod
    def load_from_disk(index_path="index.faiss", chunks_path="chunks.pkl"):
        """Loads the FAISS index and text chunks from local files."""
        if os.path.exists(index_path) and os.path.exists(chunks_path):
            index = faiss.read_index(index_path)
            with open(chunks_path, "rb") as f:
                chunks = pickle.load(f)
            return index, chunks
        return None, None