from fastapi.testclient import TestClient

from app.api.endpoints import chat as chat_endpoint
from app.main import app
from app.schemas.agent import AgentResponse


def test_chat_returns_structured_agent_response(monkeypatch):
	async def fake_run_support_agent(message: str) -> AgentResponse:
		assert message == "Check order ORD-1001"
		return AgentResponse(
			intent="order_status",
			reply=(
				"Your order is shipped, with an estimated delivery "
				"date of October 12, 2026."
			),
			confidence=0.95,
			sources=[],
			needs_human=False,
			escalation_reason=None,
		)

	monkeypatch.setattr(
		chat_endpoint,
		"run_support_agent",
		fake_run_support_agent,
	)

	response = TestClient(app).post(
		"/api/v1/chat",
		json={"message": "Check order ORD-1001"},
	)

	assert response.status_code == 200
	assert response.json() == {
		"intent": "order_status",
		"reply": (
			"Your order is shipped, with an estimated delivery "
			"date of October 12, 2026."
		),
		"confidence": 0.95,
		"sources": [],
		"needs_human": False,
		"escalation_reason": None,
	}
