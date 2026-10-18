import logging
from threading import Lock

from flashrank import Ranker

logger = logging.getLogger(__name__)

reranker: Ranker | None = None
reranker_lock = Lock()


def get_reranker() -> Ranker:
    global reranker
    if reranker is None:
        with reranker_lock:
            if reranker is None:
                logger.info("Loading lightweight local reranker model...")
                reranker = Ranker(
                    model_name="ms-marco-TinyBERT-L-2-v2",
                    max_length=256,
                )
                logger.info("Reranker model loaded.")
    return reranker
