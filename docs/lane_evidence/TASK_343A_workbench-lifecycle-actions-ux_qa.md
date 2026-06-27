# QA Evidence - TASK_343A Workbench Lifecycle Actions UX

Status: `qa_pass`
Task: `TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX`
Lane: `workbench-lifecycle-actions-ux`
Role: QA / Smoke Owner
Last updated: 2026-06-27

## Role Boundary

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active task: `TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX`.
- Current lane: `workbench-lifecycle-actions-ux`.
- Why this QA gate is allowed: delegated Reviewer result states `reviewer_pass`; the implementation re-gate passed after the side-stripe blocker was fixed, no blocking finding remained, and the lane requires QA because it changes the main Workbench operator flow.
- QA boundary: run validation and write QA evidence/checkpoint only.
- Stop point: do not modify product code, do not update `docs/task_board.md`, do not merge/commit/push, and do not start Integrator.

## Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343_project_workbench_lifecycle_actions_ux_plan.md`
- `tasks/TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343a_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md`
- `docs/lane_evidence/TASK_338_write-guard-integration_developer.md`
- `docs/lane_evidence/TASK_339A_frontend-readonly-model_developer.md`
- `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md`
- `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_qa.md`

## Environment

- Workspace: `D:\PythonProject\connlab`
- Shell: Windows PowerShell with explicit UTF-8 output
- Frontend working directory: `D:\PythonProject\connlab\frontend`
- Date: 2026-06-27
- Browser tooling: no reliable navigable browser/screenshot tool was exposed in this thread. Tool discovery returned Node REPL capability, not a direct in-app browser control surface for `/projects` walkthrough.

## Validation Commands And Results

### Focused Frontend Stop/Resume UX Tests

Command run from `D:\PythonProject\connlab\frontend`:

```powershell
npm test -- --run src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts src/features/project-workbench/useProjectWorkbenchModel.test.tsx src/features/project-workbench/ProjectWorkbenchLayout.test.tsx
```

Observed result:

- `3` test files passed.
- `60` tests passed.
- No failing tests.

Coverage included lifecycle action derivation, Workbench model Stop/Resume handlers, inline confirmation behavior, stopped readonly Resume path, closed no-action states, no Close controls, Matrix primary order, and state refresh behavior.

### Frontend Build

Command run from `D:\PythonProject\connlab\frontend`:

```powershell
npm run build
```

Observed result:

- TypeScript/Vite build passed.
- Vite transformed `110` modules and completed successfully.
- Existing non-blocking chunk-size warning remained for a post-minification JS chunk over `500 kB`.

### Diff Whitespace Check

Command run from `D:\PythonProject\connlab`:

```powershell
git diff --check -- frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/workbench.css docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md
```

Observed result:

- Passed with no whitespace errors.
- Git printed LF/CRLF working-copy warnings only.

### Trailing Whitespace Scan

Command run from `D:\PythonProject\connlab`:

```powershell
rg -n "[ \t]$" frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/workbench.css docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md
```

Observed result:

- No matches.
- Exit code `1` means `rg` found no trailing whitespace.

### Production No-Close Scan

Command run from `D:\PythonProject\connlab`:

```powershell
rg -n --glob '!*.test.ts' --glob '!*.test.tsx' "closeProjectCompletedLifecycle|closeProjectAdministrativeLifecycle|Close project|Close as completed|Close administratively|output_summary_acknowledged|close_note" frontend/src/features/project-workbench frontend/src/workbench.css
```

Observed result:

- No matches.
- Exit code `1` means TASK_343A production Workbench code exposes no Close control/copy, close confirmation field, close output acknowledgement, or close API call from this scan.

### Thick Side-Stripe Scan

Command run from `D:\PythonProject\connlab`:

```powershell
git diff -U0 -- frontend/src/workbench.css | rg "^\+.*border-(left|right): [2-9]"
```

Observed result:

- No matches.
- Exit code `1` means the changed CSS diff adds no `border-left` or `border-right` value greater than `1px`.

### Forbidden Scope Status

Command run from `D:\PythonProject\connlab`:

```powershell
git status --short -- frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx frontend/src/api/client.ts backend tests tasks/TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW.md tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md docs/task_board.md
```

Observed result:

```text
 M docs/task_board.md
```

Interpretation:

- No backend/API/schema files are modified in this scope check.
- No root `tests/` files are modified.
- `frontend/src/api/client.ts` is not modified.
- No Projects registry implementation or `ProjectListPage` changes are present.
- TASK_343B/TASK_343C files are not modified.
- `docs/task_board.md` remains a known pre-existing residual and was not edited by QA.

### TASK_343A Package Status Snapshot

Command run from `D:\PythonProject\connlab`:

```powershell
git status --short -- frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/workbench.css docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_qa.md
```

Observed result before writing this QA evidence:

- Modified TASK_343A frontend Workbench files matched the Developer implementation package.
- `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md` was present as untracked/changed lane evidence.
- `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_qa.md` did not exist yet.

QA added only this QA evidence file.

## QA Coverage Result

1. Focused frontend tests for Workbench Stop/Resume lifecycle UX: pass, `3` files / `60` tests.
2. Frontend build: pass, with existing Vite chunk-size warning only.
3. `git diff --check`: pass, LF/CRLF warnings only.
4. Trailing whitespace scan: pass, no matches.
5. Production no-Close scan: pass, no matches.
6. Changed CSS thick side-stripe scan: pass, no matches.
7. Forbidden scope status: pass; no backend/API/schema/frontend API client/Projects registry/TASK_343B/TASK_343C changes observed, aside from known pre-existing `M docs/task_board.md` residual.
8. Browser `/projects` and Workbench URL smoke: not executed because no reliable browser control/screenshot tool was available in this thread.

## Operator Flow Assertions Covered By Automated/Static Evidence

- Active project states expose Stop only when allowed by lifecycle action data.
- Active registered and active temporary states expose no Close affordance.
- Stopped state shows readonly reason and Resume only when allowed.
- Closed completed/admin states expose no Stop, no Resume, and no Close controls.
- Matrix remains primary in active Matrix workspace; lifecycle action UI remains compact and secondary.
- Stop/Resume call existing lifecycle API helpers and refresh lifecycle/project state in the Workbench model.
- No Close API helper is imported or called by TASK_343A production Workbench code paths in the no-Close scan.
- The reviewer-identified thick side-stripe issue remains fixed in the changed CSS diff.

## Residual Risk

Real browser smoke for `/projects`, a concrete Workbench URL, narrow viewport overlap, and keyboard tab order was not performed because this thread did not expose a direct browser control surface. This is accepted as a non-blocking QA residual because focused component/model tests, source scans, CSS diff checks, and build validation cover the TASK_343A contract at the available QA level.

## Decision

QA gate: pass.

No QA-blocking finding was found.

Recommended next role: Integrator packaging/readiness.

## Stop Point

Stop after QA evidence and completion callback. Do not modify product code, update board, merge, commit, push, start Integrator, or start TASK_343B/TASK_343C from this QA role.
