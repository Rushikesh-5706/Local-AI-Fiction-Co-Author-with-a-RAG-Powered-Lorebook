import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.models.schemas import HealthResponse
from src.routes.generate import router as generate_router
from src.routes.lore import router as lore_router
from src.services import chroma_service, embedding_service, llm_service

logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Initialize all services on startup."""
    logger.info("Starting application initialization")
    embedding_service.initialize()
    chroma_service.initialize()
    llm_service.initialize()
    logger.info("All services initialized successfully")
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title="Local AI Fiction Co-Author",
    description="A RAG-powered creative writing assistant backed by a local LLM and vector lorebook",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lore_router)
app.include_router(generate_router)


@app.get("/health", response_model=HealthResponse, status_code=200)
def health_check():
    """Return the health status and version of the application."""
    return HealthResponse(status="healthy", version="1.0.0")
