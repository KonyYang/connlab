# TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH Plan

Status: `ready_for_user_approval`

## 1. Confirmed repository facts

The retained product branch/worktree is clean at
`163e31d455eb4af12e606288fa36d387c81f1476`, whose sole parent is
`900c26a78009264ab0fc06f2c038e50d6d280869`. The base-to-subject diff is exactly the approved 12
product implementation/test paths.

The retained implementation already provides the existing endpoints' browser-only
`resolved_directory` query, direct `.doc/.docx/.pdf` enumeration, canonical-directory-bound opaque IDs,
filename-only picker UI, explicit selection and preserved desktop behavior. Historical focused backend
12 and frontend 54 tests passed. The corrected authoritative candidate/API/preview command later failed
with exit code 1, but its node and trace were not retained.

Static inspection identifies one definite missing contract: `_resolved_directory_candidate_id`
currently digests project ID, source kind, canonical directory and filename only. Replacing the file
contents at the same path and name can preserve the old ID.

## 2. Single bounded solution

Keep the existing GET/POST endpoints and the registered-asset default. Complete the browser-only
resolved-directory identity:

```text
GET resolved_directory
-> resolve existing Submitted Material or parsed email-attachment directory
-> enumerate immediate regular .doc/.docx/.pdf children
-> open each candidate read-only
-> derive a stable current-file fingerprint
-> digest project + source kind + canonical directory + filename + fingerprint
-> return path-free folder-* ID and filename-only metadata

POST resolved_directory selection
-> recompute preferred directory and current candidates
-> exact-match the submitted opaque ID
-> reject mismatch before preview
-> call the unchanged Matrix preview service
```

The file fingerprint is digest-only and combines read-only file-instance metadata
(`st_dev`, `st_ino`, `st_size`, `st_mtime_ns`, `st_ctime_ns` when supplied by the platform) with a
streamed SHA-256 of current file bytes. Compare file-descriptor metadata before and after hashing and
fail closed if the file changes during enumeration. This rejects an equal-length in-place rewrite even
when its modification timestamp is restored. A byte-identical replacement is additionally separated
when the platform exposes a changed file identity/creation metadata; no path or fingerprint component
is exposed to the client.

## 3. Tight RED diagnosis and implementation

After approval, the Developer must:

1. Reuse, without moving or recreating, branch
   `codex/task-matrix-import-source-picker-target-folder-file-list` and worktree
   `D:\PythonProject\connlab-worktrees\task-matrix-import-source-picker-target-folder-file-list` at
   clean subject `163e31d455eb4af12e606288fa36d387c81f1476`.
2. Run the focused candidate/API/preview pytest command once with `-x -vv` to capture the exact existing
   failing node and trace. This diagnostic result is not final evidence.
3. Add the exact regression
   `test_resolved_directory_candidate_rejects_in_place_same_name_replacement` using equal-length
   different bytes and restored mtime; prove it RED.
4. Add the exact read-only regression
   `test_resolved_directory_listing_and_selection_do_not_mutate_source_file`.
5. Implement only the smallest service/API correction required by the captured failure and stale
   replacement contract.
6. Run the narrow RED node until GREEN, then the relevant candidate/API command.
7. Self-review, commit a single bounded child when code/test bytes changed, and run the complete
   approved manifest last on that exact clean subject. Any later product/test byte change invalidates
   the result and requires the affected complete final checks again.

No frontend production byte should change merely to restage the retained implementation. A frontend
path may change only when one of the approved focused tests or the browser smoke proves a contract
defect inside this scope.

## 4. File-level approach

- `backend/application/project_test_plan_source_candidate_service.py`
  - keep preferred-directory resolution and direct enumeration;
  - calculate the current read-only file fingerprint;
  - include it only inside the opaque candidate digest;
  - compare descriptor metadata around hashing and fail closed on concurrent change;
  - preserve registered-asset behavior and internal Path-only preview handoff.

- `backend/api/routes_project_test_plan_source_candidates.py`
  - preserve the existing routes and bounded `source_scope=resolved_directory` query;
  - preserve typed responses and current 400/404 mapping;
  - change only if the captured API failure proves a route-level correction is required.

- `tests/unit/test_matrix_source_candidate_service.py`
  - retain canonical-directory/same-name coverage;
  - add in-place same-name replacement, read-only/no-mutation, stale/foreign,
    escaped/unsupported/nested and path-opacity regressions.

- `tests/integration/test_project_test_plan_source_candidates_api.py`
  - preserve registered-asset default coverage;
  - prove resolved-directory GET/POST, stale replacement rejection, filename-only response data and
    unchanged source file behavior.

- `frontend/src/api/client.ts`,
  `frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.tsx`,
  `frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts`,
  `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`,
  their three focused test files, and `frontend/src/workbench.css`
  - treat retained bytes as the baseline;
  - verify browser-only resolved-directory calls, filename-only UI, explicit selection,
    loading/empty/error, Upload/Cancel, read-only zero-call, desktop behavior, focus and 514 px layout;
  - change only a proved defect within the frozen product contract.

## 5. Exact may_touch scope (20)

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
13. `tasks/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH.md`
14. `docs/task_matrix_import_source_picker_target_folder_file_list_fresh_plan.md`
15. `docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_planner.md`
16. `docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_developer.md`
17. `docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_reviewer.md`
18. `docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_qa.md`
19. `docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_integrator.md`
20. `docs/task_board.md`

Expected scope count is exactly 20. The task worktree's product diff must remain exactly the first 12
paths. No `scripts/connlab_*`, workflow test, governance writer/runtime or other repository path is
approved.

## 6. Fail-closed regression matrix

Backend/service/API regressions must prove:

- direct regular `.doc`, `.docx`, `.pdf` enumeration and deterministic filename order;
- canonical resolved-directory identity changes the ID while its text never appears in the token;
- same filename under a different canonical directory invalidates the old ID;
- equal-length, same-path, same-name content replacement with restored mtime invalidates the old ID;
- rename, deletion, foreign project ID and stale opaque ID return not-found before preview;
- escaped/link, unsupported and nested targets are not listed and cannot be selected;
- a file that changes while it is fingerprinted fails closed;
- listing and source-path resolution preserve source bytes and metadata;
- registered-asset default GET/POST behavior remains unchanged;
- `.doc` capability remains owned by the existing preview/conversion path.

Frontend regressions must prove:

- only the ordinary browser asks for `resolved_directory`;
- source titles map to submitted material, email attachments and unavailable;
- rows contain filenames only and omit recommendation, type/source, reason, availability, path and
  `Use this file:` copy;
- no preview occurs before explicit filename selection;
- Upload other file opens the existing upload path;
- Cancel closes the picker with zero preview/upload/import mutation;
- loading, empty, error, busy/disabled and focus behavior remain usable;
- read-only mode invokes neither picker, preview nor upload;
- desktop still projects the existing initial directory into the native picker;
- the 514 px picker has reachable stacked actions and no horizontal overflow.

## 7. Complete initial validation manifest

This is the complete initial and final manifest. It uses `npm.cmd` from initial approval. It must not
be amended later.

```json
{"schema":"connlab.validation-manifest","version":1,"task_id":"TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH","checks":[{"id":"source-folder-candidate-contract","kind":"targeted","run_for":["Developer","Reviewer","QA"],"cwd":".","argv":["py","-m","pytest","tests/unit/test_matrix_source_candidate_service.py","tests/integration/test_project_test_plan_source_candidates_api.py","tests/integration/test_project_test_plan_preview_api.py","-q"],"timeout_seconds":900,"permission":"pytest_temp","required":true},{"id":"source-folder-read-only-contract","kind":"targeted","run_for":["Developer","Reviewer","QA"],"cwd":".","argv":["py","-m","pytest","tests/unit/test_matrix_source_candidate_service.py::test_resolved_directory_listing_and_selection_do_not_mutate_source_file","-q"],"timeout_seconds":300,"permission":"pytest_temp","required":true},{"id":"matrix-source-picker-ui","kind":"targeted","run_for":["Developer","Reviewer","QA"],"cwd":"frontend","argv":["npm.cmd","test","--","--run","src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx","src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx","src/features/matrix-editor/MatrixEditorWorkspace.test.tsx"],"timeout_seconds":900,"permission":"workspace","required":true},{"id":"frontend-production-build","kind":"full","run_for":["Developer","QA"],"cwd":"frontend","argv":["npm.cmd","run","build"],"timeout_seconds":900,"permission":"workspace","required":true},{"id":"source-candidate-compile","kind":"static","run_for":["Developer","QA"],"cwd":".","argv":["py","-m","py_compile","backend/application/project_test_plan_source_candidate_service.py","backend/api/routes_project_test_plan_source_candidates.py"],"timeout_seconds":120,"permission":"workspace","required":true},{"id":"scope-diff-check","kind":"static","run_for":["Developer","QA"],"cwd":".","argv":["git","diff","--check","900c26a78009264ab0fc06f2c038e50d6d280869..HEAD"],"timeout_seconds":120,"permission":"workspace","required":true},{"id":"approved-product-scope","kind":"static","run_for":["Developer","QA"],"cwd":".","argv":["py","-c","from subprocess import check_output; base='900c26a78009264ab0fc06f2c038e50d6d280869'; expected=['backend/application/project_test_plan_source_candidate_service.py','backend/api/routes_project_test_plan_source_candidates.py','frontend/src/api/client.ts','frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.tsx','frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx','frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts','frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx','frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx','frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx','frontend/src/workbench.css','tests/unit/test_matrix_source_candidate_service.py','tests/integration/test_project_test_plan_source_candidates_api.py']; actual=check_output(['git','diff','--name-only',base+'..HEAD'],text=True,encoding='utf-8').splitlines(); print({'expected':expected,'actual':actual}); raise SystemExit(0 if len(actual)==len(expected) and set(actual)==set(expected) else 1)"],"timeout_seconds":120,"permission":"workspace","required":true},{"id":"retained-subject-clean-state","kind":"static","run_for":["Developer","QA"],"cwd":".","argv":["py","-c","import subprocess; q=lambda *a: subprocess.check_output(['git',*a],text=True,encoding='utf-8').strip(); start='163e31d455eb4af12e606288fa36d387c81f1476'; base='900c26a78009264ab0fc06f2c038e50d6d280869'; branch=q('branch','--show-current'); parent_line=q('rev-list','--parents','-n','1',start); head=q('rev-parse','HEAD'); task_clean=not q('status','--porcelain=v1','--untracked-files=all'); primary='D:/PythonProject/connlab'; primary_clean=not subprocess.check_output(['git','-C',primary,'status','--porcelain=v1','--untracked-files=all'],text=True,encoding='utf-8').strip(); ancestor=subprocess.run(['git','merge-base','--is-ancestor',start,'HEAD'],check=False).returncode==0; print({'branch':branch,'head':head,'parent_line':parent_line,'ancestor':ancestor,'task_clean':task_clean,'primary_clean':primary_clean}); raise SystemExit(0 if branch=='codex/task-matrix-import-source-picker-target-folder-file-list' and parent_line==start+' '+base and ancestor and task_clean and primary_clean else 1)"],"timeout_seconds":120,"permission":"workspace","required":true},{"id":"matrix-source-picker-browser-smoke","kind":"ui","run_for":["Developer","Reviewer","QA"],"cwd":".","argv":["node","scripts/connlab_ui_smoke.mjs","--config","tmp/matrix-source-picker-ui-smoke.json"],"timeout_seconds":180,"permission":"browser","required":true}]}
```

The deterministic browser fixture is validation-only and ignored by Git. Before each complete
Developer/QA invocation, prepare the exact frozen config at
`tmp/matrix-source-picker-ui-smoke.json` and an ignored
`frontend/tmp/matrix-source-picker-ui-smoke.html` entry that renders the actual
`MatrixImportSourceCandidatePicker` with `legacy.doc`, `matrix.docx` and `spec.pdf`, imports the actual
Workbench CSS, and performs no API or filesystem operation. Start the existing frontend Vite server at
`127.0.0.1:5173` and system Chromium CDP at `127.0.0.1:9222`. These disposable ignored fixtures are test
preconditions, not repository implementation paths or manifest amendments.

The exact config bytes are:

```text
{"schema":"connlab.ui-smoke","version":1,"endpoint":"http://127.0.0.1:9222","url":"http://127.0.0.1:5173/tmp/matrix-source-picker-ui-smoke.html","viewports":[{"name":"desktop","width":1280,"height":800},{"name":"narrow-514","width":514,"height":831}],"required_selectors":["[role=\"dialog\"][aria-modal=\"true\"]","[data-testid=\"matrix-import-source-name\"]",".matrix-import-source-picker footer .matrix-editor-import-secondary-button",".matrix-import-source-picker footer .matrix-editor-import-primary-button"],"required_text":["Submitted Material files","legacy.doc","matrix.docx","spec.pdf","Cancel","Upload other file"],"forbidden_console_patterns":["uncaught","failed to fetch","typeerror","referenceerror"],"timeout_ms":30000}
```

Developer runs every Developer check last on the final exact subject. Reviewer uses `$code-review` and
selects only candidate/API, read-only, picker UI or browser check IDs relevant to findings and risk.
QA independently runs every QA check once on the clean reviewed subject. Integrator does not repeat the
manifest; it verifies exact subject, 20-path authority, 12-product-path diff, evidence topology, raw
digests, branch/worktree identity, clean states, merge parents/tree and absence of prohibited mutation.

## 8. Model routing

| Role | Model / Effort / Reason |
| --- | --- |
| Developer | `gpt-5.6-sol / medium / risk:api_contract` |
| Reviewer | `gpt-5.6-sol / medium / risk:api_contract` |
| QA | `gpt-5.6-sol / medium / risk:api_contract` |
| Integrator | `gpt-5.6-sol / medium / risk:api_contract` |

These routes are frozen unless machine authority proves a different route before approval.

## 9. Design and architecture constraints

`impeccable`, `PRODUCT.md`, `DESIGN.md`, `docs/02_ARCHITECTURE_RULES.md` and
`docs/frontend_architecture_rules.md` make this a restrained operational file list:

- source state before action;
- concise business-readable title;
- filename-only choices;
- standard existing primary/secondary controls;
- visible loading, empty, error, disabled and focus states;
- no recommendation dashboard, path disclosure, decorative card metadata or new modal framework;
- API calls remain centralized in `frontend/src/api/client.ts`;
- browser code never touches local files directly.

## 10. Risks and rollback

- Fingerprinting reads each eligible direct file. Stream bytes in bounded chunks and surface unreadable
  or concurrently changing files as an actionable fail-closed source-folder error.
- Files can change after path resolution. Re-enumeration and before/after descriptor checks close the
  approved stale-token window; the unchanged preview service remains responsible after selection.
- Existing ephemeral `folder-*` IDs change when a file changes. They are not persisted, so no migration
  is required.
- The retained backend failure may be independent of the known fingerprint gap. The Developer must
  capture it first and fix only an approved product path.
- Rollback requires only an explicitly authorized Git revert of the bounded child commit; there is no
  data migration or external artifact to undo. No automatic reset, restore or cleanup is permitted.

## 11. Canonical approved request

The following single-line UTF-8 JSON is the byte-identical canonical Approve payload:

```json
{"schema":"connlab.personal-task-approved-request","version":1,"task_id":"TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH","summary":"In the ordinary-browser Matrix Editor, list only direct .doc, .docx and .pdf files from the resolved email-attachment or Submitted Material project folder, show a concise source title and filename-only choices, preserve explicit selection, Cancel, Upload other file, empty/error/read-only states and desktop picker behavior, reuse retained clean implementation as the starting point, diagnose the failed source-folder candidate contract, and reject stale in-place same-name replacements without adding endpoints, persistence or path exposure.","kind":"planned","may_touch":["backend/application/project_test_plan_source_candidate_service.py","backend/api/routes_project_test_plan_source_candidates.py","frontend/src/api/client.ts","frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.tsx","frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx","frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts","frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx","frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx","frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx","frontend/src/workbench.css","tests/unit/test_matrix_source_candidate_service.py","tests/integration/test_project_test_plan_source_candidates_api.py","tasks/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH.md","docs/task_matrix_import_source_picker_target_folder_file_list_fresh_plan.md","docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_planner.md","docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_developer.md","docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_reviewer.md","docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_qa.md","docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_integrator.md","docs/task_board.md"],"expected_file_count":20,"classification_reason":"Planned/complex because this is a retained cross-backend/frontend API-contract task with a known authoritative backend/API validation failure, a missing stale in-place replacement identity guarantee, a complete frozen build/browser validation matrix, and mandatory independent Reviewer, QA and Integrator gates.","targeted_validation":["py -m pytest tests/unit/test_matrix_source_candidate_service.py tests/integration/test_project_test_plan_source_candidates_api.py tests/integration/test_project_test_plan_preview_api.py -q","py -m pytest tests/unit/test_matrix_source_candidate_service.py::test_resolved_directory_listing_and_selection_do_not_mutate_source_file -q","npm.cmd test -- --run src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx src/features/matrix-editor/MatrixEditorWorkspace.test.tsx (cwd frontend)","npm.cmd run build (cwd frontend)","py -m py_compile backend/application/project_test_plan_source_candidate_service.py backend/api/routes_project_test_plan_source_candidates.py","git diff --check 900c26a78009264ab0fc06f2c038e50d6d280869..HEAD","verify the base-to-HEAD product diff is exactly the frozen 12 product implementation/test paths","verify retained subject 163e31d455eb4af12e606288fa36d387c81f1476 remains an ancestor, its sole parent is 900c26a78009264ab0fc06f2c038e50d6d280869, the retained branch identity is unchanged, and primary/task worktrees are clean","node scripts/connlab_ui_smoke.mjs --config tmp/matrix-source-picker-ui-smoke.json at desktop 1280x800 and narrow 514x831","verify read-only source bytes/metadata, path-free opaque IDs, no external-file mutation, no new endpoint, database/schema/persistence, attachment copy, recursion, parser/conversion, Matrix authority, desktop bridge, public-drive or governance-runtime change"],"forbidden_categories":{"api_contract":true,"database":false,"schema_or_migration":false,"persistence":false,"authority":false,"public_drive_workflow":false,"business_rule_semantics":false,"destructive_action":false,"external_mutation":false}}
```

## 12. Approval and stop

After the primary orchestrator writes and commits the exact Task, Plan and Planner evidence, it must
consume the Planner callback and stop at `awaiting_user_approval`.

Only explicit User approval of the exact committed Plan ref and canonical approved-request bytes may
continue. Approval must store this initial manifest and the four frozen execution routes. After
approval, record and reuse the retained worktree without moving its branch/ref. No host creation,
implementation, test, role dispatch or external mutation is authorized before approval.
