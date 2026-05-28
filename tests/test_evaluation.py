from fastapi.testclient import TestClient

import app.api.evaluation as evaluation_api
from app.main import app
from app.schemas.search import SearchResult


client = TestClient(app)


class FakeEmbeddingService:
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        assert texts == ["What are the current limitations?"]
        return [[0.1, 0.2, 0.3]]


class FakeVectorStore:
    def search(self, query_embedding: list[float], top_k: int) -> list[SearchResult]:
        assert query_embedding == [0.1, 0.2, 0.3]
        assert top_k == 3

        return [
            SearchResult(
                document_id="doc-1",
                chunk_id="expected-chunk",
                chunk_index=2,
                text="Current limitations include local JSON storage.",
                score=0.91,
            ),
            SearchResult(
                document_id="doc-1",
                chunk_id="other-chunk",
                chunk_index=0,
                text="The project uses FastAPI.",
                score=0.52,
            ),
        ]


def test_retrieval_evaluation_returns_hit_and_rank(monkeypatch) -> None:
    monkeypatch.setattr(
        evaluation_api,
        "embedding_service",
        FakeEmbeddingService(),
    )
    monkeypatch.setattr(
        evaluation_api,
        "vector_store",
        FakeVectorStore(),
    )

    response = client.post(
        "/evaluation/retrieval",
        json={
            "question": "What are the current limitations?",
            "expected_chunk_id": "expected-chunk",
            "top_k": 3,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "question": "What are the current limitations?",
        "expected_chunk_id": "expected-chunk",
        "retrieved_chunk_ids": ["expected-chunk", "other-chunk"],
        "hit": True,
        "rank": 1,
        "precision_at_k": 1.0,
    }


def test_retrieval_evaluation_returns_miss(monkeypatch) -> None:
    monkeypatch.setattr(
        evaluation_api,
        "embedding_service",
        FakeEmbeddingService(),
    )
    monkeypatch.setattr(
        evaluation_api,
        "vector_store",
        FakeVectorStore(),
    )

    response = client.post(
        "/evaluation/retrieval",
        json={
            "question": "What are the current limitations?",
            "expected_chunk_id": "missing-chunk",
            "top_k": 3,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "question": "What are the current limitations?",
        "expected_chunk_id": "missing-chunk",
        "retrieved_chunk_ids": ["expected-chunk", "other-chunk"],
        "hit": False,
        "rank": None,
        "precision_at_k": 0.0,
    }