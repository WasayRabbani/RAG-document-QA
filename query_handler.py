import numpy as np
import faiss
from gemini_client import get_client


class QueryHandler:
    def __init__(self,question,container,chunks):
        
        self.query=question
        self.container=container
        self.client= get_client() 
        self.chunks=chunks 
        

# Embedding question
    def embed_query(self):
        
        self.embedded_query=self.client.models.embed_content(
            model='gemini-embedding-001',
            contents=self.query)
    
    def make_array(self):
        self.query_array=np.array(
           [ self.embedded_query.embeddings[0].values],
            dtype=np.float32
        )

    def compare_query(self):
        
        
        self.distance,self.index=self.container.search(self.query_array,k=4)
        return self.distance,self.index  

    
    # Here when we find the closest emeddings, we then get the actual text of it
    def get_results(self):
        
        self.embed_query()
        self.make_array()
        self.compare_query()
        
        results=[]
        top_index=self.index
        for i in top_index[0]:
            results.append(self.chunks[i])
        
        return results
      
        
        
      
        

