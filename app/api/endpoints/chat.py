import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.agents.graph import run_support_agent
from app.db.repositories.conversation_repository import (
    ConversationNotFoundError,
    save_exchange,
)
from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/chat",
    response_model=ChatResponse,
    tags=["Chat"],
)
async def chat(
    request: ChatRequest,
    session: Annotated[Session, Depends(get_db)],
) -> ChatResponse:
    try:
        result = await run_support_agent(request.message)
    except Exception as exc:
        logger.exception("Support agent request failed")
        raise HTTPException(
            status_code=502,
            detail="The AI service is temporarily unavailable.",
        ) from exc

    try:
        conversation = save_exchange(
            session,
            request.message,
            result,
            request.conversation_id,
        )
    except ConversationNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        ) from exc
    except SQLAlchemyError as exc:
        session.rollback()
        logger.exception("Failed to store conversation")
        raise HTTPException(
            status_code=503,
            detail="The conversation could not be stored.",
        ) from exc

    return ChatResponse.model_validate(
        {
            **result.model_dump(),
            "conversation_id": conversation.id,
        }
    )
