from app.core.config import settings
from app.services.chunk_store import ChunkStore
from app.services.chunker import TextChunker
from app.services.document_store import DocumentStore
from app.services.embedding_service import EmbeddingService
from app.services.embedding_store import EmbeddingStore
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.vector_store import FaissVectorStore


document_store = DocumentStore()
chunker = TextChunker()
chunk_store = ChunkStore()
embedding_service = EmbeddingService()
embedding_store = EmbeddingStore()
vector_store = FaissVectorStore()
llm_service = LLMService()

rag_service = RAGService(
    embedding_service=embedding_service,
    vector_store=vector_store,
    llm_service=llm_service,
    top_k=settings.rag_top_k,
)