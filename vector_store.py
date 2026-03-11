import faiss
import numpy as np
class VectorStore:
    def __init__(self,vectors):
        self.vectors=vectors
        
    def save_vectors(self):
        
        # Saving as numpy array as faiss uses that
        self.vector_array=np.array(
            self.vectors,
            dtype=np.float32
        )
        return self.vector_array
    
    def making_faiss(self):
        self.save_vectors() # Calling other funtion also
        self.dimension=len(self.vector_array[0])
        container=faiss.IndexFlatL2(self.dimension)
        container.add(self.vector_array)
        return container
            