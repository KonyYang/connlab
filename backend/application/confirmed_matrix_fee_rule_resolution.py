"""Resolve Matrix-wide context-sensitive Fee rule matches."""

from __future__ import annotations

from backend.domain import ConfirmedMatrixRow
from backend.modules.fee_evaluation import (
    FeeRuleLibrary,
    FeeRuleMatcher,
    FeeRuleMatchResult,
    normalize_fee_rule_text,
)

_HIGH_TEMPERATURE_LIFE_RULE_ID = "fee_rule_high_temperature_life"
_HIGH_TEMPERATURE_LIFE_ALIASES = {
    "long term high temperature zone load",
}


def build_matrix_fee_rule_matches(
    *,
    rows: tuple[ConfirmedMatrixRow, ...],
    matcher: FeeRuleMatcher,
    library: FeeRuleLibrary,
) -> dict[str, FeeRuleMatchResult]:
    """Return matcher results plus the one approved Matrix exact alias."""
    matches = {
        row.confirmed_row_id: matcher.match_test_item(row.test_item)
        for row in rows
    }
    high_temperature_rule = next(
        (
            rule
            for rule in library.rules
            if rule.rule_id == _HIGH_TEMPERATURE_LIFE_RULE_ID
        ),
        None,
    )
    if high_temperature_rule is not None:
        for row in rows:
            if matches[row.confirmed_row_id].rule is not None:
                continue
            if normalize_fee_rule_text(row.test_item) not in _HIGH_TEMPERATURE_LIFE_ALIASES:
                continue
            matches[row.confirmed_row_id] = FeeRuleMatchResult(
                status="matched",
                rule=high_temperature_rule,
                match_reason="matrix_exact_alias_to_high_temperature_life",
                review_required=high_temperature_rule.review_required,
                review_reason=high_temperature_rule.review_reason,
            )
    return matches
