from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import embedding_service, vector_store
from app.schemas.evaluation import (
    RetrievalEvaluationRequest,
    RetrievalEvaluationResponse,
)


router = APIRouter()


@router.post(
    "/evaluation/retrieval",
    response_model=RetrievalEvaluationResponse,
)
def evaluate_retrieval(
    request: RetrievalEvaluationRequest,
) -> RetrievalEvaluationResponse:
    query_vectors = embedding_service.embed_texts([request.question])
    query_embedding = query_vectors[0]

    try:
        results = vector_store.search(
            query_embedding=query_embedding,
            top_k=request.top_k,
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    retrieved_chunk_ids = [result.chunk_id for result in results]

    rank: int | None = None

    for index, chunk_id in enumerate(retrieved_chunk_ids, start=1):
        if chunk_id == request.expected_chunk_id:
            rank = index
            break

    hit = rank is not None
    precision_at_k = 1.0 if hit else 0.0

    return RetrievalEvaluationResponse(
        question=request.question,
        expected_chunk_id=request.expected_chunk_id,
        retrieved_chunk_ids=retrieved_chunk_ids,
        hit=hit,
        rank=rank,
        precision_at_k=precision_at_k,
    )