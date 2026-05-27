from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import (
    chunk_store,
    document_store,
    embedding_store,
    vector_store,
)
from app.schemas.chunk import TextChunk
from app.schemas.embedding import ChunkEmbedding


router = APIRouter()


@router.post("/vector-index/rebuild")
def rebuild_vector_index() -> dict[str, int | str]:
    documents = document_store.list_documents()

    all_embeddings: list[ChunkEmbedding] = []
    chunks_by_id: dict[str, TextChunk] = {}

    for document in documents:
        document_embeddings = embedding_store.get_embeddings(
            document_id=document.document_id,
        )
        document_chunks = chunk_store.get_chunks(
            document_id=document.document_id,
        )

        all_embeddings.extend(document_embeddings)

        for chunk in document_chunks:
            chunks_by_id[chunk.chunk_id] = chunk

    try:
        indexed_vector_count = vector_store.build_index(
            embeddings=all_embeddings,
            chunks_by_id=chunks_by_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return {
        "message": "FAISS index rebuilt successfully.",
        "indexed_vector_count": indexed_vector_count,
    }