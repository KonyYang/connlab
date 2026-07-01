from pathlib import Path

from backend.application.project_folder_open_service import (
    ProjectFolderOpenResult,
    ProjectFolderOpenService,
)
from backend.application.public_folder_workflow_service import (
    PublicFolderWorkflowContext,
)


def test_project_folder_open_service_opens_backend_resolved_directory(tmp_path):
    folder = tmp_path / "DL-2026-06-001" / "Official"
    folder.mkdir(parents=True)
    workflow = FakeWorkflowService(
        PublicFolderWorkflowContext(
            project_id="project-1",
            auto_sync_enabled=False,
            sync_locked=False,
            submitted_at=None,
            public_root=None,
            public_root_class=None,
            public_folder_year=None,
            year_source=None,
            year_evidence=None,
            local_official_folder_path=folder,
            public_open_path=None,
            public_closed_path=None,
            blockers=(),
            warnings=(),
        )
    )
    gateway = FakeOpenGateway()
    service = ProjectFolderOpenService(workflow_service=workflow, gateway=gateway)

    result = service.open_local_project_folder("project-1")

    assert result == ProjectFolderOpenResult(
        project_id="project-1",
        status="opened",
        message="Project folder opened.",
        local_official_folder_path=folder,
    )
    assert gateway.opened == [folder]
    assert workflow.requested_project_ids == ["project-1"]


def test_project_folder_open_service_blocks_without_local_path():
    workflow = FakeWorkflowService(
        PublicFolderWorkflowContext(
            project_id="project-1",
            auto_sync_enabled=False,
            sync_locked=False,
            submitted_at=None,
            public_root=None,
            public_root_class=None,
            public_folder_year=None,
            year_source=None,
            year_evidence=None,
            local_official_folder_path=None,
            public_open_path=None,
            public_closed_path=None,
            blockers=(),
            warnings=(),
        )
    )
    gateway = FakeOpenGateway()
    service = ProjectFolderOpenService(workflow_service=workflow, gateway=gateway)

    result = service.open_local_project_folder("project-1")

    assert result.status == "blocked"
    assert result.message == "Project folder is not available yet."
    assert result.local_official_folder_path is None
    assert gateway.opened == []


class FakeWorkflowService:
    def __init__(self, context):
        self._context = context
        self.requested_project_ids = []

    def context(self, project_id):
        self.requested_project_ids.append(project_id)
        return self._context


class FakeOpenGateway:
    def __init__(self):
        self.opened = []

    def open_directory(self, path: Path) -> ProjectFolderOpenResult:
        self.opened.append(path)
        return ProjectFolderOpenResult(
            project_id="",
            status="opened",
            message="Project folder opened.",
            local_official_folder_path=path,
        )
