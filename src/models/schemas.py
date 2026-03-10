from typing import Optional

from pydantic import BaseModel, Field


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

    temperature: Optional[float] = Field(default=0.8, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=0.9, ge=0.0, le=1.0)
    repeat_penalty: Optional[float] = Field(default=1.1, ge=1.0, le=2.0)


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
