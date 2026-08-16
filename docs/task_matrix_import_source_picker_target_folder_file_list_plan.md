# TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST Plan

Status: `ready_for_user_approval`

## 1. Single solution

Keep the existing GET/POST endpoints and preserve their registered-asset default for Project Workbench.
Add one explicit `resolved_directory` view for the ordinary-browser Matrix Editor:

```text
browser requests resolved_directory
-> resolve existing Submitted Material, else parsed email attachments, else unavailable
-> enumerate immediate regular .doc/.docx/.pdf files
-> return deterministic filename order plus opaque candidate IDs
-> explicit POST selection re-enumerates and resolves the exact current ID
-> existing Matrix preview service
```

This creates no database record, stored token, copied file, preference, registry, or second endpoint.

## 2. Backend contract

- Default GET/POST behavior remains the registered-asset view.
- Add only the bounded query value `source_scope=resolved_directory`; reject unknown values.
- Reuse the current preferred-directory priority. Scan with `Path.iterdir()` and accept only direct
  regular files with case-insensitive `.doc`, `.docx`, or `.pdf` suffixes.
- Require the resolved parent to remain the exact preferred directory; reject escaping links, nested
  paths, directories, unsupported suffixes, and missing/unreadable entries.
- Sort by `(filename.casefold(), filename)` without ranking or recommendation.
- Namespace opaque directory IDs with `folder-` and derive them from exact project ID, source kind,
  canonical resolved-directory identity, and exact filename. Canonical directory identity participates
  only in the digest; do not expose or accept a filesystem path.
- Selection recomputes the preferred directory and candidates. Stale, foreign, renamed, deleted,
  collided, escaped, source-priority-changed, or same-source-kind directory-changed IDs fail before
  preview, including when the new directory contains an identically named file.
- Preserve the response field name `source_asset_id` for client compatibility. Directory candidates use
  neutral internal metadata; the Matrix browser renders only `original_name`.
- Non-`folder-` IDs continue through the unchanged registered-asset path; no namespace fallback.
- `.doc` retains the preview service's current deferred capability. No conversion/parser change.

## 3. Frontend and UX

- The browser hook requests `resolved_directory` and forwards `preferred_import_directory_source`;
  the desktop branch retains the default request and native picker directory.
- Workspace stores only ephemeral candidates, source kind and error. Matrix/import state changes only
  after a selected candidate preview succeeds.
- Title mapping: `submitted_material` -> `Submitted Material files`; `intake_attachments` ->
  `Email attachment files`; `unavailable` -> `Project source files`.
- Remove subtitle, recommendation badge, extension/type, reason, availability and visible
  `Use this file:` prefix. Render a compact filename-only list.
- Use existing secondary styling for filename selection and Cancel, primary styling for Upload other
  file; preserve focus, busy/disabled behavior, semantics, responsive stacking and actionable states.

`impeccable` product context influences the result by making the dialog a restrained operational file
list rather than a recommendation dashboard, with concise copy and familiar ConnLab controls.

## 4. Exact file plan

Implementation/test paths are exactly:

1. `backend/application/project_test_plan_source_candidate_service.py`
2. `backend/api/routes_project_test_plan_source_candidates.py`
3. `frontend/src/api/client.ts`
4. `frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.tsx`
5. `frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx`
6. `frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts`
7. `frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx`
8. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
9. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
10. `frontend/src/workbench.css`
11. `tests/unit/test_matrix_source_candidate_service.py`
12. `tests/integration/test_project_test_plan_source_candidates_api.py`

Governance paths are the submitted Task, Plan, fixed Planner/Developer/Reviewer/QA/Integrator evidence
paths, and `docs/task_board.md`; no other submitted path is required.

## 5. Fail-closed boundary

Stop if implementation needs a new endpoint, replacement of Project Workbench provenance, persisted
folder tokens, database/schema/persistence, path registry, attachment copying, recursion, parser or
conversion change, desktop bridge change, Matrix authority change, an arbitrary client path, or any
unapproved file. Filesystem access errors do not silently fall back to another directory.

The `resolved_directory` query is an extension of the existing GET/POST API contract; it adds no API
endpoint. Runtime selection never accepts an old ID after canonical directory identity changes.

## 6. Validation manifest

```json
{"schema":"connlab.validation-manifest","version":1,"task_id":"TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST","checks":[{"id":"source-folder-candidate-contract","kind":"targeted","run_for":["Developer","Reviewer","QA"],"cwd":".","argv":["py","-m","pytest","tests/unit/test_matrix_source_candidate_service.py","tests/integration/test_project_test_plan_source_candidates_api.py","tests/integration/test_project_test_plan_preview_api.py","-q"],"timeout_seconds":900,"permission":"pytest_temp","required":true},{"id":"matrix-source-picker-ui","kind":"targeted","run_for":["Developer","Reviewer","QA"],"cwd":"frontend","argv":["npm","test","--","--run","src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx","src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx","src/features/matrix-editor/MatrixEditorWorkspace.test.tsx"],"timeout_seconds":900,"permission":"workspace","required":true},{"id":"frontend-production-build","kind":"full","run_for":["Developer","QA"],"cwd":"frontend","argv":["npm","run","build"],"timeout_seconds":900,"permission":"workspace","required":true},{"id":"source-candidate-compile","kind":"static","run_for":["Developer","QA"],"cwd":".","argv":["py","-m","py_compile","backend/application/project_test_plan_source_candidate_service.py","backend/api/routes_project_test_plan_source_candidates.py"],"timeout_seconds":120,"permission":"workspace","required":true},{"id":"scope-diff-check","kind":"static","run_for":["Developer","QA"],"cwd":".","argv":["git","diff","--check"],"timeout_seconds":120,"permission":"workspace","required":true}]}
```

QA additionally performs deterministic browser smoke at desktop and 514 px for source title,
filename-only rows, absent legacy metadata, standard buttons, explicit selection, preview, upload,
empty/error, cancel, read-only, focus and overflow. No real external file is mutated.

Backend regressions must include two different canonical resolved directories of the same source kind
containing the same filename: an ID issued for the first directory is rejected after resolution moves
to the second directory. They also prove that no canonical directory text appears in the client token.

## 7. Model routing

| Role | Route |
| --- | --- |
| Developer | `gpt-5.6-sol / medium / risk:api_contract` |
| Reviewer | `gpt-5.6-sol / medium / risk:api_contract` |
| QA | `gpt-5.6-sol / medium / risk:api_contract` |
| Integrator | `gpt-5.6-sol / medium / risk:api_contract` |

Reviewer runs risk-targeted candidate/API and UI checks. QA runs the complete manifest once plus browser
smoke. Integrator verifies subject, scope, evidence, parents/tree, clean state and integration facts
without repeating the matrix.

## 8. Canonical approved request

The following single-line UTF-8 JSON is the byte-identical payload for canonical Approve:

```json
{"schema":"connlab.personal-task-approved-request","version":1,"task_id":"TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST","summary":"Simplify the Matrix Import source chooser to list only selectable .doc, .docx, and .pdf files from the resolved intake-attachment or Submitted Material target folder; show only a concise source-location title and filenames, retain Cancel and Upload other file with standard ConnLab button styling, preserve explicit selection, empty/error states, read-only blocking, desktop behavior, and existing preview authority.","kind":"planned","may_touch":["backend/application/project_test_plan_source_candidate_service.py","backend/api/routes_project_test_plan_source_candidates.py","frontend/src/api/client.ts","frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.tsx","frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx","frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts","frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx","frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx","frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx","frontend/src/workbench.css","tests/unit/test_matrix_source_candidate_service.py","tests/integration/test_project_test_plan_source_candidates_api.py","tasks/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST.md","docs/task_matrix_import_source_picker_target_folder_file_list_plan.md","docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_planner.md","docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_developer.md","docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_reviewer.md","docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_qa.md","docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_integrator.md","docs/task_board.md"],"expected_file_count":20,"classification_reason":"Planned/complex because the correction adds a fail-closed resolved-directory view to the existing project source-candidate API while preserving its registered-asset default, crosses backend and frontend, and requires independent review, QA, integration, build and browser verification.","targeted_validation":["py -m pytest tests/unit/test_matrix_source_candidate_service.py tests/integration/test_project_test_plan_source_candidates_api.py tests/integration/test_project_test_plan_preview_api.py -q","npm test -- --run src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx src/features/matrix-editor/MatrixEditorWorkspace.test.tsx (cwd frontend)","npm run build (cwd frontend)","py -m py_compile backend/application/project_test_plan_source_candidate_service.py backend/api/routes_project_test_plan_source_candidates.py","git diff --check","deterministic browser smoke at desktop and 514px for source title, filename-only allowed rows, absent legacy metadata, standard buttons, explicit selection, upload fallback, empty/error, cancel zero mutation, read-only zero calls and unchanged desktop picker","verify exact approved scope, opaque candidate identity, containment, stale/foreign rejection, clean worktrees and no database, persistence, parser, Matrix authority, public-drive, attachment-copy or external-file mutation"],"forbidden_categories":{"api_contract":true,"database":false,"schema_or_migration":false,"persistence":false,"authority":false,"public_drive_workflow":false,"business_rule_semantics":false,"destructive_action":false,"external_mutation":false,"push_or_release":false}}
```

## 9. Stop point

After Task, Plan and Planner evidence are committed and the callback is consumed, stop at
`awaiting_user_approval`. Do not create a host or implement before explicit approval of the committed
Plan ref and approved-request SHA-256.
