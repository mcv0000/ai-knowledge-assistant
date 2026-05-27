from pydantic import BaseModel, Field


class TextChunk(BaseModel):
    chunk_id: str = Field(..., description="Unique chunk identifier.")
    document_id: str = Field(..., description="ID of the source document.")
    chunk_index: int = Field(..., description="Position of the chunk in the document.")
    text: str = Field(..., description="Chunk text content.")
    character_count: int = Field(..., description="Number of characters in the chunk.")


class ChunkDocumentResponse(BaseModel):
    message: str
    document_id: str
    chunk_count: int
    chunks: list[TextChunk]