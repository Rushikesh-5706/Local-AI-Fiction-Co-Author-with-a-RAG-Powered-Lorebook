import logging
import uuid

import chromadb
from chromadb import Collection

from src.config import settings

logger = logging.getLogger(__name__)

_client: chromadb.HttpClient | None = None
_collection: Collection | None = None


def initialize():
    """Connect to ChromaDB and get or create the lorebook collection."""
    global _client, _collection
    try:
        logger.info(
            "Connecting to ChromaDB at %s:%s", settings.chroma_host, settings.chroma_port
        )
        _client = chromadb.HttpClient(
            host=settings.chroma_host, port=settings.chroma_port
        )
        _collection = _client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "ChromaDB collection '%s' ready (count: %d)",
            settings.chroma_collection_name,
            _collection.count(),
        )
    except Exception as exc:
        logger.error("Failed to connect to ChromaDB: %s", exc)
        raise RuntimeError(f"Could not connect to ChromaDB: {exc}") from exc


def add_lore(content: str, metadata: dict, embedding: list[float]) -> str:
    """Add a lore document to the ChromaDB collection and return its ID."""
    if _collection is None:
        raise RuntimeError(
            "ChromaDB collection is not initialized. Call initialize() first."
        )
    try:
        doc_id = str(uuid.uuid4())
        _collection.add(
            ids=[doc_id],
            documents=[content],
            embeddings=[embedding],
            metadatas=[metadata if metadata else {}],
        )
        logger.info("Added lore document with id: %s", doc_id)
        return doc_id
    except Exception as exc:
        logger.error("Failed to add lore document: %s", exc)
        raise RuntimeError(f"Failed to add lore to ChromaDB: {exc}") from exc


def query_lore(query_embedding: list[float], top_k: int) -> list[str]:
    """Query the ChromaDB collection and return the top-k matching documents."""
    if _collection is None:
        raise RuntimeError(
            "ChromaDB collection is not initialized. Call initialize() first."
        )
    try:
        if _collection.count() == 0:
            logger.info("Collection is empty, returning no results")
            return []
        results = _collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, _collection.count()),
        )
        documents = results.get("documents", [[]])[0]
        logger.info("Retrieved %d lore documents", len(documents))
        return documents
    except Exception as exc:
        logger.error("Failed to query ChromaDB: %s", exc)
        raise RuntimeError(f"Failed to query lore from ChromaDB: {exc}") from exc
