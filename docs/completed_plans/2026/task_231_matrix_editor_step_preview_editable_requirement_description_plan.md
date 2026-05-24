# TASK_231 Matrix Editor Step Preview Editable Requirement Description Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_231_MATRIX_EDITOR_STEP_PREVIEW_EDITABLE_REQUIREMENT_DESCRIPTION`
- Allowed now: user confirmed the simplified Step preview target.

## Goal

Make right-side Step preview useful for the selected group without introducing backend persistence or report generation:

- derive step list from selected group column
- sort by step number
- show Test Item as read-only
- allow Requirement and Step Description edits

## Minimal Data Model

Use local frontend override state:

```text
stepOutputOverrides[`${groupId}:${stepNo}:${rowId}`] = {
  requirement?: string
  description?: string
}
```

Defaults:

- `requirement = matrix row requirement`
- `description = matrix row requirement`

## Derivation Logic

For selected `groupId`:

1. Iterate Matrix rows.
2. Parse valid step token cells.
3. For each step number, create preview row:
   - `stepNo`
   - `rowId`
   - `testItem`
   - `sourceRequirement`
   - `requirementValue`
   - `descriptionValue`
4. Sort by `stepNo`, then row order.

If no group is selected:

- show a compact empty state asking user to select a group header.

If selected group has validation errors:

- still render parseable valid steps where possible, but keep existing validation warnings in main status strip.

## File-Level Changes

1. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- add local `stepOutputOverrides` state
- add `buildSelectedGroupStepPreviewRows` helper/selector
- replace static `STEP_WORKSPACE_ROWS` rendering with derived selected group rows
- add editable fields for Requirement and Step Description

2. `frontend/src/workbench.css`
- minor layout styles for editable preview fields if current table cannot fit cleanly

3. `tests/unit/test_frontend_shell_files.py`
- add static assertions for:
  - override state
  - selected group derivation
  - editable requirement/description fields
  - read-only Test Item display

## Risks

- Ambiguous duplicate step numbers are already covered by TASK_230 validation; preview should not try to resolve them.
- Edits are local only. This must remain clear in implementation scope.
- Large text fields can crowd the right panel; keep compact but readable.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task231 or task230 or matrix_editor"
```

## Out Of Scope

- smart content generation
- persistence
- Test Record generation
- Report generation
