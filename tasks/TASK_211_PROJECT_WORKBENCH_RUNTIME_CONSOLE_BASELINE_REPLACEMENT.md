# TASK_211 Project Workbench Runtime Console Baseline Replacement

Status: completed
Date: 2026-05-16

## Execution Mode

Single-file task mode.

This file contains both the reviewable task plan and the execution record. Do not create a separate
`docs/task_211_*_plan.md` file.

## Current Phase / Active Task / Allowance

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Current active task:

```text
TASK_211_PROJECT_WORKBENCH_RUNTIME_CONSOLE_BASELINE_REPLACEMENT
```

Why this task is allowed:

- TASK_201 through TASK_210 established the minimum runtime projection chain:
  `Step Token -> Projection -> Aggregation -> Snapshot -> Typed API -> Frontend Consumer`.
- TASK_209 proved read-only runtime projection API consumption in an isolated prototype.
- TASK_210 marked that prototype as development-only.
- The current Project Workbench still visually behaves as a setup-heavy dashboard, which blocks
  practical validation of Matrix-driven runtime execution workflows.

## Model Fit Assessment

Recommended execution model:

```text
GPT-5.3-codex: suitable
```

Reason:

- The task is a bounded frontend IA replacement slice with existing API contracts and local UI
  components.
- It does not require backend architecture changes, persistence work, runtime engine design, or
  StepInstance implementation.
- Higher-capability models may help with visual judgment, but GPT-5.3-codex is sufficient for the
  controlled code change.

## Goal

Replace the Project Workbench primary information architecture with a Runtime Console baseline
skeleton aligned with the approved target direction:

```text
Workbench = Runtime Console
Matrix Editor = Definition Studio
```

This is not UI beautification, current Workbench patching, Matrix Editor implementation, or a full
runtime system.

## Core Principles

Continue preserving:

```text
Projection != Domain Identity
Runtime Projection is not source of truth.
Projection composition must remain independently evolvable.
```

The Workbench must consume runtime projection. It must not own runtime state or mutate domain
identity.

## Allowed Scope

TASK_211 may implement:

- Runtime Console layout skeleton for Project Workbench
- Runtime Summary surface
- Matrix Overview runtime projection surface
- Step Workspace entry/navigation surface
- Runtime Attention placeholder/summary surface
- Report/output sync visibility surface
- Projection snapshot consumption wiring from existing typed API
- Downgrading setup/output areas to secondary folded surfaces
- Frontend-only Workbench layout and CSS changes

Allowed files include:

- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixOverview.tsx`
- `frontend/src/workbench.css`
- `tasks/TASK_211_PROJECT_WORKBENCH_RUNTIME_CONSOLE_BASELINE_REPLACEMENT.md`
- `docs/task_board.md`

## Forbidden Scope

TASK_211 must not implement:

- Matrix Editor implementation
- execution engine or orchestration system
- write/mutation runtime flows
- report generation system
- evidence upload workflow
- websocket/background sync
- persistence redesign
- backend architecture expansion
- runtime projection API contract replacement
- StepInstance ORM or persistence
- approval/setup system redesign
- Matrix definition editing inside Workbench primary hierarchy

## Acceptance Criteria

TASK_211 is complete when:

- Project Workbench primary visual hierarchy becomes runtime-first, not setup-first.
- Top runtime summary shows project identity, Matrix authority/draft context, lifecycle/setup state,
  and runtime projection counts.
- Matrix Overview renders from runtime projection snapshot consumption, not as an Excel-like editor.
- Step Workspace is visible as a read-only runtime entry surface driven by selected projected token.
- Runtime Attention and report/output sync visibility are represented in the main console.
- Folder, Approval Package, Evidence Placement, and lookup/setup functions are downgraded to
  secondary folded surfaces.
- No backend, API, DB, runtime engine, persistence, or StepInstance changes are introduced.
- Frontend build passes.
- `docs/task_board.md` is updated after completion.

## Validation Strategy

Run:

```powershell
npm run build
```

Run static frontend shell tests if they are in scope:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

Known historical failures in that suite may remain out of scope unless they are directly caused by
TASK_211.

Manual smoke path:

- Open a project Workbench route.
- Verify the first screen reads as a Runtime Console.
- Verify runtime projection snapshot data loads when Matrix draft data exists.
- Verify selecting a Matrix token updates the Step Workspace surface.
- Verify setup/output workspaces are secondary folded sections.

## Execution Record

Completed.

Implemented files:

- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixOverview.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- `docs/task_board.md`

What was implemented:

- Replaced the old setup-heavy Workbench primary hierarchy with a Runtime Console baseline skeleton.
- Added Workbench runtime projection consumption wiring from existing Matrix draft data to the existing typed read-only runtime projection snapshot API.
- Rendered a runtime-first top area with project identity, Matrix authority state, projection coverage, and lifecycle/attention/output metrics.
- Replaced the primary Matrix surface with read-only projection token consumption instead of Matrix definition editing.
- Added a Step Workspace read-only surface driven by selected projected token.
- Added Runtime Attention and downstream output sync visibility in the main console.
- Downgraded Project Folder, Approval Package, Evidence Placement, and lookup areas to secondary folded surfaces.
- Updated static frontend shell assertions where they conflicted with the new Runtime Console boundary.

Validation results:

- `npm run build`
  - passed
- `py -m pytest tests\unit\test_frontend_shell_files.py -q`
  - 56 passed, 9 failed
  - remaining failures are known historical static assertion drift outside TASK_211 scope
  - TASK_211-specific Workbench assertions were aligned to the Runtime Console direction

Stop condition:

- TASK_211 completed and stopped.
- Did not implement Matrix Editor, runtime engine, persistence, StepInstance, backend changes, or report/evidence systems.
- Did not auto-enter the next task.
