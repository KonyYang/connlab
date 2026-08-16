# TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN Plan

Status: `ready_for_user_approval`

## 1. Approved baseline and bounded governance recovery amendment

The previous task's product implementation remains frozen at clean subject
`163e31d455eb4af12e606288fa36d387c81f1476`. The Windows manifest transport correction from `npm`
to `npm.cmd` is retained. The corrected manifest then exposed two bounded defects: the product
candidate identity does not prove in-place same-name replacement, and production Developer re-entry
reused attempt 1 before a failed board replace left partial invalid bytes.

The User authorizes one minimal amendment adding five governance runtime/test paths. It does not
change the existing product/API/UI behavior, role order, schema, callback/evidence contracts or
model routes.

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

## 3. Exact product implementation/test paths (12, frozen)

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

## 3.1 Bounded governance recovery paths (5)

13. `scripts/connlab_serial_phase2.py`
14. `scripts/connlab_serial_native_action.py`
15. `scripts/connlab_serial_board.py`
16. `tests/unit/test_connlab_serial_phase2_runtime.py`
17. `tests/integration/test_connlab_serial_phase2_writer.py`

Governance paths remain exactly the Task, this Plan, five fixed role evidence paths and
`docs/task_board.md`. Total amended scope is 25 unique paths: the existing ordered 20 followed by
the five recovery paths above. Any other path stops for User approval.

## 3.2 Single governance recovery seam

- Mechanically move native-action prompt/attempt construction from the 565-line
  `scripts/connlab_serial_phase2.py` into the sole new module
  `scripts/connlab_serial_native_action.py`.
- Derive `next_attempt(role)` from that role's durable `role_invocations` and
  `timing_facts.roles`, requiring continuous, unique and mutually consistent histories.
  `current_attempt` remains a compatibility snapshot and is not a cross-role counter.
- `scripts/connlab_serial_phase2.py` imports/re-exports the builder and uses the same per-role
  derivation for Reviewer/QA bounded Developer fixes. `BOUNDED_FIX_CODES` remains unchanged;
  `NATIVE_ACTION_FAILED` must not be added.
- `scripts/connlab_serial_board.py` validates role-attempt history as part of the complete v2
  control object. `write_board` validates complete rendered bytes before temporary-file creation,
  validates the flushed/fsynced temporary bytes again before `os.replace`, and performs no fallible
  validation after replacement. Pre-replace failure removes only its temporary file and preserves
  original board bytes, HEAD, index/worktree state and `changed=false`.
- `scripts/connlab_serial_phase2.py`, `scripts/connlab_serial_native_action.py`,
  `scripts/connlab_serial_board.py`, `tests/unit/test_connlab_serial_phase2_runtime.py` and
  `tests/integration/test_connlab_serial_phase2_writer.py` must each remain at or below 500 lines.

## 4. Amended validation manifest

```json
{"schema":"connlab.validation-manifest","version":1,"task_id":"TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN","checks":[{"id":"source-folder-candidate-contract","kind":"targeted","run_for":["Developer","Reviewer","QA"],"cwd":".","argv":["py","-m","pytest","tests/unit/test_matrix_source_candidate_service.py","tests/integration/test_project_test_plan_source_candidates_api.py","tests/integration/test_project_test_plan_preview_api.py","-q"],"timeout_seconds":900,"permission":"pytest_temp","required":true},{"id":"matrix-source-picker-ui","kind":"targeted","run_for":["Developer","Reviewer","QA"],"cwd":"frontend","argv":["npm.cmd","test","--","--run","src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx","src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx","src/features/matrix-editor/MatrixEditorWorkspace.test.tsx"],"timeout_seconds":900,"permission":"workspace","required":true},{"id":"frontend-production-build","kind":"full","run_for":["Developer","QA"],"cwd":"frontend","argv":["npm.cmd","run","build"],"timeout_seconds":900,"permission":"workspace","required":true},{"id":"source-candidate-compile","kind":"static","run_for":["Developer","QA"],"cwd":".","argv":["py","-m","py_compile","backend/application/project_test_plan_source_candidate_service.py","backend/api/routes_project_test_plan_source_candidates.py"],"timeout_seconds":120,"permission":"workspace","required":true},{"id":"scope-diff-check","kind":"static","run_for":["Developer","QA"],"cwd":".","argv":["git","diff","--check"],"timeout_seconds":120,"permission":"workspace","required":true},{"id":"serial-native-action-runtime","kind":"targeted","run_for":["Developer","Reviewer","QA"],"cwd":".","argv":["py","-m","pytest","tests/unit/test_connlab_serial_phase2_runtime.py","-q"],"timeout_seconds":900,"permission":"pytest_temp","required":true},{"id":"serial-writer-atomicity","kind":"targeted","run_for":["Developer","Reviewer","QA"],"cwd":".","argv":["py","-m","pytest","tests/integration/test_connlab_serial_phase2_writer.py","-q"],"timeout_seconds":900,"permission":"pytest_temp","required":true},{"id":"serial-recovery-compatibility","kind":"full","run_for":["Developer","QA"],"cwd":".","argv":["py","-m","pytest","tests/integration/test_connlab_serial_complex_recovery.py","tests/unit/test_connlab_personal_serial_workflow.py","tests/unit/test_connlab_serial_complex_state.py","tests/unit/test_connlab_serial_complex_orchestrator_contract.py","tests/unit/test_task_scoped_role_thread_lifecycle_governance.py","-q"],"timeout_seconds":1200,"permission":"pytest_temp","required":true},{"id":"serial-governance-compile","kind":"static","run_for":["Developer","QA"],"cwd":".","argv":["py","-m","py_compile","scripts/connlab_personal_task.py","scripts/connlab_serial_phase2.py","scripts/connlab_serial_native_action.py","scripts/connlab_serial_board.py"],"timeout_seconds":120,"permission":"workspace","required":true},{"id":"serial-python-line-budget","kind":"static","run_for":["Developer","QA"],"cwd":".","argv":["py","-c","from pathlib import Path; paths=['scripts/connlab_serial_phase2.py','scripts/connlab_serial_native_action.py','scripts/connlab_serial_board.py','tests/unit/test_connlab_serial_phase2_runtime.py','tests/integration/test_connlab_serial_phase2_writer.py']; counts={p:len(Path(p).read_text(encoding='utf-8').splitlines()) for p in paths}; print(counts); raise SystemExit(0 if all(n <= 500 for n in counts.values()) else 1)"],"timeout_seconds":120,"permission":"workspace","required":true}]}
```

Developer runs all assigned checks last against the final exact subject. Reviewer runs the product/API,
UI, native-action and atomic-writer risk checks. QA independently runs its complete set once and
performs deterministic browser smoke at desktop and 514px. Integrator verifies facts without
rerunning the matrix.

Required governance regressions prove Developer blocked/resume `1 -> 2`; Reviewer/QA bounded fixes
increment Developer from Developer history only; first and repeated Planner/Reviewer/QA/Integrator
attempts remain role-local; duplicate/gap/mismatch timing is rejected pre-replace; every writer
`BLOCKED_*` preserves exact board bytes, HEAD, index/worktree state and `changed=false`; and the
current `NATIVE_ACTION_FAILED` scene has a legal production recovery path after approval.

## 5. Model routing

| Role | Model / Effort / Reason |
| --- | --- |
| Developer | `gpt-5.6-sol / medium / risk:api_contract` |
| Reviewer | `gpt-5.6-sol / medium / risk:api_contract` |
| QA | `gpt-5.6-sol / medium / risk:api_contract` |
| Integrator | `gpt-5.6-sol / medium / risk:api_contract` |

## 6. Canonical approved request

```json
{"schema":"connlab.personal-task-approved-request","version":1,"task_id":"TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN","summary":"Simplify the Matrix Import source chooser to list only selectable .doc, .docx, and .pdf files from the resolved intake-attachment or Submitted Material target folder; show only a concise source-location title and filenames, retain Cancel and Upload other file with standard ConnLab button styling, preserve explicit selection, empty/error states, read-only blocking, desktop behavior, and existing preview authority.","kind":"planned","may_touch":["backend/application/project_test_plan_source_candidate_service.py","backend/api/routes_project_test_plan_source_candidates.py","frontend/src/api/client.ts","frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.tsx","frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx","frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts","frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx","frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx","frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx","frontend/src/workbench.css","tests/unit/test_matrix_source_candidate_service.py","tests/integration/test_project_test_plan_source_candidates_api.py","tasks/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN.md","docs/task_matrix_import_source_picker_target_folder_file_list_corrected_plan_plan.md","docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_planner.md","docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_developer.md","docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_reviewer.md","docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_qa.md","docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN_integrator.md","docs/task_board.md","scripts/connlab_serial_phase2.py","scripts/connlab_serial_native_action.py","scripts/connlab_serial_board.py","tests/unit/test_connlab_serial_phase2_runtime.py","tests/integration/test_connlab_serial_phase2_writer.py"],"expected_file_count":25,"classification_reason":"Planned/complex because the existing cross-layer API/UI task now includes an explicitly User-authorized bounded governance writer recovery for per-role durable native-action attempts and fail-closed atomic board persistence; independent Developer, Reviewer, QA and Integrator gates remain mandatory.","targeted_validation":["py -m pytest tests/unit/test_matrix_source_candidate_service.py tests/integration/test_project_test_plan_source_candidates_api.py tests/integration/test_project_test_plan_preview_api.py -q","npm.cmd test -- --run src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx src/features/matrix-editor/MatrixEditorWorkspace.test.tsx (cwd frontend)","npm.cmd run build (cwd frontend)","py -m py_compile backend/application/project_test_plan_source_candidate_service.py backend/api/routes_project_test_plan_source_candidates.py","py -m pytest tests/unit/test_connlab_serial_phase2_runtime.py -q","py -m pytest tests/integration/test_connlab_serial_phase2_writer.py -q","py -m pytest tests/integration/test_connlab_serial_complex_recovery.py tests/unit/test_connlab_personal_serial_workflow.py tests/unit/test_connlab_serial_complex_state.py tests/unit/test_connlab_serial_complex_orchestrator_contract.py tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q","py -m py_compile scripts/connlab_personal_task.py scripts/connlab_serial_phase2.py scripts/connlab_serial_native_action.py scripts/connlab_serial_board.py","verify scripts/connlab_serial_phase2.py, scripts/connlab_serial_native_action.py, scripts/connlab_serial_board.py, tests/unit/test_connlab_serial_phase2_runtime.py and tests/integration/test_connlab_serial_phase2_writer.py are each at most 500 lines","git diff --check","deterministic browser smoke at desktop and 514px for the existing source-picker product contract","verify exact 25-path scope, per-role durable attempt history, pre-replace full-board validation, zero-write BLOCKED_* outcomes, clean primary/task worktrees and unchanged product authority/non-goals"],"forbidden_categories":{"api_contract":true,"database":false,"schema_or_migration":false,"persistence":false,"authority":false,"public_drive_workflow":false,"business_rule_semantics":false,"destructive_action":false,"external_mutation":false}}
```

## 7. Approved execution and stop

After explicit approval of this amended committed Plan ref and approved-request SHA, canonical Approve
synchronizes the exact 25-path scope and preserves the existing host. Production recovery must then
derive canonical Developer attempt 2 from durable Developer history; no hand-built action, repeated
host, manual board edit or bounded-fix allowlist bypass is allowed. Developer completes the bounded
writer and product contract fix, followed by Reviewer, mandatory QA, Integrator, verified local
integration and `implemented_pending_human_review`.

Before approval, commit Task/Plan/Planner evidence, consume the Planner callback and stop at `awaiting_user_approval`.
