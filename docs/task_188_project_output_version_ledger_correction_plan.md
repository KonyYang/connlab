# TASK_188 Correction Plan - Project Output Version Ledger

## 1. Execution Gate

- Current phase: `Phase 11 - Project planning data foundation before downstream document automation`.
- Current active task ID: `TASK_188_PROJECT_OUTPUT_VERSION_LEDGER_CORRECTION`.
- Why this task is allowed now:
  - `docs/task_board.md` states the existing TASK_188 frontend-only freshness display is incomplete for confirmed traceability needs.
  - The next controlled task is this correction, pending user approval.
  - This plan file is the required review artifact before implementation.

Implementation remains blocked until the user explicitly approves this plan.

## 2. Required Read Order Check

Read for this plan:

1. `AGENTS.md` instructions supplied in the conversation.
2. `docs/task_board.md`
3. `tasks/TASK_188_PROJECT_OUTPUT_VERSION_LEDGER_CORRECTION.md`
4. `docs/task_188_project_workbench_version_and_stale_status_plan.md`
5. `docs/matrix_test_plan_data_management_decisions.md`
6. `TASK_EXECUTION_SKILL.md`
7. `TASK_REVIEW_CHECKLIST.md`
8. `docs/02_ARCHITECTURE_RULES.md`
9. `docs/frontend_architecture_rules.md`
10. Existing code around:
    - ProjectTestPlanDraft domain/repository/API
    - Section 2 write-back
    - test record / fee generation
    - approval package preview/execute
    - Project Workbench frontend status selectors/panel

`$impeccable` product context is already loaded in this session and applies to the Workbench UI portion.

## 3. Task Understanding (TASK_EXECUTION_SKILL Step 1)

### 3.1 Goal

Add a minimal persisted Project output version ledger so ConnLab can tell, after reload, whether Section 2, test record, fee evaluation, and approval package outputs are aligned with the active Matrix/TestPlan draft.

The current frontend status panel should remain useful, but its durable truth must come from backend output records rather than browser-session inference.

### 3.2 Inputs

- `Project` identity.
- Active `ProjectTestPlanDraft` identity and version.
- Existing outputs from:
  - Section 2 write-back API result.
  - test record / fee generation API result.
  - approval package execute API result.
- Existing manually supplied output paths where explicitly registered.

### 3.3 Outputs

- Persisted `ProjectOutputRecord` rows.
- Project-scoped output status API response.
- Workbench downstream status read model with `current`, `stale`, `missing`, `manual`, `failed`.
- Updated frontend status panel backed by persisted output status.

### 3.4 Involved Modules

Backend:

- `backend/domain/enums.py`
- `backend/domain/models.py`
- `backend/domain/__init__.py`
- `backend/application/project_output_record_service.py`
- `backend/infrastructure/storage/models.py`
- `backend/infrastructure/storage/repositories/project_output_record.py`
- `backend/infrastructure/storage/repositories/__init__.py`
- `backend/api/routes_project_output_records.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`
- targeted route integration:
  - `backend/api/routes_section2_write_back.py`
  - `backend/api/routes_test_record_fee_document_generation.py`
  - `backend/api/routes_approval_package.py`

Frontend:

- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/projectWorkbenchVersionSelectors.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchDocumentStatusPanel.tsx`

Tests:

- `tests/unit/test_project_output_record_service.py`
- `tests/integration/test_project_output_record_api.py`
- `tests/unit/test_frontend_shell_files.py`

### 3.5 Not Allowed

- No Matrix editing.
- No Matrix freeze UI.
- No record form import.
- No step image/evidence workflow.
- No fee price mapping overhaul.
- No report generation.
- No AI review or historical reuse implementation.
- No direct Office operation outside infrastructure gateways.
- No route-page state expansion in the frontend.

## 4. Current Code Reality

- `ProjectTestPlanDraft` already persists draft snapshots with `draft_id`, `project_id`, `version`, and `status`.
- Section 2 write-back, test record/fee generation, and approval package execution already return enough output information to create ledger records.
- Workbench currently has:
  - `projectWorkbenchVersionSelectors.ts`
  - `ProjectWorkbenchDocumentStatusPanel.tsx`
  - `versionStatus` in `useProjectWorkbenchModel`
- That frontend status is session-derived and cannot survive reload.

## 5. Design Plan (TASK_EXECUTION_SKILL Step 2)

### 5.1 Data Structure Design

Add enums:

```python
class ProjectOutputKind(StrEnum):
    SECTION2_WRITE_BACK = "section2_write_back"
    TEST_RECORD_FORM = "test_record_form"
    FEE_EVALUATION = "fee_evaluation"
    APPROVAL_PACKAGE = "approval_package"

class ProjectOutputStatus(StrEnum):
    MISSING = "missing"
    CURRENT = "current"
    STALE = "stale"
    MANUAL = "manual"
    FAILED = "failed"

class ProjectOutputSource(StrEnum):
    SYSTEM_GENERATED = "system_generated"
    SYSTEM_EXECUTED = "system_executed"
    MANUAL = "manual"
```

Add domain model:

```python
@dataclass(frozen=True, slots=True)
class ProjectOutputRecord:
    output_record_id: str
    project_id: str
    draft_id: str | None
    draft_version: int | None
    output_kind: ProjectOutputKind
    output_path: str | None
    status: ProjectOutputStatus
    source: ProjectOutputSource
    created_at: str
    updated_at: str
    note: str | None = None
```

Database table:

```text
project_output_records
  output_record_id PK
  project_id indexed FK projects.project_id
  draft_id nullable indexed
  draft_version nullable integer
  output_kind indexed
  output_path nullable text/string
  status indexed
  source
  created_at
  updated_at
  note nullable text
```

Do not enforce uniqueness on `project_id + output_kind`; history must be preserved. The read model selects the latest relevant record per kind.

### 5.2 Effective Status Rule

Store the record's explicit `status`, but compute Workbench `effective_status` during reads:

- If there is no record for an output kind: `missing`.
- If latest record status is `manual`: `manual`.
- If latest record status is `failed`: `failed`.
- If latest record has `draft_id/version` different from the active draft: `stale`.
- Otherwise: `current`.

This avoids deleting or overwriting old records and gives reload-safe stale detection.

### 5.3 Active Draft Rule For This Task

Use the same practical active-draft convention as the current Workbench:

- load Project drafts;
- treat the first non-`superseded` draft as active for the current read model;
- expose `active_draft_id` and `active_draft_version` in API response.

TASK_189 may tighten this into a formal Matrix freeze/confirm authority rule.

### 5.4 Application Service Design

Add `ProjectOutputRecordService`.

Core commands:

```python
@dataclass(frozen=True, slots=True)
class RegisterProjectOutputCommand:
    project_id: str
    output_kind: ProjectOutputKind
    output_path: str | None
    status: ProjectOutputStatus
    source: ProjectOutputSource
    draft_id: str | None = None
    note: str | None = None
```

Core service methods:

```python
def register_output(command: RegisterProjectOutputCommand) -> ProjectOutputRecord
def list_records(project_id: str) -> list[ProjectOutputRecord]
def get_workbench_status(project_id: str) -> ProjectOutputStatusSummary
```

Rules:

- Validate `project_id` exists.
- If `draft_id` is supplied, validate it belongs to the same project and copy its `version`.
- Allow `draft_id=None` only for `manual` or `failed` records that have no verified draft lineage.
- Preserve history by creating a new row for each registration.
- Do not mutate Office files.

### 5.5 API Design

Add router:

```text
GET  /api/projects/{project_id}/output-records
GET  /api/projects/{project_id}/output-status
POST /api/projects/{project_id}/output-records
```

`GET /output-records`:

- returns raw history for diagnostics and future audit.

`GET /output-status`:

- returns the Workbench read model:

```json
{
  "project_id": "...",
  "active_draft_id": "...",
  "active_draft_version": 2,
  "items": [
    {
      "output_kind": "test_record_form",
      "status": "stale",
      "output_path": "...",
      "source": "system_generated",
      "draft_id": "...",
      "draft_version": 1,
      "reason": "Output was generated from draft v1; active draft is v2."
    }
  ]
}
```

`POST /output-records`:

- records a manual or system output.
- Useful for manual path registration and tests.
- Existing generation/execute routes should call the service directly after success instead of routing through HTTP.

### 5.6 Existing Route Integration

After successful operation:

- `routes_section2_write_back.py`
  - register `section2_write_back`
  - path = `target_application_form_path`
  - source = `system_executed`
  - status = `current`
  - draft_id = route `draft_id`

- `routes_test_record_fee_document_generation.py`
  - for generated `test_record` item with output path:
    - register `test_record_form`
    - status = `current`
  - for generated `fee_evaluation` item with output path:
    - register `fee_evaluation`
    - status = `current`
  - for skipped/failed item:
    - register `failed` only if the result has enough context to be useful.

- `routes_approval_package.py`
  - on execute success with no blockers:
    - register `approval_package`
    - path = `project_folder_path`
    - source = `system_executed`
    - draft lineage is not currently in the approval-package route.

Approval package draft lineage gap:

- Current approval-package API does not include `draft_id`.
- For TASK_188 correction, keep approval-package output as `manual` or `current-without-draft-lineage` only if a draft cannot be verified.
- Preferred small API addition: optional `draft_id` on approval package request so execution can register lineage.
- This is not Office or workflow expansion; it is traceability metadata.

### 5.7 Frontend Design

Add API types/functions in `frontend/src/api/client.ts`:

```ts
export type ProjectOutputKind = ...
export type ProjectOutputStatus = ...
export type ProjectOutputStatusItem = ...
export type ProjectOutputStatusSummary = ...

export function getProjectOutputStatus(projectId: string): Promise<ProjectOutputStatusSummary>;
export function listProjectOutputRecords(projectId: string): Promise<ProjectOutputRecord[]>;
```

Update `useProjectWorkbenchModel`:

- load output status with the project Workbench data;
- expose durable output status to layout;
- keep existing session-derived selector only as a fallback or as unsaved-input display;
- refresh output status after approval package execute, evidence placement if needed, and any future generation action.

Update `projectWorkbenchVersionSelectors.ts`:

- map backend `ProjectOutputStatusSummary` into the existing `WorkbenchVersionStatus` shape;
- keep labels/reasons in selector/component, not route page.

Update `ProjectWorkbenchDocumentStatusPanel.tsx`:

- show backend-backed status;
- copy should not claim system verification for session-only manual edits.

No new route-page logic.

### 5.8 Dependency Direction

Expected dependency flow:

```text
frontend feature -> frontend api/client -> FastAPI route
api route -> ProjectOutputRecordService
service -> ProjectRepository + ProjectTestPlanDraftRepository + ProjectOutputRecordRepository
repository -> SQLAlchemy model
```

No Office gateway involvement for the ledger itself.

## 6. Risk Controls

1. Approval package currently lacks `draft_id`.
   - Mitigation: add optional traceability-only `draft_id` field or classify unverified approval package output conservatively.

2. Existing frontend status may conflict with backend status.
   - Mitigation: backend status is durable authority; frontend selector can show unsaved manual edits as local hints only.

3. Active draft semantics are not yet formal freeze semantics.
   - Mitigation: use existing non-superseded convention now, and let TASK_189 formalize freeze/confirm.

4. Over-scoping into Matrix editing.
   - Mitigation: ledger only stores output lineage; no group/step editing in this task.

5. Existing databases need new table creation.
   - Mitigation: use existing SQLAlchemy `init_db/create_all` pattern; tests use temp SQLite.

## 7. Validation Plan

Unit tests:

```powershell
py -m pytest tests\unit\test_project_output_record_service.py -q
```

Integration tests:

```powershell
py -m pytest tests\integration\test_project_output_record_api.py -q
```

Targeted related backend regression:

```powershell
py -m pytest tests\integration\test_section2_write_back_api.py tests\integration\test_test_record_fee_document_generation_api.py tests\integration\test_approval_package_api.py -q
```

Frontend:

```powershell
cd frontend
npm run build
```

Frontend static guard:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix or approval"
```

Task-board guard:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

Manual smoke after implementation:

1. Open Workbench for a project with active Matrix draft and no outputs.
   - Expected: output status shows missing.
2. Execute Section 2 write-back or document generation.
   - Expected: output status shows current after reload.
3. Create or select a newer active draft in test data.
   - Expected: older output shows stale.
4. Register a manual output record.
   - Expected: output status shows manual and does not claim verified lineage.

## 8. Acceptance Criteria

- Output records are persisted in SQLite.
- Workbench output status survives page reload/app restart.
- Current/stale detection is based on active draft identity/version.
- Existing frontend downstream status panel consumes backend-backed status.
- Existing document/write/approval routes record ledger entries after successful outputs.
- Manual/unverified paths are not falsely treated as system-generated current outputs.
- No Matrix editing, record import, image workflow, fee pricing overhaul, report generation, AI review, or multi-user scope is implemented.

## 9. Review Checklist

Before implementation approval, confirm:

- Approval package request may receive optional `draft_id` for lineage.
- `ProjectOutputRecord` history should append new records rather than update in place.
- Effective stale status may be computed at read time even if stored row remains `current`.
- TASK_189 remains blocked until this correction is implemented or explicitly deferred.

## 10. Stop Condition

Stop after this plan is reviewed.

Do not implement code until the user explicitly approves `TASK_188_PROJECT_OUTPUT_VERSION_LEDGER_CORRECTION`.
