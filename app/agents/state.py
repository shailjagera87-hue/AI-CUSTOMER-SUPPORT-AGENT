

from typing import TypedDict

from app.schemas.agent import AgentResponse


class SupportState(TypedDict):
    message: str
    route: str
    intent: str
    route_confidence: float
    reply: str
    result: AgentResponse | None
