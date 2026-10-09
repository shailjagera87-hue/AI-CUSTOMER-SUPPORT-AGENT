from app.rag.retriever import retrieve_context
from app.tools.order_lookup import lookup_order
from app.tools.calculator import calculate_expression

from langchain_core.tools import tool


@tool
def search_knowledge_base(query: str) -> str:
    """Search company policies, FAQs, shipping, returns, and products."""
    result = retrieve_context(query)
    return str(result)


@tool
def check_order_status(order_id: str) -> str:
    """Retrieve the status of a specific customer order."""
    return str(lookup_order(order_id))


@tool
def calculate(expression: str) -> str:
    """Evaluate a supported arithmetic expression."""
    return str(calculate_expression(expression))


SUPPORT_TOOLS = [
    search_knowledge_base,
    check_order_status,
    calculate,
]