from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.repositories.conversation_repository import (
	get_conversation,
	list_messages,
)
from app.db.session import get_db
from app.schemas.agent import AgentResponse
from app.schemas.conversation import ConversationHistory, ConversationMessage

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get("/{conversation_id}", response_model=ConversationHistory)
def read_conversation(
	conversation_id: UUID,
	session: Annotated[Session, Depends(get_db)],
) -> ConversationHistory:
	conversation = get_conversation(session, conversation_id)
	if conversation is None:
		raise HTTPException(status_code=404, detail="Conversation not found.")

	messages = list_messages(session, conversation.id)
	return ConversationHistory(
		id=conversation.id,
		created_at=conversation.created_at,
		updated_at=conversation.updated_at,
		messages=[
			ConversationMessage(
				role=message.role,
				content=message.content,
				created_at=message.created_at,
				response=(
					AgentResponse.model_validate(message.response_payload)
					if message.response_payload
					else None
				),
			)
			for message in messages
		],
	)
