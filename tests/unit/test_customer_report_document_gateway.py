from __future__ import annotations

from pathlib import Path

import pytest

from backend.infrastructure.office.customer_report_document_gateway import (
    CustomerReportDocumentGateway,
)


def test_customer_report_gateway_rejects_missing_internal_source(tmp_path: Path) -> None:
    template = tmp_path / "E-4515.docx"
    template.write_bytes(b"template")

    with pytest.raises(FileNotFoundError, match="Internal report source"):
        CustomerReportDocumentGateway().generate_customer_report(
            source_path=tmp_path / "missing.docx",
            template_path=template,
            output_path=tmp_path / "customer.docx",
        )


def test_customer_report_gateway_never_overwrites_source(tmp_path: Path) -> None:
    source = tmp_path / "internal.docx"
    template = tmp_path / "E-4515.docx"
    source.write_bytes(b"internal")
    template.write_bytes(b"template")

    with pytest.raises(ValueError, match="must not replace"):
        CustomerReportDocumentGateway().generate_customer_report(
            source_path=source,
            template_path=template,
            output_path=source,
        )

    assert source.read_bytes() == b"internal"
