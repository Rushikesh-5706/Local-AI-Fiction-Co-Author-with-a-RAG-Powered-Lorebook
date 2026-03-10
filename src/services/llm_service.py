import logging

import httpx
from jinja2 import Template

from src.config import settings

logger = logging.getLogger(__name__)

_persona_prompt: str = None

_PROMPT_TEMPLATE = Template(
    """{{ system_prompt }}

Here is some relevant context from the lorebook:
--- CONTEXT ---
{% for doc in context_docs %}
- {{ doc }}
{% endfor %}
--- END CONTEXT ---

Now, continue the story based on this user prompt: {{ user_prompt }}"""
)


def initialize():
    """Load the persona prompt from disk."""
    global _persona_prompt
    try:
        with open(settings.persona_prompt_path, "r", encoding="utf-8") as f:
            _persona_prompt = f.read().strip()
        if not _persona_prompt:
            raise RuntimeError(
                f"Persona prompt file is empty: {settings.persona_prompt_path}"
            )
        logger.info("Loaded persona prompt from %s", settings.persona_prompt_path)
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"Persona prompt file not found: {settings.persona_prompt_path}"
        ) from exc
    except IOError as exc:
        raise RuntimeError(
            f"Failed to read persona prompt file: {settings.persona_prompt_path}: {exc}"
        ) from exc


def generate(
    prompt: str, context_docs: list[str], temperature: float, top_p: float, repeat_penalty: float
) -> str:
    """Render the prompt template and call the Ollama LLM to generate a story segment."""
    if _persona_prompt is None:
        raise RuntimeError(
            "Persona prompt is not loaded. Call initialize() first."
        )

    rendered_prompt = _PROMPT_TEMPLATE.render(
        system_prompt=_persona_prompt,
        context_docs=context_docs,
        user_prompt=prompt,
    )

    request_body = {
        "model": settings.ollama_model,
        "prompt": rendered_prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": top_p,
            "repeat_penalty": repeat_penalty,
        },
    }

    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{settings.ollama_base_url}/api/generate",
                json=request_body,
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logger.error("Ollama returned HTTP error: %s", exc)
        raise RuntimeError(
            f"Ollama LLM returned an error (HTTP {exc.response.status_code}): {exc}"
        ) from exc
    except httpx.RequestError as exc:
        logger.error("Failed to reach Ollama: %s", exc)
        raise RuntimeError(
            f"Could not connect to Ollama at {settings.ollama_base_url}: {exc}"
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        logger.error("Ollama returned invalid JSON: %s", exc)
        raise RuntimeError(
            "Ollama returned a non-JSON response"
        ) from exc

    if "response" not in data:
        logger.error("Ollama response missing 'response' key: %s", data)
        raise RuntimeError(
            "Ollama response did not contain a 'response' field"
        )

    return data["response"]
