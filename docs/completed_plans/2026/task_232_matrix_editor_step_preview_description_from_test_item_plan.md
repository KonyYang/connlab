# TASK_232 Matrix Editor Step Preview Description From Test Item Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_232_MATRIX_EDITOR_STEP_PREVIEW_DESCRIPTION_FROM_TEST_ITEM`
- Allowed now: user explicitly requested this scoped Step preview behavior change.

## Goal

Refine Step preview field defaults and table columns to align with real usage:

- remove preview `Test Item` column
- map `Step Description` default to Matrix `Test Item`
- keep `Requirement` default to Matrix `Requirement`
- keep both fields locally editable

## Minimal Design

Current TASK_231 state:

- preview row keeps `testItem`, `sourceRequirement`
- `Requirement` and `Step Description` both default from `row.requirement`

TASK_232 mapping target:

- keep `sourceRequirement` and add/keep `sourceTestItem`
- `requirementValue = override?.requirement ?? row.requirement`
- `descriptionValue = override?.description ?? row.item`
- remove `Test Item` render column from preview table

No exception auto-fill in this task:

- LLCR / IR / DWV / mating-unmating special drafting is deferred
- explicit follow-up task required once deterministic rules are defined

## File-Level Changes

1. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- adjust `StepPreviewRow` typing for source fields
- adjust `buildSelectedGroupStepPreviewRows` default mapping
- remove `Test Item` column in Step preview table JSX
- keep override key and update handlers unchanged

2. `frontend/src/workbench.css`
- minimal width/tightness updates for the 3-column preview table (`Step`, `Requirement`, `Step Description`) if needed

3. `tests/unit/test_frontend_shell_files.py`
- add TASK_232 static checks:
  - `Step Description` default now uses `row.item`
  - `Test Item` column removed from preview header rendering
  - `Requirement` default remains `row.requirement`

## Risks

- Existing TASK_231 static assertions may still reference removed `Test Item` preview column text and need compatibility updates.
- Removing one column may shift CSS assumptions for preview widths; keep style patch minimal.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task232 or task231 or matrix_editor"
```

## Out Of Scope

- automatic special-case Step Description generation for LLCR/IR/DWV/mating-unmating
- persistence/API save behavior for preview overrides
- any Matrix main-grid behavior change
