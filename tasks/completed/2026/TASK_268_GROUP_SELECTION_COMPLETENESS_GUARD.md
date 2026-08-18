# TASK_268_GROUP_SELECTION_COMPLETENESS_GUARD

Status: complete
Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Workstream: Post-Phase-11 Matrix-driven Laboratory Execution workflow refinement
Last Updated: 2026-05-24

## Current Execution Context

Current task status:

```text
TASK_268_GROUP_SELECTION_COMPLETENESS_GUARD
```

Allowed reason:

- `TASK_261` to `TASK_267` are complete.
- `docs/task_board.md` has no active implementation task before this planning step.
- `docs/post_phase11_matrix_driven_laboratory_execution_workflow_guideline.md` recommends TASK_268 as the next workflow refinement after persistent Matrix import session UX.
- The user explicitly requested this task file and executable plan.

Implementation and validation are complete.

## Objective

Reduce the highest-risk Matrix import selection error:

```text
Missing selected group steps
```

Enhance the existing inline Group Selection mode so the operator can clearly see which groups, estimated steps, and sample quantities will enter the selected-only `ProjectMatrixDraft` before committing.

## Baseline

Existing behavior after `TASK_267`:

- Matrix import keeps an in-memory source preview session.
- The operator can return from selection mode to candidate preview.
- The operator can return from draft editing to group selection when live preview context exists.
- Group Selection mode shows Test Item rows and group columns with header checkboxes.
- Section / Method / Condition / Requirement are hidden in selection mode.
- Zero selected groups blocks commit with `Select at least one group.`

Current gaps:

- Selected group count is only embedded in a compact source line.
- Selected step count is not prominently visible.
- Sample quantity expressions are not visible in the selection table header or summary.
- Before committing, the user does not get a concise "what will enter the draft" summary.
- Zero-selection blocker exists but is not visually strong enough for the main operator risk.

## Scope

In scope:

- Frontend-only enhancement of Matrix import selection mode.
- Add a selection completeness summary derived from the existing `MatrixPreviewResponse`.
- Show selected group count and total available group count.
- Show selected step count if derivable from group step payloads.
- Show sample quantity expression per group.
- Add a concise confirmation summary before commit.
- Keep Test Item rows visible as context.
- Make zero-selection state explicit and visually blocked.
- Add React tests and static shell guardrails.
- Preserve the existing TASK_261 commit API contract.

Out of scope:

- No backend API changes.
- No database/schema migration.
- No SourceMatrix, ProjectMatrixDraft, or ConfirmedMatrix persistence changes.
- No reload recovery or backend import-session persistence.
- No multi-matrix append/merge implementation.
- No Test Record Word generation.
- No Project Workbench Matrix projection.
- No StepInstance, LLCR runtime persistence, report engine, fee engine, equipment matching, AI recommendation, permission system, or LAN behavior.
- No full Matrix editor controls inside selection mode.

## UX Requirements

Selection mode must show:

- Source document name.
- Selected group count.
- Selected step count when derivable.
- Group columns with checkboxes.
- Sample quantity expression per group.
- Test Item rows as background context.
- A visible blocker when no group is selected.
- A concise confirmation summary near `Confirm selected groups`.

Selection mode must continue to hide:

- Section.
- Method.
- Condition.
- Requirement.
- Draft/revision action groups.
- Right-side edit cards.
- Record / Report / Fee / execution actions.

`Change Selected Groups` must remain a correction of current authority configuration, not a new `Import Matrix` action.

## Expected Impact Files

Expected frontend changes:

- `frontend/src/features/matrix-editor/matrixImportSelectionSelectors.ts`
- `frontend/src/features/matrix-editor/MatrixImportSelectionMode.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`

Expected documentation changes after approved implementation:

- `tasks/TASK_268_GROUP_SELECTION_COMPLETENESS_GUARD.md`
- `docs/task_268_group_selection_completeness_guard_plan.md`
- `docs/task_board.md`

Avoid modifying:

- backend application services
- backend API routes
- persistence models/repositories
- database migrations
- Project Workbench smoke panel
- Test Record preview backend

## Acceptance Criteria

- Group Selection mode displays selected group count as `Selected groups: X / Y`.
- Group Selection mode displays selected step count when group `steps` are available, and treats unavailable step arrays distinctly from an explicit count of `0`.
- Each group header displays its sample quantity expression or a clear empty marker.
- Confirmation area summarizes selected group labels, selected group count, selected step count, and sample quantities for selected groups.
- Zero selected groups shows an explicit blocker and disables `Confirm selected groups`.
- Test Item rows remain visible in selection mode.
- Section / Method / Condition / Requirement remain hidden in selection mode.
- Existing navigation from TASK_267 remains intact: back to candidate preview, back to editor, cancel import session, change selected groups from draft.
- Existing TASK_261 import commit API request remains `preview_payload + selected_group_keys`.
- No backend files are modified.

## Validation

Minimum validation after approved implementation:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task268 or task267 or matrix_editor"
```

```powershell
cd frontend; npm test -- --run MatrixEditorWorkspace
```

```powershell
cd frontend; npm run build
```

Smoke-flow regression safety:

```powershell
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
```

Validation result on 2026-05-24:

- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task268 or task267 or matrix_editor"` passed (`36 passed, 73 deselected`).
- `cd frontend; npm test -- --run MatrixEditorWorkspace` passed (`13 passed`).
- `cd frontend; npm run build` passed.
- `py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q` passed (`1 passed`).

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- This is a bounded frontend UX and selector task.
- The data needed for counts and sample quantities already exists in `MatrixPreviewResponse`.
- The main implementation risk is UI/state clarity, not deep backend reasoning.
- Medium reasoning is enough if the worker reads the existing `TASK_267` state flow and keeps changes inside the Matrix Editor feature boundary.

## Required Executable Plan Before Implementation

Executable plan:

```text
docs/task_268_group_selection_completeness_guard_plan.md
```

Do not implement before the user explicitly approves the plan.

## Residual Risks

- Selected step count depends on `preview.groups[].steps`. The implementation should represent step count as `number | null`: `0` means an explicitly empty steps array, while `null` means the source did not provide a usable steps collection.
- Sample quantity expressions may be blank for malformed or incomplete source matrices. The UI should show a neutral empty marker, not a false value.
- This task improves operator visibility but does not prove that the original source matrix is semantically correct.
