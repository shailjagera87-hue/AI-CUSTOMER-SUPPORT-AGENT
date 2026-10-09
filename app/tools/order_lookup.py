
import re
from typing import Any


# Demo data only. Replace with an authorized order-system integration later.
MOCK_ORDERS: dict[str, dict[str, Any]] = {
    "ORD-1001": {
        "status": "Shipped",
        "estimated_delivery": "2026-10-12",
    },
    "ORD-1002": {
        "status": "Processing",
        "estimated_delivery": None,
    },
    "ORD-1003": {
        "status": "Delivered",
        "estimated_delivery": "2026-10-05",
    },
}


def extract_order_id(message: str) -> str | None:
    match = re.search(
        r"\bORD-\d{4}\b",
        message,
        flags=re.IGNORECASE,
    )
    return match.group(0).upper() if match else None


def lookup_order(order_id: str | None) -> dict[str, Any]:
    if not order_id:
        return {
            "found": False,
            "reason": "missing_order_id",
        }

    order = MOCK_ORDERS.get(order_id)

    if not order:
        return {
            "found": False,
            "reason": "order_not_found",
        }

    return {
        "found": True,
        "order_id": order_id,
        **order,
    }
