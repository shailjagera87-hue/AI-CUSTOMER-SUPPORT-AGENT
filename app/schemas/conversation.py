from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from app.schemas.agent import AgentResponse


class ConversationMessage(BaseModel):
	role: Literal["user", "assistant"]
	content: str
	created_at: datetime
	response: AgentResponse | None = None


class ConversationHistory(BaseModel):
	id: UUID
	created_at: datetime
	updated_at: datetime
	messages: list[ConversationMessage]
