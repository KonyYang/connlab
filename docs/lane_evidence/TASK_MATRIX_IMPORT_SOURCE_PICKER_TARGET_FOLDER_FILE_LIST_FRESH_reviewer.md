# TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH Reviewer Evidence

TASK_ID: TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH
ROLE: Reviewer
STATUS: blocked
SUBJECT: 1798d0377347459a78478b9a10e3c2f2a23327e4
MODEL: gpt-5.6-sol
REASONING_EFFORT: medium
MODEL_ROUTE_REASON: risk:api_contract
ACTION_ID: b78591dd5b391b44079ed32bc4d1515d75f1259647a44b9da92a2faa46be9d86
ATTEMPT: 1
PROMPT_SHA256: d8c25cd88040cb9ceb77d5b16ba7cd4f3786d511f0c8ba42c7f6180bf51750f2
NEXT: Developer
BLOCKER: The ordinary-browser workspace never renders or enters the required candidate-loading state while GET is pending, and permits repeated Import Matrix requests.

## Identity and authority

- Plan: `docs/task_matrix_import_source_picker_target_folder_file_list_fresh_plan.md@4249a74f9c672f070112226a6c37bbc705dc8f1c#bd33c088519c1f4c694469f95e2b2436f12e2e7d6105124a1fc2d374d56d514c`.
- Developer evidence: `docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_developer.md@28b3ab84511747546088f27add07c37d175aded5#593b1c838af2b9564cdc1a2fe5d8adbe646d6f05f3c4a814daf1898710478e0f`.
- Approved-request SHA-256: `addc7e5e16a2135702dc84a4c6ee40a1705aa9b36ac1e6696b310125df75f075`.
- Approved manifest SHA-256: `65f31359d60a0868bef3646b17ffee2a09a53a87b193afd196118126c4a63316`.
- Runner-bound manifest digest: `f7e9a8779b724390c61bb970332dfa986315fb6430ef711634224512911f9eb9`.
- Registered worktree: `D:\PythonProject\connlab-worktrees\task-matrix-import-source-picker-target-folder-file-list`.
- Branch/ref: `codex/task-matrix-import-source-picker-target-folder-file-list` at the exact subject.
- Exact ancestry: `1798d037... -> 163e31d4... -> 900c26a7...`; each shown parent is the sole parent.
- Primary HEAD: `ffa938249e7352b87f2af33d1c4ce52a18b0cb54`.
- Primary and task worktrees were clean before validation and after process teardown.

The base-to-subject product/test diff is exactly these 12 modified paths:

1. `backend/api/routes_project_test_plan_source_candidates.py`
2. `backend/application/project_test_plan_source_candidate_service.py`
3. `frontend/src/api/client.ts`
4. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
5. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
6. `frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx`
7. `frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.tsx`
8. `frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx`
9. `frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts`
10. `frontend/src/workbench.css`
11. `tests/integration/test_project_test_plan_source_candidates_api.py`
12. `tests/unit/test_matrix_source_candidate_service.py`

## Standards

No Standards findings. The fixed diff preserves the documented API/application/frontend boundaries,
centralized API calls, restrained filename-only UI, typed route responses, scoped styling, registered-
asset behavior, and approved product scope. No actionable baseline code smell outweighed the frozen design.

## Spec

[P2] Candidate loading and request-busy states are unreachable in the actual workspace.

`MatrixEditorWorkspace.tsx:2676` awaits `chooseMatrixImportSource()` before creating picker state at
lines 2682–2684. The picker is therefore absent for the entire GET. When eventually rendered, line 3639
hard-codes `loading={false}`. The Import Matrix button at lines 3552–3556 is disabled only for read-only
lifecycle state, so repeated clicks can also start overlapping requests.

Although `MatrixImportSourceCandidatePicker.tsx:40–41` implements `aria-busy` and “Loading project
sources...”, the workspace never exercises that branch. This violates Task required behavior 8 and the
Plan's frontend regression requirement for visible loading and busy/disabled behavior.

Developer should expose the picker's loading state before awaiting the ordinary-browser request,
prevent duplicate requests while pending, transition that same surface to loaded/error state, and add a
deferred-request Workspace regression proving loading visibility and single-request busy behavior.

Standards: 0 findings. Spec: 1 finding; worst is P2 unreachable loading/busy behavior.

## Reviewer validation

Command:

`py -m scripts.connlab_validation_manifest run --authority-root D:\PythonProject\connlab --from-board --role Reviewer`

The first invocation supplied the board-declared `browser`, `pytest_temp`, and `workspace` permissions.
Result: `ALLOW_VALIDATION`, 4/4 selected Reviewer checks passed in `82,948 ms`, with subject unchanged:

- `source-folder-candidate-contract`: passed, `17,878 ms`.
- `source-folder-read-only-contract`: passed, `7,758 ms`.
- `matrix-source-picker-ui`: passed, `56,940 ms`.
- `matrix-source-picker-browser-smoke`: passed, `266 ms`.

No Developer/QA-only build, compile, diff, or scope check was rerun.

The Plan-frozen ignored browser config and fixture were used. The fixture rendered the actual picker and
Workbench CSS with `legacy.doc`, `matrix.docx`, and `spec.pdf`; it performed no API or filesystem
operation. Desktop and 514 px smoke passed without required-selector/text loss, horizontal overflow,
runtime exception, or forbidden console output.

The existing local port-5173 Vite precondition served the smoke. A Reviewer-started fallback Vite
selected port 5174 and was terminated. Reviewer-started Chromium CDP was terminated; no Reviewer-owned
5174 or 9222 listener remained.

## Safety

Reviewer made no tracked or untracked product/test/Task/Plan/board/evidence change, wrote no Reviewer
evidence, and created no commit or descendant. No source file, database, persistence, attachment,
Matrix authority, public-drive resource, branch, ref, or worktree was mutated. No push, cleanup,
archive, reset, restore, stash, rebase, cherry-pick, deletion, or resource recreation occurred.
