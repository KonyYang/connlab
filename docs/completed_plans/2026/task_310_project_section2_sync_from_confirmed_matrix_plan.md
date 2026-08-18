# TASK_310 Project Section 2 Sync From Confirmed Matrix Plan

> For agentic workers: REQUIRED SUB-SKILL: Use test-driven development when implementing this plan.

Status: Complete.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_310_PROJECT_SECTION2_SYNC_FROM_CONFIRMED_MATRIX`, complete.

Allowed reason: `docs/task_board.md` says TASK_310 was approved and is now complete. This document records the executable plan used for implementation.

## Goal

Add an explicit Workbench action that syncs active Confirmed Matrix schedule dates into structured Application Form Section 2 fields.

## Architecture

TASK_310 is an application-service-first sync task with a thin API route and a compact Workbench entry. The backend reads active Confirmed Matrix authority data and updates structured Application Form data only. It does not write Word files, register output records, publish to public drive, or generate package artifacts.

## Mandatory Preconditions

Before implementation:

1. Read `AGENTS.md`.
2. Read `docs/task_board.md`.
3. Read `tasks/TASK_310_PROJECT_SECTION2_SYNC_FROM_CONFIRMED_MATRIX.md`.
4. Load `$impeccable`.
5. Read `docs/02_ARCHITECTURE_RULES.md`.
6. Read `docs/frontend_architecture_rules.md`.
7. Read `docs/project_management/TASK_EXECUTION_SKILL.md`.
8. Re-read this executable plan.
9. Confirm explicit user approval for implementation.

## Task Understanding

Goal:

- Copy schedule dates from the active Confirmed Matrix authority version into structured Application Form Section 2 date fields.

Inputs:

- `project_id`
- Active Confirmed Matrix authority version:
  - `sample_received_date`
  - `estimated_completion_date`
- Current project Application Form record:
  - `received_date`
  - `estimated_completion_date`

Outputs:

- Preview response showing source values, target values, and field-level sync status.
- Sync response showing changed, unchanged, skipped, and blocked fields.
- Updated structured Application Form record when sync is executed and source values are valid.

Not allowed:

- No Word `.docx` mutation.
- No `Section2WriteBackService.write_back(...)` call.
- No Office gateway call.
- No `ProjectOutputRecord`.
- No Customer Feedback generation.
- No package orchestrator.
- No public-drive publish.
- No Matrix or Fee authority mutation.

## Current Code Context

Relevant backend files:

- `backend/domain/confirmed_matrix_authority_models.py`
  - `ConfirmedMatrixVersion.sample_received_date`
  - `ConfirmedMatrixVersion.estimated_completion_date`
- `backend/infrastructure/storage/repositories/confirmed_matrix_authority.py`
  - `get_active_by_project(project_id)`
- `backend/domain/models.py`
  - `ApplicationForm.received_date`
  - `ApplicationForm.estimated_completion_date`
- `backend/infrastructure/storage/repositories/intake.py`
  - `ApplicationFormRepository.list_by_project(project_id)`
  - `ApplicationFormRepository.update(form)`
- `backend/application/section2_completion_preview_service.py`
  - existing preview logic, not the write target for TASK_310
- `backend/application/section2_write_back_service.py`
  - existing Word write-back logic, explicitly out of scope for TASK_310
- `backend/api/dependencies.py`
  - dependency wiring pattern for repositories/services
- `backend/api/main.py`
  - API router registration

Relevant frontend files:

- `frontend/src/api/client.ts`
  - typed API client layer
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
  - Workbench state and API orchestration
- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
  - Workbench model selector used by layout
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - Workbench composition
- `frontend/src/features/project-workbench/workbench.css`
  - Workbench styling
- `tests/unit/test_frontend_shell_files.py`
  - static boundary tests

## Data Model Design

Add a small application-level model set in a new service module.

Suggested file:

- Create `backend/application/project_section2_sync_service.py`

Suggested dataclasses:

```python
@dataclass(frozen=True, slots=True)
class ProjectSection2SyncCommand:
    project_id: str
    expected_confirmed_matrix_id: str | None = None
    expected_confirmed_revision: int | None = None
    operator: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectSection2FieldSync:
    field_key: Literal["received_date", "estimated_completion_date"]
    source_field_key: Literal["sample_received_date", "estimated_completion_date"]
    source_value: str | None
    current_value: str | None
    next_value: str | None
    status: Literal[
        "will_change",
        "changed",
        "unchanged",
        "skipped_missing_source",
        "blocked_invalid_source",
    ]
    message: str


@dataclass(frozen=True, slots=True)
class ProjectSection2SyncResult:
    project_id: str
    application_form_id: str
    confirmed_matrix_id: str
    confirmed_revision: int
    fields: tuple[ProjectSection2FieldSync, ...]
    status: Literal["ready", "up_to_date", "partial", "blocked", "synced"]
    synced_at: str | None = None
    operator: str | None = None
```

Port protocols:

```python
class Section2SyncConfirmedMatrixStore(Protocol):
    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        ...


class Section2SyncApplicationFormStore(Protocol):
    def list_by_project(self, project_id: str) -> list[ApplicationForm]:
        ...

    def update(self, form: ApplicationForm) -> ApplicationForm:
        ...
```

## Backend Service Behavior

Create `ProjectSection2SyncService` with:

- `preview(command: ProjectSection2SyncCommand) -> ProjectSection2SyncResult`
- `sync(command: ProjectSection2SyncCommand) -> ProjectSection2SyncResult`

Source lookup:

1. Load active Confirmed Matrix through `get_active_by_project(project_id)`.
2. If missing, raise `ProjectSection2SyncNotFoundError("Confirm Matrix authority before syncing Section 2 dates.")`.

Target lookup:

1. Load `ApplicationFormRepository.list_by_project(project_id)`.
2. If none, raise `ProjectSection2SyncNotFoundError("Application Form is required before syncing Section 2 dates.")`.
3. If exactly one Application Form exists, use it.
4. If multiple Application Forms exist, do not use repository order or `form_id` as a proxy for latest/current. Use an existing selected-form business rule only if implementation can prove it is already the project-level current Application Form and add a test for that branch. If no such existing rule is available, raise `ProjectSection2SyncAmbiguousTargetError("Multiple Application Forms exist. Select the current Application Form before syncing Section 2 dates.")`.
5. Do not invent a new target-selection table, new selection workflow, or timestamp heuristic in TASK_310.

Field mapping:

- `sample_received_date` -> `received_date`
- `estimated_completion_date` -> `estimated_completion_date`

Date validation:

- Accept ISO `YYYY-MM-DD`.
- Use `datetime.date.fromisoformat(value.strip())` for validation.
- Store normalized ISO date strings.
- Empty source values are skipped and do not clear target values.
- Invalid source values block sync and no target mutation occurs.

Preview:

- Does not mutate.
- Returns `will_change`, `unchanged`, `skipped_missing_source`, or `blocked_invalid_source`.

Sync:

- Calls preview first.
- Requires `expected_confirmed_matrix_id` and `expected_confirmed_revision`.
- If the current active Confirmed Matrix identity does not match the expected values, raise `ProjectSection2SyncConflictError` before mutation.
- If any field is `blocked_invalid_source`, raise `ProjectSection2SyncError` before mutation.
- Update only fields whose preview status is `will_change`.
- Return `changed` for fields updated during this call, plus unchanged/skipped summaries.

Transaction:

- The API dependency session commit/rollback remains owned by existing `get_session()` behavior.
- The service should call repository `update(...)`; it should not commit directly unless current dependency patterns require it.

## API Design

Create:

- `backend/api/routes_project_section2_sync.py`

Endpoints:

- `GET /api/projects/{project_id}/section2-sync/preview`
- `POST /api/projects/{project_id}/section2-sync`

POST request DTO:

```python
class ProjectSection2SyncRequest(BaseModel):
    expected_confirmed_matrix_id: str = Field(min_length=1)
    expected_confirmed_revision: int = Field(ge=1)
    operator: str | None = None
```

Response DTO:

```python
class ProjectSection2FieldSyncResponse(BaseModel):
    field_key: Literal["received_date", "estimated_completion_date"]
    source_field_key: Literal["sample_received_date", "estimated_completion_date"]
    source_value: str | None
    current_value: str | None
    next_value: str | None
    status: Literal[
        "will_change",
        "changed",
        "unchanged",
        "skipped_missing_source",
        "blocked_invalid_source",
    ]
    message: str


class ProjectSection2SyncResponse(BaseModel):
    project_id: str
    application_form_id: str
    confirmed_matrix_id: str
    confirmed_revision: int
    status: Literal["ready", "up_to_date", "partial", "blocked", "synced"]
    fields: list[ProjectSection2FieldSyncResponse]
    synced_at: str | None = None
    operator: str | None = None
```

Dependency wiring:

- Add `get_project_section2_sync_service(...)` to `backend/api/dependencies.py`.
- Register the router in `backend/api/main.py`.

Error mapping:

- Project id not found: HTTP 404.
- Missing active Confirmed Matrix: HTTP 409 readiness blocker with actionable detail.
- Missing Application Form: HTTP 409 readiness blocker with actionable detail.
- Ambiguous Application Form target: HTTP 409 readiness blocker with actionable detail.
- Expected Confirmed Matrix id/revision mismatch: HTTP 409 conflict with actionable detail telling the operator to refresh preview.
- Invalid source date: HTTP 422 with field-level detail.

## Frontend Design

API client:

- Modify `frontend/src/api/client.ts`.
- Add typed response and functions:

```ts
export type ProjectSection2SyncFieldStatus =
  | "will_change"
  | "changed"
  | "unchanged"
  | "skipped_missing_source"
  | "blocked_invalid_source";

export type ProjectSection2SyncStatus =
  | "ready"
  | "up_to_date"
  | "partial"
  | "blocked"
  | "synced";

export type ProjectSection2SyncField = {
  field_key: "received_date" | "estimated_completion_date";
  source_field_key: "sample_received_date" | "estimated_completion_date";
  source_value?: string | null;
  current_value?: string | null;
  next_value?: string | null;
  status: ProjectSection2SyncFieldStatus;
  message: string;
};

export type ProjectSection2SyncResponse = {
  project_id: string;
  application_form_id: string;
  confirmed_matrix_id: string;
  confirmed_revision: number;
  status: ProjectSection2SyncStatus;
  fields: ProjectSection2SyncField[];
  synced_at?: string | null;
  operator?: string | null;
};

export type ProjectSection2SyncRequest = {
  expected_confirmed_matrix_id: string;
  expected_confirmed_revision: number;
  operator?: string | null;
};
```

Functions:

- `fetchProjectSection2SyncPreview(projectId: string)`
- `syncProjectSection2FromConfirmedMatrix(projectId: string, input: ProjectSection2SyncRequest)`

Workbench model:

- Prefer adding the API orchestration to `useProjectWorkbenchModel.ts`.
- Expose a compact state object through `useProjectRuntimeConsoleModel.ts` only if `ProjectWorkbenchLayout` needs it.
- State should include:
  - preview response
  - loading/syncing flags
  - error copy
  - `onRefreshSection2Sync`
  - `onSyncSection2`

UI component:

- Create `frontend/src/features/project-workbench/ProjectSection2SyncPanel.tsx` if it keeps `ProjectWorkbenchLayout.tsx` small.
- Render in `ProjectWorkbenchLayout` near project preparation/readiness surfaces, after project folder panel or near downstream output readiness.
- Keep it compact and full-width, not in the selected-step side column.

Suggested copy:

- Title: `Section 2 dates`
- Up to date: `Section 2 dates match Confirmed Matrix.`
- Ready: `Confirmed Matrix has newer Section 2 dates.`
- Partial: `One Confirmed Matrix date is missing. Available dates can still sync.`
- Blocked: `Confirm Matrix authority before syncing Section 2 dates.`
- Action: `Sync Section 2 dates`
- Helper: `Updates structured Section 2 dates only. Word write-back remains a separate controlled step.`

UI must not show a Customer Feedback, package execute, public-drive publish, Test Record, or Fee Form action as part of this task.

## Testing Plan

### Backend Unit Tests

Create `tests/unit/test_project_section2_sync_service.py`.

Cover:

1. Preview reports `will_change` for different valid source dates.
2. Sync updates `ApplicationForm.received_date` and `ApplicationForm.estimated_completion_date`.
3. Preview reports `unchanged` when target already matches source.
4. Empty source values are `skipped_missing_source` and do not clear target values.
5. Invalid source date blocks sync and no update occurs.
6. Missing active Confirmed Matrix raises not-found/readiness error.
7. Missing Application Form raises not-found/readiness error.
8. Multiple Application Forms without existing selected-form semantics raises ambiguous-target readiness error.
9. Expected Confirmed Matrix id/revision mismatch raises conflict and no update occurs.

### Backend API Tests

Create `tests/integration/test_project_section2_sync_api.py`.

Cover:

1. `GET /section2-sync/preview` returns source and target field status.
2. `POST /section2-sync` updates structured Application Form dates when expected Confirmed Matrix id/revision match the preview.
3. No active Confirmed Matrix returns actionable blocker.
4. Multiple Application Forms without existing selected-form semantics returns 409 and leaves all forms unchanged.
5. Expected Confirmed Matrix id/revision mismatch returns 409 and leaves Application Form unchanged.
6. Invalid source date returns 422 and leaves Application Form unchanged.

### Frontend Tests

Update or add tests near Project Workbench:

- `frontend/src/features/project-workbench/ProjectSection2SyncPanel.test.tsx`
- Existing `ProjectWorkbench` tests if model/layout wiring is simpler there.

Cover:

1. Shows `Section 2 dates` state.
2. Shows changed fields when preview has `will_change`.
3. Sync button calls `syncProjectSection2FromConfirmedMatrix(...)`.
4. Successful sync refreshes/replaces displayed state.
5. Blocker copy is shown when no active Confirmed Matrix exists.
6. Sync sends the previewed `confirmed_matrix_id` and `confirmed_revision` as expected identity.

### Static Shell Tests

Update `tests/unit/test_frontend_shell_files.py`.

Assert:

- API client exports section2 sync types/functions.
- `ProjectWorkbenchLayout` imports/renders the section2 sync panel or equivalent named component.
- TASK_310 does not introduce `CustomerFeedback`, `PackageOrchestrator`, `ProjectWorkbenchEvidencePanel`, `TestRecordDraftGenerationButton`, or Fee Form action imports in the new section2 sync component.

## Validation Commands

Backend:

```powershell
py -m pytest tests/unit/test_project_section2_sync_service.py tests/integration/test_project_section2_sync_api.py -q
```

Frontend:

```powershell
cd frontend
npm test -- --run ProjectWorkbench --watch=false
npm run build
```

Static / regression:

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "project_workbench or section2"
git diff --check
```

Optional broader regression after implementation if changes touch shared repositories or Workbench model:

```powershell
py -m pytest tests/unit/test_section2_completion_preview_service.py tests/unit/test_section2_write_back_service.py tests/integration/test_section2_completion_preview_api.py tests/integration/test_section2_write_back_api.py -q
```

## Risks And Guards

- Target Application Form ambiguity: if current code has multiple forms and no clear selected target, implementation must return a 409 readiness blocker. Do not infer from repository order, `form_id`, filename, or upload time, and do not add new persistence just to select a target in TASK_310.
- Preview/sync drift: POST must carry the previewed Confirmed Matrix id/revision. If active authority changes between preview and sync, reject and ask the operator to refresh.
- Word file confusion: this task updates structured Application Form data only. User-facing copy and tests must not imply the Word application form has been written.
- Hidden side effects: Confirm Matrix, Confirm Fee, folder generation, and package preview must not call this sync implicitly.
- Date parsing: normalize only valid ISO dates. Do not infer locale-specific dates.
- UI crowding: keep the Workbench entry compact and avoid adding another large card that competes with Matrix workspace.

## Implementation Checklist

- [ ] Add backend service tests first.
- [ ] Implement `ProjectSection2SyncService`.
- [ ] Add API route tests.
- [ ] Implement route, DTOs, dependency, and router registration.
- [ ] Add frontend API client types/functions.
- [ ] Add Workbench UI/component tests.
- [ ] Wire compact Workbench section2 sync entry.
- [ ] Add static shell boundary tests.
- [ ] Run validation commands.
- [ ] Update `docs/task_board.md` to mark TASK_310 complete only after implementation validation.

## Stop Point

After TASK_310 implementation and validation, stop. TASK_311 Customer Feedback Form generation requires its own task file, executable plan, and explicit approval.
