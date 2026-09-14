from pathlib import Path
from zipfile import ZipFile

import pytest

from backend.application.tools_service import ToolsError, ToolsService
from backend.shared.office_document_password import OFFICE_DOCUMENT_PASSWORD


class FakeWriter:
    def generate_customer_report(
        self,
        *,
        source_path: Path,
        template_path: Path,
        output_path: Path,
        progress=None,
    ) -> Path:
        if progress is not None:
            progress("copying_content")
        output_path.write_bytes(b"customer")
        return output_path


class FakeProtector:
    def __init__(self) -> None:
        self.calls = []

    def encrypt_and_verify(self, *, source_path: Path, output_path: Path, password: str, office_kind: str) -> None:
        self.calls.append((source_path, output_path, password, office_kind))
        output_path.write_bytes(b"encrypted")


def _docx(path: Path, text: str) -> None:
    with ZipFile(path, "w") as package:
        package.writestr("word/document.xml", f"<w:document><w:t>{text}</w:t></w:document>")


def test_customer_report_requires_internal_report_marker(tmp_path: Path) -> None:
    source = tmp_path / "source.docx"
    template = tmp_path / "template.docx"
    output = tmp_path / "customer.docx"
    _docx(source, "ordinary report")
    template.write_bytes(b"template")

    with pytest.raises(ToolsError, match="LABORATORY TEST REPORT"):
        ToolsService(customer_report_writer=FakeWriter(), office_protector=FakeProtector()).generate_customer_report(
            source_path=source, template_path=template, output_path=output
        )


def test_customer_report_writes_a_new_file_for_compatible_source(tmp_path: Path) -> None:
    source = tmp_path / "DL-2026-01-001 Internal.docx"
    template = tmp_path / "template.docx"
    output = tmp_path / "customer.docx"
    _docx(source, "LABORATORY TEST REPORT")
    template.write_bytes(b"template")

    result = ToolsService(customer_report_writer=FakeWriter(), office_protector=FakeProtector()).generate_customer_report(
        source_path=source, template_path=template, output_path=output
    )

    assert result == output
    assert output.read_bytes() == b"customer"
    assert source.read_bytes() != output.read_bytes()


def test_customer_report_forwards_progress_updates(tmp_path: Path) -> None:
    source = tmp_path / "internal.docx"
    template = tmp_path / "template.docx"
    output = tmp_path / "customer.docx"
    _docx(source, "LABORATORY TEST REPORT")
    template.write_bytes(b"template")
    stages: list[str] = []

    ToolsService(
        customer_report_writer=FakeWriter(),
        office_protector=FakeProtector(),
    ).generate_customer_report(
        source_path=source,
        template_path=template,
        output_path=output,
        progress=stages.append,
    )

    assert stages == ["validating", "copying_content"]


def test_encrypt_copy_preserves_source_and_uses_separate_target(tmp_path: Path) -> None:
    source = tmp_path / "report.docx"
    output = tmp_path / "report_Secured.docx"
    source.write_bytes(b"original")
    protector = FakeProtector()

    result = ToolsService(customer_report_writer=FakeWriter(), office_protector=protector).encrypt_copy(
        source_path=source, output_path=output
    )

    assert result == output
    assert source.read_bytes() == b"original"
    assert output.read_bytes() == b"encrypted"
    assert protector.calls[0][2] == OFFICE_DOCUMENT_PASSWORD
    assert protector.calls[0][3] == "word"


@pytest.mark.parametrize(
    ("name", "expected_password"),
    [
        ("DL-2025-09-054 SLDUFNGSL.xlsx", "202509054"),
        ("DL-2026-04-038A SLDUFNGSL.xlsx", "202604038A"),
    ],
)
def test_encrypt_copy_derives_excel_password_from_dl_filename(
    tmp_path: Path, name: str, expected_password: str
) -> None:
    source = tmp_path / name
    output = tmp_path / f"{source.stem}_Secured.xlsx"
    source.write_bytes(b"original")
    protector = FakeProtector()

    ToolsService(customer_report_writer=FakeWriter(), office_protector=protector).encrypt_copy(
        source_path=source, output_path=output
    )

    assert protector.calls[0][2] == expected_password
    assert protector.calls[0][3] == "excel"


def test_encrypt_copy_rejects_excel_without_dl_filename_prefix(tmp_path: Path) -> None:
    source = tmp_path / "measurements.xlsx"
    output = tmp_path / "measurements_Secured.xlsx"
    source.write_bytes(b"original")

    with pytest.raises(ToolsError, match="Excel files must start with DL-YYYY-MM-NNN"):
        ToolsService(customer_report_writer=FakeWriter(), office_protector=FakeProtector()).encrypt_copy(
            source_path=source, output_path=output
        )
