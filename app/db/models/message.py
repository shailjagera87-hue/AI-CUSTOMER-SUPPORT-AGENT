from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Message(Base):
	__tablename__ = "messages"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	conversation_id: Mapped[str] = mapped_column(
		String(36),
		ForeignKey("conversations.id", ondelete="CASCADE"),
		nullable=False,
		index=True,
	)
	role: Mapped[str] = mapped_column(String(20), nullable=False)
	content: Mapped[str] = mapped_column(Text, nullable=False)
	response_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		nullable=False,
		server_default=func.now(),
	)
