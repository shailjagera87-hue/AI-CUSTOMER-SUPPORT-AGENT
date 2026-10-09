
from typing import Literal

from pydantic import BaseModel, Field


class RouteDecision(BaseModel):
    route: Literal[
        "knowledge_base",
        "order_lookup",
        "calculator",
        "general",
        "human",
    ] = Field(description="The workflow that should handle the request")

    intent: Literal[
        "shipping",
        "returns",
        "refunds",
        "damaged_product",
        "order_status",
        "product_information",
        "complaint",
        "other",
    ]

    confidence: float = Field(ge=0.0, le=1.0)
