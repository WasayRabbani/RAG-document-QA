import logging
from local_embedder import get_embedder

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    def __init__(self, chunks_made, client=None, batch_size=32, max_concurrent_requests=1):
        self.chunks = chunks_made
        self.embedder = get_embedder()
        self.batch_size = batch_size
        logger.info(f"DEBUG: Initialized Backend EmbeddingGenerator with batch_size={batch_size}")

    async def embed_text(self):
        logger.info(f"Starting local embedding process for {len(self.chunks)} chunks...")
        
        batch_texts = [chunk["text"] for chunk in self.chunks]
        
        # sentence-transformers encodes the whole list efficiently, handling batching internally
        embeddings = self.embedder.encode(batch_texts, show_progress_bar=True, batch_size=self.batch_size)
        
        # Return the embeddings (which is a numpy array). 
        # VectorStore will convert it correctly.
        return embeddings
