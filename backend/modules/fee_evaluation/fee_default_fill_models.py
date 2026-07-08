"""Shared DTOs for deterministic Fee Evaluation default-fill."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

FeeDefaultField = Literal[
    "spend_time",
    "unit_price",
    "unit_label",
    "units",
    "base_fee",
    "discount_percent",
    "testing_fee",
]
FeeDefaultFieldState = Literal[
    "auto_filled",
    "suggested_review",
    "manual_required",
    "not_available",
]


@dataclass(frozen=True, slots=True)
class FeeFieldMetadata:
    """Field-level default-fill state for one Fee Evaluation line."""

    field: FeeDefaultField
    state: FeeDefaultFieldState
    source: str | None
    message: str | None


@dataclass(frozen=True, slots=True)
class FeeStepQuantityContext:
    """Read-only Matrix Step quantity fact available to fee default-fill."""

    step_token: str
    step_sequence: int
    step_suffix_note: str | None
    test_points_per_sample: str | None
    readings_per_point: str | None
    contact_points_per_sample: str | None
    total_readings: str | None
    source: str | None
    review_required: bool
    review_reason: str | None
    matched: bool


@dataclass(frozen=True, slots=True)
class FeeDefaultFillContext:
    """Matrix facts available to deterministic fee default-fill rules."""

    test_item: str
    method: str
    condition: str
    requirement: str
    sample_quantity_expression: str
    spend_time: str = ""
    step_tokens: tuple[str, ...] = ()
    step_quantities: tuple[FeeStepQuantityContext, ...] = ()


@dataclass(frozen=True, slots=True)
class FeeDefaultFillResult:
    """Default-fill result for one matched fee rule."""

    status: Literal["calculated", "review_required"]
    review_required: bool
    review_reason: str | None
    spend_time: Decimal | None
    unit_label: str
    unit_price: Decimal | None
    units: Decimal | None
    base_fee: Decimal | None
    discount_percent: Decimal | None
    testing_fee: Decimal | None
    field_metadata: tuple[FeeFieldMetadata, ...]
