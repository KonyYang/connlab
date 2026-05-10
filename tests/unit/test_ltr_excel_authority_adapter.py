from datetime import date

import pytest

from backend.application.ltr_authority import CommitLtrAuthorityCommand, LtrAuthorityCommitError
from backend.application.ltr_excel_authority_adapter import ExcelWorkbookLtrAuthorityAdapter
from backend.application.ltr_workbook_write_commit_service import LtrWorkbookWriteCommitError
from backend.infrastructure.office import (
    LtrWorkbookBackupError,
    LtrWorkbookLockTimeoutError,
    LtrWorkbookReadOnlyError,
    LtrWorkbookWriteDisabledError,
)


def test_adapter_maps_lock_timeout_to_actionable_authority_message() -> None:
    adapter = ExcelWorkbookLtrAuthorityAdapter(_FailingCommitService(LtrWorkbookLockTimeoutError("x")))
    with pytest.raises(LtrAuthorityCommitError, match="locked by another operator"):
        adapter.commit_project("P1", _command())


def test_adapter_maps_read_only_to_actionable_authority_message() -> None:
    adapter = ExcelWorkbookLtrAuthorityAdapter(_FailingCommitService(LtrWorkbookReadOnlyError("x")))
    with pytest.raises(LtrAuthorityCommitError, match="read-only mode"):
        adapter.commit_project("P1", _command())


def test_adapter_maps_backup_error_to_actionable_authority_message() -> None:
    adapter = ExcelWorkbookLtrAuthorityAdapter(_FailingCommitService(LtrWorkbookBackupError("x")))
    with pytest.raises(LtrAuthorityCommitError, match="backup failed"):
        adapter.commit_project("P1", _command())


def test_adapter_maps_write_disabled_to_actionable_authority_message() -> None:
    adapter = ExcelWorkbookLtrAuthorityAdapter(_FailingCommitService(LtrWorkbookWriteDisabledError("x")))
    with pytest.raises(LtrAuthorityCommitError, match="write is disabled"):
        adapter.commit_project("P1", _command())


def test_adapter_keeps_business_validation_message() -> None:
    adapter = ExcelWorkbookLtrAuthorityAdapter(
        _FailingCommitService(LtrWorkbookWriteCommitError("Operator confirmation is required."))
    )
    with pytest.raises(LtrAuthorityCommitError, match="Operator confirmation is required"):
        adapter.commit_project("P1", _command())


def _command() -> CommitLtrAuthorityCommand:
    return CommitLtrAuthorityCommand(
        plan_date=date(2026, 5, 10),
        operator_confirmed=True,
        test_item="test",
        sample_description="sample",
        location="lab",
        test_type_in_sheet="Qualification",
        project_leader="Alice",
    )


class _FailingCommitService:
    def __init__(self, error: Exception) -> None:
        self._error = error

    def commit_project(self, project_id: str, command):
        raise self._error

