import logging

from sentence_transformers import SentenceTransformer

from src.config import settings

logger = logging.getLogger(__name__)

_model: SentenceTransformer | None = None


def initialize():
    """Load the sentence-transformers model into memory."""
    global _model
    try:
        logger.info("Loading embedding model: %s", settings.embedding_model_name)
        _model = SentenceTransformer(settings.embedding_model_name)
        logger.info("Embedding model loaded successfully")
    except Exception as exc:
        logger.error("Failed to load embedding model: %s", exc)
        raise RuntimeError(
            f"Could not load embedding model '{settings.embedding_model_name}': {exc}"
        ) from exc


def embed(text: str) -> list[float]:
    """Compute the embedding vector for the given text."""
    if _model is None:
        raise RuntimeError(
            "Embedding model is not initialized. Call initialize() first."
        )
    embedding = _model.encode(text)
    return embedding.tolist()
