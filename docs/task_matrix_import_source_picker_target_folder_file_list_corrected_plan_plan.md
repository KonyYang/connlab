# TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN Plan

Status: `ready_for_user_approval`

## 1. Single correction

The previous task's product implementation remains frozen at clean subject `163e31d455eb4af12e606288fa36d387c81f1476`. Its only blocker was the Windows validation executable name. This Plan changes only the two frontend manifest commands from `npm` to `npm.cmd`; all check IDs, ownership, cwd values, remaining argv, timeouts, permissions and required status remain unchanged.

Retained facts independently verified during planning:

- base `900c26a78009264ab0fc06f2c038e50d6d280869`;
- branch `codex/task-matrix-import-source-picker-target-folder-file-list`;
- worktree `D:\PythonProject\connlab-worktrees\task-matrix-import-source-picker-target-folder-file-list`;
- clean branch/worktree HEAD `163e31d455eb4af12e606288fa36d387c81f1476`;
- base-to-subject diff is exactly the approved 12 implementation/test paths.

## 2. Product contract

Preserve the existing registered-asset default GET/POST behavior. The Matrix browser alone uses `source_scope=resolved_directory` to enumerate direct regular `.doc`, `.docx`, `.pdf` children of the existing preferred directory. Opaque folder IDs bind project ID, source kind, canonical resolved-directory identity and filename without exposing a path; POST re-resolves and re-enumerates before exact matching. Directory changes, same-name replacements, stale/foreign IDs, links escaping containment, unsupported/nested files and unreadable targets fail closed.

The chooser title is `Submitted Material files`, `Email attachment files` or `Project source files`. Rows show filenames only. Cancel and filename selection use existing secondary styling; Upload other file uses existing primary styling. Loading, empty, error, focus, responsive, explicit-selection, read-only, cancel-zero-mutation and desktop-native-picker behavior remain intact.

No database/schema/persistence, new endpoint, parser/conversion, Matrix authority, attachment storage/copy, recursive scan, public-drive or external-file behavior changes.

## 3. Exact implementation/test paths

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

Governance paths are exactly the new Task, this Plan, five fixed role evidence paths and `docs/task_board.md`. Total approved scope is 20 paths. Any new path stops for User approval.

## 4. Corrected validation manifest

```json
{"schema":"connlab.validation-manifest","version":1,"task_id":"TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN","checks":[{"id":"source-folder-candidate-contract","kind":"targeted","run_for":["Developer","Reviewer","QA"],"cwd":".","argv":["py","-m","pytest","tests/unit/test_matrix_source_candidate_service.py","tests/integration/test_project_test_plan_source_candidates_api.py","tests/integration/test_project_test_plan_preview_api.py","-q"],"timeout_seconds":900,"permission":"pytest_temp","required":true},{"id":"matrix-source-picker-ui","kind":"targeted","run_for":["Developer","Reviewer","QA"],"cwd":"frontend","argv":["npm.cmd","test","--","--run","src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx","src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx","src/features/matrix-editor/MatrixEditorWorkspace.test.tsx"],"timeout_seconds":900,"permission":"workspace","required":true},{"id":"frontend-production-build","kind":"full","run_for":["Developer","QA"],"cwd":"frontend","argv":["npm.cmd","run","build"],"timeout_seconds":900,"permission":"workspace","required":true},{"id":"source-candidate-compile","kind":"static","run_for":["Developer","QA"],"cwd":".","argv":["py","-m","py_compile","backend/application/project_test_plan_source_candidate_service.py","backend/api/routes_project_test_plan_source_candidates.py"],"timeout_seconds":120,"permission":"workspace","required":true},{"id":"scope-diff-check","kind":"static","run_for":["Developer","QA"],"cwd":".","argv":["git","diff","--check"],"timeout_seconds":120,"permission":"workspace","required":true}]}
```

Developer runs all assigned checks last against the unchanged exact subject. Reviewer runs the two risk-targeted checks. QA independently runs its complete set once and performs deterministic browser smoke at desktop and 514px. Integrator verifies facts without rerunning the matrix.

## 5. Model routing

| Role | Model / Effort / Reason |
| --- | --- |
| Developer | `gpt-5.6-sol / medium / risk:api_contract` |
| Reviewer | `gpt-5.6-sol / medium / risk:api_contract` |
| QA | `gpt-5.6-sol / medium / risk:api_contract` |
| Integrator | `gpt-5.6-sol / medium / risk:api_contract` |

## 6. Canonical approved request

```json
{"schema":"connlab.personal-task-approved-request","version":1,"task_id":"TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN","summary":"Simplify the Matrix Import source chooser to list only selectable .doc, .docx, and .pdf files from the resolved intake-attachment or Submitted Material target folder; show only a concise source-location title and filenames, retain Cancel and Upload other file with standard ConnLab button styling, preserve explicit selection, empty/error states, read-only blocking, desktop behavior, and existing preview authority.","kind":"planned","may_touch":["backend/application/project_test_plan_source_candidate_service.py","backend/api/routes_project_test_plan_source_candidates.py","frontend/src/api/client.ts","frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.tsx","frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx","frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts","frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx","frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx","frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx","frontend/src/workbench.css","tests/unit/test_matrix_source_candidate_service.py","tests/integration/test_project_test_plan_source_candidates_api.py","tasks/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN.md","docs/task_matrix_import_source_picker_target_folder_file_list_corrected_plan_plan.md","docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_planner.md","docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_developer.md","docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_reviewer.md","docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_qa.md","docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_integrator.md","docs/task_board.md"],"expected_file_count":20,"classification_reason":"Planned/complex because the product change extends the existing project source-candidate API contract while preserving its registered-asset default, crosses backend and frontend, and requires independent review, QA, integration, build and browser verification.","targeted_validation":["py -m pytest tests/unit/test_matrix_source_candidate_service.py tests/integration/test_project_test_plan_source_candidates_api.py tests/integration/test_project_test_plan_preview_api.py -q","npm.cmd test -- --run src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx src/features/matrix-editor/MatrixEditorWorkspace.test.tsx (cwd frontend)","npm.cmd run build (cwd frontend)","py -m py_compile backend/application/project_test_plan_source_candidate_service.py backend/api/routes_project_test_plan_source_candidates.py","git diff --check","deterministic browser smoke at desktop and 514px for source title, filename-only allowed rows, absent legacy metadata, standard buttons, explicit selection, upload fallback, empty/error, cancel zero mutation, read-only zero calls and unchanged desktop picker","verify exact approved scope, opaque candidate identity, containment, stale/foreign rejection, clean worktrees and no database, persistence, parser, Matrix authority, public-drive, attachment-copy or external-file mutation"],"forbidden_categories":{"api_contract":true,"database":false,"schema_or_migration":false,"persistence":false,"authority":false,"public_drive_workflow":false,"business_rule_semantics":false,"destructive_action":false,"external_mutation":false}}
```

## 7. Approved execution and stop

After explicit approval of this committed Plan ref and approved-request SHA, record/reuse the existing clean retained branch/worktree without reset, restore, stash, rebase, cherry-pick, ref movement or replacement host creation. Fresh Developer evidence is required, followed by Reviewer, mandatory QA, Integrator, verified local integration and `implemented_pending_human_review`.

Before approval, commit Task/Plan/Planner evidence, consume the Planner callback and stop at `awaiting_user_approval`.
