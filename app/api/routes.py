from fastapi import APIRouter

from app.api.ask import router as ask_router
from app.api.documents import router as documents_router
from app.api.embeddings import router as embeddings_router
from app.api.evaluation import router as evaluation_router
from app.api.health import router as health_router
from app.api.search import router as search_router
from app.api.vector import router as vector_router


router = APIRouter()

router.include_router(health_router)
router.include_router(documents_router)
router.include_router(embeddings_router)
router.include_router(vector_router)
router.include_router(search_router)
router.include_router(ask_router)
router.include_router(evaluation_router)