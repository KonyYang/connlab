from __future__ import annotations

from pathlib import Path

import pytest
from openpyxl import Workbook, load_workbook

from backend.infrastructure.office.customer_feedback_workbook_gateway import (
    CustomerFeedbackWorkbookGateway,
    CustomerFeedbackWorkbookGatewayError,
)


def test_customer_feedback_workbook_gateway_copies_template_without_overwriting_source(
    tmp_path: Path,
) -> None:
    template = tmp_path / "E-4243_D Customer Feedback Form.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet["A1"] = "LTR Number"
    sheet["A2"] = "Product Description"
    sheet["A3"] = "Requestor"
    workbook.save(template)
    output = tmp_path / "generated" / "feedback.xlsx"

    result_path, warnings = CustomerFeedbackWorkbookGateway().generate(
        template_path=template,
        output_path=output,
        identity={
            "ltr_number": "DL-2026-05-003",
            "product_name": "Connector",
            "requestor": "MP Cao",
        },
    )

    assert result_path == output
    generated = load_workbook(output)
    sheet = generated.active
    assert sheet["B1"].value == "DL-2026-05-003"
    assert sheet["B2"].value == "Connector"
    assert sheet["B3"].value == "MP Cao"
    assert warnings == ()
    source = load_workbook(template)
    assert source.active["B1"].value is None


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
