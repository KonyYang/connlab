# TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH Developer Evidence

TASK_ID: TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH
ROLE: Developer
STATUS: ready
SUBJECT: 9f5fda4dbae711eb4e0800b35b8bb90cfc5a96d2
MODEL: gpt-5.6-sol
REASONING_EFFORT: medium
MODEL_ROUTE_REASON: risk:api_contract
ACTION_ID: ca3559014c1c6d37b9df83c3e9131488ecb813cc1d0f8c8845cd3659c5e50a7f
ATTEMPT: 2
PROMPT_SHA256: 5e85345918a7ad0c2de1f67f0ef8515435d6adc214214fd054c2b6b2cf98c7de
NEXT: Reviewer
BLOCKER: none

## Authority and identity

- Plan: `docs/task_matrix_import_source_picker_target_folder_file_list_fresh_plan.md@4249a74f9c672f070112226a6c37bbc705dc8f1c#bd33c088519c1f4c694469f95e2b2436f12e2e7d6105124a1fc2d374d56d514c`.
- Blocking Reviewer evidence: `docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_reviewer.md@5171bdb172dca3e56ae89629283f64967dd148a9#b131e72d3ac3db8e684fb47dfe7257ec64884ca6f3a2591f8df8715d4ad6d093`.
- Accepted Developer evidence: `docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_developer.md@28b3ab84511747546088f27add07c37d175aded5#593b1c838af2b9564cdc1a2fe5d8adbe646d6f05f3c4a814daf1898710478e0f`.
- Approved-request SHA-256: `addc7e5e16a2135702dc84a4c6ee40a1705aa9b36ac1e6696b310125df75f075`.
- Approved validation-manifest SHA-256: `65f31359d60a0868bef3646b17ffee2a09a53a87b193afd196118126c4a63316`.
- Runner-bound manifest digest: `f7e9a8779b724390c61bb970332dfa986315fb6430ef711634224512911f9eb9`.
- Worktree: `D:\PythonProject\connlab-worktrees\task-matrix-import-source-picker-target-folder-file-list`.
- Branch: `codex/task-matrix-import-source-picker-target-folder-file-list`.
- Base: `900c26a78009264ab0fc06f2c038e50d6d280869`.
- Retained ancestor: `163e31d455eb4af12e606288fa36d387c81f1476`.
- Starting subject: `1798d0377347459a78478b9a10e3c2f2a23327e4`.
- Final subject: `9f5fda4dbae711eb4e0800b35b8bb90cfc5a96d2`.
- Exact parent: `9f5fda4d... -> 1798d037...`.
- Branch ref and task-worktree HEAD equal the final subject. Primary and task worktrees are clean.

## Changed paths

The bounded descendant changes exactly:

1. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
2. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

The base-to-final product diff remains exactly the approved 12 paths. `git diff --check 900c26a7..HEAD` passes.

## TDD and focused validation

RED against starting production subject `1798d037...`:

`npm.cmd test -- --run src/features/matrix-editor/MatrixEditorWorkspace.test.tsx -t "shows the browser source picker while candidates load and ignores repeated import requests"`

Result: exit 1; the deferred request exposed the defect because no `dialog` existed while unresolved.

GREEN on the bounded fix:

- Same exact test: 1 passed.
- Full Workspace regression: 49/49 passed.
- Frozen focused frontend set: 55/55 passed:
  `MatrixImportSourceCandidatePicker.test.tsx`, `useMatrixImportSourcePicker.test.tsx`, and
  `MatrixEditorWorkspace.test.tsx`.

The regression proves the existing picker is visible with `aria-busy=true` while unresolved, Import
Matrix is disabled, repeated activation issues only one request, and the same dialog transitions to
the existing error state.

## Self-review

- A synchronous in-flight ref prevents same-tick duplicate races before disabled state renders.
- Only one request may be active, preventing stale completion ordering.
- React owns and discards component-local state after unmount; no external mutation or persistent side
  effect was added.
- The existing picker supplies loading accessibility semantics and disables its actions while busy.
- Desktop native selection, legacy upload fallback, explicit selection, Cancel, Upload, read-only
  behavior, focus conventions, existing copy, and styling remain unchanged.
- Impeccable guidance kept the correction on the existing restrained operational surface with no
  redesign or copy change.

## Final authoritative manifest

Command, run last on the exact clean committed descendant with `browser`, `pytest_temp`, and `workspace`
permissions supplied on the first invocation:

`py -m scripts.connlab_validation_manifest run --authority-root D:\PythonProject\connlab --from-board --role Developer --allow-permission browser --allow-permission pytest_temp --allow-permission workspace`

Result: `ALLOW_VALIDATION`, 9/9 passed in `45,662 ms`; subject before/after remained `9f5fda4d...`.

- `source-folder-candidate-contract`: passed, 13,575 ms.
- `source-folder-read-only-contract`: passed, 7,785 ms.
- `matrix-source-picker-ui`: passed, 12,398 ms.
- `frontend-production-build`: passed, 10,973 ms.
- `source-candidate-compile`: passed, 84 ms.
- `scope-diff-check`: passed, 47 ms.
- `approved-product-scope`: passed, 108 ms.
- `retained-subject-clean-state`: passed, 297 ms.
- `matrix-source-picker-browser-smoke`: passed, 299 ms.

The ignored Plan-frozen fixture rendered the actual picker and Workbench CSS without API or filesystem
operations. Validation-owned Vite and Chrome processes were stopped; no listener remains on ports 5173
or 9222.

## Safety

No tracked byte changed after the final manifest. No Task, Plan, board, role-evidence, backend, API,
client, picker, hook, CSS, database, attachment, source file, public-drive resource, Matrix authority,
governance runtime, branch, ref, or worktree identity was mutated beyond the approved two-file commit.
No push, reset, restore, stash, rebase, cherry-pick, cleanup, deletion, archive, retirement,
branch/worktree move, or resource recreation occurred.
