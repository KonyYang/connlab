# TASK_345D Workbench Lifecycle Primary Action UI Plan

Status: implementation authorized after user approval - pending Developer implementation
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Current Lane: workbench-lifecycle-primary-action-ui
Created: 2026-06-29
Last Updated: 2026-06-29

## 1. Planner Discovery Gate

### User Confirmed Facts

- The main Workbench lifecycle action should be simplified to one primary button.
- Active projects should show `Close project`.
- Stopped projects and closed projects, including Completed-closed projects, should support `Activate project`.
- `Close project` is a business phase ending, not an irreversible archive.
- Completed is no longer a special close path. All close reasons use one unified close form.
- User-facing UI must not expose `administrative`.
- Close reasons should be business-readable, including `Completed`, `Failed`, `Cancelled`, `Cannot test`, `Duplicate`, and `Other`.
- Temporary `Apply/Register LTR` is a workflow entrypoint only for the current batch; public-drive LTR workbook authority writing belongs to a later authority lane.
- Audit history must preserve close/activate time, reason, operator, and previous close information. TASK_345D consumes this as frontend display/API data; it does not implement backend audit.

### Repository Proven Facts

- `docs/task_board.md` records `TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT` complete/accepted.
- `docs/task_board.md` records `TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API` complete/accepted with backend/API/audit lifecycle activation model, business close reason categories, unified close endpoint, compatibility close wrappers, activate endpoint, close/activate event metadata, and response close reason fields.
- `docs/task_board.md` records `TASK_345C_PROJECT_LIFECYCLE_WRITE_GUARD_RULES` complete/accepted with backend write-guard/read-only semantics that point stopped/closed business writes to `activate`.
- `frontend/src/api/client.ts` currently exposes `stopProjectLifecycle`, `resumeProjectLifecycle`, `closeProjectCompletedLifecycle`, and `closeProjectAdministrativeLifecycle`; it does not expose a confirmed `activateProjectLifecycle` helper or one unified close helper.
- Current Workbench lifecycle selectors still model primary actions as `stop`, `resume`, or `none`, and still contain completed/admin split close concepts.
- Current Workbench close confirmation code still contains user-facing copy such as `Close as completed`, `Close administratively`, and administrative reason language from TASK_343B.
- TASK_343A implemented Stop/Resume Workbench UX and explicitly withheld Close controls.
- TASK_343B implemented the older completed/admin split close UX against existing frontend client helpers.
- TASK_343C kept Projects list lifecycle behavior routing-only and locked Workbench behavior/API client changes.
- TASK_344C aligned no-Matrix Workbench shell layout and preserved existing TASK_343A/B lifecycle behavior.
- `$impeccable` / frontend architecture rules require business-readable operator copy, centralized API client calls, selector/model ownership for derived UI state, and no future-scope or raw backend terminology as active UI.

### Planner Inferences

- TASK_345D should be a frontend/UI/API-client-facing lane because backend model/API/write guard semantics are now accepted in TASK_345B/C.
- `frontend/src/api/client.ts` should be May Touch for the future implementation, because current client types/helpers do not yet represent the accepted activate/unified-close frontend contract.
- Existing TASK_343A/B Workbench UI and tests should be migrated, not ignored. The target is not "Stop/Resume plus completed/admin close"; the target is one primary action: Close for active and Activate for stopped/closed.
- If Developer discovers that TASK_345B backend endpoints or response fields are insufficient, TASK_345D must stop and request a separate backend/API lane instead of modifying backend code.

### Definition Of Ready

TASK_345D is ready for a formal planning-first lane and Reviewer plan gate because:

- Upstream business contract and backend/write-guard foundations are accepted.
- Current frontend gaps are visible from existing API client and Workbench code.
- May Touch, Must Not Touch, Locked Paths, validation, and merge gates can be stated now.

TASK_345D is now ready for Developer implementation after Planner reconciliation because:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed and updated only TASK_345D plan/evidence.
- Reviewer implementation-readiness content review passed.
- User explicitly approved Developer implementation.
- Repository source-of-truth has been reconciled to record implementation authorization without marking implementation complete.

Developer planning-first update:

- The delegated route states Reviewer plan gate passed and the user approved Developer planning-first.
- Developer planning-first updated only TASK_345D plan/evidence.
- Reviewer implementation-readiness content review passed and found the plan concrete enough for implementation.
- Reviewer noted direct implementation remained blocked until repository source-of-truth recorded implementation authorization.
- User explicitly approved Developer implementation.
- Planner reconciliation on 2026-06-29 updates the task, plan, board, and reconciliation evidence to record "implementation authorized after user approval, pending Developer implementation".

## 2. Objective

Plan the first Workbench UI migration to the TASK_345A business lifecycle model:

- One primary lifecycle button in the Workbench lifecycle action area.
- Active formal/registered projects: `Close project`.
- Stopped projects: `Activate project`.
- Closed projects with recoverable backend state: `Activate project`.
- Unified close form with business reason taxonomy and required close note/reason.
- No user-facing `administrative` copy.
- API-client and UI state refresh that rely on TASK_345B/TASK_345C semantics.

## 3. State Behavior Contract

| Workbench state | Primary lifecycle action | Close behavior | Activate behavior | Notes |
|---|---|---|---|---|
| Active formal/registered with active Matrix | `Close project` | Open one unified close form with business reason taxonomy. | Not shown. | Matrix remains the primary workspace; lifecycle action should be prominent but not displace Matrix work. |
| Active formal/registered with no active Matrix | `Close project` when backend allows close. | Same unified close form. Copy must not imply testing completion unless reason is `Completed`. | Not shown. | Preserve TASK_344C no-Matrix shell. |
| Active temporary/no-LTR | No TASK_345D LTR registration action. Close handling should follow backend allowed actions and plan review. | If close is available, use unified form; do not implement completed/admin split or LTR authority write. | Not shown. | Temporary Apply/Register LTR remains downstream. |
| Stopped formal/registered | `Activate project` when backend allows activate. | Not primary in TASK_345D. | Submit activate via TASK_345B API/client helper and refresh Workbench lifecycle state. | Stop/Resume wording should be retired from primary lifecycle action copy. |
| Stopped temporary/no-LTR | `Activate project` when backend allows activate. | Not primary in TASK_345D. | Same activate pattern, no LTR authority write. | Preserve no-Matrix shell and write-guard behavior. |
| Closed Completed | `Activate project` when backend allows activate. | No close-again primary action. | Activate should restore active workflow while preserving close history. | Completed is one prior close reason, not a permanent archive state. |
| Closed Failed/Cancelled/Cannot test/Duplicate/Other | `Activate project` when backend allows activate. | No close-again primary action. | Activate should show prior close reason context where available. | UI must not say administrative. |
| Non-recoverable legacy closed fallback | No mutation if backend does not allow activate. | No close-again primary action. | Not shown. | Show business-readable unavailable state and preserve read-only display. |

## 4. Unified Close Form Contract

TASK_345D should replace the older TASK_343B completed/admin split UI with one form:

- Title/action copy: `Close project`.
- Required business close reason:
  - `Completed`
  - `Failed`
  - `Cancelled`
  - `Cannot test`
  - `Duplicate`
  - `Other`
- Required note/reason text when backend contract requires it.
- Optional display of current output/work status only as context, not as a separate Completed-only acknowledgement path unless TASK_345B API still requires a compatibility field.
- Submit through a unified close client helper if available or introduced in `frontend/src/api/client.ts`.
- On success, refresh lifecycle/project state and show the resulting closed state with business reason context.

The form must not expose:

- `Close as completed`
- `Close administratively`
- `Administrative reason`
- `Archive project` as the main business meaning
- `Completed close` as a separate path
- Any raw backend enum labels

## 5. Activate Contract

TASK_345D should add Workbench UI/API-client consumption for activation:

- Primary action label: `Activate project`.
- Use backend `allowed_actions` or the accepted TASK_345B response contract to determine availability.
- If current frontend client lacks the helper, add typed `activateProjectLifecycle(projectId, input)` in `frontend/src/api/client.ts`.
- Include reason/operator fields only as required by accepted backend API/client contract.
- On success, refresh Workbench lifecycle state, readonly model, and any displayed status/recovery copy.
- Preserve close/activate audit history display if response fields are available; do not implement backend audit storage.

## 6. API Client Decision

`frontend/src/api/client.ts` is May Touch for TASK_345D implementation.

Reason:

- Current frontend client exposes old Stop/Resume and completed/admin split close helpers.
- TASK_345B accepted backend semantics include activate and unified close/close reason response fields.
- Workbench should consume typed helpers rather than inline fetch calls or ad hoc DTO shapes.

Allowed client changes:

- Add or update typed lifecycle response fields for business close reason category/label and activation readiness where backend already returns them.
- Add `activateProjectLifecycle(...)` if missing.
- Add a unified close helper/request type if the backend endpoint exists.
- Keep compatibility helpers only where other existing callers still need them.

Forbidden client changes:

- Invent a backend contract not present in TASK_345B.
- Add Projects registry lifecycle mutation helpers or wire registry mutation flows.
- Change backend behavior from the frontend layer.

Developer planning-first confirmation:

- Existing client helpers are not sufficient for the TASK_345D target UI because they only expose `resumeProjectLifecycle(...)`, `closeProjectCompletedLifecycle(...)`, and `closeProjectAdministrativeLifecycle(...)`.
- TASK_345B developer evidence records the accepted backend shape: unified close endpoint, `activate` endpoint, `close_reason_category`, `close_reason_label`, and lifecycle `allowed_actions` containing `activate` for stopped/closed recovery.
- Future implementation should add typed `activateProjectLifecycle(...)` and unified `closeProjectLifecycle(...)` helpers and extend the lifecycle response/read-only error types for business close reason fields already returned by backend.
- Existing split close helpers may remain as compatibility exports if other callers still reference them, but Workbench TASK_345D UI should prefer the unified helper.

## 7. Migration From TASK_343A/B

TASK_345D should intentionally migrate existing Workbench lifecycle UI and tests:

- TASK_343A Stop/Resume UI was valid for the earlier model. TASK_345D should not keep Stop/Resume as competing primary lifecycle actions in the Workbench main action area.
- TASK_343B completed/admin split close UI was valid for the earlier model. TASK_345D should replace it with unified close reason UX and remove user-facing administrative copy.
- Stopped-state `Resume project` UI should be replaced by `Activate project` as the product-facing recovery action. If compatibility `resume` remains in backend `allowed_actions`, it must not become the Workbench primary action.
- Active-state `Stop project` should not compete with `Close project` in the primary lifecycle slot. If a later task wants a secondary pause/stop affordance, it needs separate scope; TASK_345D first slice should make the main lifecycle panel single-primary.
- Existing tests should be updated or replaced with explicit coverage for:
  - active shows Close project.
  - stopped shows Activate project.
  - closed Completed shows Activate project when allowed.
  - closed non-Completed shows Activate project when allowed.
  - no `Close administratively`, `Administrative reason`, or `Close as completed` user-facing copy remains in Workbench.
  - no Projects list mutation controls are introduced.

## 7.1 Developer Planning-First Implementation Strategy

Future implementation should keep the existing Workbench ownership boundaries:

- API calls stay in `frontend/src/api/client.ts`.
- Lifecycle action derivation stays in `projectWorkbenchLifecycleSelectors.ts`.
- Network orchestration and refresh behavior stay in `useProjectWorkbenchModel.ts`.
- Visual lifecycle action rendering stays in `ProjectWorkbenchLifecycleSections.tsx` plus the close confirmation component or a named replacement.
- Route/page-level JSX must not grow ad hoc lifecycle branching.

Primary action matrix:

| State | Required primary UI | API helper | Refresh behavior |
|---|---|---|---|
| Active formal/registered | `Close project` | `closeProjectLifecycle(...)` | Refresh lifecycle, project, readonly view, and output status context after success. |
| Active registered/no-Matrix | `Close project` if backend allows `close` | `closeProjectLifecycle(...)` | Preserve TASK_344C Matrix Editor empty-state shell. |
| Active temporary/no-LTR | `Close project` only if backend allows `close`; no LTR registration implementation | `closeProjectLifecycle(...)` | Preserve temporary/no-Matrix shell and no public-drive authority write. |
| Stopped formal/registered | `Activate project` when `allowed_actions` includes `activate` | `activateProjectLifecycle(...)` | Refresh lifecycle/project and remove stale stopped/recovery copy. |
| Stopped temporary/no-LTR | `Activate project` when allowed | `activateProjectLifecycle(...)` | Preserve temporary/no-Matrix shell. |
| Closed with reason `Completed` | `Activate project` when allowed | `activateProjectLifecycle(...)` | Show prior close reason as context; do not describe as permanent archive. |
| Closed with other business reason | `Activate project` when allowed | `activateProjectLifecycle(...)` | Use `close_reason_label`; never show `administrative`. |
| Legacy closed without recoverable status | No primary mutation if backend does not allow `activate` | none | Show business-readable unavailable state and non-mutating reads only. |

Unified close form:

- One entry button: `Close project`.
- One reason selector with business labels: `Completed`, `Failed`, `Cancelled`, `Cannot test`, `Duplicate`, `Other`.
- Required note/reason text for all reasons unless backend rejects this assumption during implementation.
- Output status summary may be shown as context, not as a separate completed-only acknowledgement gate.
- Submit uses the unified close helper and sends the backend-approved reason category plus note/operator fields.
- Copy must avoid `Archive project`, `Close as completed`, `Close administratively`, `Administrative reason`, `closure_type`, `cancelled` as a raw status, and raw backend enum labels.

Activate form:

- Primary entry button: `Activate project`.
- Require a short activation reason/note if the accepted backend request type requires it; otherwise still present a concise confirmation reason field to support audit traceability.
- Submit uses `activateProjectLifecycle(...)`.
- Success message should say project work is active again, not "resumed" as the product-facing action.

Temporary behavior:

- TASK_345D may display current LTR dependency as non-mutating copy only.
- It must not implement Apply/Register LTR, public-drive LTR workbook writes, duplicate project creation, or authority sync.
- Temporary close/activate follows backend lifecycle `allowed_actions`; the Workbench UI must not invent temporary-only lifecycle transitions.

Dirty residual classification for this planning pass:

- Initial targeted status showed `docs/task_board.md` as an existing board/governance residual and TASK_345D task/plan files as untracked planning artifacts.
- No `frontend/`, `backend/`, `tests/`, or `frontend/src/api/client.ts` product files were modified by this planning-first pass.
- Prior Workbench changes from TASK_343A/B and TASK_344C are accepted context for future implementation, not changes made by this pass.

## 8. May Touch

Planner/reconciliation may touch:

- `tasks/TASK_345D_WORKBENCH_LIFECYCLE_PRIMARY_ACTION_UI.md`
- `docs/task_345d_workbench_lifecycle_primary_action_ui_plan.md`
- `docs/lane_evidence/TASK_345D_workbench-lifecycle-primary-action-ui_planner.md`
- `docs/lane_evidence/TASK_345D_workbench-lifecycle-primary-action-ui_reconciliation_planner.md`
- `docs/task_board.md`

Developer implementation may touch only:

- `docs/task_345d_workbench_lifecycle_primary_action_ui_plan.md`
- `docs/lane_evidence/TASK_345D_workbench-lifecycle-primary-action-ui_developer.md`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.tsx` or a named replacement component
- `frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx` only if primary action placement requires it
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py` only for static frontend guard coverage if needed
- TASK_345D Developer/QA evidence files under `docs/lane_evidence/`

## 9. Must Not Touch

- `backend/`
- Backend API routes, services, domain models, database migrations, repositories, write guards, and backend tests.
- `frontend/src/features/projects-registry/`
- `frontend/src/pages/ProjectListPage.tsx`
- Public-drive LTR workbook authority writes and Office gateway mutation.
- Temporary Apply/Register LTR implementation.
- TASK_345E+ future task files or plans unless a separate Planner lane is created.
- StepInstance, Report generation, AI, permissions, LAN/server, multi-user, and unrelated governance/orchestration residuals.

## 10. Locked Paths

- `backend/`
- `backend/api/`
- `backend/application/`
- `backend/domain/`
- `backend/infrastructure/`
- `backend/modules/`
- `frontend/src/features/projects-registry/`
- `frontend/src/pages/ProjectListPage.tsx`
- Public-drive / Office workbook authority write paths
- `AGENTS.md`
- `.agents/`
- `docs/project_management/`

## 11. Validation Plan

Reviewer plan gate passed by callback/source-of-truth reconciliation. Developer implementation should satisfy these checks before Reviewer implementation gate:

### Focused frontend tests

- `npm test -- --run projectWorkbenchLifecycleSelectors ProjectWorkbenchCloseConfirmation ProjectWorkbenchLayout useProjectWorkbenchModel --watch=false`
- Tests may be adjusted to actual filenames if Developer splits or renames a component.
- Selector tests:
  - active with `allowed_actions=["close"]` derives primary `close`.
  - stopped with `allowed_actions=["activate", "resume", "close"]` derives primary `activate`, not `resume`.
  - closed Completed with `allowed_actions=["activate"]` derives primary `activate`.
  - closed other reason with `allowed_actions=["activate"]` derives primary `activate` and business close reason label.
  - no activate allowed derives no primary mutation and business-readable unavailable copy.
- Model/client tests:
  - close submits unified reason category and required note.
  - activate submits activation note/reason and refreshes lifecycle/project state.
  - legacy split close helpers are not called from Workbench TASK_345D flow.
- Component tests:
  - active Workbench shows one primary lifecycle button, `Close project`.
  - stopped/closed Workbench shows `Activate project`.
  - close form lists the approved business reasons.
  - Workbench contains no visible `Close as completed`, `Close administratively`, `Administrative reason`, or user-facing `administrative`.
  - temporary/no-LTR Workbench does not introduce Apply/Register LTR writes.

### Static/backend-scope checks

- Source scan confirms no user-facing Workbench copy exposes `administrative`, `Close administratively`, or `Administrative reason`.
- Source scan confirms Projects registry code does not import lifecycle mutation helpers.
- Source scan confirms no backend files changed.
- `git diff --check` on the package.

### Build

- `npm run build`

### Browser/manual smoke

QA should verify:

- Active Matrix Workbench shows one primary lifecycle action: `Close project`.
- Registered/no-Matrix Workbench uses the unified shell and shows the correct lifecycle primary action without breaking Matrix Editor access.
- Stopped Workbench shows `Activate project`, keeps write controls blocked until activation, and refreshes after activation.
- Closed Completed Workbench shows `Activate project` when backend allows it and does not describe the state as a permanent archive.
- Closed non-Completed Workbench shows business close reason context and `Activate project` when backend allows it.
- Unified close form lists business reasons and never exposes `administrative`.
- Temporary/no-LTR does not implement public-drive LTR authority writes or hidden LTR registration behavior.

## 12. QA Rationale

TASK_345B and TASK_345C did not require QA because they were backend/API/write-guard lanes covered by focused backend regression. TASK_345D is user-facing Workbench lifecycle UI and should require QA/browser smoke after Reviewer implementation gate because it changes the primary operator action, close form copy, activation path, and visible read/write recovery semantics.

## 13. Reviewer / Merge Gates

Reviewer plan gate and implementation-readiness content review have passed by callback/source-of-truth reconciliation. Developer implementation is authorized after explicit user approval.

Reviewer implementation gate is required after Developer implementation.

QA gate is required because the lane changes visible Workbench lifecycle behavior.

Integrator Merge Gate remains blocked until:

- Developer evidence records implementation and validation.
- Reviewer implementation gate passes.
- QA passes or records an accepted residual.
- Integrator package excludes backend/API/write-guard, Projects registry, public-drive LTR authority, future scope, and unrelated governance residuals.

## 14. Next Role

Recommended next role: Developer implementation pass.

Do not mark TASK_345D complete until Developer implementation evidence, Reviewer implementation gate, QA gate, and Integrator packaging/readiness gate all pass.
