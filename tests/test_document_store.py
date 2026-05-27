import pytest

from app.services.document_store import DocumentStore


def test_document_store_saves_and_reads_text_document(tmp_path) -> None:
    store = DocumentStore(data_dir=str(tmp_path))

    metadata = store.save_text_document(
        filename="sample.txt",
        content_type="text/plain",
        content="This is a test document.".encode("utf-8"),
    )

    documents = store.list_documents()
    saved_text = store.read_document_text(metadata.document_id)

    assert len(documents) == 1
    assert metadata.filename == "sample.txt"
    assert metadata.character_count == len("This is a test document.")
    assert saved_text == "This is a test document."


def test_document_store_rejects_non_txt_files(tmp_path) -> None:
    store = DocumentStore(data_dir=str(tmp_path))

    with pytest.raises(ValueError, match="Only .txt files are supported"):
        store.save_text_document(
            filename="sample.pdf",
            content_type="application/pdf",
            content=b"fake pdf content",
        )