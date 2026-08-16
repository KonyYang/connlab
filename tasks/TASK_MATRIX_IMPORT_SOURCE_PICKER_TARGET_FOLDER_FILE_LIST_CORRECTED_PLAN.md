# TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN

Status: `planned` / `governance_recovery_scope_amendment_pending_user_approval`

## Correction authority

The prior product task was production-cancelled solely because its frozen Windows validation manifest used `npm` while the authoritative `shell=False` runner requires `npm.cmd`. Product behavior, exact 12 implementation/test paths, API-contract risk, model routing, browser smoke, acceptance criteria and non-goals are unchanged.

## Retained implementation

- Base: `900c26a78009264ab0fc06f2c038e50d6d280869`.
- Branch: `codex/task-matrix-import-source-picker-target-folder-file-list`.
- Worktree: `D:\PythonProject\connlab-worktrees\task-matrix-import-source-picker-target-folder-file-list`.
- Clean subject/HEAD: `163e31d455eb4af12e606288fa36d387c81f1476`.
- The subject changes exactly the 12 approved implementation/test paths.
- Historical focused results: backend 12 passed, frontend 54 passed, `git diff --check` passed. Fresh corrected-task validation and evidence remain mandatory.

## Required behavior

1. The ordinary-browser Matrix Import chooser requests the existing endpoints' bounded `resolved_directory` view; registered-asset defaults remain unchanged.
2. List only direct regular `.doc`, `.docx`, `.pdf` files from the resolved `Submitted Material` or parsed-email attachment directory.
3. Bind each opaque ID to project, source kind, canonical resolved-directory identity and exact filename; never expose or accept a path. Re-resolve on selection and reject stale, moved, foreign, escaped or same-name-in-another-directory IDs.
4. Show only a source-kind title and filename selection rows. Remove recommendation, type/source, reason, availability, subtitle and `Use this file:` copy.
5. Keep explicit selection, Cancel, Upload other file, empty/error/loading states, standard ConnLab buttons, read-only blocking, cancel zero mutation and desktop native picker behavior.
6. Preserve Matrix authority, preview/parser capability, database, persistence and project attachment storage.

## Exact product implementation/test scope (12, frozen)

- `backend/application/project_test_plan_source_candidate_service.py`
- `backend/api/routes_project_test_plan_source_candidates.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.tsx`
- `frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx`
- `frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts`
- `frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_matrix_source_candidate_service.py`
- `tests/integration/test_project_test_plan_source_candidates_api.py`

## Bounded governance recovery scope (5)

1. `scripts/connlab_serial_phase2.py`
2. `scripts/connlab_serial_native_action.py`
3. `scripts/connlab_serial_board.py`
4. `tests/unit/test_connlab_serial_phase2_runtime.py`
5. `tests/integration/test_connlab_serial_phase2_writer.py`

These paths may only repair per-role durable attempt allocation and fail-closed pre-replace board
validation. `NATIVE_ACTION_FAILED` must not be added to the generic bounded-fix allowlist. No role
order, schema, callback, evidence or product contract may change.

The eight governance paths remain the Task, Plan, fixed Planner/Developer/Reviewer/QA/Integrator
evidence paths and `docs/task_board.md`. The amended approved scope is exactly 25 unique paths:
12 frozen product implementation/test paths, 5 bounded governance recovery paths and 8 fixed
governance paths.

## Governance recovery acceptance

- Native-action attempts are derived independently for each role from durable invocation and timing
  history; `current_attempt` is not a cross-role counter.
- Developer attempt 1 blocked and resumed must produce canonical Developer attempt 2.
- Reviewer/QA bounded fixes increment Developer from Developer history only; first and repeated
  Planner/Reviewer/QA/Integrator attempts do not borrow another role's count.
- Duplicate, gapped or mismatched role timing/invocation identity is rejected before board replace.
- `write_board` validates the complete rendered and temporary bytes before `os.replace`; any
  validation/write failure preserves the original board bytes, HEAD, index/worktree state and
  `changed=false`.
- The current `NATIVE_ACTION_FAILED` scene must recover through the ordinary production writer after
  the amended Plan is approved, without hand-built actions or manual board edits.

## Non-goals

No new endpoint, database/schema/persistence, registry, attachment copy, recursive scan, parser/conversion change, Matrix authority change, desktop bridge change, upload refactor, external-file mutation, push, cleanup, reset, restore, stash, rebase, cherry-pick or ref movement.

## Execution after amendment approval

Reuse the retained branch/worktree without moving it. Canonical Approve synchronizes the exact
25-path scope. A fresh Developer implements the bounded governance recovery and the still-approved
source-candidate contract fix, creates a clean subject and returns fresh evidence. Fresh Reviewer,
mandatory QA and Integrator then complete the normal local integration chain. Stop at
`implemented_pending_human_review`.
