import asyncio

from app.agents import graph, nodes
from app.schemas.agent import AgentResponse


def test_graph_dispatches_classified_order_request(monkeypatch):
	async def classify_order(_state):
		return {
			"route": "order_lookup",
			"intent": "order_status",
			"route_confidence": 1.0,
		}

	async def handle_order(_state):
		return {"reply": "Order ORD-1234 is shipped."}

	monkeypatch.setattr(graph, "classify_request", classify_order)
	monkeypatch.setattr(graph, "lookup_order_node", handle_order)

	result = asyncio.run(
		graph.build_graph().ainvoke({"message": "Status ORD-1234?"})
	)

	assert result["reply"] == "Order ORD-1234 is shipped."


def test_graph_returns_demo_order_response_without_llm(monkeypatch):
	def unexpected_llm_call():
		raise AssertionError("Explicit order IDs should not require LLM routing")

	monkeypatch.setattr(nodes, "get_llm", unexpected_llm_call)

	response = asyncio.run(
		graph.run_support_agent("Can you check order ORD-1001?")
	)

	assert isinstance(response, AgentResponse)
	assert response.model_dump() == {
		"intent": "order_status",
		"reply": (
			"Demo order ORD-1001 is currently shipped. "
			"Estimated delivery: 2026-10-12."
		),
		"confidence": 1.0,
		"sources": [],
		"needs_human": False,
		"escalation_reason": None,
	}
