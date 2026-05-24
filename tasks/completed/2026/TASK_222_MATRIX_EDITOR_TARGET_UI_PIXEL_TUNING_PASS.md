# TASK_222_MATRIX_EDITOR_TARGET_UI_PIXEL_TUNING_PASS

## Status

Complete. Implemented and validated on 2026-05-17.

This is a pixel-tuning alignment task, not a redesign task.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

None. `TASK_221` Matrix Editor target UI alignment and workflow convergence is complete.

## Why This Task Is Allowed Now

`TASK_221` completed structural workflow convergence for Matrix Editor. The next logical step is a pixel-level tuning pass to reduce residual visual drift against `Matrix Edit Page.png`.

This task is allowed because it is a bounded frontend refinement task:

- no backend/API/domain changes
- no business flow changes
- no new interactions
- no new data contracts
- no route changes

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable for execution.

Reason:

- The task is mostly CSS and JSX layout micro-adjustment.
- The visual target and constraints are explicit.
- Existing `TASK_221` structure is stable; this pass is controlled refinement.

## Objective

Tune Matrix Editor UI details to more closely match `Matrix Edit Page.png` while preserving the `TASK_221` structure and Definition Studio positioning.

Focus on:

- header spacing and visual hierarchy
- toolbar compactness and button rhythm
- left library density
- matrix table column/row density
- right Group/Step workspace compactness
- bottom templates and reference panel balance
- typography scale consistency

## Non-Goals

Do not:

- redesign layout
- alter workflow order
- add new behavior
- enable disabled placeholder actions
- change backend logic
- change API contracts
- change domain models
- add dependencies

## Scope

Allowed:

- `frontend/src/pages/ProjectMatrixEditorPage.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py` (only if assertions need adjustment)
- `docs/task_board.md` and this task file after completion

Forbidden:

- any backend file
- any API client contract file
- runtime projection service code
- routing behavior change
- Workbench Runtime Console behavior changes

## Acceptance Criteria

- Matrix Editor remains Definition Studio.
- Matrix Grid remains primary visual focus.
- Pixel-level spacing/typography/density visibly converges toward target image.
- Left, center, right, and bottom areas remain aligned with `TASK_221` role boundaries.
- No new interactive/business behavior is introduced.
- `npm run build` passes.
- `task221/task222` frontend static checks pass.

## Validation

Required:

```powershell
cd frontend
npm run build
```

Required targeted tests:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task222 or task221 or task220 or task219"
```

Recommended governance tests after board update:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```
