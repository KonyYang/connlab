# TASK_318 Official Project Folder Check And Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Project Folder check and missing-folder repair flow for the local Official project folder without returning to the old package-preview UI.

**Architecture:** Backend owns folder/file inspection, status calculation, conflict detection, and safe folder repair through application services and infrastructure file operations. Frontend consumes typed check/repair APIs and renders a Project Folder row plus one current action. The old `/project-package/preview` route remains historical compatibility and must not become the TASK_318 product contract.

**Tech Stack:** Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.x repositories where needed, React, TypeScript, Vitest, pytest.

---

Status: Complete. Implemented on 2026-06-13.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Completion status: TASK_318 is implemented and verified. `TASK_317C_TEMPORARY_PROJECT_PLANNING_IDENTITY` remains a separate proposed interleaved task for review; TASK_318 does not consume or rename it.

Task file:

- `tasks/TASK_318_OFFICIAL_PROJECT_FOLDER_CHECK_AND_REPAIR.md`

Predecessors:

- `TASK_316_LOCAL_PROJECT_WORKSPACE_CREATION_FROM_TEMPLATE`, complete.
- `TASK_317A_PROJECT_FOLDER_PREPARATION_UI_BLUEPRINT`, accepted.
- `TASK_317_SOURCE_BOOK_AND_REQUEST_MATERIAL_COLLECTION`, complete with review corrections.

## Required Preconditions Before Coding

Implementation worker must read:

1. `AGENTS.md`
2. `docs/task_board.md`
3. `tasks/TASK_318_OFFICIAL_PROJECT_FOLDER_CHECK_AND_REPAIR.md`
4. `docs/task_318_official_project_folder_check_and_repair_plan.md`
5. `tasks/TASK_317_SOURCE_BOOK_AND_REQUEST_MATERIAL_COLLECTION.md`
6. `docs/task_317_source_book_and_request_material_collection_plan.md`
7. `tasks/TASK_313B_OFFICIAL_PROJECT_WORKSPACE_PLAN.md`
8. `docs/project_management/TASK_EXECUTION_SKILL.md`
9. `docs/project_management/TASK_REVIEW_CHECKLIST.md`
10. `docs/02_ARCHITECTURE_RULES.md`
11. `docs/frontend_architecture_rules.md`

Because TASK_318 changes Workbench UI and UX copy, implementation must load `$impeccable` product context before UI work.

Pre-implementation gate was satisfied before coding: the user explicitly approved TASK_318 implementation after review corrections.

The task checklist below is retained as the historical execution plan. Completion status, validation, and remaining manual-smoke limitation are recorded in the task file and task board.

## Step 1 - Task Understanding

Goal:

- Check whether the local Official project folder has the expected folder structure and currently checkable required files.
- Provide a safe repair action for missing folders only.
- Surface the result inside the Project Folder Workbench flow.

Inputs:

- project id
- completed TASK_316 official workspace record
- real file system under the local DL folder
- TASK_317 request-material preview/collection state
- `ProjectOutputRecordService.get_status_summary()` for currently mappable output status rows:
  - `TEST_RECORD_FORM`
  - `FEE_EVALUATION`
  - `SECTION2_WRITE_BACK`
- existing Section 2 preview read model where already exposed
- no `ProjectPackagePreviewService` or `/project-package/preview` source as the TASK_318 read model

Outputs:

- official folder check preview
- safe repair result for missing folders
- Workbench row state
- one current next action

Involved modules:

- backend application service for official folder check
- backend infrastructure file gateway for mkdir-only repair
- backend API route and dependency wiring
- frontend API client
- Project Workbench model/selectors/components
- pytest, integration API tests, Vitest/static shell tests

Not allowed:

- no public-drive upload
- no generated Test Record/Fee Form/Customer Feedback file creation
- no Section 2 write-back
- no request material re-copy
- no overwrite/delete/move
- no direct Office calls
- no StepInstance/TestResult/evidence/report/AI/permissions/LAN/multi-user work
- no enhancement of old `/project-package/preview` as the main product path

## Step 2 - Proposed Design

### Backend Types

Create a dedicated application module:

```text
backend/application/official_project_folder_check_service.py
```

Core dataclasses:

```python
@dataclass(frozen=True, slots=True)
class OfficialFolderCheckItem:
    key: str
    label: str
    kind: str
    status: str
    path: Path | None
    message: str
    repairable: bool = False


@dataclass(frozen=True, slots=True)
class OfficialFolderCheckPreview:
    project_id: str
    status: str
    local_workspace_path: Path | None
    official_project_folder_path: Path | None
    required_folders: tuple[OfficialFolderCheckItem, ...]
    required_files: tuple[OfficialFolderCheckItem, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    next_action: str


@dataclass(frozen=True, slots=True)
class OfficialFolderRepairResult:
    project_id: str
    repair_status: str
    created_paths: tuple[Path, ...]
    unresolved_conflicts: tuple[Path, ...]
    errors: tuple[str, ...]
    preview: OfficialFolderCheckPreview
```

Status vocabulary:

- check status: `blocked`, `missing`, `warning`, `ready`, `conflict`
- item status: `ready`, `missing`, `conflict`, `warning`, `not_applicable`, `deferred`
- next action: `repair_folders`, `none`
- repair status: `completed`, `partial`, `blocked`, `conflict`

`Refresh folder check` is a frontend retry action when the check request fails. It is not a backend check status and should not be returned as `next_action` by the backend.

Required folder keys:

```python
REQUIRED_OFFICIAL_FOLDER_PATHS = (
    ("official_root", "Official project folder", Path(".")),
    ("email", "E-mail", Path("E-mail")),
    ("submitted_material", "Submitted Material", Path("Submitted Material")),
    ("photos", "Photos", Path("Photos")),
    ("test_results", "Test results", Path("Test results")),
    ("final_examination", "Final Examination", Path("Test results") / "Final Examination"),
)
```

### Backend Service Rules

`OfficialProjectFolderCheckService.preview(project_id)`:

- loads the project only to validate existence
- loads completed TASK_316 official workspace record
- blocks when no official workspace record exists
- blocks when official folder path is missing
- checks required folder paths with real file system state
- reports wrong-type path as `conflict`
- consumes TASK_317 request-material preview where available
- reports request material state without copying anything
- treats future generated files as `deferred` unless current output records/files already provide a concrete expected path
- reads output status only from `ProjectOutputRecordService.get_status_summary()` for `TEST_RECORD_FORM`, `FEE_EVALUATION`, and `SECTION2_WRITE_BACK`
- keeps Customer Feedback `deferred` unless a current approved service provides a concrete project-local target file path or explicit output record
- never calls `ProjectPackagePreviewService` or `/project-package/preview` to derive TASK_318 rows

`OfficialProjectFolderCheckService.repair_folders(project_id)`:

- reruns preview first
- rejects `blocked` and `conflict`
- creates only missing required folders
- if a later folder creation fails after earlier folders were created, catches the typed failure, reruns preview, and returns `repair_status = "partial"` with `created_paths`, `unresolved_conflicts`, `errors`, and refreshed preview
- reruns preview after repair
- returns created paths and final preview

### Infrastructure File Gateway

Create:

```text
backend/infrastructure/files/official_project_folder_repair_gateway.py
```

Gateway methods:

```python
class OfficialProjectFolderRepairGateway:
    def create_missing_folders(self, paths: Sequence[Path]) -> tuple[Path, ...]:
        """Create validated missing folders and return created paths."""
        raise NotImplementedError
```

Rules:

- call `mkdir(parents=True, exist_ok=True)` only after application service has filtered safe folder paths
- never delete
- never overwrite file paths
- raise a typed application error when a path exists as a file

### API Contract

Create:

```text
backend/api/routes_official_project_folder_check.py
```

Routes:

```text
GET  /api/projects/{project_id}/official-folder/check
POST /api/projects/{project_id}/official-folder/repair-folders
```

Preview response:

```json
{
  "project_id": "P1",
  "status": "missing",
  "local_workspace_path": "D:\\Test Project\\DL-2026-05-011",
  "official_project_folder_path": "D:\\Test Project\\DL-2026-05-011\\DL-2026-05-011 Coolpower HDF 3.40mm pin Qualification Testing",
  "required_folders": [],
  "required_files": [],
  "blockers": [],
  "warnings": [],
  "next_action": "repair_folders"
}
```

Repair response:

```json
{
  "project_id": "P1",
  "repair_status": "completed",
  "created_paths": [
    "D:\\Test Project\\DL-2026-05-011\\DL-2026-05-011 Coolpower HDF 3.40mm pin Qualification Testing\\Photos"
  ],
  "unresolved_conflicts": [],
  "errors": [],
  "preview": {}
}
```

HTTP behavior:

- `404` when project does not exist
- `409` when preview is blocked or conflicts prevent repair
- `200` for preview, successful repair, and explainable partial repair results

### Frontend Contract

Add typed DTOs and functions in `frontend/src/api/client.ts`:

```ts
export type OfficialFolderCheckStatus =
  | "blocked"
  | "missing"
  | "warning"
  | "ready"
  | "conflict";

export type OfficialFolderCheckItemStatus =
  | "ready"
  | "missing"
  | "conflict"
  | "warning"
  | "not_applicable"
  | "deferred";

export type OfficialFolderCheckItem = {
  key: string;
  label: string;
  kind: string;
  status: OfficialFolderCheckItemStatus;
  path?: string | null;
  message: string;
  repairable: boolean;
};

export type OfficialFolderCheckPreview = {
  project_id: string;
  status: OfficialFolderCheckStatus;
  local_workspace_path?: string | null;
  official_project_folder_path?: string | null;
  required_folders: OfficialFolderCheckItem[];
  required_files: OfficialFolderCheckItem[];
  blockers: string[];
  warnings: string[];
  next_action: "repair_folders" | "none";
};

export type OfficialFolderRepairResponse = {
  project_id: string;
  repair_status: "completed" | "partial" | "blocked" | "conflict";
  created_paths: string[];
  unresolved_conflicts: string[];
  errors: string[];
  preview: OfficialFolderCheckPreview;
};
```

Frontend model additions:

- `officialFolderCheckPreview`
- `officialFolderCheckLoading`
- `officialFolderCheckRepairing`
- `officialFolderCheckError`
- `onRefreshOfficialFolderCheck`
- `onRepairOfficialFolderStructure`

Project Folder UI:

- add a `Folder structure` row
- add a `Submitted Material` row backed by check status and TASK_317 request material state
- remove or replace remaining `Package readiness` copy in active Project Folder surface
- keep public-drive upload hidden or read-only
- show only one primary action from lifecycle selector

### Avoiding TASK_312 Regression

Do not use `/api/projects/{project_id}/project-package/preview` as the TASK_318 API contract.

Allowed:

- reuse lower-level helper logic only if moved behind a Project Folder check service and covered by TASK_318 tests

Forbidden:

- adding more items to `ProjectPackagePreviewService` as the main product path
- showing another package preview panel in Workbench
- user-facing `Package readiness`, `Package details`, or `Secondary package links` copy

## Implementation Tasks

### Task 1: Backend Domain And Folder Check Service

**Files:**

- Create: `backend/application/official_project_folder_check_service.py`
- Test: `tests/unit/test_official_project_folder_check_service.py`

- [ ] Write failing test: preview blocks without official workspace record.

```python
def test_preview_blocks_without_official_workspace(tmp_path):
    service = _service(tmp_path, workspace=None)

    preview = service.preview("P1")

    assert preview.status == "blocked"
    assert preview.next_action == "none"
    assert "Create local project folder before checking the Project Folder." in preview.blockers
```

- [ ] Run:

```powershell
py -m pytest tests\unit\test_official_project_folder_check_service.py -q
```

Expected: fails because module/service does not exist.

- [ ] Implement dataclasses, ports, constants, and `preview(project_id)` blocked path.
- [ ] Run the test again.

Expected: passes.

- [ ] Add failing test: preview reports missing required folders.

```python
def test_preview_reports_missing_required_folders(tmp_path):
    official = tmp_path / "DL-001" / "DL-001 Connector Qualification test"
    official.mkdir(parents=True)
    service = _service(tmp_path, workspace=_workspace(tmp_path, official))

    preview = service.preview("P1")

    missing = {item.key for item in preview.required_folders if item.status == "missing"}
    assert {"email", "submitted_material", "photos", "test_results", "final_examination"} <= missing
    assert preview.status == "missing"
    assert preview.next_action == "repair_folders"
```

- [ ] Implement required folder inspection.
- [ ] Add failing test: wrong-type path reports conflict.

```python
def test_preview_reports_conflict_when_required_folder_path_is_file(tmp_path):
    official = tmp_path / "DL-001" / "DL-001 Connector Qualification test"
    (official / "E-mail").parent.mkdir(parents=True)
    (official / "E-mail").write_text("not a folder", encoding="utf-8")
    service = _service(tmp_path, workspace=_workspace(tmp_path, official))

    preview = service.preview("P1")

    assert preview.status == "conflict"
    assert preview.next_action == "none"
    assert any(item.key == "email" and item.status == "conflict" for item in preview.required_folders)
```

- [ ] Implement conflict status.
- [ ] Add failing test: all required folders ready.

```python
def test_preview_reports_ready_when_required_folders_exist(tmp_path):
    official = _official_with_required_folders(tmp_path)
    service = _service(tmp_path, workspace=_workspace(tmp_path, official))

    preview = service.preview("P1")

    assert preview.status == "ready"
    assert preview.next_action == "none"
    assert all(item.status == "ready" for item in preview.required_folders)
```

- [ ] Implement ready status.

### Task 2: Safe Folder Repair Gateway And Service Operation

**Files:**

- Create: `backend/infrastructure/files/official_project_folder_repair_gateway.py`
- Modify: `backend/application/official_project_folder_check_service.py`
- Test: `tests/unit/test_official_project_folder_check_service.py`

- [ ] Add failing test: repair creates only missing folders.

```python
def test_repair_folders_creates_missing_required_folders(tmp_path):
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
```

- [ ] Run test and verify it fails.
- [ ] Implement `OfficialProjectFolderRepairGateway.create_missing_folders(paths)`.
- [ ] Implement `repair_folders(project_id)` in service.
- [ ] Run test and verify it passes.
- [ ] Add failing test: repair refuses conflicts.

```python
def test_repair_folders_refuses_conflict_paths(tmp_path):
    official = tmp_path / "DL-001" / "DL-001 Connector Qualification test"
    (official / "E-mail").parent.mkdir(parents=True)
    (official / "E-mail").write_text("not a folder", encoding="utf-8")
    service = _service(tmp_path, workspace=_workspace(tmp_path, official))

    with pytest.raises(OfficialProjectFolderCheckConflictError):
        service.repair_folders("P1")
```

- [ ] Implement typed conflict error and guard.
- [ ] Add failing test: partial repair failure returns created paths and refreshed preview.

```python
def test_repair_folders_returns_partial_result_when_later_folder_creation_fails(tmp_path):
    official = tmp_path / "DL-001" / "DL-001 Connector Qualification test"
    official.mkdir(parents=True)
    gateway = _FailingAfterFirstCreateGateway()
    service = _service(tmp_path, workspace=_workspace(tmp_path, official), repair_gateway=gateway)

    result = service.repair_folders("P1")

    assert result.repair_status == "partial"
    assert result.created_paths
    assert result.errors
    assert result.preview.status in {"missing", "conflict", "warning"}
```

- [ ] Implement typed partial failure result handling.
- [ ] Ensure a generic exception is not returned when partial folder creation already happened.

### Task 3: Required File And Request Material Check Integration

**Files:**

- Modify: `backend/application/official_project_folder_check_service.py`
- Test: `tests/unit/test_official_project_folder_check_service.py`

- [ ] Add failing test: request material collected state appears in required file items.

```python
def test_preview_includes_request_material_state(tmp_path):
    official = _official_with_required_folders(tmp_path)
    request_preview = _request_material_preview(status="collected")
    service = _service(
        tmp_path,
        workspace=_workspace(tmp_path, official),
        request_material_service=_RequestMaterialPreviewer(request_preview),
    )

    preview = service.preview("P1")

    assert any(item.key == "request_material" and item.status == "ready" for item in preview.required_files)
```

- [ ] Add request-material preview port to service.
- [ ] Map TASK_317 statuses:
  - `collected` -> `ready`
  - `review_required` -> `warning` with message `Needs review`
  - `partial` -> `warning` only when copyable targets remain
  - `blocked` or `conflict` -> `conflict`
  - `ready` or null -> `missing`
- [ ] Keep `Request material` and `Submitted Material` as separate rows:
  - Request material reflects TASK_317 collection/review state.
  - Submitted Material is ready only when confirmed collected targets exist in the Official project folder's `Submitted Material`.
  - Source Book-only or review-only candidates do not make Submitted Material ready and must not be counted as missing submitted files.
  - If only manual review remains after collection, TASK_317 must expose `review_required`; TASK_318 must not keep showing a `Collect request material` loop.
- [ ] Add failing test: generated files are deferred when no current output record exists.

```python
def test_preview_defers_generated_forms_without_existing_output_records(tmp_path):
    official = _official_with_required_folders(tmp_path)
    service = _service(tmp_path, workspace=_workspace(tmp_path, official))

    preview = service.preview("P1")

    generated = {item.key: item.status for item in preview.required_files if item.key in {"test_record", "fee_form", "customer_feedback"}}
    assert generated == {
        "test_record": "deferred",
        "fee_form": "deferred",
        "customer_feedback": "deferred",
    }
```

- [ ] Implement deferred generated-file items.
- [ ] Add output summary port using `ProjectOutputRecordService.get_status_summary()`.
- [ ] Map only:
  - `TEST_RECORD_FORM` -> Test Record
  - `FEE_EVALUATION` -> Fee Form / Confirmed Fee output status where current records provide a path
  - `SECTION2_WRITE_BACK` -> Application Form Section 2 status
- [ ] Leave Customer Feedback `deferred` unless a current approved service provides a concrete project-local target path or explicit output record.
- [ ] Add a test proving template discovery alone does not mark Customer Feedback ready.
- [ ] Add a test proving `ProjectPackagePreviewService` is not required or called by the check service.

### Task 4: API Routes And Dependency Wiring

**Files:**

- Create: `backend/api/routes_official_project_folder_check.py`
- Modify: `backend/api/dependencies.py`
- Modify: `backend/api/main.py`
- Test: `tests/integration/test_official_project_folder_check_api.py`

- [ ] Add failing integration test for preview.

```python
def test_official_folder_check_preview_reports_missing_folders(client, seeded_project_with_workspace):
    response = client.get(f"/api/projects/{seeded_project_with_workspace.project_id}/official-folder/check")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"missing", "ready", "warning", "conflict"}
    assert "required_folders" in body
```

- [ ] Add response DTOs for preview, item, and repair result.
- [ ] Add `GET /api/projects/{project_id}/official-folder/check`.
- [ ] Wire dependency factory.
- [ ] Add router to main app.
- [ ] Add failing integration test for repair.

```python
def test_official_folder_repair_creates_missing_folders(client, seeded_project_with_workspace):
    response = client.post(f"/api/projects/{seeded_project_with_workspace.project_id}/official-folder/repair-folders")

    assert response.status_code == 200
    body = response.json()
    assert body["created_paths"]
    assert body["preview"]["status"] in {"ready", "warning"}
```

- [ ] Implement `POST /repair-folders`.
- [ ] Map service not-found to `404`.
- [ ] Map blocked/conflict repair to `409`.

### Task 5: Frontend API Client And Workbench Model

**Files:**

- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- Modify: `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
- Test: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`

- [ ] Add DTO types shown in the Frontend Contract section.
- [ ] Add API functions:

```ts
export async function fetchOfficialFolderCheck(projectId: string): Promise<OfficialFolderCheckPreview> {
  return apiGet<OfficialFolderCheckPreview>(`/api/projects/${projectId}/official-folder/check`);
}

export async function repairOfficialFolderStructure(projectId: string): Promise<OfficialFolderRepairResponse> {
  return apiPost<OfficialFolderRepairResponse>(`/api/projects/${projectId}/official-folder/repair-folders`, {});
}
```

- [ ] Add model state:
  - `officialFolderCheckPreview`
  - `officialFolderCheckLoading`
  - `officialFolderCheckRepairing`
  - `officialFolderCheckError`
- [ ] Fetch folder check after official workspace preview and request-material collection.
- [ ] Use `officialFolderCheckError` only for frontend request failures that should show `Refresh folder check`.
- [ ] Add handlers:
  - `onRefreshOfficialFolderCheck`
  - `onRepairOfficialFolderStructure`
- [ ] Add failing test: model-driven layout shows repair action when folder check is missing.
- [ ] Implement model pass-through to runtime console model.

### Task 6: Project Folder UI Integration

**Files:**

- Modify: `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- Modify: `frontend/src/workbench.css`
- Test: `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
- Test: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- Test: `tests/unit/test_frontend_shell_files.py`

- [ ] Add lifecycle input fields:
  - `officialFolderCheckStatus`
  - `officialFolderCheckBlockers`
  - `officialFolderCheckWarnings`
  - `hasOfficialFolderCheckError`
- [ ] Add next action rule:
  - missing folder structure -> `Repair folder structure`
  - conflict -> blocker, no action
  - frontend request error -> `Refresh folder check`
- [ ] Do not add backend `stale` or `error` status vocabulary in TASK_318. Use `hasOfficialFolderCheckError` only for frontend fetch/repair request failure.
- [ ] Add one action target:
  - `official_folder_repair`
  - `official_folder_refresh`
- [ ] Add `Folder structure` row.
- [ ] Add `Submitted Material` row using check/request-material state.
- [ ] Remove active Project Folder user-facing `Package readiness` copy.
- [ ] Keep `Project Folder | Execution` tabs.
- [ ] Add selector tests:

```ts
it("routes missing folder structure to repair action", () => {
  const lifecycle = deriveProjectWorkbenchLifecycle({
    ...baseInput,
    hasLtr: true,
    hasActiveMatrix: true,
    folderReady: true,
    requestMaterialStatus: "collected",
    officialFolderCheckStatus: "missing",
  });

  expect(lifecycle.nextAction.title).toBe("Repair folder structure");
  expect(lifecycle.nextAction.actionTarget).toBe("official_folder_repair");
});
```

- [ ] Add static shell guard that active Project Folder surface does not reintroduce `Package readiness`, `Package details`, or `Secondary package links`.
- [ ] Add static shell guard or unit test that `ProjectPackagePreviewService` is not imported by the TASK_318 check service.

### Task 7: Validation, Browser Smoke, And Task Board Update

**Files:**

- Modify: `docs/task_board.md`
- Modify: `docs/task_plan_index.md`
- Modify: `tasks/TASK_318_OFFICIAL_PROJECT_FOLDER_CHECK_AND_REPAIR.md`

- [ ] Run backend unit tests:

```powershell
py -m pytest tests\unit\test_official_project_folder_check_service.py -q
```

- [ ] Run backend integration tests:

```powershell
py -m pytest tests\integration\test_official_project_folder_check_api.py -q
```

- [ ] Run frontend tests:

```powershell
cd frontend; npm test -- --run ProjectWorkbench officialFolder --watch=false
```

- [ ] Run frontend static shell tests:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "project_workbench or official_folder or task318"
```

- [ ] Run frontend build:

```powershell
cd frontend; npm run build
```

- [ ] Run diff check:

```powershell
git diff --check
```

- [ ] Browser smoke:
  1. Open an active-Matrix project with completed local project folder.
  2. Confirm Project Folder shows `Folder structure`.
  3. Confirm a fixture with missing folder shows `Repair folder structure`.
  4. Execute repair.
  5. Confirm folders exist on disk.
  6. Confirm conflicts block repair and no destructive action appears.
  7. Confirm no public-drive upload action is enabled.

- [ ] Update TASK_318 task file status only after implementation passes.
- [ ] Update task board with validation summary and next recommended task.

## Review Checklist Before Approval

- TASK_318 is not using old package preview as the main product path.
- TASK_318 uses `ProjectOutputRecordService.get_status_summary()` for currently mappable generated-output rows.
- Required generated files are deferred unless existing current records/files make them checkable.
- Customer Feedback template availability does not count as a ready project output.
- Repair partial failure returns created paths, unresolved conflicts or errors, and refreshed preview.
- Repair only creates folders.
- Request material is checked, not copied again.
- Request material and Submitted Material remain distinct statuses.
- Public-drive upload remains out of scope.
- Workbench still exposes one primary action.
- No user-facing `.connlab`, manifest, SQLite, task id, or route name appears.

## Completion Gate

TASK_318 implementation is complete. Stop here and do not enter TASK_319 or TASK_317C without a separate user approval.
