# TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH Planner Evidence

TASK_ID: TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH
ROLE: Planner
STATUS: ready
SUBJECT: 7b71998f7cce663c0b9f96eca20a1b605d602537
MODEL: gpt-5.6-sol
REASONING_EFFORT: medium
MODEL_ROUTE_REASON: risk:api_contract
ACTION_ID: cde5e45db502422cbb8f514ef034d3bd1b82d5fb25162cf9a683424cfebb531a
ATTEMPT: 1
NEXT: User
BLOCKER: none

## Machine authority

- Durable Planner prompt SHA-256:
  `0672b4eaf10d8299764f281de13d80ba336c3165e415a053451cee044a27a66f`.
- Primary was clean at
  `7b71998f7cce663c0b9f96eca20a1b605d602537`.
- Active activation parent was
  `5c4af0aec50346c940cb486ea2faf975c2838277`.
- Board raw SHA-256 was
  `1d3677ca3040b44e8b70cea4fcd2ab62f11ff09541e5b8b377c9c9350a034420`.
- Board authority was
  `running / planning / Planner attempt 1 / callback_pending`.
- Pending action matched this evidence's action ID and attempt.

## Committed planning identity

- Exact Plan ref:
  `docs/task_matrix_import_source_picker_target_folder_file_list_fresh_plan.md@4249a74f9c672f070112226a6c37bbc705dc8f1c#bd33c088519c1f4c694469f95e2b2436f12e2e7d6105124a1fc2d374d56d514c`.
- The current Task and Plan have no byte difference from commit
  `4249a74f9c672f070112226a6c37bbc705dc8f1c`.
- Canonical approved-request SHA-256:
  `addc7e5e16a2135702dc84a4c6ee40a1705aa9b36ac1e6696b310125df75f075`.
- Validation-manifest SHA-256:
  `65f31359d60a0868bef3646b17ffee2a09a53a87b193afd196118126c4a63316`.
- The board's ordered 20 `approved_code_paths` exactly equal the canonical approved request's ordered
  `may_touch`; no governance writer/runtime path is present.

## Retained subject identity

- Retained branch:
  `codex/task-matrix-import-source-picker-target-folder-file-list`.
- Retained worktree:
  `D:\PythonProject\connlab-worktrees\task-matrix-import-source-picker-target-folder-file-list`.
- Branch ref and clean worktree HEAD both equal
  `1798d0377347459a78478b9a10e3c2f2a23327e4`.
- Exact linear ancestry is
  `1798d0377347459a78478b9a10e3c2f2a23327e4`
  -> `163e31d455eb4af12e606288fa36d387c81f1476`
  -> `900c26a78009264ab0fc06f2c038e50d6d280869`.
- Base-to-subject changes exactly the frozen 12 product/test paths and nothing else.
- The Plan freezes `163e31d4...` as the retained starting ancestor and permits one bounded child;
  `1798d037...` is that anticipated child.

## Product and behavior verification

- The service enumerates only direct regular `.doc`, `.docx`, and `.pdf` files from the resolved
  preferred directory.
- Candidate identity is path-free and binds project, source kind, canonical directory, exact filename,
  and a read-only file-instance/content fingerprint.
- Subject `1798d037...` rejects same-path, same-name replacement using current bytes and descriptor
  identity without mutating the source.
- POST re-resolves/re-enumerates and exact-matches the submitted opaque ID before the unchanged Matrix
  preview handoff.
- Existing GET/POST endpoints, registered-asset default, Matrix authority, parser/conversion, database,
  persistence, attachment storage, desktop picker, Upload, Cancel, empty/error/read-only behavior and
  external files remain unchanged.
- The browser picker retains the concise source title and filename-only choices.

## Plan completeness and route

- The committed Plan contains exactly one complete nine-check validation manifest.
- Windows frontend commands use `npm.cmd` for Vitest and the production build.
- The matrix covers backend candidate/API/preview, no-mutation, frontend picker/hook/Workspace,
  production build, Python compilation, diff/scope, retained-host clean state and browser smoke.
- Developer, Reviewer, QA and Integrator routes remain
  `gpt-5.6-sol / medium / risk:api_contract`.

## Planner decision and safety

No identity, hash, ordered scope, route, behavior, Plan or retained-subject drift was found. No Plan,
Task or product rewrite is required. The task is ready for User approval of the unchanged Plan ref.

The Planner performed no board, implementation, index, ref, branch, worktree, test, browser, database,
attachment or external-resource write.

STATUS: ready

NEXT: User

BLOCKER: none
