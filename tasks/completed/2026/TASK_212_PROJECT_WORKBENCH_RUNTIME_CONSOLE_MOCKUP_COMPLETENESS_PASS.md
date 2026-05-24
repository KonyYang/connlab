# TASK_212 Project Workbench Runtime Console Mockup Completeness Pass

Status: completed
Date: 2026-05-16

## Execution Mode

Single-file task mode.

This task is approved for direct execution by the user after TASK_211 completion. Do not create a
separate plan document.

## Current Phase / Active Task / Allowance

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Current active task:

```text
TASK_212_PROJECT_WORKBENCH_RUNTIME_CONSOLE_MOCKUP_COMPLETENESS_PASS
```

Why this task is allowed:

- TASK_211 replaced Workbench IA with a Runtime Console baseline, but the first screen is still too
  sparse and does not match the approved Project Workbench Runtime Console mockup.
- The user approved using placeholder/mock projection data to make all required first-screen surfaces
  visible for business validation.
- This task improves frontend display completeness only.

## Model Fit Assessment

Recommended execution model:

```text
GPT-5.3-codex: suitable
```

Reason:

- This is a bounded frontend UI completeness pass using existing Workbench and runtime projection
  display boundaries.
- No backend, persistence, API contract, runtime engine, or Matrix Editor implementation is needed.
- GPT-5.5 would be preferable for pixel-level visual matching, but GPT-5.3-codex is sufficient for
  a controlled high-density skeleton aligned to the target mockup.

## Goal

Make the Project Workbench first screen closely resemble the approved `Project workbench UI.png`
direction, with complete placeholder surfaces where real runtime data is not yet implemented.

The priority is visible business validation, not full functionality.

## Approved User Decisions

- Matrix table, Step Workspace, issue attention, recent activity, and fee estimate surfaces may use
  fixed placeholder/mock data when real runtime projection data is unavailable.
- Step Workspace action buttons should be visible now, but write actions remain disabled/placeholders.
- Setup Manager remains a secondary entry: a top button plus compact folded setup/output sections.

## Allowed Scope

- Frontend-only Workbench UI changes.
- Dense Runtime Console first-screen layout.
- Placeholder Matrix Overview table.
- Placeholder Step Workspace detail panel.
- Placeholder runtime issues, recent activity, fee estimate, data table, workflow, and notes surfaces.
- CSS updates for Workbench layout density and visual hierarchy.
- Task board and relevant static tests.

## Forbidden Scope

- Backend changes.
- API/DTO changes.
- DB/schema/migration changes.
- Runtime engine, projection engine, report sync engine, evidence storage, notification system.
- Matrix Editor implementation or Matrix definition editing inside Workbench.
- StepInstance persistence or execution write flows.

## Acceptance Criteria

TASK_212 is complete when:

- First screen includes top project header, lifecycle strip, filter toolbar, Matrix table, right Step
  Workspace, runtime issue cards, recent activity, fee estimate, and setup entry.
- Matrix table is dense enough to visually validate group/step execution map behavior even when real
  projection data is unavailable.
- Step Workspace contains status, executor, completion time, tabs, overview facts, data summary,
  lifecycle flow, placeholder actions, notes, and save button.
- Setup/output/folder/evidence/lookup areas remain secondary and compact.
- No backend/API/DB/runtime implementation changes are made.
- `npm run build` passes.

## Execution Record

Completed.

Implemented files:

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixOverview.tsx`
- `frontend/src/workbench.css`
- `docs/task_board.md`
- board-state guard tests

What was implemented:

- Expanded the Project Workbench first screen to match the approved Runtime Console mockup direction.
- Added a dense lifecycle/readiness strip with Setup Manager entry.
- Added a runtime filter toolbar.
- Added a high-density placeholder Matrix Overview table with test items, sections, methods,
  conditions, requirements, and G1-G12 group columns.
- Added clickable placeholder step tokens so the right Step Workspace can be visually validated
  before real runtime execution data exists.
- Expanded Step Workspace with status, executor, completion time, tabs, overview facts, test data
  summary, lifecycle flow, disabled placeholder actions, notes, and save control.
- Added bottom runtime issue attention, recent activity, and fee estimate surfaces.
- Kept folder, approval, evidence, lookup, and output status as secondary surfaces rather than
  the Workbench main visual priority.

Validation results:

- `npm run build`
  - passed
- `py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q`
  - 17 passed
- `py -m pytest tests\unit\test_frontend_shell_files.py -q`
  - 56 passed, 9 failed
  - remaining failures are known historical static assertion drift outside TASK_212 scope

Stop condition:

- TASK_212 completed and stopped.
- Did not implement backend/API/DB/runtime engine/StepInstance/Matrix Editor/report/evidence systems.
- Did not auto-enter the next task.
