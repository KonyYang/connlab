# TASK_353B Registered LTR Workbook Row Preview - Planner Evidence

Task ID: `TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW`
Lane: `registered-ltr-workbook-row-preview`
Role: Planner
Date: 2026-07-07
Status: planned - ready for Reviewer plan gate

## Discovery Gate Result

Definition of Ready is satisfied for a planned lane. Implementation is not authorized by this Planner pass. The next legal role is Reviewer plan gate.

## Current Phase / Active Task / Why Allowed

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active board state: `TASK_355B_PACKAGED_FEE_EXPORT_SUBPROCESS_ENTRY` complete/accepted; `TASK_353A_BASIC_INFORMATION_CONFIRMED_IDENTITY_AUTHORITY` complete/accepted.
- Current role: Planner.
- Why allowed: user requested a new TASK_353B lane and limited this heartbeat to Planner Discovery Gate / planning-first source-of-truth work.

## Confirmed By User

- Add or rename a read-only `LTR workbook preview` / `LTR row preview` action.
- Enable it whenever a project has a registered DL/LTR number.
- It queries the public-drive LTR workbook row and displays fields like the TASK_349A Intake specified-LTR authority preview.
- It does not require Basic Information Confirm.
- It does not write or commit.
- Keep the current Basic Information sync/update function but clarify copy, for example `Update LTR from Basic Information`.

## Confirmed By Repository Evidence

- TASK_349A already added read-only specified-LTR workbook row preview concepts and business field labels.
- Basic Information LTR sync already locates exact registered LTR rows but currently requires confirmed Basic Information for preview/commit.
- `ProjectBasicInformationSummaryCard` currently exposes only `LTR update preview`, tied to confirmed Basic Information and capable of proceeding to `Confirm update`.
- There is no existing registered-LTR-only read row preview in the side panel.
- API client helpers exist for the old sync and TASK_349A paths, but no project-scoped registered-row preview helper exists.

## Inferred By Planner

- A new project-scoped read-only service/API should be added instead of weakening the existing Basic Information sync service.
- Row field mapping can reuse/extract TASK_349A row-value labels.
- Exact DL row lookup can reuse/extract the Basic Information sync service's registered-LTR row resolution.
- No database schema change is required.
- The lane should remain planned until Reviewer reviews the contract and the user/Orchestrator authorizes Developer.

## Not Yet Confirmed

- Inline side panel versus modal/dialog visual treatment.
- Whether V1 also includes Excel read-only open-at-cell from the preview table.
- Whether lifecycle closed/stopped readonly states should affect the read-only preview. Planner default: keep read-only preview available because it is non-mutating.

These are bounded and do not block Reviewer plan gate.

## May Touch / Must Not Touch / Locked Paths

See:

- `tasks/TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW.md`
- `docs/task_353b_registered_ltr_workbook_row_preview_plan.md`

## Validation Gate

Focused backend tests must prove registered-LTR read without Basic Information Confirm, no-LTR/not-found blockers, and no write/commit path. Focused frontend tests must prove separate row preview/update actions, no Commit button in row preview, and existing Basic Information update gate preserved. Build/diff/trailing/forbidden-scope scans required.

## Merge Gate

Reviewer plan gate is next. Developer, Reviewer implementation, QA/browser smoke, and Integrator packaging gates are required before acceptance. Remote push is not authorized.

## External Residuals Excluded

Current worktree contains unrelated residuals in release/settings/template/desktop packaging paths, TASK_352 PDF import files, Word/Fee output files, and other backend/frontend tests. These are not TASK_353B inputs and must not be packaged with this lane unless separately approved.

## Stop Point

Planner lane creation complete. Recommended next role: Reviewer plan gate. This Planner thread must not write product code or route Developer implementation.

## Validation Checkpoint

Planner docs-only validation completed:

- `git diff --check -- docs/task_board.md tasks/TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW.md docs/task_353b_registered_ltr_workbook_row_preview_plan.md docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_planner.md` passed with only the existing LF/CRLF warning on `docs/task_board.md`.
- Trailing whitespace scan on the TASK_353B touched docs returned no matches.
- Targeted status confirmed this Planner pass added/updated TASK_353B source-of-truth docs/board/evidence only; visible backend/frontend/test changes are external residuals and remain excluded from TASK_353B.
