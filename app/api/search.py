from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import embedding_service, vector_store
from app.schemas.search import SearchRequest, SearchResponse


router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search_documents(request: SearchRequest) -> SearchResponse:
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

    return SearchResponse(
        question=request.question,
        results=results,
    )