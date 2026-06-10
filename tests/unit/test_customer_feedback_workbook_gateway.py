from __future__ import annotations

from pathlib import Path

import pytest

from backend.infrastructure.office.customer_feedback_workbook_gateway import (
    CustomerFeedbackWorkbookGateway,
    CustomerFeedbackWorkbookGatewayError,
)


def test_customer_feedback_workbook_gateway_copies_template_without_overwriting_source(
    tmp_path: Path,
) -> None:
    template = tmp_path / "E-4243_D Customer Feedback Form.xlsx"
    template.write_bytes(b"template")
    output = tmp_path / "generated" / "feedback.xlsx"

    result_path, warnings = CustomerFeedbackWorkbookGateway().generate(
        template_path=template,
        output_path=output,
        identity={"ltr_number": "DL-2026-05-003"},
    )

    assert result_path == output
    assert output.read_bytes() == b"template"
    assert template.read_bytes() == b"template"
    assert warnings == (
        "Customer Feedback workbook was copied; safe cell filling requires Excel COM implementation.",
    )


def test_customer_feedback_workbook_gateway_rejects_non_xlsx_template(tmp_path: Path) -> None:
    template = tmp_path / "E-4243.xls"
    template.write_bytes(b"template")

    with pytest.raises(CustomerFeedbackWorkbookGatewayError, match=".xlsx"):
        CustomerFeedbackWorkbookGateway().generate(
            template_path=template,
            output_path=tmp_path / "out.xlsx",
            identity={},
        )


def test_customer_feedback_workbook_gateway_rejects_output_equal_to_template(
    tmp_path: Path,
) -> None:
    template = tmp_path / "E-4243.xlsx"
    template.write_bytes(b"template")

    with pytest.raises(CustomerFeedbackWorkbookGatewayError, match="must not overwrite"):
        CustomerFeedbackWorkbookGateway().generate(
            template_path=template,
            output_path=template,
            identity={},
        )
