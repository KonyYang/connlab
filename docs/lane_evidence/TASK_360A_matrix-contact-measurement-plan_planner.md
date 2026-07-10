# TASK_360A Matrix Contact Measurement Plan - Planner Evidence

## Completion Status

Implementation authorized. Pending Developer implementation pass.

## TASK_ID / Lane

- TASK_ID: `TASK_360A_MATRIX_CONTACT_MEASUREMENT_PLAN`
- Lane: `matrix-contact-measurement-plan`

## Source Routing

The user requested Planner Discovery Gate only for a Matrix Editor project-wide LLCR/CR Contact Measurement Plan, with downstream separation for a specialized LLCR/CR record workbook.

The user suggested `TASK_359A`, but `TASK_359A_MATRIX_RESEATING_DEFAULT_DETAILS_HOTFIX` already exists and is complete in the repository source-of-truth. Planner therefore assigned the next non-conflicting identifier: `TASK_360A_MATRIX_CONTACT_MEASUREMENT_PLAN`.

## Read Sources

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `PRODUCT.md`
- `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- TASK_357A-E and TASK_358A task/plan/evidence context
- Matrix Step quantity frontend/backend code
- Fee Evaluation default-fill quantity consumer code
- Confirmed Matrix Step quantity projection / Test Record quantity metadata code
- Test Record and workbook-generation related code search results

## Current Phase / Active Task / Role / Why Allowed

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active board task: `TASK_360A_MATRIX_CONTACT_MEASUREMENT_PLAN`.
- Role: Planner source-of-truth reconciliation.
- Why allowed: Reviewer plan gate passed, the user approved Developer planning-first, Developer planning-first completed as docs-only, Reviewer implementation-readiness passed, and the user explicitly approved reconciliation plus Developer implementation.

## Confirmed By User

- Contact Measurement Plan is Matrix-wide across all included groups.
- The UI belongs below the Matrix Editor main table near `Project Schedule`, but not inside `Project Schedule`.
- Generic quantity labels `Test points`, `Readings / point`, and `Contact points` should no longer be exposed for this business workflow.
- V1 Fee quantity is only `readings_per_sample`.
- `readings_per_sample` derives from structured contact breakdown.
- Fee is passive and uses per Group-Step units only: `readings_per_sample * group sample qty`.
- Contact breakdown is needed for a later dedicated LLCR/CR Excel record workbook.
- That specialized workbook is not the existing generic Test Record output.
- Common Matrix-wide plan must preserve explicit Group/Step overrides and must not silently overwrite confirmed/manual Step values.
- LLCR and CR may use different contact family selections.
- Confirmed Matrix Step contact snapshot is the authority after Matrix Confirm.
- `TASK_358A` is accepted; current generic Step quantity UI needs a migration/compatibility plan.

## Confirmed By Repository Evidence

- `docs/task_board.md` marks `TASK_357B`, `TASK_357C`, `TASK_357D`, `TASK_357E`, `TASK_358A`, and `TASK_359A` complete.
- Current Matrix Step quantity UI still renders generic `Test points`, `Readings`, and `Contact points` controls.
- Current selectors and backend service persist generic `test_points_per_sample`, `readings_per_point`, and `contact_points_per_sample`.
- Current Fee default-fill reads generic confirmed Step quantity facts and derives per-reading units.
- Current Test Record quantity projection exposes generic Step quantity metadata.
- Existing Test Record generation is a separate generic document output and should not be changed by this lane.

## Planner Inference

- `TASK_360A` should introduce a structured contact measurement authority model and keep the existing generic quantity model as compatibility/historical data.
- The lane may require non-destructive schema additions scoped to Matrix contact measurement draft state and confirmed snapshots.
- Fee changes should be limited to consuming derived `readings_per_sample` per Group-Step for LLCR/CR rows.
- The dedicated LLCR/CR workbook must be separated into `TASK_360B` or a later downstream lane.

## Not Yet Confirmed

- Exact legacy workbook template mapping for the downstream specialized LLCR/CR record workbook.
- Exact V1 custom contact entry metadata beyond label/count.
- Whether eligibility should be entirely deterministic or include operator include/exclude controls.

No item blocks planned `TASK_360A`; these should be rechecked by Reviewer or downstream planning.

## Planned Outputs

- Task file: `tasks/TASK_360A_MATRIX_CONTACT_MEASUREMENT_PLAN.md`
- Plan file: `docs/task_360a_matrix_contact_measurement_plan.md`
- Evidence: `docs/lane_evidence/TASK_360A_matrix-contact-measurement-plan_planner.md`
- Board update: `docs/task_board.md`

## Scope Decision

Create exactly one planned lane:

- `TASK_360A_MATRIX_CONTACT_MEASUREMENT_PLAN`

Do not create the downstream workbook lane yet. Record it as a serial future lane:

- `TASK_360B_LLCR_CR_SPECIALIZED_RECORD_WORKBOOK`

## DoR Assessment

Definition of Ready and implementation readiness are satisfied. The user has explicitly approved implementation after reconciliation; the lane is implementation authorized and pending Developer implementation.

## Validation Summary

Planner docs-only validation completed:

- `git diff --check -- docs/task_board.md tasks/TASK_360A_MATRIX_CONTACT_MEASUREMENT_PLAN.md docs/task_360a_matrix_contact_measurement_plan.md docs/lane_evidence/TASK_360A_matrix-contact-measurement-plan_planner.md` passed with the existing LF/CRLF warning for `docs/task_board.md` only.
- trailing whitespace scan on touched docs/task files returned no matches.
- targeted status showed this Planner pass touched only `docs/task_board.md` and new TASK_360A docs/task/evidence files. Existing external Fee Evaluation residuals in backend seed/rule/test files remain excluded and were not modified by this pass.

## Recommended Next Role

Developer implementation pass.

## Blocking Summary

None. Scope remains bounded to TASK_360A; downstream `TASK_360B_LLCR_CR_SPECIALIZED_RECORD_WORKBOOK` remains separate and unauthorized.
