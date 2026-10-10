from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.db.models import Conversation, Message

database_url = make_url(settings.database_url)
if database_url.drivername.startswith("sqlite") and database_url.database not in {
	None,
	":memory:",
}:
	Path(database_url.database).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
	settings.database_url,
	connect_args=(
		{"check_same_thread": False}
		if database_url.drivername.startswith("sqlite")
		else {}
	),
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def initialize_database() -> None:
	_registered_models = (Conversation, Message)
	Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
	with SessionLocal() as session:
		yield session
