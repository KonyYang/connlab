# TASK_319 Public Drive Upload Update Preview Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a preview-first public-drive upload/update workflow for the local Official project folder.

**Architecture:** Backend owns path planning, file comparison, conflict detection, safe copy, and upload-state persistence. Frontend only consumes typed preview/upload APIs and presents a Project Folder row plus one current action. Public-drive writes are explicit, conservative, and never destructive.

**Tech Stack:** Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.x, pathlib/shutil file operations behind infrastructure gateways, React, TypeScript, Vitest, pytest.

---

Status: Implemented. TASK_319 scope is complete after validation.

Execution note: the checkbox plan below is retained as the authored implementation plan. Completion status and validation evidence are recorded here and in `docs/task_board.md`.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Task file:

- `tasks/TASK_319_PUBLIC_DRIVE_UPLOAD_UPDATE_PREVIEW.md`

Predecessors:

- `TASK_316_LOCAL_PROJECT_WORKSPACE_CREATION_FROM_TEMPLATE`, complete.
- `TASK_317_SOURCE_BOOK_AND_REQUEST_MATERIAL_COLLECTION`, complete.
- `TASK_318_OFFICIAL_PROJECT_FOLDER_CHECK_AND_REPAIR`, complete.

Implementation worker must read:

1. `AGENTS.md`
2. `docs/task_board.md`
3. `tasks/TASK_319_PUBLIC_DRIVE_UPLOAD_UPDATE_PREVIEW.md`
4. `docs/task_319_public_drive_upload_update_preview_plan.md`
5. `tasks/TASK_318_OFFICIAL_PROJECT_FOLDER_CHECK_AND_REPAIR.md`
6. `docs/task_318_official_project_folder_check_and_repair_plan.md`
7. `tasks/TASK_317A_PROJECT_FOLDER_PREPARATION_UI_BLUEPRINT.md`
8. `docs/project_management/TASK_EXECUTION_SKILL.md`
9. `docs/project_management/TASK_REVIEW_CHECKLIST.md`
10. `docs/02_ARCHITECTURE_RULES.md`
11. `docs/frontend_architecture_rules.md`

Because TASK_319 changes Workbench UI and user-facing copy, implementation must load `$impeccable` product context before UI work.

## Step 1 - Task Understanding

Goal:

- Preview and execute safe upload/update from the local Official project folder to the configured public-drive project location.

Inputs:

- project id
- completed official workspace record from TASK_316
- real local Official project folder
- TASK_318 Official folder check preview
- Settings resource `Public Project locations`
- previous per-file upload records
- real public-drive file system state

Outputs:

- public-drive upload preview
- per-file add/update/skip/conflict/deferred items
- upload result
- per-file upload state records
- Workbench `Public drive upload` row and next action state

Involved modules:

- backend application service
- backend infrastructure file gateway
- backend storage repository
- backend API route/dependency wiring
- frontend API client
- Project Workbench model/selectors/layout
- pytest, API integration tests, Vitest/static shell tests

Not allowed:

- no deletion of public-drive files
- no silent overwrite
- no conflict resolution or merge
- no generated documents
- no Section 2 write-back
- no request-material re-copy
- no folder repair
- no background sync/watchers
- no StepInstance/TestResult/evidence/report/AI/permissions/LAN/multi-user work

## Step 2 - File Structure

Create:

- `backend/application/public_drive_upload_service.py`
  - Application service, DTO dataclasses, status calculation, upload orchestration.
- `backend/infrastructure/files/public_drive_upload_gateway.py`
  - File-system adapter for fingerprinting, directory creation, and copy.
- `backend/infrastructure/storage/repositories/public_drive_upload.py`
  - SQLite-backed per-file upload state repository.
- `backend/api/routes_public_drive_upload.py`
  - `GET /api/projects/{project_id}/public-drive/preview`
  - `POST /api/projects/{project_id}/public-drive/upload`
- `tests/unit/test_public_drive_upload_service.py`
  - Service preview/upload/conflict/partial failure tests.
- `tests/integration/test_public_drive_upload_api.py`
  - API smoke for preview and upload.

Modify:

- `backend/api/dependencies.py`
  - Wire service, gateway, repository, and settings path.
- `backend/api/main.py`
  - Include the public-drive upload router.
- `backend/infrastructure/storage/schema.py` or the existing migration/schema owner
  - Add upload-state table if current storage pattern requires schema declaration.
- `frontend/src/api/client.ts`
  - Add typed preview/upload DTOs and calls.
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
  - Fetch preview and call upload.
- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
  - Pass public-drive state/actions to layout.
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
  - Add next-action priority and status mapping.
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
  - Cover next-action routing.
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - Add row and action wiring.
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
  - Cover UI action visibility and conflict state.
- `tests/unit/test_frontend_shell_files.py`
  - Add TASK_319 static guards.
- `docs/task_board.md`
  - Record TASK_319 completion only after implementation and validation.

Do not modify:

- old `/project-package/preview` as the TASK_319 read model
- Matrix editor
- Fee Evaluation generation logic
- Section 2 write-back logic
- request material collection copy behavior

## Step 3 - Backend Domain Shapes

Use application dataclasses, not SQLAlchemy models, as service returns:

```python
@dataclass(frozen=True, slots=True)
class PublicDriveUploadItem:
    kind: str
    relative_path: Path
    local_path: Path | None
    public_path: Path
    action: str
    status: str
    message: str


@dataclass(frozen=True, slots=True)
class PublicDriveUploadPreview:
    project_id: str
    status: str
    local_official_folder_path: Path | None
    public_project_folder_path: Path | None
    items: tuple[PublicDriveUploadItem, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    counts: dict[str, int]
    next_action: str


@dataclass(frozen=True, slots=True)
class PublicDriveUploadResult:
    project_id: str
    upload_status: str
    copied: tuple[PublicDriveUploadItem, ...]
    updated: tuple[PublicDriveUploadItem, ...]
    skipped: tuple[PublicDriveUploadItem, ...]
    conflicts: tuple[PublicDriveUploadItem, ...]
    failed: tuple[PublicDriveUploadItem, ...]
    errors: tuple[str, ...]
    preview: PublicDriveUploadPreview
```

Status vocabulary:

- preview status: `blocked`, `ready`, `current`, `conflict`, `warning`
- item kind: `file`, `directory`
- item action: `add`, `update`, `skip`, `conflict`, `deferred`
- item status: `ready`, `current`, `conflict`, `deferred`, `failed`
- next action: `preview`, `upload`, `none`
- upload status: `completed`, `partial`, `blocked`, `conflict`

## Step 4 - Backend TDD: Preview Blocks Without Prerequisites

Files:

- Create: `tests/unit/test_public_drive_upload_service.py`
- Create later: `backend/application/public_drive_upload_service.py`

- [ ] **Step 4.1: Write failing tests**

```python
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
        folder_check=_folder_check(status="conflict", blockers=("Submitted Material is a file, expected folder.",)),
    )

    preview = service.preview("P1")

    assert preview.status == "blocked"
    assert "Submitted Material is a file, expected folder." in preview.blockers


def test_preview_blocks_when_task318_reports_blocking_missing_request_material(tmp_path: Path) -> None:
    official = _official_folder(tmp_path)
    public_root = tmp_path / "public"
    public_root.mkdir()
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path, official),
        public_root=public_root,
        folder_check=_folder_check(status="blocked", blockers=("Collect request material before public-drive upload.",)),
    )

    preview = service.preview("P1")

    assert preview.status == "blocked"
    assert "Collect request material before public-drive upload." in preview.blockers


def test_preview_keeps_non_blocking_task318_warning_visible(tmp_path: Path) -> None:
    official = _official_folder(tmp_path, files={"Submitted Material/app.docx": "local"})
    public_root = tmp_path / "public"
    public_root.mkdir()
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path, official),
        public_root=public_root,
        folder_check=_folder_check(status="warning", warnings=("Customer Feedback form generation is deferred.",)),
    )

    preview = service.preview("P1")

    assert preview.status == "warning"
    assert "Customer Feedback form generation is deferred." in preview.warnings
```

- [ ] **Step 4.2: Run tests and verify failure**

```powershell
py -m pytest tests\unit\test_public_drive_upload_service.py -q
```

Expected: fails because `backend.application.public_drive_upload_service` does not exist.

- [ ] **Step 4.3: Implement minimal service skeleton**

Create `backend/application/public_drive_upload_service.py` with:

```python
class PublicDriveUploadService:
    def __init__(
        self,
        *,
        project_repository: ProjectRepositoryPort,
        workspace_repository: OfficialWorkspaceRepositoryPort,
        public_drive_root: Path | None,
        folder_check_service: OfficialFolderCheckPreviewerPort,
        upload_repository: PublicDriveUploadRepositoryPort,
        gateway: PublicDriveUploadGatewayPort,
    ) -> None:
        self._projects = project_repository
        self._workspaces = workspace_repository
        self._public_drive_root = public_drive_root
        self._folder_check_service = folder_check_service
        self._upload_repository = upload_repository
        self._gateway = gateway

    def preview(self, project_id: str) -> PublicDriveUploadPreview:
        self._require_project(project_id)
        workspace = self._workspaces.get_by_project(project_id)
        if workspace is None or not workspace.official_folder_path.is_dir():
            return _blocked(project_id, "Create local project folder before public-drive upload.")
        if self._public_drive_root is None or not self._public_drive_root.is_dir():
            return _blocked(project_id, "Public Project locations is not configured.")
        folder_check = self._folder_check_service.preview(project_id)
        if folder_check.status in {"blocked", "conflict"}:
            return _blocked(project_id, *folder_check.blockers)
        return self._build_preview(project_id, workspace)
```

- [ ] **Step 4.4: Run tests and verify pass**

```powershell
py -m pytest tests\unit\test_public_drive_upload_service.py -q
```

Expected: prerequisite tests pass.

## Step 5 - Backend TDD: Preview Directory And File Actions

Files:

- Modify: `tests/unit/test_public_drive_upload_service.py`
- Modify: `backend/application/public_drive_upload_service.py`
- Create: `backend/infrastructure/files/public_drive_upload_gateway.py`

- [ ] **Step 5.1: Add failing action tests**

```python
def test_preview_reports_add_for_required_empty_public_directory(tmp_path: Path) -> None:
    official = _official_folder(tmp_path, directories=("Photos", "Test results/Final Examination"))
    public_root = tmp_path / "public"
    public_root.mkdir()
    service = _service(tmp_path, workspace=_workspace(tmp_path, official), public_root=public_root)

    preview = service.preview("P1")

    photos = _item(preview.items, "Photos")
    final_exam = _item(preview.items, "Test results/Final Examination")
    assert photos.kind == "directory"
    assert photos.action == "add"
    assert final_exam.kind == "directory"
    assert final_exam.action == "add"


def test_preview_reports_skip_for_existing_public_directory(tmp_path: Path) -> None:
    official = _official_folder(tmp_path, directories=("Photos",))
    public_root = _public_folder(tmp_path, directories=("Photos",))
    service = _service(tmp_path, workspace=_workspace(tmp_path, official), public_root=public_root)

    preview = service.preview("P1")

    item = _item(preview.items, "Photos")
    assert item.kind == "directory"
    assert item.action == "skip"
    assert item.status == "current"


def test_preview_conflicts_when_public_directory_target_is_file(tmp_path: Path) -> None:
    official = _official_folder(tmp_path, directories=("Photos",))
    public_root = _public_folder(tmp_path, files={"Photos": "not a folder"})
    service = _service(tmp_path, workspace=_workspace(tmp_path, official), public_root=public_root)

    preview = service.preview("P1")

    item = _item(preview.items, "Photos")
    assert preview.status == "conflict"
    assert item.kind == "directory"
    assert item.action == "conflict"


def test_preview_reports_add_for_missing_public_file(tmp_path: Path) -> None:
    official = _official_folder(tmp_path, files={"Submitted Material/app.docx": "local"})
    public_root = tmp_path / "public"
    public_root.mkdir()
    service = _service(tmp_path, workspace=_workspace(tmp_path, official), public_root=public_root)

    preview = service.preview("P1")

    item = _item(preview.items, "Submitted Material/app.docx")
    assert preview.status == "ready"
    assert item.action == "add"
    assert item.status == "ready"


def test_preview_reports_skip_for_matching_public_file(tmp_path: Path) -> None:
    official = _official_folder(tmp_path, files={"Submitted Material/app.docx": "same"})
    public_root = _public_folder(tmp_path, files={"Submitted Material/app.docx": "same"})
    service = _service(tmp_path, workspace=_workspace(tmp_path, official), public_root=public_root)

    preview = service.preview("P1")

    item = _item(preview.items, "Submitted Material/app.docx")
    assert preview.status == "current"
    assert item.action == "skip"
    assert item.status == "current"


def test_preview_reports_conflict_for_unmanaged_existing_public_file(tmp_path: Path) -> None:
    official = _official_folder(tmp_path, files={"Submitted Material/app.docx": "local"})
    public_root = _public_folder(tmp_path, files={"Submitted Material/app.docx": "human"})
    service = _service(tmp_path, workspace=_workspace(tmp_path, official), public_root=public_root)

    preview = service.preview("P1")

    item = _item(preview.items, "Submitted Material/app.docx")
    assert preview.status == "conflict"
    assert item.action == "conflict"
    assert "Public-drive file is not managed by ConnLab." in item.message
```

- [ ] **Step 5.2: Run tests and verify failure**

```powershell
py -m pytest tests\unit\test_public_drive_upload_service.py -q
```

Expected: action tests fail because `_build_preview` and directory handling are not implemented.

- [ ] **Step 5.3: Implement gateway fingerprint/list helpers**

Create `backend/infrastructure/files/public_drive_upload_gateway.py`:

```python
class PublicDriveUploadGateway:
    def fingerprint(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def list_files(self, root: Path) -> tuple[Path, ...]:
        return tuple(path for path in root.rglob("*") if path.is_file())

    def list_directories(self, root: Path) -> tuple[Path, ...]:
        return tuple(path for path in root.rglob("*") if path.is_dir())

    def create_directory(self, target: Path) -> None:
        target.mkdir(parents=True, exist_ok=True)
```

- [ ] **Step 5.4: Implement preview action mapping**

In `PublicDriveUploadService._build_preview`:

```python
local_directories = self._gateway.list_directories(workspace.official_folder_path)
local_files = self._gateway.list_files(workspace.official_folder_path)
items: list[PublicDriveUploadItem] = []
for local_directory in local_directories:
    relative = local_directory.relative_to(workspace.official_folder_path)
    public_path = public_folder / relative
    if not public_path.exists():
        items.append(_item("directory", relative, None, public_path, "add", "ready", "Directory will be created."))
        continue
    if public_path.is_dir():
        items.append(_item("directory", relative, None, public_path, "skip", "current", "Directory already exists."))
        continue
    items.append(_item("directory", relative, None, public_path, "conflict", "conflict", "Public-drive path is a file, expected directory."))

for local_path in local_files:
    relative = local_path.relative_to(workspace.official_folder_path)
    public_path = public_folder / relative
    local_fingerprint = self._gateway.fingerprint(local_path)
    previous = self._upload_repository.get_file(project_id, relative)
    if not public_path.exists():
        items.append(_item("file", relative, local_path, public_path, "add", "ready", "Will be added."))
        continue
    if not public_path.is_file():
        items.append(_item("file", relative, local_path, public_path, "conflict", "conflict", "Public-drive path is not a file."))
        continue
    public_fingerprint = self._gateway.fingerprint(public_path)
    if public_fingerprint == local_fingerprint:
        items.append(_item("file", relative, local_path, public_path, "skip", "current", "Already current."))
        continue
    if previous is None:
        items.append(_item("file", relative, local_path, public_path, "conflict", "conflict", "Public-drive file is not managed by ConnLab."))
        continue
    if public_fingerprint != previous.public_fingerprint:
        items.append(_item("file", relative, local_path, public_path, "conflict", "conflict", "Public-drive file was changed outside ConnLab."))
        continue
    items.append(_item("file", relative, local_path, public_path, "update", "ready", "Will be updated."))
```

- [ ] **Step 5.5: Run tests and verify pass**

```powershell
py -m pytest tests\unit\test_public_drive_upload_service.py -q
```

Expected: preview action tests pass.

Public target adoption rules to implement in `_build_preview`:

- Existing DL parent folder with no planned Official project folder: create the planned Official project folder and all required child directories.
- Existing planned Official project folder that is empty: adopt it and report required directories/files as `add`.
- Existing planned Official project folder with required empty directories only: report those directories as `skip` and missing files as `add`.
- Existing public files that do not collide with planned local relative paths: add a preview warning, do not delete them, and do not mark the preview conflict.
- Existing public files or directories that collide with planned local relative paths without a matching ConnLab upload record: mark the item `conflict`.
- Wrong-type public path, file expected but directory exists or directory expected but file exists: mark the item `conflict`.

Required tests:

```python
def test_preview_adopts_empty_existing_public_official_folder(tmp_path: Path) -> None:
    official = _official_folder(tmp_path, directories=("Photos",), files={"Submitted Material/app.docx": "local"})
    public_root = _public_official_folder(tmp_path, empty=True)
    service = _service(tmp_path, workspace=_workspace(tmp_path, official), public_root=public_root)

    preview = service.preview("P1")

    assert preview.status == "ready"
    assert _item(preview.items, "Photos").action == "add"
    assert _item(preview.items, "Submitted Material/app.docx").action == "add"


def test_preview_warns_for_non_colliding_extra_public_file(tmp_path: Path) -> None:
    official = _official_folder(tmp_path, files={"Submitted Material/app.docx": "local"})
    public_root = _public_folder(tmp_path, files={"operator-note.txt": "keep"})
    service = _service(tmp_path, workspace=_workspace(tmp_path, official), public_root=public_root)

    preview = service.preview("P1")

    assert preview.status == "warning"
    assert "Public project folder contains extra unmanaged files." in preview.warnings


def test_preview_conflicts_for_unmanaged_colliding_public_file(tmp_path: Path) -> None:
    official = _official_folder(tmp_path, files={"Submitted Material/app.docx": "local"})
    public_root = _public_folder(tmp_path, files={"Submitted Material/app.docx": "human"})
    service = _service(tmp_path, workspace=_workspace(tmp_path, official), public_root=public_root)

    preview = service.preview("P1")

    assert preview.status == "conflict"
    assert _item(preview.items, "Submitted Material/app.docx").action == "conflict"
```

## Step 6 - Backend TDD: Upload State And Safe Update

Files:

- Create: `backend/infrastructure/storage/repositories/public_drive_upload.py`
- Modify: storage schema/migration owner used by current repository pattern.
- Modify: `tests/unit/test_public_drive_upload_service.py`

- [ ] **Step 6.1: Add failing managed-update tests**

```python
def test_preview_allows_update_when_public_file_matches_last_connlab_upload(
    tmp_path: Path,
) -> None:
    official = _official_folder(tmp_path, files={"Submitted Material/app.docx": "new"})
    public_root = _public_folder(tmp_path, files={"Submitted Material/app.docx": "old"})
    repository = _UploadRepository()
    repository.save_file(
        project_id="P1",
        relative_path=Path("Submitted Material/app.docx"),
        public_path=_planned_public_path(public_root, "Submitted Material/app.docx"),
        local_fingerprint=_sha_text("old"),
        public_fingerprint=_sha_text("old"),
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


def test_preview_conflicts_when_managed_public_file_was_changed_by_human(
    tmp_path: Path,
) -> None:
    official = _official_folder(tmp_path, files={"Submitted Material/app.docx": "new"})
    public_root = _public_folder(tmp_path, files={"Submitted Material/app.docx": "human"})
    repository = _UploadRepository()
    repository.save_file(
        project_id="P1",
        relative_path=Path("Submitted Material/app.docx"),
        public_path=_planned_public_path(public_root, "Submitted Material/app.docx"),
        local_fingerprint=_sha_text("old"),
        public_fingerprint=_sha_text("old"),
    )
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path, official),
        public_root=public_root,
        upload_repository=repository,
    )

    preview = service.preview("P1")

    assert preview.status == "conflict"
    assert _item(preview.items, "Submitted Material/app.docx").action == "conflict"


def test_upload_rechecks_public_fingerprint_before_update(tmp_path: Path) -> None:
    official = _official_folder(tmp_path, files={"Submitted Material/app.docx": "new"})
    public_root = _public_folder(tmp_path, files={"Submitted Material/app.docx": "old"})
    repository = _UploadRepository()
    public_path = _planned_public_path(public_root, "Submitted Material/app.docx")
    repository.save_file(
        project_id="P1",
        relative_path=Path("Submitted Material/app.docx"),
        public_path=public_path,
        local_fingerprint=_sha_text("old"),
        public_fingerprint=_sha_text("old"),
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
    assert result.conflicts or result.failed
    assert public_path.read_text(encoding="utf-8") == "human"
```

- [ ] **Step 6.2: Implement repository port and SQLite repository**

Repository record shape:

```python
@dataclass(frozen=True, slots=True)
class PublicDriveUploadFileRecord:
    project_id: str
    relative_path: Path
    public_path: Path
    local_fingerprint: str
    public_fingerprint: str
    uploaded_at: str
    operation_id: str
```

Repository methods:

```python
class PublicDriveUploadRepositoryPort(Protocol):
    def get_file(self, project_id: str, relative_path: Path) -> PublicDriveUploadFileRecord | None:
        ...

    def save_file(self, record: PublicDriveUploadFileRecord) -> None:
        ...
```

SQLite table columns:

```text
project_id TEXT NOT NULL
relative_path TEXT NOT NULL
public_path TEXT NOT NULL
local_fingerprint TEXT NOT NULL
public_fingerprint TEXT NOT NULL
uploaded_at TEXT NOT NULL
operation_id TEXT NOT NULL
PRIMARY KEY (project_id, relative_path)
```

- [ ] **Step 6.3: Run tests and verify pass**

```powershell
py -m pytest tests\unit\test_public_drive_upload_service.py -q
```

Expected: managed update and human-change conflict tests pass.

## Step 7 - Backend TDD: Upload Execution And Partial Failure

Files:

- Modify: `backend/application/public_drive_upload_service.py`
- Modify: `tests/unit/test_public_drive_upload_service.py`

- [ ] **Step 7.1: Add failing upload tests**

```python
def test_upload_copies_add_items_and_next_preview_is_current(tmp_path: Path) -> None:
    official = _official_folder(tmp_path, files={"Submitted Material/app.docx": "local"})
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
    assert len(result.copied) == 1
    assert _planned_public_path(public_root, "Submitted Material/app.docx").read_text(encoding="utf-8") == "local"
    assert result.preview.status == "current"


def test_upload_refuses_conflict_preview(tmp_path: Path) -> None:
    official = _official_folder(tmp_path, files={"Submitted Material/app.docx": "local"})
    public_root = _public_folder(tmp_path, files={"Submitted Material/app.docx": "human"})
    service = _service(tmp_path, workspace=_workspace(tmp_path, official), public_root=public_root)

    with pytest.raises(PublicDriveUploadConflictError):
        service.upload("P1")


def test_upload_returns_partial_when_later_copy_fails(tmp_path: Path) -> None:
    official = _official_folder(
        tmp_path,
        files={
            "Submitted Material/a.docx": "a",
            "Submitted Material/b.docx": "b",
        },
    )
    public_root = tmp_path / "public"
    public_root.mkdir()
    gateway = _FailingAfterFirstCopyGateway()
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path, official),
        public_root=public_root,
        gateway=gateway,
    )

    result = service.upload("P1")

    assert result.upload_status == "partial"
    assert len(result.copied) == 1
    assert result.failed
    assert result.preview.status in {"ready", "warning", "conflict"}
```

- [ ] **Step 7.2: Implement upload**

Algorithm:

```python
def upload(self, project_id: str) -> PublicDriveUploadResult:
    preview = self.preview(project_id)
    if preview.status == "blocked":
        raise PublicDriveUploadBlockedError(_first_blocker(preview))
    if preview.status == "conflict":
        raise PublicDriveUploadConflictError("Resolve public-drive conflicts before upload.")

    operation_id = uuid.uuid4().hex
    copied: list[PublicDriveUploadItem] = []
    updated: list[PublicDriveUploadItem] = []
    skipped = [item for item in preview.items if item.action == "skip"]
    failed: list[PublicDriveUploadItem] = []

    for item in preview.items:
        if item.kind == "directory" and item.action == "add":
            try:
                self._gateway.create_directory(item.public_path)
                copied.append(item)
            except OSError as exc:
                failed.append(_failed_item(item, str(exc)))
                after = self.preview(project_id)
                return _partial_result(project_id, copied, updated, skipped, failed, str(exc), after)
            continue
        if item.kind != "file" or item.action not in {"add", "update"}:
            continue
        try:
            if item.action == "add":
                self._gateway.copy_new_file(item.local_path, item.public_path)
            else:
                previous = self._upload_repository.get_file(project_id, item.relative_path)
                expected_public_fingerprint = previous.public_fingerprint if previous else None
                self._gateway.replace_managed_file(
                    item.local_path,
                    item.public_path,
                    expected_public_fingerprint=expected_public_fingerprint,
                )
        except OSError as exc:
            failed.append(_failed_item(item, str(exc)))
            after = self.preview(project_id)
            return PublicDriveUploadResult(
                project_id=project_id,
                upload_status="partial",
                copied=tuple(copied),
                updated=tuple(updated),
                skipped=tuple(skipped),
                conflicts=tuple(i for i in after.items if i.action == "conflict"),
                failed=tuple(failed),
                errors=(str(exc),),
                preview=after,
            )
        record = self._record_uploaded_file(project_id, item, operation_id)
        self._upload_repository.save_file(record)
        if item.action == "add":
            copied.append(item)
        else:
            updated.append(item)

    after = self.preview(project_id)
    return PublicDriveUploadResult(
        project_id=project_id,
        upload_status="completed",
        copied=tuple(copied),
        updated=tuple(updated),
        skipped=tuple(skipped),
        conflicts=tuple(),
        failed=tuple(),
        errors=tuple(),
        preview=after,
    )
```

- [ ] **Step 7.3: Run tests and verify pass**

```powershell
py -m pytest tests\unit\test_public_drive_upload_service.py -q
```

Expected: upload execution tests pass.

Gateway write rules:

```python
class PublicDriveUploadGateway:
    def copy_new_file(self, source: Path, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise PublicDriveUploadTargetChangedError(f"Target appeared before copy: {target}")
        self._atomic_copy(source, target)

    def replace_managed_file(
        self,
        source: Path,
        target: Path,
        *,
        expected_public_fingerprint: str | None,
    ) -> None:
        if expected_public_fingerprint is None:
            raise PublicDriveUploadTargetChangedError("Missing previous upload record for update.")
        if not target.is_file():
            raise PublicDriveUploadTargetChangedError(f"Target is no longer a file: {target}")
        current = self.fingerprint(target)
        if current != expected_public_fingerprint:
            raise PublicDriveUploadTargetChangedError(f"Public-drive file changed before update: {target}")
        self._atomic_copy(source, target)

    def _atomic_copy(self, source: Path, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(f".{target.name}.connlab-{uuid.uuid4().hex}.tmp")
        try:
            shutil.copy2(source, temporary)
            os.replace(temporary, target)
        finally:
            if temporary.exists():
                temporary.unlink()
```

The upload repository must be updated only after `_atomic_copy` succeeds and the public target fingerprint matches the local source fingerprint.

## Step 8 - API Contract

Files:

- Create: `backend/api/routes_public_drive_upload.py`
- Modify: `backend/api/dependencies.py`
- Modify: `backend/api/main.py`
- Create: `tests/integration/test_public_drive_upload_api.py`

- [ ] **Step 8.1: Add failing API tests**

```python
def test_public_drive_preview_api_blocks_without_public_location(client) -> None:
    response = client.get("/api/projects/P1/public-drive/preview")

    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == "P1"
    assert data["status"] == "blocked"
    assert "Public Project locations is not configured." in data["blockers"]


def test_public_drive_preview_api_reports_file_and_directory_add_items(client, tmp_path: Path) -> None:
    _seed_project_with_official_folder(
        client,
        tmp_path,
        directories=("Photos", "Test results/Final Examination"),
        files={"Submitted Material/app.docx": "local"},
        public_root=tmp_path / "public",
    )

    response = client.get("/api/projects/P1/public-drive/preview")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert _api_item(data, "Photos")["kind"] == "directory"
    assert _api_item(data, "Photos")["action"] == "add"
    assert _api_item(data, "Submitted Material/app.docx")["kind"] == "file"
    assert _api_item(data, "Submitted Material/app.docx")["action"] == "add"


def test_public_drive_preview_api_reports_conflict_for_unmanaged_public_file(client, tmp_path: Path) -> None:
    _seed_project_with_official_folder(
        client,
        tmp_path,
        files={"Submitted Material/app.docx": "local"},
        public_files={"Submitted Material/app.docx": "human"},
        public_root=tmp_path / "public",
    )

    response = client.get("/api/projects/P1/public-drive/preview")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "conflict"
    assert _api_item(data, "Submitted Material/app.docx")["action"] == "conflict"


def test_public_drive_upload_api_returns_current_preview_after_copy(client, tmp_path: Path) -> None:
    _seed_project_with_official_folder(
        client,
        tmp_path,
        directories=("Photos",),
        files={"Submitted Material/app.docx": "local"},
        public_root=tmp_path / "public",
    )

    response = client.post("/api/projects/P1/public-drive/upload")

    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == "P1"
    assert data["upload_status"] == "completed"
    assert data["preview"]["status"] == "current"
```

- [ ] **Step 8.2: Add route DTOs**

Route module response models:

```python
class PublicDriveUploadItemResponse(BaseModel):
    kind: str
    relative_path: str
    local_path: str | None
    public_path: str
    action: str
    status: str
    message: str


class PublicDriveUploadPreviewResponse(BaseModel):
    project_id: str
    status: str
    local_official_folder_path: str | None
    public_project_folder_path: str | None
    items: list[PublicDriveUploadItemResponse]
    blockers: list[str]
    warnings: list[str]
    counts: dict[str, int]
    next_action: str
```

- [ ] **Step 8.3: Wire routes**

```python
router = APIRouter(prefix="/api/projects/{project_id}/public-drive", tags=["public-drive"])


@router.get("/preview", response_model=PublicDriveUploadPreviewResponse)
def preview_public_drive_upload(
    project_id: str,
    service: PublicDriveUploadService = Depends(get_public_drive_upload_service),
) -> PublicDriveUploadPreviewResponse:
    return _preview_response(service.preview(project_id))


@router.post("/upload", response_model=PublicDriveUploadResultResponse)
def upload_public_drive(
    project_id: str,
    service: PublicDriveUploadService = Depends(get_public_drive_upload_service),
) -> PublicDriveUploadResultResponse:
    try:
        return _result_response(service.upload(project_id))
    except PublicDriveUploadConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
```

- [ ] **Step 8.4: Run API tests**

```powershell
py -m pytest tests\integration\test_public_drive_upload_api.py -q
```

Expected: API tests pass.

## Step 9 - Frontend API And Workbench Integration

Files:

- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- Modify: `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
- Modify: `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- Modify: `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`

- [ ] **Step 9.1: Add failing selector tests**

```typescript
it("shows upload to public drive when public-drive preview is ready", () => {
  const lifecycle = deriveProjectWorkbenchLifecycle({
    hasLtr: true,
    hasActiveMatrix: true,
    folderReady: true,
    requestMaterialStatus: "collected",
    officialFolderCheckStatus: "ready",
    publicDrivePreviewStatus: "ready",
    publicDrivePreviewBlockers: [],
    publicDrivePreviewWarnings: [],
  });

  expect(lifecycle.nextAction.kind).toBe("public_drive_upload");
  expect(lifecycle.nextAction.label).toBe("Upload to public drive");
});

it("blocks upload when public-drive preview has conflicts", () => {
  const lifecycle = deriveProjectWorkbenchLifecycle({
    hasLtr: true,
    hasActiveMatrix: true,
    folderReady: true,
    requestMaterialStatus: "collected",
    officialFolderCheckStatus: "ready",
    publicDrivePreviewStatus: "conflict",
    publicDrivePreviewBlockers: ["Resolve public-drive conflicts before upload."],
    publicDrivePreviewWarnings: [],
  });

  expect(lifecycle.nextAction.kind).toBe("none");
  expect(lifecycle.stageStatus).toBe("blocked");
});
```

- [ ] **Step 9.2: Add client types and functions**

In `frontend/src/api/client.ts`:

```typescript
export type PublicDriveUploadPreview = {
  project_id: string;
  status: "blocked" | "ready" | "current" | "conflict" | "warning";
  local_official_folder_path?: string | null;
  public_project_folder_path?: string | null;
  items: PublicDriveUploadItem[];
  blockers: string[];
  warnings: string[];
  counts: Record<string, number>;
  next_action: "preview" | "upload" | "none";
};

export type PublicDriveUploadItem = {
  kind: "file" | "directory";
  relative_path: string;
  local_path?: string | null;
  public_path: string;
  action: "add" | "update" | "skip" | "conflict" | "deferred";
  status: "ready" | "current" | "conflict" | "deferred" | "failed";
  message: string;
};

export async function fetchPublicDriveUploadPreview(
  projectId: string
): Promise<PublicDriveUploadPreview> {
  return requestJson(`/api/projects/${projectId}/public-drive/preview`);
}

export async function uploadPublicDriveProjectFolder(
  projectId: string
): Promise<PublicDriveUploadResult> {
  return requestJson(`/api/projects/${projectId}/public-drive/upload`, {
    method: "POST",
  });
}
```

- [ ] **Step 9.3: Wire Workbench model**

Add model state:

```typescript
const [publicDrivePreview, setPublicDrivePreview] = useState<PublicDriveUploadPreview | null>(null);
const [publicDriveError, setPublicDriveError] = useState<string | null>(null);
const [publicDriveUploading, setPublicDriveUploading] = useState(false);
```

Add actions:

```typescript
const refreshPublicDrivePreview = useCallback(async () => {
  setPublicDriveError(null);
  try {
    setPublicDrivePreview(await fetchPublicDriveUploadPreview(projectId));
  } catch (error) {
    setPublicDriveError(error instanceof Error ? error.message : "Public-drive preview failed.");
  }
}, [projectId]);

const uploadPublicDrive = useCallback(async () => {
  setPublicDriveUploading(true);
  setPublicDriveError(null);
  try {
    const result = await uploadPublicDriveProjectFolder(projectId);
    setPublicDrivePreview(result.preview);
  } catch (error) {
    setPublicDriveError(error instanceof Error ? error.message : "Public-drive upload failed.");
  } finally {
    setPublicDriveUploading(false);
  }
}, [projectId]);
```

- [ ] **Step 9.4: Add Project Folder row**

`ProjectWorkbenchLayout.tsx` should add:

```typescript
{
  title: "Public drive upload",
  value: formatPublicDriveUploadStatus(publicDrivePreview?.status ?? null),
  status: normalizePublicDriveUploadStatus(publicDrivePreview?.status ?? null),
}
```

Use copy:

- `Not configured`
- `Ready to upload`
- `Already current`
- `Conflict`
- `Blocked`
- `Warning`

- [ ] **Step 9.5: Run frontend tests**

```powershell
cd frontend; npm test -- --run ProjectWorkbench publicDrive --watch=false
```

Expected: Workbench tests pass.

## Step 10 - Static Guards

Files:

- Modify: `tests/unit/test_frontend_shell_files.py`

- [ ] **Step 10.1: Add guard**

```python
def test_task319_public_drive_upload_boundaries_are_wired() -> None:
    feature_root = FRONTEND_ROOT / "src" / "features" / "project-workbench"
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(encoding="utf-8")
    layout_source = (feature_root / "ProjectWorkbenchLayout.tsx").read_text(encoding="utf-8")
    selector_source = (feature_root / "projectWorkbenchLifecycleSelectors.ts").read_text(encoding="utf-8")
    route_source = (
        FRONTEND_ROOT.parent / "backend" / "api" / "routes_public_drive_upload.py"
    ).read_text(encoding="utf-8")

    assert "fetchPublicDriveUploadPreview" in client_source
    assert "uploadPublicDriveProjectFolder" in client_source
    assert "Public drive upload" in layout_source
    assert "Upload to public drive" in selector_source
    assert "delete" not in route_source.lower()
    assert "ProjectPackagePreviewService" not in route_source
```

- [ ] **Step 10.2: Run guard**

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "project_workbench or public_drive or task319"
```

Expected: static guard passes.

## Step 11 - Full Validation

- [ ] **Step 11.1: Backend**

```powershell
py -m pytest tests\unit\test_public_drive_upload_service.py -q
py -m pytest tests\integration\test_public_drive_upload_api.py -q
py -m pytest tests\unit\test_official_project_folder_check_service.py tests\unit\test_project_request_material_collection_service.py -q
```

Expected: all selected backend tests pass.

- [ ] **Step 11.2: Frontend**

```powershell
cd frontend; npm test -- --run ProjectWorkbench publicDrive --watch=false
cd frontend; npm run build
```

Expected: Vitest and build pass.

- [ ] **Step 11.3: Static and diff**

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "project_workbench or public_drive or task319"
git diff --check
```

Expected: static tests pass. `git diff --check` has no whitespace errors; CRLF warnings are acceptable on this Windows repository.

## Step 12 - Browser Smoke

After implementation approval and code completion:

- [ ] Open a project with completed local Official project folder and valid `Public Project locations`.
- [ ] Confirm Project Folder shows `Public drive upload`.
- [ ] Confirm a clean public target shows `Upload to public drive`.
- [ ] Run upload.
- [ ] Refresh and confirm `Already current`.
- [ ] Manually edit one public-drive file.
- [ ] Refresh and confirm `Conflict` with no overwrite button.

## Step 13 - Task Board Update

After implementation and validation only, update `docs/task_board.md`:

- mark TASK_319 complete;
- include validation commands and results;
- state that TASK_320 requires separate approval;
- state any browser smoke limitation.

Do not mark TASK_319 complete during planning review.

## Self-Review

Spec coverage:

- Preview-first behavior is covered in Steps 4-5.
- TASK_318 local folder check gating is covered in Step 4.
- Required empty directory upload is covered in Step 5.
- Safe update, write-before-copy recheck, and human-change conflict detection are covered in Step 6.
- Upload and partial failure behavior are covered in Step 7.
- Concrete API fixture scenarios are covered in Step 8.
- Frontend wiring is covered in Steps 9-10.
- Validation and manual smoke are covered in Steps 11-12.

Placeholder scan:

- No implementation step depends on an undefined future feature.
- No public-drive delete, merge, or conflict resolution is planned.

Type consistency:

- Preview, item, result, and repository names are consistent across backend, API, and frontend tasks.

## Execution Handoff

Plan executed and saved to `docs/task_319_public_drive_upload_update_preview_plan.md`.

TASK_319 implementation is complete after validation. Do not enter TASK_320 or resume TASK_313 without separate approval.
