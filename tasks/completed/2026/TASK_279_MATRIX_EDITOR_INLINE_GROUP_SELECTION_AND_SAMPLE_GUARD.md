# TASK_279_MATRIX_EDITOR_INLINE_GROUP_SELECTION_AND_SAMPLE_GUARD

## Status

Complete.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Allowed Reason

TASK_278 is complete and the task board currently has no active implementation task. This task is a controlled follow-up from Matrix Editor smoke feedback: group selection should happen inside the Matrix editor table, and selected groups must have valid sample quantity before Matrix confirmation.

## Objective

Simplify Matrix Editor so source Matrix import creates the editable draft directly, and group inclusion is controlled inline in the main Matrix table.

Target user workflow:

```text
Import Matrix -> Matrix appears in editor -> check/uncheck group columns inline
              -> optionally filter to selected groups / used test items
              -> edit Matrix and sample quantities
              -> Confirm Matrix
```

Users must not open a separate `Selected Groups` page to choose groups. Source Matrix is an import aid for creating the editable draft; the final authority is the current Matrix Editor draft content.

## User Feedback Source

This task is based on post-TASK_278 Matrix Editor smoke feedback:

- The separate `Selected Groups` button and page interrupt the workflow.
- Group selection should live directly beside group headers in the Matrix editor table.
- Importing a source Matrix should directly populate the editor table.
- Source Matrix should reduce manual input, not become a second source-selection workspace.
- `Confirm Matrix` must be blocked if any selected group has blank sample quantity or sample text without a number.
- Missing selected-group sample quantity should be visible through red field styling, not tooltip or top warning copy.

## Product Decision

TASK_279 adopts these rules:

1. `Selected Groups` is removed from the visible Matrix Editor toolbar.
2. `MatrixImportSelectionMode` is no longer used as a user-facing group selection page.
3. `Import Matrix` confirmation imports the parsed source Matrix directly into the Matrix editor table.
4. Each group column header includes an inline checkbox controlling whether that group is included in final confirmation.
5. The Matrix editor has a filter option to hide unchecked groups and rows with no tokens in checked groups.
6. `Confirm Matrix` is disabled when any checked group sample quantity is blank or contains no digit.
7. Invalid sample quantity fields use the same red background/border language as other missing required editor fields.
8. Backend confirmation also enforces selected-group sample quantity text containing at least one digit.
9. The legacy revision path remains for compatibility but must share the same sample quantity validation rule.
10. Import dialog `Append` remains non-operational in TASK_279 and must stay disabled.

## Scope

### In Scope

1. Remove visible `Selected Groups` action from `MatrixWorkspaceActionGroups`.
2. Remove the separate group selection page from active Matrix Editor flow.
3. Change source Matrix import confirmation so it directly commits/imports all parsed groups into the editor table.
4. Add inline group inclusion checkboxes in Matrix editor table headers.
5. Preserve existing group cells, row metadata, notes, sample values, and source lineage while toggling group inclusion.
6. Add one filter control that, when enabled:
   - hides unchecked group columns
   - hides test item rows that have no step token in checked groups
   - keeps the underlying draft state intact
7. Keep filter off by default so imported content does not disappear unexpectedly.
8. Add selected-group sample guard:
   - selected group sample quantity must be nonblank
   - selected group sample quantity must contain at least one digit
   - invalid selected-group sample inputs receive red invalid styling
   - `Confirm Matrix` is disabled while the guard fails
   - no top message or tooltip is required for this guard
   - do not set or show `confirmActiveMessage` for sample-guard disable state
9. Add backend sample guard in Matrix Editor session confirm.
10. Replace legacy revision path sample quantity validation with the shared guard.
11. Add frontend tests for:
    - `Selected Groups` button removed
    - import confirmation lands directly in the editor table
    - inline group checkbox toggles `is_selected`
    - selected-only filter hides unchecked groups and unused rows without deleting state
    - invalid selected-group sample quantity disables `Confirm Matrix` and marks only selected invalid groups
12. Add backend tests for:
    - session confirm rejects selected group sample text with no digit
    - session confirm allows unselected group sample quantity to be blank
    - legacy revision confirmation uses the same digit-containing sample guard
13. Update static frontend guards to prevent reintroducing the `Selected Groups` page/action.
14. Keep import dialog `Append` button disabled and ensure it never triggers import/commit actions in TASK_279.

### Out Of Scope

Do not implement in TASK_279:

- StepInstance or execution persistence
- image/evidence/test-data persistence
- report generation
- Test Record Word generation changes
- fee calculation
- permissions, approval workflow, multi-user locking, or LAN deployment
- historical version picker UI
- cross-project Matrix import UI
- multi-source append / merge workflow
- new database tables
- broad Matrix parser redesign
- Workbench layout redesign

Existing source Matrix import persistence and Confirmed Matrix authority persistence may be reused but should not become visible concepts in the Matrix Editor UI.

## Expected Files

Likely frontend files:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/features/matrix-editor/MatrixImportSelectionMode.tsx` (remove from active flow or delete if unused)
- `frontend/src/features/matrix-editor/matrixImportSessionModel.ts`
- `frontend/src/workbench.css`
- `frontend/src/api/client.ts` only if request/response typing needs adjustment

Likely backend files:

- `backend/application/matrix_editor_session_service.py`
- `backend/application/matrix_revision_flow_service.py`
- `backend/application/matrix_sample_quantity_guard.py` or equivalent narrowly named shared application helper

Likely tests:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `tests/unit/test_matrix_editor_session_service.py`
- `tests/unit/test_matrix_revision_flow_service.py`
- `tests/integration/test_matrix_editor_session_api.py`
- `tests/unit/test_frontend_shell_files.py`

Task tracking:

- `tasks/TASK_279_MATRIX_EDITOR_INLINE_GROUP_SELECTION_AND_SAMPLE_GUARD.md`
- `docs/task_279_matrix_editor_inline_group_selection_and_sample_guard_plan.md`
- `docs/task_board.md`
- `docs/task_plan_index.md`

## Acceptance Criteria

1. Matrix Editor toolbar shows `Import Matrix`, `Cancel`, and `Confirm Matrix`; it does not show `Selected Groups`.
2. `Import Matrix` confirmed source content appears directly in the editor Matrix table.
3. The separate group selection page is not reachable from Matrix Editor.
4. Group headers include inline checkboxes with accessible labels such as `Include group 7`.
5. Toggling a group checkbox changes whether that group is included in the confirm payload.
6. Unchecking a group does not delete its cells, sample value, notes, or source identity.
7. The selected-only filter hides unchecked group columns and rows with no tokens in checked groups.
8. Turning the selected-only filter off restores hidden groups and rows without data loss.
9. If a checked group sample quantity is blank, `Confirm Matrix` is disabled and that sample input is red-highlighted.
10. If a checked group sample quantity contains no digit, `Confirm Matrix` is disabled and that sample input is red-highlighted.
11. Unchecked groups with blank or nonnumeric sample quantity do not block `Confirm Matrix`.
12. Backend `POST /api/projects/{project_id}/matrix-editor/session/confirm` rejects selected groups whose sample quantity is blank or contains no digit.
13. Legacy revision confirmation uses the same sample quantity digit rule.
14. No user-facing raw backend copy such as `revision draft`, `active_matrix_changed`, or stale draft wording is introduced.
15. No StepInstance, report, fee, image/evidence, permission, AI, or multi-user scope is introduced.
16. Import dialog `Append` is disabled and does not trigger `commitMatrixImport`.

## Validation Plan

Frontend:

```powershell
cd frontend
npm test -- --run MatrixEditorWorkspace --watch=false
npm run build
```

Backend:

```powershell
py -m pytest tests\unit\test_matrix_editor_session_service.py -q
py -m pytest tests\unit\test_matrix_revision_flow_service.py -q
py -m pytest tests\integration\test_matrix_editor_session_api.py -q
```

Static and smoke:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task279 or task278 or matrix_editor"
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
git diff --check
```

Manual browser smoke:

```text
http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f/matrix-editor
```

Check:

- import a Matrix and confirm import
- verify Matrix table appears directly without a group selection page
- uncheck one group and enable the selected-only filter
- verify unchecked group and unused rows hide
- disable filter and verify hidden content returns
- blank out a checked group sample quantity and verify `Confirm Matrix` is disabled and sample input is red
- uncheck that group and verify the sample issue no longer blocks confirm
- confirm a valid Matrix and verify Workbench projection reflects checked groups only

## Model Fit Assessment

`GPT-5.3-codex` is suitable for execution.

Reason:

- The task is a bounded React/FastAPI refactor with clear product semantics and existing test coverage.
- The highest risk is state-flow correctness between source import, editor draft, inline group selection, and confirm payload; this matches a coding-focused model with strong test discipline.
- The scope can be controlled through targeted frontend interaction tests, backend validation tests, and in-app browser smoke verification.

## Review Notes

Before implementation, reviewer should confirm:

- `Selected Groups` should be removed entirely from the visible toolbar.
- Imported source Matrix should initially include all parsed groups as checked.
- The selected-only filter should default off.
- Missing sample quantity guard should use red field styling and disabled `Confirm Matrix`, without tooltip or top explanatory copy.
- `Confirm Matrix` should publish only checked groups.
