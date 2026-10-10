from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Conversation, Message
from app.schemas.agent import AgentResponse


class ConversationNotFoundError(Exception):
	pass


def save_exchange(
	session: Session,
	message: str,
	response: AgentResponse,
	conversation_id: UUID | None = None,
) -> Conversation:
	if conversation_id is None:
		conversation = Conversation(id=str(uuid4()))
		session.add(conversation)
		session.flush()
	else:
		conversation = session.get(Conversation, str(conversation_id))
		if conversation is None:
			raise ConversationNotFoundError

	conversation.updated_at = datetime.now(UTC)
	session.add_all(
		[
			Message(
				conversation_id=conversation.id,
				role="user",
				content=message,
			),
			Message(
				conversation_id=conversation.id,
				role="assistant",
				content=response.reply,
				response_payload=response.model_dump(mode="json"),
			),
		]
	)
	session.commit()
	session.refresh(conversation)
	return conversation


def get_conversation(session: Session, conversation_id: UUID) -> Conversation | None:
	return session.get(Conversation, str(conversation_id))


def list_messages(session: Session, conversation_id: str) -> list[Message]:
	return list(
		session.scalars(
			select(Message)
			.where(Message.conversation_id == conversation_id)
			.order_by(Message.id)
		)
	)
