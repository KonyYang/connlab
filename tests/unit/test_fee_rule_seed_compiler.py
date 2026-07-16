"""Tests for deterministic compilation of fee reference seeds."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from backend.modules.fee_evaluation.fee_reference_snapshot import (
    FeeReferencePolicy,
    FeeReferenceRow,
    FeeReferenceSnapshot,
    FeeReferenceSource,
)
from backend.modules.fee_evaluation.fee_rule_extensions import (
    FeeRuleExtensionSet,
    FeeSourceRuleExtension,
)
from backend.modules.fee_evaluation.fee_rule_models import FeeRuleVersion
from backend.modules.fee_evaluation.fee_rule_seed_compiler import (
    FeeRuleCompileError,
    compile_fee_rule_library,
    compile_fee_rule_seed_files,
)


_HASH = "sha256:fb788038631aa0a12f1a052b630513718d9fa1bb64bae647e897e18529ef8a5d"


def test_compiler_creates_one_base_rule_per_source_row() -> None:
    library = compile_fee_rule_library(_snapshot(), _extensions())

    base_rules = [rule for rule in library.rules if rule.source_kind == "unit_price_reference"]

    assert tuple(rule.source_row for rule in base_rules) == tuple(range(4, 48))
    assert len(base_rules) == 44


def test_compiler_uses_raw_source_text_and_reviewed_numeric_values() -> None:
    library = compile_fee_rule_library(_snapshot(), _extensions())
    ir = next(rule for rule in library.rules if rule.rule_id == "fee_rule_source_30")

    assert ir.source_row == 30
    assert ir.base_fee.text == "（100~300）\n基于样品准备状况决定"
    assert ir.unit_price.text == (
        "测试规格为1分钟/reading: 5/reading\n测试规格为2分钟/reading: 10/reading"
    )
    assert ir.unit_label == "reading"
    assert ir.unit_price.amount is None
    assert ir.review_required is True


def test_compiler_rejects_snapshot_extension_version_mismatch() -> None:
    extensions = replace(
        _extensions(),
        version=replace(_version(), source_hash="sha256:" + "0" * 64),
    )

    with pytest.raises(FeeRuleCompileError, match="source hash"):
        compile_fee_rule_library(_snapshot(), extensions)


def test_compile_file_preserves_output_when_input_validation_fails(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "bad-snapshot.json"
    snapshot_path.write_text("{}", encoding="utf-8")
    output_path = tmp_path / "candidate.json"
    output_path.write_text("preserve-me", encoding="utf-8")

    with pytest.raises(FeeRuleCompileError, match="Unable to compile fee rule seed"):
        compile_fee_rule_seed_files(
            snapshot_path,
            tmp_path / "unused-extensions.json",
            output_path,
        )

    assert output_path.read_text(encoding="utf-8") == "preserve-me"


def _snapshot() -> FeeReferenceSnapshot:
    rows = []
    for source_row in range(4, 48):
        is_ir = source_row == 30
        rows.append(
            FeeReferenceRow(
                source_row=source_row,
                english_description="Insulation Resistance (IR)" if is_ir else f"Source {source_row}",
                chinese_description="绝缘阻抗" if is_ir else "",
                base_fee_text=(
                    "（100~300）\n基于样品准备状况决定" if is_ir else "0"
                ),
                unit_price_text=(
                    "测试规格为1分钟/reading: 5/reading\n"
                    "测试规格为2分钟/reading: 10/reading"
                    if is_ir
                    else "10/reading"
                ),
                applicable_standard="EIA-364",
                range_condition="N/A",
                chamber_or_note="",
            )
        )
    return FeeReferenceSnapshot(
        source=FeeReferenceSource(
            source_file_name="FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls",
            source_sheet="Unit Price Reference",
            source_hash=_HASH,
            captured_at="2026-07-16T00:00:00+08:00",
        ),
        rows=tuple(rows),
        policies=(
            FeeReferencePolicy(
                source_row=49,
                policy_type="discount_principles",
                text="Policy text",
            ),
        ),
    )


def _extensions() -> FeeRuleExtensionSet:
    return FeeRuleExtensionSet(
        version=_version(),
        source_rules=tuple(
            FeeSourceRuleExtension(
                source_row=source_row,
                rule_id=f"fee_rule_source_{source_row}",
                aliases=(f"Reviewed alias {source_row}",),
                base_fee_amount=None,
                unit_price_amount=None if source_row == 30 else Decimal("10"),
                unit_label="reading",
                calculation_strategy="manual_required" if source_row == 30 else "per_reading",
                review_required=source_row == 30,
                review_reason="Confirm IR duration." if source_row == 30 else None,
            )
            for source_row in range(4, 48)
        ),
        extension_rules=(),
    )


def _version() -> FeeRuleVersion:
    return FeeRuleVersion(
        version_id="fee_rules_v2026_07_16",
        source_file_name="FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls",
        source_sheet="Unit Price Reference",
        source_hash=_HASH,
        effective_from_basis="project.sample_received_date",
        created_at="2026-07-16T00:00:00+08:00",
    )
