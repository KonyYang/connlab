# TASK_317 Source Book And Request Material Collection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Collect already-registered request email and attachment assets into the local Project Folder structure, with Source Book originals, Official project folder controlled copies, and a minimal `Project Folder | Execution` Workbench surface.

**Architecture:** Backend owns source classification, preview, conflict detection, copy execution, and persistence. Frontend consumes typed preview/collect APIs and renders one Project Folder task flow without direct file operations. File copying stays behind application/infrastructure boundaries and never deletes source files.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy 2.x, Pydantic v2, React, TypeScript, Vitest, pytest.

---

Status: Implemented. TASK_317 scope is complete.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_317_SOURCE_BOOK_AND_REQUEST_MATERIAL_COLLECTION`, implementation complete.

Task file:

- `tasks/TASK_317_SOURCE_BOOK_AND_REQUEST_MATERIAL_COLLECTION.md`

Predecessors:

- `TASK_316_LOCAL_PROJECT_WORKSPACE_CREATION_FROM_TEMPLATE`, complete.
- `TASK_317A_PROJECT_FOLDER_PREPARATION_UI_BLUEPRINT`, accepted as planning prerequisite.

## Required Preconditions Before Coding

Implementation worker must read:

1. `AGENTS.md`
2. `docs/task_board.md`
3. `tasks/TASK_317_SOURCE_BOOK_AND_REQUEST_MATERIAL_COLLECTION.md`
4. `tasks/TASK_317A_PROJECT_FOLDER_PREPARATION_UI_BLUEPRINT.md`
5. `docs/task_317a_project_folder_preparation_ui_blueprint_plan.md`
6. `docs/project_management/TASK_EXECUTION_SKILL.md`
7. `docs/project_management/TASK_REVIEW_CHECKLIST.md`
8. `docs/02_ARCHITECTURE_RULES.md`
9. `docs/frontend_architecture_rules.md`

Because TASK_317 changes Workbench UI and UX copy, implementation must load `$impeccable` product context before UI work.

No code may be written until the user explicitly approves this plan for implementation.

## Step 1 - Task Understanding

Goal:

- Preview and collect project request material from existing project `FileAsset` records into the completed local project folder structure.

Inputs:

- project id
- completed TASK_316 official workspace record
- project `FileAsset` records
- project file provenance/source roles for newly confirmed projects, with conservative fallback for older rows
- real source file paths
- real target folders under `Source Book`, `E-mail`, and `Submitted Material`

Outputs:

- request-material preview response
- request-material collect response
- copied request email and attachments
- SQLite collection/index records
- Workbench `Project Folder` row state and one primary action

Involved modules:

- backend domain records/enums for request-material collection
- backend application service for preview/collect
- backend infrastructure repository and safe copy helper
- backend API route and dependency wiring
- frontend API client
- frontend Project Workbench model/selectors/components
- backend pytest, integration API tests, Vitest/static shell checks

Not allowed:

- no new Outlook connection
- no new email import
- no direct project drag/drop upload
- no public-drive upload
- no Test Record, Fee form, Customer Feedback, or Section 2 generation/write-back
- no StepInstance, evidence/photo execution workflow, report, AI, permissions, LAN, or multi-user work
- no destructive source move/delete
- no public-drive upload button

## Step 2 - Proposed Design

### Backend Data Model

Add provenance support and collection records to SQLite. Keep records small and queryable.

First, extend project file provenance so new project confirmations do not lose the original intake role:

- `FileAsset` / `FileAssetModel` should gain nullable fields for `source_package_id`, `source_intake_asset_id`, `source_role`, and `sha256` where compatible with the current repository style.
- `IntakeConfirmationService` should populate these fields from `IntakePackage` and `IntakeAsset` records.
- When confirmation would create duplicate project file assets pointing to the same physical source, it should dedupe by canonical path and hash where available, preserving the highest-confidence source role.
- Historical `FileAsset` rows without provenance must remain readable. TASK_317 preview handles them with conservative fallback rules.

Recommended model additions in `backend/infrastructure/storage/models.py`:

```python
class ProjectRequestMaterialCollectionModel(Base):
    """Database row for one project request-material collection run."""

    __tablename__ = "project_request_material_collections"

    collection_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False, index=True)
    workspace_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    item_count: Mapped[int] = mapped_column(Integer, nullable=False)
    copied_count: Mapped[int] = mapped_column(Integer, nullable=False)
    already_present_count: Mapped[int] = mapped_column(Integer, nullable=False)
    conflict_count: Mapped[int] = mapped_column(Integer, nullable=False)
    skipped_count: Mapped[int] = mapped_column(Integer, nullable=False)
    missing_source_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(64), nullable=False)
    warnings_json: Mapped[str | None] = mapped_column(Text)


class ProjectRequestMaterialCollectionItemModel(Base):
    """Database row for one request-material target copy item."""

    __tablename__ = "project_request_material_collection_items"

    item_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    collection_id: Mapped[str] = mapped_column(
        ForeignKey("project_request_material_collections.collection_id"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False, index=True)
    source_asset_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_asset_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_role: Mapped[str | None] = mapped_column(String(64))
    dedupe_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    original_name: Mapped[str | None] = mapped_column(String(255))
    target_area: Mapped[str] = mapped_column(String(64), nullable=False)
    target_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    review_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    size_bytes: Mapped[int | None] = mapped_column(Integer)
    sha256: Mapped[str | None] = mapped_column(String(64))
```

Recommended domain/application dataclasses in new file `backend/application/project_request_material_collection_service.py`:

```python
@dataclass(frozen=True, slots=True)
class RequestMaterialPreviewItem:
    """One planned request-material copy target."""

    source_asset_id: str
    source_asset_type: str
    source_role: str | None
    source_name: str
    source_path: Path
    dedupe_key: str
    target_area: str
    target_path: Path
    action: str
    status: str
    message: str
    review_required: bool = False
    size_bytes: int | None = None
    sha256: str | None = None


@dataclass(frozen=True, slots=True)
class RequestMaterialPreview:
    """Preview of request-material collection for a project."""

    project_id: str
    local_workspace_path: Path | None
    source_book_path: Path | None
    official_project_folder_path: Path | None
    status: str
    items: tuple[RequestMaterialPreviewItem, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RequestMaterialCollectResult:
    """Result of collecting request material into the Project Folder."""

    project_id: str
    collection_id: str
    status: str
    items: tuple[RequestMaterialPreviewItem, ...]
    copied_paths: tuple[Path, ...]
    already_present_paths: tuple[Path, ...]
    skipped_paths: tuple[Path, ...]
    missing_source_paths: tuple[Path, ...]
    conflict_paths: tuple[Path, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
```

Status vocabulary:

- preview status: `blocked`, `ready`, `collected`, `partial`, `conflict`
- item status: `planned`, `already_present`, `copied`, `missing_source`, `conflict`, `skipped`, `needs_review`
- action: `copy`, `already_present`, `block`, `skip`, `review`
- target area: `source_book_email`, `source_book_application_form`, `source_book_attachment`, `official_email`, `submitted_material`

### Source Classification

Use project `FileAsset` records as the normal source. Do not add a new email import workflow in TASK_317.

Rules:

- `FileAssetType.APPLICATION_FORM` is the selected Application Form source.
- New `FileAsset` rows should preserve original intake source role where available.
- Preview must dedupe source candidates by canonical path and hash before role classification.
- If duplicate rows point to the same source file, preview shows one candidate and chooses the highest-confidence role.
- Role priority for duplicates: selected application form, request email, confirmed request attachment, needs-review candidate, ignored/skipped.
- A source role of `email_source`, or a unique `.msg` fallback candidate, is the request email.
- If no request email candidate exists, preview may return `partial`; collect may copy the selected Application Form and confirmed request attachments while explicitly returning `Request email missing`.
- If multiple different `.msg` candidates remain after dedupe, preview status is `blocked` with `Multiple request email candidates need review`; collect must not run.
- `FileAssetType.ATTACHMENT` rows with known request-attachment roles are request attachments.
- `FileAssetType.ATTACHMENT` rows with unknown, ignored, inline-image, application-form-candidate, or ambiguous roles are needs-review candidates. They may be preserved in Source Book but must not be placed in `Submitted Material` in TASK_317.
- Missing selected Application Form is a blocker because it is required request material.

### Target Planning

Build target items from the completed official workspace record:

```text
Source Book/Request Material/E-mail/{safe name}
Source Book/Request Material/Application Form/{safe name}
Source Book/Request Material/Attachments/{safe name}
Official project folder/E-mail/{safe name}
Official project folder/Submitted Material/{safe name}
```

Target planning rules:

- Request email: Source Book E-mail and Official project folder E-mail.
- Selected Application Form: Source Book Application Form and Official project folder Submitted Material.
- Confirmed request attachment: Source Book Attachments and Official project folder Submitted Material.
- Needs-review attachment candidate: Source Book Attachments only; Submitted Material placement is skipped with an explicit item message.
- Ignored/inline-image candidates: skipped unless the source role is later approved by a separate task.

Recommended helper functions inside the service or a small helper module:

```python
def safe_material_filename(original_name: str | None, fallback: str, source_asset_id: str) -> str:
    """Return a Windows-safe file name for request material targets."""


def dedupe_target_names(items: Sequence[PlannedTarget]) -> tuple[PlannedTarget, ...]:
    """Append a stable source id suffix when multiple targets share a name."""
```

Target conflict rules:

- Missing source path: item status `missing_source`, preview status at least `partial`, collect skips that item unless it is the selected Application Form.
- Target absent: item action `copy`.
- Target exists and same content: item action `already_present`.
- Target exists and different content: item status `conflict`, preview status `conflict`, collect blocks.
- Duplicate planned target after safe-name normalization: add stable suffix using `source_asset_id[:8]`.

### File Copy Gateway

Add a focused infrastructure helper rather than calling `shutil` directly throughout the service.

Recommended file:

- `backend/infrastructure/files/request_material_copy_gateway.py`

Recommended API:

```python
class RequestMaterialCopyGateway:
    """Copy request material through a ConnLab-owned staging directory."""

    def copy_items(
        self,
        *,
        items: Sequence[RequestMaterialPreviewItem],
        staging_root: Path,
    ) -> tuple[Path, ...]:
        """Copy planned items without overwriting existing target files."""
```

Rules:

- Use `{Local DL folder}/.connlab/tmp/request-material-{uuid}` as staging root.
- Copy each source file into staging first.
- Create final target parent directories.
- Move staged files to final target paths only if the final target still does not exist.
- If an item is already present, do not copy it.
- Clean only the operation staging directory.
- Do not delete or modify source files.

### API Route

Recommended new route file:

- `backend/api/routes_project_request_material.py`

Route shape:

```text
GET  /api/projects/{project_id}/request-material/preview
POST /api/projects/{project_id}/request-material/collect
```

Recommended response models:

```python
class RequestMaterialPreviewItemResponse(BaseModel):
    source_asset_id: str
    source_asset_type: str
    source_role: str | None = None
    source_name: str
    source_path: str
    dedupe_key: str
    target_area: str
    target_path: str
    action: str
    status: str
    message: str
    review_required: bool = False
    size_bytes: int | None = None
    sha256: str | None = None


class RequestMaterialPreviewResponse(BaseModel):
    project_id: str
    local_workspace_path: str | None
    source_book_path: str | None
    official_project_folder_path: str | None
    status: str
    items: list[RequestMaterialPreviewItemResponse]
    blockers: list[str]
    warnings: list[str]


class RequestMaterialCollectResponse(RequestMaterialPreviewResponse):
    collection_id: str
    copied_paths: list[str]
    already_present_paths: list[str]
    skipped_paths: list[str]
    missing_source_paths: list[str]
    conflict_paths: list[str]
```

Dependency wiring:

- Modify `backend/api/dependencies.py`
- Modify `backend/api/main.py`

The route must map:

- missing project/workspace to 404 or 409 with business-readable detail
- conflicts to 409
- invalid input/state to 400
- partial collection with skipped/missing non-required items to 200 with explicit `skipped_paths`, `missing_source_paths`, `blockers`, and `warnings`

### Repository

Recommended new file:

- `backend/infrastructure/storage/repositories/request_material_collection.py`

Repository API:

```python
class ProjectRequestMaterialCollectionRepository:
    """Persist request-material collection records."""

    def save_collection(
        self,
        collection: ProjectRequestMaterialCollectionRecord,
        items: tuple[ProjectRequestMaterialCollectionItemRecord, ...],
    ) -> ProjectRequestMaterialCollectionRecord:
        """Persist a collection run and item rows."""

    def latest_by_project(self, project_id: str) -> ProjectRequestMaterialCollectionRecord | None:
        """Return the latest collection run for a project."""

    def list_items(self, collection_id: str) -> tuple[ProjectRequestMaterialCollectionItemRecord, ...]:
        """Return items for a collection run."""
```

Add repository export in:

- `backend/infrastructure/storage/repositories/__init__.py`

### Frontend API Client

Modify `frontend/src/api/client.ts`.

Add types:

```ts
export type RequestMaterialItemStatus =
  | "planned"
  | "already_present"
  | "copied"
  | "missing_source"
  | "conflict"
  | "skipped"
  | "needs_review";

export type RequestMaterialPreviewStatus =
  | "blocked"
  | "ready"
  | "collected"
  | "partial"
  | "conflict";

export type RequestMaterialPreviewItem = {
  source_asset_id: string;
  source_asset_type: string;
  source_role?: string | null;
  source_name: string;
  source_path: string;
  dedupe_key: string;
  target_area: string;
  target_path: string;
  action: string;
  status: RequestMaterialItemStatus;
  message: string;
  review_required: boolean;
  size_bytes?: number | null;
  sha256?: string | null;
};

export type RequestMaterialPreview = {
  project_id: string;
  local_workspace_path?: string | null;
  source_book_path?: string | null;
  official_project_folder_path?: string | null;
  status: RequestMaterialPreviewStatus;
  items: RequestMaterialPreviewItem[];
  blockers: string[];
  warnings: string[];
};

export type RequestMaterialCollectResponse = RequestMaterialPreview & {
  collection_id: string;
  copied_paths: string[];
  already_present_paths: string[];
  skipped_paths: string[];
  missing_source_paths: string[];
  conflict_paths: string[];
};
```

Add functions near official workspace APIs:

```ts
export function fetchRequestMaterialPreview(projectId: string): Promise<RequestMaterialPreview> {
  return requestJson<RequestMaterialPreview>(
    `/api/projects/${encodeURIComponent(projectId)}/request-material/preview`,
    { cache: "no-store" }
  );
}

export function collectRequestMaterial(projectId: string): Promise<RequestMaterialCollectResponse> {
  return requestJson<RequestMaterialCollectResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/request-material/collect`,
    { method: "POST" }
  );
}
```

### Frontend Workbench Model

Modify `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`.

Add model state:

```ts
requestMaterialPreview: RequestMaterialPreview | null;
requestMaterialLoading: boolean;
requestMaterialCollecting: boolean;
requestMaterialError: string | null;
onRefreshRequestMaterial: () => Promise<void>;
onCollectRequestMaterial: () => Promise<void>;
```

Load preview after official workspace preview and after collection. Do not run collection automatically.

### Frontend Project Folder UI

Create or refactor toward focused files instead of growing `ProjectWorkbenchLayout.tsx`:

- Create `frontend/src/features/project-workbench/ProjectFolderPreparationPanel.tsx`
- Create `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- Create `frontend/src/features/project-workbench/RequestMaterialCollectionPanel.tsx`
- Create `frontend/src/features/project-workbench/projectFolderPreparationSelectors.ts`

Expected behavior:

- Active Matrix Workbench tabs show `Project Folder | Execution`.
- No `Overview` tab in active-Matrix Project Folder flow.
- Existing internal `package_preparation` mode may remain temporarily, but the user-facing label and copy must be `Project Folder`.
- Top banner uses one next action. If request material is the first blocker, show `Collect request material`.
- Request-material controls live only in the `Request material` row/detail panel.
- Public-drive upload row is hidden or read-only with no enabled button.
- Existing Matrix/Step UI remains only in `Execution`.

Recommended display rows for TASK_317:

```text
Local project folder        Created / Needs repair / Missing
Request material            Missing / Partial / Collected / Conflict
Confirmed Fee authority     Missing / Confirmed / Stale
Required forms              Not started / Blocked by authority / Ready later
Application Form Section 2  Not updated / Preview later / Synced
Submitted Material          Pending TASK_318 check
```

Do not show `Package`, `Project package`, `Workspace`, `.connlab`, `manifest`, `SQLite`, or task ids in user-facing copy.

When request email is missing but partial collection is allowed, the row must state `Request email missing` and the primary action copy should make clear that ConnLab will collect the available request material only. When multiple email candidates exist, the row must be blocked with `Multiple request email candidates need review`.

## Implementation Tasks

### Task 1: FileAsset Provenance And Dedupe Baseline

**Files:**

- Modify: `backend/infrastructure/storage/models.py`
- Modify: `backend/domain/models.py`
- Modify: `backend/infrastructure/storage/repositories/records.py`
- Modify: `backend/application/intake_confirmation_service.py`
- Test: `tests/unit/test_intake_confirmation_service.py`
- Test: `tests/integration/test_intake_package_repositories.py`

- [ ] Add nullable `source_package_id`, `source_intake_asset_id`, `source_role`, and `sha256` fields to the project `FileAsset` domain/model/repository mapping where compatible with existing tests.
- [ ] Populate selected Application Form assets with source role `selected_application_form`.
- [ ] Populate imported request email/package source assets with source role `email_source`.
- [ ] Populate other intake assets with their original intake asset role.
- [ ] Deduplicate FileAsset creation by canonical path and hash during confirmation so the same `.msg` source is not registered twice for new confirmations.
- [ ] Keep historical FileAsset rows with missing provenance readable.

Run:

```powershell
py -m pytest tests\unit\test_intake_confirmation_service.py tests\integration\test_intake_package_repositories.py -q
```

Expected:

```text
passed
```

### Task 2: Request Material Collection Repository

**Files:**

- Modify: `backend/infrastructure/storage/models.py`
- Create: `backend/infrastructure/storage/repositories/request_material_collection.py`
- Modify: `backend/infrastructure/storage/repositories/__init__.py`
- Test: `tests/unit/test_project_request_material_collection_repository.py`

- [ ] Add SQLAlchemy models for collection summary and item rows.
- [ ] Add repository dataclasses or reuse application dataclasses if kept layer-safe.
- [ ] Implement save/latest/list item operations.
- [ ] Add unit tests for saving a collection with items and reading latest by project.

Run:

```powershell
py -m pytest tests\unit\test_project_request_material_collection_repository.py -q
```

Expected:

```text
passed
```

### Task 3: Backend Preview Service

**Files:**

- Create: `backend/application/project_request_material_collection_service.py`
- Test: `tests/unit/test_project_request_material_collection_service.py`

- [ ] Define preview/result dataclasses.
- [ ] Add repository ports for Project, OfficialWorkspace, FileAsset, and collection records.
- [ ] Implement `preview(project_id)`.
- [ ] Deduplicate source candidates by canonical path and hash before classification.
- [ ] Classify source assets deterministically using source roles first and conservative fallback second.
- [ ] Build Source Book and Official project folder target items.
- [ ] Compute file size/hash for existing sources and targets.
- [ ] Return `blocked` when completed official workspace is missing.
- [ ] Return `blocked` when multiple different request email candidates remain after dedupe.
- [ ] Return `partial` when request email is missing but other request material exists.
- [ ] Mark unknown or ambiguous attachment candidates as `needs_review` and plan Source Book only.
- [ ] Return `conflict` when target exists with different content.
- [ ] Return `collected` when every required item is already present.

Run:

```powershell
py -m pytest tests\unit\test_project_request_material_collection_service.py -q
```

Expected:

```text
passed
```

### Task 4: Safe Copy Execution

**Files:**

- Create: `backend/infrastructure/files/request_material_copy_gateway.py`
- Modify: `backend/application/project_request_material_collection_service.py`
- Test: `tests/unit/test_project_request_material_collection_service.py`

- [ ] Implement staged copy under `{Local DL folder}/.connlab/tmp/request-material-{uuid}`.
- [ ] Re-run preview inside `collect(project_id)`.
- [ ] Block collect when preview has conflicts, multiple request email candidates, or missing selected Application Form.
- [ ] Allow partial collect when request email is missing but selected Application Form exists; return skipped/missing request email state.
- [ ] Copy planned files without overwriting.
- [ ] Preserve needs-review attachment candidates in Source Book only and return skipped Submitted Material placement.
- [ ] Persist collection summary and item records after copy attempt.
- [ ] Return copied, already-present, skipped, missing-source, conflict paths, blockers, and warnings.
- [ ] Confirm source files remain in place.

Run:

```powershell
py -m pytest tests\unit\test_project_request_material_collection_service.py -q
```

Expected:

```text
passed
```

### Task 5: API Routes And Dependency Wiring

**Files:**

- Create: `backend/api/routes_project_request_material.py`
- Modify: `backend/api/dependencies.py`
- Modify: `backend/api/main.py`
- Test: `tests/integration/test_project_request_material_collection_api.py`

- [ ] Add Pydantic response DTOs.
- [ ] Add `GET /api/projects/{project_id}/request-material/preview`.
- [ ] Add `POST /api/projects/{project_id}/request-material/collect`.
- [ ] Wire service dependencies using existing repositories.
- [ ] Return 409 for conflicts and blocked collection state.
- [ ] Return 200 for partial collection when only non-required request email or needs-review candidates are skipped.
- [ ] Add integration tests for preview and collect using temporary files.

Run:

```powershell
py -m pytest tests\integration\test_project_request_material_collection_api.py -q
```

Expected:

```text
passed
```

### Task 6: Frontend API Client And Model

**Files:**

- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- Test: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`

- [ ] Add request-material DTO types.
- [ ] Add preview/collect API functions.
- [ ] Add Workbench model state and refresh/collect handlers.
- [ ] Refresh request-material preview after official workspace preview and after collection.
- [ ] Keep errors local to request-material state.
- [ ] Surface skipped, missing-source, conflict, and needs-review states in typed model data.

Run:

```powershell
cd frontend; npm test -- --run ProjectWorkbench --watch=false
```

Expected:

```text
passed
```

### Task 7: Project Folder Workbench Surface

**Files:**

- Modify: `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- Create: `frontend/src/features/project-workbench/ProjectFolderPreparationPanel.tsx`
- Create: `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- Create: `frontend/src/features/project-workbench/RequestMaterialCollectionPanel.tsx`
- Create: `frontend/src/features/project-workbench/projectFolderPreparationSelectors.ts`
- Modify: `frontend/src/workbench.css`
- Test: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- Test: `tests/unit/test_frontend_shell_files.py`

- [ ] Change active-Matrix tab labels to `Project Folder | Execution`.
- [ ] Remove active-Matrix `Overview` tab from the user flow.
- [ ] Keep internal mode names if needed, but render user-facing copy as Project Folder.
- [ ] Render the preparation task list.
- [ ] Add `Request material` row/detail panel.
- [ ] Show top `Collect request material` action when request material is missing and prerequisites are met.
- [ ] Show `Request email missing` when partial collection is allowed without an email source.
- [ ] Show `Multiple request email candidates need review` as a blocker with no collect action.
- [ ] Show needs-review attachment candidates without claiming they are supporting attachments or placing them into Submitted Material.
- [ ] Render disabled/read-only future rows without enabled public-drive upload.
- [ ] Remove user-facing `Package readiness`, `Package details`, and `Secondary package links` copy from the active Project Folder surface in this task.
- [ ] Keep Matrix execution map and Step workspace only in `Execution`.

Run:

```powershell
cd frontend; npm test -- --run ProjectWorkbench requestMaterial --watch=false
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "project_workbench or request_material or task317"
```

Expected:

```text
passed
```

### Task 8: Full Validation And Task Board Update

**Files:**

- Modify: `docs/task_board.md`
- Modify: `docs/task_plan_index.md`
- Modify: `tasks/TASK_317_SOURCE_BOOK_AND_REQUEST_MATERIAL_COLLECTION.md`

- [ ] Run backend unit tests.
- [ ] Run backend integration tests.
- [ ] Run frontend Vitest target.
- [ ] Run frontend build.
- [ ] Run static shell tests.
- [ ] Run `git diff --check`.
- [ ] Browser smoke an active-Matrix project with completed local project folder.
- [ ] Update task file status to complete only after implementation passes.
- [ ] Update task board with validation summary and next recommended task.

Run:

```powershell
py -m pytest tests\unit\test_project_request_material_collection_service.py tests\unit\test_project_request_material_collection_repository.py -q
py -m pytest tests\unit\test_intake_confirmation_service.py tests\integration\test_intake_package_repositories.py -q
py -m pytest tests\integration\test_project_request_material_collection_api.py -q
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "project_workbench or request_material or task317"
cd frontend; npm test -- --run ProjectWorkbench requestMaterial --watch=false
cd frontend; npm run build
git diff --check
```

Expected:

```text
all selected tests pass
frontend build passes
git diff --check has no errors, CRLF warnings only if matching existing repository behavior
```

## Browser Smoke Checklist

Use the in-app Browser after implementation approval:

1. Open an active-Matrix project with completed local project folder.
2. Confirm top tabs read `Project Folder | Execution`.
3. Confirm there is no `Overview` tab for the active-Matrix flow.
4. Confirm the top action is `Collect request material` when request material is missing.
5. Click `Collect request material`.
6. Confirm the UI reports copied/already collected/partial state.
7. Refresh the page and confirm the state persists.
8. Inspect disk:
   - request email copy under `Source Book/Request Material/E-mail`
   - request email copy under Official project folder `E-mail`
   - selected Application Form under `Source Book/Request Material/Application Form`
   - selected Application Form under Official project folder `Submitted Material`
   - confirmed request attachments under both Source Book and `Submitted Material`
   - needs-review attachment candidates under Source Book only
9. Confirm source files still exist in their original locations.
10. Confirm no public-drive upload button is enabled.

## Completion Checklist

- The task uses existing project `FileAsset` records and does not add a new email import workflow.
- New project FileAsset provenance/source role is preserved or collection source role is persisted before classification.
- Duplicate FileAsset rows for the same source path/hash are deduped before request email classification.
- Multiple different `.msg` candidates block collection instead of copying multiple request emails.
- Missing request email policy is explicit: partial collect is allowed only with visible `Request email missing` state and skipped/missing response data.
- Unknown or ambiguous attachments are needs-review candidates, not automatically `Submitted Material` attachments.
- The task copies only and never deletes or moves source files.
- Source Book and Official project folder targets are clearly separated.
- Missing source email/application form behavior is explicit.
- The preview endpoint is read-only.
- The collect endpoint reruns preview before copying.
- The collect response includes blockers, warnings, skipped paths, missing-source paths, and conflict paths.
- Conflict behavior is no-overwrite and business-readable.
- Workbench starts from `Project Folder | Execution`.
- Public-drive upload remains hidden or read-only.
- No generated form, Section 2, report, execution evidence, or future scope sneaks into TASK_317.

## Completion Gate

TASK_317 implementation is complete. The next allowed action is to create and review
`TASK_318_OFFICIAL_PROJECT_FOLDER_CHECK_AND_REPAIR` task file and executable plan before
any new implementation code.
