# TASK_214 Project Workbench Mockup Visual Clone Density Pass

Status: completed
Date: 2026-05-16

## Execution Mode

Single-file task mode. Approved by user as a focused visual clone correction after TASK_213.

## Current Phase / Active Task / Allowance

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Current active task:

```text
TASK_214_PROJECT_WORKBENCH_MOCKUP_VISUAL_CLONE_DENSITY_PASS
```

Why this task is allowed:

- TASK_212/TASK_213 added the required Runtime Console surfaces.
- User review shows the result still does not visually match the approved Project Workbench UI mockup.
- This task tightens visual density and layout proportions only.

## Model Fit Assessment

Recommended execution model:

```text
GPT-5.3-codex: suitable
```

Reason:

- Bounded frontend CSS/layout tuning.
- No backend, API, DB, runtime engine, Matrix Editor, or StepInstance scope.

## Goal

Make the Workbench first screen visually closer to the approved mockup:

- compact top region;
- normal-sized controls;
- G1-G12 Matrix columns visible with dense table sizing;
- right Step Workspace closer to mockup width and information density;
- fewer oversized paddings, fonts, and row heights.

## Forbidden Scope

- Backend/API/DB changes.
- Runtime implementation or persistence.
- Matrix Editor implementation.
- New write workflows.

## Validation

Run:

```powershell
npm run build
```

## Execution Record

Completed.

Implemented files:

- `frontend/src/workbench.css`
- `docs/task_board.md`
- board-state guard tests

What was implemented:

- Tightened Workbench page outer spacing so the Runtime Console uses the viewport more like the
  approved mockup.
- Reduced topbar padding, metric spacing, and top region visual height.
- Reduced Matrix table `min-width`, row/cell padding, font size, group column width, and token badge
  size so more G1-G12 content is visible at once.
- Reduced Step Workspace width and internal field/data/lifecycle spacing.
- Reduced note area, data summary, lifecycle flow, and bottom surface density.

Validation results:

- `npm run build`
  - passed

Stop condition:

- TASK_214 completed and stopped.
- No backend/API/DB/runtime implementation changes.
