# TASK_345C Project Lifecycle Write Guard Rules Developer Evidence

Status: ready_for_review
Task: TASK_345C_PROJECT_LIFECYCLE_WRITE_GUARD_RULES
Lane: project-lifecycle-write-guard-rules
Role: Developer planning-first
Last Updated: 2026-06-28

## Current Phase / Task / Lane

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

Current task: TASK_345C_PROJECT_LIFECYCLE_WRITE_GUARD_RULES

Current lane: project-lifecycle-write-guard-rules

Allowed reason: user delegated Developer planning-first after stating Reviewer plan gate passed. This pass is documentation-only and updates only the TASK_345C plan/evidence.

Board note: `docs/task_board.md` still records TASK_345C as planned for Reviewer plan gate. Because the newest delegation allows only Developer planning-first and does not authorize product implementation or board reconciliation, this pass records the board lag and does not modify `docs/task_board.md`.

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
- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_developer.md`
- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_reconciliation_planner.md`
- `docs/lane_evidence/DISCOVERY_project-lifecycle-business-model-rework_planner.md`
- `tasks/TASK_345C_PROJECT_LIFECYCLE_WRITE_GUARD_RULES.md`
- `docs/task_345c_project_lifecycle_write_guard_rules_plan.md`
- `docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_planner.md`
- `docs/task_337b_project_lifecycle_guard_inventory_and_test_matrix.md`
- `docs/lane_evidence/TASK_337B_guard-inventory_developer.md`
- `docs/task_338_project_lifecycle_write_guard_integration_plan.md`
- current `backend/application/project_lifecycle_write_guard.py`
- current `backend/api/lifecycle_errors.py`
- current `tests/unit/test_project_lifecycle_write_guard.py`
- `rg` scan for guard usage in backend/tests

## Read-Only Code Findings

- `ProjectLifecycleWriteGuard` currently covers the TASK_338 first slice operations only.
- Stopped projects currently return message `This project is stopped. Resume it before making changes.` and `allowed_actions=("resume", "close")`.
- Closed completed projects currently return `This project is closed as completed and is readonly.` with empty `allowed_actions`.
- Closed administrative projects currently return `This project is closed administratively and is readonly.` with empty `allowed_actions`.
- `backend/api/lifecycle_errors.py` maps guard errors to structured API `409` detail with `code`, `project_id`, `lifecycle_state`, `closure_type`, `message`, and `allowed_actions`.
- Route files already catch `ProjectLifecycleReadonlyError` and route through `lifecycle_readonly_conflict`.
- Existing write guard unit tests intentionally lock the old stopped/closed behavior and must be updated in the future implementation pass.
- TASK_345B evidence confirms unified close, business close reasons, activate endpoint, activate event metadata, and lifecycle response `allowed_actions=["activate"]` for closed projects; TASK_345B intentionally did not change write guard behavior.

## Developer Planning Decisions

TASK_345C should remain backend/API/test scoped.

Guard semantics:

- Active writes remain allowed by existing business rules.
- Stopped and closed business writes remain blocked until activation.
- Guard conflicts should point product-facing recovery to `activate`.
- Completed closed is not a special permanent archive.
- Closed non-completed reasons must not expose `administrative` as business copy.
- Lifecycle transitions (`stop`, unified `close`, `activate`, compatibility `resume`, and compatibility close routes) must not be blocked by generic write guard.
- Non-mutating read/preview endpoints remain available only when the endpoint does not mutate DB records, files, Office documents, public-drive authority, local cache, output records, or workbook state.
- Temporary Apply/Register LTR and public-drive LTR workbook authority write remain outside TASK_345C.

Future implementation file list:

- `backend/application/project_lifecycle_write_guard.py`
- `backend/api/lifecycle_errors.py`
- `tests/unit/test_project_lifecycle_write_guard.py`
- `tests/integration/test_project_basic_information_api.py`
- `tests/integration/test_matrix_editor_session_api.py`
- `tests/integration/test_fee_evaluation_pricing_draft_api.py`
- `tests/integration/test_project_folder_required_forms_api.py`
- `tests/integration/test_ltr_workbook_basic_information_sync_api.py`
- route files that already map guard errors only if needed for error shape adjustment:
  - `backend/api/routes_project_basic_information.py`
  - `backend/api/routes_matrix_editor_session.py`
  - `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`
  - `backend/api/routes_project_folder_required_forms.py`
  - `backend/api/routes_ltr_workbook_basic_information_sync.py`

## Dirty Workspace Classification

Pre-edit targeted status showed:

- `M docs/task_board.md`
- `?? docs/task_345c_project_lifecycle_write_guard_rules_plan.md`

These were pre-existing board/planning residuals. This Developer planning-first pass did not modify product source, backend implementation, frontend implementation, tests, API client, Projects registry, public-drive/LTR authority, or future-scope files.

## Files Changed In This Pass

- `docs/task_345c_project_lifecycle_write_guard_rules_plan.md`
- `docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_developer.md`

No backend/frontend/tests/API client product implementation files were changed.

## Validation Results

- Required docs exist: all required governance, TASK_345A, TASK_345B, TASK_345C, discovery, TASK_337B/TASK_338 guard inventory, and current write guard code/test inputs returned `True`.
- `git diff --check -- docs/task_345c_project_lifecycle_write_guard_rules_plan.md docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_developer.md`: passed with no output.
- `rg -n "[ \t]$" docs/task_345c_project_lifecycle_write_guard_rules_plan.md docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_developer.md`: no matches; exit code `1` indicates no trailing whitespace.
- Targeted status for `backend`, `frontend`, `tests`, `frontend/src/api/client.ts`, `docs/task_board.md`, TASK_345C plan, and TASK_345C Developer evidence showed only:
  - `M docs/task_board.md`
  - `?? docs/task_345c_project_lifecycle_write_guard_rules_plan.md`
  - `?? docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_developer.md`
- No backend/frontend/tests/API client product implementation files were changed by this planning-first pass.

## Risks / Follow-Ups

- Board source-of-truth still lags the conversational Reviewer plan gate; Reviewer/Orchestrator should reconcile if repository-only routing is required before implementation.
- Implementation should not change frontend API client or UI copy; TASK_345D+ owns UI/client-facing lifecycle action alignment.
- Adding `close_reason_category` to guard errors is optional and should not expand TASK_345C into lifecycle API redesign.
- Activation conflicts for legacy closed rows without recoverable previous status remain owned by TASK_345B lifecycle service/API behavior.

## Stop Point

Stop after planning/evidence/validation. Recommended next role: Reviewer implementation-readiness gate.

## Developer Implementation Pass

Date: 2026-06-28
Role: Developer implementation
Status: ready_for_review

### Authorization Re-Check

- `docs/task_board.md` records TASK_345C as implementation authorized / pending Developer implementation.
- `tasks/TASK_345C_PROJECT_LIFECYCLE_WRITE_GUARD_RULES.md` records the exact backend write-guard implementation scope.
- `docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_reconciliation_planner.md` records Planner source-of-truth reconciliation after Reviewer readiness content pass and explicit user approval.
- This implementation stayed inside the authorized backend write-guard/test/evidence scope.

### Implementation Summary

- Updated `ProjectLifecycleWriteGuard` stopped and closed write conflicts to point product-facing recovery to `activate`.
- Replaced old stopped `Resume it before making changes` copy with `Activate it before making changes`.
- Replaced old closed permanent readonly/archive copy with `This project is closed. Activate it before making changes.`
- Added optional business close reason fields to `ProjectLifecycleReadonlyError` and guard results:
  - `close_reason_category`
  - `close_reason_label`
- Guard errors infer `completed` / `Completed` for legacy completed closed rows and `other` / `Other` for legacy administrative or unknown closed rows.
- API readonly conflict details now include business close reason fields.
- API readonly conflict details keep `closure_type="completed"` for completed compatibility but suppress legacy `administrative` from the guard detail by returning `closure_type=null`.
- Existing route mapping remained unchanged because all selected routes already call `lifecycle_readonly_conflict`.
- Lifecycle transition endpoints were not changed; `stop`, unified `close`, `activate`, compatibility `resume`, and compatibility close routes remain governed by lifecycle service/API behavior, not generic write guard.

### Files Changed By This Implementation Pass

- `backend/application/project_lifecycle_write_guard.py`
- `backend/api/lifecycle_errors.py`
- `tests/unit/test_project_lifecycle_write_guard.py`
- `tests/integration/test_project_basic_information_api.py`
- `tests/integration/test_matrix_editor_session_api.py`
- `tests/integration/test_fee_evaluation_pricing_draft_api.py`
- `tests/integration/test_project_folder_required_forms_api.py`
- `tests/integration/test_ltr_workbook_basic_information_sync_api.py`
- `docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_developer.md`

### Scope Proof

Not changed in this pass:

- `frontend/`
- `frontend/src/api/client.ts`
- Projects registry implementation
- Workbench UI implementation
- public-drive LTR authority or Office workbook authority write paths
- TASK_345D+ future lanes
- StepInstance, Report, AI, permissions, LAN/server, multi-user scope
- unrelated governance/orchestration residuals

Pre-existing reconciliation/source-of-truth changes in `docs/task_board.md`, `tasks/TASK_345C_PROJECT_LIFECYCLE_WRITE_GUARD_RULES.md`, `docs/task_345c_project_lifecycle_write_guard_rules_plan.md`, and `docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_reconciliation_planner.md` were Planner reconciliation/planning inputs, not product implementation changes from this pass.

### Validation Results

- `py -m pytest tests\unit\test_project_lifecycle_write_guard.py tests\integration\test_project_basic_information_api.py tests\integration\test_matrix_editor_session_api.py tests\integration\test_fee_evaluation_pricing_draft_api.py tests\integration\test_project_folder_required_forms_api.py tests\integration\test_ltr_workbook_basic_information_sync_api.py -q` -> `54 passed`.
- `py -m pytest tests\unit\test_project_lifecycle_state_service.py tests\integration\test_project_lifecycle_migration.py tests\integration\test_project_lifecycle_api.py tests\integration\test_project_registry_summary_api.py -q` -> `21 passed`.
- Static old-copy scan for `Resume it before making changes`, closed readonly/archive copy, and legacy write-guard allowed-actions returned no matches in write-guard/API focused files.
- Remaining `["activate", "resume", "close"]` matches are in lifecycle API/service tests and `ProjectLifecycleStateService`, which is TASK_345B compatibility behavior and outside TASK_345C generic write guard changes.
- `git diff --check` on implementation package files passed with LF/CRLF normalization warnings only.
- trailing whitespace scan on implementation package files returned no matches.
- Targeted forbidden-scope status showed only TASK_345C authorized backend/test/evidence implementation files plus pre-existing TASK_345C board/task/plan/reconciliation docs:
  - `M backend/api/lifecycle_errors.py`
  - `M backend/application/project_lifecycle_write_guard.py`
  - `M tests/integration/test_fee_evaluation_pricing_draft_api.py`
  - `M tests/integration/test_ltr_workbook_basic_information_sync_api.py`
  - `M tests/integration/test_matrix_editor_session_api.py`
  - `M tests/integration/test_project_basic_information_api.py`
  - `M tests/integration/test_project_folder_required_forms_api.py`
  - `M tests/unit/test_project_lifecycle_write_guard.py`
  - `?? docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_developer.md`
  - pre-existing `M docs/task_board.md`, `?? tasks/TASK_345C_PROJECT_LIFECYCLE_WRITE_GUARD_RULES.md`, `?? docs/task_345c_project_lifecycle_write_guard_rules_plan.md`, and `?? docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_reconciliation_planner.md`
- No `frontend/`, `frontend/src/api/client.ts`, Projects registry, public-drive LTR authority, TASK_345D+ future-scope, `docs/project_management/`, `.agents/`, or `AGENTS.md` implementation changes were introduced by this pass.

### Known Residuals / Follow-Ups

- TASK_345D+ frontend/UI lanes still need to consume the updated write-guard recovery direction in Workbench and other UI surfaces.
- `ProjectLifecycleReadonlyError` now carries business close reason fields for guard errors, but this lane does not redesign frontend API client types.
- `ProjectLifecycleStateService` intentionally still reports stopped lifecycle `allowed_actions=["activate", "resume", "close"]` for compatibility; generic write guard conflicts now prefer only `activate`.

### Stop Point

Stop after final validation, evidence update, and Orchestrator callback. Recommended next role: Reviewer implementation gate.

## Integrator Packaging Checkpoint

Date: 2026-06-29
Role: Integrator
Status: integrator_accepted

### Package Decision

TASK_345C is accepted for local controlled packaging after Reviewer implementation gate pass and Integrator validation.

### Package Scope

Included scope:

- Approved TASK_345C backend write-guard and API error mapper files.
- Focused TASK_345C write-guard/API regression tests.
- TASK_345C task, plan, Planner evidence, Developer evidence, reconciliation evidence, and `docs/task_board.md` closeout.

Excluded scope:

- Frontend runtime files and `frontend/src/api/client.ts`.
- Workbench UI, Projects registry, CSS, routing, and UI copy implementation.
- Public-drive LTR authority and Office workbook authority writes.
- Temporary Apply/Register LTR implementation.
- TASK_345D+ future lanes.
- StepInstance, Report generation, AI, permissions, LAN/server, and multi-user scope.
- Unrelated governance/orchestration residuals.

### QA Decision

QA is not required for this package because the accepted surface is backend/API write-guard semantics and is covered by focused unit/integration/API regression. Frontend/UX smoke belongs to downstream TASK_345D+ lanes after their UI/API-client contracts are approved.

### Integrator Validation

Integrator rerun:

- `py -m pytest tests\unit\test_project_lifecycle_write_guard.py tests\integration\test_project_basic_information_api.py tests\integration\test_matrix_editor_session_api.py tests\integration\test_fee_evaluation_pricing_draft_api.py tests\integration\test_project_folder_required_forms_api.py tests\integration\test_ltr_workbook_basic_information_sync_api.py -q`
- Result: `54 passed`.
- `py -m pytest tests\unit\test_project_lifecycle_state_service.py tests\integration\test_project_lifecycle_migration.py tests\integration\test_project_lifecycle_api.py tests\integration\test_project_registry_summary_api.py -q`
- Result: `21 passed`.

Package validation:

- `git diff --cached --check` passed with LF/CRLF normalization warnings only.
- Staged forbidden-path checks passed: no frontend runtime, `frontend/src/api/client.ts`, Workbench UI, Projects registry, public-drive LTR authority, TASK_345D+ future-scope, `AGENTS.md`, `.agents/`, or `docs/project_management/` paths were staged.

### Stop Point

Stop after local controlled TASK_345C commit and Orchestrator callback. Do not push remote and do not start TASK_345D+ from this Integrator thread.
