# TASK_305 Fee Evaluation Preview / Export Parity Hardening - Executable Plan

## Summary

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_305_FEE_EVALUATION_PREVIEW_EXPORT_PARITY_HARDENING`, complete.

TASK_305 was approved for implementation and completed on 2026-06-09. This plan is retained as the executable record for the completed task.

TASK_305 is a hardening pass for the existing Fee Evaluation preview/export workflow. The goal is not to add new pricing intelligence. The goal is to make the visible webpage preview, saved local pricing draft, direct-download payload, and generated Excel Fee Form agree on the rows and editable fields that already exist in the current operator workflow.

## Step 1 - Task Understanding

Goal:

- Align Fee Evaluation web preview and Fee Form export behavior for existing V1 rows, fields, formulas, and comments.

Inputs:

- Active Confirmed Matrix authority.
- TASK_286 Fee Evaluation draft.
- TASK_299 local editable preview state.
- TASK_300 direct-download edited export payload.
- TASK_301 saved pricing draft payload.
- Formal optimized Fee Form template used by existing export configuration.

Outputs:

- Hardened frontend preview model/table behavior.
- Hardened edited export payload behavior if current contracts already support it.
- Hardened workbook gateway behavior.
- Unit/integration tests for preview/export parity.
- Manual/browser smoke checklist and task-board completion notes.

Modules involved:

- `frontend/src/features/fee-evaluation/`
- `backend/infrastructure/office/fee_evaluation_workbook_gateway.py`
- `backend/application/confirmed_matrix_fee_evaluation_export_service.py`
- `backend/application/fee_evaluation_pricing_draft_persistence_service.py`
- existing Fee Evaluation API tests and frontend static checks

Not allowed:

- No new fee-rule policy.
- No rule-maintenance UI.
- No production workbook parsing workflow.
- No new database migration.
- No broad page redesign.
- No StepInstance/execution/report scope.
- No new workbook writer dependency.

## Step 2 - Design

### Current Architecture Boundary

There are four related but separate representations:

1. Backend Fee Draft:
   - Derived from active Confirmed Matrix and active fee rule version.
   - Does not include all manual/static Excel rows as first-class pricing rows.

2. Frontend Preview Rows:
   - Built by `feeEvaluationPreviewModel.ts`.
   - Expands Matrix lines into step rows.
   - Contains local-only editable cells.

3. Edited Export Payload:
   - Built in `FeeEvaluationReviewExportPage.tsx`.
   - Sends stable backend identity fields for Matrix step rows.
   - Sends manual trailing `Report preparation` through `manual_rows`.
   - Sends summary/manual fields for condition confirmation and external cost.

4. Excel Workbook Rows:
   - Written by `FeeEvaluationWorkbookGateway`.
   - Uses the formal optimized template anchors and formulas.
   - Inserts some rows that do not naturally exist in the Fee Draft.

TASK_305 must make the mapping between these representations explicit and tested.

### File-Level Design

#### Frontend Preview Model

File:

- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`

Checks/changes:

- Ensure `buildFeeEvaluationPreviewRows(...)` inserts per-group Sample preparation rows with stable preview identity.
- Ensure group filtering includes Sample preparation rows in the selected group preview.
- Implement the TASK_305 V1 contract decision: Sample preparation is editable, saveable, reloadable, and exportable.
- Ensure scope totals and working-hours calculations include Sample preparation rows because they are editable pricing rows.
- Ensure `hydrateFeeEvaluationPreviewEditsFromSavedDraft(...)` applies Sample preparation edits only through an explicit stable Sample preparation identity.

#### Frontend Preview Table

File:

- `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`

Checks/changes:

- Ensure Sample preparation renders like a normal operator-visible pricing row:
  - Group
  - Step
  - Man-hour
  - Description
  - Unit Price
  - Unit Type
  - Units
  - Base Fee
  - Discount
  - Testing Fee
  - Notes
- Avoid adding new visual controls unless parity requires them.
- Keep copy concise and operator-facing.

#### Frontend Export Payload

File:

- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`

Checks/changes:

- Update `buildEditedExportPayload(...)` so the exported row kinds are explicit:
  - Matrix step rows
  - Sample preparation rows
  - Report preparation manual row
  - summary fields
- Sample preparation must not be sent as an ordinary Matrix step row. It needs a stable dedicated identity keyed by the active Confirmed Matrix group.
- Add a test that proves Sample preparation edits appear in the direct-download payload with that dedicated identity.

#### Pricing Draft Persistence

Files:

- `backend/application/fee_evaluation_pricing_draft_persistence_service.py`
- `tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py`
- `tests/integration/test_fee_evaluation_pricing_draft_api.py`

Checks/changes:

- Extend the existing TASK_301 pricing draft payload/repository shape only as narrowly as needed to persist Sample preparation edits.
- Prefer an additional manual-row kind or equivalent typed field over a broad schema redesign.
- The stable persisted identity must include enough group context to avoid collisions and stale application:
  - project id through the draft header
  - confirmed matrix id
  - confirmed revision
  - fee rule version id
  - confirmed group id or stable group key/label fallback
- Saved Sample preparation edits must be rehydrated after reload only when the saved draft is current.
- Stale or unmatched Sample preparation rows must not be applied.
- Do not add a database migration unless explicitly necessary and approved by this task.

#### Workbook Gateway

File:

- `backend/infrastructure/office/fee_evaluation_workbook_gateway.py`

Checks/changes:

- Ensure inserted Sample preparation rows have explicit default values:
  - B = `0`
  - D = `0`
  - E = `per sample`
  - F = `1`
  - G = `0`
  - H = `0`
  - I = formula where supported
- Ensure Matrix and Report preparation row Notes become comments on the I-column Testing Fee cell only when non-empty.
- Ensure External Cost amount writes to column D on the External Cost row.
- Ensure External Cost note writes as a comment on that same D-column cell only when non-empty.
- Ensure External Cost export does not overwrite the I-column formula/value managed by the template.
- Preserve existing no-overwrite and timeout-protected export flow.

#### Export Service/API

Files:

- `backend/application/confirmed_matrix_fee_evaluation_export_service.py`
- `backend/api/routes_confirmed_matrix_fee_evaluation_export.py`
- `tests/integration/test_confirmed_matrix_fee_file_download_api.py`

Checks/changes:

- No new endpoint expected.
- Keep direct-download body optional/no-body compatible.
- Confirm edited payload warnings from gateway are propagated.
- Do not change timeout subprocess behavior.

## Data Contracts

### Row Notes

Source:

- Preview row `notes` field.

Export:

- Non-empty note becomes a comment on the row's Testing Fee cell.
- Empty note clears or leaves no comment.

Failure behavior:

- If Excel comment creation fails for a non-empty note, gateway must return an actionable warning.

### External Cost Note

Source:

- `summary.external_cost_note`.

Export:

- Non-empty note becomes a comment on the External Cost amount cell in column D.
- Empty note creates no comment.
- Column I is not written by External Cost note/amount logic.

Failure behavior:

- If Excel comment creation fails for a non-empty External Cost note, gateway must return an actionable warning.

### Sample Preparation

Preview:

- One row per group, before ordinary step rows, with `Step=0`.
- Editable fields are the same as ordinary pricing rows:
  - Man-hour
  - Unit Price
  - Unit Type
  - Units
  - Base Fee
  - Discount
  - Notes

Export:

- One row per group, before ordinary group detail rows.
- Must keep default editable-column values aligned with preview defaults.
- Edited values must be written to B/D/E/F/G/H.
- Non-empty Notes must be written as a comment on I.
- I must remain formula-backed where supported.

Persistence and payload:

- V1 decision is fixed: Sample preparation edits are part of TASK_305.
- Use a dedicated Sample preparation row identity, not a Matrix step identity.
- Recommended shape:
  - `row_kind = "sample_preparation"`
  - `confirmed_group_id`
  - `group_key`
  - `group_label`
  - editable values matching `FeeEvaluationEditedManualRow`
- The route/service validators must reject malformed Sample preparation rows and must not accept unknown row kinds silently.

## Task Breakdown

### Task 1 - Baseline Audit

- Inspect current preview rows for the provided project.
- Inspect current generated workbook behavior using existing fake COM tests.
- Identify any parity mismatches before editing.
- Confirm existing payload/repository structures and choose the smallest typed extension for Sample preparation rows.
- Confirm no database migration is required; if a migration is required, stop and revise the task/plan before implementing.

### Task 2 - Frontend Preview Parity Tests

Add/adjust tests in:

- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx` if payload behavior changes

Coverage:

- Sample preparation appears once per group.
- It precedes group step rows.
- `Step=0`.
- Selected-group filtering includes that row.
- Totals behavior is explicitly locked.
- Sample preparation local edits affect Testing Fee, working hours, selected-group totals, and Grand Cost.
- Direct-download payload includes Sample preparation edited values through the dedicated identity.
- Saving a draft and hydrating it back applies Sample preparation edits when current.
- Stale saved Sample preparation edits are ignored.

### Task 3 - Workbook Gateway Parity Tests

Add/adjust tests in:

- `tests/unit/test_fee_evaluation_workbook_gateway.py`

Coverage:

- Sample preparation B/D/E/F/G/H defaults are populated.
- Sample preparation I formula is present.
- Edited Sample preparation B/D/E/F/G/H values are written when provided.
- Edited Sample preparation Notes become I-cell comments when non-empty.
- Row Notes comments are written only when non-empty.
- External Cost amount writes to D.
- External Cost note comment writes to D.
- External Cost does not write I.
- Comment creation failure produces warning for non-empty notes.

### Task 4 - Implementation

Only after tests define the intended behavior:

- Apply minimal frontend preview/payload changes.
- Apply minimal workbook gateway changes.
- Avoid unrelated UI layout changes.
- Avoid new pricing rule changes.

### Task 5 - Regression Verification

Run:

- `cd frontend; npm test -- --run FeeEvaluation --watch=false`
- `cd frontend; npm run build`
- `py -m pytest tests/unit/test_fee_evaluation_workbook_gateway.py -q`
- `py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/integration/test_confirmed_matrix_fee_file_download_api.py -q`
- `py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q`
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or project_workbench"`
- If real-template Excel smoke is run, use the existing timeout-protected production export path or TASK_290A subprocess harness. Do not run naked Excel COM from the main test process.
- `git diff --check`

### Task 6 - Manual Smoke

Use the provided project route:

- `http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f/fee-evaluation`

Smoke checklist:

- Preview shows Sample preparation for every group.
- Group selector still filters rows and totals.
- Edit one Sample preparation row, save changes, reload the page, and confirm the edit rehydrates.
- Generate Fee Form and confirm the edited Sample preparation row is exported.
- Edits to a representative row update Testing Fee.
- Notes can be entered.
- External Cost note can be entered.
- Fee Form export succeeds.
- Generated workbook shows matching rows/defaults/comments/formulas.

If the Browser plugin or Excel COM is unavailable, record that limitation and rely on automated tests plus manual verification instructions.

## Risks And Mitigations

Risk: Sample preparation needs a new row identity and could be incorrectly matched to Matrix rows.

Mitigation:

- Use a dedicated `sample_preparation` identity.
- Reject malformed sample preparation payload rows.
- Lock save/load/export behavior with frontend, service, API, and gateway tests.

Risk: Excel comments can fail silently in real COM.

Mitigation:

- Gateway must return warnings for non-empty note/comment failures.
- Tests should cover fake comment failure.

Risk: External Cost formula cells are accidentally overwritten.

Mitigation:

- Tests assert D-column write and I-column preservation.

Risk: Preview/export parity tests become too brittle around formatting.

Mitigation:

- Assert semantic cells/rows/formulas/comments, not cosmetic details unless the task explicitly requires formatting.

## Acceptance Checklist

- [ ] TASK_305 implementation changes only approved parity surfaces.
- [ ] Web preview row list and workbook row list agree for V1 rows.
- [ ] Sample preparation defaults are explicit in preview and export.
- [ ] Sample preparation edits save, reload, and export through a dedicated identity.
- [ ] Direct-download payload behavior is covered for Matrix rows, Sample preparation, Report preparation, and summary fields.
- [ ] Row Notes comments and External Cost note comments are tested.
- [ ] Optional direct-download no-body behavior remains compatible.
- [ ] Existing TASK_299/TASK_300/TASK_301/TASK_302 regression tests pass.
- [ ] Task board is updated after completion.
- [ ] Stop after TASK_305; do not start the next task.

## Stop Point

Stop after TASK_305 implementation and validation. Do not begin TASK_306 or any new pricing-rule, UI-maintenance, StepInstance, execution, report, or server task.
