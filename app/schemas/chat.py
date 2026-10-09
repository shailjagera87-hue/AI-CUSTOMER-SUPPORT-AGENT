
from pydantic import BaseModel, Field

from app.schemas.agent import AgentResponse


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000,
        description="Message from the customer",
    )


class ChatResponse(AgentResponse):
    pass
