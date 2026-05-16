from sentence_transformers import CrossEncoder
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Loading local reranker model 'cross-encoder/ms-marco-MiniLM-L-6-v2' (this may take a few seconds)...")
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
logger.info("Reranker model loaded successfully.")

def get_reranker():
    return reranker
