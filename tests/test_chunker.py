from app.services.chunker import TextChunker


def test_chunker_normalizes_text() -> None:
    chunker = TextChunker(chunk_size=100, chunk_overlap=10)

    chunks = chunker.split_text(
        document_id="doc-1",
        text="This\n\nis     a   test\n document.",
    )

    assert len(chunks) == 1
    assert chunks[0].document_id == "doc-1"
    assert chunks[0].chunk_index == 0
    assert chunks[0].text == "This is a test document."


def test_chunker_creates_multiple_chunks() -> None:
    chunker = TextChunker(chunk_size=20, chunk_overlap=5)

    chunks = chunker.split_text(
        document_id="doc-1",
        text="This is a longer document that should be split into multiple chunks.",
    )

    assert len(chunks) > 1
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1