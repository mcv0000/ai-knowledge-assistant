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


def test_chunker_removes_bom_characters() -> None:
    chunker = TextChunker(chunk_size=100, chunk_overlap=10)

    chunks = chunker.split_text(
        document_id="doc-1",
        text="\ufeffï»¿This is a document with broken BOM characters.",
    )

    assert len(chunks) == 1
    assert "\ufeff" not in chunks[0].text
    assert "ï»¿" not in chunks[0].text
    assert chunks[0].text == "This is a document with broken BOM characters."


def test_chunker_merges_small_last_chunk_without_duplicate_overlap() -> None:
    chunker = TextChunker(
        chunk_size=120,
        chunk_overlap=20,
        min_chunk_size=80,
    )

    chunks = chunker.split_text(
        document_id="doc-1",
        text=(
            "FastAPI powers the backend layer for document ingestion and API routing. "
            "SentenceTransformers generate embeddings for semantic search workflows. "
            "FAISS retrieves relevant chunks by comparing query vectors with stored vectors. "
            "OpenAI generates grounded answers from retrieved context and source chunks. "
            "Tiny ending."
        ),
    )

    full_text = " ".join(chunk.text for chunk in chunks)

    assert len(chunks) > 1
    assert chunks[-1].character_count >= 80
    assert "Tiny ending." in chunks[-1].text
    assert "vectors. vectors." not in full_text
    assert "chunks. chunks." not in full_text