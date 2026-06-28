# TASK_344C QA Evidence

Status: complete - Integrator accepted
Task: TASK_344C_NO_MATRIX_WORKBENCH_EMPTY_STATE_ALIGNMENT
Lane: no-matrix-workbench-empty-state-alignment
Role: QA / Smoke Owner
Date: 2026-06-28

## Summary

QA reran focused frontend validation and performed browser-rendered smoke for registered/no-Matrix and temporary/no-LTR no-Matrix Workbench states.

Core TASK_344C shell alignment is visible in both smoke cases:

- the Workbench opens in the unified shell rather than the old separate setup/planning page;
- `Project Workbench actions` is visible;
- `Matrix Editor` is visible and the existing `/matrix-editor` route renders;
- `Fee Evaluation` and `Create project folder` are visible but disabled when active Matrix authority is missing;
- `Basic Information` remains visible;
- the Matrix region contains a concise `No active Matrix` workspace prompt.

Initial QA gate was blocked because the temporary/no-LTR smoke page exposed contradictory lifecycle/delete copy: the same page said `Temporary project before LTR registration` and `Stop or safely remove this temporary record`, but also showed the blocker `Project is not a temporary planning project.` under the lifecycle panel.

QA re-smoke after the Developer B1 fix confirmed the contradictory user-facing copy is gone. Current QA gate: pass.

Recommended next role: Integrator packaging/readiness.

## Integrator Packaging Checkpoint

Status: `integrator_accepted`
Date: 2026-06-28

Integrator accepted TASK_344C after QA re-smoke passed. Accepted package includes the QA evidence and screenshots under `docs/lane_evidence/artifacts/TASK_344C_qa/`.

Integrator validation reran focused Workbench tests (`3` files / `68` tests), frontend build, package diff check, trailing whitespace scan, future-scope scan, and forbidden-scope status checks. No backend/API/schema/frontend API client, Projects list/TASK_344B, TASK_344A, StepInstance, Report, AI, permissions, LAN/server, multi-user, or governance/orchestration residuals were included.

## Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `$impeccable` product context and product-register guidance
- Browser control skill and screenshot guidance
- `tasks/TASK_344C_NO_MATRIX_WORKBENCH_EMPTY_STATE_ALIGNMENT.md`
- `docs/task_344c_no_matrix_workbench_empty_state_alignment_plan.md`
- `docs/lane_evidence/TASK_344C_no-matrix-workbench-empty-state-alignment_developer.md`
- Relevant Workbench implementation/test files by read-only inspection

Board note:

- `docs/task_board.md` still showed TASK_344C as ready for Reviewer plan gate during QA read, while the delegated prompt supplied Reviewer implementation gate pass. QA proceeded from the newer Orchestrator delegation and recorded the mismatch.

## Environment

- Workspace: `D:\PythonProject\connlab`
- Frontend app: `http://localhost:5173`
- Browser smoke: temporary system Chrome headless screenshots at 1280 x 900.
- In-app browser attempt: failed with `Timed out waiting for the Browser webview to attach for this browser-use page`; QA used system Chrome/CDP/native screenshots as fallback.

## Validation Commands

Focused Workbench tests:

```powershell
cd frontend
npm test -- --run projectWorkbenchShellModel projectWorkbenchLifecycleSelectors ProjectWorkbenchLayout --watch=false
```

Observed:

- Test files: 3 passed
- Tests: 67 passed

Frontend build:

```powershell
cd frontend
npm run build
```

Observed:

- Build passed.
- Existing Vite warning only: chunk larger than 500 kB after minification.

Package whitespace/diff checks:

```powershell
git diff --check -- frontend/src/features/project-workbench/projectWorkbenchShellModel.ts frontend/src/features/project-workbench/projectWorkbenchShellModel.test.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx frontend/src/workbench.css docs/lane_evidence/TASK_344C_no-matrix-workbench-empty-state-alignment_developer.md
```

Observed:

- Passed with LF/CRLF working-copy warnings only.

Trailing whitespace scan on TASK_344C package files:

- No matches.

## Data Selection

Read-only candidate scan found active no-Matrix projects:

Registered/no-Matrix:

- Project ID: `7c55618e2acc41bd9973b7e4eaaf7e0f`
- Display ID: `DL-2026-05-002`
- Registry status: `ltr_registered`
- `has_registered_ltr`: `true`
- Lifecycle: `active`
- Allowed lifecycle actions: `stop,close`
- Active Matrix snapshot: HTTP 404

Temporary/no-LTR no-Matrix:

- Project ID: `c4f39233742949febda453a428bd5e42`
- Display ID: `TMP-C4F39233`
- Registry status: `draft`
- `has_registered_ltr`: `false`
- Lifecycle: `active`
- Allowed lifecycle actions: `stop,close`
- Active Matrix snapshot: HTTP 404

Matrix Editor route checks:

- `http://localhost:5173/projects/7c55618e2acc41bd9973b7e4eaaf7e0f/matrix-editor` returned HTTP 200 and rendered the existing Matrix Editor page.
- `http://localhost:5173/projects/c4f39233742949febda453a428bd5e42/matrix-editor` returned HTTP 200 and rendered a Matrix Editor page.

## Browser Smoke

Screenshot artifacts:

- `docs/lane_evidence/artifacts/TASK_344C_qa/registered_no_matrix_DL-2026-05-002_native.png`
- `docs/lane_evidence/artifacts/TASK_344C_qa/temporary_no_ltr_no_matrix_TMP-C4F39233_native.png`
- `docs/lane_evidence/artifacts/TASK_344C_qa/registered_matrix_editor_route_DL-2026-05-002.png`
- `docs/lane_evidence/artifacts/TASK_344C_qa/temporary_matrix_editor_route_TMP-C4F39233.png`

Registered/no-Matrix observation:

- Unified Workbench shell is shown.
- `Project Workbench actions` commandbar is visible.
- `Matrix Editor` is visible/enabled.
- `Fee Evaluation` is visible but disabled.
- `Basic Information` is visible/enabled.
- `Create project folder` is visible but disabled.
- Matrix region shows `No active Matrix` and prompts the operator to open Matrix Editor.
- Downstream outputs copy says they are available after active Matrix authority is confirmed.
- Stop and Close lifecycle controls are visible, matching `allowed_actions: ["stop","close"]`.
- No old full-page registered setup surface was observed.

Temporary/no-LTR no-Matrix observation:

- Unified Workbench shell is shown.
- `Project Workbench actions` commandbar is visible.
- `Matrix Editor` is visible/enabled.
- `Fee Evaluation` is visible but disabled.
- `Basic Information` is visible/enabled.
- `Create project folder` is visible but disabled.
- Matrix region shows `No active Matrix` and prompts the operator to open Matrix Editor.
- Project setup card says `Temporary project before LTR registration`.
- The page does not imply official package output readiness.
- Stop/Admin Close behavior follows lifecycle allowed actions.
- No old full-page temporary-planning setup surface was observed.

## Blocking Finding

### B1 - Temporary/no-LTR Workbench shows contradictory lifecycle/delete state copy

Severity: blocking for TASK_344C QA.

Repro steps:

1. Open `http://localhost:5173/projects/c4f39233742949febda453a428bd5e42`.
2. Observe the unified Workbench shell.
3. In the Matrix workspace, observe `Project setup: Temporary project before LTR registration`.
4. In the lifecycle panel, observe heading/copy `Stop or safely remove this temporary record`.
5. In the same lifecycle panel, observe blocker text `Project is not a temporary planning project.`

Read-only API confirmation:

```powershell
Invoke-RestMethod -Uri 'http://localhost:5173/api/projects/c4f39233742949febda453a428bd5e42/lifecycle' -Method Get
Invoke-RestMethod -Uri 'http://localhost:5173/api/projects/c4f39233742949febda453a428bd5e42/delete-preview' -Method Get
```

Observed:

- Lifecycle response: `lifecycle_state = active`, `status = draft`, `allowed_actions = ["stop","close"]`.
- Delete preview response: `can_delete = false`, `blockers = ["Project is not a temporary planning project."]`, `recommended_action = "stop"`.

Expected:

- The temporary/no-LTR no-Matrix Workbench should present one coherent lifecycle story.
- If the project is a temporary/no-LTR planning project, the delete-preview blocker should not say it is not temporary planning.
- If delete is not available for a valid reason, the UI should expose a business-readable blocker that does not contradict the same page's `Temporary project before LTR registration` state.

Actual:

- The UI simultaneously presents the project as temporary/no-LTR and not temporary planning.

Recommended owner:

- Developer fix pass to triage the Workbench lifecycle/delete UI and determine whether to suppress/translate the conflicting blocker or align the delete-preview state.
- If the root cause is an API/domain definition ambiguity, route Planner/User for a separate boundary decision.

## Scope Safety

QA did not modify:

- frontend product source/tests/CSS
- backend/API/schema/frontend API client
- Projects list/TASK_344B
- TASK_344A fixture/procedure
- Matrix Editor business logic
- TASK_343A/TASK_343B accepted implementation
- `docs/task_board.md`
- governance/orchestration residuals
- merge/commit/push/destructive operations

Status check observed existing dirty/untracked files outside QA's evidence write:

- `docs/task_board.md` modified before QA evidence write.
- TASK_344C task/plan/developer evidence files are untracked in the current worktree.

QA-created files:

- `docs/lane_evidence/TASK_344C_no-matrix-workbench-empty-state-alignment_qa.md`
- `docs/lane_evidence/artifacts/TASK_344C_qa/`

## QA Result

Initial QA gate: blocked.

Blocking product behavior: temporary/no-LTR no-Matrix Workbench contains contradictory state copy on the lifecycle/delete surface.

Recommended next role: Developer fix pass.

## QA Re-Smoke

Status: qa_pass
Date: 2026-06-28

Re-smoke objective:

- Re-test the exact B1 temporary/no-LTR path.
- Confirm the contradictory delete/lifecycle copy is gone.
- Reconfirm the broader TASK_344C no-Matrix unified shell smoke remains passing.

### Re-Smoke Validation

Focused Workbench tests:

```powershell
cd frontend
npm test -- --run projectWorkbenchShellModel projectWorkbenchLifecycleSelectors ProjectWorkbenchLayout --watch=false
```

Observed:

- Test files: 3 passed
- Tests: 68 passed

Frontend build:

```powershell
cd frontend
npm run build
```

Observed:

- Build passed.
- Existing Vite warning only: chunk larger than 500 kB after minification.

Package diff check:

```powershell
git diff --check -- frontend/src/features/project-workbench/projectWorkbenchShellModel.ts frontend/src/features/project-workbench/projectWorkbenchShellModel.test.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/workbench.css docs/lane_evidence/TASK_344C_no-matrix-workbench-empty-state-alignment_developer.md
```

Observed:

- Passed with LF/CRLF working-copy warnings only.

Trailing whitespace scan on fix-pass files:

- No matches.

### Re-Smoke Data

B1 temporary/no-LTR fixture:

- Project ID: `c4f39233742949febda453a428bd5e42`
- Display ID: `TMP-C4F39233`
- URL: `http://localhost:5173/projects/c4f39233742949febda453a428bd5e42`
- Lifecycle API: `active`, `draft`, `readonly = false`, `allowed_actions = stop,close`
- Active Matrix snapshot: HTTP 404
- Delete preview API still returns the raw backend blocker `Project is not a temporary planning project.`, which is acceptable only because the Workbench UI now translates it into business-readable guidance.

Registered/no-Matrix regression fixture:

- Project ID: `7c55618e2acc41bd9973b7e4eaaf7e0f`
- Display ID: `DL-2026-05-002`
- URL: `http://localhost:5173/projects/7c55618e2acc41bd9973b7e4eaaf7e0f`
- Lifecycle API: `active`, `ltr_registered`, `readonly = false`, `allowed_actions = stop,close`
- Active Matrix snapshot: HTTP 404

Route checks:

- Temporary Workbench URL returned HTTP 200.
- Registered Workbench URL returned HTTP 200.
- Temporary Matrix Editor route returned HTTP 200.
- Registered Matrix Editor route returned HTTP 200.

### Re-Smoke Browser Artifacts

New screenshots:

- `docs/lane_evidence/artifacts/TASK_344C_qa/resmoke_B1_temporary_no_ltr_TMP-C4F39233.png`
- `docs/lane_evidence/artifacts/TASK_344C_qa/resmoke_registered_no_matrix_DL-2026-05-002.png`

Temporary/no-LTR B1 re-smoke observation:

- Unified Workbench shell remains visible.
- `Project Workbench actions` commandbar remains visible.
- `Matrix Editor` remains visible/enabled.
- `Fee Evaluation` remains visible but disabled.
- `Basic Information` remains visible/enabled.
- `Create project folder` remains visible but disabled.
- Matrix region still shows `No active Matrix`.
- Project setup still says `Temporary project before LTR registration`.
- Lifecycle/delete panel no longer shows raw `Project is not a temporary planning project.`.
- Lifecycle/delete panel no longer uses the delete-available heading `Stop or safely remove this temporary record`.
- Current visible heading: `Stop this temporary project lifecycle`.
- Current visible guidance: `Temporary deletion is unavailable here. Stop the project if work should not continue.`
- Disabled `Delete temporary project` remains visible without implying deletion is currently available.

Registered/no-Matrix regression observation:

- Unified Workbench shell remains visible.
- `Project Workbench actions` commandbar remains visible.
- `Matrix Editor` remains visible/enabled.
- `Fee Evaluation` and `Create project folder` remain disabled until active Matrix authority exists.
- `Basic Information` remains visible/enabled.
- Matrix region still shows `No active Matrix`.

### Re-Smoke Result

B1 status: resolved.

Remaining blocking findings: none.

QA gate: pass.

Recommended next role: Integrator packaging/readiness.
