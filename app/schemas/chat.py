
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.agent import AgentResponse


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000,
        description="Message from the customer",
    )
    conversation_id: UUID | None = Field(
        default=None,
        description="Existing conversation ID for a follow-up message",
    )


class ChatResponse(AgentResponse):
    conversation_id: UUID
