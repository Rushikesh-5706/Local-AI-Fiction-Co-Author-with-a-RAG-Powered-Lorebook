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

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/Rushikesh-5706/Local-AI-Fiction-Co-Author-with-a-RAG-Powered-Lorebook.git
   cd Local-AI-Fiction-Co-Author-with-a-RAG-Powered-Lorebook
   ```

2. Create your environment file from the provided template:
   ```bash
   cp .env.example .env
   ```

3. Build and start all services in detached mode:
   ```bash
   docker-compose up -d --build
   ```

4. Wait for all three services to report as healthy. This may take several minutes on first run, as Ollama needs to download the language model:
   ```bash
   docker-compose ps
   ```
   All services should show a status of "healthy" before proceeding.

5. Verify the application is running:
   ```bash
   curl http://localhost:8080/health
   ```
   Expected response:
   ```json
   {"status": "healthy", "version": "1.0.0"}
   ```

---

## API Reference

### GET /health

Returns the current health status and version of the application.

**Response (200):**
```json
{"status": "healthy", "version": "1.0.0"}
```

---

### POST /api/lore

Add a new lore entry to the vector lorebook. The content is embedded and stored in ChromaDB for later retrieval during story generation.

| Field    | Type   | Required | Description                                          |
|----------|--------|----------|------------------------------------------------------|
| content  | string | Yes      | The lore text to store (character bios, locations, etc.) |
| metadata | object | No       | Optional key-value metadata to associate with the entry  |

**Example request:**
```bash
curl -X POST http://localhost:8080/api/lore \
  -H "Content-Type: application/json" \
  -d '{"content": "Kael is a wandering swordsman who lost his memory in the Siege of Ashvale.", "metadata": {"type": "character"}}'
```

**Response (201):**
```json
{"status": "success", "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"}
```

---

### POST /api/generate

Generate a story segment. The system embeds your prompt, retrieves relevant lore from ChromaDB, assembles a full prompt with the persona and context, and sends it to the LLM.

| Field                  | Type   | Required | Description                                    |
|------------------------|--------|----------|------------------------------------------------|
| prompt                 | string | Yes      | The story prompt or continuation instruction   |
| parameters.temperature | float  | No       | Controls randomness (default: 0.8)             |
| parameters.top_p       | float  | No       | Nucleus sampling threshold (default: 0.9)      |

**Example request:**
```bash
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Kael enters a tavern in a port town and recognizes a face from his past.", "parameters": {"temperature": 0.7, "top_p": 0.85}}'
```

**Response (200):**
```json
{"story_segment": "The salt-heavy air of the Broken Anchor tavern clung to Kael's coat as he pushed through the door..."}
```

---

## RAG Pipeline Explained

Retrieval-augmented generation is the core architectural pattern that makes this project more than just a wrapper around a language model. The fundamental insight is that LLMs, even large ones, have no persistent memory of your fictional world. Every call to the model is stateless. If you told it yesterday that your protagonist lost an arm in battle, it will not remember today. The RAG pipeline solves this by giving the model a searchable external memory -- the lorebook.

When you add a lore entry through the API, the system converts the text into a dense vector representation using the all-MiniLM-L6-v2 sentence transformer model. This model maps text into a 384-dimensional vector space where semantically similar texts end up near each other. The phrase "a warrior who lost his memory" will produce a vector close to "an amnesiac soldier," even though they share almost no words. These vectors, along with the original text, are stored in ChromaDB using cosine similarity as the distance metric.

When a generation request arrives, the same embedding model converts the user's story prompt into a vector. ChromaDB then performs an approximate nearest neighbor search, returning the top-k lore entries whose vectors are closest to the prompt vector. These retrieved documents -- the most contextually relevant pieces of your world-building -- are injected into a Jinja2 prompt template alongside the persona system prompt and the user's original instruction. The fully assembled prompt is sent to the Ollama LLM, which generates a story continuation that is grounded in the retrieved lore. The result is coherent fiction that respects the established world, because the model was given the relevant context at generation time rather than relying on its own parametric memory.

---

## Generation Parameters

| Parameter      | Range       | Default | Effect                                                                 |
|----------------|-------------|---------|------------------------------------------------------------------------|
| temperature    | 0.0 - 2.0  | 0.8     | Controls randomness; lower values produce safer, more predictable text |
| top_p          | 0.0 - 1.0  | 0.9     | Nucleus sampling cutoff; lower values restrict vocabulary diversity     |
| repeat_penalty | 1.0 - 2.0  | 1.1     | Discourages token repetition; higher values force more lexical variety  |

For detailed examples of how each parameter affects generated output, see the [parameter effects documentation](docs/parameter_effects.md).

---

## Running the Tests

The test suite uses mocked service dependencies, so it does not require Ollama or ChromaDB to be running. To run the tests inside the app container:

```bash
docker-compose exec app python -m pytest tests/ -v
```

Alternatively, if you have Python 3.11 and the project dependencies installed locally:

```bash
python -m pytest tests/ -v
```

---

## Docker Hub

The pre-built Docker image for the application service is available on Docker Hub. You can pull it directly without building from source:

```bash
docker pull rushi5706/local-ai-fiction-co-author:latest
```

This image contains the FastAPI application and all Python dependencies. You still need to run Ollama and ChromaDB separately (or use the provided docker-compose.yml) for the full system to function.
