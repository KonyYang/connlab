# TASK_252CQ Plan - Matrix Editor Identical Sample Rows Merge Note

## 0. Protocol Snapshot

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_252CQ_MATRIX_EDITOR_IDENTICAL_SAMPLE_ROWS_MERGE_NOTE`
- Why allowed now: user explicitly approved merging identical multi-row sample quantities and showing source-row information in the right-side Samples notes.

## 1. Task Understanding

1. Goal:
   - When imported sample rows such as `Header`, `Rec.`, and `Rec+ Cable` have identical values for a group, display a single sample value and add a right-side note that the rows were merged.
2. Input:
   - Matrix preview `rows`, including multiple `is_sample_row` entries and their group token values.
3. Output:
   - One editable sample value per group.
   - Right-side `Samples` `Notes` includes both existing marker note and merge-source note.
4. Modules:
   - `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
   - `tests/unit/test_frontend_shell_files.py`
   - `docs/task_board.md`
5. Not allowed:
   - No backend parser/API schema change.
   - No global group-column width change.

## 2. Design

- Extend `buildMatrixFromPreview()` to calculate `sampleMergeNotes`.
- For each group:
  - collect non-empty sample row values from preview sample rows;
  - if all non-empty values are identical and more than one source label exists, store one displayed sample value and a merge note like `Header / Rec. / Rec+ Cable share the same sample quantity.`
- Add `sampleMergeNotes` frontend state keyed by group id.
- Append selected group merge note to `selectedGroupSampleNotes` after existing marker/sample note.
- Clear merge note for a group when the operator edits that group sample value.

## 3. Validation

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task252cq or matrix_editor"
```

```powershell
cd frontend
npm run build
```
