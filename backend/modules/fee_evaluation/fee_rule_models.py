"""Typed fee-rule seed models and validation constants."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

CalculationStrategy = Literal[
    "per_sample",
    "per_reading",
    "per_cycle",
    "per_hour",
    "per_photo",
    "per_specimen",
    "fixed_per_group",
    "manual_required",
    "unknown",
]

FeeRuleMatchStatus = Literal["matched", "no_rule_match"]

ALLOWED_CALCULATION_STRATEGIES: tuple[CalculationStrategy, ...] = (
    "per_sample",
    "per_reading",
    "per_cycle",
    "per_hour",
    "per_photo",
    "per_specimen",
    "fixed_per_group",
    "manual_required",
    "unknown",
)

SUPPORTED_EFFECTIVE_FROM_BASES: tuple[str, ...] = ("project.sample_received_date",)


class FeeRuleSeedValidationError(ValueError):
    """Raised when a fee-rule seed file is malformed or internally inconsistent."""


@dataclass(frozen=True, slots=True)
class FeeRuleVersion:
    """Version metadata for one reviewed pricing authority snapshot."""

    version_id: str
    source_file_name: str
    source_sheet: str
    source_hash: str
    effective_from_basis: str
    created_at: str


@dataclass(frozen=True, slots=True)
class FeeAmount:
    """Structured numeric-or-text amount value from the reviewed source sheet."""

    amount: Decimal | None
    text: str


@dataclass(frozen=True, slots=True)
class FeeRule:
    """One deterministic or review-required pricing rule."""

    rule_id: str
    display_name: str
    aliases: tuple[str, ...]
    base_fee: FeeAmount
    unit_price: FeeAmount
    unit_label: str
    applicable_standard: str
    range_condition: str
    calculation_strategy: CalculationStrategy
    review_required: bool
    review_reason: str | None


@dataclass(frozen=True, slots=True)
class FeeRuleLibrary:
    """Version metadata and all reviewed rules for that version."""

    version: FeeRuleVersion
    rules: tuple[FeeRule, ...]


@dataclass(frozen=True, slots=True)
class FeeRuleMatchResult:
    """Stable match outcome for one Matrix-style test item string."""

    status: FeeRuleMatchStatus
    rule: FeeRule | None
    match_reason: str
    review_required: bool
    review_reason: str | None
