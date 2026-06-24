from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest

from backend.application.project_output_record_service import (
    ProjectOutputRecordError,
    ProjectOutputRecordService,
    RegisterProjectOutputCommand,
)
from backend.domain import (
    Project,
    ProjectOutputKind,
    ProjectOutputRecord,
    ProjectOutputSource,
    ProjectOutputStatus,
    ProjectStatus,
    ProjectTestPlanDraft,
    ProjectTestPlanDraftStatus,
)


class _ProjectStore:
    def __init__(self, project: Project) -> None:
        self.project = project

    def get(self, project_id: str) -> Project | None:
        return self.project if self.project.project_id == project_id else None


class _DraftStore:
    def __init__(self, drafts: list[ProjectTestPlanDraft]) -> None:
        self.drafts = drafts

    def get(self, draft_id: str) -> ProjectTestPlanDraft | None:
        return next((item for item in self.drafts if item.draft_id == draft_id), None)

    def list_by_project(self, project_id: str) -> list[ProjectTestPlanDraft]:
        return [item for item in self.drafts if item.project_id == project_id]


class _OutputStore:
    def __init__(self) -> None:
        self.items: list[ProjectOutputRecord] = []

    def create(self, record: ProjectOutputRecord) -> ProjectOutputRecord:
        self.items.append(record)
        return record

    def list_by_project(self, project_id: str) -> list[ProjectOutputRecord]:
        return [item for item in self.items if item.project_id == project_id]


def test_register_output_requires_draft_for_current_status() -> None:
    service = _service()
    with pytest.raises(ProjectOutputRecordError):
        service.register_output(
            RegisterProjectOutputCommand(
                project_id="P1",
                output_kind=ProjectOutputKind.SECTION2_WRITE_BACK,
                status=ProjectOutputStatus.CURRENT,
                source=ProjectOutputSource.SYSTEM_EXECUTED,
                output_path="C:/a.docx",
                draft_id=None,
            )
        )


def test_register_output_allows_context_bound_current_system_output_without_draft() -> None:
    service = _service()

    record = service.register_output(
        RegisterProjectOutputCommand(
            project_id="P1",
            output_kind=ProjectOutputKind.FEE_EVALUATION,
            status=ProjectOutputStatus.CURRENT,
            source=ProjectOutputSource.SYSTEM_GENERATED,
            output_path="C:/fee.xls",
            draft_id=None,
            source_context_signature="basic:1@hash|fee-output:matrix_basic",
        )
    )

    assert record.status is ProjectOutputStatus.CURRENT
    assert record.source is ProjectOutputSource.SYSTEM_GENERATED
    assert record.draft_id is None


def test_status_summary_marks_stale_when_active_draft_version_changes() -> None:
    store = _OutputStore()
    draft = _draft(version=1)
    service = ProjectOutputRecordService(
        project_store=_ProjectStore(_project()),
        draft_store=_DraftStore([replace(draft, status=ProjectTestPlanDraftStatus.REVIEWED)]),
        output_store=store,
    )
    service.register_output(
        RegisterProjectOutputCommand(
            project_id="P1",
            output_kind=ProjectOutputKind.TEST_RECORD_FORM,
            status=ProjectOutputStatus.CURRENT,
            source=ProjectOutputSource.SYSTEM_GENERATED,
            output_path="C:/record.docx",
            draft_id="D1",
        )
    )
    service_with_new_draft = ProjectOutputRecordService(
        project_store=_ProjectStore(_project()),
        draft_store=_DraftStore([replace(draft, version=2, status=ProjectTestPlanDraftStatus.REVIEWED)]),
        output_store=store,
    )
    summary = service_with_new_draft.get_status_summary("P1")
    item = next(it for it in summary.items if it.output_kind is ProjectOutputKind.TEST_RECORD_FORM)
    assert item.status is ProjectOutputStatus.STALE
    assert item.draft_version == 1


def test_status_summary_uses_reviewed_authority_when_candidate_exists() -> None:
    store = _OutputStore()
    reviewed = _draft(
        draft_id="D1",
        version=1,
        status=ProjectTestPlanDraftStatus.REVIEWED,
        reviewed_at="2026-05-14T01:00:00+00:00",
    )
    candidate = _draft(
        draft_id="D2",
        version=2,
        status=ProjectTestPlanDraftStatus.DRAFT,
    )
    service = ProjectOutputRecordService(
        project_store=_ProjectStore(_project()),
        draft_store=_DraftStore([reviewed, candidate]),
        output_store=store,
    )
    service.register_output(
        RegisterProjectOutputCommand(
            project_id="P1",
            output_kind=ProjectOutputKind.SECTION2_WRITE_BACK,
            status=ProjectOutputStatus.CURRENT,
            source=ProjectOutputSource.SYSTEM_EXECUTED,
            output_path="C:/a.docx",
            draft_id="D1",
        )
    )
    summary = service.get_status_summary("P1")
    assert summary.active_draft_id == "D1"
    assert summary.active_draft_version == 1
    item = next(it for it in summary.items if it.output_kind is ProjectOutputKind.SECTION2_WRITE_BACK)
    assert item.status is ProjectOutputStatus.CURRENT


def _service() -> ProjectOutputRecordService:
    return ProjectOutputRecordService(
        project_store=_ProjectStore(_project()),
        draft_store=_DraftStore([_draft(version=1)]),
        output_store=_OutputStore(),
    )


def _project() -> Project:
    return Project(
        project_id="P1",
        project_no="DL-2026-05-001",
        product_name="Connector",
        requestor="Alice",
        status=ProjectStatus.LTR_REGISTERED,
        created_on=date(2026, 5, 12),
    )


def _draft(
    *,
    draft_id: str = "D1",
    version: int,
    status: ProjectTestPlanDraftStatus = ProjectTestPlanDraftStatus.DRAFT,
    reviewed_at: str | None = None,
) -> ProjectTestPlanDraft:
    return ProjectTestPlanDraft(
        draft_id=draft_id,
        project_id="P1",
        source_document_path="C:/spec.docx",
        source_document_name="spec.docx",
        source_format=".docx",
        status=status,
        version=version,
        payload_json='{"groups":[],"warnings":[],"blockers":[]}',
        created_at="2026-05-14T00:00:00+00:00",
        updated_at="2026-05-14T00:00:00+00:00",
        source_asset_id=None,
        source_case_id=None,
        source_draft_id=None,
        reviewed_at=reviewed_at,
    )
