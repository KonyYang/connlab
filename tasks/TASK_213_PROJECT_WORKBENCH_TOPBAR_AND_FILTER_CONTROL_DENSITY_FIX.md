# TASK_213 Project Workbench Topbar And Filter Control Density Fix

Status: completed
Date: 2026-05-16

## Execution Mode

Single-file task mode. Approved by user as a focused correction after TASK_212.

## Current Phase / Active Task / Allowance

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Current active task:

```text
TASK_213_PROJECT_WORKBENCH_TOPBAR_AND_FILTER_CONTROL_DENSITY_FIX
```

Why this task is allowed:

- TASK_212 completed the Workbench Runtime Console mockup completeness pass.
- User review found two concrete UI defects:
  - filter checkbox/radio icons are too large;
  - the page top content still does not match the approved Project Workbench UI mockup.
- This task is a focused frontend display correction only.

## Model Fit Assessment

Recommended execution model:

```text
GPT-5.3-codex: suitable
```

Reason:

- Bounded frontend CSS/layout correction.
- No backend, API, runtime, DB, Matrix Editor, or persistence scope.

## Goal

Make the Workbench top area closer to the target mockup:

- compact app title/project identity row;
- project metadata and LTR badge inline with project title;
- progress, runtime metrics, and last update on the same top bar;
- readiness strip remains below;
- filter controls use normal product UI checkbox/radio sizing.

## Forbidden Scope

- Backend/API/DB/runtime changes.
- New behavior or write workflows.
- Matrix Editor or StepInstance implementation.

## Validation

Run:

```powershell
npm run build
```

## Execution Record

Completed.

Implemented files:

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/workbench.css`
- `docs/task_board.md`
- board-state guard tests

What was implemented:

- Reworked the Workbench top area into a compact target-mockup-style header:
  - app title and menu affordance on the left;
  - project name, status badge, LTR, BU, and requestor inline;
  - project progress, runtime metrics, last update, and refresh affordance in the same top row.
- Removed the oversized top card feel introduced in TASK_212.
- Locked Runtime Console filter checkbox/radio controls to normal 14px product UI sizing.
- Reduced readiness status dot size.

Validation results:

- `npm run build`
  - passed

Stop condition:

- TASK_213 completed and stopped.
- No backend/API/DB/runtime implementation changes.
