from fastapi import FastAPI

from app.api.routes import router
from app.middleware.request_logging import (
    RequestLoggingMiddleware,
    configure_logging,
)


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title="AI Knowledge Assistant API",
        description="A RAG-based API for document question answering.",
        version="0.1.0",
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.include_router(router)

    return app


app = create_app()