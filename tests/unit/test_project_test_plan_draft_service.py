from __future__ import annotations

import json

import pytest

from backend.application.project_test_plan_draft_service import (
    CreateProjectTestPlanDraftCommand,
    ProjectTestPlanDraftError,
    ProjectTestPlanDraftNotFoundError,
    ProjectTestPlanDraftService,
    UpdateProjectTestPlanDraftCommand,
)
from backend.domain import Project, ProjectStatus, ProjectTestPlanDraft, ProjectTestPlanDraftStatus


def test_project_test_plan_draft_service_creates_and_supersedes_same_source() -> None:
    service = _service()
    payload = _payload("Group 1")

    first = service.create_draft(
        CreateProjectTestPlanDraftCommand(
            project_id="P1",
            source_document_path="C:/spec.docx",
            source_document_name="spec.docx",
            source_format=".docx",
            payload=payload,
            source_case_id="CASE1",
            source_draft_id="DRAFT1",
        )
    )
    second = service.create_draft(
        CreateProjectTestPlanDraftCommand(
            project_id="P1",
            source_document_path="C:/spec.docx",
            source_document_name="spec.docx",
            source_format=".docx",
            payload=_payload("Group 2"),
        )
    )

    drafts = service.list_by_project("P1")
    first_after = service.get_draft("P1", first.draft_id)
    assert first_after.status is ProjectTestPlanDraftStatus.SUPERSEDED
    assert second.version == 2
    assert second.status is ProjectTestPlanDraftStatus.DRAFT
    assert len(drafts) == 2
    assert json.loads(first.payload_json)["groups"][0]["group_label"] == "Group 1"
    assert first.source_case_id == "CASE1"
    assert first.source_draft_id == "DRAFT1"


def test_project_test_plan_draft_service_updates_draft_to_reviewed() -> None:
    service = _service()
    draft = service.create_draft(_create_command())

    updated = service.update_draft(
        UpdateProjectTestPlanDraftCommand(
            project_id="P1",
            draft_id=draft.draft_id,
            status=ProjectTestPlanDraftStatus.REVIEWED,
            payload=_payload("Reviewed Group"),
        )
    )

    assert updated.status is ProjectTestPlanDraftStatus.REVIEWED
    assert updated.reviewed_at is not None
    assert json.loads(updated.payload_json)["groups"][0]["group_label"] == "Reviewed Group"


def test_project_test_plan_draft_service_rejects_unknown_project() -> None:
    service = _service(projects={})

    with pytest.raises(ProjectTestPlanDraftNotFoundError, match="Project not found"):
        service.create_draft(_create_command())


def test_project_test_plan_draft_service_rejects_cross_project_read() -> None:
    service = _service()
    draft = service.create_draft(_create_command())

    with pytest.raises(ProjectTestPlanDraftNotFoundError):
        service.get_draft("P2", draft.draft_id)


def test_project_test_plan_draft_service_rejects_reviewed_to_draft_transition() -> None:
    service = _service()
    draft = service.create_draft(_create_command(status=ProjectTestPlanDraftStatus.REVIEWED))

    with pytest.raises(ProjectTestPlanDraftError, match="Invalid"):
        service.update_draft(
            UpdateProjectTestPlanDraftCommand(
                project_id="P1",
                draft_id=draft.draft_id,
                status=ProjectTestPlanDraftStatus.DRAFT,
            )
        )


def _create_command(
    *,
    status: ProjectTestPlanDraftStatus = ProjectTestPlanDraftStatus.DRAFT,
) -> CreateProjectTestPlanDraftCommand:
    return CreateProjectTestPlanDraftCommand(
        project_id="P1",
        source_document_path="C:/spec.docx",
        source_document_name="spec.docx",
        source_format=".docx",
        payload=_payload("Group 1"),
        status=status,
    )


def _payload(group_label: str) -> dict[str, object]:
    return {
        "groups": [
            {
                "group_key": "group_1",
                "group_label": group_label,
                "steps": [{"sequence": 1, "test_item": "Examination"}],
            }
        ],
        "warnings": [],
        "blockers": [],
    }


def _service(
    *,
    projects: dict[str, Project] | None = None,
) -> ProjectTestPlanDraftService:
    return ProjectTestPlanDraftService(
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
                ),
                "P2": Project(
                    project_id="P2",
                    project_no="DL-2026-05-002",
                    product_name="Other",
                    requestor="Bob",
                    status=ProjectStatus.LTR_REGISTERED,
                ),
            }
        ),
        draft_store=_DraftStore(),
    )


class _ProjectStore:
    def __init__(self, projects: dict[str, Project]) -> None:
        self._projects = projects

    def get(self, project_id: str) -> Project | None:
        return self._projects.get(project_id)


class _DraftStore:
    def __init__(self) -> None:
        self._drafts: dict[str, ProjectTestPlanDraft] = {}

    def create(self, draft: ProjectTestPlanDraft) -> ProjectTestPlanDraft:
        self._drafts[draft.draft_id] = draft
        return draft

    def get(self, draft_id: str) -> ProjectTestPlanDraft | None:
        return self._drafts.get(draft_id)

    def list_by_project(self, project_id: str) -> list[ProjectTestPlanDraft]:
        return [draft for draft in self._drafts.values() if draft.project_id == project_id]

    def list_by_project_and_source(
        self,
        project_id: str,
        source_document_path: str,
    ) -> list[ProjectTestPlanDraft]:
        return [
            draft
            for draft in self._drafts.values()
            if draft.project_id == project_id
            and draft.source_document_path == source_document_path
        ]

    def update(self, draft: ProjectTestPlanDraft) -> ProjectTestPlanDraft:
        self._drafts[draft.draft_id] = draft
        return draft
