# TASK_219E_WORKBENCH_RUNTIME_CONSOLE_REGRESSION_GUARDS

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

None. `TASK_219E` regression guards are implemented.

## Why This Task Is Allowed Now

Recent Workbench iterations moved quickly:

- Runtime Projection Prototype
- Runtime Console baseline
- Workbench mockup completeness
- Matrix Editor placeholder route
- Matrix Editor visual/pixel alignment

The new product conclusion changes the Workbench boundary again. Static regression guards are needed so future tasks do not reintroduce old behavior:

- Workbench as a complex setup workbench
- large manual output-preparation forms
- Step execution persistence before approval
- report/image/data-entry actions presented as available
- Matrix editing controls inside Workbench instead of Matrix Editor

## Model Fit Assessment

`GPT-5.3-codex` is suitable because this is a bounded test/documentation guard task that checks file content and route boundaries. It requires precision but not deep algorithmic work.

## Objective

Add regression guards that encode the new Workbench Runtime Console boundary.

The guards should prevent:

- large approval package manual path form from returning to the main Workbench surface
- folder/evidence/lookup panels from becoming the primary lower-half IA again
- Matrix Definition Studio controls from being implemented inside Workbench
- future-scope Step execution/report/image persistence from appearing as active Workbench behavior
- direct `fetch()` or filesystem/Office operations outside approved layers

## Existing Code Context

Likely test file:

- `tests/unit/test_frontend_shell_files.py`

Relevant frontend files:

- `frontend/src/pages/ProjectWorkbenchPage.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/pages/ProjectMatrixEditorPage.tsx`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/api/client.ts`

Relevant docs:

- `AGENTS.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `docs/task_board.md`

## Scope

Allowed:

- static tests for frontend boundaries
- documentation guard updates if needed
- test-only changes unless a small copy marker is required
- create an implementation plan document before code

Forbidden:

- frontend redesign
- backend/API/DB changes
- StepInstance/report/image/evidence persistence implementation
- changing route behavior
- broad rewriting of existing historical tests

## Execution Result

Implemented static regression guards in:

- `tests/unit/test_frontend_shell_files.py`

Added `test_task219e_runtime_console_regression_guards_keep_workbench_boundary` to assert:

- Workbench remains Runtime Console first (`runtime-console-shell`, `Step Workspace`, runtime attention surface).
- Setup/Evidence stays secondary via Setup Manager collapsibles.
- Matrix edit actions are not hosted in Workbench layout.
- Matrix definition editing remains routed to `ProjectMatrixEditorPage`.
- `fetch()` remains outside Workbench page/layout/model and in API client.

## Implementation Guidance After Approval

Suggested guard categories:

- `ProjectWorkbenchLayout` contains Runtime Console primary labels.
- Workbench does not render Matrix draft edit/validate/confirm controls directly.
- Workbench does not expose active Step persistence buttons.
- Approval package form labels are absent from the primary Workbench layout after TASK_219A, or only present in explicitly named support/advanced component files.
- `ProjectMatrixEditorPage` remains the route for Matrix definition editing.
- API client remains the only fetch boundary.

## Acceptance Criteria

- Guards fail if Workbench is turned back into a broad setup/preparation page.
- Guards allow Matrix Editor to remain the definition-editing surface.
- Guards do not block legitimate support-status summaries.
- Tests are narrow enough to avoid brittle visual pixel assertions.
- Static test command passes.

## Validation

Required:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

If docs/task-board wording is touched:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```
