import uuid

from app.schemas.chunk import TextChunk


class TextChunker:
    """
    Splits documents into overlapping text chunks.

    This is a simple character-based chunker.
    It is not perfect, but it is clear, deterministic, and good enough
    for the first production-style version of this portfolio project.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0.")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative.")

        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, document_id: str, text: str) -> list[TextChunk]:
        clean_text = self._normalize_text(text)

        if not clean_text:
            return []

        chunks: list[TextChunk] = []
        start = 0
        chunk_index = 0

        while start < len(clean_text):
            end = start + self.chunk_size
            chunk_text = clean_text[start:end].strip()

            if chunk_text:
                chunks.append(
                    TextChunk(
                        chunk_id=str(uuid.uuid4()),
                        document_id=document_id,
                        chunk_index=chunk_index,
                        text=chunk_text,
                        character_count=len(chunk_text),
                    )
                )
                chunk_index += 1

            start += self.chunk_size - self.chunk_overlap

        return chunks

    def _normalize_text(self, text: str) -> str:
        return " ".join(text.split())