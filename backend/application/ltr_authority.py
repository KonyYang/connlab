"""Authority boundary for LTR registration commit orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol

from backend.application.ltr_duplicate_resolution_service import DuplicateResolutionCommand
from backend.domain import LtrRecord


class LtrAuthorityCommitError(ValueError):
    """Raised when the active LTR authority cannot commit a registration."""


@dataclass(frozen=True, slots=True)
class CommitLtrAuthorityCommand:
    """Input command for committing one authority-backed LTR registration."""

    plan_date: date
    operator_confirmed: bool
    number_input: str | None = None
    test_item: str = ""
    sample_description: str = ""
    location: str = ""
    test_type_in_sheet: str = ""
    project_leader: str = ""
    requested_by: str | None = None
    requested_date: date | None = None
    operator_note: str | None = None
    current_case_id: str | None = None
    duplicate_resolution: DuplicateResolutionCommand | None = None


@dataclass(frozen=True, slots=True)
class LtrAuthorityCommitResult:
    """Authority-backed LTR commit result exposed to application orchestrators."""

    ltr: LtrRecord
    workbook_path: str | None = None
    workbook_sheet_name: str | None = None
    workbook_row_number: int | None = None
    workbook_backup_path: str | None = None


class LtrAuthorityPort(Protocol):
    """Authority seam for current workbook mode and future server authority."""

    def commit_project(
        self,
        project_id: str,
        command: CommitLtrAuthorityCommand,
    ) -> LtrAuthorityCommitResult:
        """Commit one LTR registration through the active authority adapter."""
