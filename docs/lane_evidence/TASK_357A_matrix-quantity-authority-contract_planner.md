# TASK_357A Matrix Quantity Authority Contract Planner Evidence

Status: planned
Task: `TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT`
Lane: `matrix-quantity-authority-contract`
Date: 2026-07-08
Role: Planner

## Routing Summary

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active task: board reports `TASK_356A_LTR_READONLY_WORKBOOK_OPEN_EXISTING_EXCEL` complete and next work requires Orchestrator/User routing.
- Why allowed: User/Orchestrator answered the three Discovery blockers from `DISCOVERY_matrix-step-quantity-authority` and requested creation of a planned contract lane.
- Stop point: planned contract lane only. No Developer implementation is authorized.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/lane_evidence/DISCOVERY_matrix-step-quantity-authority_planner.md`
- `docs/task_357_matrix_step_quantity_authority_discovery_plan.md`
- Existing repository facts from Discovery covering Basic Information, Matrix Editor, Fee Evaluation default-fill, and Test Record/Fee dataset preview.

## User Confirmations Recorded

1. V1 field vocabulary may use structured quantity fields such as `test_points_per_sample`, `readings_per_point`, `contact_points_per_sample`, and `total_readings`.
2. V1 granularity is one parameter set per Matrix Step, not per group/condition/sample-size split.
3. Basic Information draft values may be used as import defaults for Matrix Step setup.

## Planned Contract Scope

TASK_357A defines the source-of-truth contract for:

- Basic Information draft/confirmed defaults;
- Matrix Step setup as final override authority;
- Fee Evaluation passive consumption;
- future Test Record/Report reuse boundaries;
- downstream serial lane split.

It does not authorize product code.

## May Touch

- `tasks/TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT.md`
- `docs/task_357a_matrix_quantity_authority_contract_plan.md`
- `docs/lane_evidence/TASK_357A_matrix-quantity-authority-contract_planner.md`
- `docs/lane_evidence/DISCOVERY_matrix-step-quantity-authority_planner.md`
- `docs/task_board.md`

## Must Not Touch / Locked Paths

- `backend/**`
- `frontend/**`
- `tests/**`
- `frontend/src/api/client.ts`
- Matrix parser/import implementation
- Fee Evaluation implementation
- Basic Information implementation
- LTR workbook/public-drive authority implementation
- Test Record / Report / StepInstance / AI / permissions / LAN/server / multi-user implementation
- real workbook/folder/document data
- release/settings/template residual cleanup
- `.agents/**`
- `docs/project_management/**`

## Dependency Plan

Serial implementation path:

1. `TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT`
2. `TASK_357B_BASIC_INFORMATION_TEST_QUANTITY_DEFAULTS`
3. `TASK_357C_MATRIX_STEP_QUANTITY_SETUP_MODEL_UI`
4. `TASK_357D_FEE_EVALUATION_MATRIX_QUANTITY_CONSUMPTION`

Later:

- `TASK_357E_TEST_RECORD_REPORT_QUANTITY_REUSE_CONTRACT`

## Definition Of Ready

- Ready for Reviewer plan gate: yes.
- Ready for implementation: no, by design.
- Recommended next role: Reviewer plan gate.

## Validation Summary

Pending validation after this write:

- `git diff --check` on TASK_357A docs/board/evidence.
- trailing whitespace scan on touched docs.
- targeted `git status --short` proving no product code changed by this Planner pass.
