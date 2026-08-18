# TASK_357A Matrix Quantity Authority Contract

Status: complete/accepted contract - downstream lane basis, implementation not authorized
Lane: `matrix-quantity-authority-contract`
Owner Role: Planner / Reviewer
Created: 2026-07-08

## Purpose

Define the product and data authority contract for structured test point, reading, and contact-point quantities before any implementation lane starts.

This contract must align:

```text
Basic Information draft/confirmed defaults
  -> Matrix Step setup final override
  -> Fee Evaluation passive consumption
  -> future Test Record / Report reuse
```

## Why This Lane Exists

Current ConnLab behavior stores group-level `sample_quantity_expression` in Matrix authority and lets Fee Evaluation derive some units from Matrix row text. That is not enough for user-confirmed point/reading/contact quantities because Fee Evaluation must not become the data entry authority.

The first downstream task must therefore define the source hierarchy, field vocabulary, granularity, fallback policy, and validation boundaries.

## User-Confirmed Contract Inputs

- Fee Evaluation is a passive consumer, not the point/reading/contact input surface.
- Basic Information may hold project-level default quantity values.
- Basic Information draft values may be imported into Matrix Step setup as defaults.
- Matrix Step setup is the final confirmation and override point.
- V1 uses one parameter set per Matrix Step.
- V1 may use fields such as:
  - `test_points_per_sample`
  - `readings_per_point`
  - `contact_points_per_sample`
  - `total_readings`
- V1 does not initially split quantity parameters by group, condition, or sample size.
- Confirmed Matrix Step structured quantities should later serve Fee Evaluation, Test Record, Report, and other derived outputs.

## Contract Scope

This lane is documentation and source-of-truth only.

It must define:

- field names and meanings;
- Basic Information default-source policy for draft and confirmed values;
- Matrix Step setup final authority behavior;
- Fee Evaluation passive-consumer boundary;
- Test Record / Report future reuse boundary;
- downstream lane split and dependencies;
- May Touch / Must Not Touch / Locked Paths drafts for downstream lanes;
- validation and merge gates for the series.

## Non-Goals

- No product code.
- No backend schema/model/API implementation.
- No frontend UI implementation.
- No Fee Evaluation calculation changes.
- No Matrix Step setup UI.
- No StepInstance, Test Record generation, Report generation, AI, permissions, LAN/server, or multi-user scope.
- No LTR workbook/public-drive authority changes.
- No real workbook/folder/document mutation.

## May Touch

- `tasks/TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT.md`
- `docs/task_357a_matrix_quantity_authority_contract_plan.md`
- `docs/lane_evidence/TASK_357A_matrix-quantity-authority-contract_planner.md`
- `docs/lane_evidence/DISCOVERY_matrix-step-quantity-authority_planner.md`
- `docs/task_board.md`

## Must Not Touch

- `backend/**`
- `frontend/**`
- `tests/**`
- `frontend/src/api/client.ts`
- Matrix parser/import implementation
- Fee Evaluation implementation
- Basic Information implementation
- LTR workbook/public-drive authority implementation
- StepInstance / Test Record / Report / AI / permissions / LAN/server / multi-user implementation
- release/settings/template residual cleanup

## Locked Paths

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

## Downstream Dependency Plan

Serial implementation path:

1. `TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT`
2. `TASK_357B_BASIC_INFORMATION_TEST_QUANTITY_DEFAULTS`
3. `TASK_357C_MATRIX_STEP_QUANTITY_SETUP_MODEL_UI`
4. `TASK_357D_FEE_EVALUATION_MATRIX_QUANTITY_CONSUMPTION`

Later contract/planning:

- `TASK_357E_TEST_RECORD_REPORT_QUANTITY_REUSE_CONTRACT`

Parallelization:

- TASK_357B and TASK_357C may be planned in parallel only after TASK_357A contract is accepted.
- TASK_357D must not implement before TASK_357C confirms structured Matrix Step quantities.
- TASK_357E may plan after TASK_357A but must not expose Report/Test Record future scope as current product UI.

## Evidence

- Discovery evidence: `docs/lane_evidence/DISCOVERY_matrix-step-quantity-authority_planner.md`
- Plan: `docs/task_357a_matrix_quantity_authority_contract_plan.md`
- Planner evidence: `docs/lane_evidence/TASK_357A_matrix-quantity-authority-contract_planner.md`
- Developer planning evidence: `docs/lane_evidence/TASK_357A_matrix-quantity-authority-contract_developer.md`
- Reviewer evidence: `docs/lane_evidence/TASK_357A_matrix-quantity-authority-contract_reviewer.md`
- Reconciliation evidence: `docs/lane_evidence/TASK_357A_matrix-quantity-authority-contract_reconciliation_planner.md`

## Validation Gate

- Reviewer confirms the contract captures user-confirmed field vocabulary, V1 Step granularity, draft Basic Information default policy, Matrix final authority, Fee passive boundary, and downstream dependency split.
- `git diff --check` on TASK_357A docs/board/evidence.
- trailing whitespace scan on touched docs.
- targeted status confirms no product code changed.

## Merge Gate

- Reviewer plan gate pass.
- No Developer implementation from this lane.
- User/Orchestrator must create or approve downstream planned lanes separately.

## Source-Of-Truth Reconciliation

Date: 2026-07-08

TASK_357A is accepted as a contract/source-of-truth basis after:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed docs-only.
- Reviewer implementation-readiness passed.
- User/Orchestrator approved reconciliation and downstream lane creation.

This reconciliation does not authorize product implementation for TASK_357A. The next legal product sequence begins with separate downstream planned lanes, starting with `TASK_357B_BASIC_INFORMATION_QUANTITY_DEFAULTS`.
