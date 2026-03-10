from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def mock_service_initialization():
    """
    Patch all three service initialize() calls in the lifespan context so that
    tests do not require a running ChromaDB instance, a downloaded embedding
    model, or the persona prompt file on disk.
    """
    with (
        patch("src.main.embedding_service.initialize"),
        patch("src.main.chroma_service.initialize"),
        patch("src.main.llm_service.initialize"),
    ):
        yield
