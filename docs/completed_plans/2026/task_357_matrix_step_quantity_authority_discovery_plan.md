# TASK_357 Matrix Step Quantity Authority Discovery Plan

Status: discovery checkpoint only - not approved for implementation
Discovery ID: `DISCOVERY_matrix-step-quantity-authority`
Date: 2026-07-08
Role: Planner

## 1. Current Phase / Active Task / Role / Why Allowed

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current board state: `TASK_356A_LTR_READONLY_WORKBOOK_OPEN_EXISTING_EXCEL` is complete, and the board says the next action requires Orchestrator/User routing.
- Current role: Planner.
- Why allowed: the user explicitly requested a Planner Discovery Gate for a new Matrix quantity authority series. This pass only records facts, split recommendations, risks, and Definition of Ready. It does not create an approved implementation lane, write product code, or route Developer.

## 2. User Goal Restatement

ConnLab needs a controlled authority chain for test point / reading / contact-point quantities:

1. Basic Information may hold project-level default values, such as `20 points/readings per specimen`.
2. Matrix Step setup is the final confirmation and override point. A step may import Basic Information defaults, then override them, for example Power-related steps using `4` points instead of the project default `20`.
3. Fee Evaluation should passively consume confirmed Matrix Step quantities for `units` and should not become the reminder, entry, or authority screen for those quantities.
4. The same structured Matrix Step quantity data should later serve Fee Evaluation, Test Record, Report, and other derived outputs.

## 3. Confirmed By User

- Fee Evaluation is a passive consumer for point/reading/contact quantities.
- Basic Information can collect project-level default test point/reading values as fallback defaults.
- Matrix Step is the final confirmation/override location.
- Per-step values may differ from the Basic Information default.
- Confirmed Matrix Step structured quantity data should serve Fee Evaluation, Test Record, Report, and future derived outputs.

## 4. Confirmed By Repository Evidence

- `AGENTS.md` and `PRODUCT.md` state that Matrix is the execution authority map, Project is the lifecycle container, and Fee Evaluation / Test Record / Report are derived outputs.
- `docs/task_board.md` records `TASK_351_FEE_EVALUATION_AUTO_DEFAULT_FILL` complete/accepted and confirms Fee Evaluation default-fill is backend-owned from confirmed Matrix authority.
- `backend/modules/fee_evaluation/fee_default_fill.py` currently computes LLCR/CR `units` only when readings/specimen can be parsed from Matrix row text and sample quantity is a plain number.
- `backend/application/confirmed_matrix_fee_draft_service.py` builds Fee Evaluation drafts from active Confirmed Matrix authority using group `sample_quantity_expression`, row fields, and parsed step tokens. It does not consume a structured per-step quantity setup model.
- `backend/domain/project_matrix_draft_models.py` and `backend/domain/confirmed_matrix_authority_models.py` currently persist group `sample_quantity_expression`, rows, and cells. They do not expose structured fields such as readings per specimen, contact points per sample, or total readings per step.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` currently manages selected groups, group sample quantity expressions, row detail fields, cell step tokens, and confirm guards. It has no dedicated Step setup UI for structured quantity parameters.
- `backend/application/project_basic_information_service.py` assembles Basic Information from project/LTR/application/sample sources and persists operator drafts/confirmed records. Existing Basic Information fields are identity and project information fields; there are no project-level default readings/contact-point fields.
- `backend/application/test_record_fee_dataset_preview_service.py` still emits a conservative fee `quantity_basis` string and does not consume structured Matrix Step quantity authority.
- `docs/task_351_fee_evaluation_auto_default_fill_plan.md` already documents the current limitation: LLCR readings/specimen are derived only when explicit text can be found; otherwise review is required.
- `docs/02_ARCHITECTURE_RULES.md` and `docs/frontend_architecture_rules.md` require backend/application ownership for authoritative rules, centralized API access, and frontend feature boundaries rather than business logic in page JSX.

## 5. Inferred By Planner

- This is not a Fee Evaluation quick fix. It changes the data authority chain for execution quantities and should be split.
- The first lane should be a product/data authority contract before implementation. Without it, Basic Information, Matrix, Fee, Test Record, and Report could each invent incompatible meanings for "points", "readings", "contacts", and "units".
- The current group-level sample quantity remains useful but is not enough for per-step readings/contact quantities.
- A likely V1 domain shape is:
  - project default quantity settings in Basic Information, for example default readings/contact points per specimen;
  - Matrix Step quantity setup values per confirmed group/row/cell or step-token context;
  - derived total units computed from sample quantity and per-specimen/per-step quantity when deterministic;
  - source metadata indicating imported default, operator override, or unresolved/manual review.
- The implementation may require schema/API changes if structured per-step setup must survive draft save, confirm, revision, and downstream consumption. That should be reviewed explicitly rather than hidden inside Fee logic.
- Fee Evaluation should later prefer confirmed Matrix Step quantities over text parsing, with text parsing retained only as compatibility fallback if the contract permits it.

## 6. Not Yet Confirmed / Blocker Questions

These block approved implementation but not discovery:

1. What exact V1 fields should be supported: `readings_per_specimen`, `contact_points_per_specimen`, `measurement_points_per_sample`, `total_readings`, or a smaller controlled set?
2. What is the Matrix Step granularity for V1: one setup per group-row cell, one setup per parsed step token inside a cell, or one setup per Matrix row/group combination regardless of token count?
3. Should Basic Information defaults be confirmed-only authority, draft fallback, or both, when importing defaults into Matrix Step setup?

## 7. Recommended Lane Split

### TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT

- Lane: `matrix-quantity-authority-contract`
- Purpose: define the product/data authority contract for project defaults, Matrix Step overrides, downstream consumption, audit/source metadata, and migration constraints.
- Dependency: first and serial.
- Suggested next role: User review, then Reviewer plan gate if the user wants this contract formalized.

May Touch:

- `docs/task_357a_matrix_quantity_authority_contract_plan.md`
- `tasks/TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT.md`
- `docs/lane_evidence/TASK_357A_matrix-quantity-authority-contract_planner.md`
- `docs/task_board.md` only through normal planning flow.

Must Not Touch / Locked Paths:

- `backend/**`
- `frontend/**`
- `tests/**`
- real workbook/folder data
- `.agents/**`
- `docs/project_management/**`

Validation:

- Contract review checks that authority order is Basic Information default -> Matrix Step confirmed override -> downstream derived outputs.
- Contract must define vocabulary, granularity, migration strategy, and fallback behavior before product code.

### TASK_357B_BASIC_INFORMATION_TEST_QUANTITY_DEFAULTS

- Lane: `basic-information-test-quantity-defaults`
- Purpose: add project-level default quantity fields to Basic Information after the contract is accepted.
- Dependency: after TASK_357A.
- Parallelism: can be planned in parallel with TASK_357C only after TASK_357A fixes field names/API contract; implementation should likely happen before Matrix default import.

May Touch Draft:

- `backend/application/project_basic_information_service.py`
- Basic Information repository/model/API route/DTO files if the contract requires persisted fields.
- `frontend/src/features/project-basic-information/**`
- `frontend/src/api/client.ts` only for typed Basic Information DTO changes.
- focused Basic Information backend/frontend tests.

Must Not Touch / Locked Paths:

- Matrix editor parser/import/authority confirmation behavior except tests that prove no regression.
- Fee Evaluation default-fill logic.
- LTR workbook/public-drive authority writes.
- Report/Test Record/StepInstance execution persistence.
- release/settings residuals and unrelated dirty files.

Validation:

- Basic Information draft/confirm persists default fields.
- Existing identity fields and TASK_353A confirmed identity behavior remain unchanged.
- Defaults have clear empty/manual-review behavior and do not mutate Intake raw data or LTR notes.

### TASK_357C_MATRIX_STEP_QUANTITY_SETUP_MODEL_UI

- Lane: `matrix-step-quantity-setup-model-ui`
- Purpose: make Matrix Step setup the final confirmation/override location for structured quantities, importing Basic Information defaults where applicable.
- Dependency: after TASK_357A and probably after TASK_357B for implementation. Planning can begin once TASK_357A answers granularity.
- Parallelism: must be serial before Fee consumption.

May Touch Draft:

- `backend/domain/project_matrix_draft_models.py`
- `backend/domain/confirmed_matrix_authority_models.py`
- Matrix draft persistence/session/confirm/revision services.
- Matrix API DTOs/routes for draft save and confirmed authority read models.
- `frontend/src/features/matrix-editor/**`
- `frontend/src/api/client.ts` for Matrix DTOs.
- focused Matrix backend/frontend tests.

Must Not Touch / Locked Paths:

- Fee calculation/default-fill implementation except compatibility tests.
- StepInstance execution persistence, Report generation, AI, permissions, LAN/server, multi-user.
- Matrix parser rule expansion unless explicitly approved.
- real user documents/workbooks/folders.

Validation:

- Matrix Step setup can import Basic Information defaults.
- Operator can override per applicable step.
- Confirmed Matrix authority persists structured quantities and source metadata.
- Existing group sample quantity guard remains intact.
- Revision flow preserves or intentionally resets quantity setup according to contract.

### TASK_357D_FEE_EVALUATION_MATRIX_QUANTITY_CONSUMPTION

- Lane: `fee-evaluation-matrix-quantity-consumption`
- Purpose: make Fee Evaluation consume confirmed Matrix Step quantities for units, with no entry authority in Fee.
- Dependency: after TASK_357C.
- Parallelism: cannot implement before confirmed Matrix structured quantities exist.

May Touch Draft:

- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/modules/fee_evaluation/fee_default_fill.py`
- Fee default-fill models/tests.
- `frontend/src/features/fee-evaluation/**` only to display source/review metadata if needed.
- `frontend/src/api/client.ts` only if response metadata changes.

Must Not Touch / Locked Paths:

- Basic Information fields/model except read-only contract tests.
- Matrix Step setup UI/model except fixture/read-model consumption.
- Fee workbook export/template redesign.
- Test Record/Report implementation.
- real workbook/folder data.

Validation:

- LLCR/CR units prefer confirmed Matrix Step readings/contact quantities.
- Fee page does not introduce point/reading entry controls.
- Missing Matrix Step quantity shows review-required in Fee without inventing values.
- Existing TASK_351 rules remain stable for unrelated fee lines.

### TASK_357E_TEST_RECORD_REPORT_QUANTITY_REUSE_CONTRACT

- Lane: `test-record-report-quantity-reuse-contract`
- Purpose: plan how Test Record and Report later consume confirmed Matrix Step quantities without implementing future execution persistence.
- Dependency: after TASK_357A; implementation after TASK_357C.
- Parallelism: planning can run in parallel with Fee consumption planning after Matrix contract, but product implementation should wait until structured quantities exist.

May Touch Draft:

- docs/task/evidence only for contract.
- later implementation may touch Test Record dataset preview services and report adapters only under separate approval.

Must Not Touch / Locked Paths:

- StepInstance persistence.
- Report generation expansion.
- AI review, image/evidence execution asset management.
- Fee Evaluation implementation.

Validation:

- Contract references confirmed Matrix Step quantity fields as read-only inputs.
- No new execution/report feature is exposed before its own lane.

## 8. Dependency And Parallelization Recommendation

Serial core:

1. TASK_357A contract.
2. TASK_357B Basic Information defaults.
3. TASK_357C Matrix Step setup model/UI.
4. TASK_357D Fee Evaluation passive consumption.

Potential parallel planning:

- TASK_357B and TASK_357C planning may overlap after TASK_357A if the contract fixes field names and ownership.
- TASK_357D and TASK_357E planning may overlap after TASK_357C design is stable, but implementation should remain downstream of confirmed Matrix structured quantity persistence.

Not parallel:

- Fee Evaluation implementation must not precede Matrix Step confirmed quantity authority.
- Test Record/Report implementation must not precede Matrix Step confirmed quantity authority.

## 9. Global Must Not Touch / Locked Paths

- No product code in this Discovery pass.
- No approved implementation lane from this pass.
- No Developer routing.
- No StepInstance, execution persistence, image/evidence assets, report generation, AI, permissions, LAN/server, or multi-user implementation.
- No LTR workbook/public-drive authority changes.
- No Matrix parser/import rule expansion unless a later lane explicitly approves it.
- No Fee workbook template/export redesign.
- No real user workbook/folder/document mutation.
- No release/settings/template residual cleanup.
- No `.agents/**` or `docs/project_management/**` edits.

## 10. Validation Gate Draft For The Series

- Backend unit tests for Basic Information default field persistence and source priority.
- Matrix backend tests for draft save, autosave, confirm, revision, and active authority read-model persistence of structured quantities.
- Matrix frontend tests for default import, manual override, disabled/readonly states, and visible source/review cues.
- Fee backend tests proving units come from confirmed Matrix Step quantities for LLCR/CR/contact families and remain review-required when missing.
- Fee frontend tests proving units are passive display/editable Fee pricing fields, not source-of-truth quantity entry.
- Regression tests for existing sample quantity guard and TASK_351 default-fill behavior.
- `npm run build`.
- `git diff --check`, trailing whitespace scan, and forbidden-scope scans for future-scope and real-data paths.

## 11. Definition Of Ready

Discovery is complete enough to recommend a formal contract lane, but not enough to approve implementation.

- Ready for User review: yes.
- Ready for Reviewer plan gate on a contract-only TASK_357A lane: yes, after user confirms the lane should be created.
- Ready for Basic Information / Matrix / Fee implementation: no.

Blocking inputs before approved implementation:

1. Controlled field vocabulary.
2. Matrix Step quantity granularity.
3. Basic Information draft-vs-confirmed default import policy.

## 12. Recommended Next Role

User review of this Discovery checkpoint. If accepted, route Planner to create a formal planned `TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT` lane, then Reviewer plan gate. Do not route Developer from this checkpoint.
