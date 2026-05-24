# TASK_251 Matrix Editor Samples Quantity (PCS) UI Guards Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_251_MATRIX_EDITOR_SAMPLES_QUANTITY_PCS_UI_GUARDS`
- Allowed now: follows approved staged path from `TASK_250` feasibility.

## Task Understanding

Goal:

- In Matrix Editor, add a fixed final row for `Samples Quantity (PCS)`.
- Capture per-group quantity as required positive integers.
- Keep this task frontend-only.

Input data:

- Current Matrix Editor local draft row model:
  - `EditableMatrixRow` with `groups: Record<group_id, string>`
- Current group structural operations and step-token validation.

Output data:

- UI-only per-group quantity values in Matrix Editor local state.
- UI validation cues for required integer quantity.

## Minimal Design

### 1. Data placement (frontend-local)

Add local state:

- `sampleQuantityByGroupId: Record<string, string>`

Reason:

- avoids polluting existing test-item row model in this slice
- isolates quantity validation from step-token logic
- naturally keyed by stable `group.id`

### 2. Initialization and synchronization

- initialize with one entry for initial `group-1`, default empty
- when group columns change (add/insert/duplicate/delete), update `sampleQuantityByGroupId` by `group.id`
- preserve existing values for unchanged groups

### 3. Grid rendering

Add one fixed row after all editable test rows:

- first six cells:
  - row selector cell
  - `Test Item` cell text: `Samples Quantity (PCS)`
  - remaining fixed-column cells blank/placeholder
- group cells:
  - editable inputs bound to `sampleQuantityByGroupId[group.id]`

### 4. Validation

Per group quantity:

- required (non-empty)
- integer only (`^\d+$`)
- numeric value `>= 1`

Error strategy:

- reuse existing invalid style class pattern (`is-invalid`/error message approach)
- include first error in status strip alongside existing messages

### 5. Guard separation

- step-token parse/sequence rules continue to run only on test-item rows
- quantity row must not participate in:
  - step preview derivation
  - step sequence validation
  - missing-step row warning logic

## File-Level Changes

1. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- add quantity state
- add group-sync update logic
- add quantity validators
- render final fixed quantity row

2. `frontend/src/workbench.css` (only if needed)
- minimal selector for quantity-row label/readability

3. `tests/unit/test_frontend_shell_files.py`
- add TASK_251 static checks for:
  - quantity row label
  - quantity state keyed by group id
  - required integer validation logic
  - separation from step-token validations

4. `tasks/TASK_251_MATRIX_EDITOR_SAMPLES_QUANTITY_PCS_UI_GUARDS.md`
- update status and validation after implementation.

5. `docs/task_board.md`
- mark TASK_251 complete after implementation and validation.

## Risks

- UI-only storage means quantities are not persisted yet. This is acceptable in TASK_251 and is resolved in TASK_252.
- If quantity row is accidentally merged into normal rows, step-token validation will break. Explicit separation is required.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task251 or matrix_editor"
```

## Stop Point

After plan approval, implement TASK_251 only. Do not start TASK_252 in the same turn.
