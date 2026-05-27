\# AI Knowledge Assistant API



A production-style FastAPI backend for document question answering using Retrieval Augmented Generation.



The system allows users to upload text documents, split them into chunks, generate embeddings, store them in a FAISS vector index, retrieve relevant context, and answer questions using an LLM based only on retrieved document context.



\## Why this project exists



This project was built as a portfolio backend project for AI Engineer roles.



It demonstrates:



\- FastAPI backend architecture

\- Document ingestion

\- Text chunking

\- Embedding generation

\- FAISS vector search

\- Retrieval Augmented Generation

\- Source-grounded LLM answers

\- Clean separation between API routes, schemas, and services



\## Tech stack



\- Python 3.11+

\- FastAPI

\- Pydantic

\- Uvicorn

\- SentenceTransformers

\- FAISS

\- OpenAI API

\- python-dotenv



\## RAG pipeline



```text

Upload document

&#x20;     ↓

Read text

&#x20;     ↓

Split into chunks

&#x20;     ↓

Generate embeddings

&#x20;     ↓

Build FAISS vector index

&#x20;     ↓

Ask question

&#x20;     ↓

Embed question

&#x20;     ↓

Retrieve relevant chunks

&#x20;     ↓

Send context to LLM

&#x20;     ↓

Return grounded answer + sources

```



\## Project structure



```text

app/

├── api/

│   └── routes.py

├── core/

│   └── config.py

├── schemas/

│   ├── ask.py

│   ├── chunk.py

│   ├── document.py

│   ├── embedding.py

│   └── search.py

├── services/

│   ├── chunk\_store.py

│   ├── chunker.py

│   ├── document\_store.py

│   ├── embedding\_service.py

│   ├── embedding\_store.py

│   ├── llm\_service.py

│   ├── rag\_service.py

│   └── vector\_store.py

└── main.py

```



\## Main endpoints



\### Health check



```http

GET /health

```



Returns basic API status.



\### Upload document



```http

POST /documents/upload

```



Uploads a `.txt` document.



\### List documents



```http

GET /documents

```



Returns uploaded document metadata.



\### Create chunks



```http

POST /documents/{document\_id}/chunks

```



Splits the selected document into text chunks.



\### Get chunks



```http

GET /documents/{document\_id}/chunks

```



Returns chunks for a document.



\### Generate embeddings



```http

POST /documents/{document\_id}/embeddings

```



Generates embeddings for document chunks.



\### Get embeddings summary



```http

GET /documents/{document\_id}/embeddings

```



Returns embedding metadata without exposing full vectors.



\### Rebuild FAISS index



```http

POST /vector-index/rebuild

```



Builds a local FAISS vector index from generated embeddings.



\### Semantic search



```http

POST /search

```



Retrieves relevant chunks for a question.



Example body:



```json

{

&#x20; "question": "What is this document about?",

&#x20; "top\_k": 3

}

```



\### Ask question



```http

POST /ask

```



Runs the full RAG pipeline.



Example body:



```json

{

&#x20; "question": "What is this document about?"

}

```



Example response:



```json

{

&#x20; "answer": "The document is about FastAPI, RAG, embeddings, and vector search.",

&#x20; "sources": \[

&#x20;   {

&#x20;     "document\_id": "example-document-id",

&#x20;     "chunk\_id": "example-chunk-id",

&#x20;     "text": "This is a test document about FastAPI RAG embeddings and vector search."

&#x20;   }

&#x20; ]

}

```

## Docker setup

Build the Docker image:

```bash
docker compose build

Run the API:

docker compose up

Open API docs:

http://127.0.0.1:8000/docs

Stop the containers:

docker compose down

The application stores local runtime data in:

data/

This directory is mounted as a Docker volume and is ignored by Git.

\## Local setup



\### 1. Create virtual environment



Windows:



```cmd

py -3.13 -m venv .venv

.venv\\Scripts\\activate.bat

```



macOS / Linux:



```bash

python3 -m venv .venv

source .venv/bin/activate

```



\### 2. Install dependencies



```bash

pip install -r requirements.txt

```



\### 3. Create environment file



Create a `.env` file in the project root:



```env

OPENAI\_API\_KEY=your\_api\_key\_here

OPENAI\_MODEL=your\_model\_here

RAG\_TOP\_K=3

```



\### 4. Run the API



```bash

uvicorn app.main:app --reload

```



Open API docs:



```text

http://127.0.0.1:8000/docs

```



\## Example usage flow



1\. Start the API.

2\. Upload a `.txt` document with `POST /documents/upload`.

3\. Copy the returned `document\_id`.

4\. Create chunks with `POST /documents/{document\_id}/chunks`.

5\. Generate embeddings with `POST /documents/{document\_id}/embeddings`.

6\. Rebuild the FAISS index with `POST /vector-index/rebuild`.

7\. Ask a question with `POST /ask`.



\## Current limitations



This is intentionally a simple portfolio version.



Current limitations:



\- Supports `.txt` files only

\- Uses local file storage

\- Uses local FAISS index

\- No authentication

\- No database

\- No async background processing

\- No PDF parsing yet

\- No Docker setup yet



\## Possible future improvements



\- PDF ingestion

\- PostgreSQL metadata storage

\- Docker Compose setup

\- Authentication

\- Background jobs for embeddings

\- Better chunking strategy

\- Streaming LLM responses

\- Unit and integration tests

\- CI pipeline with GitHub Actions



\## Design principles



The project intentionally avoids overengineering.



The goal is to clearly demonstrate the core RAG architecture:



```text

ingestion → chunking → embeddings → vector search → grounded answer

```



The code is organized so each responsibility lives in a separate service.

