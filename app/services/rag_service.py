from app.schemas.ask import AskResponse, Source
from app.schemas.search import SearchResult
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.vector_store import FaissVectorStore


class RAGService:
    """
    Orchestrates the RAG flow:
    question -> embedding -> vector search -> context -> LLM answer.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: FaissVectorStore,
        llm_service: LLMService,
        top_k: int = 3,
    ) -> None:
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.llm_service = llm_service
        self.top_k = top_k

    def answer_question(self, question: str) -> AskResponse:
        query_embedding = self.embedding_service.embed_texts([question])[0]

        search_results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=self.top_k,
        )

        if not search_results:
            return AskResponse(
                answer="I don't know based on the provided documents.",
                sources=[],
            )

        context = self._build_context(search_results)

        answer = self.llm_service.generate_answer(
            question=question,
            context=context,
        )

        sources = [
            Source(
                document_id=result.document_id,
                chunk_id=result.chunk_id,
                text=result.text,
            )
            for result in search_results
        ]

        return AskResponse(
            answer=answer,
            sources=sources,
        )

    def _build_context(self, search_results: list[SearchResult]) -> str:
        context_blocks = []

        for index, result in enumerate(search_results, start=1):
            context_blocks.append(
                "\n".join(
                    [
                        f"[Source {index}]",
                        f"document_id: {result.document_id}",
                        f"chunk_id: {result.chunk_id}",
                        f"score: {result.score}",
                        f"text: {result.text}",
                    ]
                )
            )

        return "\n\n".join(context_blocks)