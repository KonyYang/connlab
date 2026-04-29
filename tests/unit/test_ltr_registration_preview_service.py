from datetime import datetime
from pathlib import Path

import pytest

from backend.application.ltr_registration_preview_service import (
    LtrPreviewError,
    LtrPreviewMode,
    LtrRegistrationType,
    LtrRegistrationPreviewService,
    PreviewLtrRegistrationCommand,
)
from backend.application.ltr_readiness_service import (
    LtrReadinessField,
    LtrReadinessResult,
)
from backend.domain import LtrRecord, LtrStatus
from backend.infrastructure.office.models import LtrWorkbookFormat, LtrWorkbookSnapshot
from backend.modules.ltr import ReadinessSeverity


def test_normal_ltr_preview_does_not_generate_or_reserve_number() -> None:
    ltr_repo = _LtrRepo(
        search_rows=[
            _ltr("L1", "OTHER", "DL-2026-04-001"),
            _ltr("L2", "OTHER", "DL-2026-04-002ABC"),
            _ltr("L3", "OTHER", "W123"),
        ]
    )
    service = LtrRegistrationPreviewService(
        ltr_repository=ltr_repo,
        readiness_service=_Readiness(blockers=()),
    )

    preview = service.preview_project(
        "P1",
        PreviewLtrRegistrationCommand(year=2026, month=4),
    )

    assert preview.status == "review_required"
    assert preview.proposed_ltr_number is None
    assert preview.registration_type is LtrRegistrationType.NORMAL
    assert preview.number_preflight_required is False
    assert preview.number_preview_allowed is False
    assert preview.final_number_reserved is False
    assert preview.mode is LtrPreviewMode.LOCAL_ONLY
    assert preview.target_sheet == "2026"
    assert preview.target_row is None
    assert preview.snapshot_fingerprint is None
    assert ltr_repo.created == []


def test_ltr_preview_blocks_when_readiness_has_missing_blockers() -> None:
    service = LtrRegistrationPreviewService(
        ltr_repository=_LtrRepo(),
        readiness_service=_Readiness(blockers=("phone",)),
    )

    preview = service.preview_project(
        "P1",
        PreviewLtrRegistrationCommand(year=2026, month=4),
    )

    assert preview.status == "blocked"
    assert preview.readiness.blockers[0].key == "phone"


def test_ltr_preview_reports_local_and_project_conflicts() -> None:
    service = LtrRegistrationPreviewService(
        ltr_repository=_LtrRepo(
            project_rows=[_ltr("L1", "P1", "DL-2026-04-001")],
            search_rows=[_ltr("L1", "P1", "DL-2026-04-001")],
        ),
        readiness_service=_Readiness(blockers=(), warnings=()),
    )

    with pytest.raises(LtrPreviewError, match="DL suffix"):
        service.preview_project(
            "P1",
            PreviewLtrRegistrationCommand(
                year=2026,
                month=4,
                registration_type=LtrRegistrationType.ASSOCIATED,
                proposed_ltr_number="DL-2026-04-001",
            ),
        )


def test_associated_ltr_preview_uses_workbook_snapshot_when_available() -> None:
    snapshot = _snapshot(existing=("DL-2025-11-002", "DL-2025-11-002B"))
    service = LtrRegistrationPreviewService(
        ltr_repository=_LtrRepo(),
        readiness_service=_Readiness(blockers=(), warnings=()),
        workbook_snapshot_provider=_SnapshotProvider(snapshot),
    )

    preview = service.preview_project(
        "P1",
        PreviewLtrRegistrationCommand(
            year=2026,
            month=4,
            registration_type=LtrRegistrationType.ASSOCIATED,
            mode=LtrPreviewMode.EXCEL_READONLY,
            proposed_ltr_number="DL-2025-11-002A",
        ),
    )

    assert preview.status == "ready"
    assert preview.proposed_ltr_number == "DL-2025-11-002A"
    assert preview.registration_type is LtrRegistrationType.ASSOCIATED
    assert preview.parsed_base_number == "DL-2025-11-002"
    assert preview.base_year_sheet == "2025"
    assert preview.target_write_year_sheet == "2026"
    assert preview.target_sheet == "2026"
    assert preview.target_row == 4
    assert preview.snapshot_fingerprint
    assert preview.family_numbers == ("DL-2025-11-002", "DL-2025-11-002B")


def test_ltr_preview_reports_workbook_duplicate_for_requested_number() -> None:
    service = LtrRegistrationPreviewService(
        ltr_repository=_LtrRepo(),
        readiness_service=_Readiness(blockers=(), warnings=()),
        workbook_snapshot_provider=_SnapshotProvider(
            _snapshot(existing=("DL-2026-04-001A",))
        ),
    )

    preview = service.preview_project(
        "P1",
        PreviewLtrRegistrationCommand(
            year=2026,
            month=4,
            registration_type=LtrRegistrationType.ASSOCIATED,
            mode=LtrPreviewMode.EXCEL_READONLY,
            proposed_ltr_number="DL-2026-04-001A",
        ),
    )

    assert preview.status == "conflict"
    assert "Proposed LTR already exists in workbook snapshot: DL-2026-04-001A" in (
        preview.conflicts
    )


def test_ltr_preview_warns_when_excel_snapshot_is_unavailable() -> None:
    service = LtrRegistrationPreviewService(
        ltr_repository=_LtrRepo(),
        readiness_service=_Readiness(blockers=(), warnings=()),
        workbook_snapshot_provider=_SnapshotProvider(None),
    )

    preview = service.preview_project(
        "P1",
        PreviewLtrRegistrationCommand(
            year=2026,
            month=4,
            mode=LtrPreviewMode.EXCEL_READONLY,
        ),
    )

    assert preview.status == "ready"
    assert preview.proposed_ltr_number is None


class _LtrRepo:
    def __init__(
        self,
        *,
        project_rows: list[LtrRecord] | None = None,
        search_rows: list[LtrRecord] | None = None,
    ) -> None:
        self._project_rows = project_rows or []
        self._search_rows = search_rows or []
        self.created: list[LtrRecord] = []

    def list_by_project(self, project_id: str) -> list[LtrRecord]:
        return [ltr for ltr in self._project_rows if ltr.project_id == project_id]

    def search(self, query: str) -> list[LtrRecord]:
        return [ltr for ltr in self._search_rows if query in ltr.ltr_number]


class _Readiness:
    def __init__(
        self,
        *,
        blockers: tuple[str, ...],
        warnings: tuple[str, ...] = ("location",),
    ) -> None:
        self._blockers = blockers
        self._warnings = warnings

    def evaluate_project(
        self,
        project_id: str,
        proposed_ltr_number: str | None = None,
    ) -> LtrReadinessResult:
        fields = (
            _field("dl", proposed_ltr_number, "confirmed"),
            *(_field(key, None, "missing") for key in self._blockers),
            *(_field(key, None, "needs_review") for key in self._warnings),
        )
        blockers = tuple(field for field in fields if field.state == "missing")
        warnings = tuple(field for field in fields if field.state == "needs_review")
        status = "blocked" if blockers else "review_required" if warnings else "ready"
        return LtrReadinessResult(
            project_id=project_id,
            status=status,
            fields=fields,
            blockers=blockers,
            warnings=warnings,
        )


class _SnapshotProvider:
    def __init__(self, snapshot: LtrWorkbookSnapshot | None) -> None:
        self._snapshot = snapshot

    def get_snapshot(self) -> LtrWorkbookSnapshot | None:
        return self._snapshot


def _field(key: str, value: str | None, state: str) -> LtrReadinessField:
    severity = (
        ReadinessSeverity.BLOCKER
        if state == "missing"
        else ReadinessSeverity.REVIEW_REQUIRED
    )
    return LtrReadinessField(
        key=key,
        label=key,
        value=value,
        source="test",
        severity=severity,
        state=state,
        operator_action=f"Confirm {key}.",
    )


def _ltr(ltr_id: str, project_id: str, number: str) -> LtrRecord:
    return LtrRecord(
        ltr_id=ltr_id,
        project_id=project_id,
        ltr_number=number,
        status=LtrStatus.REGISTERED,
    )


def _snapshot(existing: tuple[str, ...]) -> LtrWorkbookSnapshot:
    return LtrWorkbookSnapshot(
        workbook_path=Path("ltr.xlsx"),
        workbook_format=LtrWorkbookFormat.XLSX,
        size_bytes=100,
        modified_time=datetime(2026, 4, 28, 8, 0, 0),
        sheet_names=("2026",),
        readable_sheet_names=("2026",),
        sheet_strategy="year_sheets",
        existing_ltr_numbers=existing,
    )
