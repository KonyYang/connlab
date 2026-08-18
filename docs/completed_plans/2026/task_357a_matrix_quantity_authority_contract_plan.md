# TASK_357A Matrix Quantity Authority Contract Plan

Status: complete/accepted contract - downstream lane basis, implementation not authorized
Task: `TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT`
Lane: `matrix-quantity-authority-contract`
Date: 2026-07-08
Role: Planner

## 1. Current Phase / Active Task / Role / Why Allowed

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current board state: `TASK_356A_LTR_READONLY_WORKBOOK_OPEN_EXISTING_EXCEL` is complete and the board requires Orchestrator/User routing before new work.
- Current role: Planner.
- Why allowed: User/Orchestrator answered the Discovery blockers for `DISCOVERY_matrix-step-quantity-authority` and requested creation of a planned contract lane. This pass writes docs/source-of-truth only and does not authorize implementation.

## 2. User Confirmations

- Fee Evaluation must remain a passive consumer for point/reading/contact quantities.
- Basic Information may hold project-level default quantity values.
- Basic Information draft values may be imported into Matrix Step setup as defaults.
- Matrix Step setup is the final confirmation and override location.
- V1 field vocabulary may use:
  - `test_points_per_sample`
  - `readings_per_point`
  - `contact_points_per_sample`
  - `total_readings`
- V1 granularity is one parameter set per Matrix Step.
- V1 does not initially split quantity parameters by group, condition, or sample size.
- Confirmed Matrix Step quantities should later serve Fee Evaluation, Test Record, Report, and other derived outputs.

## 3. Repository Facts

- `AGENTS.md` and `PRODUCT.md` define Matrix as the execution authority map, with Fee Evaluation, Test Record, and Report as derived outputs.
- `TASK_351_FEE_EVALUATION_AUTO_DEFAULT_FILL` is complete and has backend-owned default-fill rules, but current LLCR/CR units still depend on parsing readings/specimen from Matrix text when available.
- Current Basic Information service has draft/confirmed records but no test quantity default fields.
- Current Matrix draft and confirmed authority models persist groups, group sample quantity expressions, rows, and cells, but no structured per-step quantity parameters.
- Current Fee Evaluation frontend already displays editable `units`, field metadata, and review-required state from backend responses; it should not become the quantity authority surface.
- Current Test Record/Fee dataset preview has conservative quantity-basis text and no structured quantity authority.

## 4. Contract Draft

### 4.1 Authority Order

1. Basic Information default:
   - Provides project-level default quantity values.
   - May come from draft Basic Information for default import.
   - Confirmed Basic Information remains the stronger local project record when available, but draft values may still be used as operator-entered defaults before confirmation.
2. Matrix Step setup:
   - Imports Basic Information defaults when available.
   - Allows the operator to override the defaults per Step.
   - Becomes the final authority after Matrix confirmation.
3. Fee Evaluation:
   - Consumes confirmed Matrix Step quantity values.
   - May show review-required when quantities are missing.
   - Must not become the primary entry surface for these quantities.
4. Test Record / Report:
   - Future derived consumers of confirmed Matrix Step quantity values.
   - Must not be implemented in TASK_357A.

### 4.2 V1 Field Vocabulary

The contract should define these fields as structured numeric-or-empty values with source metadata:

| Field | Meaning | Typical use |
|---|---|---|
| `test_points_per_sample` | Default or confirmed test points measured for one sample/specimen. | General measurement-point workflows. |
| `readings_per_point` | Readings taken at each point. | Readings totals when one point can have multiple readings. |
| `contact_points_per_sample` | Contact points measured for one sample/specimen. | LLCR/CR/contact-resistance workflows. |
| `total_readings` | Derived or manually confirmed total reading count for one Step. | Fee Evaluation units for `per reading` rules. |

Recommended source metadata:

- `source`: `basic_information_draft`, `basic_information_confirmed`, `matrix_step_override`, `derived`, or `manual_required`.
- `review_required`: boolean.
- `review_reason`: short business-readable reason.

### 4.3 Step Granularity

V1 uses one parameter set per Matrix Step.

The contract must explicitly avoid V1 support for:

- separate values by group;
- separate values by condition;
- separate values by sample size;
- per-token splitting inside one Step unless a future contract reopens it.

If implementation later discovers the current Matrix model lacks an explicit Step identity, TASK_357C must define the closest stable identity without changing this contract silently.

### 4.4 Basic Information Default Source

- Draft Basic Information values may be imported into Matrix Step setup as defaults.
- Confirmed Basic Information values may also be imported.
- Imported values are defaults only. They do not become final downstream authority until confirmed in Matrix Step setup.
- Later changes to Basic Information should not silently rewrite already confirmed Matrix Step quantities. Refresh/update behavior must be previewed or manually triggered in a later implementation lane.

### 4.5 Matrix Step Final Authority

- Matrix Step setup owns final override before downstream consumption.
- Confirming Matrix should persist the structured quantity values with the confirmed Matrix authority.
- Revision flow must define whether quantities are copied, reset, or review-required when rows/steps change.
- Missing Step quantity data should remain a visible review state, not an invented number.

### 4.6 Fee Passive Consumer Boundary

- Fee Evaluation may display units, source/review metadata, and editable fee pricing fields.
- Fee Evaluation must not become the first-class entry surface for test points/readings/contact points.
- Fee default-fill should later prefer confirmed Matrix Step quantity values over text parsing for affected rules.
- Existing text parsing from TASK_351 may remain compatibility fallback only if downstream plan/review confirms it.

### 4.7 Test Record / Report Future Boundary

- Test Record and Report may later consume confirmed Matrix Step quantity values.
- TASK_357A does not authorize StepInstance, Report generation, execution persistence, evidence/image assets, or AI review.
- Any Test Record / Report implementation requires separate lanes.

## 5. Recommended Downstream Lanes

1. `TASK_357B_BASIC_INFORMATION_TEST_QUANTITY_DEFAULTS`
   - Add Basic Information default fields and persistence/API/UI once contract accepted.
2. `TASK_357C_MATRIX_STEP_QUANTITY_SETUP_MODEL_UI`
   - Add Matrix Step setup model/UI and final confirmation/override behavior.
3. `TASK_357D_FEE_EVALUATION_MATRIX_QUANTITY_CONSUMPTION`
   - Make Fee Evaluation consume confirmed Matrix Step quantities.
4. `TASK_357E_TEST_RECORD_REPORT_QUANTITY_REUSE_CONTRACT`
   - Plan future Test Record/Report reuse without implementation.

## 6. May Touch

- `tasks/TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT.md`
- `docs/task_357a_matrix_quantity_authority_contract_plan.md`
- `docs/lane_evidence/TASK_357A_matrix-quantity-authority-contract_planner.md`
- `docs/lane_evidence/DISCOVERY_matrix-step-quantity-authority_planner.md`
- `docs/task_board.md`

## 7. Must Not Touch / Locked Paths

Must not touch:

- product backend code;
- product frontend code;
- tests outside docs-only validation;
- Basic Information implementation;
- Matrix Editor implementation;
- Fee Evaluation implementation;
- Matrix parser/import implementation;
- LTR workbook/public-drive authority implementation;
- Test Record / Report / StepInstance / AI / permissions / LAN/server / multi-user implementation;
- release/settings/template residual cleanup.

Locked paths:

- `backend/**`
- `frontend/**`
- `tests/**`
- `frontend/src/api/client.ts`
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

## 8. Acceptance Criteria

1. Contract clearly defines Basic Information defaults, Matrix Step final authority, Fee passive consumption, and future Test Record/Report reuse.
2. Contract includes V1 field vocabulary and Step-level granularity.
3. Contract records that draft Basic Information may be imported as defaults.
4. Contract explicitly blocks implementation and future-scope work.
5. Contract defines downstream lane order and parallelization limits.
6. Reviewer can use this plan to decide whether TASK_357A is ready as a contract source-of-truth lane.

## 9. Validation Gate

- `git diff --check -- docs/task_board.md tasks/TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT.md docs/task_357a_matrix_quantity_authority_contract_plan.md docs/lane_evidence/TASK_357A_matrix-quantity-authority-contract_planner.md docs/lane_evidence/DISCOVERY_matrix-step-quantity-authority_planner.md`
- trailing whitespace scan on touched docs.
- targeted `git status --short` proving no product code changed by this Planner pass.

## 10. Merge Gate

- Reviewer plan gate pass.
- No Developer implementation from TASK_357A.
- Downstream TASK_357B+ lanes must be created separately through Planner flow and user approval.

## 11. Definition Of Ready

TASK_357A is ready for Reviewer plan gate as a planned contract lane.

It is not ready for Developer implementation because this lane intentionally authorizes no product code.

## 12. Developer Planning-First Refinement

Status: developer planning-first complete.

This refinement keeps TASK_357A as a contract/source-of-truth lane only. It does not authorize backend, frontend, API, schema, seed, parser, Fee, Basic Information, Matrix Editor, Test Record, Report, or test implementation changes.

### 12.1 Current Repository Boundary

Repository facts checked during Developer planning-first:

- Basic Information currently persists generic `values` for draft and confirmed records. It has no structured test quantity fields.
- Matrix draft and confirmed authority currently persist selected groups, group `sample_quantity_expression`, rows, and sparse cells. They do not persist structured quantity parameters per Step.
- Matrix Editor has parsed step-token concepts and runtime projections, but current persisted Matrix authority still stores row/group/cell data rather than a first-class Step quantity authority record.
- Fee Evaluation consumes active Confirmed Matrix authority and group `sample_quantity_expression`. TASK_351 default-fill provides backend-owned field metadata and review-required classification, but LLCR/CR reading units still rely on text extraction plus group sample quantity when structured quantities are absent.
- Test Record/Fee dataset preview still emits conservative quantity-basis text and does not consume structured quantity authority.

### 12.2 V1 DTO / Field Naming Contract

Future implementation lanes should use one Step quantity parameter object with the following stable field names:

| Field | Type contract | Meaning | Derived relationship |
|---|---|---|---|
| `test_points_per_sample` | decimal-compatible number or empty | Number of measured test points for one sample/specimen. | May feed `total_readings` when paired with `readings_per_point` and sample quantity. |
| `readings_per_point` | decimal-compatible number or empty | Number of readings taken for each measured point. | May feed `total_readings`. |
| `contact_points_per_sample` | decimal-compatible number or empty | Contact points measured for one sample/specimen. | Preferred default source for LLCR/CR contact-count workflows when applicable. |
| `total_readings` | decimal-compatible number or empty | Total reading count for the Step across selected quantity basis. | May be manually confirmed or derived. Fee should prefer this when present. |

Recommended metadata per field:

- `value`: normalized decimal string or empty.
- `source`: one of `basic_information_draft`, `basic_information_confirmed`, `matrix_step_override`, `derived`, `manual_required`, `compatibility_text_parse`.
- `review_required`: boolean.
- `review_reason`: short business-readable text when review is required.
- `updated_at` / `updated_by`: required once the Matrix Step override lane persists operator changes.

Recommended aggregate fields:

- `step_quantity_id`: stable record ID once persisted.
- `step_identity`: stable V1 Step identity for the Matrix Step lane to define, likely based on confirmed/draft row lineage plus parsed step token identity.
- `quantity_basis`: `per_matrix_step` for V1.
- `source_revision`: Basic Information or Matrix source revision used when defaults were imported.

### 12.3 Source Precedence And Import Policy

The contract source precedence is:

1. Matrix Step override: final operator-confirmed value for downstream consumers.
2. Imported Basic Information confirmed default: stronger default when available, but still not final until accepted in Matrix Step setup.
3. Imported Basic Information draft default: allowed as an operator convenience before Basic Information confirmation, but must remain default/proposed state.
4. Derived value: allowed only when source fields are explicit and deterministic.
5. Compatibility text parse: allowed only as a fallback for existing behavior and should carry source metadata.
6. Manual required: no invented numeric value.

Basic Information defaults are import defaults only:

- Creating or opening Matrix Step setup may prefill from latest Basic Information draft/confirmed values.
- Basic Information edits must not silently mutate already confirmed Matrix Step quantities.
- Refreshing defaults after Basic Information changes must be explicit, previewed, or handled by a later approved lane.
- Confirmed Basic Information may supersede draft as the preferred default for new Matrix Step setup sessions, but not as an automatic downstream authority.

### 12.4 Matrix Step Override Record Semantics

TASK_357C should define the closest stable V1 Step identity. The record should support one parameter set per Matrix Step and should not split by group, condition, or sample size in V1.

Minimum Matrix Step behavior for future implementation:

- Import defaults into Step setup with visible source/review metadata.
- Let the operator accept, clear, or override each quantity field.
- Persist the override with draft Matrix state before confirmation.
- Copy the accepted values into confirmed Matrix authority at Matrix confirmation.
- Mark missing or stale values `review_required` instead of inventing values.
- On Matrix revision, carry forward quantities only when Step identity is stable; otherwise mark review-required.

### 12.5 Fee Evaluation Passive Consumption Contract

Fee Evaluation must remain a passive consumer:

- It may consume confirmed Matrix Step quantities from active Confirmed Matrix authority.
- For per-reading rules, it should prefer confirmed `total_readings` when available.
- If `total_readings` is absent but confirmed `test_points_per_sample`, `readings_per_point`, `contact_points_per_sample`, and sample quantity provide a deterministic derivation, the backend may calculate with metadata.
- If structured quantities are absent, TASK_351 compatibility text parsing may remain only as fallback metadata, not as the new authority.
- Fee UI may display source/review cues and editable pricing values, but must not become the primary point/reading/contact quantity input surface.

### 12.6 Future Test Record / Report Reuse Boundary

Test Record and Report lanes may later consume confirmed Matrix Step quantities, but TASK_357A does not authorize:

- StepInstance persistence;
- execution-result persistence;
- image/evidence assets;
- report generation;
- AI review;
- permissions, LAN/server, or multi-user behavior.

TASK_357E should define read-only reuse expectations before any Test Record/Report implementation.

### 12.7 Downstream Lane Split And Gates

Recommended downstream order:

1. `TASK_357B_BASIC_INFORMATION_TEST_QUANTITY_DEFAULTS`
   - Add Basic Information default fields only.
   - Preserve draft/confirmed behavior and expose values as default candidates.
   - Must not make Basic Information final downstream authority.
2. `TASK_357C_MATRIX_STEP_QUANTITY_SETUP_MODEL_UI`
   - Define/persist Matrix Step quantity records and UI.
   - Import Basic Information defaults.
   - Make Matrix Step setup the final override authority at Matrix confirmation.
3. `TASK_357D_FEE_EVALUATION_MATRIX_QUANTITY_CONSUMPTION`
   - Consume confirmed Matrix Step quantities.
   - Keep Fee UI passive and compatibility text parsing as fallback only if still needed.
4. `TASK_357E_TEST_RECORD_REPORT_QUANTITY_REUSE_CONTRACT`
   - Contract/planning only for Test Record/Report reuse.

Dependency gates:

- TASK_357D implementation must not start until TASK_357C has a confirmed Matrix Step quantity authority read model.
- TASK_357B and TASK_357C may be planned in parallel after TASK_357A acceptance, but implementation ordering must prevent Fee from depending on Basic Information directly as final authority.
- Any schema migration belongs to the specific downstream implementation lane, not TASK_357A.

### 12.8 Future May Touch Drafts

Potential TASK_357B files:

- `backend/application/project_basic_information_service.py`
- Basic Information repository/model/API DTO files if needed.
- Basic Information frontend model/components/tests if UI is included.
- Focused Basic Information backend/frontend tests.

Potential TASK_357C files:

- Matrix draft/confirmed domain models.
- Matrix draft persistence / confirmation services and repositories.
- Matrix Editor Step setup components, selectors, and tests.
- API DTO/client types only if needed for Step quantity setup.

Potential TASK_357D files:

- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/application/confirmed_matrix_fee_draft_models.py`
- Fee default-fill modules under `backend/modules/fee_evaluation/`
- Fee frontend display/model tests only for source/review metadata consumption.

Potential TASK_357E files:

- Contract docs/evidence only unless separately approved.

### 12.9 Must Not Touch / Locked Paths For This Lane

TASK_357A Developer planning-first may touch only:

- `docs/task_357a_matrix_quantity_authority_contract_plan.md`
- `docs/lane_evidence/TASK_357A_matrix-quantity-authority-contract_developer.md`

It must not touch:

- `backend/**`
- `frontend/**`
- `tests/**`
- `frontend/src/api/client.ts`
- Matrix parser/import implementation
- Basic Information implementation
- Matrix Editor implementation
- Fee Evaluation implementation
- Test Record / Report / StepInstance implementation
- LTR workbook/public-drive authority implementation
- real workbook/folder/document data
- release/settings/template residual cleanup
- `.agents/**`
- `docs/project_management/**`

### 12.10 Test And Validation Plan For Downstream Series

TASK_357B validation should cover:

- draft and confirmed Basic Information default quantity values;
- required/optional field handling;
- source metadata and no silent Matrix/Fee authority behavior.

TASK_357C validation should cover:

- default import from Basic Information draft and confirmed values;
- operator override persistence;
- Matrix confirmation copying structured quantities into confirmed authority;
- Matrix revision carry-forward versus review-required behavior;
- one parameter set per Matrix Step.

TASK_357D validation should cover:

- Fee uses confirmed Matrix Step `total_readings` before text parsing;
- deterministic derivation from confirmed Step fields where permitted;
- missing quantities produce review-required rows;
- frontend remains display/edit pricing surface, not quantity-authoring surface.

TASK_357A planning-first validation remains docs-only:

- required docs/evidence exist;
- `git diff --check` on TASK_357A plan/evidence;
- trailing whitespace scan on touched docs;
- targeted status proves no product code changed by this pass.

### 12.11 Package Isolation Risks

The current workspace contains external residuals in Settings/LTR, release/desktop/packaging, New Project tests, `dist_release/**`, `packaging/**`, `temp_agents_stash.md`, and `docs/task_board.md`. They must remain excluded from TASK_357A. This lane's package is docs-only and must not absorb those residuals.

## 13. Developer Planning-First Stop Point

Recommended next role: Reviewer implementation-readiness gate.

Blocking summary: none.

Implementation remains not authorized. Downstream product implementation requires separate source-of-truth reconciliation, Reviewer readiness, and user approval.

## 14. Planner Source-Of-Truth Reconciliation

Date: 2026-07-08
Status: contract readiness passed / downstream lane basis

Facts reconciled:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed docs-only and refined the contract.
- Reviewer implementation-readiness gate passed.
- User/Orchestrator approved source-of-truth reconciliation and downstream planned lane creation.

Planner decision:

- TASK_357A is complete/accepted as a contract lane and may be used as the source-of-truth basis for downstream lane planning.
- TASK_357A still does not authorize product implementation.
- First downstream planned lane: `TASK_357B_BASIC_INFORMATION_QUANTITY_DEFAULTS` / `basic-information-quantity-defaults`.
- Next role after this reconciliation: Reviewer plan gate for TASK_357B.
