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


@dataclass(frozen=True, slots=True)
class MatrixPreviewFromPathCommand:
    """Input command for local-path Matrix preview calibration."""

    source_path: Path
    project_id: str | None = None


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
        parsed = self._parser.parse_tables(snapshot.tables)
        capability_status = "supported" if not parsed.blockers else "unsupported"
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
