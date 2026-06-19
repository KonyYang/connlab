from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from backend.application.official_project_folder_check_service import (
    OfficialFolderRepairFailureError,
    OfficialProjectFolderCheckConflictError,
    OfficialProjectFolderCheckService,
)
from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.application.project_output_record_service import (
    ProjectOutputStatusItem,
    ProjectOutputStatusSummary,
)
from backend.application.project_request_material_collection_types import (
    RequestMaterialPreview,
    RequestMaterialPreviewItem,
)
from backend.domain import (
    Project,
    ProjectOutputKind,
    ProjectOutputSource,
    ProjectOutputStatus,
    ProjectStatus,
)


def test_preview_blocks_without_official_workspace(tmp_path: Path) -> None:
    service = _service(tmp_path, workspace=None)

    preview = service.preview("P1")

    assert preview.status == "blocked"
    assert preview.next_action == "none"
    assert "Create local project folder before checking the Project Folder." in preview.blockers


def test_preview_reports_missing_required_folders(tmp_path: Path) -> None:
    official = tmp_path / "DL-001" / "DL-001 Connector Qualification test"
    official.mkdir(parents=True)
    service = _service(tmp_path, workspace=_workspace(tmp_path, official))

    preview = service.preview("P1")

    missing = {item.key for item in preview.required_folders if item.status == "missing"}
    assert {"email", "submitted_material", "photos", "test_results", "final_examination"} <= missing
    assert preview.status == "missing"
    assert preview.next_action == "repair_folders"


def test_preview_reports_conflict_when_required_folder_path_is_file(tmp_path: Path) -> None:
    official = tmp_path / "DL-001" / "DL-001 Connector Qualification test"
    (official / "E-mail").parent.mkdir(parents=True)
    (official / "E-mail").write_text("not a folder", encoding="utf-8")
    service = _service(tmp_path, workspace=_workspace(tmp_path, official))

    preview = service.preview("P1")

    assert preview.status == "conflict"
    assert preview.next_action == "none"
    assert any(item.key == "email" and item.status == "conflict" for item in preview.required_folders)


def test_preview_reports_ready_when_required_folders_exist(tmp_path: Path) -> None:
    official = _official_with_required_folders(tmp_path)
    request_preview = _request_material_preview(
        tmp_path,
        status="collected",
        item_status="already_present",
        target_area="submitted_material",
    )
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path, official),
        request_material_service=_RequestMaterialPreviewer(request_preview),
    )

    preview = service.preview("P1")

    assert preview.status == "ready"
    assert preview.next_action == "none"
    assert all(item.status == "ready" for item in preview.required_folders)


def test_preview_reports_missing_when_required_request_material_is_missing(
    tmp_path: Path,
) -> None:
    official = _official_with_required_folders(tmp_path)
    service = _service(tmp_path, workspace=_workspace(tmp_path, official))

    preview = service.preview("P1")

    assert preview.status == "missing"
    assert preview.next_action == "none"
    assert _item(preview.required_files, "request_material").status == "missing"


def test_repair_folders_creates_missing_required_folders(tmp_path: Path) -> None:
    official = tmp_path / "DL-001" / "DL-001 Connector Qualification test"
    official.mkdir(parents=True)
    service = _service(tmp_path, workspace=_workspace(tmp_path, official))

    result = service.repair_folders("P1")

    assert (official / "E-mail").is_dir()
    assert (official / "Submitted Material").is_dir()
    assert (official / "Photos").is_dir()
    assert (official / "Test results" / "Final Examination").is_dir()
    assert result.repair_status == "completed"
    assert result.created_paths


def test_repair_folders_refuses_conflict_paths(tmp_path: Path) -> None:
    official = tmp_path / "DL-001" / "DL-001 Connector Qualification test"
    (official / "E-mail").parent.mkdir(parents=True)
    (official / "E-mail").write_text("not a folder", encoding="utf-8")
    service = _service(tmp_path, workspace=_workspace(tmp_path, official))

    with pytest.raises(OfficialProjectFolderCheckConflictError):
        service.repair_folders("P1")


def test_repair_folders_returns_partial_result_when_later_folder_creation_fails(
    tmp_path: Path,
) -> None:
    official = tmp_path / "DL-001" / "DL-001 Connector Qualification test"
    official.mkdir(parents=True)
    gateway = _FailingAfterFirstCreateGateway()
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path, official),
        repair_gateway=gateway,
    )

    result = service.repair_folders("P1")

    assert result.repair_status == "partial"
    assert result.created_paths
    assert result.errors
    assert result.preview.status in {"missing", "conflict", "warning"}


def test_preview_includes_request_material_state(tmp_path: Path) -> None:
    official = _official_with_required_folders(tmp_path)
    request_preview = _request_material_preview(
        tmp_path,
        status="collected",
        item_status="already_present",
        target_area="submitted_material",
    )
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path, official),
        request_material_service=_RequestMaterialPreviewer(request_preview),
    )

    preview = service.preview("P1")

    assert any(item.key == "request_material" and item.status == "ready" for item in preview.required_files)
    assert any(item.key == "submitted_material" and item.status == "ready" for item in preview.required_files)


def test_preview_keeps_review_required_separate_from_submitted_material_missing(
    tmp_path: Path,
) -> None:
    official = _official_with_required_folders(tmp_path)
    request_preview = _request_material_preview(
        tmp_path,
        status="review_required",
        item_status="needs_review",
        target_area="review_attachment",
        review_required=True,
    )
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path, official),
        request_material_service=_RequestMaterialPreviewer(request_preview),
    )

    preview = service.preview("P1")

    request_item = _item(preview.required_files, "request_material")
    submitted_item = _item(preview.required_files, "submitted_material")
    assert request_item.status == "warning"
    assert "Needs review" in request_item.message
    assert submitted_item.status == "deferred"


def test_preview_defers_generated_forms_without_existing_output_records(tmp_path: Path) -> None:
    official = _official_with_required_folders(tmp_path)
    service = _service(tmp_path, workspace=_workspace(tmp_path, official))

    preview = service.preview("P1")

    generated = {
        item.key: item.status
        for item in preview.required_files
        if item.key in {"test_record", "fee_form", "customer_feedback_form"}
    }
    assert generated == {
        "test_record": "deferred",
        "fee_form": "deferred",
        "customer_feedback_form": "deferred",
    }


def test_preview_maps_current_output_records_and_keeps_customer_feedback_deferred_without_output(
    tmp_path: Path,
) -> None:
    official = _official_with_required_folders(tmp_path)
    test_record_path = official / "Submitted Material" / "Test Record.docx"
    test_record_path.write_text("test record", encoding="utf-8")
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path, official),
        output_service=_OutputStatusService(
            _output_summary(
                ProjectOutputStatusItem(
                    output_kind=ProjectOutputKind.TEST_RECORD_FORM,
                    status=ProjectOutputStatus.CURRENT,
                    output_path=str(test_record_path),
                    source=ProjectOutputSource.SYSTEM_GENERATED,
                    draft_id="draft-1",
                    draft_version=1,
                    reason="current",
                    updated_at="2026-06-13T00:00:00+00:00",
                )
            )
        ),
    )

    preview = service.preview("P1")

    assert _item(preview.required_files, "test_record").status == "ready"
    assert _item(preview.required_files, "customer_feedback_form").status == "deferred"


def test_current_test_record_and_fee_outputs_are_missing_when_files_are_absent(
    tmp_path: Path,
) -> None:
    official = _official_with_required_folders(tmp_path)
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path, official),
        output_service=_OutputStatusService(
            _output_summary(
                ProjectOutputStatusItem(
                    output_kind=ProjectOutputKind.TEST_RECORD_FORM,
                    status=ProjectOutputStatus.CURRENT,
                    output_path=str(official / "Submitted Material" / "Test Record.docx"),
                    source=ProjectOutputSource.SYSTEM_GENERATED,
                    draft_id="draft-1",
                    draft_version=1,
                    reason="current",
                    updated_at="2026-06-13T00:00:00+00:00",
                ),
                ProjectOutputStatusItem(
                    output_kind=ProjectOutputKind.FEE_EVALUATION,
                    status=ProjectOutputStatus.CURRENT,
                    output_path=str(official / "DL-001_Fee_Form.xls"),
                    source=ProjectOutputSource.SYSTEM_GENERATED,
                    draft_id="draft-1",
                    draft_version=1,
                    reason="current",
                    updated_at="2026-06-13T00:00:00+00:00",
                ),
            )
        ),
    )

    preview = service.preview("P1")

    assert _item(preview.required_files, "test_record").status == "missing"
    assert _item(preview.required_files, "fee_form").status == "missing"


def test_customer_feedback_ready_when_current_output_exists(tmp_path: Path) -> None:
    official = _official_with_required_folders(tmp_path)
    feedback_path = official / "DL-001_Customer_Feedback_Form.xlsx"
    feedback_path.write_text("feedback", encoding="utf-8")
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path, official),
        output_service=_OutputStatusService(
            _output_summary(
                ProjectOutputStatusItem(
                    output_kind=ProjectOutputKind.CUSTOMER_FEEDBACK_FORM,
                    status=ProjectOutputStatus.CURRENT,
                    output_path=str(feedback_path),
                    source=ProjectOutputSource.SYSTEM_GENERATED,
                    draft_id="draft-1",
                    draft_version=1,
                    reason="current",
                    updated_at="2026-06-13T00:00:00+00:00",
                )
            )
        ),
    )

    preview = service.preview("P1")

    assert _item(preview.required_files, "customer_feedback_form").status == "ready"


def test_customer_feedback_missing_when_current_output_missing_on_disk(tmp_path: Path) -> None:
    official = _official_with_required_folders(tmp_path)
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path, official),
        output_service=_OutputStatusService(
            _output_summary(
                ProjectOutputStatusItem(
                    output_kind=ProjectOutputKind.CUSTOMER_FEEDBACK_FORM,
                    status=ProjectOutputStatus.CURRENT,
                    output_path=str(official / "DL-001_Customer_Feedback_Form.xlsx"),
                    source=ProjectOutputSource.SYSTEM_GENERATED,
                    draft_id="draft-1",
                    draft_version=1,
                    reason="current",
                    updated_at="2026-06-13T00:00:00+00:00",
                )
            )
        ),
    )

    preview = service.preview("P1")

    assert _item(preview.required_files, "customer_feedback_form").status == "missing"


@dataclass
class _ProjectRepo:
    project: Project

    def get(self, project_id: str) -> Project | None:
        return self.project if self.project.project_id == project_id else None


class _WorkspaceRepo:
    def __init__(self, workspace: OfficialWorkspaceRecord | None) -> None:
        self._workspace = workspace

    def get_by_project(self, project_id: str) -> OfficialWorkspaceRecord | None:
        if self._workspace is None or self._workspace.project_id != project_id:
            return None
        return self._workspace


class _FailingAfterFirstCreateGateway:
    def create_missing_folders(self, paths: tuple[Path, ...]) -> tuple[Path, ...]:
        created: list[Path] = []
        for index, path in enumerate(paths):
            if index == 1:
                raise OfficialFolderRepairFailureError(
                    "folder creation failed",
                    created_paths=tuple(created),
                    failed_path=path,
                )
            path.mkdir(parents=True, exist_ok=True)
            created.append(path)
        return tuple(created)


class _RequestMaterialPreviewer:
    def __init__(self, preview: RequestMaterialPreview) -> None:
        self._preview = preview

    def preview(self, project_id: str) -> RequestMaterialPreview:
        return self._preview


class _OutputStatusService:
    def __init__(self, summary: ProjectOutputStatusSummary) -> None:
        self._summary = summary

    def get_status_summary(self, project_id: str) -> ProjectOutputStatusSummary:
        return self._summary


def _service(
    tmp_path: Path,
    *,
    workspace: OfficialWorkspaceRecord | None,
    repair_gateway: object | None = None,
    request_material_service: object | None = None,
    output_service: object | None = None,
) -> OfficialProjectFolderCheckService:
    return OfficialProjectFolderCheckService(
        project_repository=_ProjectRepo(
            Project(
                project_id="P1",
                project_no="DL-001",
                product_name="Connector",
                requestor="Alice",
                status=ProjectStatus.CONFIRMED,
            )
        ),
        workspace_repository=_WorkspaceRepo(workspace),
        repair_gateway=repair_gateway,
        request_material_service=request_material_service,
        output_status_service=output_service,
    )


def _workspace(tmp_path: Path, official: Path) -> OfficialWorkspaceRecord:
    local = tmp_path / "DL-001"
    return OfficialWorkspaceRecord(
        workspace_id="W1",
        project_id="P1",
        dl_number="DL-001",
        local_workspace_path=local,
        source_book_path=local / "Source Book",
        official_folder_path=official,
        manifest_path=local / ".connlab" / "manifest.json",
        template_source_path=tmp_path / "template",
        created_at="2026-06-13T00:00:00+00:00",
    )


def _official_with_required_folders(tmp_path: Path) -> Path:
    official = tmp_path / "DL-001" / "DL-001 Connector Qualification test"
    (official / "E-mail").mkdir(parents=True)
    (official / "Submitted Material").mkdir()
    (official / "Photos").mkdir()
    (official / "Test results" / "Final Examination").mkdir(parents=True)
    return official


def _request_material_preview(
    tmp_path: Path,
    *,
    status: str,
    item_status: str,
    target_area: str,
    review_required: bool = False,
) -> RequestMaterialPreview:
    target_path = tmp_path / "DL-001" / "DL-001 Connector Qualification test" / "Submitted Material" / "file.docx"
    return RequestMaterialPreview(
        project_id="P1",
        local_workspace_path=tmp_path / "DL-001",
        source_book_path=tmp_path / "DL-001" / "Source Book",
        official_project_folder_path=tmp_path / "DL-001" / "DL-001 Connector Qualification test",
        status=status,
        items=(
            RequestMaterialPreviewItem(
                source_asset_id="asset-1",
                source_asset_type="attachment",
                source_role="supporting_attachment",
                source_name="file.docx",
                source_path=tmp_path / "source" / "file.docx",
                dedupe_key="path:file.docx",
                target_area=target_area,
                target_path=target_path,
                action="already_present",
                status=item_status,
                message="Already collected.",
                review_required=review_required,
            ),
        ),
        blockers=tuple(),
        warnings=tuple(),
    )


def _output_summary(*items: ProjectOutputStatusItem) -> ProjectOutputStatusSummary:
    return ProjectOutputStatusSummary(
        project_id="P1",
        active_draft_id="draft-1",
        active_draft_version=1,
        items=items,
    )


def _item(items: tuple[object, ...], key: str):
    for item in items:
        if getattr(item, "key") == key:
            return item
    raise AssertionError(f"Missing item {key}")
