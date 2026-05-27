import json
from pathlib import Path

import faiss
import numpy as np

from app.schemas.chunk import TextChunk
from app.schemas.embedding import ChunkEmbedding
from app.schemas.search import SearchResult


class FaissVectorStore:
    """
    Local FAISS vector store for semantic search.

    We use IndexFlatIP because embeddings are already normalized.
    Inner product on normalized vectors behaves like cosine similarity.
    """

    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.faiss_dir = self.data_dir / "faiss"
        self.index_path = self.faiss_dir / "index.faiss"
        self.metadata_path = self.faiss_dir / "metadata.json"

        self.faiss_dir.mkdir(parents=True, exist_ok=True)

    def build_index(
        self,
        embeddings: list[ChunkEmbedding],
        chunks_by_id: dict[str, TextChunk],
    ) -> int:
        if not embeddings:
            raise ValueError("No embeddings available to build FAISS index.")

        vectors = np.array(
            [item.embedding for item in embeddings],
            dtype="float32",
        )

        if vectors.ndim != 2:
            raise ValueError("Embeddings must be a 2D array.")

        dimension = vectors.shape[1]

        index = faiss.IndexFlatIP(dimension)
        index.add(vectors)

        metadata = []

        for item in embeddings:
            chunk = chunks_by_id.get(item.chunk_id)

            if chunk is None:
                continue

            metadata.append(
                {
                    "document_id": item.document_id,
                    "chunk_id": item.chunk_id,
                    "chunk_index": item.chunk_index,
                    "text": chunk.text,
                }
            )

        if len(metadata) != len(embeddings):
            raise ValueError("Some embeddings do not have matching chunks.")

        faiss.write_index(index, str(self.index_path))

        self.metadata_path.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return index.ntotal

    def search(
        self,
        query_embedding: list[float],
        top_k: int,
    ) -> list[SearchResult]:
        if not self.index_path.exists() or not self.metadata_path.exists():
            raise FileNotFoundError("FAISS index does not exist. Build it first.")

        index = faiss.read_index(str(self.index_path))
        metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))

        query_vector = np.array([query_embedding], dtype="float32")

        scores, indices = index.search(query_vector, top_k)

        results: list[SearchResult] = []

        for score, index_position in zip(scores[0], indices[0], strict=True):
            if index_position == -1:
                continue

            item = metadata[index_position]

            results.append(
                SearchResult(
                    document_id=item["document_id"],
                    chunk_id=item["chunk_id"],
                    chunk_index=item["chunk_index"],
                    text=item["text"],
                    score=float(score),
                )
            )

        return results