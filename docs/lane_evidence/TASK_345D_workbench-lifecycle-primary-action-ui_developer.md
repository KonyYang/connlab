# TASK_345D Workbench Lifecycle Primary Action UI - Developer Evidence

Status: implementation complete - pending Reviewer implementation gate
Lane: `workbench-lifecycle-primary-action-ui`
Last Updated: 2026-06-29

## Current Phase / Task / Lane

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Task: `TASK_345D_WORKBENCH_LIFECYCLE_PRIMARY_ACTION_UI`
- Lane: `workbench-lifecycle-primary-action-ui`
- Role: Developer implementation
- Allowed reason: Planner reconciliation records implementation authorized after Reviewer implementation-readiness and explicit user approval. This pass implements only the approved Workbench lifecycle primary-action UI/API-client-facing scope.

## Source-Of-Truth Note

`docs/task_board.md` still records TASK_345D as planned / ready for Reviewer plan gate. The current delegation records the newer route fact that Reviewer plan gate passed and Developer planning-first is approved.

This Developer pass did not update `docs/task_board.md`. Board closeout and packaging remain Planner/Integrator ownership.

## Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `$impeccable` product context through `node .agents/skills/impeccable/scripts/load-context.mjs`
- `$impeccable` product reference
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
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
- `tasks/TASK_345C_PROJECT_LIFECYCLE_WRITE_GUARD_RULES.md`
- `docs/task_345c_project_lifecycle_write_guard_rules_plan.md`
- `docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_developer.md`
- `docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_reconciliation_planner.md`
- TASK_343A/B/C and TASK_344C Workbench lifecycle evidence as current UI context
- Read-only frontend files:
  - `frontend/src/api/client.ts`
  - `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
  - `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
  - `frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.tsx`
  - `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
  - `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - focused Workbench tests by search.

## Planning Findings

The current frontend still reflects the earlier TASK_343A/B lifecycle model:

- `frontend/src/api/client.ts` exposes `stopProjectLifecycle(...)`, `resumeProjectLifecycle(...)`, `closeProjectCompletedLifecycle(...)`, and `closeProjectAdministrativeLifecycle(...)`.
- The client does not yet expose a confirmed `activateProjectLifecycle(...)` helper or one unified close helper.
- `projectWorkbenchLifecycleSelectors.ts` derives primary actions as `stop`, `resume`, or `none`.
- `ProjectWorkbenchLifecycleSections.tsx` renders `Stop project` / `Resume project` buttons and passes split close callbacks.
- `ProjectWorkbenchCloseConfirmation.tsx` still uses the older `Close as completed` / `Close administratively` paths and `Administrative reason` copy.
- `useProjectWorkbenchModel.ts` still calls the old completed/admin close helpers and `resumeProjectLifecycle(...)`.

The TASK_345B/TASK_345C accepted backend foundation changes the target model:

- TASK_345B introduced unified close, business close reason categories, `activate`, `close_reason_category`, and `close_reason_label`.
- TASK_345B evidence records closed projects exposing `allowed_actions=["activate"]`; stopped projects expose `activate` while retaining `resume` compatibility during migration.
- TASK_345C write guard evidence records product-facing recovery as `activate`, not permanent archive or resume-only language.
- TASK_345D should therefore migrate Workbench UI to one primary action rather than layering Activate on top of the old Stop/Resume/split Close UI.

## Refined Implementation Strategy

Future implementation should keep existing frontend ownership boundaries:

- API typing and network helpers: `frontend/src/api/client.ts`.
- Derived lifecycle action model: `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`.
- Workbench orchestration and refresh: `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`.
- Visible lifecycle UI: `ProjectWorkbenchLifecycleSections.tsx`, `ProjectWorkbenchCloseConfirmation.tsx` or a named replacement, and `ProjectWorkbenchLayout.tsx`.
- Styling only where needed in `frontend/src/workbench.css`.

Primary action matrix:

| State | Primary action | Notes |
|---|---|---|
| Active formal/registered | `Close project` | Use unified close form when backend `allowed_actions` includes close. |
| Active registered/no-Matrix | `Close project` | Preserve TASK_344C unified no-Matrix shell and Matrix Editor affordance. |
| Active temporary/no-LTR | `Close project` only when backend allows close | Do not implement Apply/Register LTR or public-drive authority write. |
| Stopped formal/registered | `Activate project` | Compatibility `resume` must not be product-facing primary action. |
| Stopped temporary/no-LTR | `Activate project` | Preserve temporary/no-Matrix shell and no public-drive side effects. |
| Closed with reason Completed | `Activate project` | Completed is a prior close reason, not permanent archive. |
| Closed with other business reason | `Activate project` | Use business close reason label; never show `administrative`. |
| Legacy non-recoverable closed | No primary mutation if backend does not allow activate | Show business-readable unavailable state. |

Unified close form:

- One action: `Close project`.
- Business reason selector: `Completed`, `Failed`, `Cancelled`, `Cannot test`, `Duplicate`, `Other`.
- Required note/reason text for all reasons unless implementation discovers the accepted backend contract rejects it.
- Output status summary may be shown as context only. It must not be a completed-only acknowledgement path.
- No visible `Close as completed`, `Close administratively`, `Administrative reason`, raw enum names, or user-facing `administrative`.

Activate form:

- One action: `Activate project`.
- Provide activation reason/note collection for audit traceability and backend requiredness.
- Submit through `activateProjectLifecycle(...)`.
- Refresh lifecycle, project, readonly view, and displayed Workbench state after success.
- Success/recovery copy should use `activate`, not `resume`, as the product vocabulary.

## API Client Decision

`frontend/src/api/client.ts` is required May Touch for TASK_345D implementation.

Existing helpers are not enough because the accepted TASK_345B backend contract added:

- unified close endpoint semantics;
- `activate` endpoint semantics;
- `close_reason_category`;
- `close_reason_label`;
- activation/write-guard recovery through `allowed_actions=["activate"]`.

Future implementation should add typed `activateProjectLifecycle(...)` and `closeProjectLifecycle(...)` helpers and extend lifecycle response/error types for already-accepted backend fields. Existing split close helpers can remain as compatibility exports, but Workbench TASK_345D should not call them for the new primary action flow.

## Exact Future Implementation File List

Future Developer implementation should be limited to:

- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx` only if primary action placement requires it
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py` only if static frontend guard coverage is needed
- `docs/lane_evidence/TASK_345D_workbench-lifecycle-primary-action-ui_developer.md`

## Must Not Touch

- `backend/**`
- backend API routes, services, domain models, database migrations, repositories, write guards, and backend tests
- `frontend/src/features/projects-registry/**`
- `frontend/src/pages/ProjectListPage.tsx`
- public-drive LTR workbook authority writes and Office gateway mutation
- Temporary Apply/Register LTR implementation
- TASK_345E+ future lanes
- StepInstance, Report generation, AI, permissions, LAN/server, multi-user scope
- unrelated governance/orchestration residuals
- `docs/task_board.md`
- merge, commit, push, reset, or destructive git operations

## Focused Test Plan

Future implementation should add/update:

- `projectWorkbenchLifecycleSelectors` tests for active close, stopped activate, closed Completed activate, closed other activate, and legacy no-action fallback.
- `useProjectWorkbenchModel` tests proving unified close helper and activate helper are called, old split close helpers are not used by the new Workbench flow, and lifecycle/project state refreshes after success.
- `ProjectWorkbenchCloseConfirmation` or replacement tests for reason taxonomy, required note/reason, no completed/admin split, and no user-facing `administrative`.
- `ProjectWorkbenchLayout` tests for active Matrix, registered/no-Matrix, temporary/no-LTR, stopped, closed Completed, and closed other reason states.
- Static shell test or source scan proving Workbench copy does not expose `Close administratively`, `Administrative reason`, raw `administrative`, or Projects registry mutation wiring.
- Browser/QA smoke for active close, stopped activate, closed Completed activate, closed other activate, temporary/no-LTR no authority write, and registered/no-Matrix shell continuity.

## Dirty Residual Classification

This planning-first pass treated existing residuals as outside scope:

- `docs/task_board.md` is already modified by prior board/governance activity and was not edited here.
- TASK_345D task/plan files are planning artifacts from Planner activation.
- No frontend product source, backend source, tests, Projects registry, or API client product file was modified by this pass.
- Existing accepted Workbench lifecycle/no-Matrix behavior from TASK_343A/B and TASK_344C is implementation context for the future pass, not work changed here.

## Files Changed In Planning-First Pass

- `docs/task_345d_workbench_lifecycle_primary_action_ui_plan.md`
- `docs/lane_evidence/TASK_345D_workbench-lifecycle-primary-action-ui_developer.md`

No frontend, backend, tests, API client, Projects registry, board, governance/orchestration, merge, commit, or push operation was performed in this planning-first pass.

## Planning-First Validation Results

Executed in this planning-first pass:

- Required docs existence check passed:
  - `docs/task_345d_workbench_lifecycle_primary_action_ui_plan.md`
  - `docs/lane_evidence/TASK_345D_workbench-lifecycle-primary-action-ui_developer.md`
- `git diff --check -- docs/task_345d_workbench_lifecycle_primary_action_ui_plan.md docs/lane_evidence/TASK_345D_workbench-lifecycle-primary-action-ui_developer.md` passed with no output.
- Trailing whitespace scan on the TASK_345D plan/evidence files returned no matches.
- Targeted status for `frontend`, `backend`, `tests`, `frontend/src/api/client.ts`, `docs/task_board.md`, TASK_345D plan, and TASK_345D Developer evidence showed:
  - pre-existing `M docs/task_board.md`;
  - TASK_345D plan/evidence docs as untracked planning artifacts;
  - no frontend/backend/tests/API client product code changes by this pass.

## Recommended Next Gate

Reviewer implementation-readiness gate.

## Stop Point

Planning-first stopped after Developer evidence and validation.

## Developer Implementation Pass - 2026-06-29

Implementation status: `implementation complete - pending Reviewer implementation gate`.

### Implementation Summary

- Added TASK_345B/C-facing frontend lifecycle helpers and types:
  - `activateProjectLifecycle(...)`
  - `closeProjectLifecycle(...)`
  - business close reason category typing and lifecycle response close reason fields.
- Migrated Workbench lifecycle action derivation to the TASK_345D primary-action model:
  - active projects expose single primary `Close project` when backend `allowed_actions` includes `close`;
  - stopped and closed projects expose single primary `Activate project` when backend `allowed_actions` includes `activate`;
  - compatibility `resume` remains non-product-facing in this Workbench model.
- Replaced split close UI with one unified business close form:
  - reason selector: `Completed`, `Failed`, `Cancelled`, `Cannot test`, `Duplicate`, `Other`;
  - close note is required and the confirm action is disabled until the note is present;
  - no visible `Close as completed`, `Close administratively`, `Administrative reason`, or raw lifecycle enum copy.
- Updated Workbench lifecycle panels and model callbacks to use unified close and activate paths, then refresh lifecycle/workbench state after success.
- Updated readonly/shell copy so stopped and closed states point operators to `Activate project` instead of `Resume` or permanent archive language.

### Changed Files

- `frontend/src/api/client.ts`
- `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.ts`
- `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.test.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx`
- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/projectWorkbenchShellModel.ts`
- `frontend/src/features/project-workbench/projectWorkbenchShellModel.test.ts`
- `docs/lane_evidence/TASK_345D_workbench-lifecycle-primary-action-ui_developer.md`

### Scope Notes

- `useProjectRuntimeConsoleModel.ts` was touched because it is the Workbench model projection that wires the lifecycle callbacks consumed by `ProjectWorkbenchLayout`.
- `projectLifecycleReadonlyModel.ts` and `projectWorkbenchShellModel.ts` were touched to remove old user-facing resume/archive/admin copy from Workbench-facing lifecycle state.
- Existing compatibility helpers and backend enum compatibility remain in the API layer where needed for older routes; the Workbench UI no longer calls the old completed/admin split close helpers.
- No backend, Projects registry, public-drive LTR authority write, TASK_345E+, StepInstance, Report, AI, permissions, LAN/server, multi-user, merge, commit, or push work was performed.

### Validation Results

- Focused frontend tests:
  - `npm test -- --run projectLifecycleReadonlyModel projectWorkbenchLifecycleSelectors ProjectWorkbenchCloseConfirmation useProjectWorkbenchModel ProjectWorkbenchLayout projectWorkbenchShellModel --watch=false`
  - Result: `6 passed`, `81 passed`.
- Frontend build:
  - `npm run build`
  - Result: passed; Vite reported the existing chunk-size warning for the main JS bundle.
- Static Workbench/lifecycle production copy scan:
  - scanned for old split labels, user-facing `administrative`, archive copy, and old Stop/Resume primary-action labels.
  - Result: no matches in production Workbench/lifecycle source.
- Projects registry mutation-helper scan:
  - scanned `frontend/src/features/projects-registry` and `frontend/src/pages/ProjectListPage.tsx` for lifecycle/delete mutation helpers.
  - Result: no matches.
- `git diff --check` on package files:
  - Result: passed; only LF/CRLF normalization warnings.
- Trailing whitespace scan on package files:
  - Result: no matches.
- Targeted forbidden-scope status:
  - `backend`, Projects registry, and `ProjectListPage.tsx` clean for this pass.
  - `docs/task_board.md` remains a pre-existing external board residual and was not edited here.
  - `frontend/src/api/client.ts` is modified as approved for TASK_345D API-client-facing lifecycle helpers.

### Browser Smoke Residual

Browser smoke was not completed in this thread because there is no confirmed local fixture set for active, stopped, closed Completed, closed other reason, and temporary lifecycle states. QA should run smoke on those fixtures after Reviewer implementation gate, especially verifying that closed/stopped Workbench states show `Activate project` and active/temporary states use the unified `Close project` form.

## Latest Stop Point

Stop after Developer implementation evidence and validation. Recommended next role: Reviewer implementation gate.

## Integrator Packaging Checkpoint - 2026-06-29

Integrator gate: `accepted`.

### Package Scope Accepted

- Approved TASK_345D Workbench lifecycle UI/model/test files.
- `frontend/src/api/client.ts` typed activate/unified-close helpers required by TASK_345B/TASK_345D.
- TASK_345D task, plan, planner/developer/QA/reconciliation evidence, QA screenshots, and `docs/task_board.md` closeout.

### Excluded Scope

- No backend/API/schema/migration/write-guard implementation.
- No Projects registry or `ProjectListPage` changes.
- No public-drive LTR workbook authority write.
- No TASK_345E+ future lane work.
- No StepInstance, Report, AI, permissions, LAN/server, multi-user, `AGENTS.md`, `.agents/`, `docs/project_management/`, or unrelated governance/orchestration files.

### Integrator Validation

- Focused frontend tests rerun:
  - `npm test -- --run projectLifecycleReadonlyModel projectWorkbenchLifecycleSelectors ProjectWorkbenchCloseConfirmation useProjectWorkbenchModel ProjectWorkbenchLayout projectWorkbenchShellModel --watch=false`
  - Result: passed, `6` files / `81` tests.
- Frontend build rerun:
  - `npm run build`
  - Result: passed with existing Vite chunk-size warning only.
- Staged package checks:
  - `git diff --cached --check` passed with LF/CRLF normalization warnings only.
  - Staged forbidden-path checks found no backend/API/schema/migration/write-guard, Projects registry, `ProjectListPage`, public-drive LTR authority, TASK_345E+ future scope, StepInstance, Report, AI, permissions, LAN/server, multi-user, `AGENTS.md`, `.agents/`, `docs/project_management/`, or unrelated governance/orchestration files.

### QA Residual

Closed Completed and closed other browser fixtures remain unavailable in the current local data because QA found zero closed lifecycle rows and did not mutate data. This is accepted as non-blocking because focused tests cover closed activation behavior and QA browser smoke passed active registered close, stopped registered activate, and temporary unified close paths.

### Final Stop Point

TASK_345D is packaged locally by Integrator. Remote push was intentionally not performed. Recommended next role: Orchestrator/Planner for one legal next routing action, or User if the lifecycle series should pause.
