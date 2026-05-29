import logging

from fastapi import APIRouter, HTTPException, Request, status

from app.api.dependencies import embedding_service, vector_store
from app.schemas.search import SearchRequest, SearchResponse


router = APIRouter()
logger = logging.getLogger("app.retrieval")


@router.post("/search", response_model=SearchResponse)
def search_documents(
    request: SearchRequest,
    http_request: Request,
) -> SearchResponse:
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

    logger.info(
        "retrieval_completed",
        extra={
            "request_id": getattr(http_request.state, "request_id", None),
            "question": request.question,
            "top_k": request.top_k,
            "result_count": len(results),
            "retrieved_chunk_ids": [result.chunk_id for result in results],
            "scores": [round(result.score, 4) for result in results],
        },
    )

    return SearchResponse(
        question=request.question,
        results=results,
    )