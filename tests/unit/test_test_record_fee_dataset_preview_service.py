from __future__ import annotations

import json

import pytest

from backend.application.test_record_fee_dataset_preview_service import (
    TestRecordFeeDatasetPreviewCommand as DatasetPreviewCommand,
    TestRecordFeeDatasetPreviewError as DatasetPreviewError,
    TestRecordFeeDatasetPreviewNotFoundError as DatasetPreviewNotFoundError,
    TestRecordFeeDatasetPreviewService as DatasetPreviewService,
)
from backend.domain import Project, ProjectStatus, ProjectTestPlanDraft, ProjectTestPlanDraftStatus


def test_dataset_preview_builds_test_record_and_fee_datasets() -> None:
    service = _service(draft=_draft(payload=_payload(complete=True)))

    preview = service.preview(_command())

    assert preview.source_document_name == "spec.docx"
    assert preview.test_record_dataset is not None
    group = preview.test_record_dataset.groups[0]
    assert group.group_label == "Group 1"
    assert group.source_table_index == 21
    assert group.steps[0].test_item == "LLCR"
    assert group.steps[0].condition_summary == "After conditioning"
    assert group.steps[0].duration_hint == "1 day(s)"
    assert preview.fee_dataset is not None
    assert preview.fee_dataset.summary.group_count == 1
    assert preview.fee_dataset.summary.step_count == 1
    assert preview.fee_dataset.summary.explicit_duration_days == 1
    assert preview.fee_dataset.line_items[0].pricing_status == "price_source_missing"
    assert "No pricing source" in preview.fee_dataset.line_items[0].warnings[0]
    assert preview.warnings == ()


def test_dataset_preview_warns_for_missing_step_fields() -> None:
    service = _service(draft=_draft(payload=_payload(complete=False)))

    preview = service.preview(_command())

    assert preview.test_record_dataset is not None
    step = preview.test_record_dataset.groups[0].steps[0]
    assert "condition_summary is missing." in step.warnings
    assert "duration_hint is missing." in step.warnings
    assert any("condition_summary is missing" in warning for warning in preview.warnings)
    assert preview.fee_dataset is not None
    assert "Duration is missing" in preview.fee_dataset.line_items[0].warnings[1]


def test_dataset_preview_can_disable_one_dataset() -> None:
    service = _service(draft=_draft(payload=_payload(complete=True)))

    preview = service.preview(
        DatasetPreviewCommand(
            project_id="P1",
            draft_id="D1",
            include_test_record_dataset=False,
            include_fee_dataset=True,
        )
    )

    assert preview.test_record_dataset is None
    assert preview.fee_dataset is not None


def test_dataset_preview_rejects_missing_project_cross_project_and_superseded() -> None:
    with pytest.raises(DatasetPreviewNotFoundError, match="Project not found"):
        _service(projects={}).preview(_command())

    with pytest.raises(DatasetPreviewNotFoundError, match="not found"):
        _service(draft=_draft(project_id="P2")).preview(_command())

    with pytest.raises(DatasetPreviewError, match="Superseded"):
        _service(
            draft=_draft(status=ProjectTestPlanDraftStatus.SUPERSEDED)
        ).preview(_command())


def test_dataset_preview_requires_at_least_one_dataset() -> None:
    service = _service()

    with pytest.raises(DatasetPreviewError, match="At least one"):
        service.preview(
            DatasetPreviewCommand(
                project_id="P1",
                draft_id="D1",
                include_test_record_dataset=False,
                include_fee_dataset=False,
            )
        )


def _command() -> DatasetPreviewCommand:
    return DatasetPreviewCommand(project_id="P1", draft_id="D1")


def _payload(*, complete: bool) -> dict[str, object]:
    step: dict[str, object] = {
        "sequence": 1,
        "test_item": "LLCR",
        "source_table_index": 21,
        "source_row_index": 5,
        "source_section": "5.4",
    }
    if complete:
        step.update(
            {
                "condition_summary": "After conditioning",
                "method_summary": "Measure low level contact resistance",
                "reference_standard": "EIA-364-23",
                "judgement_criteria": "20 mOhm max",
                "estimated_duration_days": 1,
            }
        )
    return {
        "groups": [
            {
                "group_key": "group_1",
                "group_label": "Group 1",
                "source_table_index": 21,
                "steps": [step],
            }
        ]
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
        payload_json=json.dumps(payload or _payload(complete=True), ensure_ascii=False),
        created_at="2026-05-12T00:00:00+00:00",
        updated_at="2026-05-12T00:00:00+00:00",
        reviewed_at="2026-05-12T00:00:00+00:00",
    )


def _service(
    *,
    projects: dict[str, Project] | None = None,
    draft: ProjectTestPlanDraft | None = None,
) -> DatasetPreviewService:
    return DatasetPreviewService(
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
