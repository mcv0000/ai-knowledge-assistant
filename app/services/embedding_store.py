import json
from pathlib import Path

from app.schemas.embedding import ChunkEmbedding


class EmbeddingStore:
    """
    Stores generated embeddings locally as JSON files.

    This is temporary but useful for learning and debugging.

    In the next step, these embeddings will be loaded into FAISS.
    """

    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.embeddings_dir = self.data_dir / "embeddings"
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)

    def save_embeddings(
        self,
        document_id: str,
        embeddings: list[ChunkEmbedding],
    ) -> None:
        embedding_path = self._get_embedding_path(document_id)
        raw_embeddings = [embedding.model_dump() for embedding in embeddings]

        embedding_path.write_text(
            json.dumps(raw_embeddings, indent=2),
            encoding="utf-8",
        )

    def get_embeddings(self, document_id: str) -> list[ChunkEmbedding]:
        embedding_path = self._get_embedding_path(document_id)

        if not embedding_path.exists():
            return []

        raw_embeddings = json.loads(embedding_path.read_text(encoding="utf-8"))
        return [ChunkEmbedding(**item) for item in raw_embeddings]

    def _get_embedding_path(self, document_id: str) -> Path:
        return self.embeddings_dir / f"{document_id}.json"