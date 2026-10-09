
from typing import Literal

from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    intent: Literal[
        "shipping",
        "returns",
        "refunds",
        "damaged_product",
        "order_status",
        "product_information",
        "complaint",
        "other",
    ] = Field(
        description="The customer's primary intent"
    )

    reply: str = Field(
        description="The customer-facing support response"
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "Estimated confidence in the intent classification, "
            "from 0.0 to 1.0"
        ),
    )

    sources: list[str] = Field(
        default_factory=list,
        description=(
            "Knowledge-base filenames that support the response"
        ),
    )

    needs_human: bool = Field(
        description="Whether the issue requires human review"
    )

    escalation_reason: str | None = Field(
        default=None,
        description=(
            "Reason for escalation, or null if escalation is not needed"
        ),
    )
