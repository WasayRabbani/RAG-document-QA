from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Loading local embedding model 'all-MiniLM-L6-v2' (this may take a few seconds)...")
embedder = SentenceTransformer('all-MiniLM-L6-v2')
logger.info("Model loaded successfully.")

def get_embedder():
    return embedder
