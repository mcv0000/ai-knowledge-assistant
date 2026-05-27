from fastapi import FastAPI

from app.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Knowledge Assistant API",
        description="A RAG-based API for document question answering.",
        version="0.1.0",
    )

    app.include_router(router)

    return app


app = create_app()