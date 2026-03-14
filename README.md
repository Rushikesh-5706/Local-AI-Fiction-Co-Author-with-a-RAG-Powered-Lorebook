# Local AI Fiction Co-Author with a RAG-Powered Lorebook

This project is a locally-hosted creative writing assistant that pairs a large language model with a persistent vector-backed lorebook. The idea is straightforward but architecturally compelling: every piece of world-building you feed into the system -- character backstories, location descriptions, artifact lore, historical events -- gets embedded into a vector space and stored in ChromaDB. When you ask the model to continue your story, the system first retrieves the most semantically relevant lore entries, injects them into a structured prompt alongside a carefully crafted persona, and then hands the whole package to an Ollama-hosted LLM for generation. The result is fiction that actually remembers its own world, written in a consistent voice, powered entirely by infrastructure running on your own machine.

---

## Architecture Overview

The data flow through the system follows a clear retrieval-augmented generation pipeline:

```
                         +---------------------------+
                         |      User Prompt          |
                         +------------+--------------+
                                      |
                                      v
                         +---------------------------+
                         |     FastAPI Application    |
                         +------------+--------------+
                                      |
                         +------------+--------------+
                         |   Embedding Service        |
                         |  (Sentence Transformers)   |
                         +------------+--------------+
                                      |
                                      v
                         +---------------------------+
                         |       ChromaDB             |
                         |   (Vector Similarity       |
                         |    Search - Cosine)        |
                         +------------+--------------+
                                      |
                                      v
                         +---------------------------+
                         |    Retrieved Lore Docs     |
                         +------------+--------------+
                                      |
                                      v
                         +---------------------------+
                         |  Jinja2 Prompt Template    |
                         |  (Persona + Context +      |
                         |   User Prompt)             |
                         +------------+--------------+
                                      |
                                      v
                         +---------------------------+
                         |      Ollama LLM            |
                         |   (llama3.1:8b default)    |
                         +------------+--------------+
                                      |
                                      v
                         +---------------------------+
                         |  Generated Story Segment   |
                         +---------------------------+
```

The user's prompt enters the FastAPI application, gets embedded into a vector, and is used to search ChromaDB for the most relevant lorebook entries. Those entries are combined with a persona system prompt via a Jinja2 template, and the fully assembled prompt is sent to the Ollama LLM. The generated text comes back to the user as a story segment.

---

## Technology Stack

| Component          | Technology                | Purpose                                              |
|--------------------|---------------------------|------------------------------------------------------|
| Web Framework      | FastAPI 0.111.0           | Async-capable REST API with automatic OpenAPI docs    |
| LLM Runtime        | Ollama                    | Local model serving for llama3.1:8b                   |
| Vector Database    | ChromaDB 0.5.3            | Persistent vector store with cosine similarity search |
| Embeddings         | Sentence Transformers 3.0 | Text-to-vector encoding using all-MiniLM-L6-v2       |
| Prompt Templating  | Jinja2 3.1.4              | Dynamic prompt assembly with context injection        |
| Configuration      | Pydantic Settings 2.3.4   | Type-safe environment variable management             |
| HTTP Client        | httpx 0.27.0              | Async-capable HTTP client for Ollama API calls        |
| Containerization   | Docker / Docker Compose   | Multi-service orchestration with healthchecks         |
| Testing            | pytest 8.2.2              | Unit testing with mocked service dependencies         |

---

## Project Structure

```
Local-AI-Fiction-Co-Author-with-a-RAG-Powered-Lorebook/
├── docker-compose.yml
├── Dockerfile
├── .dockerignore
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── prompts/
│   └── persona.md
├── docs/
│   └── parameter_effects.md
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── lore.py
│   │   └── generate.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── embedding_service.py
│   │   ├── chroma_service.py
│   │   └── llm_service.py
│   └── models/
│       ├── __init__.py
│       └── schemas.py
└── tests/
    ├── __init__.py
    ├── test_lore.py
    └── test_generate.py
```

---

## Prerequisites

Before running this project, make sure you have the following installed and configured on your machine:

1. **Docker Desktop** version 24 or later
2. **Docker Compose** version 2 or later (bundled with modern Docker Desktop)
3. At least **8 GB of RAM** allocated to Docker (the LLM and embedding model both need significant memory)
4. At least **10 GB of free disk space** for the Ollama model weights and Docker images

---

## Getting Started: Evaluator Step-by-Step Guide

Follow these exact steps to build the project, run the services, and verify the outputs. 

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Rushikesh-5706/Local-AI-Fiction-Co-Author-with-a-RAG-Powered-Lorebook.git
   cd Local-AI-Fiction-Co-Author-with-a-RAG-Powered-Lorebook
   ```

2. **Create the environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Build and start all services in detached mode:**
   ```bash
   docker-compose up -d --build
   ```
   *Expected Output snippet:*
   ```text
   [+] Running 4/4
    ✔ Network local-ai-fiction-co-author... Created
    ✔ Container local-ai...chromadb-1       Started
    ✔ Container local-ai...ollama-1         Started
    ✔ Container local-ai...app-1            Started
   ```

4. **Wait for Services to be Healthy:**
   The Ollama service starts, waits for the server to be ready, then automatically pulls the 4.7GB `llama3.1:8b` model. This may take 5–10 minutes depending on your network. Check the status:
   ```bash
   docker-compose ps
   ```
   *Expected Output:*
   ```text
   NAME               IMAGE                               COMMAND                  SERVICE    STATUS
   ...app-1           local-ai-fiction-co-author-app      "python -m uvicorn s…"   app        Up (healthy)
   ...chromadb-1      chromadb/chroma:0.5.3              "/docker-entrypoint.…"   chromadb   Up (healthy)
   ...ollama-1        ollama/ollama:latest                "/bin/sh -c 'ollama …"   ollama     Up (healthy)
   ```
   **Do not proceed until all three services show `(healthy)`.**
Note: the Ollama healthcheck uses `ollama list` and the ChromaDB healthcheck uses a bash TCP socket check, as neither container includes curl or wget.
   
6. **Verify the App Health Endpoint:**
   ```bash
   curl -s http://localhost:8080/health
   ```
   *Expected Output:*
   ```json
   {"status":"healthy","version":"1.0.0"}
   ```

---

## API Reference & Usage Guide

Once the system is healthy, test the API contracts exactly as specified.

### 1. Add Lore to the Vector Database (`POST /api/lore`)

Inject world-building context into the ChromaDB vector store. 

**Request:**
```bash
curl -s -X POST http://localhost:8080/api/lore \
  -H "Content-Type: application/json" \
  -d '{"content": "Kael is a wandering swordsman who lost his memory in the Siege of Ashvale. He carries a shattered obsidian blade.", "metadata": {"type": "character"}}'
```

**Expected Output (201 Created):**
```json
{
  "status": "success",
  "id": "e44d5a9b-32b0-4f51-b0db-6e6a1c1a2f1a"
}
```
*(Note: the UUID will be dynamically generated).*

### 2. Generate a Story Segment (`POST /api/generate`)

The system will embed your prompt, retrieve the relevant lore ("Kael is a wandering swordsman..."), combine it with the cinematic persona prompt, and generate a contextual response via Ollama.

**Request:**
```bash
curl -s -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Kael enters a tavern in a port town and recognizes a face from his past.",
    "parameters": {
      "temperature": 0.7,
      "top_p": 0.85,
      "repeat_penalty": 1.15
    }
  }'
```

**Expected Output (200 OK):**
```json
{
  "story_segment": "The heavy oak door of the Drowning Sailor tavern groaned inward, admitting a gust of salt-thick air and a lone figure. Kael stepped over the threshold, his hand instinctively brushing the hilt of the shattered obsidian blade at his hip. The tavern was a dim cavern of lantern light and stale ale..."
}
```
*(Note: Exect prose will vary slightly due to LLM sampling).*

---

## Generation Parameters

The API accepts granular generation parameters that are forwarded directly to the Ollama runtime:

| Parameter      | Range       | Default | Effect                                                                 |
|----------------|-------------|---------|------------------------------------------------------------------------|
| temperature    | `0.0` - `2.0` | 0.8     | Controls randomness; lower values produce safer, more predictable text |
| top_p          | `0.0` - `1.0` | 0.9     | Nucleus sampling cutoff; lower values restrict vocabulary diversity    |
| repeat_penalty | `1.0` - `2.0` | 1.1     | Discourages token repetition; higher values force more lexical variety |

For detailed examples of how each parameter affects generated output, see the [parameter effects documentation](docs/parameter_effects.md).

---

## RAG Pipeline Explained

Retrieval-augmented generation is the core architectural pattern that makes this project more than just a wrapper around a language model. The fundamental insight is that LLMs, even large ones, have no persistent memory of your fictional world. Every call to the model is stateless. 

1. **Ingestion:** When you add a lore entry through the API, the system converts the text into a dense vector representation using the `all-MiniLM-L6-v2` sentence transformer model. These vectors, along with the original text, are stored in ChromaDB using cosine similarity as the distance metric.
2. **Retrieval & Generation:** When a generation request arrives, the same embedding model converts the user's prompt into a vector. ChromaDB then performs an approximate nearest neighbor search, returning the top-k lore entries whose vectors are closest. These retrieved documents are injected into a Jinja2 prompt template alongside the cinematic persona system prompt and the user's original instruction. The fully assembled prompt is sent to the Ollama LLM. The result is coherent fiction heavily grounded in established lore.

---

## Running the Tests

The automated test suite uses `unittest.mock.patch` to perfectly isolate tests from infrastructure dependencies. It intercepts the FastAPI `lifespan` startup to prevent the app from attempting to connect to ChromaDB or download models during test runs.

### Option A: Run directly on your host machine
If you have Python 3.11+ installed locally:

```bash
# 1. Install production dependencies
pip install -r requirements.txt

# 2. Install development and testing tools
pip install -r requirements-dev.txt

# 3. Execute the test suite
python -m pytest tests/ -v
```

**Expected Output:**
```text
============================= test session starts ==============================
platform darwin -- Python 3.12.4, pytest-8.2.2, pluggy-1.6.0
configfile: pytest.ini
plugins: timeout-2.4.0, asyncio-0.23.7, anyio-3.7.1
collected 5 items                                                              

tests/test_generate.py::test_generate_success PASSED                     [ 20%]
tests/test_generate.py::test_generate_empty_prompt PASSED                [ 40%]
tests/test_generate.py::test_generate_temperature_param PASSED           [ 60%]
tests/test_lore.py::test_add_lore_success PASSED                         [ 80%]
tests/test_lore.py::test_add_lore_empty_content PASSED                   [100%]

============================== 5 passed in 0.49s ===============================
```

### Option B: Run inside the Docker container
If you prefer not to install dependencies locally, you can run the tests inside the pre-built application container. 

```bash
docker-compose exec app pip install -r requirements-dev.txt
docker-compose exec app python -m pytest tests/ -v
```

---

## Docker Hub

The pre-built Docker image for the application service is available on Docker Hub. You can pull it directly without building from source:

```bash
docker pull rushi5706/local-ai-fiction-co-author:latest
```

This image contains the FastAPI application and all Python dependencies. You still need to run Ollama and ChromaDB separately (or use the provided docker-compose.yml) for the full system to function.
