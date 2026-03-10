import logging

from fastapi import APIRouter, HTTPException

from src.models.schemas import LoreRequest, LoreResponse
from src.services import chroma_service, embedding_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/api/lore", response_model=LoreResponse, status_code=201)
def add_lore(request: LoreRequest):
    """Add a new lore entry to the lorebook vector store."""
    if not request.content.strip():
        raise HTTPException(status_code=422, detail="Lore content cannot be empty")

    try:
        embedding = embedding_service.embed(request.content)
        doc_id = chroma_service.add_lore(
            content=request.content,
            metadata=request.metadata if request.metadata else {},
            embedding=embedding,
        )
        return LoreResponse(status="success", id=doc_id)
    except Exception as exc:
        logger.error("Failed to add lore: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
