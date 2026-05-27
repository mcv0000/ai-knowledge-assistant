from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="The user's question about the ingested documents.",
    )


class Source(BaseModel):
    document_id: str
    chunk_id: str
    text: str


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]