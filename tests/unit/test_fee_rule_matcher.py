from __future__ import annotations

from decimal import Decimal

from backend.modules.fee_evaluation import FeeRuleMatcher, load_active_fee_rule_library, normalize_fee_rule_text
from backend.modules.fee_evaluation.fee_rule_models import FeeAmount, FeeRule, FeeRuleLibrary, FeeRuleVersion


def test_normalize_fee_rule_text_handles_mixed_language_punctuation() -> None:
    normalized = normalize_fee_rule_text("  Visual Examination, 外观检查  ")

    assert normalized == "visual examination 外观检查"


def test_fee_rule_matcher_supports_exact_alias_match() -> None:
    matcher = FeeRuleMatcher(load_active_fee_rule_library())

    result = matcher.match_test_item("LLCR")

    assert result.status == "matched"
    assert result.rule is not None
    assert result.rule.rule_id == "fee_rule_llcr"
    assert result.review_required is True


def test_fee_rule_matcher_supports_conservative_token_match() -> None:
    matcher = FeeRuleMatcher(load_active_fee_rule_library())

    result = matcher.match_test_item("Visual examination after environmental test")

    assert result.status == "matched"
    assert result.rule is not None
    assert result.rule.rule_id == "fee_rule_visual_exam"
    assert result.match_reason.startswith("token_alias_match:")


def test_fee_rule_matcher_returns_no_match_for_ambiguous_token_match() -> None:
    matcher = FeeRuleMatcher(_ambiguous_library())

    result = matcher.match_test_item("connector visual inspection package")

    assert result.status == "no_rule_match"
    assert result.rule is None
    assert result.review_required is True
    assert "Ambiguous token match" in result.match_reason


def test_fee_rule_matcher_returns_stable_no_match_when_unmatched() -> None:
    matcher = FeeRuleMatcher(load_active_fee_rule_library())

    result = matcher.match_test_item("Laser welding cross section simulation")

    assert result.status == "no_rule_match"
    assert result.rule is None
    assert result.review_reason == "No fee rule match."


def _ambiguous_library() -> FeeRuleLibrary:
    version = FeeRuleVersion(
        version_id="fee_rules_v2026_06_03",
        source_file_name="Testing Fee Evaluation-Even.xls",
        source_sheet="Unit Price Reference",
        source_hash="sha256:b19cce35f774ad3a83260805f7b717d5446f23ca1a90c209a08d8cb7f91fe226",
        effective_from_basis="project.sample_received_date",
        created_at="2026-06-03T00:00:00+08:00",
    )
    amount = FeeAmount(amount=Decimal("0"), text="0")
    return FeeRuleLibrary(
        version=version,
        rules=(
            FeeRule(
                rule_id="rule_visual_a",
                display_name="Visual A",
                aliases=("connector visual inspection",),
                base_fee=amount,
                unit_price=amount,
                unit_label="sample",
                applicable_standard="N/A",
                range_condition="N/A",
                calculation_strategy="per_sample",
                review_required=False,
                review_reason=None,
            ),
            FeeRule(
                rule_id="rule_visual_b",
                display_name="Visual B",
                aliases=("visual inspection package",),
                base_fee=amount,
                unit_price=amount,
                unit_label="sample",
                applicable_standard="N/A",
                range_condition="N/A",
                calculation_strategy="per_sample",
                review_required=False,
                review_reason=None,
            ),
        ),
    )
