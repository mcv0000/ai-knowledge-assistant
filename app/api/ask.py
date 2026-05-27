from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import rag_service
from app.schemas.ask import AskRequest, AskResponse


router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest) -> AskResponse:
    try:
        return rag_service.answer_question(question=request.question)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc