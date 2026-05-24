# TASK_224_MATRIX_EDITOR_STRUCTURAL_EDIT_INTERACTION_RULES

## Status

Complete. Implemented and validated on 2026-05-18.

This is an interaction-design and scope-control task for Matrix Editor structural editing. It does not implement code.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

None. `TASK_223` Matrix Editor grid local fix is complete.

## Why This Task Is Allowed Now

The user explicitly requested Matrix Editor table editing interaction rules after the Matrix grid became locally editable. The task is allowed because it defines the next controlled frontend interaction boundary for Matrix Editor without changing backend, API contract, or matrix domain model.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable for execution.

Reason:

- The work is a bounded frontend product interaction design task.
- The rules are explicit and can be translated into local React state guards and UI affordances later.
- No backend persistence, API contract, or domain model changes are involved.
- The main complexity is interaction judgment and edge-case protection, not deep algorithmic work.

## Business Goal

Matrix Editor must let lab users maintain test item rows and test group columns while protecting the Matrix structure from accidental deletion, movement, or corruption.

The Matrix table is an authority editing surface, not a free-form spreadsheet. Operators can edit content and manage controlled row/group structures, but fixed headers and core test-definition columns must remain protected.

## Fixed Structure Rules

Header row:

- The first table row is the formal header row.
- It cannot be moved.
- It cannot be copied.
- It cannot be deleted.
- No row can be inserted before it.

Fixed first five columns:

- `Test Item`
- `Section`
- `Method`
- `Condition`
- `Requirement`

These five columns:

- cannot be moved
- cannot be copied
- cannot be deleted
- cannot have new columns inserted before them
- can only have their data-cell content edited

Minimum viable structure:

- At least one test item content row must always remain.
- At least one group column must always remain.
- The last test item row cannot be deleted.
- The last group column cannot be deleted.

## Recommended Interaction Scheme

Use a combined interaction model:

- Top toolbar for global commands and recovery actions.
- Row action rail for row-specific structure commands.
- Group header dropdown for group-column structure commands.
- Contextual action bar for selected row/group state.
- Right-click context menu as a secondary accelerator only.

This combination fits enterprise software because it is discoverable for new users, efficient for repeated editing, and safer than hidden spreadsheet-only gestures.

## Why Not Right-Click As Primary

Right-click is useful but should not be the primary trigger.

Reasons:

- Discoverability is weak. Many operators will not know actions exist.
- Enterprise Windows users understand right-click, but training cost increases if critical actions are hidden there.
- Browser context menus can conflict with custom menus.
- Touchpad and accessibility workflows are less predictable.
- Hidden destructive commands increase misoperation risk.

Recommendation:

- Support right-click later as an accelerator.
- In MVP, prioritize visible row controls, visible group header menus, and a contextual action bar.
- If right-click is implemented, it must mirror the same allowed/disabled command model as visible controls.

## Row Operation Placement

Recommended primary placement: row action rail.

Behavior:

- Add a narrow protected row-control area at the far left of body rows only.
- The header row area shows a locked/header indicator, not actions.
- On row hover or row selection, show compact row actions:
  - insert above
  - insert below
  - duplicate
  - move up
  - move down
  - delete
- The row-control area is not a data column and must not reintroduce a `#` sequence column as data.

Why:

- Row actions are spatially tied to the row they affect.
- Users can discover actions without right-click.
- It avoids putting row commands into every editable cell.
- It keeps fixed first five data columns protected while still enabling row maintenance.

Secondary placement:

- Selected-row contextual action bar above the table can expose the same row actions with text labels.
- This helps users who prefer explicit buttons and reduces learning cost.

## Group Column Operation Placement

Recommended primary placement: group header dropdown.

Behavior:

- Each group column header, for example `G1`, `G2`, `G3`, has a compact dropdown trigger.
- The dropdown contains:
  - insert group left
  - insert group right
  - duplicate group
  - move left
  - move right
  - delete group
- Fixed first five headers do not show this dropdown.
- Group column body cells remain content-editable.

Why:

- Column actions belong to column headers.
- It avoids overloading body cells.
- It makes fixed vs editable column regions obvious.
- It scales better than putting all group operations in one toolbar.

Secondary placement:

- Selecting a group column can show a contextual action bar with group actions.
- Top toolbar can include `Add group` as a global action.

## Top Toolbar Role

The top toolbar should not become a generic command dump.

Recommended MVP toolbar actions:

- `Add test item`
- `Add group`
- `Undo`

Optional if space allows:

- `Duplicate selected`
- `Delete selected`

Rules:

- Toolbar actions must reflect current selection.
- If no row/group is selected, `Add test item` appends a row and `Add group` appends a group.
- Destructive actions are disabled until a valid row/group selection exists.
- Disabled actions show a short reason through tooltip or inline status text.

## Contextual Action Bar

Use a contextual action bar when a row or group column is selected.

Behavior:

- Row selected: show row actions.
- Group selected: show group actions.
- Cell selected only: show content-editing state, not structural commands.
- Fixed header or fixed data column selected: show protected-state text instead of destructive actions.

Why:

- It keeps users oriented.
- It reduces clutter.
- It makes forbidden operations visible and explainable without allowing them.

## Fixed Area Visual Hints

Do not use decorative polish. Use operational hints only.

Header row:

- sticky header behavior
- slightly stronger header background
- no row action affordance
- optional small lock label/icon in the row-control header area

Fixed first five columns:

- subtle protected-region background or divider between `Requirement` and first group column
- no column dropdown on fixed headers
- tooltip or status text such as `Fixed definition column` when hovering header controls

Body cells in fixed columns:

- show normal editable cell focus style because content is editable
- do not show column-move/delete affordances

## Forbidden Operation Handling

Rules should be enforced in both UI affordances and command handlers.

UI layer:

- Hide commands that do not apply to a region, for example group dropdown on fixed columns.
- Disable commands that are contextually invalid, for example delete last row.
- Show a short reason for disabled commands.

Command guard layer:

- Every structural command must run through a guard function before mutating state.
- Guard results should return:
  - allowed boolean
  - reason string
  - affected target type

Recommended disabled reasons:

- `Header row is fixed`
- `Definition columns are fixed`
- `At least one test item row is required`
- `At least one group column is required`
- `Cannot insert before fixed definition columns`

## Delete, Copy, And Move Protection

Row rules:

- Delete row is blocked when row count is one.
- Move up is blocked for the first content row.
- Move down is blocked for the last content row.
- Insert above is allowed for any content row because it still stays below the fixed header.
- Insert below is allowed for any content row.
- Duplicate row inserts below the source row by default.

Group column rules:

- Delete group is blocked when group count is one.
- Move left is blocked for the first group column because it would cross into fixed columns.
- Move right is blocked for the last group column.
- Insert left is allowed only within the group region and before the selected group.
- Insert right is allowed only within the group region and after the selected group.
- Duplicate group inserts to the right of the source group by default.

Fixed column rules:

- Fixed columns cannot be deleted, copied, reordered, duplicated, or used as insertion anchors for new columns before them.
- Fixed-column data cells can be edited.

## Undo Requirement

Undo is recommended for MVP, but only as a lightweight local structural undo.

MVP undo scope:

- row add
- row duplicate
- row delete
- row move
- group add
- group duplicate
- group delete
- group move
- group insert

MVP undo can be one-step or short-stack local undo. It does not need backend history, persistence, audit trail, or multi-user conflict handling.

Why include undo:

- Structural edits have higher mistake cost than cell text edits.
- Delete confirmations alone slow users down.
- Undo lowers risk without adding a heavy workflow.

Suggested MVP pattern:

- For destructive operations, show a brief non-modal status message with `Undo`.
- For reorder/insert/duplicate, allow toolbar `Undo`.
- Keep confirmation dialogs out of MVP except for deleting rows/groups that contain non-empty data and no undo is available.

## MVP Minimal Implementation Boundary

The MVP implementation should be frontend-only.

Allowed:

- Matrix Editor table UI state for rows and group columns
- selection state for row, group, and cell
- row action rail
- group header dropdown
- top toolbar `Add test item`, `Add group`, and `Undo`
- command guard helpers
- disabled command reasons
- lightweight local undo stack
- focused frontend tests or static checks

Forbidden:

- backend changes
- API contract changes
- matrix domain model changes
- persistence workflow
- server-side undo/history
- StepInstance or execution persistence
- report/test-record generation behavior
- broad Matrix Editor redesign
- Workbench page changes

## Implementation Boundary For Future Approved Task

If this design is approved for implementation, use this file scope:

- `frontend/src/pages/ProjectMatrixEditorPage.tsx`
- `frontend/src/workbench.css`
- optional `frontend/src/features/matrix-editor/*` extraction only if the task explicitly authorizes moving table logic out of the page
- `tests/unit/test_frontend_shell_files.py` for focused frontend static checks
- `docs/task_board.md` after completion

Implementation should not modify:

- backend files
- API client DTOs or route contracts
- domain/application/infrastructure files
- Project Workbench components

## Suggested MVP Interaction Sequence

1. User clicks a body cell and edits content inline.
2. User hovers a row-control area or selects a row to reveal row actions.
3. User opens a group header dropdown to manage that group column.
4. User uses toolbar `Add test item` or `Add group` for append operations.
5. User attempts a forbidden action.
6. UI disables it or shows a short protected-state reason.
7. User performs a structural action.
8. Local undo becomes available.

## Future Enhancements

Later tasks may add:

- right-click context menus as secondary accelerators
- keyboard shortcuts for insert, duplicate, delete, and move
- drag handles for row and group reordering
- multi-select rows/groups
- persisted matrix draft save
- version comparison and restore
- audit trail for matrix structural edits
- validation before publishing
- integration with structured Step records when execution phase is explicitly approved

## Acceptance Criteria For This Design Task

- Interaction scheme is explicitly defined.
- Right-click menu position is clarified.
- Row operation placement is clarified.
- Group operation placement is clarified.
- Fixed region protection rules are defined.
- Forbidden-operation handling is defined.
- Delete/copy/move guards are defined.
- Undo recommendation is defined.
- MVP and future scopes are separated.
- Backend/API/domain changes are explicitly forbidden.

## Completion Notes

- Implemented frontend-only structural editing interactions in Matrix Editor table area.
- Added row control rail for row insert/duplicate/move/delete.
- Added group header actions menu for insert/duplicate/move/delete.
- Added protected-structure status message and minimum-structure guard reasons.
- Added top actionbar commands for `Add test item`, `Add group`, and `Undo`.
- Added local undo stack for structural actions only.
- Kept backend/API/domain models unchanged.

## Validation Result

- `cd frontend && npm run build` passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task224 or task223 or task222 or task221"` passed (`3 passed`, `69 deselected`).
