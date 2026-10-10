from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.endpoints import chat as chat_endpoint
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.schemas.agent import AgentResponse


def test_chat_returns_structured_agent_response(monkeypatch):
	engine = create_engine(
		"sqlite://",
		connect_args={"check_same_thread": False},
		poolclass=StaticPool,
	)
	Base.metadata.create_all(engine)
	testing_sessions = sessionmaker(bind=engine, autoflush=False)

	def override_get_db():
		with testing_sessions() as session:
			yield session

	async def fake_run_support_agent(message: str) -> AgentResponse:
		assert message in {"Check order ORD-1001", "And where is it now?"}
		return AgentResponse(
			intent="order_status",
			reply="Your order is shipped.",
			confidence=0.95,
			sources=[],
			needs_human=False,
			escalation_reason=None,
		)

	monkeypatch.setattr(chat_endpoint, "run_support_agent", fake_run_support_agent)
	app.dependency_overrides[get_db] = override_get_db

	try:
		with TestClient(app) as client:
			first_response = client.post(
				"/api/v1/chat",
				json={"message": "Check order ORD-1001"},
			)
			assert first_response.status_code == 200
			first_payload = first_response.json()
			conversation_id = first_payload["conversation_id"]
			assert first_payload["intent"] == "order_status"
			assert first_payload["reply"] == "Your order is shipped."
			assert first_payload["confidence"] == 0.95

			second_response = client.post(
				"/api/v1/chat",
				json={
					"message": "And where is it now?",
					"conversation_id": conversation_id,
				},
			)
			assert second_response.status_code == 200
			assert second_response.json()["conversation_id"] == conversation_id

			history_response = client.get(
				f"/api/v1/conversations/{conversation_id}"
			)

		assert history_response.status_code == 200
		history = history_response.json()
		assert [message["role"] for message in history["messages"]] == [
			"user",
			"assistant",
			"user",
			"assistant",
		]
		assert history["messages"][1]["response"]["intent"] == "order_status"
	finally:
		app.dependency_overrides.clear()
		engine.dispose()
