from unittest.mock import patch

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app, raise_server_exceptions=False)


@patch("src.routes.lore.chroma_service")
@patch("src.routes.lore.embedding_service")
def test_add_lore_success(mock_embedding_service, mock_chroma_service):
    """Adding valid lore content returns 201 with status success and a non-empty id."""
    mock_embedding_service.embed.return_value = [0.1, 0.2, 0.3]
    mock_chroma_service.add_lore.return_value = "abc-123-uuid"

    response = client.post(
        "/api/lore",
        json={"content": "The Obsidian Tower stands at the edge of the Whispering Marsh."},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert isinstance(data["id"], str)
    assert len(data["id"]) > 0


@patch("src.routes.lore.chroma_service")
@patch("src.routes.lore.embedding_service")
def test_add_lore_empty_content(mock_embedding_service, mock_chroma_service):
    """Posting empty lore content returns 422 with a descriptive error message."""
    response = client.post(
        "/api/lore",
        json={"content": ""},
    )

    assert response.status_code == 422
    data = response.json()
    assert "Lore content cannot be empty" in data["detail"]
