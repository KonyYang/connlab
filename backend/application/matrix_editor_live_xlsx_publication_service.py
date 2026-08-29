"""Draft-or-formal publication for the Matrix Editor XLSX output."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from backend.application.matrix_editor_live_xlsx_export_service import (
    MatrixEditorLiveXlsxExportCell,
    MatrixEditorLiveXlsxExportGroup,
    MatrixEditorLiveXlsxExportProjection,
    MatrixEditorLiveXlsxExportRequest,
    MatrixEditorLiveXlsxExportRow,
    MatrixEditorLiveXlsxExportSchedule,
    safe_matrix_xlsx_reference,
)
from backend.application.matrix_schedule_planning import calculate_group_test_days
from backend.application.project_lifecycle_write_guard import (
    LifecycleWriteOperation,
    ProjectLifecycleWriteGuard,
)


class WorkspaceLookup(Protocol):
    def get_by_project(self, project_id: str): ...


class MatrixAuthorityMatcher(Protocol):
    def matches_active_authority(
        self,
        project_id: str,
        request: MatrixEditorLiveXlsxExportRequest,
    ) -> bool: ...


class ConfirmedMatrixStore(Protocol):
    def get_active_by_project(self, project_id: str): ...


class ExportService(Protocol):
    def export(self, request: MatrixEditorLiveXlsxExportRequest): ...


class PublicationFileGateway(Protocol):
    def fingerprint(self, path: Path) -> str: ...

    def stage_bytes(
        self,
        *,
        content: bytes,
        staging_dir: Path,
        file_name: str,
    ) -> Path: ...

    def publish(
        self,
        *,
        staged_path: Path,
        target_path: Path,
        conflict_action: str,
        history_dir: Path,
        expected_target_fingerprint: str | None,
    ) -> Path | None: ...


class MatrixEditorLiveXlsxPublicationError(ValueError):
    """Base error for formal Matrix workbook publication."""


class MatrixEditorLiveXlsxPublicationBlockedError(
    MatrixEditorLiveXlsxPublicationError
):
    """Raised when formal publication prerequisites are not satisfied."""


class MatrixEditorLiveXlsxPublicationConflictError(
    MatrixEditorLiveXlsxPublicationError
):
    """Raised when the preview or replacement choice is stale."""


class ConfirmedMatrixLiveXlsxAuthorityMatcher:
    """Compare the exported Matrix fields with active confirmed authority."""

    def __init__(self, confirmed_store: ConfirmedMatrixStore) -> None:
        self._confirmed = confirmed_store

    def matches_active_authority(
        self,
        project_id: str,
        request: MatrixEditorLiveXlsxExportRequest,
    ) -> bool:
        snapshot = self._confirmed.get_active_by_project(project_id)
        if snapshot is None:
            return False
        groups = tuple(snapshot.groups)
        cells = {
            (cell.confirmed_row_id, cell.confirmed_group_id): cell.cell_value
            for cell in snapshot.cells
        }
        group_days = calculate_group_test_days(
            rows=(
                {
                    "row_id": row.confirmed_row_id,
                    "day_expression": row.day_expression,
                    "is_sample_row": False,
                }
                for row in snapshot.rows
            ),
            cells=(
                {
                    "row_id": cell.confirmed_row_id,
                    "group_id": cell.confirmed_group_id,
                    "cell_value": cell.cell_value,
                }
                for cell in snapshot.cells
            ),
            selected_group_ids=(group.confirmed_group_id for group in groups),
        )
        projected_groups = tuple(
            MatrixEditorLiveXlsxExportGroup(
                group.confirmed_group_id,
                group.group_key,
                group.group_label,
                group.sample_quantity_expression,
                f"{_decimal_text(group_days[group.confirmed_group_id])} d",
                getattr(group, "sample_note", None) or "",
            )
            for group in groups
        )
        projected_rows = tuple(
            MatrixEditorLiveXlsxExportRow(
                row.confirmed_row_id,
                row.test_item,
                row.source_section or "",
                row.method or "",
                row.condition or "",
                row.requirement or "",
                tuple(
                    MatrixEditorLiveXlsxExportCell(
                        group.confirmed_group_id,
                        cells.get((row.confirmed_row_id, group.confirmed_group_id), ""),
                    )
                    for group in groups
                ),
                getattr(row, "day_expression", None) or "",
            )
            for row in snapshot.rows
            if any(
                _text(cells.get((row.confirmed_row_id, group.confirmed_group_id), ""))
                for group in groups
            )
        )
        authority = MatrixEditorLiveXlsxExportProjection(
            groups=projected_groups,
            rows=projected_rows,
            schedule=MatrixEditorLiveXlsxExportSchedule(
                post_test_buffer_days=getattr(snapshot.version, "post_test_buffer_days", None) or "",
                sample_received_date=getattr(snapshot.version, "sample_received_date", None) or "",
                planned_test_start_date=getattr(snapshot.version, "planned_test_start_date", None) or "",
                planned_test_complete_date=getattr(snapshot.version, "planned_test_complete_date", None) or "",
                estimated_completion_date=getattr(snapshot.version, "estimated_completion_date", None) or "",
            ),
        )
        return (
            build_matrix_editor_live_xlsx_authority_signature(request)
            == build_matrix_editor_live_xlsx_authority_signature(authority)
        )


def build_matrix_editor_live_xlsx_authority_signature(
    value: MatrixEditorLiveXlsxExportRequest | MatrixEditorLiveXlsxExportProjection,
) -> str:
    """Hash only workbook fields owned by confirmed Matrix authority."""
    payload = {
        "groups": [
            {
                "group_key": _text(group.group_key),
                "group_label": _text(group.group_label),
                "sample_size": _text(group.sample_size),
                "time_display": _text(group.time_display),
                "sample_note": _text(group.sample_note),
            }
            for group in value.groups
        ],
        "rows": [
            {
                "test_item": _text(row.test_item),
                "section": _text(row.section),
                "test_method": _text(row.test_method),
                "condition": _text(row.condition),
                "requirement": _text(row.requirement),
                "day_expression": _text(row.day_expression),
                "steps": [_text(cell.step_text) for cell in row.cells],
            }
            for row in value.rows
        ],
        "schedule": _schedule_signature(value.schedule),
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _text(value: object | None) -> str:
    return str(value or "").strip()


def _schedule_signature(schedule) -> dict[str, str]:
    if schedule is None:
        return {}
    payload = {
        key: _text(getattr(schedule, key))
        for key in (
            "post_test_buffer_days",
            "sample_received_date",
            "planned_test_start_date",
            "planned_test_complete_date",
            "estimated_completion_date",
        )
    }
    return payload if any(payload.values()) else {}


def _decimal_text(value) -> str:
    text = format(value, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


@dataclass(frozen=True, slots=True)
class PreviewMatrixEditorLiveXlsxPublicationCommand:
    project_id: str
    request: MatrixEditorLiveXlsxExportRequest


@dataclass(frozen=True, slots=True)
class ExecuteMatrixEditorLiveXlsxPublicationCommand:
    project_id: str
    request: MatrixEditorLiveXlsxExportRequest
    preview_token: str
    conflict_action: str
    staging_dir: Path


@dataclass(frozen=True, slots=True)
class MatrixEditorLiveXlsxPublicationPreview:
    project_id: str
    mode: str
    status: str
    target_path: Path | None
    target_fingerprint: str | None
    existing_file: bool
    existing_modified_at: str | None
    blockers: tuple[str, ...]
    preview_token: str


@dataclass(frozen=True, slots=True)
class MatrixEditorLiveXlsxPublicationResult:
    project_id: str
    target_path: Path
    archive_path: Path | None
    file_name: str


class MatrixEditorLiveXlsxPublicationService:
    def __init__(
        self,
        *,
        workspace_store: WorkspaceLookup,
        authority_matcher: MatrixAuthorityMatcher,
        export_service: ExportService,
        file_gateway: PublicationFileGateway,
        lifecycle_write_guard: ProjectLifecycleWriteGuard | None = None,
    ) -> None:
        self._workspaces = workspace_store
        self._authority = authority_matcher
        self._export = export_service
        self._files = file_gateway
        self._lifecycle_write_guard = lifecycle_write_guard

    def preview(
        self,
        command: PreviewMatrixEditorLiveXlsxPublicationCommand,
    ) -> MatrixEditorLiveXlsxPublicationPreview:
        workspace = self._workspaces.get_by_project(command.project_id)
        if workspace is None:
            return self._preview_result(command, mode="download")
        if not self._authority.matches_active_authority(
            command.project_id,
            command.request,
        ):
            return self._preview_result(command, mode="download")
        source_book = Path(workspace.source_book_path)
        if not source_book.is_dir():
            return self._preview_result(
                command,
                mode="official",
                status="blocked",
                blockers=("The recorded Source Book folder is missing.",),
            )
        dl_number = _text(getattr(workspace, "dl_number", ""))
        if not dl_number:
            return self._preview_result(
                command,
                mode="official",
                status="blocked",
                blockers=("The project folder is missing its DL/LTR Number.",),
            )
        target = source_book / f"{safe_matrix_xlsx_reference(dl_number)} Matrix.xlsx"
        if target.exists() and not target.is_file():
            return self._preview_result(
                command,
                mode="official",
                status="blocked",
                target_path=target,
                blockers=("The formal Matrix target is not a file.",),
            )
        fingerprint = self._files.fingerprint(target) if target.is_file() else None
        modified_at = (
            datetime.fromtimestamp(target.stat().st_mtime).astimezone().isoformat()
            if fingerprint is not None
            else None
        )
        return self._preview_result(
            command,
            mode="official",
            status="conflict" if fingerprint is not None else "ready",
            target_path=target,
            target_fingerprint=fingerprint,
            existing_modified_at=modified_at,
        )

    def execute(
        self,
        command: ExecuteMatrixEditorLiveXlsxPublicationCommand,
    ) -> MatrixEditorLiveXlsxPublicationResult:
        if self._lifecycle_write_guard is not None:
            self._lifecycle_write_guard.require_write_allowed(
                command.project_id,
                LifecycleWriteOperation.MATRIX_EXPORT_PUBLISH,
            )
        current = self.preview(
            PreviewMatrixEditorLiveXlsxPublicationCommand(
                command.project_id,
                command.request,
            )
        )
        if current.preview_token != command.preview_token:
            raise MatrixEditorLiveXlsxPublicationConflictError(
                "Matrix authority or Source Book target changed after preview. Try again."
            )
        if current.mode != "official" or current.target_path is None:
            raise MatrixEditorLiveXlsxPublicationBlockedError(
                "Confirm Matrix before publishing a formal Matrix workbook."
            )
        if current.status == "blocked":
            raise MatrixEditorLiveXlsxPublicationBlockedError(current.blockers[0])
        action = command.conflict_action.strip().lower()
        if current.existing_file and action not in {"archive", "recycle"}:
            raise MatrixEditorLiveXlsxPublicationConflictError(
                "Choose Archive old file, Move old file to Recycle Bin, or Cancel."
            )
        if not current.existing_file and action != "none":
            raise MatrixEditorLiveXlsxPublicationConflictError(
                "The Matrix workbook conflict no longer exists."
            )
        workspace = self._workspaces.get_by_project(command.project_id)
        if workspace is None:
            raise MatrixEditorLiveXlsxPublicationConflictError(
                "Project workspace changed after preview. Try again."
            )
        export_result = self._export.export(command.request)
        operation_dir = Path(command.staging_dir) / uuid4().hex
        staged_path: Path | None = None
        try:
            staged_path = self._files.stage_bytes(
                content=export_result.content,
                staging_dir=operation_dir,
                file_name=current.target_path.name,
            )
            archive_path = self._files.publish(
                staged_path=staged_path,
                target_path=current.target_path,
                conflict_action=action,
                history_dir=(
                    Path(workspace.local_workspace_path) / "History" / "Matrix"
                ),
                expected_target_fingerprint=current.target_fingerprint,
            )
        finally:
            if staged_path is not None and staged_path.exists():
                staged_path.unlink()
            if operation_dir.is_dir() and not any(operation_dir.iterdir()):
                operation_dir.rmdir()
        return MatrixEditorLiveXlsxPublicationResult(
            project_id=command.project_id,
            target_path=current.target_path,
            archive_path=archive_path,
            file_name=current.target_path.name,
        )

    def _preview_result(
        self,
        command: PreviewMatrixEditorLiveXlsxPublicationCommand,
        *,
        mode: str,
        status: str = "ready",
        target_path: Path | None = None,
        target_fingerprint: str | None = None,
        existing_modified_at: str | None = None,
        blockers: tuple[str, ...] = (),
    ) -> MatrixEditorLiveXlsxPublicationPreview:
        token_payload = {
            "project_id": command.project_id,
            "authority_signature": build_matrix_editor_live_xlsx_authority_signature(
                command.request
            ),
            "mode": mode,
            "status": status,
            "target_path": str(target_path) if target_path else None,
            "target_fingerprint": target_fingerprint,
            "blockers": blockers,
        }
        preview_token = sha256(
            json.dumps(
                token_payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        return MatrixEditorLiveXlsxPublicationPreview(
            project_id=command.project_id,
            mode=mode,
            status=status,
            target_path=target_path,
            target_fingerprint=target_fingerprint,
            existing_file=target_fingerprint is not None,
            existing_modified_at=existing_modified_at,
            blockers=blockers,
            preview_token=preview_token,
        )
