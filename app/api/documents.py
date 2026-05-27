from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.api.dependencies import chunk_store, chunker, document_store
from app.schemas.chunk import ChunkDocumentResponse, TextChunk
from app.schemas.document import DocumentMetadata, UploadDocumentResponse


router = APIRouter()

MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024


@router.post(
    "/documents/upload",
    response_model=UploadDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(file: UploadFile = File(...)) -> UploadDocumentResponse:
    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if len(content) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Uploaded file is too large. Maximum size is 5 MB.",
        )

    try:
        document = document_store.save_text_document(
            filename=file.filename or "uploaded.txt",
            content_type=file.content_type,
            content=content,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return UploadDocumentResponse(
        message="Document uploaded successfully.",
        document=document,
    )


@router.get("/documents", response_model=list[DocumentMetadata])
def list_documents() -> list[DocumentMetadata]:
    return document_store.list_documents()


@router.post(
    "/documents/{document_id}/chunks",
    response_model=ChunkDocumentResponse,
)
def chunk_document(document_id: str) -> ChunkDocumentResponse:
    try:
        document_text = document_store.read_document_text(document_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    chunks = chunker.split_text(
        document_id=document_id,
        text=document_text,
    )

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document does not contain enough text to create chunks.",
        )

    chunk_store.save_chunks(document_id=document_id, chunks=chunks)

    return ChunkDocumentResponse(
        message="Document chunked successfully.",
        document_id=document_id,
        chunk_count=len(chunks),
        chunks=chunks,
    )


@router.get(
    "/documents/{document_id}/chunks",
    response_model=list[TextChunk],
)
def get_document_chunks(document_id: str) -> list[TextChunk]:
    document = document_store.get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}",
        )

    return chunk_store.get_chunks(document_id=document_id)