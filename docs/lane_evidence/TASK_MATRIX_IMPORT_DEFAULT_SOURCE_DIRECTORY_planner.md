# TASK_MATRIX_IMPORT_DEFAULT_SOURCE_DIRECTORY Planner Evidence

TASK_ID: TASK_MATRIX_IMPORT_DEFAULT_SOURCE_DIRECTORY
ROLE: Planner
STATUS: bounded_scope_amendment_pending_user_approval
MODEL: gpt-5.6-sol
REASONING_EFFORT: medium
MODEL_ROUTE_REASON: risk:cross_frontend_backend
ATTEMPT: 1
ACTION_ID: 52ed7cfd1c6a00acd853e4ee75534c147b28f7e3920980d6e223c1480b5b2098
PROMPT_SHA256: 2561494a1e996fe9f448d5d90c0899ede1bde203e8b4793a320ae3e7eaae2e5e
NEXT: User
BLOCKER: none

## Machine Preflight

- Planning base and activation parent: `57a735199927387e0978a92165fd858fce435972`.
- Board was idle with `active=null`, queue `[]`, and raw SHA-256
  `0f5cb07ed8d0619cc65fa02b22717cf38356bb0319a82c0ea60374757f7490af`.
- Canonical Submit returned `ALLOW_ACTIVATE`; activation was committed board-only.
- Planner begin-role and invocation were committed as separate board-only durability transitions.
- Primary was clean before activation and before planning writes.
- No product/test implementation, branch/worktree creation, push, cleanup, or external mutation
  occurred.

## Discovery Evidence

- The selected Matrix Editor button calls a hidden HTML file input; browsers do not provide an API
  to set its starting directory.
- Installed PyWebView accepts an explicit `directory` argument for native file dialogs.
- Existing desktop bridge is Settings-specific and does not have a Matrix source picker.
- Existing project source-candidate service sees project-owned file assets, including controlled
  intake attachment paths.
- Existing official workspace records identify the created project folder and its guaranteed
  `Submitted Material` child.
- Existing path-preview and upload-preview APIs allow desktop and browser paths to converge without
  changing Matrix parser, persistence, or authority behavior.

## Planner Decision

- Classification: complex, because the bounded implementation crosses application/API, desktop
  bridge, and React feature boundaries and extends an API response.
- Route after approval: Developer -> Reviewer -> QA -> Integrator.
- Required route for all four roles: `gpt-5.6-sol / medium / risk:cross_frontend_backend`.
- Exact implementation/test scope is the 15 listed product/test paths plus `docs/task_board.md`.
- No unresolved discovery question changes the file boundary, priority rule, fallback behavior, or
  acceptance criteria.
- Implementation is not authorized until the User approves the exact committed Plan ref and
  canonical approved-request hash.

## Bounded Scope Amendment Evidence

- Amendment attempt: `2` (inline read-only Planner under the active Orchestrator; no role dispatch
  or board transition).
- Source blocker: Developer attempt 2 evidence
  `docs/lane_evidence/TASK_MATRIX_IMPORT_DEFAULT_SOURCE_DIRECTORY_developer.md@f1069be903e866c41be2a994b9e5593e20a64df4#e8591ca4479a53c69df2664db95a20ba3756dbd9695a9e3a7253c90610a076f2`.
- User-confirmed scope addition is exactly:
  - `backend/api/routes_project_test_plan.py`
  - `tests/integration/test_project_test_plan_preview_api.py`
- R1 is limited to forwarding existing locator page/table/query values through the existing
  `matrix-preview-from-path` request into the existing application command.
- R2 remains limited to the originally approved `MatrixEditorWorkspace.test.tsx` regression scope.
- The amended contract has 17 implementation/test paths plus `docs/task_board.md`, 18 total.
- Database, schema/migration, persistence, Matrix authority, parser rules, other APIs, public-drive
  workflows, and business semantics remain forbidden.
- Primary was clean at `03087cdf30a46f005bf4d7fa0d231cc20fcb0e43`; raw board SHA-256 was
  `284243ef33356a80dd4181219bbeed9478e4178ff342bf1cac7dd73665d3b010` and the board remained
  `running/blocked/DEVELOPER_BLOCKED` with no pending callback.
- Candidate remained clean at `f1069be903e866c41be2a994b9e5593e20a64df4`; no candidate, board,
  runtime, test, product, worktree-lifecycle, push, or cleanup write occurred during planning.
- NEXT: User.
- BLOCKER: none.
