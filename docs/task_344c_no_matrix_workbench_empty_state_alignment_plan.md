# TASK_344C No-Matrix Workbench Empty State Alignment Plan

Status: complete - Integrator accepted
Lane: `no-matrix-workbench-empty-state-alignment`
Last Updated: 2026-06-28

## Discovery Gate

Confirmed by user:

- New Project after LTR registration currently lands in a no-Matrix page that feels like a different page.
- Expected behavior is the unified Workbench layout, similar to the active Matrix screenshot.
- The Matrix display area may be empty or show a simple prompt to click `Matrix Editor`.
- Temporary project Workbench should also use the same unified layout pattern.

Confirmed by repository:

- New Project completion routes to `/projects/:project_id` through `frontend/src/features/new-project/useNewProjectCompletion.ts` and `frontend/src/App.tsx`.
- `derivePrimaryWorkspace(...)` currently returns `matrix_setup` for registered/no-Matrix projects and `temporary_planning` for temporary/no-LTR projects.
- `ProjectWorkbenchLayout.tsx` renders the top commandbar actions only for `active_matrix`.
- Non-active states render `TemporaryPlanningMode` or `RegisteredSetupMode`, which creates the separate setup-page feel.
- Current Workbench lifecycle controls from TASK_343A/TASK_343B are implemented in Workbench files and must be preserved.

Planner inference:

- The user-facing issue is frontend shell composition, not backend lifecycle data.
- A controlled frontend slice can align no-Matrix states with the unified shell without changing API, schema, Matrix authority rules, or Projects list behavior.
- Existing pre-implementation worktree contains Workbench diffs from prior accepted lanes or packaging residuals; TASK_344C must not absorb those silently.

Open but non-blocking details:

- Whether non-Matrix states should show all commandbar buttons as visible disabled/available controls or only safe navigation actions should be finalized in Developer planning/review.
- Browser screenshot tooling availability for New Project after LTR registration must be confirmed during QA or implementation smoke.

Definition of Ready:

- User goal is explicit.
- Repository evidence identifies the current split path.
- Scope, May Touch, Must Not Touch, validation, and merge gates are defined.
- This lane is ready for Reviewer plan gate before product code.

## Implementation Intent

The implementation should keep the unified Workbench frame visible for active Matrix, registered/no-Matrix, and temporary/no-LTR projects.

Recommended approach:

1. Keep lifecycle/status derivation semantically accurate. Do not relabel no-Matrix states as active Matrix.
2. Add a layout path for no-Matrix states that uses the unified Workbench command/header and the same primary workspace geometry.
3. Replace the full-page `RegisteredSetupMode` / `TemporaryPlanningMode` feel with an embedded no-Matrix workspace empty state.
4. Keep `Matrix Editor` as the primary action for creating/editing Matrix authority.
5. Preserve existing Stop/Resume/Close eligibility and confirmation flows.

## Developer Planning-First Refinement

Developer planning inspection on 2026-06-28 confirmed that the minimal implementation should not introduce a new route or backend rule. It should change Workbench composition only:

1. Introduce a display-level predicate such as `showUnifiedWorkbenchFrame` for active lifecycle Workbench states whose primary workspace is `active_matrix`, `matrix_setup`, or `temporary_planning`.
2. Keep `derivePrimaryWorkspace(...)` semantically unchanged for now: no-Matrix states remain `matrix_setup` or `temporary_planning`, not `active_matrix`.
3. Render the top `Project Workbench actions` commandbar for eligible no-Matrix states, not only for `isActiveMatrixWorkspace`.
4. Render a unified no-Matrix workspace surface inside the existing `Matrix` region instead of the current full-page `TemporaryPlanningMode` / `RegisteredSetupMode` surfaces.
5. Keep existing lifecycle action derivation and `ProjectLifecycleManagementPanel` ownership. TASK_344C should only reposition/host existing allowed actions as needed; it must not change Stop/Resume/Close authorization.

Commandbar availability for no-Matrix states:

- `Matrix Editor`: visible and enabled when the lifecycle is not readonly. This is the primary preparation affordance for both registered/no-Matrix and temporary/no-LTR states.
- `Fee Evaluation`: visible for shell consistency but disabled until there is a Matrix draft/candidate that can support fee planning. For registered/no-Matrix without active authority, disabled copy should make clear that active Matrix authority is required before downstream fee/output work.
- `Basic Information`: visible and enabled when the existing route callback is available. It should remain a navigation/read/edit surface, not a lifecycle mutation.
- `Create project folder` / `Update project folder`: visible for shell consistency but disabled for no-Matrix states until active Matrix authority and the existing folder-output prerequisites are satisfied. Disabled title/copy must explain that Matrix authority is required.

No-Matrix workspace surface:

- Replace the setup-page feel with a large Matrix-area empty state using the same operational density as the active Matrix workspace.
- The empty state should include concise copy, for example: no active Matrix is available yet; open `Matrix Editor` to prepare the authority map.
- Registered/no-Matrix may mention that downstream Test Record, Fee Evaluation, Section 2 sync, and package readiness derive from the active Matrix.
- Temporary/no-LTR may mention that LTR registration is still pending, but should not become a separate temporary-planning page.
- Avoid disabled or placeholder future controls beyond the commandbar buttons listed above.

Read-only and closed behavior:

- Closed projects remain `readonly_archive`; TASK_344C must not show Stop, Resume, Close, or Matrix Editor for closed archive states.
- Stopped projects keep TASK_343A readonly behavior and only expose Resume where lifecycle `allowed_actions` allows it.
- Existing TASK_343B Close completed/admin confirmation behavior remains unchanged.

## UX Rules

- Registered/no-Matrix header badges should still communicate `Active`, `Registered project`, and `No Matrix`.
- Temporary/no-LTR header badges should still communicate temporary planning/no registered project semantics.
- The Matrix region empty state should be brief and operator-oriented, for example: no active Matrix is available yet; open Matrix Editor to prepare authority.
- Avoid backend enum tokens in visible copy.
- Avoid thick side stripes, decorative gradients, oversized marketing hero patterns, and page-level cards nested in other cards.
- Maintain dense, operational layout consistent with ConnLab's `$impeccable` product-register guidance.

## Proposed Later Implementation Files

- `frontend/src/features/project-workbench/projectWorkbenchShellModel.ts`
- `frontend/src/features/project-workbench/projectWorkbenchShellModel.test.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/workbench.css`
- `docs/lane_evidence/TASK_344C_no-matrix-workbench-empty-state-alignment_developer.md`

Do not touch `frontend/src/api/client.ts`, `backend/**`, `frontend/src/pages/ProjectListPage.tsx`, or `frontend/src/features/projects-registry/**`.

## Test Plan

Focused tests should cover:

- Active Matrix Workbench remains unchanged.
- Registered/no-Matrix Workbench renders the unified shell, stable command area, no-Matrix badge, and empty Matrix workspace prompt.
- Temporary/no-LTR Workbench renders the same unified shell pattern and no-Matrix prompt.
- `Matrix Editor` remains the route/action used for Matrix preparation.
- Registered/no-Matrix commandbar disables downstream Fee/Project Folder actions until Matrix authority is active.
- Temporary/no-LTR commandbar keeps `Matrix Editor` available and does not imply official package output readiness.
- Stopped readonly Workbench remains readonly with allowed Resume behavior from TASK_343A.
- Closed completed/admin archive remains readonly with no Stop, Resume, or Close actions.
- No Projects list lifecycle mutation controls are introduced.

## Validation Commands

Expected Developer implementation validation:

```powershell
cd frontend
npm test -- --run projectWorkbenchShellModel projectWorkbenchLifecycleSelectors ProjectWorkbenchLayout --watch=false
npm run build
```

Expected repository validation:

```powershell
git diff --check -- frontend/src/features/project-workbench/projectWorkbenchShellModel.ts frontend/src/features/project-workbench/projectWorkbenchShellModel.test.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/workbench.css docs/lane_evidence/TASK_344C_no-matrix-workbench-empty-state-alignment_developer.md
```

QA/browser smoke should verify:

- Creating or opening a registered/no-Matrix project lands in the unified Workbench shell.
- Opening a temporary/no-LTR project lands in the same unified shell pattern.
- The Matrix region shows a clear empty state or prompt and does not look like a separate setup page.
- Existing lifecycle action behavior still matches TASK_343A/TASK_343B.

## Risks

- Existing uncommitted Workbench diffs may already touch the same implementation files; Developer must inspect and work with them, not revert them.
- Showing commandbar buttons for no-Matrix states can imply availability of downstream workflows. Implementation should preserve existing availability/disabled semantics and avoid creating new write paths.
- The change is visual/IA-heavy, so QA browser smoke is recommended after Reviewer implementation gate.

## Stop Point

Stop after Integrator packaging/readiness, local controlled commit, and completion callback.

## Integrator Closeout

Integrator accepted TASK_344C after Reviewer implementation re-gate and QA re-smoke gate passed.

Accepted package boundary:

- `tasks/TASK_344C_NO_MATRIX_WORKBENCH_EMPTY_STATE_ALIGNMENT.md`
- `docs/task_344c_no_matrix_workbench_empty_state_alignment_plan.md`
- `docs/lane_evidence/TASK_344C_no-matrix-workbench-empty-state-alignment_planner.md`
- `docs/lane_evidence/TASK_344C_no-matrix-workbench-empty-state-alignment_developer.md`
- `docs/lane_evidence/TASK_344C_no-matrix-workbench-empty-state-alignment_qa.md`
- `docs/lane_evidence/artifacts/TASK_344C_qa/`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/workbench.css`
- `docs/task_board.md`

`ProjectWorkbenchCloseConfirmation.tsx` is included because the compact lifecycle dock used by the unified Workbench Matrix region depends on its `compact` display variant. The `frontend/src/workbench.css` `linear-gradient` diff is accepted as the compact lifecycle dock background already documented by Developer evidence and covered by Reviewer/QA; no gradient text, decorative side stripe, or unrelated visual direction is introduced by the no-Matrix empty state itself.

Excluded from this package: `AGENTS.md`, `.agents/skills/*`, `docs/project_management/*`, backend/API/schema/frontend API client, Projects list/TASK_344B, TASK_344A smoke fixture/procedure, Matrix Editor business logic, TASK_343A/B rewrites outside compatible Workbench hosting, StepInstance, Report, AI, permissions, LAN/server, and multi-user scope.
