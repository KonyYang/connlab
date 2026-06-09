"""Build reviewed candidate fee-rule libraries from structured maintenance rows."""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal

from backend.modules.fee_evaluation.fee_rule_models import (
    CalculationStrategy,
    FeeAmount,
    FeeRule,
    FeeRuleLibrary,
    FeeRuleVersion,
)
from backend.modules.fee_evaluation.fee_rule_seed_loader import validate_fee_rule_library


@dataclass(frozen=True, slots=True)
class FeeReferenceCandidateRow:
    """One reviewed structured row from a Unit Price Reference maintenance source."""

    rule_id: str
    display_name: str
    aliases: tuple[str, ...]
    base_fee_amount: Decimal | None
    base_fee_text: str
    unit_price_amount: Decimal | None
    unit_price_text: str
    unit_label: str
    applicable_standard: str
    range_condition: str
    calculation_strategy: CalculationStrategy
    review_required: bool
    review_reason: str | None


def build_fee_rule_library_candidate(
    *,
    version: FeeRuleVersion,
    rows: tuple[FeeReferenceCandidateRow, ...],
) -> FeeRuleLibrary:
    """Build and validate a fee-rule library candidate from structured rows."""
    library = FeeRuleLibrary(
        version=version,
        rules=tuple(_candidate_row_to_rule(row) for row in rows),
    )
    validate_fee_rule_library(library)
    return library


def fee_rule_library_to_seed_json(library: FeeRuleLibrary) -> str:
    """Serialize a candidate library to stable reviewed-seed JSON."""
    validate_fee_rule_library(library)
    return json.dumps(_library_to_payload(library), ensure_ascii=False, indent=2) + "\n"


def _candidate_row_to_rule(row: FeeReferenceCandidateRow) -> FeeRule:
    return FeeRule(
        rule_id=row.rule_id,
        display_name=row.display_name,
        aliases=row.aliases,
        base_fee=FeeAmount(amount=row.base_fee_amount, text=row.base_fee_text),
        unit_price=FeeAmount(amount=row.unit_price_amount, text=row.unit_price_text),
        unit_label=row.unit_label,
        applicable_standard=row.applicable_standard,
        range_condition=row.range_condition,
        calculation_strategy=row.calculation_strategy,
        review_required=row.review_required,
        review_reason=row.review_reason,
    )


def _library_to_payload(library: FeeRuleLibrary) -> dict[str, object]:
    version = library.version
    return {
        "version": {
            "version_id": version.version_id,
            "source_file_name": version.source_file_name,
            "source_sheet": version.source_sheet,
            "source_hash": version.source_hash,
            "effective_from_basis": version.effective_from_basis,
            "created_at": version.created_at,
        },
        "rules": [
            {
                "rule_id": rule.rule_id,
                "display_name": rule.display_name,
                "aliases": list(rule.aliases),
                "base_fee": _amount_to_payload(rule.base_fee),
                "unit_price": _amount_to_payload(rule.unit_price),
                "unit_label": rule.unit_label,
                "applicable_standard": rule.applicable_standard,
                "range_condition": rule.range_condition,
                "calculation_strategy": rule.calculation_strategy,
                "review_required": rule.review_required,
                "review_reason": rule.review_reason,
            }
            for rule in library.rules
        ],
    }


def _amount_to_payload(amount: FeeAmount) -> dict[str, object]:
    return {
        "amount": str(amount.amount) if amount.amount is not None else None,
        "text": amount.text,
    }
