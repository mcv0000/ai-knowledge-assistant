from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import (
    chunk_store,
    document_store,
    embedding_service,
    embedding_store,
)
from app.schemas.embedding import (
    ChunkEmbedding,
    DocumentEmbeddingsResponse,
    EmbedDocumentResponse,
    EmbeddingSummaryItem,
)


router = APIRouter()


@router.post(
    "/documents/{document_id}/embeddings",
    response_model=EmbedDocumentResponse,
)
def embed_document_chunks(document_id: str) -> EmbedDocumentResponse:
    document = document_store.get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}",
        )

    chunks = chunk_store.get_chunks(document_id=document_id)

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No chunks found for this document. Create chunks before embeddings.",
        )

    chunk_texts = [chunk.text for chunk in chunks]
    vectors = embedding_service.embed_texts(chunk_texts)

    embeddings = [
        ChunkEmbedding(
            document_id=chunk.document_id,
            chunk_id=chunk.chunk_id,
            chunk_index=chunk.chunk_index,
            embedding=vector,
        )
        for chunk, vector in zip(chunks, vectors, strict=True)
    ]

    embedding_store.save_embeddings(
        document_id=document_id,
        embeddings=embeddings,
    )

    embedding_dimension = embedding_service.get_embedding_dimension(vectors)

    return EmbedDocumentResponse(
        message="Embeddings generated successfully.",
        document_id=document_id,
        embedding_count=len(embeddings),
        embedding_dimension=embedding_dimension,
        model_name=embedding_service.model_name,
    )


@router.get(
    "/documents/{document_id}/embeddings",
    response_model=DocumentEmbeddingsResponse,
)
def get_document_embeddings(document_id: str) -> DocumentEmbeddingsResponse:
    document = document_store.get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}",
        )

    embeddings = embedding_store.get_embeddings(document_id=document_id)

    summary_items = [
        EmbeddingSummaryItem(
            document_id=embedding.document_id,
            chunk_id=embedding.chunk_id,
            chunk_index=embedding.chunk_index,
            embedding_dimension=len(embedding.embedding),
        )
        for embedding in embeddings
    ]

    return DocumentEmbeddingsResponse(
        document_id=document_id,
        embedding_count=len(summary_items),
        embeddings=summary_items,
    )