"""Application service for read-only project test-plan Matrix previews."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from backend.application.project_basic_information_output import (
    ConfirmedBasicInformationReader,
)
from backend.infrastructure.files.pdf_matrix_source_gateway import (
    PdfMatrixSourceGateway,
    PdfMatrixSourceGatewayError,
)
from backend.infrastructure.office import OfficeFacade
from backend.modules.test_plan import (
    MatrixGroupPreview,
    MatrixRowPreview,
    ProductSpecMatrixParser,
)


class ProjectTestPlanMatrixPreviewError(ValueError):
    """Raised when a Matrix preview request is invalid."""


@dataclass(frozen=True, slots=True)
class ProjectTestPlanMatrixPreview:
    """Read-only Matrix preview for a product specification document."""

    project_id: str | None
    source_document_path: Path
    source_document_name: str
    source_format: str
    capability_status: str
    generated_at: str
    groups: tuple[MatrixGroupPreview, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    blockers: tuple[str, ...] = field(default_factory=tuple)
    selected_table_index: int | None = None
    selected_page_number: int | None = None
    selected_page_table_index: int | None = None
    candidate_tables: tuple[dict[str, object], ...] = field(default_factory=tuple)
    preview_pdf_token: str | None = None
    rows: tuple[MatrixRowPreview, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class MatrixPreviewFromPathCommand:
    """Input command for local-path Matrix preview calibration."""

    source_path: Path
    project_id: str | None = None
    page_number: int | None = None
    page_table_index: int | None = None
    table_text_query: str | None = None


class ProjectTestPlanMatrixPreviewService:
    """Coordinate read-only Matrix previews through Office infrastructure."""

    def __init__(
        self,
        *,
        office: OfficeFacade | None = None,
        pdf_gateway: PdfMatrixSourceGateway | None = None,
        parser: ProductSpecMatrixParser | None = None,
        basic_information_reader: ConfirmedBasicInformationReader | None = None,
    ) -> None:
        """Create a Matrix preview service."""
        self._office = office or OfficeFacade()
        self._pdf_gateway = pdf_gateway or PdfMatrixSourceGateway()
        self._parser = parser or ProductSpecMatrixParser()
        self._basic_information = basic_information_reader

    def preview_from_path(
        self,
        command: MatrixPreviewFromPathCommand,
        *,
        preview_pdf_token: str | None = None,
        table_locations: tuple | None = None,
    ) -> ProjectTestPlanMatrixPreview:
        """Return a read-only Matrix preview for a local source path."""
        source_path = Path(command.source_path)
        if not source_path.is_file():
            raise ProjectTestPlanMatrixPreviewError(
                f"Product specification source file not found: {source_path}"
            )
        suffix = source_path.suffix.lower()
        generated_at = datetime.now(timezone.utc).isoformat()
        if suffix == ".pdf":
            try:
                snapshot = self._pdf_gateway.read_pdf_document(source_path)
            except PdfMatrixSourceGatewayError as exc:
                return ProjectTestPlanMatrixPreview(
                    project_id=command.project_id,
                    source_document_path=source_path,
                    source_document_name=source_path.name,
                    source_format=suffix,
                    capability_status="unsupported",
                    generated_at=generated_at,
                    blockers=(str(exc),),
                    preview_pdf_token=preview_pdf_token,
                )
            return _preview_from_snapshot(
                project_id=command.project_id,
                source_path=source_path,
                source_format=suffix,
                generated_at=generated_at,
                parser=self._parser,
                tables=[
                    [list(row) for row in table]
                    for table in snapshot.tables
                ],
                paragraphs=list(snapshot.paragraphs),
                table_locations=snapshot.table_locations,
                page_number=command.page_number,
                page_table_index=command.page_table_index,
                table_text_query=command.table_text_query,
                preview_pdf_token=preview_pdf_token,
                applicable_specifications=self._applicable_specifications(command.project_id),
            )
        if suffix != ".docx":
            status, blocker = _unsupported_format_blocker(suffix)
            return ProjectTestPlanMatrixPreview(
                project_id=command.project_id,
                source_document_path=source_path,
                source_document_name=source_path.name,
                source_format=suffix or "unknown",
                capability_status=status,
                generated_at=generated_at,
                blockers=(blocker,),
            )

        snapshot = self._office.read_word_document(source_path)
        return _preview_from_snapshot(
            project_id=command.project_id,
            source_path=source_path,
            source_format=suffix,
            generated_at=generated_at,
            parser=self._parser,
            tables=snapshot.tables,
            paragraphs=snapshot.paragraphs,
            table_locations=table_locations or (),
            page_number=command.page_number,
            page_table_index=command.page_table_index,
            table_text_query=command.table_text_query,
            preview_pdf_token=preview_pdf_token,
            applicable_specifications=self._applicable_specifications(command.project_id),
        )

    def _applicable_specifications(self, project_id: str | None) -> str | None:
        """Read the current Basic Information specification for preview defaults."""
        if self._basic_information is None or not project_id:
            return None
        snapshot = self._basic_information.get_preview_snapshot(project_id)
        if snapshot is None:
            return None
        return snapshot.values.get("applicable_specifications")

    def convert_legacy_doc_to_docx(self, source_path: Path, output_path: Path) -> Path:
        """Convert a legacy `.doc` source through the Office boundary."""
        return self._office.convert_legacy_doc_to_docx(source_path, output_path)

    def read_word_table_locations(self, source_path: Path) -> tuple:
        """Read table location metadata for upload preview calibration."""
        return self._office.read_word_table_locations(source_path)

    def export_word_preview_pdf(self, source_path: Path, output_pdf_path: Path) -> Path:
        """Export an upload preview source to PDF through the Office boundary."""
        return self._office.export_word_preview_pdf(source_path, output_pdf_path)


def _unsupported_format_blocker(suffix: str) -> tuple[str, str]:
    """Return capability status and blocker for unsupported source formats."""
    if suffix == ".doc":
        return (
            "deferred",
            "Legacy .doc product specifications require a Word COM conversion/read gateway in a later task.",
        )
    if suffix == ".pdf":
        return (
            "deferred",
            "PDF product specifications require a deterministic PDF table extraction gateway in a later task.",
        )
    return (
        "unsupported",
        f"Unsupported product specification format: {suffix or 'unknown'}.",
    )


def _preview_from_snapshot(
    *,
    project_id: str | None,
    source_path: Path,
    source_format: str,
    generated_at: str,
    parser: ProductSpecMatrixParser,
    tables: list[list[list[str]]],
    paragraphs: list[str],
    table_locations: tuple,
    page_number: int | None,
    page_table_index: int | None,
    table_text_query: str | None,
    preview_pdf_token: str | None,
    applicable_specifications: str | None,
) -> ProjectTestPlanMatrixPreview:
    """Parse a neutral document snapshot into a Matrix preview."""
    candidate_tables = tuple(
        {
            "table_index": item.table_index,
            "page_number": item.page_number,
            "page_table_index": item.page_table_index,
            "preceding_paragraph": item.preceding_paragraph,
            "text_preview": item.text_preview,
            "row_count": item.row_count,
            "column_count": item.column_count,
        }
        for item in table_locations
    )
    selected_table_index = _select_table_index(
        table_locations=table_locations,
        page_number=page_number,
        page_table_index=page_table_index,
        table_text_query=table_text_query,
    )
    if selected_table_index is None and _has_explicit_locator(
        page_number=page_number,
        page_table_index=page_table_index,
        table_text_query=table_text_query,
    ):
        return ProjectTestPlanMatrixPreview(
            project_id=project_id,
            source_document_path=source_path,
            source_document_name=source_path.name,
            source_format=source_format,
            capability_status="unsupported",
            generated_at=generated_at,
            blockers=("No table matched the requested Matrix locator.",),
            candidate_tables=candidate_tables,
            preview_pdf_token=preview_pdf_token,
        )
    parsed = parser.parse_tables(
        tables,
        paragraphs=paragraphs,
        selected_table_index=selected_table_index,
        table_contexts={
            item.table_index: (item.preceding_paragraph or "")
            for item in table_locations
        },
        applicable_specifications=applicable_specifications,
    )
    selected_location = None
    location_table_index = (
        parsed.selected_table_index
        if parsed.selected_table_index is not None
        else selected_table_index
    )
    if location_table_index is not None:
        selected_location = _selected_location_for_preview(
            table_locations=table_locations,
            selected_table_index=location_table_index,
            page_number=page_number,
            page_table_index=page_table_index,
        )
    return ProjectTestPlanMatrixPreview(
        project_id=project_id,
        source_document_path=source_path,
        source_document_name=source_path.name,
        source_format=source_format,
        capability_status="supported" if not parsed.blockers else "unsupported",
        generated_at=generated_at,
        groups=parsed.groups,
        warnings=parsed.warnings,
        blockers=parsed.blockers,
        selected_table_index=parsed.selected_table_index,
        selected_page_number=selected_location.page_number if selected_location else None,
        selected_page_table_index=selected_location.page_table_index if selected_location else None,
        candidate_tables=candidate_tables,
        preview_pdf_token=preview_pdf_token,
        rows=parsed.rows,
    )


def _select_table_index(
    *,
    table_locations: tuple,
    page_number: int | None,
    page_table_index: int | None,
    table_text_query: str | None,
) -> int | None:
    """Resolve a selected table index from optional locator inputs."""
    if page_table_index is not None and page_number is None:
        return None
    candidates = list(table_locations)
    if page_number is not None:
        candidates = [item for item in candidates if item.page_number == page_number]
    if page_table_index is not None:
        candidates = [
            item
            for item in candidates
            if item.page_table_index == page_table_index
        ]
    query = (table_text_query or "").strip().lower()
    if query:
        for item in candidates:
            hay = f"{item.preceding_paragraph or ''} {item.text_preview or ''}".lower()
            if query in hay:
                return item.table_index
        return None
    if page_number is not None and len(candidates) == 1:
        return candidates[0].table_index
    if page_number is not None and page_table_index is not None and candidates:
        return candidates[0].table_index
    return None


def _has_explicit_locator(
    *,
    page_number: int | None,
    page_table_index: int | None,
    table_text_query: str | None,
) -> bool:
    """Return whether the operator supplied any table locator value."""
    return (
        page_number is not None
        or page_table_index is not None
        or bool((table_text_query or "").strip())
    )


def _selected_location_for_preview(
    *,
    table_locations: tuple,
    selected_table_index: int,
    page_number: int | None,
    page_table_index: int | None,
) -> object | None:
    """Return the location that best reflects the operator's selector."""
    if page_number is not None and page_table_index is not None:
        requested = next(
            (
                item
                for item in table_locations
                if item.table_index == selected_table_index
                and item.page_number == page_number
                and item.page_table_index == page_table_index
            ),
            None,
        )
        if requested is not None:
            return requested
    return next(
        (item for item in table_locations if item.table_index == selected_table_index),
        None,
    )
