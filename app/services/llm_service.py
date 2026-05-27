from openai import OpenAI

from app.core.config import settings


class LLMService:
    """
    Thin wrapper around the LLM provider.

    This class keeps OpenAI-specific code outside FastAPI routes.
    """

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or settings.openai_model
        self._client: OpenAI | None = None

    def generate_answer(self, question: str, context: str) -> str:
        client = self._get_client()

        response = client.responses.create(
            model=self.model_name,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI Knowledge Assistant. "
                        "Answer the user's question using only the provided context. "
                        "If the answer is not present in the context, say: "
                        "'I don't know based on the provided documents.' "
                        "Do not use outside knowledge."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Context:\n{context}\n\n"
                        f"Question:\n{question}\n\n"
                        "Answer:"
                    ),
                },
            ],
        )

        return response.output_text.strip()

    def _get_client(self) -> OpenAI:
        if not settings.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is missing. Add it to your .env file."
            )

        if self._client is None:
            self._client = OpenAI(api_key=settings.openai_api_key)

        return self._client