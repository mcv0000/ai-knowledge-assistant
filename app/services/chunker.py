import uuid

from app.schemas.chunk import TextChunk


class TextChunker:
    """
    Splits documents into overlapping text chunks.

    This chunker is intentionally simple and deterministic, but avoids
    cutting chunks in the middle of words when possible. Better chunking
    improves retrieval quality because FAISS receives cleaner semantic units.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        min_chunk_size: int = 120,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0.")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative.")

        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")

        if min_chunk_size <= 0:
            raise ValueError("min_chunk_size must be greater than 0.")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    def split_text(self, document_id: str, text: str) -> list[TextChunk]:
        clean_text = self._normalize_text(text)

        if not clean_text:
            return []

        raw_chunks: list[str] = []
        start = 0

        while start < len(clean_text):
            target_end = min(start + self.chunk_size, len(clean_text))
            end = self._find_chunk_boundary(clean_text, start, target_end)

            chunk_text = clean_text[start:end].strip()

            if chunk_text:
                raw_chunks.append(chunk_text)

            if end >= len(clean_text):
                break

            next_start = max(0, end - self.chunk_overlap)
            start = self._move_to_word_boundary(clean_text, next_start)

            if start >= end:
                start = end

        raw_chunks = self._merge_small_last_chunk(raw_chunks)

        chunks: list[TextChunk] = []

        for chunk_index, chunk_text in enumerate(raw_chunks):
            chunks.append(
                TextChunk(
                    chunk_id=str(uuid.uuid4()),
                    document_id=document_id,
                    chunk_index=chunk_index,
                    text=chunk_text,
                    character_count=len(chunk_text),
                )
            )

        return chunks

    def _normalize_text(self, text: str) -> str:
        text = text.replace("\ufeff", "")
        text = text.replace("ï»¿", "")
        return " ".join(text.split())

    def _find_chunk_boundary(self, text: str, start: int, target_end: int) -> int:
        if target_end >= len(text):
            return len(text)

        boundary = text.rfind(" ", start, target_end)

        if boundary <= start:
            return target_end

        return boundary

    def _move_to_word_boundary(self, text: str, start: int) -> int:
        while start < len(text) and not text[start].isspace():
            start += 1

        while start < len(text) and text[start].isspace():
            start += 1

        return start

    def _merge_small_last_chunk(self, chunks: list[str]) -> list[str]:
        if len(chunks) < 2:
            return chunks

        last_chunk = chunks[-1]

        if len(last_chunk) >= self.min_chunk_size:
            return chunks

        previous_chunk = chunks[-2]
        merged_chunk = self._merge_overlapping_text(previous_chunk, last_chunk)

        chunks[-2] = merged_chunk
        chunks.pop()

        return chunks

    def _merge_overlapping_text(self, first_text: str, second_text: str) -> str:
        max_overlap = min(len(first_text), len(second_text))

        for overlap_size in range(max_overlap, 0, -1):
            if first_text[-overlap_size:] == second_text[:overlap_size]:
                return f"{first_text}{second_text[overlap_size:]}".strip()

        return f"{first_text} {second_text}".strip()