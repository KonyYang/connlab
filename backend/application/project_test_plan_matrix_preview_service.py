"""Application service for read-only project test-plan Matrix previews."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from backend.infrastructure.office import OfficeFacade
from backend.modules.test_plan import (
    MatrixGroupPreview,
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
        parser: ProductSpecMatrixParser | None = None,
    ) -> None:
        """Create a Matrix preview service."""
        self._office = office or OfficeFacade()
        self._parser = parser or ProductSpecMatrixParser()

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
        resolved_locations = table_locations or ()
        selected_table_index = _select_table_index(
            table_locations=resolved_locations,
            page_number=command.page_number,
            page_table_index=command.page_table_index,
            table_text_query=command.table_text_query,
        )
        parsed = self._parser.parse_tables(
            snapshot.tables,
            paragraphs=snapshot.paragraphs,
            selected_table_index=selected_table_index,
        )
        capability_status = "supported" if not parsed.blockers else "unsupported"
        selected_location = None
        if parsed.selected_table_index is not None:
            selected_location = next(
                (item for item in resolved_locations if item.table_index == parsed.selected_table_index),
                None,
            )
        return ProjectTestPlanMatrixPreview(
            project_id=command.project_id,
            source_document_path=source_path,
            source_document_name=source_path.name,
            source_format=suffix,
            capability_status=capability_status,
            generated_at=generated_at,
            groups=parsed.groups,
            warnings=parsed.warnings,
            blockers=parsed.blockers,
            selected_table_index=parsed.selected_table_index,
            selected_page_number=selected_location.page_number if selected_location else None,
            selected_page_table_index=selected_location.page_table_index if selected_location else None,
            candidate_tables=tuple(
                {
                    "table_index": item.table_index,
                    "page_number": item.page_number,
                    "page_table_index": item.page_table_index,
                    "preceding_paragraph": item.preceding_paragraph,
                    "text_preview": item.text_preview,
                    "row_count": item.row_count,
                    "column_count": item.column_count,
                }
                for item in resolved_locations
            ),
            preview_pdf_token=preview_pdf_token,
        )


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


def _select_table_index(
    *,
    table_locations: tuple,
    page_number: int | None,
    page_table_index: int | None,
    table_text_query: str | None,
) -> int | None:
    """Resolve a selected table index from optional locator inputs."""
    if page_number is not None and page_table_index is not None:
        for item in table_locations:
            if item.page_number == page_number and item.page_table_index == page_table_index:
                return item.table_index
    query = (table_text_query or "").strip().lower()
    if query:
        for item in table_locations:
            hay = f"{item.preceding_paragraph or ''} {item.text_preview or ''}".lower()
            if query in hay:
                return item.table_index
    return None
