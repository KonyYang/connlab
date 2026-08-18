# TASK_MATRIX_IMPORT_BROWSER_PROJECT_SOURCE_PICKER Plan

Status: `ready_for_user_approval`

## 1. Outcome

The browser Matrix Editor uses project-owned intake sources first without hiding the existing upload
fallback. Desktop behavior is unchanged:

```text
Import Matrix
  desktop bridge available -> existing native project-directory picker
  ordinary browser -> project source chooser
    explicit candidate selection -> existing candidate preview API
    Upload other file -> existing hidden file input/upload preview
```

This is a selection and presentation change only. It creates no attachment, draft, Matrix revision,
or persisted preference merely by opening or cancelling the chooser.

## 2. Discovery Gate

### User-confirmed

- Browser file inputs cannot be directed to a project folder.
- Project source candidates and candidate preview endpoints already exist.
- The browser must present candidates, explicit selection, upload fallback, empty state, cancel, and
  read-only protection, while preserving the desktop picker.
- No API, database, schema, persistence, file-copy, parser, or Matrix-authority change is wanted.

### Repository-confirmed

- `MatrixSourceCandidate` already exposes `original_name`, `extension`, `asset_type`,
  `candidate_kind`, `reason`, and `stored_file_available`.
- `listProjectTestPlanSourceCandidates` and
  `previewProjectTestPlanMatrixFromSourceCandidate` already exist in the typed API client.
- The backend candidate service sorts by its domain score, then deterministic name/id tie-breakers.
- `useMatrixImportSourcePicker` currently preserves the desktop native path and returns `browser`
  when the bridge is absent.
- `MatrixEditorWorkspace` performs its read-only check before invoking the picker but currently
  responds to `browser` by clicking the upload input immediately.
- A Project Workbench source selector exists as interaction reference; this task does not refactor
  or share that separate workflow surface.

### Bounded Planner assumptions

- API order remains authoritative. The browser UI does not independently re-rank candidates.
- `candidate_kind=likely_spec_or_matrix` maps to a visible `Recommended` label; API `reason` remains
  the business-readable explanation.
- Unavailable candidates remain visible for traceability but their Select action is disabled.
- Candidate-load failure is shown as a concise non-blocking message beside `Upload other file`.

No unresolved question changes scope, API ownership, UX behavior, or validation.

## 3. UX And State Design

ConnLab is a daytime product workbench. Use a restrained, familiar file-source chooser with dense
rows and explicit actions, not an attachment-management page or decorative card grid.

- Open one focused chooser only in the browser branch.
- Heading: `Choose a project source`.
- Candidate row: file name, Word/type metadata, recommendation reason, availability, optional
  `Recommended` badge, and explicit `Use this file` action.
- Footer actions: `Cancel` and `Upload other file`.
- Empty state teaches the next action: no project candidates are available, upload another file.
- Loading and preview-busy states prevent duplicate actions and remain screen-reader observable.
- Cancel closes the chooser without clearing or replacing the current Matrix/import state.
- The existing parser-progress dialog begins only after explicit candidate selection or upload.

## 4. File-Level Changes

### Feature component

- `MatrixImportSourceCandidatePicker.tsx`
  - render the focused browser candidate chooser with loading, warnings, empty/error, recommended,
    unavailable, cancel, upload, and explicit-selection states;
  - remain presentation-focused and receive typed candidates/actions by props.
- `MatrixImportSourceCandidatePicker.test.tsx`
  - verify API-ranked presentation, recommended/type/reason copy, unavailable behavior, empty/error
    fallback, explicit selection, upload, and cancellation.

### Feature hook/orchestration

- `useMatrixImportSourcePicker.ts`
  - preserve existing desktop selection behavior;
  - expose browser candidate loading through the existing list API without moving API calls into the
    display component;
  - return candidate response/errors in a bounded typed result.
- `useMatrixImportSourcePicker.test.tsx`
  - retain native directory/cancel/format coverage and add browser candidate success, empty, and
    failure behavior with no desktop regression.

### Workspace integration

- `MatrixEditorWorkspace.tsx`
  - keep the lifecycle read-only gate before any picker work;
  - open the chooser only for the hook's browser result;
  - call the existing candidate-preview client after explicit selection and feed the response into
    the current preview state/dialog;
  - route upload fallback to the existing hidden input and make chooser cancel a zero-state-change
    operation.
- `MatrixEditorWorkspace.test.tsx`
  - cover browser candidate preview, upload fallback, no candidates, cancel/no mutation, read-only
    zero calls, and unchanged desktop path behavior.
- `workbench.css`
  - add only Matrix Editor source-chooser styles using existing tokens, focus states, compact rows,
    responsive layout, and semantic text-plus-color states.

## 5. Non-Goals And Forbidden Categories

All are false for the planned implementation: API contract, database, schema/migration,
persistence, authority, public-drive workflow, business-rule semantics, destructive action, and
external mutation.

Explicit non-goals: attachment management, upload architecture refactor, backend sorting changes,
new endpoints, new file formats, parser changes, automatic candidate import, persisted selection,
Matrix authority changes, and desktop picker changes.

## 6. Risks And Controls

- **Accidental auto-import:** no default selection and no preview until `Use this file`.
- **Duplicate ranking logic:** preserve backend order; only map the controlled candidate kind to a
  badge.
- **Missing stored file:** keep it visible but disable selection with `Unavailable` text.
- **Candidate API outage:** display a non-blocking message and keep upload available.
- **State mutation on cancel:** candidate chooser owns only ephemeral visibility/load state; Matrix
  preview/replacement state changes only after preview succeeds.
- **Desktop regression:** preserve the bridge-first branch and existing native picker tests.
- **Large Workspace:** move chooser markup into the named feature component and keep Workspace to
  orchestration.

Rollback is one local revert of the bounded implementation commit; no data migration or cleanup is
needed.

## 7. Validation

```text
py -m pytest tests/unit/test_matrix_source_candidate_service.py -q
npm test -- --run frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx
npm run build
git diff --check
```

Deterministic browser smoke:

1. Browser Import opens the chooser, with the API-ranked likely specification candidate first.
2. No preview call occurs until the operator chooses `Use this file`.
3. Selection opens the current preview; `Upload other file` opens the existing browser input.
4. Empty/API-failure states retain upload; Cancel changes no Matrix state.
5. A read-only project cannot open chooser/input or call list/preview.
6. With the desktop bridge present, Import still opens the native path picker and not the chooser.

## 8. Exact Approved Request

The following code fence is the canonical single-line UTF-8 approved request for `Approve`:

```json
{"schema":"connlab.personal-task-approved-request","version":1,"task_id":"TASK_MATRIX_IMPORT_BROWSER_PROJECT_SOURCE_PICKER","summary":"In browser Matrix Editor, show current project intake source candidates before file upload, preview only after explicit selection, preserve Upload other file, desktop picker, empty state, cancel and read-only behavior.","kind":"planned","may_touch":["frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.tsx","frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx","frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts","frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx","frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx","frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx","frontend/src/workbench.css","docs/task_board.md"],"expected_file_count":8,"classification_reason":"Bounded browser Matrix source-selection UI using existing candidate list and preview APIs, with independent review and QA; no backend, API, database, schema, persistence, parser, attachment-storage, Matrix-authority, public-drive, or business-rule change.","targeted_validation":["py -m pytest tests/unit/test_matrix_source_candidate_service.py -q","npm test -- --run frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx","npm run build","git diff --check","deterministic browser smoke: API-ranked candidate list and recommendation; explicit candidate preview; upload fallback; empty/error state; cancel zero mutation; read-only zero calls; desktop native picker unchanged"],"forbidden_categories":{"api_contract":false,"database":false,"schema_or_migration":false,"persistence":false,"authority":false,"public_drive_workflow":false,"business_rule_semantics":false,"destructive_action":false,"external_mutation":false}}
```

## 9. Stop Point

Wait for explicit User approval of the committed Plan ref and approved-request SHA-256. No product,
test, branch, worktree, Developer, or implementation action is authorized before approval.

