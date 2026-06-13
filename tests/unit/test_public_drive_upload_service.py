from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from backend.application.official_project_folder_check_service import (
    OfficialFolderCheckPreview,
)
from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.application.public_drive_upload_service import (
    PublicDriveUploadConflictError,
    PublicDriveUploadFileRecord,
    PublicDriveUploadService,
    PublicDriveUploadTargetChangedError,
)
from backend.domain import Project, ProjectStatus


def test_preview_blocks_without_completed_workspace(tmp_path: Path) -> None:
    service = _service(tmp_path, workspace=None, public_root=tmp_path / "public")

    preview = service.preview("P1")

    assert preview.status == "blocked"
    assert preview.next_action == "none"
    assert "Create local project folder before public-drive upload." in preview.blockers


def test_preview_blocks_without_public_project_location(tmp_path: Path) -> None:
    official = _official_folder(tmp_path)
    service = _service(tmp_path, workspace=_workspace(tmp_path, official), public_root=None)

    preview = service.preview("P1")

    assert preview.status == "blocked"
    assert preview.next_action == "none"
    assert "Public Project locations is not configured." in preview.blockers


def test_preview_blocks_when_task318_reports_folder_conflict(tmp_path: Path) -> None:
    official = _official_folder(tmp_path)
    public_root = tmp_path / "public"
    public_root.mkdir()
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path, official),
        public_root=public_root,
        folder_check=_folder_check(
            official,
            status="conflict",
            blockers=("Submitted Material is a file, expected folder.",),
        ),
    )

    preview = service.preview("P1")

    assert preview.status == "blocked"
    assert "Submitted Material is a file, expected folder." in preview.blockers


def test_preview_reports_add_for_required_empty_public_directory(tmp_path: Path) -> None:
    official = _official_folder(
        tmp_path,
        directories=("Photos", "Test results", "Test results/Final Examination"),
    )
    public_root = tmp_path / "public"
    public_root.mkdir()
    service = _service(tmp_path, workspace=_workspace(tmp_path, official), public_root=public_root)

    preview = service.preview("P1")

    photos = _item(preview.items, "Photos")
    final_exam = _item(preview.items, "Test results/Final Examination")
    assert preview.status == "ready"
    assert photos.kind == "directory"
    assert photos.action == "add"
    assert final_exam.kind == "directory"
    assert final_exam.action == "add"


def test_preview_reports_skip_for_existing_public_directory(tmp_path: Path) -> None:
    official = _official_folder(tmp_path, directories=("Photos",))
    public_root = _public_folder(tmp_path, official, directories=("Photos",))
    service = _service(tmp_path, workspace=_workspace(tmp_path, official), public_root=public_root)

    preview = service.preview("P1")

    item = _item(preview.items, "Photos")
    assert preview.status == "current"
    assert item.kind == "directory"
    assert item.action == "skip"
    assert item.status == "current"


def test_preview_reports_add_for_missing_public_file(tmp_path: Path) -> None:
    official = _official_folder(tmp_path, files={"Submitted Material/app.docx": "local"})
    public_root = tmp_path / "public"
    public_root.mkdir()
    service = _service(tmp_path, workspace=_workspace(tmp_path, official), public_root=public_root)

    preview = service.preview("P1")

    item = _item(preview.items, "Submitted Material/app.docx")
    assert preview.status == "ready"
    assert item.kind == "file"
    assert item.action == "add"
    assert item.status == "ready"


def test_preview_reports_conflict_for_unmanaged_existing_public_file(tmp_path: Path) -> None:
    official = _official_folder(tmp_path, files={"Submitted Material/app.docx": "local"})
    public_root = _public_folder(tmp_path, official, files={"Submitted Material/app.docx": "human"})
    service = _service(tmp_path, workspace=_workspace(tmp_path, official), public_root=public_root)

    preview = service.preview("P1")

    item = _item(preview.items, "Submitted Material/app.docx")
    assert preview.status == "conflict"
    assert item.action == "conflict"
    assert "not managed by ConnLab" in item.message


def test_preview_warns_for_non_colliding_extra_public_file(tmp_path: Path) -> None:
    official = _official_folder(tmp_path, files={"Submitted Material/app.docx": "local"})
    public_root = _public_folder(tmp_path, official, files={"operator-note.txt": "keep"})
    service = _service(tmp_path, workspace=_workspace(tmp_path, official), public_root=public_root)

    preview = service.preview("P1")

    assert preview.status == "warning"
    assert "extra unmanaged files" in preview.warnings[0]


def test_preview_allows_update_when_public_file_matches_last_connlab_upload(
    tmp_path: Path,
) -> None:
    official = _official_folder(tmp_path, files={"Submitted Material/app.docx": "new"})
    public_root = _public_folder(tmp_path, official, files={"Submitted Material/app.docx": "old"})
    repository = _UploadRepository()
    public_path = _planned_public_path(public_root, official, "Submitted Material/app.docx")
    repository.save_file(
        PublicDriveUploadFileRecord(
            project_id="P1",
            relative_path=Path("Submitted Material/app.docx"),
            public_path=public_path,
            local_fingerprint=_sha_text("old"),
            public_fingerprint=_sha_text("old"),
            uploaded_at="2026-06-13T00:00:00Z",
            operation_id="op1",
        )
    )
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path, official),
        public_root=public_root,
        upload_repository=repository,
    )

    preview = service.preview("P1")

    assert preview.status == "ready"
    assert _item(preview.items, "Submitted Material/app.docx").action == "update"


def test_upload_rechecks_public_fingerprint_before_update(tmp_path: Path) -> None:
    official = _official_folder(tmp_path, files={"Submitted Material/app.docx": "new"})
    public_root = _public_folder(tmp_path, official, files={"Submitted Material/app.docx": "old"})
    public_path = _planned_public_path(public_root, official, "Submitted Material/app.docx")
    repository = _UploadRepository()
    repository.save_file(
        PublicDriveUploadFileRecord(
            project_id="P1",
            relative_path=Path("Submitted Material/app.docx"),
            public_path=public_path,
            local_fingerprint=_sha_text("old"),
            public_fingerprint=_sha_text("old"),
            uploaded_at="2026-06-13T00:00:00Z",
            operation_id="op1",
        )
    )
    gateway = _MutatesPublicFileBeforeReplaceGateway(public_path, "human")
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path, official),
        public_root=public_root,
        upload_repository=repository,
        gateway=gateway,
    )

    result = service.upload("P1")

    assert result.upload_status == "partial"
    assert result.failed or result.conflicts
    assert public_path.read_text(encoding="utf-8") == "human"


def test_gateway_refuses_new_file_when_public_target_appears_before_final_create(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.txt"
    target = tmp_path / "public" / "source.txt"
    source.write_text("local", encoding="utf-8")
    gateway = _CreatesPublicTargetBeforeFinalCreateGateway(target, "human")

    with pytest.raises(PublicDriveUploadTargetChangedError):
        gateway.copy_new_file(source, target)

    assert target.read_text(encoding="utf-8") == "human"


def test_upload_copies_add_items_and_next_preview_is_current(tmp_path: Path) -> None:
    official = _official_folder(
        tmp_path,
        directories=("Photos",),
        files={"Submitted Material/app.docx": "local"},
    )
    public_root = tmp_path / "public"
    public_root.mkdir()
    repository = _UploadRepository()
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path, official),
        public_root=public_root,
        upload_repository=repository,
    )

    result = service.upload("P1")

    assert result.upload_status == "completed"
    assert _planned_public_path(public_root, official, "Submitted Material/app.docx").read_text(
        encoding="utf-8"
    ) == "local"
    assert _planned_public_path(public_root, official, "Photos").is_dir()
    assert result.preview.status == "current"


def test_upload_refuses_conflict_preview(tmp_path: Path) -> None:
    official = _official_folder(tmp_path, files={"Submitted Material/app.docx": "local"})
    public_root = _public_folder(tmp_path, official, files={"Submitted Material/app.docx": "human"})
    service = _service(tmp_path, workspace=_workspace(tmp_path, official), public_root=public_root)

    with pytest.raises(PublicDriveUploadConflictError):
        service.upload("P1")


def _service(
    tmp_path: Path,
    *,
    workspace: OfficialWorkspaceRecord | None,
    public_root: Path | None,
    folder_check: OfficialFolderCheckPreview | None = None,
    upload_repository: "_UploadRepository | None" = None,
    gateway: object | None = None,
) -> PublicDriveUploadService:
    official = workspace.official_folder_path if workspace else tmp_path / "missing"
    return PublicDriveUploadService(
        project_repository=_ProjectRepository(),
        workspace_repository=_WorkspaceRepository(workspace),
        public_drive_root=public_root,
        folder_check_service=_FolderCheckPreviewer(folder_check or _folder_check(official)),
        upload_repository=upload_repository or _UploadRepository(),
        gateway=gateway,
    )


def _official_folder(
    tmp_path: Path,
    *,
    directories: tuple[str, ...] = tuple(),
    files: dict[str, str] | None = None,
) -> Path:
    official = tmp_path / "local" / "DL-2026-05-011" / "DL-2026-05-011 Connector Qualification test"
    official.mkdir(parents=True)
    for relative in directories:
        (official / relative).mkdir(parents=True, exist_ok=True)
    for relative, content in (files or {}).items():
        path = official / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return official


def _public_folder(
    tmp_path: Path,
    official: Path,
    *,
    directories: tuple[str, ...] = tuple(),
    files: dict[str, str] | None = None,
) -> Path:
    public_root = tmp_path / "public"
    target = public_root / "DL-2026-05-011" / official.name
    target.mkdir(parents=True)
    for relative in directories:
        (target / relative).mkdir(parents=True, exist_ok=True)
    for relative, content in (files or {}).items():
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return public_root


def _planned_public_path(public_root: Path, official: Path, relative: str) -> Path:
    return public_root / "DL-2026-05-011" / official.name / relative


def _workspace(tmp_path: Path, official: Path) -> OfficialWorkspaceRecord:
    return OfficialWorkspaceRecord(
        workspace_id="W1",
        project_id="P1",
        dl_number="DL-2026-05-011",
        local_workspace_path=tmp_path / "local" / "DL-2026-05-011",
        source_book_path=tmp_path / "local" / "DL-2026-05-011" / "Source Book",
        official_folder_path=official,
        manifest_path=tmp_path / "local" / "DL-2026-05-011" / ".connlab" / "manifest.json",
        template_source_path=tmp_path / "template",
        created_at="2026-06-13T00:00:00Z",
    )


def _folder_check(
    official: Path,
    *,
    status: str = "ready",
    blockers: tuple[str, ...] = tuple(),
    warnings: tuple[str, ...] = tuple(),
) -> OfficialFolderCheckPreview:
    return OfficialFolderCheckPreview(
        project_id="P1",
        status=status,
        local_workspace_path=official.parent,
        official_project_folder_path=official,
        required_folders=tuple(),
        required_files=tuple(),
        blockers=blockers,
        warnings=warnings,
        next_action="none",
    )


def _item(items: tuple[object, ...], relative_path: str) -> object:
    normalized = Path(relative_path)
    for item in items:
        if item.relative_path == normalized:
            return item
    raise AssertionError(f"Missing item: {relative_path}")


def _sha_text(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class _ProjectRepository:
    def get(self, project_id: str) -> Project | None:
        return Project(
            project_id=project_id,
            project_no="DL-2026-05-011",
            product_name="Connector",
            requestor="Lab",
            status=ProjectStatus.CONFIRMED,
        )


class _WorkspaceRepository:
    def __init__(self, workspace: OfficialWorkspaceRecord | None) -> None:
        self._workspace = workspace

    def get_by_project(self, project_id: str) -> OfficialWorkspaceRecord | None:
        return self._workspace


class _FolderCheckPreviewer:
    def __init__(self, preview: OfficialFolderCheckPreview) -> None:
        self._preview = preview

    def preview(self, project_id: str) -> OfficialFolderCheckPreview:
        return self._preview


class _UploadRepository:
    def __init__(self) -> None:
        self.records: dict[tuple[str, Path], PublicDriveUploadFileRecord] = {}

    def get_file(self, project_id: str, relative_path: Path) -> PublicDriveUploadFileRecord | None:
        return self.records.get((project_id, relative_path))

    def save_file(self, record: PublicDriveUploadFileRecord) -> PublicDriveUploadFileRecord:
        self.records[(record.project_id, record.relative_path)] = record
        return record


class _MutatesPublicFileBeforeReplaceGateway:
    def __init__(self, public_path: Path, content: str) -> None:
        from backend.infrastructure.files.public_drive_upload_gateway import PublicDriveUploadGateway

        self._delegate = PublicDriveUploadGateway()
        self._public_path = public_path
        self._content = content

    def fingerprint(self, path: Path) -> str:
        return self._delegate.fingerprint(path)

    def list_files(self, root: Path) -> tuple[Path, ...]:
        return self._delegate.list_files(root)

    def list_directories(self, root: Path) -> tuple[Path, ...]:
        return self._delegate.list_directories(root)

    def create_directory(self, target: Path) -> None:
        self._delegate.create_directory(target)

    def copy_new_file(self, source: Path, target: Path) -> None:
        self._delegate.copy_new_file(source, target)

    def replace_managed_file(
        self,
        source: Path,
        target: Path,
        *,
        expected_public_fingerprint: str | None,
    ) -> None:
        self._public_path.write_text(self._content, encoding="utf-8")
        self._delegate.replace_managed_file(
            source,
            target,
            expected_public_fingerprint=expected_public_fingerprint,
        )


class _CreatesPublicTargetBeforeFinalCreateGateway:
    def __init__(self, public_path: Path, content: str) -> None:
        from backend.infrastructure.files.public_drive_upload_gateway import PublicDriveUploadGateway

        class RacingGateway(PublicDriveUploadGateway):
            def _before_new_file_final_create(self, target: Path) -> None:
                public_path.parent.mkdir(parents=True, exist_ok=True)
                public_path.write_text(content, encoding="utf-8")

        self._delegate = RacingGateway()

    def copy_new_file(self, source: Path, target: Path) -> None:
        self._delegate.copy_new_file(source, target)
