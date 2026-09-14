from __future__ import annotations

from pathlib import Path
from hashlib import sha256
import shutil

import pytest
from docx import Document

from backend.infrastructure.office import customer_report_document_gateway as gateway_module
from backend.infrastructure.office.customer_report_document_gateway import (
    CustomerReportDocumentGateway,
)
from backend.infrastructure.office.office_protected_document_gateway import (
    WordPackageProtectionState,
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


def test_customer_report_gateway_retries_transient_word_file_lock(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "internal.docx"
    _minimal_document(source, customer=False)
    template = tmp_path / "E-4515_F.docx"
    _minimal_document(template, customer=True)
    output = tmp_path / "customer.docx"
    attempts = 0
    original_write = gateway_module._write_source_report_sha256

    def write_after_word_releases_file(path: Path, fingerprint: str) -> None:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            lock_error = PermissionError(13, "file is being used", str(path))
            lock_error.winerror = 32
            raise lock_error
        original_write(path, fingerprint)

    monkeypatch.setattr(gateway_module, "_generate_with_word", lambda *_args: None)
    monkeypatch.setattr(
        gateway_module,
        "_write_source_report_sha256",
        write_after_word_releases_file,
    )

    CustomerReportDocumentGateway(
        transient_retry_delay=lambda _seconds: None,
    ).generate_customer_report(
        source_path=source,
        template_path=template,
        output_path=output,
    )

    assert attempts == 2
    assert output.is_file()


def test_customer_report_gateway_does_not_retry_regular_permission_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "internal.docx"
    _minimal_document(source, customer=False)
    template = tmp_path / "E-4515_F.docx"
    _minimal_document(template, customer=True)
    attempts = 0

    def reject_write(_path: Path, _fingerprint: str) -> None:
        nonlocal attempts
        attempts += 1
        raise PermissionError(13, "access denied")

    monkeypatch.setattr(gateway_module, "_generate_with_word", lambda *_args: None)
    monkeypatch.setattr(gateway_module, "_write_source_report_sha256", reject_write)

    with pytest.raises(PermissionError, match="access denied"):
        CustomerReportDocumentGateway(
            transient_retry_delay=lambda _seconds: None,
        ).generate_customer_report(
            source_path=source,
            template_path=template,
            output_path=tmp_path / "customer.docx",
        )

    assert attempts == 1


def test_customer_report_restores_template_password_protection_after_audit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "internal.docx"
    _minimal_document(source, customer=False)
    template = tmp_path / "protected-E-4515_F.docx"
    _minimal_document(template, customer=True)
    output = tmp_path / "customer.docx"
    calls: list[tuple[str, Path]] = []

    class _ProtectedPackageGateway:
        def stage_editable_copy(self, source_path: Path, output_path: Path):
            calls.append(("stage", source_path))
            shutil.copy2(source_path, output_path)
            return WordPackageProtectionState(was_password_protected=True)

        def restore_password_protection(self, editable_path: Path, state) -> None:
            assert state.was_password_protected is True
            assert editable_path.is_file()
            calls.append(("restore", editable_path))

    monkeypatch.setattr(
        "backend.infrastructure.office.customer_report_document_gateway._generate_with_word",
        lambda source_path, target_path: None,
    )

    CustomerReportDocumentGateway(
        protected_package_gateway=_ProtectedPackageGateway(),
    ).generate_customer_report(
        source_path=source,
        template_path=template,
        output_path=output,
    )

    assert calls[0] == ("stage", template)
    assert calls[1][0] == "restore"
    assert output.is_file()


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


def test_customer_report_gateway_reports_word_and_verification_stages(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "internal.docx"
    _minimal_document(source, customer=False)
    template = tmp_path / "E-4515_F.docx"
    _minimal_document(template, customer=True)
    stages: list[str] = []

    def generate_in_word(_source_path, _target_path, *, progress) -> None:
        progress("opening_word")
        progress("copying_content")

    monkeypatch.setattr(gateway_module, "_generate_with_word", generate_in_word)

    CustomerReportDocumentGateway().generate_customer_report(
        source_path=source,
        template_path=template,
        output_path=tmp_path / "customer.docx",
        progress=stages.append,
    )

    assert stages == [
        "preparing_template",
        "opening_word",
        "copying_content",
        "verifying_output",
        "protecting_output",
    ]


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


def test_heading_index_performs_one_lookup_per_heading_and_reuses_matches() -> None:
    class _ParagraphRange:
        def __init__(self, text: str, start: int, end: int) -> None:
            self.Text = text
            self.Start = start
            self.End = end

        @property
        def Duplicate(self):
            return _ParagraphRange(self.Text, self.Start, self.End)

    class _Paragraph:
        def __init__(self, text: str, start: int, end: int) -> None:
            self.Range = _ParagraphRange(text, start, end)

    class _Paragraphs:
        def __init__(self, paragraph: _Paragraph) -> None:
            self._paragraph = paragraph

        def __call__(self, _index: int):
            return self._paragraph

    class _Finder:
        def __init__(self, search) -> None:
            self._search = search
            self.Text = ""

        def ClearFormatting(self) -> None:
            return None

        def Execute(self) -> bool:
            document = self._search._document
            document.lookup_count += 1
            position = document.text.find(
                self.Text,
                self._search.Start,
                self._search.End,
            )
            if position < 0:
                return False
            self._search.Start = position
            self._search.End = position + len(self.Text)
            self._search._paragraph = next(
                paragraph
                for paragraph in document.paragraphs
                if paragraph.Range.Start <= position < paragraph.Range.End
            )
            return True

    class _SearchRange:
        def __init__(self, document, start: int, end: int) -> None:
            self._document = document
            self._paragraph = None
            self.Start = start
            self.End = end

        @property
        def Duplicate(self):
            return _SearchRange(self._document, self.Start, self.End)

        @property
        def Find(self):
            return _Finder(self)

        @property
        def Paragraphs(self):
            return _Paragraphs(self._paragraph)

    class _Document:
        def __init__(self, text: str) -> None:
            self.text = text
            self.lookup_count = 0
            self.paragraphs = []
            start = 0
            for paragraph_text in text.split("\r")[:-1]:
                end = start + len(paragraph_text) + 1
                self.paragraphs.append(
                    _Paragraph(f"{paragraph_text}\r", start, end)
                )
                start = end
            self.Content = _SearchRange(self, 0, len(text))

        def Range(self, start: int, end: int):
            return _SearchRange(self, start, end)

    document = _Document(
        "cover\rPURPOSE\rbody\r2. CONCLUSIONS\rmore body\r"
        "REVISION RECORD\rtail\r"
    )

    headings = gateway_module._NumberedHeadingIndex.from_document(
        document,
        ((1, "PURPOSE"), (2, "CONCLUSIONS"), (8, "REVISION RECORD")),
    )
    purpose, purpose_text = headings.get(1, "PURPOSE")
    conclusions, conclusions_text = headings.get(2, "CONCLUSIONS")
    revision, revision_text = headings.get(8, "REVISION RECORD")
    headings.get(1, "PURPOSE")
    headings.get(8, "REVISION RECORD")

    assert document.lookup_count == 3
    assert (purpose.Start, purpose_text) == (6, "PURPOSE")
    assert (conclusions.Start, conclusions_text) == (19, "2. CONCLUSIONS")
    assert (revision.Start, revision_text) == (44, "REVISION RECORD")


def test_disclosure_scan_returns_only_matching_paragraph_offsets() -> None:
    text = (
        "Customer-visible introduction.\r"
        "This Laboratory Test Report shall not be reproduced except in full.\r"
        "Visible result paragraph.\r"
        "*.: internal note\r"
    )

    spans = gateway_module._internal_disclosure_spans(text)

    assert [text[start:end] for start, end in spans] == [
        "This Laboratory Test Report shall not be reproduced except in full.\r",
        "*.: internal note\r",
    ]


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
