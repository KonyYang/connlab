# TASK_316 Local Project Workspace Creation From Template Executable Plan

Status: Complete. Review follow-up applied: completed-workspace preview recognition, registered-LTR authority preference over legacy `project.project_no`, application-form requested-testing folder naming input, Settings-page `Public Project locations` only for public-drive placement, Workbench path-blocker reminder without a shortcut button, and sidebar Projects restoration to the current Workbench context. Local workspace root and official project folder template remain installation-level settings, not ordinary operator Settings fields.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_316_LOCAL_PROJECT_WORKSPACE_CREATION_FROM_TEMPLATE`, complete.

Allowed reason: `TASK_313B_OFFICIAL_PROJECT_WORKSPACE_PLAN` boundary corrections are documented and accepted for planning. `TASK_313`, `TASK_314`, and `TASK_315` remain deferred. TASK_316 is the next controlled task only after this task file and executable plan are reviewed and explicitly approved for implementation.

Task file:

- `tasks/TASK_316_LOCAL_PROJECT_WORKSPACE_CREATION_FROM_TEMPLATE.md`

Reference guide:

- `docs/task_313b_official_project_workspace_execution_guide.md`

## Required Preconditions Before Coding

Implementation worker must read:

1. `AGENTS.md`
2. `docs/task_board.md`
3. `tasks/TASK_316_LOCAL_PROJECT_WORKSPACE_CREATION_FROM_TEMPLATE.md`
4. `docs/task_313b_official_project_workspace_execution_guide.md`
5. `docs/project_management/TASK_EXECUTION_SKILL.md`
6. `docs/project_management/TASK_REVIEW_CHECKLIST.md`
7. `docs/02_ARCHITECTURE_RULES.md`
8. `docs/frontend_architecture_rules.md`

Because TASK_316 touches Project Workbench UI, implementation must load `$impeccable` product context before UI work.

No code may be written until the user explicitly approves this plan for implementation.

## Step 1 - Task Understanding

Goal:

- Create the local DL workspace and official project folder from a configured template, with preview-first safety and a minimal single-primary-action Workbench state.

Inputs:

- project id
- project DL number, using `project.project_no` or latest LTR fallback according to existing Workbench/project conventions
- product description
- test description from available project/application data
- configured local workspace root
- configured official project folder template path
- configured public drive root path, documented for later TASK_319 and never blocking TASK_316 local create

Outputs:

- workspace preview response
- workspace create response
- local DL workspace folder
- `Source Book`
- copied official project folder
- `.connlab/manifest.json`
- SQLite/index record if needed for lookup
- Workbench one-primary-action surface for workspace creation

Involved modules:

- backend settings/config
- backend application service for official workspace preview/create
- backend infrastructure for manifest writing and safe template copy
- backend API routes and dependency wiring
- frontend API client
- frontend Project Workbench model/selectors/components
- backend pytest and frontend Vitest/static shell tests

Not allowed:

- no public drive upload
- no request email or attachment collection
- no submitted material copy
- no Test Record/Fee/Customer Feedback generation changes
- no Section 2 write-back changes
- no StepInstance/TestResult/evidence/report/AI/permissions/multi-user work
- no destructive move/delete behavior
- no overwrite of existing folders
- no user-facing `Package`, `.connlab`, `manifest`, task id, or API route names in Workbench copy

## Step 2 - Proposed Design

### Settings Contract

Reuse the existing operator-visible Settings registry instead of inventing parallel config:

- `Project default save location` (`project_output_root`) is the local workspace root.
- `Template folder` (`project_folder_template`) is the official project folder template parent/root.
- `Public Project locations` (`official_public_drive_root`) is the future public-drive upload root.

There is no hidden `[official_workspace]` fallback path for TASK_316. If one of the visible Settings registry rows is missing, inactive, or invalid, preview/create reports that condition directly instead of silently using a default path.

Blocking rules:

- Missing or invalid `Project default save location` blocks preview/create.
- Missing or invalid `Template folder` blocks preview/create.
- Missing or invalid `Public Project locations` is only a warning/future-readiness issue in TASK_316. It does not block local workspace preview or creation.
- TASK_316 does not upload or write to the public drive.

Expected backend file:

- Modify `backend/shared/config.py`

Add a dataclass similar to existing setting groups:

```python
@dataclass(frozen=True, slots=True)
class OfficialWorkspaceSettings:
    """Runtime settings for official project workspace creation."""

    local_workspace_root: Path | None = None
    template_path: Path | None = None
    public_drive_root: Path | None = None
```

Then add `official_workspace: OfficialWorkspaceSettings` to `Settings`.

### Workspace Preview Model

New backend application DTOs should be pure dataclasses in a focused service file.

Recommended new file:

- `backend/application/official_project_workspace_service.py`

Recommended dataclasses:

```python
@dataclass(frozen=True, slots=True)
class OfficialWorkspacePreview:
    """Preview of local official project workspace creation."""

    project_id: str
    dl_number: str
    local_workspace_root: Path | None
    local_workspace_path: Path | None
    source_book_path: Path | None
    template_path: Path | None
    official_folder_path: Path | None
    manifest_path: Path | None
    template_root_mode: str | None
    status: str
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    planned_paths: tuple[Path, ...]
```

Status values:

- `ready`: create can run
- `completed`: ConnLab workspace record, `.connlab/manifest.json`, and file-system paths match an already-created local official workspace
- `blocked`: missing settings, missing project identity, invalid template, invalid root, path too long
- `adoptable`: the top-level local DL workspace already exists and is safe to continue from
- `exists`: the planned official project folder target already exists and must not be overwritten or merged in TASK_316
- `inconsistent`: manifest/SQLite/file-system state disagrees and requires repair before create

Create may proceed from `ready` and `adoptable`. Create may return the existing workspace record without writing when preview is `completed`. Create must reject `blocked`, `exists`, and `inconsistent` unless a later task explicitly implements repair/adopt for those cases.

### Folder Name Planner

Keep naming rules pure and independently tested.

Recommended new file:

- `backend/application/official_project_workspace_naming.py`

Recommended API:

```python
def build_official_project_folder_name(
    *,
    dl_number: str,
    product_description: str | None,
    test_description: str | None,
    max_segment_length: int = 150,
) -> str:
    """Return a safe business-readable official project folder name."""
```

Rules:

- replace Windows-invalid characters `< > : " / \ | ? *` with spaces or `_`
- normalize all whitespace to single spaces
- trim leading/trailing spaces and trailing dots
- avoid reserved Windows device names if the final segment would match one
- fallback product description: `Product`
- fallback test description: `Qualification test`
- preserve the DL number at the beginning
- fail with an actionable error if the resulting full path would exceed the configured safe full-path limit

### Template Path Interpretation

TASK_316 must accept one configured template path with deterministic interpretation:

1. If the path itself contains the required template subfolders, treat it as the template root.
2. Otherwise, if it is a parent directory containing exactly one child directory that contains the required template subfolders, treat that child as the template root.
3. Otherwise block preview with a message asking the operator to choose the official project folder template root.

Minimum required template subfolders:

- `E-mail`
- `Submitted Material`
- `Photos`
- `Test results`
- `Test results/Final Examination`

Recommended helper:

```python
def resolve_official_template_root(path: Path) -> OfficialTemplateRoot:
    """Resolve configured template path to exactly one official project template root."""
```

### Existing Workspace Adoption

TASK_316 must support real projects where the operator or earlier tools already created part of the local structure.

Rules:

- If `{LOCAL_WORKSPACE_ROOT}/{DL_NUMBER}/` already exists and has no unsafe conflict, preview returns `adoptable` instead of blocking the whole workflow.
- If `Source Book/` is missing inside an adoptable workspace, create may add it.
- If `.connlab/` is missing inside an adoptable workspace, create may add it.
- If `.connlab/manifest.json` exists and matches the planned file-system state, create may continue.
- If `.connlab/manifest.json` exists but disagrees with the file system or SQLite workspace index, preview returns `inconsistent` with a repairable inconsistency message.
- If the planned official project folder target already exists, preview returns `exists`; TASK_316 must not overwrite, merge, or silently adopt that official folder. A later repair/adopt task can define that behavior.

### Manifest Contract

Recommended new infrastructure file:

- `backend/infrastructure/official_workspace_manifest.py`

Manifest path:

```text
{LOCAL_WORKSPACE_ROOT}/{DL_NUMBER}/.connlab/manifest.json
```

Manifest content:

```json
{
  "schema_version": 1,
  "project_id": "...",
  "dl_number": "DL-2025-11-074",
  "local_workspace_path": "...",
  "source_book_path": "...",
  "official_project_folder_path": "...",
  "template_source_path": "...",
  "created_at": "2026-06-12T00:00:00Z"
}
```

Rules:

- Write UTF-8 JSON.
- Create `.connlab` only under the local DL workspace.
- Do not expose `.connlab` or manifest language in UI.
- If an existing manifest disagrees with SQLite or the file system, report a repairable inconsistency instead of overwriting.

### SQLite Index

Prefer adding a focused workspace record rather than overloading existing `ProjectFolderRecord`, because the new model distinguishes:

- local DL workspace,
- Source Book,
- official project folder,
- future public drive upload target.

Recommended new domain/infrastructure pieces:

- Create `ProjectOfficialWorkspaceRecord` domain object if the domain pattern supports it.
- Create repository/table in existing SQLite infrastructure.
- Keep API response DTOs separate from ORM/storage objects.

If the existing repository layer makes a new table too risky for TASK_316, implementation may initially store only the manifest and derive preview from file system, but it must document that SQLite workspace index is deferred and update tests/board accordingly. The preferred plan is to index in SQLite now to avoid relying on manifest alone.

### API Contract

Recommended new file:

- `backend/api/routes_official_project_workspace.py`

Routes:

```text
GET  /api/projects/{project_id}/official-workspace/preview
POST /api/projects/{project_id}/official-workspace/create
```

Dependency:

- Modify `backend/api/dependencies.py` to provide `OfficialProjectWorkspaceService`.
- Modify `backend/api/main.py` to include the router.

Response models should be typed Pydantic classes in the route module or a narrow DTO module.

Create must:

1. re-run preview,
2. accept only `ready` or `adoptable` status for creation,
3. return the existing workspace record without writing when preview is `completed`,
4. reject `blocked`, `exists`, and `inconsistent`,
5. create folders in a safe order,
6. copy template to a ConnLab-owned temporary directory,
7. rename the copied temporary directory to the planned official folder path,
8. create `Source Book`,
9. write manifest,
10. write SQLite index if included,
11. return created paths.

No final write may occur if a target conflict is detected during preview.

### File Operation Recovery

Template copy must be staged so a partial copy does not poison future previews.

Required behavior:

- Create a ConnLab-owned temporary directory under the local DL workspace, for example `.connlab/tmp/create-official-folder-{operation_id}`.
- Copy the resolved template root into that temporary directory.
- After copy succeeds, rename the copied root to the final official project folder path.
- Write manifest and SQLite index only after the final rename succeeds.
- If copy fails, remove only the temporary directory created during this run.
- If rename fails, remove the temporary directory when possible and return an actionable error.
- Never delete or alter user-created existing folders/files.
- Never leave a half-created final official project folder path after a failed create.

### Frontend Contract

Recommended API client additions:

- Modify `frontend/src/api/client.ts`

Add types:

```typescript
export type OfficialWorkspacePreviewStatus =
  | "ready"
  | "blocked"
  | "adoptable"
  | "exists"
  | "inconsistent";

export type OfficialWorkspacePreview = {
  project_id: string;
  dl_number?: string | null;
  status: OfficialWorkspacePreviewStatus;
  local_workspace_path?: string | null;
  official_project_folder_path?: string | null;
  source_book_path?: string | null;
  blockers: string[];
  warnings: string[];
  planned_paths: string[];
};
```

Add client functions:

```typescript
export async function getOfficialWorkspacePreview(projectId: string): Promise<OfficialWorkspacePreview>;
export async function createOfficialWorkspace(projectId: string): Promise<OfficialWorkspaceCreateResponse>;
```

Recommended frontend feature files:

- Create `frontend/src/features/project-workbench/OfficialWorkspaceActionPanel.tsx`
- Create `frontend/src/features/project-workbench/officialWorkspaceSelectors.ts`
- Add/modify tests near `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`

Minimum UI behavior:

- Backend preview can be available for any project with a DL number.
- Workbench primary action appears only when the project has a DL number, active Confirmed Matrix, and no completed local workspace.
- In the relevant state, show one primary action: `Create local project workspace`.
- Show one reason, for example: `The official project folder has not been created locally.`
- Keep path diagnostics collapsed or secondary.
- Do not render `Package` copy in this state.

## Step 3 - File-Level Change Plan

### Backend Files

Create:

- `backend/application/official_project_workspace_naming.py`
- `backend/application/official_project_workspace_service.py`
- `backend/infrastructure/official_workspace_manifest.py`
- `backend/api/routes_official_project_workspace.py`
- `tests/unit/test_official_project_workspace_naming.py`
- `tests/unit/test_official_project_workspace_service.py`
- `tests/integration/test_official_project_workspace_api.py`

Likely modify:

- `backend/shared/config.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`
- SQLite repository/database setup files, after locating the existing persistence pattern during implementation.

### Frontend Files

Create:

- `frontend/src/features/project-workbench/OfficialWorkspaceActionPanel.tsx`
- `frontend/src/features/project-workbench/officialWorkspaceSelectors.ts`

Modify:

- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchSupportModel.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `tests/unit/test_frontend_shell_files.py`

Avoid:

- Growing `ProjectWorkbenchLayout.tsx` with large new branches.
- Putting file-system business logic in React click handlers.
- Adding duplicate Workbench tabs or checklist panels.

## Step 4 - Implementation Tasks

### Task 1 - Backend Naming Tests And Pure Planner

Files:

- Create `tests/unit/test_official_project_workspace_naming.py`
- Create `backend/application/official_project_workspace_naming.py`

Steps:

- Write tests for invalid characters, whitespace, missing product, missing test description, long segment truncation, reserved names, and DL prefix preservation.
- Implement the pure planner.
- Run:

```powershell
py -m pytest tests/unit/test_official_project_workspace_naming.py -q
```

Expected:

- All naming tests pass.

### Task 2 - Settings Contract

Files:

- Modify `backend/shared/config.py`
- Modify or add `tests/unit/test_config.py`

Steps:

- Add `OfficialWorkspaceSettings`.
- Load env/local TOML values.
- Keep missing values as `None`.
- Do not create directories for optional external roots automatically unless existing settings behavior requires it.
- Add tests for env overrides and local config parsing.
- Run:

```powershell
py -m pytest tests/unit/test_config.py -q
```

Expected:

- Existing config tests plus new official workspace settings tests pass.

### Task 3 - Manifest Gateway

Files:

- Create `backend/infrastructure/official_workspace_manifest.py`
- Create/extend `tests/unit/test_official_project_workspace_service.py` or a separate manifest test if preferred.

Steps:

- Add UTF-8 JSON write/read helpers.
- Ensure manifest writes only under the planned `.connlab` directory.
- Test schema version, key paths, and no accidental write outside workspace.
- Run:

```powershell
py -m pytest tests/unit/test_official_project_workspace_service.py -q
```

Expected:

- Manifest write/read behavior is covered.

### Task 4 - Preview Service

Files:

- Create `backend/application/official_project_workspace_service.py`
- Extend `tests/unit/test_official_project_workspace_service.py`

Steps:

- Add service protocols for project lookup and optional workspace index repository.
- Implement preview:
  - load project,
  - derive DL number,
  - validate configured local root,
  - validate template path,
  - resolve template root,
  - plan local DL workspace path,
  - plan Source Book path,
  - plan official folder path,
  - plan manifest path,
  - detect target conflicts,
  - classify safe existing local DL workspace as `adoptable`,
  - classify planned official folder target existence as `exists`,
  - classify manifest/index/file-system disagreement as `inconsistent`,
  - report public-drive root issues as warnings only,
  - return blockers/warnings/status.
- Use file-system checks through `Path` and temporary directories in tests.
- Run:

```powershell
py -m pytest tests/unit/test_official_project_workspace_service.py -q
```

Expected:

- Missing settings block.
- Missing DL blocks.
- Invalid template blocks.
- Existing target returns `exists`.
- Existing safe local DL workspace returns `adoptable`.
- Manifest/file-system disagreement returns `inconsistent`.
- Missing public-drive root does not block.
- Valid template returns `ready`.

### Task 5 - Create Service

Files:

- Modify `backend/application/official_project_workspace_service.py`
- Extend `tests/unit/test_official_project_workspace_service.py`

Steps:

- Implement create by re-running preview.
- Accept `ready` or `adoptable` preview.
- Reject `blocked`, `exists`, and `inconsistent`.
- Create a ConnLab-owned temporary copy directory under the local DL workspace.
- Copy the resolved template root into the temporary directory.
- Rename the temporary official folder copy to the planned official folder path.
- Create `Source Book` when missing.
- Create `.connlab/manifest.json` after successful final rename.
- Persist SQLite workspace index after successful final rename if included.
- Clean only the ConnLab-owned temporary directory if copy/rename fails.
- Guarantee no overwrite.
- Run:

```powershell
py -m pytest tests/unit/test_official_project_workspace_service.py -q
```

Expected:

- Successful create copies template folders.
- Safe existing local DL workspace can be continued.
- Existing official folder target blocks.
- Failed template copy does not leave a half-created final official folder.
- Manifest is created.
- Original template remains unchanged.

### Task 6 - API Route And Integration Tests

Files:

- Create `backend/api/routes_official_project_workspace.py`
- Modify `backend/api/dependencies.py`
- Modify `backend/api/main.py`
- Create `tests/integration/test_official_project_workspace_api.py`

Steps:

- Add Pydantic response models.
- Add `GET preview`.
- Add `POST create`.
- Map missing project to `404`.
- Map blockers/conflicts to `409` where create is blocked.
- Keep validation messages actionable.
- Run:

```powershell
py -m pytest tests/integration/test_official_project_workspace_api.py -q
```

Expected:

- Preview ready response works.
- Create response works.
- Blocked create returns `409`.
- Missing project returns `404`.

### Task 7 - Frontend API Client

Files:

- Modify `frontend/src/api/client.ts`

Steps:

- Add official workspace types.
- Add `getOfficialWorkspacePreview`.
- Add `createOfficialWorkspace`.
- Ensure errors flow through existing client error handling.
- Run:

```powershell
cd frontend
npm test -- --run officialWorkspace --watch=false
```

Expected:

- New client/selector tests pass once added in the next task. If no test target exists yet, run after Task 8.

### Task 8 - Workbench Selector And Minimal UI

Files:

- Create `frontend/src/features/project-workbench/officialWorkspaceSelectors.ts`
- Create `frontend/src/features/project-workbench/OfficialWorkspaceActionPanel.tsx`
- Modify `frontend/src/features/project-workbench/useProjectWorkbenchSupportModel.ts`
- Modify `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- Modify `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- Modify `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- Modify `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`

Steps:

- Load workspace preview with existing Workbench support-model patterns.
- Keep backend preview separate from Workbench primary-action selection.
- Derive a state where DL number plus active Confirmed Matrix plus no completed workspace shows `Create local project workspace`.
- Render one primary button.
- Put path details in collapsed/secondary diagnostics.
- On click, call create, refresh preview, and show result/error using existing page feedback patterns.
- Avoid adding new mode tabs.
- Avoid showing `Package` for this state.
- Run:

```powershell
cd frontend
npm test -- --run ProjectWorkbench officialWorkspace --watch=false
```

Expected:

- Relevant Workbench tests pass.
- The no-workspace state has one primary action.

### Task 9 - Static UI Copy Guard

Files:

- Modify `tests/unit/test_frontend_shell_files.py`

Steps:

- Add a guard that user-facing Workbench workspace state does not contain:
  - `Package`
  - `.connlab`
  - `manifest`
  - `TASK_316`
  - API route strings
- Run:

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "project_workbench or official_workspace"
```

Expected:

- Static UI copy guard passes.

### Task 10 - Full Validation And Board Update

Files:

- Modify `docs/task_board.md`
- Modify `docs/task_plan_index.md` if status changes are needed

Run:

```powershell
py -m pytest tests/unit/test_official_project_workspace_naming.py tests/unit/test_official_project_workspace_service.py -q
py -m pytest tests/integration/test_official_project_workspace_api.py -q
cd frontend
npm test -- --run ProjectWorkbench officialWorkspace --watch=false
npm run build
cd ..
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "project_workbench or official_workspace"
git diff --check
```

Expected:

- All targeted tests pass.
- Build passes.
- `git diff --check` has no blocking issues.
- Task board records TASK_316 completion only after implementation succeeds.
- Stop after TASK_316. Do not continue to TASK_317.

## Risk Controls

- Folder operations use temporary directories in tests.
- Create re-runs preview before writing.
- No overwrite, no suffix auto-resolution, no silent delete.
- Safe existing top-level DL workspace can be continued instead of blocking real projects.
- Existing official folder target remains blocked until a later explicit repair/adopt task.
- Public drive root is warning-only in TASK_316.
- Template copy uses a ConnLab-owned temporary directory and manifest/index writes happen last.
- Manifest is a cache/portable record, not the only truth source.
- Public drive root is only configured/validated for future use; no public-drive write occurs.
- Workbench UI is constrained to one primary action so the old button-stack problem does not return.

## Review Checklist Mapping

Architecture:

- API route calls application service only.
- UI calls API client only.
- File copy and manifest writing live outside UI.
- Office automation is not touched.

Scope:

- No public drive upload.
- No request material collection.
- No package execution.
- No report/evidence/Step execution scope.

Design:

- Naming planner is pure and tested.
- Settings are explicit.
- Preview and create are separate.
- File system remains final existence authority.

Validation:

- Backend unit tests.
- Backend integration tests.
- Frontend Vitest.
- Frontend static copy guard.
- Build.
- Browser smoke after implementation approval.

## Browser Smoke Checklist After Implementation Approval

Use a project with:

- DL number present,
- active Confirmed Matrix present,
- no local workspace record/folder.

Check:

1. Workbench default surface shows `Create local project workspace`.
2. Only one primary workspace action is visible.
3. Diagnostics are collapsed or visually secondary.
4. Create action creates:
   - `{DL_NUMBER}/`
   - `Source Book/`
   - copied official project folder
   - `.connlab/manifest.json`
5. No public drive upload occurs.
6. No request email or attachment copy occurs.
7. No `Package`, task id, `.connlab`, or manifest copy appears as the operator's workflow language.

Also smoke an existing local DL workspace case:

1. Pre-create `{DL_NUMBER}/` with no official project folder.
2. Confirm preview is adoptable/continuable, not a hard blocker.
3. Confirm create adds missing ConnLab-managed pieces and copies the official folder template.

## Stop Point

Stop now for user review. Do not implement TASK_316 until explicit user approval. After implementation approval and completion, stop again and do not enter TASK_317 automatically.
