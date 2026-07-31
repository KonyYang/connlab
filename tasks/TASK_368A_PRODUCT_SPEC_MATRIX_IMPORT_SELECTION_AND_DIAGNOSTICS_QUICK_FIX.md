# TASK_368A_PRODUCT_SPEC_MATRIX_IMPORT_SELECTION_AND_DIAGNOSTICS_QUICK_FIX

Status: `complete` / `accepted` / `locally_integrated`
Lane: `task-368a-product-spec-matrix-import-quick-fix`
Owner role: Integrator closeout complete; no active implementation owner
Date: 2026-07-31

## Current Phase / Why Allowed

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- The user explicitly asked the permanent Quick Fixer to start resolving the reproduced Matrix
  import problem after reviewing the diagnosis.
- The defect is stable, expected behavior is clear, and it does not change Matrix authority,
  persistence, schema, public-drive data, or API contracts.
- The active browser-release lane explicitly excludes frontend Matrix and application/parser
  paths. TASK_368A has no product-path overlap with that lane.
- `docs/task_board.md` remains Orchestrator/Integrator-owned shared governance. Quick Fixer must
  not edit it during implementation.

## Integrator Blocked Checkpoint

- Reviewer status: `reviewer_pass`; blocking and non-blocking findings: none.
- QA status: `qa_pass`; required clean-commit regressions passed.
- Integration input: lane HEAD `826e0a232982153eb00b6fc379892c4611a872e1`.
- Primary pre-merge HEAD: `2e6b1d9bd43ffcfb9e6a15d57a04b543492ff866`.
- The authorized non-fast-forward merge stopped on a content conflict in
  `docs/lane_evidence/TASK_368A_product-spec-matrix-import-selection-and-diagnostics_quick-fixer.md`.
  Primary contains the earlier dispatch checkpoint from `a55e4f22`; the lane contains the later
  Quick Fixer/fix-pass evidence from `144aeb83` and `78dcce7d`.
- Integrator did not select, combine, or discard either evidence version. The failed merge was
  aborted back to the verified clean pre-merge primary state.
- No TASK_368A product/test commit is integrated. No post-merge tests, worktree retirement, push,
  publication, or service restart occurred.
- Residual classification: `conflict` for the shared evidence path, owned by Planner/User
  governance reconciliation. The full clean lane remains `retain` at the exact lane HEAD until a
  new authorized merge attempt; no implementation change is requested.

## Planner Integration Reconciliation

- Planner Discovery found no missing material dispatch fact, product/test change, acceptance
  semantic change, destructive action, or remote action requiring a new user decision.
- Existing Goal authority covers this ordinary evidence reconciliation and local governance
  checkpoint.
- At the next authorized merge attempt, the Quick Fixer conflict path must resolve to the exact
  lane HEAD `826e0a232982153eb00b6fc379892c4611a872e1` blob
  `eff7f9f2c50621ebcc53515b932287225ba8db7a`.
- The lane blob is the chronological successor of the primary dispatch placeholder. It preserves
  the dispatch authorization, diagnosis, ownership, branch/worktree/base, and clean-start facts,
  and replaces pending fields with the reviewed implementation/fix-pass record.
- Primary `approved_ready_for_quick_fixer_dispatch`, `Quick Fixer checkpoint: pending`, and the
  prospective required-record instructions are `stale/superseded`, not unknown discard.
- Lane product/test paths plus Reviewer and QA evidence must remain unchanged.
- Integrator must verify the final index blob, complete nine-path package, Reviewer/QA ancestry,
  and original merged-tree validation before any acceptance claim.
- TASK_368A remains unintegrated, not accepted, and not pushed. The cancelled retained
  browser-release checkpoint remains completely independent and locked.
- Reconciliation evidence:
  `docs/lane_evidence/TASK_368A_product-spec-matrix-import-selection-and-diagnostics_integration-reconciliation_planner.md`.

## Local Integration Acceptance

- Planner-authorized retry pre-merge HEAD:
  `3c4f43bdc2763c0f394b3a4a7e9977cea9fe2973`.
- Complete QA/lane HEAD:
  `826e0a232982153eb00b6fc379892c4611a872e1`.
- Local non-fast-forward merge commit:
  `3bf1f56512eb6593db94111ce55b8a4cb9dd44d2`.
- The sole evidence conflict was closed using the exact authorized lane blob
  `eff7f9f2c50621ebcc53515b932287225ba8db7a`; no product, test, Reviewer, or QA
  evidence content was changed during integration.
- The full nine-path package is integrated. Merged-tree validation passed: backend
  `31 passed`, pycompile passed, MatrixEditorWorkspace `45 passed`, and frontend build
  passed with the existing chunk-size warning only.
- No real DOCX was opened or written. No localhost process was started, stopped, or
  restarted; an already-running localhost may therefore still serve the old process code.
  No publication or remote push occurred.
- The safe retirement script passed dry-run but failed during the real Windows directory
  removal with `Invalid argument`. Git no longer registers the TASK_368A worktree; the
  merged local lane branch remains at the exact lane HEAD, and the non-worktree residual
  directory is retained without force or manual cleanup for permanent Orchestrator/User
  governance.
- The cancelled browser-release checkpoint remains an independent existing `retain` item
  and was not touched.

## Goal

Correct Product Specification Matrix table selection and explicit locator diagnostics so the
GS-12-2186-shaped document selects the real qualification Matrix, rejects the following Revision
Record, honors Page + Keyword as a scoped locator, and preserves the backend's precise blocker in
the Matrix Editor.

The real user attachment is read-only diagnostic evidence. Tests must use synthetic in-repository
data with the same structural characteristics.

## Inputs

- Neutral table snapshots passed to `ProductSpecMatrixParser`.
- Neutral table location metadata: document table index, page number, table-on-page index,
  preceding paragraph, and bounded text preview.
- Optional explicit locator values: Page, Table on page, and Keyword.
- A Matrix preview response containing groups, selected location, warnings, and blockers.

## Outputs

- The structurally valid qualification Matrix is selected.
- Split header text such as `SECTIO N` is recognized only during canonical header matching.
- Revision Record tables with `Rev` or `Revision`, singular or plural `Page(s)`, and
  `Description` or `Date` markers are rejected before loose Matrix header inference.
- Explicit locators fail closed instead of falling back to an unrelated auto-selected table.
- Page + Keyword searches only within the requested page.
- The frontend shows a returned backend blocker before synthesizing page/table mismatch text.

## Acceptance Criteria

1. A synthetic correct Matrix whose header contains `SECTIO N` parses successfully without
   globally changing body text.
2. A following `Rev | Page | Description | EC# | Date` table containing
   `CHANGE GROUP P TEST ITEM` is rejected in both automatic and explicitly selected parsing.
3. The combined synthetic document auto-selects the correct Matrix and yields the expected
   eleven Group labels: `1, 2, 3, 4, 5, 6a, 6b, 7, 8, 9, 10`.
4. Page + Keyword matches only a table on that page.
5. Any supplied locator combination that cannot be satisfied returns a no-match blocker and
   never falls back to automatic table scoring.
6. When a failed preview contains a precise blocker and no selected page, the Matrix Editor
   displays that blocker instead of `Requested page/table did not match a matrix.`
7. Existing parser and Matrix Editor import regressions remain green.

## May Touch

Product:

- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `backend/modules/test_plan/product_spec_matrix_parser_support.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`

Tests:

- new bounded `tests/unit/test_task_368a_product_spec_matrix_import_selection.py`
- exact import/locator regression hunk only in
  `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

Lane-local governance:

- this task and its approved plan, read-only during implementation
- `docs/lane_evidence/TASK_368A_product-spec-matrix-import-selection-and-diagnostics_quick-fixer.md`

The existing oversized Matrix Editor test is an explicit exception because the affected decision
is private component behavior and already has a focused import/locator fixture section. Add at
most the bounded regression needed for acceptance criterion 6; do not refactor the test file.

## Must Not Touch

- Real user DOCX/PDF files or `data/**`.
- Office gateways, conversion/rendering, API routes/DTOs/client contracts.
- Matrix persistence, draft/session/CAS, source replacement, Confirm Matrix, Method authority,
  Fee, Test Record, output records, schema/database/migrations, LTR/public-drive authority.
- Layout, styling, labels, modal structure, or unrelated Matrix Editor behavior.
- Release/packaging paths, the retained browser-release worktree, historical V2 worktrees,
  `.agents/**`, or `docs/project_management/**`.
- `docs/task_board.md` during Quick Fixer implementation.
- Push, destructive cleanup, stash, reset, restore, or unknown residual absorption.

## Locked Paths / Ownership

- TASK_368A exclusively owns the four product paths and two test paths above until Integrator
  closeout.
- The browser-release lane retains exclusive ownership of its release/launcher/runtime paths.
- `docs/task_board.md` is serialized to Orchestrator now and Integrator at closeout.
- The real attachment and every external file are read-only and must not enter the repository.

## Validation Gate

From the lane worktree:

```powershell
py -m pytest tests\unit\test_task_368a_product_spec_matrix_import_selection.py tests\unit\test_product_spec_matrix_parser.py -q
py -m py_compile backend\modules\test_plan\product_spec_matrix_parser.py backend\modules\test_plan\product_spec_matrix_parser_support.py backend\application\project_test_plan_matrix_preview_service.py
Set-Location frontend
npm test -- MatrixEditorWorkspace.test.tsx
npm run build
```

Quick Fixer must use TDD, record RED and GREEN results, create an exact-path local checkpoint
commit, leave the worktree/index clean, update lane evidence to `ready_for_review`, and callback
the permanent Orchestrator.

## Merge Gate

- Exact committed diff stays inside May Touch.
- Reviewer confirms acceptance criteria and no parser over-normalization.
- QA reruns the synthetic parser/locator regression and focused frontend import smoke on the
  reviewed clean commit.
- Integrator updates the board, records an exact residual ledger, integrates locally only when
  authorized, and retires only a clean integrated worktree.
- No remote push.
