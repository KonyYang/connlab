import json

import pytest

from backend.application.ltr_local_commit_service import (
    CommitLocalLtrCommand,
    LtrLocalCommitError,
    LtrLocalCommitService,
)
from backend.application.ltr_registration_preview_service import (
    LtrPreviewMode,
    LtrRegistrationType,
    LtrRegistrationPreview,
)
from backend.application.ltr_readiness_service import (
    LtrReadinessField,
    LtrReadinessResult,
)
from backend.application.ltr_service import RegisterLtrCommand
from backend.domain import LtrRecord, LtrStatus
from backend.modules.ltr import ReadinessSeverity


def test_ltr_local_commit_registers_approved_preview_with_audit_notes() -> None:
    preview = _preview(status="review_required")
    ltr_service = _LtrService()
    service = LtrLocalCommitService(
        preview_service=_PreviewService(preview),
        ltr_service=ltr_service,
    )

    result = service.commit_project(
        "P1",
        CommitLocalLtrCommand(
            year=2026,
            month=4,
            operator_confirmed=True,
            registration_type=LtrRegistrationType.ASSOCIATED,
            proposed_ltr_number="DL-2026-04-001A",
            requested_by="Alice",
            operator_note="Approved by intake operator",
        ),
    )

    assert result.ltr.ltr_number == "DL-2026-04-001A"
    assert ltr_service.commands[0].requested_by == "Alice"
    audit = json.loads(result.ltr.notes or "{}")
    assert audit["commit_mode"] == "local_only"
    assert audit["operator_note"] == "Approved by intake operator"
    assert audit["preview"]["proposed_ltr_number"] == "DL-2026-04-001A"
    assert audit["preview"]["registration_type"] == "associated"
    assert audit["readiness"]["warnings"] == ["location"]


def test_ltr_local_commit_requires_operator_confirmation() -> None:
    service = LtrLocalCommitService(
        preview_service=_PreviewService(_preview(status="ready")),
        ltr_service=_LtrService(),
    )

    with pytest.raises(LtrLocalCommitError, match="Operator confirmation"):
        service.commit_project(
            "P1",
            CommitLocalLtrCommand(year=2026, month=4, operator_confirmed=False),
        )


def test_ltr_local_commit_rejects_blocked_preview() -> None:
    service = LtrLocalCommitService(
        preview_service=_PreviewService(_preview(status="blocked", blockers=("phone",))),
        ltr_service=_LtrService(),
    )

    with pytest.raises(LtrLocalCommitError, match="blocked"):
        service.commit_project(
            "P1",
            CommitLocalLtrCommand(year=2026, month=4, operator_confirmed=True),
        )


def test_ltr_local_commit_rejects_conflict_preview() -> None:
    service = LtrLocalCommitService(
        preview_service=_PreviewService(
            _preview(status="conflict", conflicts=("Project already has an LTR.",))
        ),
        ltr_service=_LtrService(),
    )

    with pytest.raises(LtrLocalCommitError, match="conflicts"):
        service.commit_project(
            "P1",
            CommitLocalLtrCommand(year=2026, month=4, operator_confirmed=True),
        )


def test_ltr_local_commit_rejects_normal_preview_without_final_number() -> None:
    service = LtrLocalCommitService(
        preview_service=_PreviewService(_normal_preview_without_number()),
        ltr_service=_LtrService(),
    )

    with pytest.raises(LtrLocalCommitError, match="requires a final LTR number"):
        service.commit_project(
            "P1",
            CommitLocalLtrCommand(year=2026, month=4, operator_confirmed=True),
        )


class _PreviewService:
    def __init__(self, preview: LtrRegistrationPreview) -> None:
        self.preview = preview

    def preview_project(self, project_id, command):
        return self.preview


class _LtrService:
    def __init__(self) -> None:
        self.commands: list[RegisterLtrCommand] = []

    def register_ltr(self, project_id: str, command: RegisterLtrCommand) -> LtrRecord:
        self.commands.append(command)
        return LtrRecord(
            ltr_id="L1",
            project_id=project_id,
            ltr_number=command.ltr_number,
            status=LtrStatus.REGISTERED,
            requested_by=command.requested_by,
            requested_date=command.requested_date,
            notes=command.notes,
        )


def _preview(
    *,
    status: str,
    blockers: tuple[str, ...] = (),
    conflicts: tuple[str, ...] = (),
) -> LtrRegistrationPreview:
    readiness = _readiness(blockers)
    return LtrRegistrationPreview(
        project_id="P1",
        status=status,
        proposed_ltr_number="DL-2026-04-001A",
        registration_type=LtrRegistrationType.ASSOCIATED,
        mode=LtrPreviewMode.LOCAL_ONLY,
        target_write_year_sheet="2026",
        number_preflight_required=True,
        number_preview_allowed=True,
        final_number_reserved=False,
        target_sheet=None,
        target_row=None,
        snapshot_fingerprint=None,
        source_numbers=(),
        readiness=readiness,
        conflicts=conflicts,
        warnings=("Confirm location.",),
    )


def _normal_preview_without_number() -> LtrRegistrationPreview:
    readiness = _readiness(())
    return LtrRegistrationPreview(
        project_id="P1",
        status="review_required",
        proposed_ltr_number=None,
        registration_type=LtrRegistrationType.NORMAL,
        mode=LtrPreviewMode.LOCAL_ONLY,
        target_write_year_sheet="2026",
        number_preflight_required=False,
        number_preview_allowed=False,
        final_number_reserved=False,
        target_sheet="2026",
        target_row=None,
        snapshot_fingerprint=None,
        source_numbers=(),
        readiness=readiness,
        conflicts=(),
        warnings=("Confirm location.",),
    )


def _readiness(blockers: tuple[str, ...]) -> LtrReadinessResult:
    blocker_fields = tuple(_field(key, "missing") for key in blockers)
    warning_fields = (_field("location", "needs_review"),)
    fields = (_field("dl", "confirmed"), *blocker_fields, *warning_fields)
    return LtrReadinessResult(
        project_id="P1",
        status="blocked" if blockers else "review_required",
        fields=fields,
        blockers=blocker_fields,
        warnings=warning_fields,
    )


def _field(key: str, state: str) -> LtrReadinessField:
    severity = (
        ReadinessSeverity.BLOCKER
        if state == "missing"
        else ReadinessSeverity.REVIEW_REQUIRED
    )
    return LtrReadinessField(
        key=key,
        label=key,
        value="DL-2026-04-001" if key == "dl" else None,
        source="test",
        severity=severity,
        state=state,
        operator_action=f"Confirm {key}.",
    )
