from __future__ import annotations

import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from docx import Document

from backend.application.external_resource_service import (
    ExternalResourceNotFoundError,
    ExternalResourceService,
)
from backend.domain import (
    ExternalResource,
    ExternalResourceType,
    ExternalResourceValidationStatus,
)


def test_external_resource_service_upserts_and_validates_folder_template(
    tmp_path: Path,
) -> None:
    template = tmp_path / "template"
    (template / "{DL_NUMBER}").mkdir(parents=True)
    store = _Store()
    service = ExternalResourceService(store, office=_FakeOffice())

    registered = service.upsert_resource(
        ExternalResourceType.PROJECT_FOLDER_TEMPLATE,
        template,
        active=True,
    )
    validated = service.validate_resource(ExternalResourceType.PROJECT_FOLDER_TEMPLATE)

    assert registered.resource_type is ExternalResourceType.PROJECT_FOLDER_TEMPLATE
    assert validated.validation_status is ExternalResourceValidationStatus.VALID
    assert validated.validation_failure_reason is None
    assert validated.last_validated_at


def test_external_resource_service_records_invalid_excel_reason(tmp_path: Path) -> None:
    missing = tmp_path / "missing.xlsx"
    store = _Store()
    service = ExternalResourceService(store, office=_FakeOffice())
    service.upsert_resource(
        ExternalResourceType.LTR_WORKBOOK,
        missing,
        active=True,
    )

    validated = service.validate_resource(ExternalResourceType.LTR_WORKBOOK)

    assert validated.validation_status is ExternalResourceValidationStatus.INVALID
    assert "Expected an existing file" in (validated.validation_failure_reason or "")


def test_external_resource_service_uses_office_facade_for_docx(tmp_path: Path) -> None:
    template = tmp_path / "template.docx"
    template.write_bytes(b"docx")
    office = _FakeOffice()
    service = ExternalResourceService(_Store(), office=office)
    service.upsert_resource(
        ExternalResourceType.APPLICATION_FORM_TEMPLATE,
        template,
        active=True,
    )

    validated = service.validate_resource(ExternalResourceType.APPLICATION_FORM_TEMPLATE)

    assert validated.validation_status is ExternalResourceValidationStatus.VALID
    assert office.word_reads == [template]


def test_external_resource_service_reads_real_docx_template(tmp_path: Path) -> None:
    template = tmp_path / "application-template.docx"
    document = Document()
    document.add_paragraph("Laboratory Testing Request")
    document.save(template)
    service = ExternalResourceService(_Store())
    service.upsert_resource(
        ExternalResourceType.APPLICATION_FORM_TEMPLATE,
        template,
        active=True,
    )

    validated = service.validate_resource(ExternalResourceType.APPLICATION_FORM_TEMPLATE)

    assert validated.validation_status is ExternalResourceValidationStatus.VALID


def test_external_resource_service_reads_real_xlsx_resource(tmp_path: Path) -> None:
    workbook = tmp_path / "standard-record.xlsx"
    _write_minimal_xlsx(
        workbook,
        "Standard Records",
        ("LTR Number", "Date", "Test Item", "Sample Description"),
    )
    service = ExternalResourceService(_Store())
    service.upsert_resource(
        ExternalResourceType.STANDARD_RECORD_EXCEL,
        workbook,
        active=True,
    )

    validated = service.validate_resource(ExternalResourceType.STANDARD_RECORD_EXCEL)

    assert validated.validation_status is ExternalResourceValidationStatus.VALID


def test_external_resource_service_rejects_xlsx_with_missing_structure(
    tmp_path: Path,
) -> None:
    workbook = tmp_path / "standard-record.xlsx"
    _write_minimal_xlsx(workbook, "Standard Records", ("LTR Number", "Date"))
    service = ExternalResourceService(_Store())
    service.upsert_resource(
        ExternalResourceType.STANDARD_RECORD_EXCEL,
        workbook,
        active=True,
    )

    validated = service.validate_resource(ExternalResourceType.STANDARD_RECORD_EXCEL)

    assert validated.validation_status is ExternalResourceValidationStatus.INVALID
    assert "Missing required headers" in (validated.validation_failure_reason or "")


def test_external_resource_service_rejects_unregistered_resource() -> None:
    service = ExternalResourceService(_Store(), office=_FakeOffice())

    try:
        service.validate_resource(ExternalResourceType.LTR_WORKBOOK)
    except ExternalResourceNotFoundError as exc:
        assert "ltr_workbook" in str(exc)
    else:
        raise AssertionError("Expected missing resource error.")


class _Store:
    """In-memory external resource store for service tests."""

    def __init__(self) -> None:
        self.resources: dict[ExternalResourceType, ExternalResource] = {}

    def list_all(self) -> list[ExternalResource]:
        """Return all resources."""
        return list(self.resources.values())

    def get_by_type(
        self,
        resource_type: ExternalResourceType,
    ) -> ExternalResource | None:
        """Return a resource by type."""
        return self.resources.get(resource_type)

    def upsert(self, resource: ExternalResource) -> ExternalResource:
        """Store a resource."""
        self.resources[resource.resource_type] = resource
        return resource


class _FakeOffice:
    """Fake Office facade for service tests."""

    def __init__(self) -> None:
        self.word_reads: list[Path] = []
        self.excel_reads: list[Path] = []

    def read_word_document(self, source_path: Path) -> object:
        """Record Word reads."""
        self.word_reads.append(source_path)
        return object()

    def read_excel_workbook(self, source_path: Path) -> object:
        """Record Excel reads."""
        self.excel_reads.append(source_path)
        return object()


def _write_minimal_xlsx(
    path: Path,
    sheet_name: str,
    headers: tuple[str, ...],
) -> None:
    """Write a minimal XLSX workbook package with one sheet."""
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "[Content_Types].xml",
            (
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                '<Default Extension="xml" ContentType="application/xml"/>'
                '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                "</Types>"
            ),
        )
        archive.writestr(
            "_rels/.rels",
            (
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
                "</Relationships>"
            ),
        )
        archive.writestr(
            "xl/workbook.xml",
            (
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                f'<sheets><sheet name="{escape(sheet_name)}" sheetId="1" r:id="rId1"/></sheets>'
                "</workbook>"
            ),
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            (
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
                "</Relationships>"
            ),
        )
        archive.writestr(
            "xl/worksheets/sheet1.xml",
            (
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                f"<sheetData>{_header_row_xml(headers)}</sheetData>"
                "</worksheet>"
            ),
        )


def _header_row_xml(headers: tuple[str, ...]) -> str:
    """Return one XLSX row with inline header strings."""
    cells = []
    for column_index, value in enumerate(headers):
        reference = f"{chr(65 + column_index)}1"
        cells.append(f'<c r="{reference}" t="inlineStr"><is><t>{value}</t></is></c>')
    return f'<row r="1">{"".join(cells)}</row>'
