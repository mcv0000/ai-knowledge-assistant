# AI Knowledge Assistant API

Production-oriented RAG backend built with FastAPI, SentenceTransformers, FAISS and OpenAI.

AI Knowledge Assistant demonstrates backend and AI engineering patterns used in real LLM systems: document ingestion, text chunking, embedding generation, vector search, source-grounded answer generation, retrieval evaluation, structured logging, Docker-based development and GitHub Actions CI.

---

## Highlights

* FastAPI backend for document question answering
* Retrieval-Augmented Generation architecture
* Local document ingestion and metadata storage
* Text chunking optimized for cleaner semantic retrieval
* SentenceTransformers embedding pipeline
* FAISS vector search using cosine-style similarity
* OpenAI-powered grounded answer generation
* Source-aware `/ask` responses
* Retrieval evaluation endpoint for checking top-k quality
* Structured JSON request logs
* Request ID propagation with `X-Request-ID`
* Retrieval trace logging with chunk IDs and similarity scores
* Docker and Docker Compose support
* Automated tests with pytest
* GitHub Actions CI

---

## Architecture

The project is organized around clear service boundaries.

API routes stay thin. Business logic lives in services. Schemas define request and response contracts.

```text
app/
├── api/
│   ├── ask.py
│   ├── dependencies.py
│   ├── documents.py
│   ├── embeddings.py
│   ├── evaluation.py
│   ├── health.py
│   ├── routes.py
│   ├── search.py
│   └── vector.py
├── core/
│   └── config.py
├── middleware/
│   └── request_logging.py
├── schemas/
│   ├── ask.py
│   ├── chunk.py
│   ├── document.py
│   ├── embedding.py
│   ├── evaluation.py
│   └── search.py
├── services/
│   ├── chunk_store.py
│   ├── chunker.py
│   ├── document_store.py
│   ├── embedding_service.py
│   ├── embedding_store.py
│   ├── llm_service.py
│   ├── rag_service.py
│   └── vector_store.py
└── main.py
```

---

## RAG Flow

```text
Upload document
      ↓
Read and normalize text
      ↓
Split text into retrieval-friendly chunks
      ↓
Generate embeddings with SentenceTransformers
      ↓
Store chunk embeddings
      ↓
Build FAISS vector index
      ↓
Ask a question
      ↓
Embed the question
      ↓
Retrieve top-k relevant chunks
      ↓
Send retrieved context to the LLM
      ↓
Return grounded answer + source chunks
```

---

## Engineering Decisions

### Thin API routes

Routes are intentionally small. They validate request flow, call services, and return typed responses.

### Service-oriented backend structure

Document storage, chunking, embedding generation, vector search and RAG orchestration are separated into service classes. This keeps the system easier to test and extend.

### Local-first storage

The first version uses local JSON files and local FAISS index files. This keeps the project simple and easy to run while still demonstrating the core AI backend architecture.

### FAISS IndexFlatIP

The vector store uses FAISS `IndexFlatIP`. Embeddings are normalized, so inner product behaves like cosine similarity.

### Grounded answers

The `/ask` flow is designed to answer only from retrieved document context and return sources with the answer.

### Retrieval quality before extra infrastructure

The project prioritizes retrieval quality, evaluation and observability before adding heavier infrastructure such as PostgreSQL, queues or authentication.

---

## Features

### Document ingestion

* Upload `.txt` documents
* Store uploaded files locally
* Store metadata in JSON
* Validate empty files and max upload size
* Decode common text encodings

### Chunking

* Normalizes whitespace
* Removes BOM artifacts
* Avoids cutting chunks in the middle of words when possible
* Uses overlap to preserve context across chunk boundaries
* Merges very small final chunks
* Covered by unit tests

### Embeddings

* Generates chunk embeddings with SentenceTransformers
* Stores embeddings locally
* Exposes embedding metadata without returning full vectors

### Vector search

* Builds a FAISS index from chunk embeddings
* Supports semantic search over document chunks
* Returns chunk IDs, text and similarity scores

### RAG answers

* Retrieves relevant chunks
* Sends context to OpenAI
* Returns grounded answers with source chunks

### Retrieval evaluation

* Evaluates whether an expected chunk appears in top-k results
* Returns hit/miss, rank and precision-style score
* Useful for validating retrieval quality during development

### Observability

* Adds `X-Request-ID` to responses
* Accepts incoming `X-Request-ID` headers
* Emits structured JSON logs
* Logs request method, path, status code and latency
* Logs retrieval traces with question, top-k, chunk IDs and scores

---

## API Endpoints

### Health

```http
GET /health
```

Returns API health status.

---

### Upload document

```http
POST /documents/upload
```

Uploads a `.txt` document.

---

### List documents

```http
GET /documents
```

Returns uploaded document metadata.

---

### Create chunks

```http
POST /documents/{document_id}/chunks
```

Splits a document into retrieval chunks.

---

### Get chunks

```http
GET /documents/{document_id}/chunks
```

Returns chunks for a document.

---

### Generate embeddings

```http
POST /documents/{document_id}/embeddings
```

Generates embeddings for document chunks.

---

### Get embeddings summary

```http
GET /documents/{document_id}/embeddings
```

Returns embedding metadata without exposing full vectors.

---

### Rebuild vector index

```http
POST /vector-index/rebuild
```

Builds a local FAISS index from generated embeddings.

---

### Semantic search

```http
POST /search
```

Retrieves relevant chunks for a question.

Example body:

```json
{
  "question": "What are the current limitations of the project?",
  "top_k": 3
}
```

Example response:

```json
{
  "question": "What are the current limitations of the project?",
  "results": [
    {
      "document_id": "example-document-id",
      "chunk_id": "example-chunk-id",
      "chunk_index": 2,
      "text": "Current limitations include local JSON storage, local FAISS index files, and synchronous embedding generation.",
      "score": 0.3602
    }
  ]
}
```

---

### Retrieval evaluation

```http
POST /evaluation/retrieval
```

Checks whether an expected chunk appears in retrieved top-k results.

Example body:

```json
{
  "question": "What are the current limitations of the project?",
  "expected_chunk_id": "example-chunk-id",
  "top_k": 3
}
```

Example response:

```json
{
  "question": "What are the current limitations of the project?",
  "expected_chunk_id": "example-chunk-id",
  "retrieved_chunk_ids": [
    "example-chunk-id",
    "another-chunk-id"
  ],
  "hit": true,
  "rank": 1,
  "precision_at_k": 1.0
}
```

---

### Ask question

```http
POST /ask
```

Runs the full RAG pipeline.

Example body:

```json
{
  "question": "What is this document about?"
}
```

Example response:

```json
{
  "answer": "The document is about FastAPI, RAG, embeddings and vector search.",
  "sources": [
    {
      "document_id": "example-document-id",
      "chunk_id": "example-chunk-id",
      "text": "This is a test document about FastAPI RAG embeddings and vector search."
    }
  ]
}
```

---

## Local Setup

### 1. Create a virtual environment

Windows:

```cmd
py -3.13 -m venv .venv
.venv\Scripts\activate.bat
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create environment file

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=your_model_here
RAG_TOP_K=3
```

### 4. Run the API

```bash
uvicorn app.main:app --reload
```

Open API docs:

```text
http://127.0.0.1:8000/docs
```

---

## Docker Setup

Build the Docker image:

```bash
docker compose build
```

Run the API:

```bash
docker compose up
```

Open API docs:

```text
http://127.0.0.1:8000/docs
```

Stop the containers:

```bash
docker compose down
```

Local runtime data is stored in:

```text
data/
```

This directory is ignored by Git.

---

## Example Usage Flow

1. Start the API.
2. Upload a `.txt` document with `POST /documents/upload`.
3. Copy the returned `document_id`.
4. Create chunks with `POST /documents/{document_id}/chunks`.
5. Generate embeddings with `POST /documents/{document_id}/embeddings`.
6. Rebuild the FAISS index with `POST /vector-index/rebuild`.
7. Test retrieval with `POST /search`.
8. Evaluate retrieval quality with `POST /evaluation/retrieval`.
9. Ask a grounded question with `POST /ask`.

---

## Retrieval Quality

The project includes basic retrieval quality validation.

A manual validation flow was used to check whether relevant chunks appear in top-k retrieval results.

Example checks:

* A specific FAISS question should retrieve the chunk explaining query embeddings and stored chunk embeddings.
* A limitations question should retrieve the chunk describing local JSON storage, local FAISS files and synchronous embedding generation.
* General questions may retrieve relevant context in top-k even when the best chunk is not ranked first.

This makes retrieval behavior inspectable instead of treating the RAG pipeline as a black box.

---

## Evaluation Methodology

The `/evaluation/retrieval` endpoint supports lightweight retrieval evaluation.

It measures:

* whether the expected chunk appears in retrieved results
* the rank of the expected chunk
* a simple precision-style hit score

This is intentionally simple. The goal is not to build an academic evaluation framework, but to demonstrate practical AI engineering discipline: checking whether retrieval returns the context the LLM needs.

---

## Observability

The API includes production-oriented observability basics.

Each request receives an `X-Request-ID` response header. If a client sends an `X-Request-ID`, the API reuses it.

Request logs are emitted as structured JSON.

Example request log:

```json
{
  "level": "INFO",
  "message": "request_completed",
  "logger": "app.request",
  "request_id": "manual-retrieval-test-1",
  "method": "POST",
  "path": "/search",
  "status_code": 200,
  "duration_ms": 123.45,
  "client_host": "127.0.0.1"
}
```

Retrieval logs include retrieved chunk IDs and scores.

Example retrieval log:

```json
{
  "level": "INFO",
  "message": "retrieval_completed",
  "logger": "app.retrieval",
  "request_id": "manual-retrieval-test-1",
  "question": "What are the current limitations of the project?",
  "top_k": 3,
  "result_count": 3,
  "retrieved_chunk_ids": [
    "example-chunk-id"
  ],
  "scores": [
    0.3602
  ]
}
```

---

## Tests

Run tests:

```bash
pytest
```

Current test coverage includes:

* health endpoint
* request ID header
* text normalization
* BOM cleanup
* chunk creation
* small final chunk merging
* document storage
* retrieval evaluation hit case
* retrieval evaluation miss case

---

## CI

GitHub Actions runs the test suite on push and pull requests to `main`.

The CI pipeline helps verify that core backend behavior remains stable as the project evolves.

---

## Deployment Story

This project is currently designed as a local-first portfolio backend.

It can run locally with Python or through Docker Compose. The next deployment step would be to run the API on a small cloud VM or container platform with environment variables configured for OpenAI access.

A production deployment would need persistent storage, secret management and a more durable metadata store.

---

## Current Limitations

This is intentionally a focused portfolio version.

Current limitations:

* Supports `.txt` files only
* Uses local JSON metadata storage
* Uses local file storage for uploads
* Uses local FAISS index files
* Embedding generation is synchronous
* No authentication yet
* No database yet
* No PDF parsing yet
* No streaming LLM responses yet
* No background job queue yet

---

## Next Improvements

High-impact next improvements:

* PDF ingestion
* Streaming responses for `/ask`
* API key authentication
* PostgreSQL metadata storage
* Background embedding jobs
* More advanced retrieval evaluation datasets
* Metadata filtering
* Docker deployment guide
* Better error handling around model loading and missing indexes

---

## Design Principles

The project intentionally avoids unnecessary complexity.

The goal is to demonstrate practical AI backend engineering:

```text
ingestion -> chunking -> embeddings -> retrieval -> grounded answer -> evaluation -> observability
```

The codebase is built to be readable, testable and easy to extend without turning into an overengineered framework.
