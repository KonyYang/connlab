"""Generate Test Status XLSX previews from current Matrix Editor UI state."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Protocol

from backend.application.test_status_workbook_projection import (
    TestStatusGroup,
    TestStatusProjection,
    TestStatusRow,
    build_test_status_projection,
)


class MatrixEditorTestStatusWorkbookGenerationError(ValueError):
    """Raised when current Matrix Editor state cannot generate a workbook."""


class MatrixEditorTestStatusWorkbookGenerationNotFoundError(LookupError):
    """Raised when the target project does not exist."""


class ProjectLookup(Protocol):
    def get(self, project_id: str):
        """Return one project or None."""


class TestStatusWorkbookWriter(Protocol):
    def write(self, *, output_path: Path, projection: TestStatusProjection) -> Path:
        """Write one Test Status workbook."""


@dataclass(frozen=True, slots=True)
class MatrixEditorTestStatusGroupInput:
    group_key: str
    group_label: str
    sample_quantity_expression: str


@dataclass(frozen=True, slots=True)
class MatrixEditorTestStatusRowInput:
    test_item: str
    is_sample_row: bool
    group_values: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class GenerateMatrixEditorTestStatusWorkbookCommand:
    project_id: str
    project_reference: str | None
    output_dir: Path
    groups: tuple[MatrixEditorTestStatusGroupInput, ...]
    rows: tuple[MatrixEditorTestStatusRowInput, ...]


@dataclass(frozen=True, slots=True)
class MatrixEditorTestStatusWorkbookGenerationResult:
    output_path: Path
    file_name: str


class MatrixEditorTestStatusWorkbookGenerationService:
    """Generate one downloadable Test Status workbook from unsaved editor state."""

    def __init__(self, *, project_store: ProjectLookup, writer: TestStatusWorkbookWriter) -> None:
        self._projects = project_store
        self._writer = writer

    def generate(
        self, command: GenerateMatrixEditorTestStatusWorkbookCommand
    ) -> MatrixEditorTestStatusWorkbookGenerationResult:
        project = self._projects.get(command.project_id)
        if project is None:
            raise MatrixEditorTestStatusWorkbookGenerationNotFoundError("Project not found.")
        try:
            projection = build_test_status_projection(
                groups=tuple(
                    TestStatusGroup(
                        group.group_key,
                        group.group_label,
                        group.sample_quantity_expression,
                    )
                    for group in command.groups
                ),
                rows=tuple(
                    TestStatusRow(row.test_item, row.group_values)
                    for row in command.rows
                    if not row.is_sample_row
                ),
            )
        except ValueError as exc:
            raise MatrixEditorTestStatusWorkbookGenerationError(str(exc)) from exc
        command.output_dir.mkdir(parents=True, exist_ok=True)
        project_no = str(getattr(project, "project_no", "") or "").strip()
        preferred_name = (
            str(command.project_reference or "").strip()
            or project_no
            or command.project_id
        )
        safe_name = "".join(
            character if character.isalnum() or character in {"-", " "} else " "
            for character in preferred_name
        ).strip(" .")
        file_name = f"{safe_name} test status.xlsx"
        output_path = command.output_dir / file_name
        try:
            written = self._writer.write(output_path=output_path, projection=projection)
        except (ValueError, FileNotFoundError, OSError) as exc:
            raise MatrixEditorTestStatusWorkbookGenerationError(str(exc)) from exc
        return MatrixEditorTestStatusWorkbookGenerationResult(written, file_name)
