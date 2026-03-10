from unittest.mock import patch

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app, raise_server_exceptions=False)


@patch("src.routes.generate.llm_service")
@patch("src.routes.generate.chroma_service")
@patch("src.routes.generate.embedding_service")
def test_generate_success(mock_embedding_service, mock_chroma_service, mock_llm_service):
    """A valid generation request returns 200 with a non-empty story segment."""
    mock_embedding_service.embed.return_value = [0.1, 0.2, 0.3]
    mock_chroma_service.query_lore.return_value = ["Ancient dragons guard the northern pass."]
    mock_llm_service.generate.return_value = "The wind howled through the northern pass as shadows stirred."

    response = client.post(
        "/api/generate",
        json={"prompt": "Continue the journey north."},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["story_segment"], str)
    assert len(data["story_segment"]) > 0


@patch("src.routes.generate.llm_service")
@patch("src.routes.generate.chroma_service")
@patch("src.routes.generate.embedding_service")
def test_generate_empty_prompt(mock_embedding_service, mock_chroma_service, mock_llm_service):
    """Posting an empty prompt returns 422 with a descriptive error message."""
    response = client.post(
        "/api/generate",
        json={"prompt": ""},
    )

    assert response.status_code == 422
    data = response.json()
    assert "Prompt cannot be empty" in data["detail"]


@patch("src.routes.generate.llm_service")
@patch("src.routes.generate.chroma_service")
@patch("src.routes.generate.embedding_service")
def test_generate_temperature_param(mock_embedding_service, mock_chroma_service, mock_llm_service):
    """The temperature value from the request body is forwarded to llm_service.generate."""
    mock_embedding_service.embed.return_value = [0.1, 0.2, 0.3]
    mock_chroma_service.query_lore.return_value = []
    mock_llm_service.generate.return_value = "A tale unfolds."

    response = client.post(
        "/api/generate",
        json={
            "prompt": "Begin the chapter.",
            "parameters": {"temperature": 0.3, "top_p": 0.5},
        },
    )

    assert response.status_code == 200
    mock_llm_service.generate.assert_called_once()
    call_kwargs = mock_llm_service.generate.call_args.kwargs
    assert call_kwargs["temperature"] == 0.3
    assert call_kwargs["top_p"] == 0.5
