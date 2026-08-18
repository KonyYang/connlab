# TASK_357C Matrix Step Quantity Setup

Status: complete/accepted by Integrator
Lane: `matrix-step-quantity-setup`
Owner Role: Planner / Reviewer
Created: 2026-07-08

## Purpose

Plan the Matrix Step layer for one structured quantity parameter set per Step.

This lane follows:

- `TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT`
- `TASK_357B_BASIC_INFORMATION_QUANTITY_DEFAULTS`

Basic Information now provides project-level quantity defaults. TASK_357C plans how Matrix Step setup imports those defaults, lets the operator override them per Step, and makes the accepted Step quantity data the final authority for downstream consumers.

## User Goal

Matrix Step setup should be the final confirmation and override location for test point, reading, and contact-point quantities. Each Step may import Basic Information draft/confirmed defaults, but operator edits in Matrix Step setup become the authoritative values for later Fee Evaluation, Test Record, and Report reuse.

Fee Evaluation remains a passive consumer and is not implemented in this lane.

## Scope

TASK_357C is a planned lane only. It defines implementation boundaries for:

- per-Step quantity setup model and UI;
- Basic Information default import into Matrix Step setup;
- draft versus confirmed Basic Information default precedence;
- manual override semantics;
- persistence handoff from Matrix draft to confirmed Matrix authority;
- derived/display policy for `total_readings`;
- downstream handoff to TASK_357D and TASK_357E.

This Planner reconciliation does not implement product code. It records that implementation is now authorized after Reviewer readiness and user approval.

## V1 Fields

Contract fields inherited from TASK_357A:

- `test_points_per_sample`
- `readings_per_point`
- `contact_points_per_sample`
- `total_readings`

TASK_357B implemented only the first three fields as Basic Information defaults. For TASK_357C, `total_readings` should be a Matrix Step derived/display/downstream value, not a Basic Information persisted input.

## Authority Boundary

- Basic Information draft values may be imported as defaults.
- Confirmed Basic Information values are stronger defaults when available.
- Imported Basic Information values remain proposed defaults until accepted or overridden in Matrix Step setup.
- Matrix Step setup is the final authority after operator confirmation.
- Later Fee Evaluation must consume confirmed Matrix Step quantity values passively.
- Later Test Record/Report reuse requires separate lanes.

## May Touch

Planning/source-of-truth now:

- `tasks/TASK_357C_MATRIX_STEP_QUANTITY_SETUP.md`
- `docs/task_357c_matrix_step_quantity_setup_plan.md`
- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_planner.md`
- `docs/task_board.md`

Authorized implementation May Touch:

- `backend/domain/project_matrix_draft_models.py`
- `backend/domain/confirmed_matrix_authority_models.py`
- backend Matrix draft / confirmed Matrix persistence services and repositories as identified by Developer planning-first
- backend Matrix draft / confirmation / revision API DTOs and route handlers as needed
- `backend/application/project_basic_information_service.py` only for read-only default retrieval or small helper reuse; no Basic Information mutation behavior
- `frontend/src/features/matrix-editor/**`
- `frontend/src/api/client.ts` only for typed Matrix quantity DTO/client helpers
- focused backend Matrix draft/confirmation/revision tests
- focused frontend Matrix Editor tests
- TASK_357C developer/reviewer/QA evidence and board updates through normal lane flow

Schema authorization boundary:

- Narrowly scoped Matrix draft/confirmed authority schema tables for Step quantity setup are authorized for TASK_357C implementation.
- This does not authorize StepInstance, execution persistence, Fee Evaluation consumption, Test Record/Report reuse, Matrix parser/import changes, or Basic Information schema changes.

## Must Not Touch

- Fee Evaluation consumption/default-fill implementation.
- Test Record / Report reuse implementation.
- Basic Information quantity default implementation beyond read-only default source consumption.
- Matrix parser/import rules.
- LTR workbook/public-drive authority rules.
- StepInstance, execution persistence, image/evidence assets, Report generation, AI, permissions, LAN/server, multi-user.
- release/settings/template residual cleanup.
- unrelated dirty files.

## Locked Paths

- `backend/modules/fee_evaluation/**`
- `backend/application/confirmed_matrix_fee_draft_service.py`
- `frontend/src/features/fee-evaluation/**`
- Test Record / Report implementation paths
- Matrix parser/import implementation paths unless only type references are required
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

- Upstream: `TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT` accepted as contract/downstream basis.
- Upstream: `TASK_357B_BASIC_INFORMATION_QUANTITY_DEFAULTS` complete/accepted; Basic Information V1 exposes `test_points_per_sample`, `readings_per_point`, and `contact_points_per_sample`.
- Direct downstream: `TASK_357D_FEE_EVALUATION_MATRIX_QUANTITY_CONSUMPTION`.
- Later downstream: `TASK_357E_TEST_RECORD_REPORT_QUANTITY_REUSE`.

TASK_357D must not implement before TASK_357C provides a confirmed Matrix Step quantity read model.

## Validation Gate

Reviewer plan gate should verify:

- Matrix Step remains final quantity authority.
- Basic Information remains default source only.
- one parameter set per Step is explicit.
- `total_readings` is derived/display/downstream in TASK_357C, not a Basic Information persisted input.
- Fee Evaluation, Test Record, and Report remain locked for later lanes.
- validation covers default import, manual override, draft persistence, confirmation copy, revision/stale review behavior, build, diff/trailing scans, and forbidden-scope scans.

## Merge Gate

- Reviewer plan gate pass before Developer planning-first.
- User approval required before Developer planning-first.
- Developer planning-first must refine data shape, API, UI placement, and persistence strategy.
- Developer implementation is authorized only after this source-of-truth reconciliation records Reviewer readiness pass and user approval.

## Evidence

- Plan: `docs/task_357c_matrix_step_quantity_setup_plan.md`
- Planner evidence: `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_planner.md`
- Developer planning evidence: `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_developer.md`
- Reviewer evidence: `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_reviewer.md`
- Reconciliation evidence: `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_reconciliation_planner.md`

## Source-Of-Truth Reconciliation

Date: 2026-07-08

TASK_357C was implementation authorized after:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed docs-only.
- Reviewer implementation-readiness passed.
- User approved source-of-truth reconciliation and Developer implementation.

Implementation remains limited to Matrix Step quantity setup:

- one quantity parameter set per Matrix Step;
- import Basic Information draft/confirmed defaults;
- operator accept/override/clear semantics;
- Matrix Step as final quantity authority;
- `total_readings` derived/read-only display/downstream policy;
- narrowly scoped Matrix draft/confirmed Step quantity authority schema tables.

Still locked:

- Fee Evaluation consumption/default-fill;
- Test Record / Report reuse;
- StepInstance / execution persistence;
- Matrix parser/import rules;
- Basic Information mutation/schema changes beyond read-only default import/use;
- LTR/public-drive/real workbook/folder scope;
- release/settings/template residual cleanup;
- `.agents/**`, `docs/project_management/**`, and remote push.

Integrator packaging/readiness accepted TASK_357C after Developer implementation, Reviewer B1 fix re-gate pass, QA pass, package isolation, and validation. Remote push was not authorized and was not performed.
