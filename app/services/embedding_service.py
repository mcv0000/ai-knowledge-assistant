from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Generates dense vector embeddings for text chunks.

    The model is loaded lazily, only when embeddings are first requested.
    This keeps FastAPI startup faster.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> None:
        self.model_name = model_name
        self._model: SentenceTransformer | None = None

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        model = self._get_model()

        embeddings = model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embeddings.astype("float32").tolist()

    def get_embedding_dimension(self, embeddings: list[list[float]]) -> int:
        if not embeddings:
            return 0

        return len(embeddings[0])

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)

        return self._model