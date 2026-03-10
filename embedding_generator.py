
from google import genai
from dotenv import load_dotenv


class EmbeddingGenerator:
    
    def __init__(self,chunks_made):
        self.chunks=chunks_made
        load_dotenv()
        self.client=genai.Client()
  
    def embed_text(self):
        self.embedded_data=self.client.models.embed_content(
            
            model='gemini-embedding-001',
            contents=self.chunks)
        result=[]
        for i in self.embedded_data.embeddings:
            result.append(i.values)
        return result
    

