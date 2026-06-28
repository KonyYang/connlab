# TASK_344C No-Matrix Workbench Empty State Alignment

Status: complete - Integrator accepted
Lane: `no-matrix-workbench-empty-state-alignment`
Owner Roles: Planner / Frontend Developer / Reviewer / QA / Integrator
Last Updated: 2026-06-28

## Goal

Align the Project Workbench experience for projects that do not yet have an active Matrix.

After a New Project receives an LTR number, and when a temporary project opens before LTR registration, operators should still land in the unified Workbench shell. The main Matrix workspace may show an empty state or simple instruction to open Matrix Editor, but the page should not look like a different setup page.

## User-Confirmed Scope

- Registered project with no active Matrix uses the unified Workbench layout.
- Temporary/no-LTR project uses the same unified Workbench layout pattern.
- The Matrix display area can be empty or show a concise prompt to use `Matrix Editor`.
- The rest of the Workbench layout should remain visually consistent with the active Matrix Workbench.

## In Scope

- Frontend-only Workbench shell and no-Matrix empty-state alignment.
- Registered/no-Matrix and temporary/no-LTR Workbench states.
- Preserve current lifecycle badges and state meaning, including `No Matrix`.
- Preserve Matrix as the primary operational workspace.
- Preserve TASK_343A Stop/Resume and TASK_343B Close completed/admin behavior.
- Focused Workbench tests and browser smoke expectations.

## Out Of Scope

- Backend, API, schema, database, migrations, or frontend API client changes.
- Matrix Editor business logic, Matrix draft creation rules, or authority publication rules.
- Projects list / registry behavior from TASK_343C or TASK_344B.
- Closed smoke data fixture/procedure from TASK_344A.
- StepInstance, Report generation, execution persistence, AI, permissions, LAN/server, or multi-user scope.

## May Touch

Planning/activation:

- `tasks/TASK_344C_NO_MATRIX_WORKBENCH_EMPTY_STATE_ALIGNMENT.md`
- `docs/task_344c_no_matrix_workbench_empty_state_alignment_plan.md`
- `docs/lane_evidence/TASK_344C_no-matrix-workbench-empty-state-alignment_planner.md`
- `docs/task_board.md`

Future implementation after Reviewer plan gate and explicit implementation routing:

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
- QA evidence and screenshots under `docs/lane_evidence/` if routed to QA.

## Must Not Touch

- `backend/**`
- `frontend/src/api/client.ts`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- Matrix Editor implementation beyond existing navigation/open affordance.
- TASK_343A / TASK_343B accepted behavior except where no-Matrix layout composition naturally hosts existing controls.
- TASK_344A smoke data fixture/procedure.
- Public-drive, Office, LTR authority files.
- Unrelated governance/orchestration residuals.

## UX Contract

- The page should feel like the same Project Workbench, not a separate Matrix setup page.
- The Workbench header and command area should remain stable across active Matrix, registered/no-Matrix, and temporary/no-LTR states.
- `Matrix Editor` remains the primary way to create or edit Matrix authority.
- The Matrix workspace region should show a concise no-Matrix empty state when no active Matrix exists.
- Business-readable copy must avoid exposing backend enum tokens.
- No direct lifecycle mutation controls are added to Projects list by this task.

## Validation Gate

Before implementation can be accepted:

- Focused Workbench tests cover active Matrix unchanged, registered/no-Matrix unified shell, temporary/no-LTR unified shell, stopped readonly behavior, and closed archive behavior.
- Tests confirm Stop/Resume/Close visibility remains governed by existing lifecycle `allowed_actions`.
- Tests confirm no Projects list, backend, API client, or Matrix Editor business behavior changes.
- `npm run build` from `frontend/` passes, or blockers are documented.
- `git diff --check` passes for the approved package.
- Browser or manual smoke verifies a New Project after LTR registration lands in the unified no-Matrix Workbench shell.

## Merge Gate

Merge remains blocked until Developer implementation evidence, Reviewer implementation gate, QA/browser smoke gate if requested, and Integrator packaging/readiness gate all pass.

## Integrator Closeout

Integrator accepted TASK_344C after Reviewer implementation re-gate and QA re-smoke gate passed.

Accepted package includes the TASK_344C task/plan/evidence/QA artifacts, board closeout, and approved Workbench frontend files for the unified no-Matrix shell. `ProjectWorkbenchCloseConfirmation.tsx` is included as a compatible Workbench package input because the compact lifecycle dock now passes a compact close-confirmation variant through `ProjectWorkbenchLifecycleSections.tsx`.

Stop point: local controlled commit only. Remote push intentionally not performed.
