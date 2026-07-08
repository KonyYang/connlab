# TASK_357D Fee Passive Consumes Matrix Step Quantities

Status: complete/accepted by Integrator
Lane: `fee-passive-consumes-matrix-step-quantities`
Owner Role: Developer / Reviewer / QA / Integrator
Created: 2026-07-08

## Purpose

Plan Fee Evaluation passive consumption of confirmed Matrix Step quantity authority.

This lane follows:

- `TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT`
- `TASK_357B_BASIC_INFORMATION_QUANTITY_DEFAULTS`
- `TASK_357C_MATRIX_STEP_QUANTITY_SETUP`

TASK_357C made Matrix Step setup the final confirmation/override location for Step quantity parameters. TASK_357D plans how Fee Evaluation uses those confirmed quantities for units/default-fill without becoming a test quantity entry surface.

## User Goal

Fee Evaluation should passively consume confirmed Matrix Step quantities for fee units/default-fill. Matrix Step quantity authority is the source. Basic Information remains a default source only and must not be treated by Fee as final authority.

## Scope

TASK_357D is now implementation authorized after Planner/Reviewer/Developer planning gates and user approval. It defines implementation boundaries for:

- reading confirmed Matrix Step quantities from the active Confirmed Matrix snapshot;
- mapping Step quantities into Fee default-fill context;
- preferring Matrix Step quantity values over TASK_351 text parsing where applicable;
- keeping Fee Evaluation as an editable fee review surface, not a point/reading/contact quantity setup surface;
- preserving review-required behavior when quantities are missing, ambiguous, or not mapped;
- downstream handoff to TASK_357E for Test Record/Report reuse.

This Planner reconciliation pass does not implement product code.

## Fee Passive-Consumer Contract

- Fee Evaluation may consume confirmed Matrix Step quantity fields:
  - `test_points_per_sample`
  - `readings_per_point`
  - `contact_points_per_sample`
  - derived/read-only `total_readings`
- Fee Evaluation must not edit, create, or persist Matrix Step quantity authority.
- Fee Evaluation must not fetch Basic Information defaults directly as final quantity authority.
- Missing or review-required Matrix Step quantities should produce Fee review-required output, not invented units.
- TASK_351 text parsing remains a compatibility fallback only where Matrix Step quantity authority is absent or unmapped and Reviewer approves fallback behavior.

## May Touch

Planning/source-of-truth now:

- `tasks/TASK_357D_FEE_PASSIVE_CONSUMES_MATRIX_STEP_QUANTITIES.md`
- `docs/task_357d_fee_passive_consumes_matrix_step_quantities_plan.md`
- `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_planner.md`
- `docs/task_board.md`

Authorized implementation May Touch:

- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/application/confirmed_matrix_fee_draft_models.py`
- `backend/modules/fee_evaluation/fee_default_fill.py`
- `backend/modules/fee_evaluation/fee_default_fill_models.py`
- `backend/modules/fee_evaluation/fee_default_fill_common.py` only if source metadata helpers are needed
- `backend/api/routes_confirmed_matrix_fee_draft.py` only if response DTOs expose quantity source/review metadata
- `frontend/src/api/client.ts` only for typed Fee draft metadata changes
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
- `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx` only if preview model wiring requires it
- focused Fee Evaluation backend/frontend tests
- TASK_357D developer/reviewer/QA evidence and board updates through normal lane flow

## Must Not Touch

- Matrix Step setup authoring UI or authority mutation.
- Matrix Step quantity storage schema/migration, except read-model use of already accepted TASK_357C fields.
- Basic Information quantity defaults or Basic Information schema/mutation behavior.
- Test Record / Report reuse implementation.
- StepInstance / execution persistence.
- Matrix parser/import rules.
- LTR workbook/public-drive authority rules.
- real workbook files, real folders, or public-drive data.
- release/settings/template residual cleanup.
- unrelated dirty files.

## Locked Paths

- `frontend/src/features/matrix-editor/**`
- `backend/application/matrix_step_quantity_service.py`
- Matrix Step quantity storage models/repositories except read-only type imports if unavoidable
- `backend/application/project_basic_information_service.py`
- `frontend/src/features/project-basic-information/**`
- Test Record / Report implementation paths
- Matrix parser/import implementation paths
- real workbook files
- real public-drive folders
- real local project folders
- `D:\Test Project/**`
- `D:\PublicProject/**`
- `.agents/**`
- `docs/project_management/**`
- `dist_release/**`
- `packaging/**`
- release scripts/tests/docs
- `temp_agents_stash.md`

## Dependencies

- Upstream: `TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT` accepted.
- Upstream: `TASK_357B_BASIC_INFORMATION_QUANTITY_DEFAULTS` accepted.
- Upstream: `TASK_357C_MATRIX_STEP_QUANTITY_SETUP` complete/accepted; confirmed Matrix snapshots now carry Step quantity records.
- Downstream: `TASK_357E_TEST_RECORD_REPORT_QUANTITY_REUSE` remains future scope.

TASK_357D implementation is authorized after source-of-truth reconciliation. Developer must still remain inside this lane's authorized May Touch / Must Not Touch / Locked Paths.

## Validation Gate

Reviewer plan gate should verify:

- Fee remains passive and does not become the point/reading/contact quantity input surface.
- confirmed Matrix Step quantities are preferred over Basic Information defaults and TASK_351 text parsing for mapped rules.
- missing/review-required Step quantities surface Fee review-required output.
- existing TASK_351 deterministic rules remain compatible.
- no Test Record/Report, StepInstance, Matrix parser/import, Basic Information mutation, or LTR/public-drive scope is introduced.

## Merge Gate

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed as docs-only planning.
- Reviewer implementation-readiness passed.
- User approved source-of-truth reconciliation and Developer implementation.
- Developer implementation pass completed.
- Reviewer implementation re-gate passed after B1 line-count/headroom fix.
- QA gate passed.
- Integrator packaging/readiness accepted the controlled TASK_357D package.

## Evidence

- Plan: `docs/task_357d_fee_passive_consumes_matrix_step_quantities_plan.md`
- Planner evidence: `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_planner.md`
- Developer planning-first evidence: `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_developer.md`
- Reviewer gate evidence: `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_reviewer.md`
- Planner reconciliation evidence: `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_reconciliation_planner.md`
- QA evidence: `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_qa.md`

## Planner Source-Of-Truth Reconciliation

Date: 2026-07-08

Reconciled facts:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed without product code changes.
- Reviewer implementation-readiness passed.
- User approved source-of-truth reconciliation and Developer implementation.
- TASK_357D is complete/accepted after Developer implementation, Reviewer B1 fix re-gate pass, QA pass, and Integrator packaging/readiness.

Authorized implementation scope:

- Fee Evaluation passively consumes active `ConfirmedMatrixSnapshot.step_quantities` for units/default-fill.
- Lookup may match by `confirmed_group_id`, `confirmed_row_id`, `step_sequence`, and normalized suffix.
- Fee default-fill context may be extended with structured Step quantity facts.
- V1 maps LLCR and CR specified-current per-reading rules unless a later gate explicitly expands scope.
- `readings_per_sample` derives from `test_points_per_sample * readings_per_point` when deterministic.
- `contact_points_per_sample` remains review metadata, not silent total-reading replacement.
- Multiple-Step aggregation must remain conservative.
- TASK_351 text fallback remains only when structured Step quantity authority is absent or unmapped.
- Fee remains a passive editable fee review surface with no point/reading/contact authoring UI.

Locks preserved:

- no Fee-side Step quantity editing;
- no Matrix Step setup/storage mutation;
- no Basic Information mutation or final authority consumption;
- no Test Record / Report / StepInstance scope;
- no Matrix parser/import changes;
- no LTR/public-drive/real workbook/folder changes;
- no release/settings/template residual cleanup;
- no `.agents/**` or `docs/project_management/**`;
- no remote push.

## Integrator Acceptance

Date: 2026-07-08

TASK_357D was accepted by Integrator after package isolation and merge-gate validation. The accepted package is limited to Fee Evaluation passive consumption of confirmed Matrix Step quantities, focused backend/default-fill tests, TASK_357D evidence/docs, and board closeout. Remote push was intentionally not performed.
