from langgraph.graph import END, START, StateGraph

from app.agents.nodes import (
    answer_from_knowledge,
    answer_general,
    calculate_node,
    classify_request,
    escalate_to_human,
    lookup_order_node,
)
from app.agents.state import SupportState
from app.schemas.agent import AgentResponse


def select_handler(state: SupportState) -> str:
    return state["route"]


def build_graph():
    builder = StateGraph(SupportState)

    builder.add_node("classify", classify_request)
    builder.add_node("knowledge_base", answer_from_knowledge)
    builder.add_node("order_lookup", lookup_order_node)
    builder.add_node("calculator", calculate_node)
    builder.add_node("general", answer_general)
    builder.add_node("human", escalate_to_human)
    builder.add_edge(START, "classify")
    builder.add_conditional_edges(
        "classify",
        select_handler,
        {
            "knowledge_base": "knowledge_base",
            "order_lookup": "order_lookup",
            "calculator": "calculator",
            "general": "general",
            "human": "human",
        },
    )

    for handler in (
        "knowledge_base",
        "order_lookup",
        "calculator",
        "general",
        "human",
    ):
        builder.add_edge(handler, END)

    return builder.compile()


support_graph = build_graph()


async def run_support_agent(message: str) -> AgentResponse:
    """Run the support graph and return its structured response."""
    result = await support_graph.ainvoke({"message": message})
    response = result["result"]
    if not isinstance(response, AgentResponse):
        raise TypeError("The support graph did not produce a structured response.")
    return response