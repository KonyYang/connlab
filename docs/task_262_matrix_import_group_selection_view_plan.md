# TASK_262 Matrix Import Group Selection View Plan

## 0) Anti-Skip Protocol

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task for this plan: `TASK_262_MATRIX_IMPORT_GROUP_SELECTION_VIEW` (planned, awaiting approval)
- Why this task is allowed now:
  - `TASK_261_MATRIX_IMPORT_GROUP_SELECTION_COMMIT` is complete.
  - `docs/task_board.md` has no active implementation task.
  - `docs/matrix_authority_to_test_record_smoke_flow_plan.md` recommends `TASK_262` after TASK_261.

This document is a plan only. No implementation should start until user approval.

Model fit:

- Recommended model: `GPT-5.3-codex`, reasoning `medium`.
- Why: bounded frontend workflow wiring + typed API client + compact feature component + deterministic tests.

UI context loaded for planning:

- `$impeccable` product register context from `PRODUCT.md` and `DESIGN.md`.
- `docs/02_ARCHITECTURE_RULES.md`.
- `docs/frontend_architecture_rules.md`.

## 1) Goal

Add an operator-facing Group Selection View to the Matrix import flow:

```text
Import Matrix -> Preview -> Group Selection -> TASK_261 commit -> selected-only draft -> Matrix Editor
```

The goal is workflow correctness:

- Operator chooses which imported groups become the project execution draft.
- Full Source Matrix lineage is preserved by TASK_261.
- Matrix Editor only receives the selected-only `ProjectMatrixDraft`.

## 2) Task Understanding

Input data:

- Existing Matrix preview payload produced by the Matrix Editor import preview flow.
- Project id from the Matrix Editor route/workspace context.
- Selected group keys chosen by the operator.

Output data:

- Loaded selected-only `ProjectMatrixDraft` returned by TASK_261.
- Matrix Editor state updated from the returned draft.
- Operational status explaining `created`, `reused`, loading, and validation errors.

Involved modules:

- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- new `frontend/src/features/matrix-editor/MatrixImportGroupSelectionView.tsx`
- optional new `frontend/src/features/matrix-editor/matrixImportSelectionSelectors.ts`
- `frontend/src/workbench.css`
- frontend test files and static shell tests

Not allowed:

- backend changes
- parser changes
- Matrix Editor layout redesign
- Confirmed Matrix creation
- Test Record preview
- execution/report/fee/evidence/future-scope UI

## 3) UX Shape

Scene sentence:

An offline lab engineer on a daytime Windows workstation has just parsed a DOCX Matrix and needs a compact, trustworthy checkpoint to decide which group columns become this project's editable execution draft.

Design direction:

- Product register, restrained operational UI.
- Use the existing Matrix Editor import modal/workflow vocabulary.
- Show a compact group list/table with checkboxes, group label/key, sample quantity, and optional step count.
- Keep primary action focused on creating/loading the project draft.
- Avoid exposing row-level Matrix details in this view.

Suggested view structure:

```text
Header: Select groups for this project
Status line: N groups found, M selected
Group list:
  [ ] Group label/key | Samples | Step count
Footer:
  Cancel | Create project draft
Inline message:
  blocked reason / API error / reused loaded
```

## 4) File-Level Change Plan

1. API client
   - Update `frontend/src/api/client.ts`.
   - Add request/response DTOs for TASK_261:
     - `MatrixImportCommitRequest`
     - `MatrixImportCommitResponse`
     - reuse or align with existing `ProjectMatrixDraft` DTO.
   - Add `commitMatrixImport(projectId, input)`.
   - Keep `fetch` centralized in API client only.

2. Selection selectors/helpers
   - Add `frontend/src/features/matrix-editor/matrixImportSelectionSelectors.ts` if practical.
   - Responsibilities:
     - derive selectable groups from preview payload
     - normalize group key fallback consistently with backend fallback (`group_1`, `group_2`, ...)
     - calculate selected count
     - calculate confirm disabled reason
     - avoid row/detail data exposure

3. Group Selection View component
   - Add `frontend/src/features/matrix-editor/MatrixImportGroupSelectionView.tsx`.
   - Props should include:
     - parsed groups
     - selected keys
     - loading state
     - error/status text
     - callbacks for toggle, cancel, confirm
   - Render only group-level fields.
   - Use existing product UI classes and restrained styles.

4. Matrix Editor workflow wiring
   - Update `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`.
   - Existing import preview confirmation should open group selection instead of directly applying imported preview data.
   - Confirm selection calls `commitMatrixImport`.
   - On response, call existing draft application path for `ProjectMatrixDraft`.
   - Preserve existing save/revision/confirm behavior after draft load.

5. Styling
   - Update `frontend/src/workbench.css` only with scoped Matrix Editor group-selection classes.
   - Avoid nested cards, thick colored side stripes, gradient text, glassmorphism, and decorative motion.

6. Tests
   - Update or add Vitest coverage around `MatrixEditorWorkspace` when feasible:
     - group selection appears after preview confirmation
     - confirm disabled when no group selected
     - commit API success loads selected-only draft
   - Update `tests/unit/test_frontend_shell_files.py`:
     - API client symbol/path assertions
     - new component/selectors exist
     - Group Selection View does not include forbidden detail columns or future-scope copy

7. Documentation
   - Mark `tasks/TASK_262_MATRIX_IMPORT_GROUP_SELECTION_VIEW.md` complete after implementation.
   - Update `docs/task_board.md` with deliverables, validation, and next recommended task.

## 5) API Contract

Endpoint:

```text
POST /api/projects/{project_id}/matrix-import/commit
```

Request body:

```json
{
  "source_document_path": "...",
  "source_document_name": "...",
  "source_format": ".docx",
  "preview_payload": {},
  "selected_group_keys": ["g1", "g2"]
}
```

Response body:

```json
{
  "source_import_id": "smi-...",
  "source_snapshot_id": "sms-...",
  "selected_group_keys_committed": ["g1", "g2"],
  "commit_status": "created",
  "project_matrix_draft": {}
}
```

Frontend behavior:

- `created`: load returned draft and show success status.
- `reused`: load returned draft and show reuse status.
- `422`: keep Group Selection View open and show business-readable error.
- `404` / `409`: keep view open with actionable status.

## 6) State And Data Flow

```text
import preview payload
-> selectable group view model
-> selected group key state
-> commitMatrixImport()
-> ProjectMatrixDraft response
-> existing draft-to-editor mapper
-> selected-only editor grid
```

State ownership:

- `MatrixEditorWorkspace` may own transient import preview, selected keys, loading, and error state.
- Group selection rendering should live in the new feature component.
- Derived disabled reasons should live in selector/helper code where practical.

## 7) Out Of Scope

- Backend API implementation or changes.
- Preview token support.
- Group reselection from persisted Source Matrix.
- Matrix library/import source expansion.
- Test Record preview.
- Confirmed Matrix authority creation.
- Runtime execution, StepInstance, evidence, images, report, fee, duration, equipment, AI review, LAN, permissions, deployment.
- Broad decomposition of `MatrixEditorWorkspace.tsx` beyond what is necessary for this task.

## 8) Implementation Steps

1. Add frontend TASK_261 commit DTOs and API client function.
2. Add selection helper/selector for preview groups and disabled reason.
3. Add `MatrixImportGroupSelectionView` component.
4. Wire existing import preview confirmation to open group selection.
5. Wire confirm to `commitMatrixImport` and load returned `ProjectMatrixDraft`.
6. Add scoped styles.
7. Add/update frontend/static tests.
8. Run validation commands.
9. Update task file and board only after implementation passes.

## 9) Validation Plan

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task262 or matrix_editor"
```

```powershell
cd frontend; npm test -- --run MatrixEditorWorkspace
```

```powershell
cd frontend; npm run build
```

## 10) Risks

- `MatrixEditorWorkspace.tsx` is large; this task should add a named component and selectors rather than expanding one-off JSX.
- Existing import preview metadata may not have clean source document path/name/format in every path. Implementation must reuse the actual available preview/upload metadata and avoid inventing fake authority.
- A reused commit may surprise operators if not messaged clearly; it should be treated as successful draft load.
- Group selection must not become a second Matrix editor.

## 11) Review Checklist

- Group Selection View appears after import preview confirmation.
- Only group-level information is rendered.
- At least one group is required.
- TASK_261 commit API is called through `frontend/src/api/client.ts`.
- Returned `ProjectMatrixDraft` is loaded through existing editor draft mapping.
- Matrix Editor shows selected groups only.
- Existing preview APIs are unchanged.
- Existing save/revision/confirm flows are unchanged.
- No backend implementation is changed.
- No Test Record/report/fee/execution/future-scope UI is introduced.
