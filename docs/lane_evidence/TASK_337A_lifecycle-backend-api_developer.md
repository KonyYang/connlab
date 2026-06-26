# Developer Evidence - TASK_337A Lifecycle Backend API

Status: complete
Task: TASK_337A_PROJECT_LIFECYCLE_BACKEND_API_SHAPE
Lane: lifecycle-backend-api
Role: Developer
Last Updated: 2026-06-27

## Approval

The user approved changing the sequence on 2026-06-26 so TASK_337A runs before TASK_338.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

## Why This Lane Is Allowed

TASK_336 contract is complete and accepted.

TASK_337B guard inventory is complete.

TASK_338 write guard integration needs a stable backend lifecycle/API shape before implementation.

## Goal

Plan and then, after explicit user approval, implement backend lifecycle/API shape for Stop, Resume, Close completed, and Close administrative.

## May Touch

Planner activation may touch:

- `tasks/TASK_337A_PROJECT_LIFECYCLE_BACKEND_API_SHAPE.md`
- `docs/task_board.md`
- `docs/lane_evidence/TASK_337A_lifecycle-backend-api_developer.md`
- `tasks/TASK_338_PROJECT_LIFECYCLE_WRITE_GUARD_INTEGRATION.md`
- `docs/lane_evidence/TASK_338_write-guard-integration_developer.md`

Developer planning may touch:

- `docs/task_337a_project_lifecycle_backend_api_shape_plan.md`
- `docs/lane_evidence/TASK_337A_lifecycle-backend-api_developer.md`

Developer implementation may touch only files explicitly listed in the user-approved TASK_337A implementation plan.

## Must Not Touch

- product implementation code before plan approval
- frontend UI
- broad write guard integration from TASK_338
- Workbench shell implementation
- Projects registry implementation
- Office gateway internals
- StepInstance, Report generation, AI, permissions, LAN/server, multi-user scope

## Locked Paths

- `tasks/TASK_337A_PROJECT_LIFECYCLE_BACKEND_API_SHAPE.md`
- `docs/task_337a_project_lifecycle_backend_api_shape_plan.md`
- `docs/lane_evidence/TASK_337A_lifecycle-backend-api_developer.md`
- product files explicitly listed in the approved TASK_337A implementation plan

## Validation Gate

- Plan file exists and is user-approved before product code changes.
- Lifecycle status/API shape is explicit.
- Compatibility with current `cancelled` behavior is explicit.
- Stop/Resume/Close DTOs and tests are defined.
- TASK_338 write guard work remains deferred.

## Merge Gate

Reviewer and Integrator gates are required. TASK_338 remains blocked until TASK_337A is implemented, reviewed, and accepted.

## Commands Or Checks Run

Planner activation:

- Read current `docs/task_board.md`.
- Read TASK_336 contract plan.
- Read TASK_337B guard inventory/test matrix.
- Read TASK_338 task/evidence.
- Created TASK_337A task/evidence.
- Marked TASK_338 as `approved_blocked`.
- Updated `docs/task_board.md` so TASK_337A is the active approved planning-first lane.
- Verified TASK_337A task/evidence files exist.
- Verified board contains `lifecycle-backend-api` as approved and `write-guard-integration` as `approved_blocked`.
- `git diff --check -- tasks/TASK_337A_PROJECT_LIFECYCLE_BACKEND_API_SHAPE.md docs/lane_evidence/TASK_337A_lifecycle-backend-api_developer.md tasks/TASK_338_PROJECT_LIFECYCLE_WRITE_GUARD_INTEGRATION.md docs/lane_evidence/TASK_338_write-guard-integration_developer.md docs/task_board.md` completed with no whitespace errors. Git printed a CRLF normalization warning for `docs/task_board.md`.
- `rg -n "[ \t]$" tasks\TASK_337A_PROJECT_LIFECYCLE_BACKEND_API_SHAPE.md docs\lane_evidence\TASK_337A_lifecycle-backend-api_developer.md tasks\TASK_338_PROJECT_LIFECYCLE_WRITE_GUARD_INTEGRATION.md docs\lane_evidence\TASK_338_write-guard-integration_developer.md docs\task_board.md` returned no matches.
- `git status --short -- ... backend frontend tests` showed no backend/frontend/tests changes.

Developer planning:

- Confirmed current task board active lane: `lifecycle-backend-api` / `TASK_337A_PROJECT_LIFECYCLE_BACKEND_API_SHAPE`, status `approved`, Developer planning first.
- Created dedicated execution branch: `codex/task-337a-lifecycle-backend-api`.
- Read required inputs:
  - `AGENTS.md`
  - `docs/task_board.md`
  - `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
  - `docs/project_management/TASK_EXECUTION_SKILL.md`
  - `tasks/TASK_337A_PROJECT_LIFECYCLE_BACKEND_API_SHAPE.md`
  - `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`
  - `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`
  - `tasks/TASK_337B_PROJECT_LIFECYCLE_GUARD_INVENTORY_AND_TEST_MATRIX.md`
  - `docs/task_337b_project_lifecycle_guard_inventory_and_test_matrix.md`
  - `docs/lane_evidence/TASK_337A_lifecycle-backend-api_developer.md`
- Performed read-only source inspection of:
  - `backend/application/project_lifecycle_management_service.py`
  - `backend/application/project_lifecycle_service.py`
  - `backend/domain/models.py`
  - `backend/domain/enums.py`
  - `backend/infrastructure/storage/models.py`
  - `backend/infrastructure/storage/database.py`
  - `backend/infrastructure/storage/repositories/project.py`
  - `backend/infrastructure/storage/repositories/project_cleanup.py`
  - `backend/api/routes_project.py`
  - `backend/api/dependencies.py`
  - existing lifecycle/API tests
- Created plan file:
  - `docs/task_337a_project_lifecycle_backend_api_shape_plan.md`

Developer implementation:

- User explicitly approved the TASK_337A plan before product code changes.
- Wrote failing TASK_337A tests first:
  - `tests/unit/test_project_lifecycle_state_service.py`
  - `tests/integration/test_project_lifecycle_migration.py`
  - `tests/integration/test_project_lifecycle_api.py`
- Initial RED check failed at collection with `ModuleNotFoundError: No module named 'backend.application.project_lifecycle_state_service'`, as expected before implementation.
- Implemented backend lifecycle overlay domain, persistence, service, migration, and API shape.
- Kept TASK_338 write guard integration deferred.
- Did not edit frontend, Workbench shell, Office gateway internals, Matrix/Fee/LTR/Folder/Basic Information/Public Drive runtime behavior beyond lifecycle API compatibility.

## Changed Files

Developer planning changed:

- `docs/task_337a_project_lifecycle_backend_api_shape_plan.md`
- `docs/lane_evidence/TASK_337A_lifecycle-backend-api_developer.md`

No backend, frontend, database schema, runtime behavior, Office gateway, Matrix, Fee, LTR, Folder, Basic Information, Public Drive, Report, StepInstance, AI, permissions, LAN/server, or multi-user implementation files were edited during planning.

Developer implementation changed:

- `backend/domain/enums.py`
- `backend/domain/models.py`
- `backend/domain/__init__.py`
- `backend/infrastructure/storage/models.py`
- `backend/infrastructure/storage/database.py`
- `backend/infrastructure/storage/repositories/project.py`
- `backend/infrastructure/storage/repositories/project_lifecycle_event.py`
- `backend/infrastructure/storage/repositories/__init__.py`
- `backend/application/project_lifecycle_state_service.py`
- `backend/api/dependencies.py`
- `backend/api/routes_project.py`
- `tests/unit/test_project_lifecycle_state_service.py`
- `tests/integration/test_project_lifecycle_migration.py`
- `tests/integration/test_project_lifecycle_api.py`
- `docs/lane_evidence/TASK_337A_lifecycle-backend-api_developer.md`

No frontend, Workbench shell, Office gateway internals, Matrix/Fee implementation, LTR authority writeback, Folder generation, Basic Information, Public Drive, Report, StepInstance, AI, permissions, LAN/server, or multi-user implementation files were edited.

## Planning Summary

The plan proposes:

- lifecycle overlay fields on `Project` / `projects`
- `project_lifecycle_events` event ledger
- compatibility treatment for existing `status='cancelled'`
- lifecycle state service for Stop, Resume, Close completed, and Close administrative
- typed lifecycle API routes under `/api/projects/{project_id}/lifecycle/...`
- completed-close manual confirmation plus output summary acknowledgement
- temporary/no-LTR completed-close rejection with administrative-close guidance
- focused unit and integration validation
- explicit deferral of broad write guard integration to TASK_338

## Review Follow-Up

Reviewer decision received on 2026-06-26: implementation approval was blocked until the TASK_337A plan resolved two planning issues.

Follow-up changes made:

- Fixed `cancelled` compatibility policy so it is no longer optional:
  - new Stop must set lifecycle overlay `stopped`
  - new Stop must keep compatibility `Project.status='cancelled'` during this compatibility phase
  - Stop event metadata must record `previous_project_status`
  - Resume must restore compatibility status from the latest lifecycle stop event metadata
  - legacy migrated `cancelled` rows without recoverable previous status must not resume by guessing `draft`; they return a business conflict instead
- Added explicit migration test coverage:
  - `tests/integration/test_project_lifecycle_migration.py`
  - creates a legacy `projects` table without lifecycle columns
  - inserts active, `cancelled`, and `closed` rows
  - runs `init_db`
  - asserts active/stopped/closed administrative backfill behavior
- Added `backend/infrastructure/storage/repositories/__init__.py` to the planned modified file list so `ProjectLifecycleEventRepository` follows local repository export patterns.

## Validation Results

Plan-only validation:

- `Test-Path docs\task_337a_project_lifecycle_backend_api_shape_plan.md` -> `True`
- `Select-String` checks passed for:
  - `ProjectLifecycleState`
  - `CloseCompletedProjectCommand`
  - `TASK_338`
- `Select-String -Path docs\lane_evidence\TASK_337A_lifecycle-backend-api_developer.md -Pattern 'Status: ready_for_review' -Encoding UTF8` -> matched line 3
- `rg -n "[ \t]$" docs\task_337a_project_lifecycle_backend_api_shape_plan.md docs\lane_evidence\TASK_337A_lifecycle-backend-api_developer.md` -> no matches, exit code 1, meaning no trailing whitespace found in the lane files.

Product tests were not run because this pass is planning-only and no product implementation files were changed.

Review follow-up validation:

- `Select-String` confirmed the plan now contains concrete compatibility policy lines for:
  - `New Stop action must set`
  - `previous_project_status`
  - `Resume must not guess`
  - `test_project_lifecycle_migration.py`
  - `repositories/__init__.py`
  - `ProjectLifecycleEventRepository`
- `Select-String` confirmed evidence contains `Review Follow-Up`, the compatibility decision, and the legacy migrated-row resume boundary.
- `Select-String` for unresolved optional wording (`may keep`, `does not need`, `fallback should`, `choose one`, `otherwise draft`) returned no matches.
- `rg -n "[ \t]$" docs\task_337a_project_lifecycle_backend_api_shape_plan.md docs\lane_evidence\TASK_337A_lifecycle-backend-api_developer.md` returned no matches after the follow-up.

Developer implementation validation:

- RED before implementation:
  - `py -m pytest tests\unit\test_project_lifecycle_state_service.py tests\integration\test_project_lifecycle_migration.py tests\integration\test_project_lifecycle_api.py -q`
  - Result: failed during collection because `backend.application.project_lifecycle_state_service` did not exist yet.
- Focused TASK_337A validation after implementation:
  - `py -m pytest tests\unit\test_project_lifecycle_state_service.py tests\integration\test_project_lifecycle_migration.py tests\integration\test_project_lifecycle_api.py -q`
  - Result: `11 passed in 2.39s`
- Adjacent compatibility validation:
  - `py -m pytest tests\integration\test_project_registry_summary_api.py tests\unit\test_project_lifecycle_management_service.py -q`
  - First run exposed a legacy `/api/projects/{id}/stop` audit compatibility regression.
  - Fixed old Stop endpoint so it keeps existing cleanup audit behavior and synchronizes the new lifecycle overlay/event.
- Final combined validation:
  - `py -m pytest tests\unit\test_project_lifecycle_state_service.py tests\integration\test_project_lifecycle_migration.py tests\integration\test_project_lifecycle_api.py tests\integration\test_project_registry_summary_api.py tests\unit\test_project_lifecycle_management_service.py -q`
  - Result: `24 passed in 3.89s`
- Whitespace validation:
  - `git diff --check -- backend\application\project_lifecycle_state_service.py backend\api\dependencies.py backend\api\routes_project.py backend\domain\__init__.py backend\domain\enums.py backend\domain\models.py backend\infrastructure\storage\database.py backend\infrastructure\storage\models.py backend\infrastructure\storage\repositories\__init__.py backend\infrastructure\storage\repositories\project.py backend\infrastructure\storage\repositories\project_lifecycle_event.py tests\unit\test_project_lifecycle_state_service.py tests\integration\test_project_lifecycle_migration.py tests\integration\test_project_lifecycle_api.py`
  - Result: no whitespace errors. Git printed LF/CRLF normalization warnings for existing tracked files.

Reviewer blocker fix:

- Fixed completed-close summary contract:
  - `ProjectLifecycleStateService` now accepts the existing read-only `ProjectOutputRecordService` through an output status protocol.
  - Completed close persists `signals.project_identity`, `signals.registered_ltr`, `signals.output_status_summary_available`, and serialized `output_status_summary`.
  - Summary warning now uses the TASK_337A/TASK_336 wording that completion is manually confirmed because StepInstance does not exist.
- Fixed lifecycle action error shape:
  - 409 lifecycle conflicts now return `code`, `project_id`, `lifecycle_state`, `closure_type`, `message`, and `allowed_actions`.
  - Error shape is populated from the current lifecycle view so TASK_338/TASK_339 can rely on the stable contract.
- Added/updated tests:
  - unit completed-close summary assertions for `signals` and `output_status_summary`
  - API completed-close summary assertions using a persisted manual output record
  - API 409 conflict shape assertions for closed-project resume

Reviewer blocker fix validation:

- RED check after adding blocker tests:
  - `py -m pytest tests\unit\test_project_lifecycle_state_service.py tests\integration\test_project_lifecycle_api.py -q`
  - Result: failed as expected before implementation because `output_status_service` was not accepted, `signals` was missing, and 409 detail lacked `project_id`.
- Focused validation after fix:
  - `py -m pytest tests\unit\test_project_lifecycle_state_service.py tests\integration\test_project_lifecycle_api.py -q`
  - Result: `10 passed in 2.34s`
- Full TASK_337A plus adjacent reviewer validation:
  - `py -m pytest tests\unit\test_project_lifecycle_state_service.py tests\integration\test_project_lifecycle_migration.py tests\integration\test_project_lifecycle_api.py tests\integration\test_project_registry_summary_api.py tests\unit\test_project_lifecycle_management_service.py tests\unit\test_project_service.py tests\integration\test_project_api.py -q`
  - Result: `30 passed in 4.47s`
- Whitespace validation:
  - `git diff --check -- backend\application\project_lifecycle_state_service.py backend\api\dependencies.py backend\api\routes_project.py tests\unit\test_project_lifecycle_state_service.py tests\integration\test_project_lifecycle_api.py docs\lane_evidence\TASK_337A_lifecycle-backend-api_developer.md`
  - Result: no whitespace errors. Git printed LF/CRLF normalization warnings for existing tracked files.
  - `rg -n "[ \t]$" backend\application\project_lifecycle_state_service.py backend\api\dependencies.py backend\api\routes_project.py tests\unit\test_project_lifecycle_state_service.py tests\integration\test_project_lifecycle_api.py docs\lane_evidence\TASK_337A_lifecycle-backend-api_developer.md`
  - Result: no matches.

Second review decision:

- Reviewer reported no remaining blocking findings after the compatibility and migration follow-up.
- Non-blocking recommendation: add `backend/domain/__init__.py` to the plan because local domain package patterns export domain enums/models there.
- Plan updated to include `backend/domain/__init__.py` in the file list and `git diff --check` command for exporting `ProjectLifecycleState`, `ProjectClosureType`, `ProjectLifecycleEventType`, and `ProjectLifecycleEvent`.

## Integrator Completion

Integrator completion on 2026-06-27:

- Confirmed current phase is `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Confirmed active lane is `lifecycle-backend-api` / `TASK_337A_PROJECT_LIFECYCLE_BACKEND_API_SHAPE`.
- Confirmed Reviewer gate has no remaining blocking findings.
- Confirmed the TASK_337A package is limited to the task file, plan, lane evidence, approved backend lifecycle/API/storage files, and focused lifecycle tests.
- Explicitly excluded unrelated governance/planning residue from other lanes, including AGENTS/TASK_335/TASK_337B/TASK_338/TASK_340 and controlled-parallel governance files.
- Confirmed no frontend, Workbench shell, Office gateway internals, Matrix/Fee/LTR/Folder/Basic Information/Public Drive, Report, StepInstance, AI, permissions, LAN/server, or multi-user scope is included.
- Updated global task board completion state through an Integrator-owned clean board update path.
- TASK_338 remains blocked until the task board separately unblocks the next lane step.

## Stop Point

TASK_337A is complete. Stop here; do not start TASK_338, TASK_339, Workbench implementation, or any future-scope lane without separate explicit approval.
