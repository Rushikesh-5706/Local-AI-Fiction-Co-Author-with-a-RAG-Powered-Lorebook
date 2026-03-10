from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    ollama_model: str = "llama3.1:8b"
    ollama_base_url: str = "http://ollama:11434"
    chroma_host: str = "chromadb"
    chroma_port: int = 8000
    chroma_collection_name: str = "lorebook"
    embedding_model_name: str = "all-MiniLM-L6-v2"
    app_port: int = 8080
    app_host: str = "0.0.0.0"
    log_level: str = "info"
    rag_top_k: int = 3
    persona_prompt_path: str = "/app/prompts/persona.md"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
