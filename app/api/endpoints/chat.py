import logging

from fastapi import APIRouter, HTTPException

from app.agents.graph import run_support_agent
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/chat",
    response_model=ChatResponse,
    tags=["Chat"],
)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        result = await run_support_agent(request.message)

        return ChatResponse.model_validate(result.model_dump())

    except Exception as exc:
        logger.exception("Support agent request failed")

        raise HTTPException(
            status_code=502,
            detail="The AI service is temporarily unavailable.",
        ) from exc
