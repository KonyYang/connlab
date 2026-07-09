# DISCOVERY matrix-step-quantity-authority Planner Evidence

Status: discovery_checkpoint
Date: 2026-07-08
Role: Planner
Discovery scope: Matrix Step quantity authority chain from Basic Information defaults to Matrix Step setup and downstream Fee/Test Record/Report consumption.

## Routing Summary

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active task: board reports `TASK_356A_LTR_READONLY_WORKBOOK_OPEN_EXISTING_EXCEL` complete and next work requires Orchestrator/User routing.
- Why allowed: User/Orchestrator requested a Planner Discovery Gate for a new series. This checkpoint does not approve implementation, write product code, or route Developer.
- Evidence/plan draft: `docs/task_357_matrix_step_quantity_authority_discovery_plan.md`.

## Required Facts Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `$impeccable` product context from `PRODUCT.md` / `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `docs/task_351_fee_evaluation_auto_default_fill_plan.md`
- `docs/task_353a_basic_information_confirmed_identity_authority_plan.md`
- `backend/modules/fee_evaluation/fee_default_fill.py`
- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/application/project_basic_information_service.py`
- `backend/domain/project_matrix_draft_models.py`
- `backend/domain/confirmed_matrix_authority_models.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
- `backend/application/test_record_fee_dataset_preview_service.py`
- `docs/task_board.md` current accepted TASK_351/TASK_353A/TASK_356A context
- `git status --short`

## Confirmed By User

- Fee Evaluation is a passive consumer, not the point/reading entry or reminder authority.
- Basic Information may provide project-level default test point/reading/contact values.
- Matrix Step setup is the final confirmation and override surface.
- Step values may import defaults and then be manually changed for specific tests, such as Power steps using fewer points.
- Confirmed structured Matrix Step quantity data should serve Fee Evaluation, Test Record, Report, and later derived outputs.

## Confirmed By Repository Evidence

- ConnLab product rules make Matrix the execution authority map and Fee/Test Record/Report derived outputs.
- Current Basic Information service has no project-level quantity default fields.
- Current Matrix draft/confirmed models persist group sample quantity, rows, and cells but no structured per-step readings/contact quantity setup.
- Current Fee default-fill computes reading units by parsing explicit readings/specimen text plus group sample quantity; when those facts are missing it returns review-required.
- Current Fee draft builder consumes confirmed Matrix authority and group `sample_quantity_expression`; it does not consume structured step quantities.
- Existing Test Record/Fee dataset preview still emits conservative quantity-basis text rather than structured quantity authority.
- Existing frontend architecture rules require feature hooks/selectors/API boundaries and avoid business authority in display components.

## Planner Inferences

- The request is a multi-lane authority-chain change, not a quick Fee Evaluation bug.
- The first formal lane should be a contract/data authority lane.
- Basic Information defaults, Matrix Step confirmed overrides, Fee passive consumption, and future Test Record/Report reuse should be separated.
- Implementation likely needs schema/API changes for Matrix draft/confirmed authority if structured values must survive save, confirm, and revision.
- Fee Evaluation should eventually prefer confirmed Matrix Step quantity authority and keep text parsing as compatibility fallback only if the contract allows it.

## Not Yet Confirmed / Blockers

1. Exact V1 vocabulary: readings/specimen, contact points/specimen, measurement points/sample, total readings, or another controlled set.
2. Matrix Step granularity: per group-row cell, per parsed step token inside a cell, or per row/group combination.
3. Whether Basic Information defaults imported into Matrix Step setup come from confirmed Basic Information only, drafts, or both.

## Recommended Split

1. `TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT` / `matrix-quantity-authority-contract`.
2. `TASK_357B_BASIC_INFORMATION_TEST_QUANTITY_DEFAULTS` / `basic-information-test-quantity-defaults`.
3. `TASK_357C_MATRIX_STEP_QUANTITY_SETUP_MODEL_UI` / `matrix-step-quantity-setup-model-ui`.
4. `TASK_357D_FEE_EVALUATION_MATRIX_QUANTITY_CONSUMPTION` / `fee-evaluation-matrix-quantity-consumption`.
5. `TASK_357E_TEST_RECORD_REPORT_QUANTITY_REUSE_CONTRACT` / `test-record-report-quantity-reuse-contract`.

Serial dependency: 357A -> 357B -> 357C -> 357D for implementation. 357E remains contract/planning until future Test Record/Report lanes are approved.

## Scope Locks

- No product code in this Planner pass.
- No approved implementation lane.
- No Developer routing.
- No StepInstance, Report generation, AI, permissions, LAN/server, or multi-user implementation.
- No LTR workbook/public-drive authority changes.
- No Matrix parser expansion.
- No Fee workbook export/template redesign.
- No real workbook/folder/document mutation.
- No release/settings residual cleanup.
- No `.agents/**` or `docs/project_management/**` edits.

## Validation Summary

Discovery file creation only. Pending after write:

- `git diff --check` on discovery plan/evidence.
- trailing whitespace scan on touched docs.
- targeted status to confirm no product code changed by this pass.

## Completion Decision

Completion status: `discovery_checkpoint`.

Recommended next role: User review. If accepted, route Planner to create planned `TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT` and then Reviewer plan gate. Do not route Developer from this checkpoint.

## Follow-Up Checkpoint - Blockers Answered

Date: 2026-07-08
Status: continued_to_planned_contract_lane

User/Orchestrator answered the three Discovery blockers:

1. V1 vocabulary may use the Planner-proposed structured quantity family, including fields such as `test_points_per_sample`, `readings_per_point`, `contact_points_per_sample`, and `total_readings`.
2. V1 granularity is one parameter set per Matrix Step. It does not initially split by group, condition, or sample size.
3. Basic Information draft values may be imported as defaults. Later authority updates can decide whether and how confirmed versions refresh defaults.

Planner decision:

- Create planned contract lane `TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT` / `matrix-quantity-authority-contract`.
- Keep implementation not authorized.
- Recommend next role: Reviewer plan gate.
- Do not route Developer from this Discovery checkpoint.
