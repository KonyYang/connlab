from __future__ import annotations

import json
from decimal import Decimal

import pytest

from backend.modules.fee_evaluation import (
    FeeReferenceCandidateRow,
    FeeRuleSeedValidationError,
    FeeRuleVersion,
    build_fee_rule_library_candidate,
    fee_rule_library_to_seed_json,
)


def test_candidate_builder_creates_valid_reviewed_library() -> None:
    library = build_fee_rule_library_candidate(
        version=_version("fee_rules_v2026_06_10"),
        rows=(_candidate_row("fee_rule_visual"),),
    )

    assert library.version.version_id == "fee_rules_v2026_06_10"
    assert library.rules[0].rule_id == "fee_rule_visual"
    assert library.rules[0].unit_price.amount == Decimal("10")


def test_candidate_builder_preserves_review_required_ambiguous_row() -> None:
    library = build_fee_rule_library_candidate(
        version=_version("fee_rules_v2026_06_10"),
        rows=(
            _candidate_row(
                "fee_rule_force",
                unit_price_amount=None,
                unit_price_text="depends on force range",
                review_required=True,
                review_reason="Pricing depends on force range.",
            ),
        ),
    )

    assert library.rules[0].unit_price.amount is None
    assert library.rules[0].review_required is True
    assert library.rules[0].review_reason == "Pricing depends on force range."


def test_candidate_builder_rejects_invalid_unit_label() -> None:
    with pytest.raises(FeeRuleSeedValidationError, match="unsupported unit_label"):
        build_fee_rule_library_candidate(
            version=_version("fee_rules_v2026_06_10"),
            rows=(_candidate_row("fee_rule_bad", unit_label="duration"),),
        )


def test_candidate_builder_rejects_duplicate_aliases() -> None:
    with pytest.raises(FeeRuleSeedValidationError, match="Duplicate alias"):
        build_fee_rule_library_candidate(
            version=_version("fee_rules_v2026_06_10"),
            rows=(
                _candidate_row("fee_rule_a", aliases=("LLCR",)),
                _candidate_row("fee_rule_b", aliases=("llcr",)),
            ),
        )


def test_fee_rule_library_to_seed_json_is_stable_and_loadable() -> None:
    library = build_fee_rule_library_candidate(
        version=_version("fee_rules_v2026_06_10"),
        rows=(_candidate_row("fee_rule_visual"),),
    )

    payload = json.loads(fee_rule_library_to_seed_json(library))

    assert payload["version"]["version_id"] == "fee_rules_v2026_06_10"
    assert payload["rules"][0]["unit_price"] == {"amount": "10", "text": "10/sample"}


def _version(version_id: str) -> FeeRuleVersion:
    return FeeRuleVersion(
        version_id=version_id,
        source_file_name="Testing Fee Evaluation-Even.optimized-v2.xls",
        source_sheet="Unit Price Reference",
        source_hash="sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        effective_from_basis="project.sample_received_date",
        created_at="2026-06-10T00:00:00+08:00",
    )


def _candidate_row(
    rule_id: str,
    *,
    aliases: tuple[str, ...] | None = None,
    unit_price_amount: Decimal | None = Decimal("10"),
    unit_price_text: str = "10/sample",
    unit_label: str = "sample",
    review_required: bool = False,
    review_reason: str | None = None,
) -> FeeReferenceCandidateRow:
    return FeeReferenceCandidateRow(
        rule_id=rule_id,
        display_name=rule_id,
        aliases=aliases or (rule_id,),
        base_fee_amount=Decimal("0"),
        base_fee_text="0",
        unit_price_amount=unit_price_amount,
        unit_price_text=unit_price_text,
        unit_label=unit_label,
        applicable_standard="EIA-364",
        range_condition="N/A",
        calculation_strategy="per_sample",
        review_required=review_required,
        review_reason=review_reason,
    )
