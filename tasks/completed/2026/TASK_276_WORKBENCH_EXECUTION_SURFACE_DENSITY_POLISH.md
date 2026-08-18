# TASK_276_WORKBENCH_EXECUTION_SURFACE_DENSITY_POLISH

## Status

Complete. Implemented and validated on 2026-05-26.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Allowed Reason

TASK_275 is complete and the task board currently has no active implementation task. This task is a controlled frontend-only follow-up created from user smoke-test feedback on the Project Workbench information hierarchy.

## Objective

Polish the Project Workbench first screen so it behaves like a dense laboratory execution surface instead of an explanatory dashboard.

The Workbench should prioritize:

- current LTR/project identity
- Matrix execution map
- selected Step Workspace
- Matrix-related actions and compact execution signals
- total fee placeholder near step context

It should remove duplicated, explanatory, or low-value surfaces that distract from group execution tracking.

## User Feedback Source

This task is based on the TASK_275 follow-up discussion:

- Users care most about which test groups are completed, in progress, not started, or failed.
- Total test item counts and pass counts are not useful on this screen; failed items matter only as exceptions.
- Matrix status color is already visible in the table, so repeated legends and group-header summaries are unnecessary.
- Header identity should start from the LTR or temporary project identifier, followed by product and test description in one line.
- Business unit and requester are not important on this page.
- `Last updated` should become an on-demand `View activity history` affordance.
- The filter card and explanatory Matrix labels add noise.
- `Project issues / reminders` is not needed here.
- `Fee estimate` belongs near the Step Workspace, not as a disconnected bottom card.
- The right Step Workspace is important because it will become the step execution data entry area for test data, images, evidence, result judgement, and completion information.
- The current Step Workspace repeats Matrix metadata and exposes actions that do not belong there.

## Scope

### In Scope

Frontend-only Project Workbench UI changes:

1. Simplify the Workbench header identity into a single line:
   - `DL-2026-05-003 · Coolpower HDF 3.40mm pin · <test description>`
   - If no LTR exists, use a temporary project marker/id instead.
   - Use an existing frontend-available test-description source only; do not add API fields in this task.
   - If no test description is currently available in frontend state, render a stable fallback such as `Test description unavailable`.
   - Do not show business unit or requester in this primary header identity.
2. Replace `Last updated` with `View activity history`.
   - This may remain a non-invasive placeholder if no approved activity modal exists in current scope.
3. Remove top-level execution metric cards that duplicate the Matrix table or bottom surfaces.
4. Move any still-needed Matrix execution signals into the Matrix area only.
   - Keep them compact and directly tied to the Matrix surface.
   - Do not reintroduce a generic dashboard metrics strip.
5. Remove Matrix explanatory labels and redundant copy, including:
   - `Matrix Projection`
   - `Matrix execution projection`
   - `Read-only projection`
   - `Read-only authority view`
   - These strings may currently exist in either `ProjectWorkbenchLayout.tsx` or `ProjectWorkbenchMatrixProjectionPanel.tsx`; both files are in-scope for cleanup.
6. Remove the four-status legend from the Matrix area.
   - The Matrix table status colors and text remain the status carrier.
7. Remove the entire test item category/filter card from the Workbench first screen, including:
   - `Test item category`
   - `Show active items only`
   - `Show status icons`
   - `Show markers`
   - `Status filter`
8. Place `Matrix` and `Test record` controls near the Matrix table because they are Matrix-derived actions.
   - `Matrix` should continue to navigate to Matrix Editor.
   - `Test record` must not trigger unapproved generation behavior in this task; use an existing safe behavior only if already wired, otherwise keep it disabled/placeholder.
9. Remove `Project issues / reminders` from the always-visible Workbench first screen.
10. Move `Fee estimate` below or alongside the right Step Workspace, aligned with that column.
    - Keep total-only fee presentation.
    - Do not implement real fee calculation in this task.
11. Preserve the Matrix table structure introduced in TASK_275:
    - `Test item` plus group columns.
    - bottom rows for `Sample sizes`, `Estimated completion date`, and `Status`.
    - status set limited to `Not started`, `In progress`, `Pass`, and `Failed`.
12. Preserve Matrix token click behavior:
    - clicking a Matrix token updates the right-side Step Workspace selection context.
13. Refocus the right Step Workspace as a future step execution input area:
    - remove repeated static Matrix metadata fields when they duplicate selected context already visible in the Matrix table, including `Test item`, `Section`, `Group`, and `Step token`
    - remove misplaced action buttons: `Edit step`, `Copy to other steps`, and `Generate record`
    - move `Image` next to bottom execution intake actions such as `Import data`
    - collapse `Step Lifecycle` into one dynamic status label instead of rendering the whole process chain
    - separate planned completion and actual completion concepts, for example `Estimated completion` and `Actual completion`
    - add a result judgement area as display/edit placeholder without implementing persistence
    - keep placeholders non-mutating unless an approved API already exists

### Out Of Scope

Do not implement:

- backend/API/domain/storage changes
- StepInstance or execution persistence
- real image/evidence/test-data persistence
- real activity history modal or audit timeline
- real Test Record generation flow placement beyond a safe disabled/placeholder control
- real fee calculation
- result judgement persistence or automated judgement logic
- report generation
- permission, approval, or multi-user workflow
- Matrix Editor behavior changes
- broad design-system rewrites

## Expected Files

Likely frontend and test files:

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
- `frontend/src/features/project-workbench/projectWorkbenchMatrixProjectionSelectors.ts` if compact Matrix-local metrics need selector support
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`

Task tracking files:

- `tasks/TASK_276_WORKBENCH_EXECUTION_SURFACE_DENSITY_POLISH.md`
- `docs/task_276_workbench_execution_surface_density_polish_plan.md`
- `docs/task_board.md`
- `docs/task_plan_index.md`

## Acceptance Criteria

1. Workbench header shows one primary identity line led by the LTR number or temporary project id, followed by product and test description when available, or `Test description unavailable` fallback when not available.
2. Header no longer shows business unit or requester as primary identity content.
3. `Last updated` is no longer shown; `View activity history` is visible as the on-demand history affordance.
4. Top-level metric cards/strip are removed or fully relocated into a compact Matrix-local presentation.
5. The Workbench first screen no longer renders:
   - `Matrix Projection`
   - `Matrix execution projection`
   - `Read-only projection`
   - `Read-only authority view`
   - Matrix four-status legend copy
6. The Workbench first screen no longer renders the test item category/filter card or its controls.
7. Matrix area exposes `Matrix` and `Test record` controls.
8. `Matrix` remains the Matrix Editor navigation action.
9. `Test record` does not introduce active unapproved generation behavior.
10. `Project issues / reminders` is removed from the always-visible first screen.
11. `Fee estimate` is positioned with the right Step Workspace column and remains total-only.
12. Matrix table still renders group columns and bottom rows for sample sizes, estimated completion date, and status.
13. Matrix token clicks still update the right Step Workspace context.
14. Right Step Workspace no longer repeats `Test item`, `Section`, `Group`, or `Step token` as standalone metadata fields when those values are already represented by the selected Matrix context.
15. Right Step Workspace no longer renders `Edit step`, `Copy to other steps`, or `Generate record`.
16. `Image` is positioned with bottom execution intake actions such as `Import data`.
17. Step lifecycle is shown as a compact dynamic status label, not as a full multi-stage process row.
18. Step Workspace distinguishes estimated completion from actual completion.
19. Step Workspace includes a result judgement display/edit placeholder without adding persistence.
20. No backend files are changed.

## Validation Plan

Run targeted frontend and guard validation:

```powershell
cd frontend
npm test -- --run ProjectWorkbenchMatrixProjectionPanel
npm run build
```

Run static and integration guards from repository root:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task276 or task275 or project_workbench"
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
git diff --name-only -- backend
git diff --check
```

Manual smoke path:

```text
http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f
```

Check:

- first viewport is not crowded by explanatory labels or filter controls
- Matrix table remains readable
- `Matrix` action is near the Matrix table
- `Test record` is present but not misleadingly active if functionality is out of scope
- Step Workspace remains visible and follows Matrix token selection
- Step Workspace reads as a step execution input area, not a duplicate Matrix metadata card
- Fee estimate sits under or with the right-side Step Workspace

## Model Fit Assessment

`GPT-5.3-codex` is suitable for execution.

Reason:

- The task is a scoped frontend refactor/polish task with existing React components, tests, and static guards.
- It requires careful UI hierarchy judgment, but no new backend architecture, storage migration, or algorithmic uncertainty.
- The main risks are accidental reintroduction of hidden functionality or removal of still-needed Step Workspace wiring; these can be controlled through targeted tests and browser smoke checks.

## Implementation Protocol

Implementation must not start until the user explicitly approves this task and plan.

Recommended execution mode:

```text
superpowers:executing-plans
```

Use a serial implementation flow, with tests/guards updated alongside each UI surface change.
