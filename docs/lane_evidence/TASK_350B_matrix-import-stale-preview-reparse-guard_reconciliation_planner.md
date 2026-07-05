# TASK_350B Matrix Import Stale Preview Reparse Guard - Planner Reconciliation Evidence

Task: `TASK_350B_MATRIX_IMPORT_STALE_PREVIEW_REPARSE_GUARD`
Lane: `matrix-import-stale-preview-reparse-guard`
Role: Planner
Status: implementation authorized - pending Developer implementation
Date: 2026-07-05

## Gate

Planner source-of-truth reconciliation only.

No product code, frontend runtime code, backend code, tests, API client, parser, preview service, `.agents/**`, or `docs/project_management/**` files were modified by this Planner pass.

## Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `tasks/TASK_350B_MATRIX_IMPORT_STALE_PREVIEW_REPARSE_GUARD.md`
- `docs/task_350b_matrix_import_stale_preview_reparse_guard_plan.md`
- `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_planner.md`
- `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_developer.md`
- Current `git status --short`

## Reconciled Fact Chain

- Planner created TASK_350B as a formal lightweight frontend follow-up lane.
- User updated the requirement after the first Reviewer plan pass and before Developer planning-first approval.
- Planner updated the task, plan, evidence, and board so stale `Replace` auto-runs Reparse instead of being disabled merely because stale.
- Reviewer plan re-gate passed on the updated behavior contract.
- User approved TASK_350B for Developer planning-first.
- Developer planning-first completed and recorded evidence in `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_developer.md`.
- Reviewer implementation-readiness passed.
- User approved TASK_350B source-of-truth reconciliation and Developer implementation.

## Implementation Authorization

TASK_350B is now implementation authorized / pending Developer implementation.

This is not completion. Reviewer implementation gate, QA gate, and Integrator packaging remain required.

## Preserved Behavior Contract

- Record `lastParsedLocator` after initial preview success and manual Reparse success.
- Detect stale preview when current Page / Table on page / Keyword differs from `lastParsedLocator`.
- Stale `Replace` auto-runs Reparse with the current locator before commit.
- Auto-Reparse success with usable Matrix groups updates `importPreview` and `lastParsedLocator`, then continues the original Replace/commit.
- Auto-Reparse failure, invalid input, page-table mismatch, or no usable Matrix groups keeps the modal open, shows the in-dialog result/error, and does not commit.
- Manual Reparse remains available.
- Non-stale Replace commits the current preview directly without another preview call.
- Reparse/Replace busy state must disable conflicting inputs and actions.

## Authorized Future Implementation May Touch

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_developer.md`
- TASK_350B task/plan/evidence/board through normal lane flow

## Scope Locks

- No `backend/**`.
- No `frontend/src/api/client.ts`.
- No Matrix parser rule changes.
- No backend preview service or route changes.
- No TASK_350A `.doc` conversion backend flow changes.
- No Confirmed Matrix authority, Fee Evaluation, Test Record generation, lifecycle semantics, Folder Actions / public folder workflow, Intake / LTR workflow, Projects registry/list, release/settings cleanup, or unrelated residual cleanup.
- No `.agents/**`.
- No `docs/project_management/**`.

## External Residuals Excluded

Current workspace status includes external release/settings/desktop/New Project residuals and untracked files. They remain excluded from TASK_350B reconciliation and are not authorized for Developer packaging.

## Validation

- `git diff --check -- docs/task_board.md tasks/TASK_350B_MATRIX_IMPORT_STALE_PREVIEW_REPARSE_GUARD.md docs/task_350b_matrix_import_stale_preview_reparse_guard_plan.md docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_reconciliation_planner.md`: passed with Git LF/CRLF warning for `docs/task_board.md` only.
- Trailing whitespace scan on touched TASK_350B docs/board/evidence: no matches.
- Targeted status shows this Planner pass touched `docs/task_board.md`, TASK_350B task/plan docs, and this reconciliation evidence.
- Targeted status shows external backend/settings/desktop/New Project residuals; they remain excluded and are not authorized for TASK_350B packaging.
- Targeted status shows no `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`, `frontend/src/api/client.ts`, parser, preview service, route, `.agents/**`, or `docs/project_management/**` product/governance implementation changes from this Planner pass.

## Next Role

Developer implementation pass.

## Stop Point

Stop after this Planner reconciliation and callback Orchestrator.
