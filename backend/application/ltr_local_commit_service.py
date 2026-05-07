"""Application service for local-only LTR registration commit."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from backend.application.ltr_registration_preview_service import (
    LtrPreviewMode,
    LtrRegistrationType,
    LtrRegistrationPreview,
    LtrRegistrationPreviewService,
    PreviewLtrRegistrationCommand,
)
from backend.application.ltr_service import (
    LtrService,
    RegisterLtrCommand,
)
from backend.domain import LtrRecord


class LtrLocalCommitError(ValueError):
    """Raised when a local LTR commit cannot proceed."""


@dataclass(frozen=True, slots=True)
class CommitLocalLtrCommand:
    """Input command for committing an approved preview locally."""

    year: int
    month: int
    operator_confirmed: bool
    registration_type: LtrRegistrationType = LtrRegistrationType.NORMAL
    mode: LtrPreviewMode = LtrPreviewMode.LOCAL_ONLY
    proposed_ltr_number: str | None = None
    requested_by: str | None = None
    requested_date: date | None = None
    operator_note: str | None = None


@dataclass(frozen=True, slots=True)
class LtrLocalCommitResult:
    """Result of a local-only LTR commit."""

    ltr: LtrRecord
    preview: LtrRegistrationPreview


class LtrRegistrationPreviewServicePort(Protocol):
    """Preview service behavior required by local commit."""

    def preview_project(
        self,
        project_id: str,
        command: PreviewLtrRegistrationCommand,
    ) -> LtrRegistrationPreview:
        """Return a no-write preview."""


class LtrServicePort(Protocol):
    """LTR registration behavior required by local commit."""

    def register_ltr(self, project_id: str, command: RegisterLtrCommand) -> LtrRecord:
        """Register one LTR locally."""


class LtrLocalCommitService:
    """Commit approved LTR previews to local ConnLab records only."""

    def __init__(
        self,
        preview_service: LtrRegistrationPreviewServicePort | LtrRegistrationPreviewService,
        ltr_service: LtrServicePort | LtrService,
    ) -> None:
        """Create a local commit service."""
        self._preview_service = preview_service
        self._ltr_service = ltr_service

    def commit_project(
        self,
        project_id: str,
        command: CommitLocalLtrCommand,
    ) -> LtrLocalCommitResult:
        """Commit an approved no-write preview to local records."""
        if not command.operator_confirmed:
            raise LtrLocalCommitError("Operator confirmation is required.")

        preview = self._preview_service.preview_project(
            project_id,
            PreviewLtrRegistrationCommand(
                year=command.year,
                month=command.month,
                registration_type=command.registration_type,
                mode=command.mode,
                proposed_ltr_number=command.proposed_ltr_number,
            ),
        )
        if preview.proposed_ltr_number is None:
            raise LtrLocalCommitError(
                "Local commit requires a final LTR number from workbook write "
                "or an explicit associated LTR number."
            )
        if preview.status == "blocked":
            raise LtrLocalCommitError("LTR preview is blocked by missing readiness fields.")
        if preview.status == "conflict":
            detail = "; ".join(preview.conflicts)
            raise LtrLocalCommitError(
                "LTR preview has conflicts and cannot be committed."
                + (f" {detail}" if detail else "")
            )

        ltr = self._ltr_service.register_ltr(
            project_id,
            RegisterLtrCommand(
                ltr_number=preview.proposed_ltr_number,
                requested_by=command.requested_by,
                requested_date=command.requested_date,
                notes=_audit_notes(preview, command.operator_note),
            ),
        )
        return LtrLocalCommitResult(ltr=ltr, preview=preview)


def _audit_notes(
    preview: LtrRegistrationPreview,
    operator_note: str | None,
) -> str:
    """Build traceable audit JSON for the local LTR record notes field."""
    payload = {
        "commit_mode": "local_only",
        "operator_note": operator_note,
        "preview": {
            "mode": preview.mode.value,
            "registration_type": preview.registration_type.value,
            "status": preview.status,
            "proposed_ltr_number": preview.proposed_ltr_number,
            "target_sheet": preview.target_sheet,
            "target_row": preview.target_row,
            "snapshot_fingerprint": preview.snapshot_fingerprint,
            "source_numbers": list(preview.source_numbers),
            "conflicts": list(preview.conflicts),
            "warnings": list(preview.warnings),
        },
        "readiness": {
            "status": preview.readiness.status,
            "blockers": [field.key for field in preview.readiness.blockers],
            "warnings": [field.key for field in preview.readiness.warnings],
            "fields": [
                {
                    "key": field.key,
                    "value": field.value,
                    "source": field.source,
                    "state": field.state,
                    "severity": field.severity.value,
                }
                for field in preview.readiness.fields
            ],
        },
    }
    return json.dumps(payload, ensure_ascii=True, sort_keys=True)
