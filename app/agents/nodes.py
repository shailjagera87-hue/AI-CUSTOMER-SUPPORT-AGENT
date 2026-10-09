
import re

from app.agents.state import SupportState
from app.core.config import settings
from app.rag.retriever import retrieve_context
from app.schemas.agent import AgentResponse
from app.schemas.routing import RouteDecision
from app.services.llm_service import generate_structured_reply, get_llm
from app.tools.calculator import calculate_expression
from app.tools.order_lookup import extract_order_id, lookup_order


async def classify_request(state: SupportState) -> dict:
    if extract_order_id(state["message"]):
        return {
            "route": "order_lookup",
            "intent": "order_status",
            "route_confidence": 1.0,
        }

    classifier = get_llm().with_structured_output(
        RouteDecision,
        method="function_calling",
    )

    decision = await classifier.ainvoke(
        [
            (
                "system",
                """
Classify the customer request and choose exactly one route.

Routing rules:
- Use order_lookup for a request about a specific order's status.
- Use calculator for an explicit arithmetic calculation.
- Use knowledge_base for company policies, shipping, returns,
  refunds, and product information.
- Use human for explicit requests to speak to a person or
  serious complaints that require human judgment.
- Use general for greetings and other ordinary questions.
- Never claim a tool has already been executed.
""",
            ),
            ("human", state["message"]),
        ]
    )

    return {
        "route": decision.route,
        "intent": decision.intent,
        "route_confidence": decision.confidence,
    }


async def answer_from_knowledge(state: SupportState) -> dict:
    context = retrieve_context(state["message"])
    result = await generate_structured_reply(
        message=state["message"],
        context=context,
    )

    return {"reply": result.reply, "result": result}


async def lookup_order_node(state: SupportState) -> dict:
    order_id = extract_order_id(state["message"])
    order = lookup_order(order_id)

    if not order["found"]:
        reason = order["reason"]

        reply = (
            "Please provide your order number in the format ORD-1234 "
            "so I can check the demo order records."
            if reason == "missing_order_id"
            else "I couldn't find that order in the demo records. "
                 "A support agent can help verify the order."
        )

        result = AgentResponse(
            intent="order_status",
            reply=reply,
            confidence=0.99,
            sources=[],
            needs_human=reason == "order_not_found",
            escalation_reason=(
                "Order was not found in the demo records."
                if reason == "order_not_found"
                else None
            ),
        )
    else:
        delivery = order["estimated_delivery"]
        delivery_text = (
            f" Estimated delivery: {delivery}."
            if delivery
            else " An estimated delivery date is not available yet."
        )

        result = AgentResponse(
            intent="order_status",
            reply=(
                f"Demo order {order['order_id']} is currently "
                f"{order['status'].lower()}.{delivery_text}"
            ),
            confidence=1.0,
            sources=[],
            needs_human=False,
            escalation_reason=None,
        )

    return {"reply": result.reply, "result": result}


async def calculate_node(state: SupportState) -> dict:
    match = re.search(
        r"(?<![A-Za-z])([0-9][0-9\s.+*/()\-]{0,99})",
        state["message"],
    )

    if not match:
        result = AgentResponse(
            intent="other",
            reply="Please provide a basic arithmetic expression, "
                  "such as 25 * 4.",
            confidence=0.95,
            sources=[],
            needs_human=False,
            escalation_reason=None,
        )
    else:
        try:
            value = calculate_expression(match.group(1).strip())
            result = AgentResponse(
                intent="other",
                reply=f"The result is {value:g}.",
                confidence=1.0,
                sources=[],
                needs_human=False,
                escalation_reason=None,
            )
        except (ValueError, SyntaxError, ZeroDivisionError):
            result = AgentResponse(
                intent="other",
                reply="I couldn't calculate that expression. "
                      "Please provide a basic arithmetic expression.",
                confidence=0.95,
                sources=[],
                needs_human=False,
                escalation_reason=None,
            )

    return {"reply": result.reply, "result": result}


async def answer_general(state: SupportState) -> dict:
    result = await generate_structured_reply(
        message=state["message"],
        context="",
    )

    return {"reply": result.reply, "result": result}


async def escalate_to_human(state: SupportState) -> dict:
    result = AgentResponse(
        intent=state["intent"],
        reply=(
            "I can connect you with a human support agent for further "
            "assistance. No support ticket has been created yet."
        ),
        confidence=state["route_confidence"],
        sources=[],
        needs_human=True,
        escalation_reason="The request requires human assistance.",
    )

    return {"reply": result.reply, "result": result}
