import json
from pathlib import Path

from app.schemas.chunk import TextChunk


class ChunkStore:
    """
    Stores generated chunks locally as JSON files.

    Each document gets its own chunk file:
    data/chunks/{document_id}.json
    """

    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.chunks_dir = self.data_dir / "chunks"
        self.chunks_dir.mkdir(parents=True, exist_ok=True)

    def save_chunks(self, document_id: str, chunks: list[TextChunk]) -> None:
        chunk_path = self._get_chunk_path(document_id)
        raw_chunks = [chunk.model_dump() for chunk in chunks]

        chunk_path.write_text(
            json.dumps(raw_chunks, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def get_chunks(self, document_id: str) -> list[TextChunk]:
        chunk_path = self._get_chunk_path(document_id)

        if not chunk_path.exists():
            return []

        raw_chunks = json.loads(chunk_path.read_text(encoding="utf-8"))
        return [TextChunk(**item) for item in raw_chunks]

    def _get_chunk_path(self, document_id: str) -> Path:
        return self.chunks_dir / f"{document_id}.json"