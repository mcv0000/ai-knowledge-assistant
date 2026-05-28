from pydantic import BaseModel, Field


class RetrievalEvaluationRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question used to evaluate retrieval quality.",
    )
    expected_chunk_id: str = Field(
        ...,
        min_length=1,
        description="Chunk ID expected to appear in the retrieved results.",
    )
    top_k: int = Field(
        3,
        ge=1,
        le=10,
        description="Maximum number of chunks to retrieve during evaluation.",
    )


class RetrievalEvaluationResponse(BaseModel):
    question: str
    expected_chunk_id: str
    retrieved_chunk_ids: list[str]
    hit: bool
    rank: int | None
    precision_at_k: float