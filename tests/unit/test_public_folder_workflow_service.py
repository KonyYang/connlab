from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from backend.application.official_project_folder_check_service import OfficialFolderCheckPreview
from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.application.public_folder_path_resolver import PublicFolderPathError, PublicFolderPathResolver
from backend.application.public_folder_workflow_service import (
    PublicFolderWorkflowConflictError,
    PublicFolderWorkflowExecuteCommand,
    PublicFolderWorkflowService,
    PublicFolderWorkflowState,
)
from backend.application.public_folder_year_resolver import PublicFolderYearResolver
from backend.domain import Project, ProjectStatus
from backend.infrastructure.files.public_folder_workflow_gateway import PublicFolderWorkflowGateway


def test_path_resolver_blocks_missing_public_root(tmp_path: Path) -> None:
    resolver = PublicFolderPathResolver()

    with pytest.raises(PublicFolderPathError):
        resolver.resolve(
            public_root=tmp_path / "missing",
            year=2026,
            project_folder_name="DL-1 Product",
        )

    assert not (tmp_path / "missing").exists()


def test_sync_execute_copies_to_open_and_records_operation(tmp_path: Path) -> None:
    service, repository, paths = _service(tmp_path)
    (paths["local"] / "Submitted Material").mkdir()
    (paths["local"] / "Submitted Material" / "app.docx").write_text("v1", encoding="utf-8")

    preview = service.preview_sync("P1")
    result = service.execute_sync(
        "P1",
        PublicFolderWorkflowExecuteCommand(
            preview_hash=preview.preview_hash,
            confirmed=True,
            confirm_directory_creation=True,
            operator="tester",
        ),
    )

    copied = paths["public"] / "Open" / "2026" / paths["local"].name / "Submitted Material" / "app.docx"
    assert result.status == "completed"
    assert copied.read_text(encoding="utf-8") == "v1"
    assert repository.operations[-1].operation_type == "sync"
    assert repository.get_file("P1", Path("Submitted Material/app.docx")) is not None


def test_execute_rejects_stale_preview_hash(tmp_path: Path) -> None:
    service, _repository, paths = _service(tmp_path)
    (paths["local"] / "file.txt").write_text("v1", encoding="utf-8")
    preview = service.preview_sync("P1")
    target = paths["public"] / "Open" / "2026" / paths["local"].name / "file.txt"
    target.parent.mkdir(parents=True)
    target.write_text("human", encoding="utf-8")

    with pytest.raises(PublicFolderWorkflowConflictError):
        service.execute_sync(
            "P1",
            PublicFolderWorkflowExecuteCommand(
                preview_hash=preview.preview_hash,
                confirmed=True,
                confirm_directory_creation=True,
            ),
        )


def test_submit_moves_open_to_closed_and_locks_sync(tmp_path: Path) -> None:
    service, repository, paths = _service(tmp_path)
    (paths["local"] / "file.txt").write_text("v1", encoding="utf-8")
    sync = service.preview_sync("P1")
    service.execute_sync(
        "P1",
        PublicFolderWorkflowExecuteCommand(
            preview_hash=sync.preview_hash,
            confirmed=True,
            confirm_directory_creation=True,
        ),
    )

    submit = service.preview_submit("P1")
    service.execute_submit(
        "P1",
        PublicFolderWorkflowExecuteCommand(
            preview_hash=submit.preview_hash,
            confirmed=True,
            confirm_directory_creation=True,
        ),
    )

    closed_file = paths["public"] / "Closed" / "2026" / paths["local"].name / "file.txt"
    assert closed_file.read_text(encoding="utf-8") == "v1"
    assert repository.get_state("P1").sync_locked is True
    assert "Sync is locked after Submit." in service.preview_sync("P1").blockers


def test_submit_preview_blocks_unmanaged_public_open_file(tmp_path: Path) -> None:
    service, _repository, paths = _service(tmp_path)
    (paths["local"] / "file.txt").write_text("v1", encoding="utf-8")
    sync = service.preview_sync("P1")
    service.execute_sync(
        "P1",
        PublicFolderWorkflowExecuteCommand(
            preview_hash=sync.preview_hash,
            confirmed=True,
            confirm_directory_creation=True,
        ),
    )
    open_folder = paths["public"] / "Open" / "2026" / paths["local"].name
    closed_folder = paths["public"] / "Closed" / "2026" / paths["local"].name
    unmanaged = open_folder / "human-extra.txt"
    unmanaged.write_text("outside ConnLab", encoding="utf-8")

    submit = service.preview_submit("P1")

    assert submit.status == "conflict"
    assert submit.next_action == "none"
    assert submit.counts["conflict"] == 1
    assert "Public Open file is not managed by ConnLab" in submit.conflicts[0]
    with pytest.raises(PublicFolderWorkflowConflictError):
        service.execute_submit(
            "P1",
            PublicFolderWorkflowExecuteCommand(
                preview_hash=submit.preview_hash,
                confirmed=True,
                confirm_directory_creation=True,
            ),
        )
    assert open_folder.is_dir()
    assert (open_folder / "file.txt").read_text(encoding="utf-8") == "v1"
    assert unmanaged.read_text(encoding="utf-8") == "outside ConnLab"
    assert not closed_folder.exists()


def test_submit_execute_rejects_stale_preview_when_unmanaged_file_appears(tmp_path: Path) -> None:
    service, _repository, paths = _service(tmp_path)
    (paths["local"] / "file.txt").write_text("v1", encoding="utf-8")
    sync = service.preview_sync("P1")
    service.execute_sync(
        "P1",
        PublicFolderWorkflowExecuteCommand(
            preview_hash=sync.preview_hash,
            confirmed=True,
            confirm_directory_creation=True,
        ),
    )
    submit = service.preview_submit("P1")
    assert submit.status == "ready"
    open_folder = paths["public"] / "Open" / "2026" / paths["local"].name
    closed_folder = paths["public"] / "Closed" / "2026" / paths["local"].name
    (open_folder / "human-extra.txt").write_text("outside ConnLab", encoding="utf-8")

    with pytest.raises(PublicFolderWorkflowConflictError, match="stale"):
        service.execute_submit(
            "P1",
            PublicFolderWorkflowExecuteCommand(
                preview_hash=submit.preview_hash,
                confirmed=True,
                confirm_directory_creation=True,
            ),
        )
    assert open_folder.is_dir()
    assert (open_folder / "human-extra.txt").exists()
    assert not closed_folder.exists()


def test_pull_copies_closed_to_local_history_without_overwriting_current(tmp_path: Path) -> None:
    service, _repository, paths = _service(tmp_path)
    closed = paths["public"] / "Closed" / "2026" / paths["local"].name
    closed.mkdir(parents=True)
    (closed / "approved.txt").write_text("approved", encoding="utf-8")
    (paths["local"] / "current.txt").write_text("current", encoding="utf-8")

    preview = service.preview_pull("P1")
    result = service.execute_pull(
        "P1",
        PublicFolderWorkflowExecuteCommand(
            preview_hash=preview.preview_hash,
            confirmed=True,
            confirm_directory_creation=True,
        ),
    )

    assert result.status == "completed"
    assert (paths["local"] / "current.txt").read_text(encoding="utf-8") == "current"
    assert preview.target_path is not None
    assert (preview.target_path / "approved.txt").read_text(encoding="utf-8") == "approved"


def _service(tmp_path: Path):
    local = tmp_path / "local" / "DL-2026-06-001 Product"
    public = tmp_path / "PublicProject"
    local.mkdir(parents=True)
    public.mkdir()
    project_repository = _Projects()
    ltr_repository = _Ltrs()
    repository = _WorkflowRepository()
    service = PublicFolderWorkflowService(
        project_repository=project_repository,
        workspace_repository=_Workspaces(local),
        year_resolver=PublicFolderYearResolver(
            project_repository=project_repository,
            ltr_repository=ltr_repository,
        ),
        workflow_repository=repository,
        folder_check_service=_FolderCheck(local),
        public_root=public,
        gateway=PublicFolderWorkflowGateway(),
    )
    return service, repository, {"local": local, "public": public}


class _Projects:
    def get(self, project_id: str) -> Project | None:
        if project_id != "P1":
            return None
        return Project(
            project_id="P1",
            project_no="DL-2026-06-001",
            product_name="Product",
            requestor="User",
            status=ProjectStatus.LTR_REGISTERED,
            created_on=date(2026, 6, 30),
        )


class _Ltrs:
    def list_by_project(self, project_id: str):
        return []


class _Workspaces:
    def __init__(self, official_folder: Path) -> None:
        self._official_folder = official_folder

    def get_by_project(self, project_id: str) -> OfficialWorkspaceRecord | None:
        return OfficialWorkspaceRecord(
            workspace_id="workspace",
            project_id=project_id,
            dl_number="DL-2026-06-001",
            local_workspace_path=self._official_folder.parent,
            source_book_path=self._official_folder.parent / "Source Book",
            official_folder_path=self._official_folder,
            manifest_path=self._official_folder.parent / ".connlab" / "manifest.json",
            template_source_path=Path("template"),
            created_at="2026-06-30T00:00:00+00:00",
        )


class _FolderCheck:
    def __init__(self, official_folder: Path) -> None:
        self._official_folder = official_folder

    def preview(self, project_id: str) -> OfficialFolderCheckPreview:
        return OfficialFolderCheckPreview(
            project_id=project_id,
            status="ready",
            local_workspace_path=self._official_folder.parent,
            official_project_folder_path=self._official_folder,
            required_folders=tuple(),
            required_files=tuple(),
            blockers=tuple(),
            warnings=tuple(),
            next_action="none",
        )


class _WorkflowRepository:
    def __init__(self) -> None:
        self.states: dict[str, PublicFolderWorkflowState] = {}
        self.files = {}
        self.operations = []

    def get_state(self, project_id: str) -> PublicFolderWorkflowState:
        return self.states.get(project_id, PublicFolderWorkflowState(project_id=project_id))

    def save_state(self, state: PublicFolderWorkflowState) -> PublicFolderWorkflowState:
        self.states[state.project_id] = state
        return state

    def get_file(self, project_id: str, relative_path: Path):
        return self.files.get((project_id, relative_path.as_posix()))

    def save_file(self, record):
        self.files[(record.project_id, record.relative_path.as_posix())] = record
        return record

    def rebase_files(self, *, project_id: str, old_root: Path, new_root: Path, operation_id: str, updated_at: str) -> None:
        for key, record in list(self.files.items()):
            if key[0] != project_id:
                continue
            try:
                relative = record.public_path.relative_to(old_root)
            except ValueError:
                continue
            self.files[key] = record.__class__(
                project_id=record.project_id,
                relative_path=record.relative_path,
                public_path=new_root / relative,
                local_fingerprint=record.local_fingerprint,
                public_fingerprint=record.public_fingerprint,
                updated_at=updated_at,
                operation_id=operation_id,
            )

    def save_operation(self, record):
        self.operations.append(record)
        return record
