"""Excel-backed authority adapter for LTR commit orchestration."""

from __future__ import annotations

from backend.application.ltr_authority import (
    CommitLtrAuthorityCommand,
    LtrAuthorityCommitError,
    LtrAuthorityCommitResult,
    LtrAuthorityPort,
)
from backend.application.ltr_workbook_write_commit_service import (
    CommitLtrWorkbookWriteCommand,
    LtrWorkbookWriteCommitError,
    LtrWorkbookWriteCommitService,
)
from backend.infrastructure.office import (
    LtrWorkbookBackupError,
    LtrWorkbookLockTimeoutError,
    LtrWorkbookReadOnlyError,
    LtrWorkbookWriteDisabledError,
    LtrWorkbookWriteError,
)


class ExcelWorkbookLtrAuthorityAdapter(LtrAuthorityPort):
    """Adapt workbook write-commit service to the authority boundary."""

    def __init__(self, service: LtrWorkbookWriteCommitService) -> None:
        self._service = service

    def commit_project(
        self,
        project_id: str,
        command: CommitLtrAuthorityCommand,
    ) -> LtrAuthorityCommitResult:
        """Commit one LTR through workbook authority and map to neutral result."""
        try:
            result = self._service.commit_project(
                project_id,
                CommitLtrWorkbookWriteCommand(
                    plan_date=command.plan_date,
                    operator_confirmed=command.operator_confirmed,
                    preview_acknowledged=True,
                    number_input=command.number_input,
                    test_item=command.test_item,
                    sample_description=command.sample_description,
                    location=command.location,
                    test_type_in_sheet=command.test_type_in_sheet,
                    project_leader=command.project_leader,
                    requested_by=command.requested_by,
                    requested_date=command.requested_date,
                    operator_note=command.operator_note,
                ),
            )
        except (LtrWorkbookWriteCommitError, LtrWorkbookWriteError) as exc:
            raise LtrAuthorityCommitError(_authority_commit_error_message(exc)) from exc
        return LtrAuthorityCommitResult(
            ltr=result.ltr,
            workbook_path=str(result.workbook_path),
            workbook_sheet_name=result.pointer.sheet_name,
            workbook_row_number=result.pointer.row_number,
            workbook_backup_path=str(result.backup_path),
        )


def _authority_commit_error_message(exc: Exception) -> str:
    """Return business-readable workbook authority commit guidance."""
    if isinstance(exc, LtrWorkbookLockTimeoutError):
        return (
            "LTR workbook is currently locked by another operator. "
            "Close other Excel sessions or wait, then retry."
        )
    if isinstance(exc, LtrWorkbookReadOnlyError):
        return (
            "LTR workbook opened in read-only mode. "
            "Check modify password and workbook lock state, then retry."
        )
    if isinstance(exc, LtrWorkbookWriteDisabledError):
        return (
            "LTR workbook write is disabled in settings. "
            "Enable write before applying an LTR number."
        )
    if isinstance(exc, LtrWorkbookBackupError):
        return (
            "LTR workbook backup failed before write. "
            "Check workbook path and backup directory access."
        )
    if isinstance(exc, LtrWorkbookWriteError):
        return str(exc)
    return str(exc)
