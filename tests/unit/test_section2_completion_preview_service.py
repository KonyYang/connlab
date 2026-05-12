from __future__ import annotations

import json
from datetime import date

import pytest

from backend.application.section2_completion_preview_service import (
    Section2CompletionPreviewCommand,
    Section2CompletionPreviewError,
    Section2CompletionPreviewNotFoundError,
    Section2CompletionPreviewService,
)
from backend.domain import Project, ProjectStatus, ProjectTestPlanDraft, ProjectTestPlanDraftStatus


def test_section2_preview_computes_summary_and_completion_date() -> None:
    service = _service(draft=_draft(payload=_payload(with_duration=True)))

    preview = service.preview(
        Section2CompletionPreviewCommand(
            project_id="P1",
            draft_id="D1",
            received_date=date(2026, 5, 12),
            lab=" Connector Lab ",
            assigned_personnel="White",
            sample_condition="Good condition",
            sample_preparation_days=1,
            test_group_scheduling_buffer_days=1,
            report_drafting_days=3,
            review_days=1,
        )
    )

    assert preview.estimated_completion_date == date(2026, 5, 20)
    assert preview.lab == "Connector Lab"
    assert preview.duration_summary.explicit_test_duration_days == 2
    assert preview.duration_summary.total_estimated_days == 8
    assert "Group 1: Examination, LLCR" in preview.test_demand_summary
    assert preview.warnings == ()


def test_section2_preview_warns_when_explicit_duration_is_missing() -> None:
    service = _service(draft=_draft(payload=_payload(with_duration=False)))

    preview = service.preview(
        Section2CompletionPreviewCommand(
            project_id="P1",
            draft_id="D1",
            received_date=date(2026, 5, 12),
        )
    )

    assert preview.estimated_completion_date == date(2026, 5, 18)
    assert preview.duration_summary.total_estimated_days == 6
    assert preview.warnings == (
        "No explicit test duration was found in the Project test-plan draft.",
    )


def test_section2_preview_rejects_unknown_project_and_cross_project_draft() -> None:
    service = _service(projects={}, draft=_draft())

    with pytest.raises(Section2CompletionPreviewNotFoundError, match="Project not found"):
        service.preview(_command(project_id="P1", draft_id="D1"))

    service = _service(draft=_draft(project_id="P2"))

    with pytest.raises(Section2CompletionPreviewNotFoundError, match="not found"):
        service.preview(_command(project_id="P1", draft_id="D1"))


def test_section2_preview_rejects_superseded_draft_and_bad_buffers() -> None:
    service = _service(
        draft=_draft(status=ProjectTestPlanDraftStatus.SUPERSEDED),
    )

    with pytest.raises(Section2CompletionPreviewError, match="Superseded"):
        service.preview(_command(project_id="P1", draft_id="D1"))

    service = _service(draft=_draft())

    with pytest.raises(Section2CompletionPreviewError, match="review_days"):
        service.preview(
            Section2CompletionPreviewCommand(
                project_id="P1",
                draft_id="D1",
                received_date=date(2026, 5, 12),
                review_days=-1,
            )
        )


def _command(project_id: str, draft_id: str) -> Section2CompletionPreviewCommand:
    return Section2CompletionPreviewCommand(
        project_id=project_id,
        draft_id=draft_id,
        received_date=date(2026, 5, 12),
    )


def _payload(*, with_duration: bool = False) -> dict[str, object]:
    steps: list[dict[str, object]] = [
        {"sequence": 1, "test_item": "Examination"},
        {"sequence": 2, "test_item": "LLCR"},
    ]
    if with_duration:
        steps[0]["estimated_duration_hours"] = 24
        steps[1]["estimated_duration_days"] = 1
    return {
        "groups": [
            {
                "group_key": "group_1",
                "group_label": "Group 1",
                "steps": steps,
            }
        ],
        "warnings": [],
        "blockers": [],
    }


def _draft(
    *,
    project_id: str = "P1",
    status: ProjectTestPlanDraftStatus = ProjectTestPlanDraftStatus.REVIEWED,
    payload: dict[str, object] | None = None,
) -> ProjectTestPlanDraft:
    return ProjectTestPlanDraft(
        draft_id="D1",
        project_id=project_id,
        source_document_path="C:/spec.docx",
        source_document_name="spec.docx",
        source_format=".docx",
        source_asset_id=None,
        source_case_id=None,
        source_draft_id=None,
        status=status,
        version=1,
        payload_json=json.dumps(payload or _payload(), ensure_ascii=False),
        created_at="2026-05-12T00:00:00+00:00",
        updated_at="2026-05-12T00:00:00+00:00",
        reviewed_at="2026-05-12T00:00:00+00:00",
    )


def _service(
    *,
    projects: dict[str, Project] | None = None,
    draft: ProjectTestPlanDraft | None = None,
) -> Section2CompletionPreviewService:
    return Section2CompletionPreviewService(
        project_store=_ProjectStore(
            projects
            if projects is not None
            else {
                "P1": Project(
                    project_id="P1",
                    project_no="DL-2026-05-001",
                    product_name="Connector",
                    requestor="Alice",
                    status=ProjectStatus.LTR_REGISTERED,
                )
            }
        ),
        draft_store=_DraftStore(draft or _draft()),
    )


class _ProjectStore:
    def __init__(self, projects: dict[str, Project]) -> None:
        self._projects = projects

    def get(self, project_id: str) -> Project | None:
        return self._projects.get(project_id)


class _DraftStore:
    def __init__(self, draft: ProjectTestPlanDraft) -> None:
        self._draft = draft

    def get(self, draft_id: str) -> ProjectTestPlanDraft | None:
        if draft_id == self._draft.draft_id:
            return self._draft
        return None
