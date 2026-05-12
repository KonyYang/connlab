from __future__ import annotations

from pathlib import Path

import pytest

from backend.infrastructure.office.fee_evaluation_workbook_gateway import (
    FeeEvaluationWorkbookGateway,
)


def test_fee_gateway_rejects_unsupported_template_type(tmp_path: Path) -> None:
    template = tmp_path / "fee.csv"
    template.write_text("x", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported fee template type"):
        FeeEvaluationWorkbookGateway().generate(
            template_path=template,
            output_path=tmp_path / "out.xls",
            preview=None,
        )


def test_fee_gateway_rejects_missing_template(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Template does not exist"):
        FeeEvaluationWorkbookGateway().generate(
            template_path=tmp_path / "missing.xls",
            output_path=tmp_path / "out.xls",
            preview=None,
        )
