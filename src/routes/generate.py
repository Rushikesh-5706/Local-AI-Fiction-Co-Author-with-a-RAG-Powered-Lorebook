import logging

from fastapi import APIRouter, HTTPException

from src.config import settings
from src.models.schemas import GenerateRequest, GenerateResponse
from src.services import chroma_service, embedding_service, llm_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/api/generate", response_model=GenerateResponse, status_code=200)
def generate_story(request: GenerateRequest):
    """Generate a story segment using RAG-powered context from the lorebook."""
    if not request.prompt.strip():
        raise HTTPException(status_code=422, detail="Prompt cannot be empty")

    try:
        query_embedding = embedding_service.embed(request.prompt)
        context_docs = chroma_service.query_lore(
            query_embedding=query_embedding,
            top_k=settings.rag_top_k,
        )
        temperature = request.parameters.temperature
        top_p = request.parameters.top_p
        story_segment = llm_service.generate(
            prompt=request.prompt,
            context_docs=context_docs,
            temperature=temperature,
            top_p=top_p,
        )
        return GenerateResponse(story_segment=story_segment)
    except RuntimeError as exc:
        logger.error("Failed to generate story: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
