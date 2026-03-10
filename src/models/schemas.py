from typing import Optional

from pydantic import BaseModel


class LoreRequest(BaseModel):
    """Request body for adding a lore entry."""

    content: str
    metadata: Optional[dict] = None


class LoreResponse(BaseModel):
    """Response body after adding a lore entry."""

    status: str
    id: str


class GenerationParameters(BaseModel):
    """Optional generation parameters for story generation."""

    temperature: Optional[float] = 0.8
    top_p: Optional[float] = 0.9


class GenerateRequest(BaseModel):
    """Request body for generating a story segment."""

    prompt: str
    parameters: Optional[GenerationParameters] = GenerationParameters()


class GenerateResponse(BaseModel):
    """Response body containing the generated story segment."""

    story_segment: str


class HealthResponse(BaseModel):
    """Response body for the health check endpoint."""

    status: str
    version: str
