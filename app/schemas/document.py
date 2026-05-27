from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    document_id: str = Field(..., description="Unique document identifier.")
    filename: str = Field(..., description="Original uploaded filename.")
    stored_filename: str = Field(..., description="Filename used in local storage.")
    content_type: str | None = Field(None, description="Uploaded file content type.")
    size_bytes: int = Field(..., description="File size in bytes.")
    character_count: int = Field(..., description="Number of characters in the document.")


class UploadDocumentResponse(BaseModel):
    message: str
    document: DocumentMetadata