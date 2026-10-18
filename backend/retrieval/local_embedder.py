import logging
from collections.abc import Iterable
from threading import Lock

import numpy as np
from fastembed import TextEmbedding

logger = logging.getLogger(__name__)

MODEL_NAME = "BAAI/bge-small-en-v1.5"


class LocalEmbedder:
    def __init__(self):
        logger.info("Loading local embedding model '%s'...", MODEL_NAME)
        self.model = TextEmbedding(model_name=MODEL_NAME)
        logger.info("Embedding model loaded.")

    def encode(
        self,
        sentences: str | Iterable[str],
        batch_size: int = 32,
    ) -> np.ndarray:
        if isinstance(sentences, str):
            return next(self.model.query_embed(sentences))
        return np.asarray(
            list(self.model.embed(sentences, batch_size=batch_size)),
            dtype=np.float32,
        )


embedder: LocalEmbedder | None = None
embedder_lock = Lock()


def get_embedder() -> LocalEmbedder:
    global embedder
    if embedder is None:
        with embedder_lock:
            if embedder is None:
                embedder = LocalEmbedder()
    return embedder
