from __future__ import annotations

import pytest

from backend.application.project_test_plan_draft_service import (
    CreateProjectTestPlanDraftCommand,
    ProjectTestPlanDraftService,
)
from backend.application.project_test_plan_matrix_edit_service import (
    ConfirmProjectTestPlanMatrixCommand,
    ProjectTestPlanMatrixEditError,
    ProjectTestPlanMatrixEditService,
    UpdateProjectTestPlanMatrixCommand,
)
from backend.domain import Project, ProjectStatus, ProjectTestPlanDraft, ProjectTestPlanDraftStatus


def test_matrix_edit_service_revises_reviewed_draft_as_new_version() -> None:
    service, draft_service = _service()
    reviewed = draft_service.create_draft(
        CreateProjectTestPlanDraftCommand(
            project_id="P1",
            source_document_path="C:/spec.docx",
            source_document_name="spec.docx",
            source_format=".docx",
            payload=_payload("1"),
            status=ProjectTestPlanDraftStatus.REVIEWED,
        )
    )
    result = service.update_matrix_draft(
        UpdateProjectTestPlanMatrixCommand(
            project_id="P1",
            draft_id=reviewed.draft_id,
            groups=_groups("1", "2"),
        )
    )

    assert result.created_new_draft is True
    assert result.draft.version == 2
    assert result.draft.status is ProjectTestPlanDraftStatus.DRAFT
    previous = draft_service.get_draft("P1", reviewed.draft_id)
    assert previous.status is ProjectTestPlanDraftStatus.REVIEWED


def test_matrix_edit_service_confirm_blocks_on_sequence_gap() -> None:
    service, draft_service = _service()
    created = draft_service.create_draft(
        CreateProjectTestPlanDraftCommand(
            project_id="P1",
            source_document_path="C:/spec.docx",
            source_document_name="spec.docx",
            source_format=".docx",
            payload=_payload("1 3"),
        )
    )
    with pytest.raises(ProjectTestPlanMatrixEditError):
        service.confirm_matrix_draft(
            ConfirmProjectTestPlanMatrixCommand(
                project_id="P1",
                draft_id=created.draft_id,
            )
        )


def test_matrix_edit_service_confirms_valid_draft() -> None:
    service, draft_service = _service()
    created = draft_service.create_draft(
        CreateProjectTestPlanDraftCommand(
            project_id="P1",
            source_document_path="C:/spec.docx",
            source_document_name="spec.docx",
            source_format=".docx",
            payload=_payload("1 2"),
        )
    )
    result = service.confirm_matrix_draft(
        ConfirmProjectTestPlanMatrixCommand(
            project_id="P1",
            draft_id=created.draft_id,
        )
    )

    assert result.validation.blockers == ()
    assert result.draft.status is ProjectTestPlanDraftStatus.REVIEWED


def test_matrix_edit_service_confirm_supersedes_previous_reviewed_authority() -> None:
    service, draft_service = _service()
    reviewed = draft_service.create_draft(
        CreateProjectTestPlanDraftCommand(
            project_id="P1",
            source_document_path="C:/spec.docx",
            source_document_name="spec.docx",
            source_format=".docx",
            payload=_payload("1"),
            status=ProjectTestPlanDraftStatus.REVIEWED,
        )
    )
    edited = service.update_matrix_draft(
        UpdateProjectTestPlanMatrixCommand(
            project_id="P1",
            draft_id=reviewed.draft_id,
            groups=_groups("1", "2"),
        )
    )
    assert draft_service.get_draft("P1", reviewed.draft_id).status is ProjectTestPlanDraftStatus.REVIEWED

    confirmed = service.confirm_matrix_draft(
        ConfirmProjectTestPlanMatrixCommand(
            project_id="P1",
            draft_id=edited.draft.draft_id,
        )
    )
    assert confirmed.draft.status is ProjectTestPlanDraftStatus.REVIEWED
    assert draft_service.get_draft("P1", reviewed.draft_id).status is ProjectTestPlanDraftStatus.SUPERSEDED


def test_matrix_edit_service_confirm_allows_warning_only_missing_method_requirement() -> None:
    service, draft_service = _service()
    created = draft_service.create_draft(
        CreateProjectTestPlanDraftCommand(
            project_id="P1",
            source_document_path="C:/spec.docx",
            source_document_name="spec.docx",
            source_format=".docx",
            payload={
                "groups": [
                    {
                        "group_key": "group_1",
                        "group_label": "Group 1",
                        "steps": [{"raw_token": "1", "test_item": "Visual examination"}],
                    }
                ],
                "warnings": [],
                "blockers": [],
            },
        )
    )

    result = service.confirm_matrix_draft(
        ConfirmProjectTestPlanMatrixCommand(
            project_id="P1",
            draft_id=created.draft_id,
        )
    )
    assert result.draft.status is ProjectTestPlanDraftStatus.REVIEWED
    assert result.validation.blockers == ()
    assert any("method is missing" in item for item in result.validation.warnings)
    assert any("requirement is missing" in item for item in result.validation.warnings)


def test_matrix_edit_service_confirm_blocks_when_group_identity_missing() -> None:
    service, draft_service = _service()
    created = draft_service.create_draft(
        CreateProjectTestPlanDraftCommand(
            project_id="P1",
            source_document_path="C:/spec.docx",
            source_document_name="spec.docx",
            source_format=".docx",
            payload={
                "groups": [{"steps": [{"raw_token": "1", "test_item": "Visual examination"}]}],
                "warnings": [],
                "blockers": [],
            },
        )
    )
    with pytest.raises(ProjectTestPlanMatrixEditError):
        service.confirm_matrix_draft(
            ConfirmProjectTestPlanMatrixCommand(project_id="P1", draft_id=created.draft_id)
        )


def _payload(token: str) -> dict[str, object]:
    return {
        "groups": _groups(token),
        "warnings": [],
        "blockers": [],
    }


def _groups(*tokens: str) -> list[dict[str, object]]:
    return [
        {
            "group_key": "group_1",
            "group_label": "Group 1",
            "steps": [
                {
                    "raw_token": token,
                    "test_item": f"Test {index + 1}",
                    "method_summary": "Method A",
                    "judgement_criteria": "Pass",
                    "condition_summary": "Condition",
                }
                for index, token in enumerate(tokens)
            ],
        }
    ]


def _service() -> tuple[ProjectTestPlanMatrixEditService, ProjectTestPlanDraftService]:
    project_store = _ProjectStore(
        {
            "P1": Project(
                project_id="P1",
                project_no="DL-2026-05-001",
                product_name="Connector",
                requestor="Alice",
                status=ProjectStatus.LTR_REGISTERED,
            )
        }
    )
    draft_store = _DraftStore()
    draft_service = ProjectTestPlanDraftService(
        project_store=project_store,
        draft_store=draft_store,
    )
    return (
        ProjectTestPlanMatrixEditService(draft_service=draft_service),
        draft_service,
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
