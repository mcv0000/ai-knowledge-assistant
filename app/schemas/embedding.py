from pydantic import BaseModel, Field


class ChunkEmbedding(BaseModel):
    document_id: str = Field(..., description="ID of the source document.")
    chunk_id: str = Field(..., description="ID of the source chunk.")
    chunk_index: int = Field(..., description="Position of the chunk in the document.")
    embedding: list[float] = Field(..., description="Vector representation of the chunk.")


class EmbeddingSummaryItem(BaseModel):
    document_id: str
    chunk_id: str
    chunk_index: int
    embedding_dimension: int


class EmbedDocumentResponse(BaseModel):
    message: str
    document_id: str
    embedding_count: int
    embedding_dimension: int
    model_name: str


class DocumentEmbeddingsResponse(BaseModel):
    document_id: str
    embedding_count: int
    embeddings: list[EmbeddingSummaryItem]