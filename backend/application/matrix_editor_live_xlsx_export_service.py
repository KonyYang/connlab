"""Validate a live Matrix Editor snapshot and render an in-memory workbook."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Protocol


class MatrixEditorLiveXlsxExportError(ValueError):
    """Raised when a live export snapshot violates the public contract."""


@dataclass(frozen=True)
class MatrixEditorLiveXlsxExportCell:
    group_id: str
    step_text: str


@dataclass(frozen=True)
class MatrixEditorLiveXlsxExportGroup:
    group_id: str
    group_key: str
    group_label: str
    sample_size: str
    time_display: str


@dataclass(frozen=True)
class MatrixEditorLiveXlsxExportRow:
    row_id: str
    test_item: str
    section: str
    test_method: str
    condition: str
    requirement: str
    cells: tuple[MatrixEditorLiveXlsxExportCell, ...]


@dataclass(frozen=True)
class MatrixEditorLiveXlsxExportRequest:
    source: str
    project_reference: str
    groups: tuple[MatrixEditorLiveXlsxExportGroup, ...]
    rows: tuple[MatrixEditorLiveXlsxExportRow, ...]


@dataclass(frozen=True)
class MatrixEditorLiveXlsxExportProjection:
    groups: tuple[MatrixEditorLiveXlsxExportGroup, ...]
    rows: tuple[MatrixEditorLiveXlsxExportRow, ...]


@dataclass(frozen=True)
class MatrixEditorLiveXlsxExportResult:
    content: bytes
    file_name: str


class MatrixEditorLiveXlsxWorkbookGateway(Protocol):
    def render(self, projection: MatrixEditorLiveXlsxExportProjection) -> bytes:
        """Return XLSX bytes without writing files."""


class MatrixEditorLiveXlsxExportService:
    """Enforce snapshot bounds before invoking the workbook gateway."""

    def __init__(
        self,
        gateway: MatrixEditorLiveXlsxWorkbookGateway,
        *,
        clock: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._gateway = gateway
        self._clock = clock

    def export(
        self, request: MatrixEditorLiveXlsxExportRequest
    ) -> MatrixEditorLiveXlsxExportResult:
        """Validate, freeze, render, and name one live Matrix export."""
        projection = _validate(request)
        content = self._gateway.render(projection)
        safe_reference = _safe_windows_segment(request.project_reference)
        timestamp = self._clock().strftime("%Y%m%d%H%M%S")
        return MatrixEditorLiveXlsxExportResult(
            content=content,
            file_name=f"{safe_reference} Matrix Draft {timestamp}.xlsx",
        )


def _validate(
    request: MatrixEditorLiveXlsxExportRequest,
) -> MatrixEditorLiveXlsxExportProjection:
    if request.source != "matrix_editor_current_ui_state":
        _blocked("Source must be the current Matrix Editor UI state.")
    _required(request.project_reference, 255, "Project reference")
    if not 1 <= len(request.groups) <= 64:
        _blocked("Select between 1 and 64 Groups.")
    if not 1 <= len(request.rows) <= 512:
        _blocked("Export requires between 1 and 512 qualifying rows.")
    group_ids = [_required(group.group_id, 128, "Group id") for group in request.groups]
    group_keys = [_required(group.group_key, 128, "Group key") for group in request.groups]
    if len(set(group_ids)) != len(group_ids) or len(set(group_keys)) != len(group_keys):
        _blocked("Group ids and keys must be unique.")
    for group in request.groups:
        _required(group.group_label, 255, "Group label")
        _limited(group.sample_size, 255, "Sample size")
        _limited(group.time_display, 32, "Time")
    row_ids: list[str] = []
    total_cells = 0
    for row in request.rows:
        row_ids.append(_required(row.row_id, 128, "Row id"))
        for label, value in (
            ("Test item", row.test_item),
            ("Section", row.section),
            ("Test method", row.test_method),
            ("Condition", row.condition),
            ("Requirement", row.requirement),
        ):
            _limited(value, 2048, label)
        total_cells += len(row.cells)
        cell_ids = [_required(cell.group_id, 128, "Cell Group id") for cell in row.cells]
        if cell_ids != group_ids:
            _blocked("Every row must contain one ordered cell for each Group.")
        if not any(cell.step_text.strip() for cell in row.cells):
            _blocked("Every export row must contain a selected-Group step.")
        for cell in row.cells:
            _limited(cell.step_text, 255, "Step text")
    if len(set(row_ids)) != len(row_ids):
        _blocked("Row ids must be unique.")
    if total_cells > 16_384:
        _blocked("Export exceeds the 16,384-cell limit.")
    return MatrixEditorLiveXlsxExportProjection(
        groups=tuple(request.groups), rows=tuple(request.rows)
    )


def _required(value: str, maximum: int, label: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        _blocked(f"{label} is required.")
    _limited(cleaned, maximum, label)
    return cleaned


def _limited(value: str, maximum: int, label: str) -> None:
    if len(value) > maximum:
        _blocked(f"{label} exceeds {maximum} characters.")


def _blocked(message: str) -> None:
    raise MatrixEditorLiveXlsxExportError(message)


_INVALID_WINDOWS = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')
_RESERVED_WINDOWS = re.compile(r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$", re.IGNORECASE)


def _safe_windows_segment(value: str) -> str:
    segment = _INVALID_WINDOWS.sub("_", value.strip()).rstrip(" .")
    if _RESERVED_WINDOWS.fullmatch(segment):
        segment = f"_{segment}"
    segment = segment[:120].rstrip(" .")
    return segment or "Project"
