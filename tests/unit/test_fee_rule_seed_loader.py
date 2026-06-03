from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.modules.fee_evaluation import (
    FeeRuleSeedLoaderError,
    FeeRuleSeedValidationError,
    load_active_fee_rule_library,
    load_fee_rule_library,
)


def test_load_active_fee_rule_library_includes_confirmed_source_metadata() -> None:
    library = load_active_fee_rule_library()

    assert library.version.version_id == "fee_rules_v2026_06_03"
    assert library.version.source_file_name == "Testing Fee Evaluation-Even.xls"
    assert library.version.source_sheet == "Unit Price Reference"
    assert library.version.source_hash == "sha256:b19cce35f774ad3a83260805f7b717d5446f23ca1a90c209a08d8cb7f91fe226"
    assert library.version.effective_from_basis == "project.sample_received_date"
    assert any(rule.rule_id == "fee_rule_report_preparation" for rule in library.rules)


def test_mfg_daily_source_price_is_not_marked_as_per_hour() -> None:
    library = load_active_fee_rule_library()
    mfg_rule = next(rule for rule in library.rules if rule.rule_id == "fee_rule_mfg_class_iia")

    assert mfg_rule.unit_price.text == "1000/day"
    assert mfg_rule.unit_label == "day"
    assert mfg_rule.calculation_strategy == "manual_required"
    assert mfg_rule.review_required is True


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
) -> dict[str, object]:
    return {
        "rule_id": rule_id,
        "display_name": rule_id,
        "aliases": aliases or [rule_id],
        "base_fee": {"amount": 0, "text": "0"},
        "unit_price": {"amount": 10, "text": "10/specimen"},
        "unit_label": "specimen",
        "applicable_standard": "EIA-364-23",
        "range_condition": "N/A",
        "calculation_strategy": calculation_strategy,
        "review_required": False,
        "review_reason": None,
    }
