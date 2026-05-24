# TASK_223_MATRIX_EDITOR_GRID_LOCAL_FIX

## Status

Complete. Implemented and validated on 2026-05-18.

This is a Matrix Editor table-area hotfix, not a UI redesign.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

None. `TASK_222` Matrix Editor target UI pixel tuning pass is complete and pending user approval for the next controlled task.

## Why This Task Is Allowed Now

The user explicitly requested a local Matrix Editor grid/table correction after `TASK_222`. The requested work is bounded to the existing Matrix Editor table area and does not alter backend, API contracts, domain models, routing, Workbench, or overall Matrix Editor workflow.

This task is allowed as a controlled hotfix because it only corrects the current Matrix Grid presentation and basic client-side edit affordance.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable for execution.

Reason:

- The scope is narrow and localized to one React page table region plus existing CSS selectors.
- The task requires careful JSX/CSS edits and simple client-side state, not architecture design.
- There are explicit non-goals preventing backend/API/domain changes.
- Validation can be handled with `npm run build` and focused frontend static checks.

## Objective

Apply a minimal Matrix Editor grid/table-area fix:

1. Remove the left `#` sequence column from the Matrix Editor table header and body.
2. Remove the extra duplicate header/placeholder row so only one formal header layer remains.
3. Tighten `Test Item`, `Condition`, and `Requirement` column widths so more `G1/G2/G3...` columns are visible in the main grid area.
4. Allow long text in fixed information columns to wrap instead of expanding the table enough to hide group columns.
5. Add basic inline editing for body cells only, including group cells, without new modals or workflow.

## Scope

Allowed files:

- `frontend/src/pages/ProjectMatrixEditorPage.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py` only for focused static assertions if needed
- `docs/task_board.md` and this task file after implementation completion

Forbidden files and areas:

- Backend files
- API route files
- API client contract files
- Domain/application/infrastructure layers
- Project Workbench page or Workbench Matrix Overview implementation
- App routing outside what already exists
- New dependencies

## Implementation Boundaries

- Keep the existing Matrix Editor page structure.
- Do not refactor Matrix Editor into new feature folders in this task.
- Do not introduce persistence, save APIs, autosave, validation workflow, StepInstance, execution records, or report bindings.
- Inline edits are frontend-local only for this hotfix unless a later approved task adds persistence.
- The formal header row remains non-editable.
- Body cells for `Test Item`, `Section`, `Method`, `Condition`, `Requirement`, and group columns should support editing.
- If the task wording is ambiguous, apply this interpretation: only header cells are non-editable; data-row cells are editable.

## Planned Design

- Convert the static `MATRIX_ROWS` rendering into a local editable grid state initialized from the existing placeholder rows.
- Remove the `#` header/body cell and update group-column index-based CSS selectors accordingly.
- Replace the two-row header with one header row:
  - `Test Item`
  - `Section`
  - `Method`
  - `Condition`
  - `Requirement`
  - `G1` through `G12`
- Use compact column sizing with wrapping:
  - `Test Item` compact but readable
  - `Condition` and `Requirement` narrower than today
  - group columns fixed/minimum compact width with center alignment
- Add simple inline controls for body cells, preferably lightweight `textarea` or `input` elements styled to read as table text.
- Keep group-cell edit values as local strings.

## Acceptance Criteria

- Matrix Editor table no longer shows the `#` column or row sequence numbers.
- Matrix Editor table has only one formal header row.
- `G1/G2/G3...` group columns are more visible in the main grid area than before.
- `Test Item`, `Condition`, and `Requirement` wrap long text and do not over-expand the table.
- Body cells are editable inline, including group cells.
- Header cells are not editable.
- No backend/API/domain files are changed.
- Workbench Matrix Overview is not changed.
- No new dialog, modal, save workflow, or unrelated visual polish is introduced.

## Validation

Required:

```powershell
cd frontend
npm run build
```

Required targeted frontend checks if static assertions are updated:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task223 or task222 or task221"
```

Manual smoke:

1. Open Matrix Editor for a project.
2. Confirm there is no `#` column.
3. Confirm there is only one header row.
4. Confirm several `G` columns are visible without horizontal scrolling caused mainly by text columns.
5. Edit a data-row text cell and a group cell inline.
6. Confirm no Workbench page table changed.

## Completion Notes

- Implemented local grid hotfix in Matrix Editor table area only.
- Removed `#` column and removed duplicate second header row.
- Tightened text column widths and enabled wrapping so group columns are prioritized.
- Added inline editable body cells for `Test Item`, `Section`, `Method`, `Condition`, `Requirement`, and all group columns.
- Editing remains frontend-local and does not alter backend or API contracts.

## Validation Result

- `cd frontend && npm run build` passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task223 or task222 or task221"` passed (`2 passed`, `69 deselected`).
