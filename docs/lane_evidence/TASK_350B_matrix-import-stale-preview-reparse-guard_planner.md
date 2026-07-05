# TASK_350B Matrix Import Stale Preview Reparse Guard - Planner Evidence

Task: `TASK_350B_MATRIX_IMPORT_STALE_PREVIEW_REPARSE_GUARD`
Lane: `matrix-import-stale-preview-reparse-guard`
Role: Planner
Status: planned - requirement update applied; ready for Reviewer plan re-gate; implementation not authorized
Date: 2026-07-04

## Gate

Planner Discovery Gate / formal planned lane creation, plus requirement-update plan fix after user changed stale Replace behavior before Developer planning-first approval.

## Sources Read

- `AGENTS.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/impeccable/SKILL.md`
- `$impeccable` product context (`PRODUCT.md`, `DESIGN.md`)
- `docs/task_board.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/frontend_architecture_rules.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_reconciliation_planner.md`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- Current `git status --short`

## Current Facts / Root Cause

- TASK_350A is complete/accepted and Matrix import now accepts `.doc,.docx`.
- MatrixEditorWorkspace currently has locator state (`locatorPage`, `locatorTableOnPage`, `locatorKeyword`) and preview state (`importPreview`, `importingPreview`, `committingImport`).
- Reparse already sends current locator inputs to `previewProjectTestPlanMatrixFromUpload` and validates positive integer Page / Table on page fields.
- Replace currently remains enabled when `importPreview` exists and groups are present, even if locator inputs have changed since that preview was generated.
- There is no `lastParsedLocator` snapshot or stale-preview derived state.
- Replace calls `commitMatrixImport` with the current `importPreview`, so stale preview commit is possible if the UI does not block it.

## Planner Decision

Create formal planned lane:

- Task: `TASK_350B_MATRIX_IMPORT_STALE_PREVIEW_REPARSE_GUARD`
- Lane: `matrix-import-stale-preview-reparse-guard`
- Status: `planned`
- Next role: Reviewer plan re-gate

This is a formal lightweight frontend follow-up, not a quick fix, because it protects Matrix import authority correctness.

## Requirement Update

After the first Reviewer plan gate had passed but before Developer planning-first approval, the user changed the required stale-preview behavior:

- Current locator edits still mark the preview stale by comparing the current Page / Table on page / Keyword against `lastParsedLocator`.
- `Replace` must not be disabled only because the preview is stale.
- Clicking `Replace` while stale must first run Reparse with the current locator fields.
- Auto-Reparse success with usable Matrix groups updates `importPreview` and `lastParsedLocator`, then continues the original Replace/commit.
- Auto-Reparse failure, not-found/no usable Matrix groups, invalid Page/Table, or page-table mismatch must keep the modal open, show the in-dialog result/error, and skip commit.
- Manual Reparse remains as an explicit refresh path.
- Non-stale Replace commits the current preview directly and does not reparse.

The old planned behavior "stale preview disables Replace and Reparse is the only refresh entry" is superseded.

## May Touch

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- TASK_350B task/plan/evidence/board docs.

## Must Not Touch / Locked

- `backend/**`
- `frontend/src/api/client.ts`
- Matrix parser rules / backend preview service / backend preview route.
- Confirmed Matrix, Fee, Test Record, lifecycle semantics.
- TASK_350A `.doc` conversion backend flow.
- Folder Actions / public folder workflow.
- Intake / LTR workflow.
- Projects registry/list.
- Release/settings cleanup and unrelated residuals.
- `.agents/**`
- `docs/project_management/**`

## Acceptance Summary

- Record locator snapshot after initial preview success and Reparse success.
- Detect stale preview when current locator fields differ from the snapshot.
- Keep Replace available for a stale preview when an existing preview with groups exists and no readonly/busy blocker applies.
- Stale Replace auto-Reparses using the current locator fields before any commit.
- Auto-Reparse success with usable Matrix groups refreshes `importPreview`, updates `lastParsedLocator`, and then commits the refreshed preview.
- Auto-Reparse failure, not-found/no usable Matrix groups, invalid Page/Table, or page-table mismatch keeps the modal open, shows in-dialog error/result, and does not commit.
- Manual Reparse success refreshes preview and snapshot.
- Manual Reparse failure keeps modal open and shows in-dialog error/message.
- Non-stale Replace commits directly without calling preview/reparse.
- Disable locator inputs, Reparse, Replace, and Append while manual Reparse, auto-Reparse, or commit is running.

## External Residuals Excluded

Current `git status --short` shows release/settings/desktop residuals and related untracked files. No product code is changed by this Planner pass. Future TASK_350B implementation must keep those residuals excluded.

## Files Created / Updated

- `tasks/TASK_350B_MATRIX_IMPORT_STALE_PREVIEW_REPARSE_GUARD.md`
- `docs/task_350b_matrix_import_stale_preview_reparse_guard_plan.md`
- `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_planner.md`
- `docs/task_board.md`

## Validation

- `git diff --check -- docs/task_board.md tasks/TASK_350B_MATRIX_IMPORT_STALE_PREVIEW_REPARSE_GUARD.md docs/task_350b_matrix_import_stale_preview_reparse_guard_plan.md docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_planner.md`: passed with Git LF/CRLF warning for `docs/task_board.md` only.
- Trailing whitespace scan on touched TASK_350B docs/board/evidence: no matches.
- Targeted status shows modified `docs/task_board.md` plus TASK_350B task/plan/planner evidence files.
- Targeted status also shows external backend/settings/desktop residuals; this Planner pass did not edit product code and does not approve or package those residuals.

## Next Role

Reviewer plan re-gate.

## Stop Point

Stop after planned lane creation and callback. Do not route Developer and do not write product code.
