"""Tests for the reviewed fee-rule extension-layer loader."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.modules.fee_evaluation.fee_rule_extensions import (
    FeeRuleExtensionValidationError,
    load_fee_rule_extensions,
)


def test_extension_loader_requires_one_mapping_for_every_source_row(tmp_path: Path) -> None:
    path = _write_extensions(tmp_path, source_rules=_source_rules(4, 47))

    extensions = load_fee_rule_extensions(path)

    assert tuple(item.source_row for item in extensions.source_rules) == tuple(range(4, 48))
    assert "fee_rule_reseating" in {rule.rule_id for rule in extensions.extension_rules}


def test_extension_loader_rejects_missing_source_mapping(tmp_path: Path) -> None:
    path = _write_extensions(tmp_path, source_rules=_source_rules(5, 47))

    with pytest.raises(FeeRuleExtensionValidationError, match="Missing source mappings: 4"):
        load_fee_rule_extensions(path)


def test_extension_loader_rejects_duplicate_rule_ids(tmp_path: Path) -> None:
    mappings = _source_rules(4, 47)
    mappings[1]["rule_id"] = mappings[0]["rule_id"]
    path = _write_extensions(tmp_path, source_rules=mappings)

    with pytest.raises(FeeRuleExtensionValidationError, match="Duplicate rule_id"):
        load_fee_rule_extensions(path)


def test_extension_loader_requires_reason_for_reviewed_rule(tmp_path: Path) -> None:
    mappings = _source_rules(4, 47)
    mappings[0].update(review_required=True, review_reason=None)
    path = _write_extensions(tmp_path, source_rules=mappings)

    with pytest.raises(FeeRuleExtensionValidationError, match="review_reason"):
        load_fee_rule_extensions(path)


def test_extension_loader_rejects_alias_collision_across_sections(tmp_path: Path) -> None:
    mappings = _source_rules(4, 47)
    mappings[0]["aliases"] = ["Reseating"]
    path = _write_extensions(tmp_path, source_rules=mappings)

    with pytest.raises(FeeRuleExtensionValidationError, match="Duplicate alias"):
        load_fee_rule_extensions(path)


def _write_extensions(
    tmp_path: Path,
    *,
    source_rules: list[dict[str, object]],
) -> Path:
    path = tmp_path / "extensions.json"
    path.write_text(
        json.dumps(
            {
                "version": _version(),
                "source_rules": source_rules,
                "extension_rules": [_extension_rule()],
            }
        ),
        encoding="utf-8",
    )
    return path


def _version() -> dict[str, str]:
    return {
        "version_id": "fee_rules_v2026_07_16",
        "source_file_name": "FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls",
        "source_sheet": "Unit Price Reference",
        "source_hash": "sha256:fb788038631aa0a12f1a052b630513718d9fa1bb64bae647e897e18529ef8a5d",
        "effective_from_basis": "project.sample_received_date",
        "created_at": "2026-07-16T00:00:00+08:00",
    }


def _source_rules(start: int, end: int) -> list[dict[str, object]]:
    return [
        {
            "source_row": source_row,
            "rule_id": f"fee_rule_source_{source_row}",
            "aliases": [f"Source alias {source_row}"],
            "base_fee_amount": None,
            "unit_price_amount": "10",
            "unit_label": "reading",
            "calculation_strategy": "per_reading",
            "review_required": False,
            "review_reason": None,
        }
        for source_row in range(start, end + 1)
    ]


def _extension_rule() -> dict[str, object]:
    return {
        "rule_id": "fee_rule_reseating",
        "display_name": "Reseating",
        "aliases": ["Reseating"],
        "base_fee": {"amount": "0", "text": "0"},
        "unit_price": {"amount": "2", "text": "2/cycle"},
        "unit_label": "cycle",
        "applicable_standard": "Reviewed ConnLab extension",
        "range_condition": "Cycles extracted from Matrix condition; fallback 3 cycles",
        "calculation_strategy": "per_cycle",
        "review_required": False,
        "review_reason": None,
    }
