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
class CrSpecifiedCurrentAuthority:
    """Typed, exact confirmed CR Measurement Plan authority."""

    confirmed_group_id: str
    confirmed_row_id: str
    step_sequence: int
    step_suffix_note: str
    contact_kind: str
    readings_per_sample: str | None
    revision_id: str | None
    revision_sequence: int | None
    fingerprint: str | None
    diagnostic: str | None = None

    @property
    def is_valid(self) -> bool:
        return bool(
            self.readings_per_sample
            and self.revision_id
            and self.revision_sequence is not None
            and self.fingerprint
            and self.contact_kind == "cr_specified_current"
            and self.diagnostic is None
        )

    @property
    def source(self) -> str:
        """Return deterministic confirmed CR authority lineage metadata."""
        return (
            "Confirmed CR Measurement Plan: "
            f"revision {self.revision_sequence} ({self.revision_id}; {self.fingerprint})"
        )


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
    cr_authority: CrSpecifiedCurrentAuthority | None = None


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
    cr_authority: CrSpecifiedCurrentAuthority | None = None


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
