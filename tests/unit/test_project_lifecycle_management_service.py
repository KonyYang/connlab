from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from backend.application.no_ltr_project_cleanup_service import ProjectCleanupAuditRecord
from backend.application.project_lifecycle_management_service import (
    ProjectLifecycleManagementService,
    ProjectStopCommand,
)
from backend.domain import Project, ProjectStatus, ProjectTemporaryContext


def test_safe_temporary_project_can_be_deleted() -> None:
    stores = _Stores(project=_project(), temporary_context=_context())
    service = stores.service()

    preview = service.preview_temporary_delete("P1")
    result = service.delete_temporary_project("P1")

    assert preview.can_delete is True
    assert preview.recommended_action == "delete"
    assert result.deleted is True
    assert result.deleted_temporary_context is True
    assert stores.projects.deleted == ["P1"]
    assert stores.temporary_contexts.deleted == ["P1"]


def test_registered_project_delete_is_blocked_and_recommends_stop() -> None:
    stores = _Stores(project=_project(project_no="DL-2026-06-001"))
    service = stores.service()

    preview = service.preview_temporary_delete("P1")

    assert preview.can_delete is False
    assert preview.recommended_action == "stop"
    assert any("registered project number" in blocker for blocker in preview.blockers)


def test_matrix_draft_blocks_temporary_delete_in_v1() -> None:
    stores = _Stores(
        project=_project(),
        temporary_context=_context(),
        matrix_drafts=[object()],
    )
    service = stores.service()

    preview = service.preview_temporary_delete("P1")

    assert preview.can_delete is False
    assert any("Temporary Matrix drafts exist" in blocker for blocker in preview.blockers)


def test_linked_source_material_blocks_temporary_delete_in_v1() -> None:
    stores = _Stores(
        project=_project(),
        temporary_context=ProjectTemporaryContext(
            context_id="CTX1",
            project_id="P1",
            source_asset_ids=("ASSET1",),
        ),
    )
    service = stores.service()

    preview = service.preview_temporary_delete("P1")

    assert preview.can_delete is False
    assert any("Temporary source material is linked" in blocker for blocker in preview.blockers)


def test_project_file_assets_block_temporary_delete() -> None:
    stores = _Stores(
        project=_project(),
        temporary_context=_context(),
        file_assets=[object()],
    )
    service = stores.service()

    preview = service.preview_temporary_delete("P1")

    assert preview.can_delete is False
    assert any("Project file assets exist" in blocker for blocker in preview.blockers)


def test_stop_project_maps_to_cancelled_and_records_reason() -> None:
    stores = _Stores(project=_project(status=ProjectStatus.DRAFT))
    service = stores.service()

    result = service.stop_project(
        ProjectStopCommand(
            project_id="P1",
            reason="Customer stopped feasibility review.",
            operator="Lab User",
        )
    )

    assert result.status == "cancelled"
    assert result.status_label == "Stopped"
    assert result.reason == "Customer stopped feasibility review."
    assert result.audit_recorded is True
    assert stores.projects.updated[-1].status is ProjectStatus.CANCELLED
    assert stores.audits.items[-1].reason == "Customer stopped feasibility review."


@dataclass
class _Stores:
    project: Project
    temporary_context: ProjectTemporaryContext | None = None
    ltrs: list[object] | None = None
    active_matrix: object | None = None
    workspace: object | None = None
    folders: list[object] | None = None
    outputs: list[object] | None = None
    file_assets: list[object] | None = None
    request_material: object | None = None
    confirmed_fee: object | None = None
    matrix_drafts: list[object] | None = None

    def __post_init__(self) -> None:
        self.projects = _ProjectStore(self.project)
        self.temporary_contexts = _TemporaryContextStore(self.temporary_context)
        self.audits = _AuditStore()

    def service(self) -> ProjectLifecycleManagementService:
        return ProjectLifecycleManagementService(
            project_store=self.projects,
            temporary_context_store=self.temporary_contexts,
            ltr_store=_ListStore(self.ltrs),
            confirmed_matrix_store=_ActiveStore(self.active_matrix),
            official_workspace_store=_GetStore(self.workspace),
            folder_store=_ListStore(self.folders),
            file_asset_store=_ListStore(self.file_assets),
            output_store=_ListStore(self.outputs),
            request_material_store=_LatestStore(self.request_material),
            confirmed_fee_store=_LatestStore(self.confirmed_fee),
            matrix_draft_store=_ListStore(self.matrix_drafts),
            audit_store=self.audits,
        )


class _ProjectStore:
    def __init__(self, project: Project) -> None:
        self.project = project
        self.updated: list[Project] = []
        self.deleted: list[str] = []

    def get(self, project_id: str) -> Project | None:
        return self.project if self.project.project_id == project_id else None

    def update(self, project: Project) -> Project:
        self.project = project
        self.updated.append(project)
        return project

    def delete(self, project_id: str) -> bool:
        self.deleted.append(project_id)
        return True


class _TemporaryContextStore:
    def __init__(self, context: ProjectTemporaryContext | None) -> None:
        self.context = context
        self.deleted: list[str] = []

    def get_by_project(self, project_id: str) -> ProjectTemporaryContext | None:
        if self.context and self.context.project_id == project_id:
            return self.context
        return None

    def delete_by_project(self, project_id: str) -> bool:
        self.deleted.append(project_id)
        return self.context is not None


class _ListStore:
    def __init__(self, items: list[object] | None = None) -> None:
        self.items = items or []

    def list_by_project(self, project_id: str) -> list[object]:
        return self.items


class _ActiveStore:
    def __init__(self, item: object | None = None) -> None:
        self.item = item

    def get_active_by_project(self, project_id: str) -> object | None:
        return self.item


class _GetStore:
    def __init__(self, item: object | None = None) -> None:
        self.item = item

    def get_by_project(self, project_id: str) -> object | None:
        return self.item


class _LatestStore:
    def __init__(self, item: object | None = None) -> None:
        self.item = item

    def get_latest_by_project(self, project_id: str) -> object | None:
        return self.item

    def latest_by_project(self, project_id: str) -> object | None:
        return self.item


class _AuditStore:
    def __init__(self) -> None:
        self.items: list[ProjectCleanupAuditRecord] = []

    def create(self, record: ProjectCleanupAuditRecord) -> ProjectCleanupAuditRecord:
        self.items.append(record)
        return record


def _project(
    *,
    project_no: str | None = None,
    status: ProjectStatus = ProjectStatus.DRAFT,
) -> Project:
    return Project(
        project_id="P1",
        project_no=project_no,
        product_name="Temporary planning project",
        requestor="Lab User",
        status=status,
        created_on=date(2026, 6, 13),
    )


def _context() -> ProjectTemporaryContext:
    return ProjectTemporaryContext(
        context_id="CTX1",
        project_id="P1",
        request_summary="Temporary request",
    )
