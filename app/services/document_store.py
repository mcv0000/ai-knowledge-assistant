import json
import uuid
from pathlib import Path

from app.schemas.document import DocumentMetadata


class DocumentStore:
    """
    Simple local document storage.

    This is intentionally simple for the first version:
    - uploaded text files are saved to data/uploads/
    - metadata is saved to data/documents.json

    Later, chunking and embeddings will read from this storage.
    """

    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.upload_dir = self.data_dir / "uploads"
        self.metadata_path = self.data_dir / "documents.json"

        self.upload_dir.mkdir(parents=True, exist_ok=True)

        if not self.metadata_path.exists():
            self.metadata_path.write_text("[]", encoding="utf-8")

    def save_text_document(
        self,
        filename: str,
        content_type: str | None,
        content: bytes,
    ) -> DocumentMetadata:
        original_filename = Path(filename).name

        if not original_filename.lower().endswith(".txt"):
            raise ValueError("Only .txt files are supported at this stage.")

        text = self._decode_text_content(content)

        document_id = str(uuid.uuid4())
        stored_filename = f"{document_id}_{original_filename}"
        document_path = self.upload_dir / stored_filename

        document_path.write_text(text, encoding="utf-8")

        metadata = DocumentMetadata(
            document_id=document_id,
            filename=original_filename,
            stored_filename=stored_filename,
            content_type=content_type,
            size_bytes=len(content),
            character_count=len(text),
        )

        documents = self.list_documents()
        documents.append(metadata)

        self._save_metadata(documents)

        return metadata

    def list_documents(self) -> list[DocumentMetadata]:
        raw_metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        return [DocumentMetadata(**item) for item in raw_metadata]

    def get_document(self, document_id: str) -> DocumentMetadata | None:
        for document in self.list_documents():
            if document.document_id == document_id:
                return document

        return None

    def read_document_text(self, document_id: str) -> str:
        document = self.get_document(document_id)

        if document is None:
            raise FileNotFoundError(f"Document not found: {document_id}")

        document_path = self.upload_dir / document.stored_filename

        if not document_path.exists():
            raise FileNotFoundError(f"Stored document file not found: {document_id}")

        return document_path.read_text(encoding="utf-8")

    def _save_metadata(self, documents: list[DocumentMetadata]) -> None:
        raw_metadata = [document.model_dump() for document in documents]
        self.metadata_path.write_text(
            json.dumps(raw_metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _decode_text_content(self, content: bytes) -> str:
        supported_encodings = ["utf-8", "utf-8-sig", "utf-16", "cp1250"]

        for encoding in supported_encodings:
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue

        raise ValueError(
            "Could not decode text file. Supported encodings: UTF-8, UTF-16, CP1250."
        )