# TASK_345B Project Lifecycle Activation Model API - Developer Evidence

Date: 2026-06-28
Role: Developer
Task: `TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API`
Lane: `project-lifecycle-activation-model-api`
Status: ready_for_review
Implementation approved: yes
Product code changed: yes - backend/API/audit/tests only

## Current Phase / Task / Permission

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current task/lane: `TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API` / `project-lifecycle-activation-model-api`
- Allowed reason: user explicitly approved Developer planning-first after Reviewer plan gate pass in the Orchestrator delegation.
- Board note: `docs/task_board.md` still described TASK_345B as planned for Reviewer plan gate during this pass. This Developer pass follows the newer Orchestrator/User delegation and records the board mismatch as external state. The board was not modified.

## Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT.md`
- `docs/task_345a_project_lifecycle_business_model_contract_plan.md`
- `docs/lane_evidence/TASK_345A_project-lifecycle-business-model-contract_planner.md`
- `tasks/TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API.md`
- `docs/task_345b_project_lifecycle_activation_model_api_plan.md`
- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_planner.md`
- `docs/lane_evidence/DISCOVERY_project-lifecycle-business-model-rework_planner.md`
- Existing backend lifecycle files and tests by read-only inspection:
  - `backend/domain/enums.py`
  - `backend/domain/models.py`
  - `backend/application/project_lifecycle_state_service.py`
  - `backend/application/project_lifecycle_write_guard.py`
  - `backend/api/routes_project.py`
  - `backend/api/lifecycle_errors.py`
  - `backend/infrastructure/storage/database.py`
  - `backend/infrastructure/storage/models.py`
  - `backend/infrastructure/storage/repositories/project.py`
  - `backend/infrastructure/storage/repositories/project_lifecycle_event.py`
  - `tests/unit/test_project_lifecycle_state_service.py`
  - `tests/integration/test_project_lifecycle_api.py`
  - `tests/integration/test_project_lifecycle_migration.py`

## Planning Findings

Developer read-only inspection confirmed the Planner facts:

- Current domain enums are `ProjectLifecycleState = active | stopped | closed`, `ProjectClosureType = completed | administrative`, and event types `stop | resume | close_completed | close_administrative`.
- Current service rejects resume from closed projects.
- Current API has split close routes: `close-completed` and `close-administrative`.
- Current completed close requires `close_note`, `manual_completion_confirmed`, and `output_summary_acknowledged`.
- Current `projects` table has `closure_type` and `closed_reason`, but no separate business close reason category.
- Current `project_lifecycle_events` table has metadata JSON, enough for close/activate audit payloads without a new audit table.
- Current migration backfills legacy `status='closed'` rows to `closure_type='administrative'`.
- Current write guard still exposes closed completed/admin readonly messages and no closed allowed actions. TASK_345B should avoid full write guard behavior changes; TASK_345C owns that lane.

## Plan Refinement Summary

Updated `docs/task_345b_project_lifecycle_activation_model_api_plan.md` to make the future implementation strategy concrete:

- Add unified `POST /api/projects/{project_id}/lifecycle/close`.
- Keep existing split close routes as compatibility wrappers only.
- Add business close reason category values: `completed`, `failed`, `cancelled`, `cannot_test`, `duplicate`, `other`.
- Add persisted close reason category migration/backfill strategy.
- Keep `ProjectClosureType` as legacy/internal compatibility until a later cleanup lane, but do not expose `administrative` as business meaning.
- Add `POST /api/projects/{project_id}/lifecycle/activate`.
- Require activation reason/note in v1.
- Allow activate from stopped and closed when previous project status is recoverable.
- Return structured conflict rather than guessing when a legacy closed row lacks recoverable previous project status.
- Use `project_lifecycle_events.metadata_json` for close/activate audit metadata instead of adding a new event table.
- Add `close` and `activate` event types while preserving old event types for history compatibility.
- Define focused unit/API/migration test coverage.
- Define exact future implementation file list.

## Future Implementation File List

Candidate future files after Reviewer implementation-readiness and explicit implementation routing:

- `backend/domain/enums.py`
- `backend/domain/models.py`
- `backend/domain/__init__.py`
- `backend/application/project_lifecycle_state_service.py`
- `backend/api/routes_project.py`
- `backend/api/dependencies.py`
- `backend/api/lifecycle_errors.py`
- `backend/infrastructure/storage/database.py`
- `backend/infrastructure/storage/models.py`
- `backend/infrastructure/storage/repositories/project.py`
- `backend/infrastructure/storage/repositories/project_lifecycle_event.py`
- `tests/unit/test_project_lifecycle_state_service.py`
- `tests/integration/test_project_lifecycle_api.py`
- `tests/integration/test_project_lifecycle_migration.py`
- `tests/integration/test_project_registry_summary_api.py`
- `tests/unit/test_project_lifecycle_write_guard.py` only for baseline assertions that must remain unchanged until TASK_345C.

## Scope Locks Confirmed

This planning pass did not modify and does not authorize:

- backend/API/schema/test implementation code;
- frontend runtime, `frontend/src/api/client.ts`, Workbench, Projects registry, or CSS;
- public-drive LTR workbook authority write behavior;
- TASK_345C write guard implementation;
- TASK_345D/E/F/G/H implementation;
- Matrix, Fee, Folder, Basic Information, Required Forms, Approval Package, Public Drive business logic;
- StepInstance, Report generation, AI, permissions, LAN/server, multi-user scope;
- `docs/task_board.md`;
- governance/orchestration residuals.

## Dirty Workspace Classification

Targeted status checks during this planning pass are expected to show existing dirty frontend/governance residuals from prior lanes, including Workbench files and `docs/task_board.md`. These are outside TASK_345B Developer planning-first and were not modified, routed, or packaged by this pass.

## Files Changed In This Pass

- `docs/task_345b_project_lifecycle_activation_model_api_plan.md`
- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_developer.md`

No product implementation files were changed.

## Validation Results

- Required docs exist: all required governance, TASK_345A, TASK_345B, discovery, plan, and evidence files returned `True`.
- `git diff --check -- docs/task_345b_project_lifecycle_activation_model_api_plan.md docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_developer.md`: passed, with only the existing LF/CRLF normalization warning on the plan file.
- Trailing whitespace scan for TASK_345B plan/evidence: no matches.
- Targeted status check for `backend`, `frontend`, `tests`, `frontend/src/api/client.ts`, `docs/task_board.md`, and TASK_345B plan/evidence showed only:
  - `M docs/task_345b_project_lifecycle_activation_model_api_plan.md`
  - `?? docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_developer.md`
- No backend/frontend/tests product implementation files were changed by this planning-first pass.

## Recommended Next Gate

Reviewer implementation-readiness gate.

## Stop Point

Stop after Developer planning-first evidence and validation. Do not implement backend/API/schema/tests/frontend product code, do not update `docs/task_board.md`, and do not route implementation directly from this Developer thread.

## Implementation Pass Legality Check - Blocked

Date: 2026-06-28
Role: Developer implementation gate checker
Status: blocked - missing repository evidence for implementation authorization

The Orchestrator delegation stated that Reviewer implementation-readiness passed and the user approved implementation. Before editing product code, this Developer pass re-read the board and TASK_345B evidence as required.

Blocking facts from repository evidence:

- `docs/task_board.md` still states that `TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API` is planned and ready for Reviewer plan gate only, with no active implementation lane and no Developer implementation approval.
- `tasks/TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API.md` still identifies the task as a planning-first backend/API contract draft, not approved for implementation.
- This Developer evidence still had status `developer planning-first complete - pending Reviewer implementation-readiness gate`.
- `docs/lane_evidence` contains TASK_345B Planner and Developer evidence only; no TASK_345B Reviewer implementation-readiness evidence file was present during the targeted file search.

Decision:

- Do not implement backend/API/schema/tests product code from this pass.
- Do not update `docs/task_board.md`.
- Return to Orchestrator/Reviewer/Planner to reconcile the missing Reviewer readiness evidence and board state.

Validation:

- Read required governance, task, plan, Planner evidence, Developer evidence, and TASK_345A/discovery inputs.
- Searched TASK_345B evidence paths and current board for Reviewer readiness status.
- Product code was not edited.

Recommended next role:

Reviewer implementation-readiness gate or Planner/Integrator board/evidence reconciliation.

## Developer Implementation Pass

Date: 2026-06-28
Role: Developer implementation
Status: ready_for_review

### Authorization Re-Check

- `docs/task_board.md` now records `TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API` as implementation authorized.
- `tasks/TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API.md` now records Developer implementation authorization and the exact May Touch list.
- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_reconciliation_planner.md` records the source-of-truth reconciliation for the missing Reviewer readiness checkpoint.
- This pass stayed inside the backend/API/audit/test/evidence scope.

### Implementation Summary

- Added business close reason category support with values `completed`, `failed`, `cancelled`, `cannot_test`, `duplicate`, and `other`.
- Added persisted project-level `close_reason_category` and SQLite migration/backfill:
  - legacy completed rows -> `completed`;
  - legacy administrative/unknown closed rows -> `other`;
  - active/stopped rows remain unset.
- Added unified backend lifecycle close command and `POST /api/projects/{project_id}/lifecycle/close`.
- Kept existing `close-completed` and `close-administrative` routes as compatibility wrappers over unified close.
- Added `POST /api/projects/{project_id}/lifecycle/activate`.
- Activation requires a non-empty reason and restores prior active project status from lifecycle event metadata.
- Closed projects now expose lifecycle `allowed_actions=["activate"]`; stopped projects expose `activate` while retaining `resume` compatibility until later frontend/write-guard lanes.
- Lifecycle API responses expose `close_reason_category` and `close_reason_label`; API response mapping no longer exposes `administrative` as a lifecycle close business value.
- Added `close` and `activate` lifecycle event types while preserving old event types for read compatibility.
- Close/activate event metadata records previous project status, previous close category/note/type, restored status, operator, timestamp, and compatibility route metadata where applicable.
- Preserved TASK_345C boundary: write guard implementation was not changed.

### Files Changed By This Implementation Pass

- `backend/domain/enums.py`
- `backend/domain/models.py`
- `backend/domain/__init__.py`
- `backend/application/project_lifecycle_state_service.py`
- `backend/api/routes_project.py`
- `backend/infrastructure/storage/database.py`
- `backend/infrastructure/storage/models.py`
- `backend/infrastructure/storage/repositories/project.py`
- `tests/unit/test_project_lifecycle_state_service.py`
- `tests/integration/test_project_lifecycle_api.py`
- `tests/integration/test_project_lifecycle_migration.py`
- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_developer.md`

Not changed in this pass:

- `frontend/`
- `frontend/src/api/client.ts`
- Projects registry implementation
- public-drive LTR workbook authority or Office gateways
- TASK_345C write guard implementation
- TASK_345D/E/F/G/H
- StepInstance, Report, AI, permissions, LAN/server, multi-user scope

Pre-existing reconciliation/source-of-truth changes in `docs/task_board.md`, `tasks/TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API.md`, `docs/task_345b_project_lifecycle_activation_model_api_plan.md`, and `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_reconciliation_planner.md` were Planner reconciliation inputs, not product implementation changes from this pass.

### Validation Results

- `py -m pytest tests\unit\test_project_lifecycle_state_service.py tests\integration\test_project_lifecycle_migration.py tests\integration\test_project_lifecycle_api.py -q` -> `13 passed`.
- `py -m pytest tests\unit\test_project_lifecycle_state_service.py tests\integration\test_project_lifecycle_migration.py tests\integration\test_project_lifecycle_api.py tests\integration\test_project_registry_summary_api.py tests\unit\test_project_lifecycle_write_guard.py -q` -> `26 passed`.

- `git diff --check -- backend/domain/enums.py backend/domain/models.py backend/domain/__init__.py backend/application/project_lifecycle_state_service.py backend/api/routes_project.py backend/infrastructure/storage/database.py backend/infrastructure/storage/models.py backend/infrastructure/storage/repositories/project.py tests/unit/test_project_lifecycle_state_service.py tests/integration/test_project_lifecycle_api.py tests/integration/test_project_lifecycle_migration.py docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_developer.md` -> passed with LF/CRLF normalization warnings only.
- Trailing whitespace scan for TASK_345B package files -> no matches.
- Targeted forbidden-scope status check showed no `frontend/`, `frontend/src/api/client.ts`, public-drive/LTR authority, Projects registry, or future-scope implementation changes from this pass.
- Targeted status still shows pre-existing Planner reconciliation/source-of-truth changes in `docs/task_board.md`, `tasks/TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API.md`, `docs/task_345b_project_lifecycle_activation_model_api_plan.md`, and `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_reconciliation_planner.md`; those are not product implementation changes from this Developer pass.

### Known Residuals / Follow-Ups

- TASK_345C still owns lifecycle write guard behavior/copy changes. Closed write guards still block business writes using the existing readonly guard behavior until TASK_345C updates the guard contract.
- Frontend API client and UI are intentionally unchanged; TASK_345D/E/F own Workbench/registry/client-facing UX follow-up.
- `close-completed` and `close-administrative` remain compatibility routes, but new product code should prefer unified close.
- `closure_type` remains a legacy compatibility field in storage/domain; business close reason is now `close_reason_category`.

### Stop Point

Stop after final validation, evidence update, and Orchestrator callback. Do not implement TASK_345C, frontend UI/API client, Projects registry, public-drive LTR authority, or future scope from this Developer thread.

## Integrator Packaging Checkpoint

Date: 2026-06-28
Role: Integrator
Status: integrator_accepted

### Package Decision

TASK_345B is accepted for local controlled packaging after Reviewer implementation gate pass and Integrator validation.

### Package Scope

Included scope:

- Approved TASK_345B backend/API/audit/model/migration files.
- Focused TASK_345B backend unit/API/migration tests.
- TASK_345B task, plan, Developer evidence, Planner evidence, reconciliation evidence, and `docs/task_board.md` closeout.

Excluded scope:

- Frontend runtime files and `frontend/src/api/client.ts`.
- Projects registry.
- Public-drive LTR workbook authority and Office gateway writes.
- TASK_345C write guard implementation beyond existing baseline assertions.
- TASK_345D/E/F/G/H implementation.
- StepInstance, Report generation, AI, permissions, LAN/server, and multi-user scope.
- Unrelated governance/orchestration residuals.

### QA Decision

QA is not required for this package because the accepted surface is backend/API/migration/audit behavior and is covered by focused unit/API/migration/registry/write-guard regression. Frontend/UX smoke belongs to downstream TASK_345C+ lanes after their UI/API-client contracts are approved.

### Integrator Validation

Integrator rerun:

- `py -m pytest tests\unit\test_project_lifecycle_state_service.py tests\integration\test_project_lifecycle_migration.py tests\integration\test_project_lifecycle_api.py tests\integration\test_project_registry_summary_api.py tests\unit\test_project_lifecycle_write_guard.py -q`
- Result: `26 passed`.

Package validation:

- `git diff --cached --check` passed with LF/CRLF normalization warnings only.
- Staged forbidden-path checks passed: no frontend runtime, `frontend/src/api/client.ts`, Projects registry, public-drive LTR authority, TASK_345C+ future-scope, `AGENTS.md`, `.agents/`, or `docs/project_management/` paths were staged.

### Stop Point

Stop after local controlled TASK_345B commit and Orchestrator callback. Do not push remote and do not start TASK_345C from this Integrator thread.
