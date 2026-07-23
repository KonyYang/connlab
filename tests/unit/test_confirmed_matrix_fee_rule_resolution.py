from __future__ import annotations

import pytest

from backend.application.confirmed_matrix_fee_rule_resolution import (
    build_matrix_fee_rule_matches,
)
from backend.domain import ConfirmedMatrixRow
from backend.modules.fee_evaluation import (
    FeeRuleMatcher,
    load_active_fee_rule_library,
)


def test_approved_temperature_alias_resolves_to_existing_rule() -> None:
    matches = _matches("Long-term high temperature zone load")

    match = matches["row-1"]
    assert match.status == "matched"
    assert match.rule is not None
    assert match.rule.rule_id == "fee_rule_high_temperature_life"
    assert match.match_reason == "matrix_exact_alias_to_high_temperature_life"


@pytest.mark.parametrize(
    "test_item",
    ("Long-term temperature cycle with load", "Long-term damp heat"),
)
def test_rejected_temperature_aliases_remain_unmatched(test_item: str) -> None:
    match = _matches(test_item)["row-1"]

    assert match.status == "no_rule_match"
    assert match.rule is None
    assert match.review_required is True


@pytest.mark.parametrize(
    "items",
    (
        ("CONTACT RESISTANCE",),
        ("CONTACT RESISTANCE", "LOW LEVEL CONTACT RESISTANCE"),
    ),
)
def test_plain_contact_resistance_never_falls_back_to_llcr(
    items: tuple[str, ...],
) -> None:
    match = _matches(*items)["row-1"]

    assert match.status == "matched"
    assert match.rule is not None
    assert match.rule.rule_id == "fee_rule_contact_resistance_specified_current"
    assert "llcr" not in match.match_reason.lower()


def test_existing_matcher_result_is_not_overwritten() -> None:
    match = _matches("CURRENT RATING")["row-1"]

    assert match.status == "matched"
    assert match.rule is not None
    assert match.rule.rule_id == "fee_rule_temperature_rise"
    assert match.match_reason == "exact_alias_match"


def _matches(*test_items: str):
    library = load_active_fee_rule_library()
    rows = tuple(
        ConfirmedMatrixRow(
            confirmed_row_id=f"row-{index}",
            confirmed_matrix_id="matrix-1",
            draft_row_id=f"draft-row-{index}",
            source_row_snapshot_id=f"source-row-{index}",
            row_order=index,
            test_item=test_item,
        )
        for index, test_item in enumerate(test_items, start=1)
    )
    return build_matrix_fee_rule_matches(
        rows=rows,
        matcher=FeeRuleMatcher(library),
        library=library,
    )
