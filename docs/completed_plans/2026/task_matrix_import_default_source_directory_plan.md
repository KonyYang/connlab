# TASK_MATRIX_IMPORT_DEFAULT_SOURCE_DIRECTORY Plan

Status: `bounded_scope_amendment_ready_for_user_approval`

## 1. Outcome

The desktop `Import Matrix` action opens at a project-relevant directory without changing Matrix
authority or file-storage semantics. The resolver order is exact:

```text
existing official workspace / Submitted Material
-> existing project-owned stored intake-attachment parent
-> native OS default / browser upload fallback
```

## 2. Discovery Findings

### Repository facts

- `MatrixEditorWorkspace.tsx` currently calls a hidden HTML file input. That path supports
  `.pdf/.doc/.docx` upload but cannot choose an initial directory.
- PyWebView's installed `Window.create_file_dialog` supports a `directory` parameter.
- `DesktopPathPickerApi` and `desktop_bridge_script()` currently expose only
  `pickExternalResourcePath`, so Matrix has no desktop-native project picker contract.
- `ProjectTestPlanSourceCandidateService` already owns the project/file-asset read model and the
  source-candidate route already serves Matrix source information.
- `OfficialWorkspaceRecord.official_folder_path` identifies the created project folder.
- Confirmed intake assets are already registered as project `FileAsset` records whose stored paths
  point into controlled intake storage. No database or schema change is required.
- `/api/test-plan/matrix-preview-from-path` already previews an exact local `.pdf/.docx` path;
  `.doc` remains handled through the existing upload conversion path unless current path preview
  capability supports it. The implementation must not expand parser behavior.

### Platform boundary

A normal browser cannot be forced to open its file input at an arbitrary filesystem directory.
Therefore the requirement is guaranteed in the ConnLab desktop/PyWebView host. Browser-only
development retains the existing upload picker. The UI must not claim that the browser fallback
honors the preferred directory.

## 3. Design

### 3.1 Read-only preferred-directory projection

Extend the existing project Matrix source-candidate result with nullable, operator-safe fields:

- `preferred_import_directory`
- `preferred_import_directory_source` with controlled values
  `submitted_material | intake_attachments | unavailable`

Resolution rules:

1. Load the project; preserve the existing not-found behavior.
2. If an official workspace record exists and
   `<official_folder_path>/Submitted Material` is a directory, return it.
3. Otherwise inspect project-owned `FileAssetType.ATTACHMENT` records that have an intake asset
   identity, exclude the request-email source, require the stored file and its parent directory to
   exist, then select the parent deterministically by normalized path ordering.
4. Otherwise return `null / unavailable`.

The route returns the projection with the existing candidate list. It performs no directory
creation, file copy, persistence, or external mutation.

### 3.2 Desktop picker contract

Add a dedicated Matrix picker call rather than overloading Settings resource semantics:

```text
pickMatrixImportSource(initialDirectory: string | null)
```

The Python bridge validates the optional initial directory as an existing directory before passing
it to PyWebView. Invalid/unavailable input becomes an empty directory argument so the OS chooses its
normal location. The dialog is single-select and filters `.pdf`, `.doc`, `.docx`, plus all files.
Cancel returns `null`.

### 3.3 Frontend orchestration

Add a bounded Matrix feature hook/module that:

1. detects the dedicated desktop bridge;
2. reads the project source-candidate projection;
3. invokes the native Matrix picker with the preferred directory;
4. returns the selected local path, cancellation, or a browser-fallback decision.

`MatrixEditorWorkspace` remains the owner of Matrix import state. It will factor the existing
preview-state initialization so both paths share the same behavior:

- desktop path -> `previewProjectTestPlanMatrixFromPath`;
- browser fallback -> existing hidden input and `previewProjectTestPlanMatrixFromUpload`.

An API/projection failure must not disable import. It falls back to the browser input. Read-only
lifecycle blocking remains first and unchanged.

### 3.4 No hidden side effects

- Opening or cancelling the picker creates no Matrix draft and writes no file.
- Directory resolution does not create `Submitted Material` or copy intake files.
- Import preview remains read-only; existing Replace/Confirm boundaries remain authoritative.
- No path is stored as a new preference and no last-used-directory persistence is introduced.

## 4. File-Level Changes

### Backend/application/API

- `backend/application/project_test_plan_source_candidate_service.py`
  - inject a read-only official-workspace lookup;
  - resolve the deterministic preferred directory and expose controlled source metadata.
- `backend/api/routes_project_test_plan_source_candidates.py`
  - add the two nullable response fields.
- `backend/api/dependencies.py`
  - compose the source-candidate service with the existing official-workspace repository.
- `backend/api/routes_project_test_plan.py`
  - extend only the existing `matrix-preview-from-path` request DTO with the locator page,
    table-on-page index, and table-text query fields already supported by
    `MatrixPreviewFromPathCommand`;
  - pass those values unchanged into the existing command without changing endpoint identity,
    parser behavior, persistence, or Matrix authority.

### Desktop boundary

- `backend/desktop/path_picker_api.py`
  - add the dedicated Matrix picker method, initial-directory validation, and document filters.
- `backend/desktop/shell.py`
  - expose the dedicated bridge function in the injected JavaScript contract.

### Frontend

- `frontend/src/api/client.ts`
  - type the new source-candidate response fields.
- `frontend/src/desktop/pathPickerBridge.ts`
  - type/detect/invoke the dedicated Matrix picker contract.
- `frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts`
  - own preferred-directory lookup and desktop/browser fallback selection.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
  - route Import Matrix through the feature hook and unify path/upload preview state handling.

### Tests

- `tests/unit/test_matrix_source_candidate_service.py`
  - Submitted Material priority, intake fallback, deterministic choice, missing paths.
- `tests/integration/test_project_test_plan_source_candidates_api.py`
  - typed projection for both workspace states and not-found compatibility.
- `tests/integration/test_project_test_plan_preview_api.py`
  - prove the existing path-preview endpoint accepts and forwards all locator values and preserves
    its existing defaults when they are absent.
- `tests/unit/test_desktop_path_picker_api.py`
  - exact initial directory, filters, invalid-directory fallback, cancel.
- `tests/unit/test_frontend_shell_files.py`
  - dedicated bridge wiring and no Settings contract regression.
- `frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx`
  - desktop selection, cancellation, API failure, bridge absence.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
  - local-path preview, browser upload fallback, read-only state, cancel/no mutation.

## 5. Risks And Controls

- **Path disclosure:** return only the project-owned preferred directory already available to the
  local operator; do not expose it in public copy or logs.
- **Stale workspace record:** require the exact `Submitted Material` directory to exist before use.
- **Wrong attachment folder:** require project ownership, intake asset identity, non-email role,
  existing file, and deterministic parent selection.
- **Browser limitation:** preserve the current upload input rather than simulate an unsupported
  initial directory.
- **`.doc` compatibility:** preserve current upload conversion; do not claim path-preview support
  beyond existing backend capability.
- **Oversized UI owner:** place selection logic in a feature hook/module and keep workspace changes
  to orchestration/state reuse.

## 6. Validation

```text
py -m pytest tests/unit/test_matrix_source_candidate_service.py tests/unit/test_desktop_path_picker_api.py tests/unit/test_frontend_shell_files.py -q
py -m pytest tests/integration/test_project_test_plan_source_candidates_api.py -q
py -m pytest tests/integration/test_project_test_plan_preview_api.py -q
npm test -- --run frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx
npm run build
py -m py_compile backend/application/project_test_plan_source_candidate_service.py backend/api/routes_project_test_plan_source_candidates.py backend/api/routes_project_test_plan.py backend/desktop/path_picker_api.py backend/desktop/shell.py
git diff --check
```

Manual desktop smoke:

1. Project without official workspace but with stored attachments opens the native dialog at that
   attachment directory.
2. After official folder creation, the same action opens at `Submitted Material`.
3. Cancel leaves Matrix state unchanged.
4. Browser-only localhost retains the upload picker and completes preview.

## 7. Exact Approved Request

The following code fence is the canonical single-line UTF-8 approved request for `Approve`:

```json
{"schema":"connlab.personal-task-approved-request","version":1,"task_id":"TASK_MATRIX_IMPORT_DEFAULT_SOURCE_DIRECTORY","summary":"Make Matrix Editor Import Matrix open at the project Submitted Material folder after project-folder creation, otherwise at the stored intake-attachment directory, with safe desktop and browser fallback behavior.","kind":"planned","may_touch":["backend/application/project_test_plan_source_candidate_service.py","backend/api/routes_project_test_plan_source_candidates.py","backend/api/dependencies.py","backend/desktop/path_picker_api.py","backend/desktop/shell.py","frontend/src/api/client.ts","frontend/src/desktop/pathPickerBridge.ts","frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx","frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts","tests/unit/test_matrix_source_candidate_service.py","tests/integration/test_project_test_plan_source_candidates_api.py","tests/unit/test_desktop_path_picker_api.py","tests/unit/test_frontend_shell_files.py","frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx","frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx","backend/api/routes_project_test_plan.py","tests/integration/test_project_test_plan_preview_api.py","docs/task_board.md"],"expected_file_count":18,"classification_reason":"Minimal bounded scope amendment for the existing path-preview API contract plus its integration regression, while retaining the approved cross-frontend/backend desktop route and independent Reviewer, QA, and Integrator gates; no database, schema, persistence, Matrix authority, public-drive, parser, or business-rule change.","targeted_validation":["py -m pytest tests/unit/test_matrix_source_candidate_service.py tests/unit/test_desktop_path_picker_api.py tests/unit/test_frontend_shell_files.py -q","py -m pytest tests/integration/test_project_test_plan_source_candidates_api.py -q","py -m pytest tests/integration/test_project_test_plan_preview_api.py -q","npm test -- --run frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx","npm run build","py -m py_compile backend/application/project_test_plan_source_candidate_service.py backend/api/routes_project_test_plan_source_candidates.py backend/api/routes_project_test_plan.py backend/desktop/path_picker_api.py backend/desktop/shell.py","git diff --check","desktop smoke: project without workspace opens at stored attachment directory; project with workspace opens at Submitted Material; browser-only fallback remains usable"],"forbidden_categories":{"api_contract":true,"database":false,"schema_or_migration":false,"persistence":false,"authority":false,"public_drive_workflow":false,"business_rule_semantics":false,"destructive_action":false,"external_mutation":false}}
```

## 8. Stop Point

Wait for explicit User approval of the committed Plan ref and approved-request SHA-256. No product,
test, branch, worktree, Developer, or implementation action is authorized before approval.

## 9. Minimal Bounded Scope Amendment

Reviewer R1 and Developer attempt 2 established a precise contract gap. The existing application
command already accepts locator page, table-on-page index, and table-text query values, but the
existing `matrix-preview-from-path` FastAPI request and route do not expose or forward them. A
frontend-only change would therefore be silently ignored and is prohibited as a false fix.

The amendment adds only `backend/api/routes_project_test_plan.py` and
`tests/integration/test_project_test_plan_preview_api.py`. It authorizes no endpoint addition, no
parser change, no database/schema/persistence change, no Matrix authority change, and no other path.
R2 remains within the original approved `MatrixEditorWorkspace.test.tsx` path. The active board stays
`DEVELOPER_BLOCKED`, and candidate `f1069be903e866c41be2a994b9e5593e20a64df4` plus all existing
evidence remain retained until the User explicitly approves this committed amendment.
