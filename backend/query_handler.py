import numpy as np
import faiss
from local_embedder import get_embedder

class QueryHandler:
    def __init__(self, question, container, chunks, client=None, threshold=1.5):
        self.query = question
        self.container = container
        self.client = client # Kept for signature compatibility but unused
        self.chunks = chunks 
        self.threshold = threshold # Lower L2 distance means higher similarity
        self.embedder = get_embedder()

    def embed_query(self):
        # Local model encodes the string synchronously
        self.embedded_query = self.embedder.encode(self.query)
    
    def make_array(self):
        self.query_array = np.array(
           [self.embedded_query],
            dtype=np.float32
        )

    def compare_query(self):
        # Fetch top 10 from FAISS to give reranker more options
        self.distances, self.indices = self.container.search(self.query_array, k=10)
        return self.distances, self.indices  

    def get_results(self):
        self.embed_query()
        self.make_array()
        self.compare_query()
        
        from local_reranker import get_reranker
        reranker = get_reranker()
        
        candidate_chunks = []
        # distances[0] contains the L2 distances
        # indices[0] contains the indices of the matches
        for dist, idx in zip(self.distances[0], self.indices[0]):
            if dist < self.threshold:
                candidate_chunks.append(self.chunks[idx])
            else:
                print(f"Skipping FAISS chunk with distance {dist:.2f}")
                
        if not candidate_chunks:
            return []

        # Rerank with Cross-Encoder
        pairs = [[self.query, chunk['text']] for chunk in candidate_chunks]
        scores = reranker.predict(pairs)
        
        for i, chunk in enumerate(candidate_chunks):
            chunk['rerank_score'] = float(scores[i])
            print(f"Chunk page {chunk['page']} score: {chunk['rerank_score']:.2f}")
            
        # Sort chunks by rerank score (highest first)
        candidate_chunks.sort(key=lambda x: x['rerank_score'], reverse=True)
        
        # Return top 2 absolutely most relevant chunks
        return candidate_chunks[:2]
