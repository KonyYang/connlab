from __future__ import annotations

from pathlib import Path
from hashlib import sha256

import pytest
from docx import Document

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


def test_generated_customer_report_records_current_internal_fingerprint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "internal.docx"
    _minimal_document(source, customer=False)
    template = tmp_path / "E-4515_F.docx"
    _minimal_document(template, customer=True)
    output = tmp_path / "customer.docx"
    monkeypatch.setattr(
        "backend.infrastructure.office.customer_report_document_gateway._generate_with_word",
        lambda source_path, target_path: None,
    )

    gateway = CustomerReportDocumentGateway()
    gateway.generate_customer_report(
        source_path=source,
        template_path=template,
        output_path=output,
    )

    assert gateway.read_source_report_sha256(output) == sha256(source.read_bytes()).hexdigest()
    assert gateway.read_source_report_sha256(template) is None


def test_customer_report_gateway_uses_short_word_working_copy_names(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "internal.docx"
    _minimal_document(source, customer=False)
    template = tmp_path / "E-4515_F.docx"
    _minimal_document(template, customer=True)
    output = tmp_path / ("DL-001-CR " + "Long qualification report name " * 5 + ".docx")
    opened_targets: list[Path] = []

    def capture_word_target(_source_path: Path, target_path: Path) -> None:
        opened_targets.append(Path(target_path))

    monkeypatch.setattr(
        "backend.infrastructure.office.customer_report_document_gateway._generate_with_word",
        capture_word_target,
    )

    CustomerReportDocumentGateway().generate_customer_report(
        source_path=source,
        template_path=template,
        output_path=output,
    )

    assert len(opened_targets) == 1
    assert opened_targets[0].parent == output.parent
    assert len(opened_targets[0].name) <= 64


def test_customer_report_gateway_rejects_internal_disclosure_in_body(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "internal.docx"
    _minimal_document(source, customer=False)
    template = tmp_path / "E-4515_F.docx"
    _minimal_document(template, customer=True)

    def retain_internal_disclosure(_source_path: Path, target_path: Path) -> None:
        document = Document(target_path)
        document.add_paragraph(
            "This Laboratory Test Report shall not be reproduced except in full "
            "unless written permission is received from the Laboratory Manager."
        )
        document.save(target_path)

    monkeypatch.setattr(
        "backend.infrastructure.office.customer_report_document_gateway._generate_with_word",
        retain_internal_disclosure,
    )

    with pytest.raises(ValueError, match="internal-only disclosures"):
        CustomerReportDocumentGateway().generate_customer_report(
            source_path=source,
            template_path=template,
            output_path=tmp_path / "customer.docx",
        )


def test_customer_report_gateway_rejects_template_report_number_placeholder(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "internal.docx"
    _minimal_document(source, customer=False)
    template = tmp_path / "E-4515_F.docx"
    _minimal_document(template, customer=True)
    template_document = Document(template)
    template_document.sections[0].first_page_header.tables[0].cell(2, 0).text = (
        "WW-XXXX-YY-ZZZ-CR"
    )
    template_document.save(template)
    monkeypatch.setattr(
        "backend.infrastructure.office.customer_report_document_gateway._generate_with_word",
        lambda source_path, target_path: None,
    )

    with pytest.raises(ValueError, match="placeholder"):
        CustomerReportDocumentGateway().generate_customer_report(
            source_path=source,
            template_path=template,
            output_path=tmp_path / "customer.docx",
        )


def _minimal_document(path: Path, *, customer: bool) -> None:
    document = Document()
    document.sections[0].different_first_page_header_footer = True
    header = document.sections[0].first_page_header
    table = header.add_table(rows=5, cols=3, width=1)
    table.cell(0, 1).text = "CUSTOMER TEST REPORT" if customer else "LABORATORY TEST REPORT"
    table.cell(2, 0).text = "DL-001-CR" if customer else "DL-001"
    for heading in (
        "PURPOSE",
        "CONCLUSIONS",
        "SAMPLE DESCRIPTION",
        "TEST DESCRIPTION",
        "TEST METHODS/REQUIREMENTS",
        "TEST RESULTS",
        "REVISION RECORD",
    ):
        document.add_paragraph(heading)
    document.save(path)
