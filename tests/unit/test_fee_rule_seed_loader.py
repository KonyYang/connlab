from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.modules.fee_evaluation import (
    ALLOWED_UNIT_LABELS,
    FeeRuleSeedLoaderError,
    FeeRuleSeedValidationError,
    load_active_fee_rule_library,
    load_fee_rule_library,
)
from backend.modules.fee_evaluation.fee_rule_seed_loader import _parse_active_seed_name


_SEEDS = Path(__file__).parents[2] / "backend" / "modules" / "fee_evaluation" / "seeds"


def test_load_active_fee_rule_library_uses_complete_reference_snapshot() -> None:
    library = load_active_fee_rule_library()

    assert library.version.version_id == "fee_rules_v2026_07_17_r6"
    assert library.version.source_file_name == "FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls"
    assert library.version.source_sheet == "Unit Price Reference"
    assert library.version.source_hash == (
        "sha256:fb788038631aa0a12f1a052b630513718d9fa1bb64bae647e897e18529ef8a5d"
    )
    assert library.version.effective_from_basis == "project.sample_received_date"
    assert any(rule.rule_id == "fee_rule_report_preparation" for rule in library.rules)


def test_old_seed_loads_with_backward_compatible_provenance_defaults() -> None:
    library = load_fee_rule_library(_SEEDS / "fee_rules_v2026_06_03.json")

    assert all(rule.source_kind == "legacy_seed" for rule in library.rules)
    assert all(rule.source_row is None for rule in library.rules)


def test_compiled_production_seed_is_complete_and_reloadable() -> None:
    library = load_fee_rule_library(_SEEDS / "fee_rules_v2026_07_16.json")

    base_rules = [rule for rule in library.rules if rule.source_kind == "unit_price_reference"]

    assert len(base_rules) == 44
    assert {rule.source_row for rule in base_rules} == set(range(4, 48))


def test_active_seed_manifest_accepts_file_name_only() -> None:
    assert _parse_active_seed_name({"active_seed_name": "fee_rules_v2026_06_03.json"}) == (
        "fee_rules_v2026_06_03.json"
    )


@pytest.mark.parametrize(
    "seed_name",
    [
        "../fee_rules_v2026_06_03.json",
        "subdir/fee_rules_v2026_06_03.json",
        "subdir\\fee_rules_v2026_06_03.json",
        "active_fee_rule_seed.json",
        "fee_rules_v2026_06_03.txt",
    ],
)
def test_active_seed_manifest_rejects_unsafe_seed_names(seed_name: str) -> None:
    with pytest.raises(FeeRuleSeedValidationError):
        _parse_active_seed_name({"active_seed_name": seed_name})


def test_mfg_daily_source_price_is_not_marked_as_per_hour() -> None:
    library = load_active_fee_rule_library()
    mfg_rule = next(rule for rule in library.rules if rule.rule_id == "fee_rule_mfg_class_iia")

    assert mfg_rule.unit_price.text == "1000/day"
    assert mfg_rule.unit_label == "day"
    assert mfg_rule.calculation_strategy == "manual_required"
    assert mfg_rule.review_required is True


def test_allowed_unit_labels_preserve_existing_and_future_fee_units() -> None:
    assert "group" in ALLOWED_UNIT_LABELS
    assert "specimen" in ALLOWED_UNIT_LABELS
    assert "contact" in ALLOWED_UNIT_LABELS
    assert "time" in ALLOWED_UNIT_LABELS
    assert "report" in ALLOWED_UNIT_LABELS


def test_load_fee_rule_library_accepts_compatible_unit_labels(tmp_path: Path) -> None:
    seed_path = tmp_path / "compatible_unit_labels.json"
    seed_path.write_text(
        json.dumps(
            {
                "version": _valid_version(),
                "rules": [
                    _valid_rule("rule_group", aliases=["Group setup"], unit_label="group"),
                    _valid_rule("rule_specimen", aliases=["Specimen setup"], unit_label="specimen"),
                    _valid_rule("rule_contact", aliases=["Contact setup"], unit_label="contact"),
                    _valid_rule("rule_time", aliases=["Per occurrence setup"], unit_label="time"),
                    _valid_rule("rule_report", aliases=["Report setup"], unit_label="report"),
                ],
            }
        ),
        encoding="utf-8",
    )

    library = load_fee_rule_library(seed_path)

    assert [rule.unit_label for rule in library.rules] == [
        "group",
        "specimen",
        "contact",
        "time",
        "report",
    ]


def test_load_fee_rule_library_rejects_unknown_unit_label(tmp_path: Path) -> None:
    seed_path = tmp_path / "bad_unit_label.json"
    payload = {
        "version": _valid_version(),
        "rules": [
            _valid_rule("rule_a", unit_label="duration"),
        ],
    }
    seed_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(FeeRuleSeedValidationError, match="unsupported unit_label"):
        load_fee_rule_library(seed_path)


def test_load_fee_rule_library_rejects_missing_metadata_field(tmp_path: Path) -> None:
    seed_path = tmp_path / "broken.json"
    seed_path.write_text(
        json.dumps(
            {
                "version": {
                    "version_id": "fee_rules_v2026_06_03",
                    "source_file_name": "Testing Fee Evaluation-Even.xls",
                    "source_hash": "sha256:b19cce35f774ad3a83260805f7b717d5446f23ca1a90c209a08d8cb7f91fe226",
                    "effective_from_basis": "project.sample_received_date",
                    "created_at": "2026-06-03T00:00:00+08:00",
                },
                "rules": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(FeeRuleSeedValidationError, match="version.source_sheet"):
        load_fee_rule_library(seed_path)


def test_load_fee_rule_library_rejects_duplicate_aliases(tmp_path: Path) -> None:
    seed_path = tmp_path / "duplicate_alias.json"
    seed_path.write_text(
        json.dumps(
            {
                "version": _valid_version(),
                "rules": [
                    _valid_rule("rule_a", aliases=["LLCR", "低阶接触电阻"]),
                    _valid_rule("rule_b", aliases=["llcr"]),
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(FeeRuleSeedValidationError, match="Duplicate alias"):
        load_fee_rule_library(seed_path)


def test_load_fee_rule_library_rejects_duplicate_rule_ids(tmp_path: Path) -> None:
    seed_path = tmp_path / "duplicate_rule_id.json"
    seed_path.write_text(
        json.dumps(
            {
                "version": _valid_version(),
                "rules": [
                    _valid_rule("rule_a"),
                    _valid_rule("rule_a", aliases=["other alias"]),
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(FeeRuleSeedValidationError, match="Duplicate rule_id"):
        load_fee_rule_library(seed_path)


def test_load_fee_rule_library_rejects_unknown_strategy(tmp_path: Path) -> None:
    seed_path = tmp_path / "bad_strategy.json"
    payload = {
        "version": _valid_version(),
        "rules": [
            _valid_rule("rule_a", calculation_strategy="per_universe"),
        ],
    }
    seed_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(FeeRuleSeedValidationError, match="unsupported calculation_strategy"):
        load_fee_rule_library(seed_path)


def test_load_fee_rule_library_requires_row_for_reference_provenance(tmp_path: Path) -> None:
    seed_path = tmp_path / "missing_source_row.json"
    rule = _valid_rule("rule_a")
    rule.update(source_kind="unit_price_reference", source_row=None)
    seed_path.write_text(
        json.dumps({"version": _valid_version(), "rules": [rule]}),
        encoding="utf-8",
    )

    with pytest.raises(FeeRuleSeedValidationError, match="source_row"):
        load_fee_rule_library(seed_path)


def test_load_fee_rule_library_rejects_non_json_seed(tmp_path: Path) -> None:
    seed_path = tmp_path / "broken.json"
    seed_path.write_text("{not-json}", encoding="utf-8")

    with pytest.raises(FeeRuleSeedLoaderError, match="Invalid JSON"):
        load_fee_rule_library(seed_path)


def _valid_version() -> dict[str, object]:
    return {
        "version_id": "fee_rules_v2026_06_03",
        "source_file_name": "Testing Fee Evaluation-Even.xls",
        "source_sheet": "Unit Price Reference",
        "source_hash": "sha256:b19cce35f774ad3a83260805f7b717d5446f23ca1a90c209a08d8cb7f91fe226",
        "effective_from_basis": "project.sample_received_date",
        "created_at": "2026-06-03T00:00:00+08:00",
    }


def _valid_rule(
    rule_id: str,
    *,
    aliases: list[str] | None = None,
    calculation_strategy: str = "per_sample",
    unit_label: str = "specimen",
) -> dict[str, object]:
    return {
        "rule_id": rule_id,
        "display_name": rule_id,
        "aliases": aliases or [rule_id],
        "base_fee": {"amount": 0, "text": "0"},
        "unit_price": {"amount": 10, "text": "10/specimen"},
        "unit_label": unit_label,
        "applicable_standard": "EIA-364-23",
        "range_condition": "N/A",
        "calculation_strategy": calculation_strategy,
        "review_required": False,
        "review_reason": None,
    }
