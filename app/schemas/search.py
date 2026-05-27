from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question used to search relevant document chunks.",
    )
    top_k: int = Field(
        3,
        ge=1,
        le=10,
        description="Maximum number of chunks to retrieve.",
    )


class SearchResult(BaseModel):
    document_id: str
    chunk_id: str
    chunk_index: int
    text: str
    score: float


class SearchResponse(BaseModel):
    question: str
    results: list[SearchResult]