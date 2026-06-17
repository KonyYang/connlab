from __future__ import annotations

from pathlib import Path

import pytest

from backend.application.fee_evaluation_template_discovery import (
    FeeEvaluationTemplateAmbiguousError,
    FeeEvaluationTemplateDiscoveryError,
    discover_fee_evaluation_template,
)


def test_discovers_unique_fdqf_e_176_xls_template(tmp_path: Path) -> None:
    template = tmp_path / "FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls"
    template.write_bytes(b"template")
    (tmp_path / "FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xlsx").write_bytes(
        b"wrong extension"
    )
    (tmp_path / "E-4243_D Customer Feedback Form.xlsx").write_bytes(b"other")

    assert discover_fee_evaluation_template(tmp_path) == template


def test_missing_fee_template_reports_required_form_id(tmp_path: Path) -> None:
    tmp_path.mkdir(exist_ok=True)

    with pytest.raises(FeeEvaluationTemplateDiscoveryError, match="FDQF-E-176"):
        discover_fee_evaluation_template(tmp_path)


def test_multiple_fee_templates_are_rejected(tmp_path: Path) -> None:
    (tmp_path / "FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls").write_bytes(
        b"template"
    )
    (tmp_path / "FDQF-E-176 Testing Fee Evaluation_Rev_G-v1.xls").write_bytes(
        b"template"
    )

    with pytest.raises(FeeEvaluationTemplateAmbiguousError, match="exactly one"):
        discover_fee_evaluation_template(tmp_path)
