from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from backend.modules.fee_evaluation import (
    FeeAmount,
    FeeRule,
    FeeRuleLibrary,
    FeeRuleVersion,
    diff_fee_rule_libraries,
    load_fee_rule_library,
)


_SEEDS = Path(__file__).parents[2] / "backend" / "modules" / "fee_evaluation" / "seeds"


def test_fee_rule_library_diff_classifies_added_removed_changed_and_unchanged() -> None:
    active = FeeRuleLibrary(
        version=_version("active"),
        rules=(
            _rule("rule_removed"),
            _rule("rule_changed", unit_price=Decimal("10")),
            _rule("rule_unchanged"),
        ),
    )
    candidate = FeeRuleLibrary(
        version=_version("candidate"),
        rules=(
            _rule("rule_added"),
            _rule("rule_changed", unit_price=Decimal("15")),
            _rule("rule_unchanged"),
        ),
    )

    diff = diff_fee_rule_libraries(active, candidate)

    assert diff.added_count == 1
    assert diff.removed_count == 1
    assert diff.changed_count == 1
    assert diff.unchanged_count == 1
    assert [(entry.rule_id, entry.status) for entry in diff.entries] == [
        ("rule_added", "added"),
        ("rule_changed", "changed"),
        ("rule_removed", "removed"),
        ("rule_unchanged", "unchanged"),
    ]


def test_fee_rule_library_diff_reports_alias_and_price_changes() -> None:
    active = FeeRuleLibrary(version=_version("active"), rules=(_rule("rule_a"),))
    candidate_rule = replace(
        _rule("rule_a"),
        aliases=("Rule A", "Visual A"),
        unit_price=FeeAmount(amount=Decimal("20"), text="20/sample"),
    )
    candidate = FeeRuleLibrary(version=_version("candidate"), rules=(candidate_rule,))

    entry = diff_fee_rule_libraries(active, candidate).entries[0]

    assert entry.status == "changed"
    assert {change.field_name for change in entry.field_changes} == {"aliases", "unit_price"}


def test_fee_rule_library_diff_reports_source_provenance_changes() -> None:
    active = FeeRuleLibrary(version=_version("active"), rules=(_rule("rule_a"),))
    candidate = FeeRuleLibrary(
        version=_version("candidate"),
        rules=(
            replace(
                _rule("rule_a"),
                source_kind="unit_price_reference",
                source_row=30,
            ),
        ),
    )

    entry = diff_fee_rule_libraries(active, candidate).entries[0]

    assert {change.field_name for change in entry.field_changes} == {
        "source_kind",
        "source_row",
    }


def test_candidate_diff_preserves_every_existing_rule_id() -> None:
    active = load_fee_rule_library(_SEEDS / "fee_rules_v2026_06_03.json")
    candidate = load_fee_rule_library(_SEEDS / "fee_rules_v2026_07_16.json")

    diff = diff_fee_rule_libraries(active, candidate)

    assert diff.removed_count == 0


def _version(version_id: str) -> FeeRuleVersion:
    return FeeRuleVersion(
        version_id=version_id,
        source_file_name="Testing Fee Evaluation-Even.xls",
        source_sheet="Unit Price Reference",
        source_hash="sha256:b19cce35f774ad3a83260805f7b717d5446f23ca1a90c209a08d8cb7f91fe226",
        effective_from_basis="project.sample_received_date",
        created_at="2026-06-03T00:00:00+08:00",
    )


def _rule(rule_id: str, *, unit_price: Decimal = Decimal("10")) -> FeeRule:
    return FeeRule(
        rule_id=rule_id,
        display_name=rule_id,
        aliases=(rule_id,),
        base_fee=FeeAmount(amount=Decimal("0"), text="0"),
        unit_price=FeeAmount(amount=unit_price, text=f"{unit_price}/sample"),
        unit_label="sample",
        applicable_standard="EIA-364",
        range_condition="N/A",
        calculation_strategy="per_sample",
        review_required=False,
        review_reason=None,
    )
