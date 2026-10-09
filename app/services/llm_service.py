from functools import lru_cache

from langchain_groq import ChatGroq

from app.core.config import settings
from app.schemas.agent import AgentResponse


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    """Create and cache the Groq model."""
    return ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        temperature=0.2,
        max_retries=2,
    )


async def generate_structured_reply(
    message: str,
    context: str,
) -> AgentResponse:
    """Generate a validated customer-support response using Groq."""
    assistant = get_llm().with_structured_output(
        AgentResponse,
        method="function_calling",
    )

    return await assistant.ainvoke(
        [
            (
                "system",
                """You are a polite, concise customer support assistant.
Use the provided context when answering policy or product questions.
Do not invent facts. If the context does not answer the question, say so.
Set needs_human only when human assistance is required, and never claim
that a support ticket has been created unless it has.""",
            ),
            (
                "human",
                f"Customer message: {message}\n\nContext:\n{context}",
            ),
        ]
    )