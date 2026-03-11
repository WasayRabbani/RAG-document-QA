from gemini_client import get_client

class EmbeddingGenerator:
    
    def __init__(self,chunks_made):
        self.chunks=chunks_made
        
        self.client=get_client()
  
    def embed_text(self):
        self.embedded_data=self.client.models.embed_content(
            
            model='gemini-embedding-001',
            contents=self.chunks)
        result=[]
        for i in self.embedded_data.embeddings:
            result.append(i.values)
        return result
    

