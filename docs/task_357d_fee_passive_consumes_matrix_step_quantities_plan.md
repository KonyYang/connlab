# TASK_357D Fee Passive Consumes Matrix Step Quantities Plan

Status: complete/accepted by Integrator
Task: `TASK_357D_FEE_PASSIVE_CONSUMES_MATRIX_STEP_QUANTITIES`
Lane: `fee-passive-consumes-matrix-step-quantities`
Date: 2026-07-08
Role: Planner

## 1. Current Phase / Active Task / Role / Why Allowed

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current board state: `TASK_357C_MATRIX_STEP_QUANTITY_SETUP` is complete/accepted. It made Matrix Step setup the final per-Step quantity confirmation/override location and added confirmed Matrix Step quantity authority.
- Current role: Planner.
- Why allowed: User/Orchestrator requested the next downstream planned lane after TASK_357A/B/C completion. This pass creates source-of-truth docs only and does not authorize implementation.

## 2. User Goal Restatement

Fee Evaluation should consume confirmed Matrix Step quantity parameters for units/default-fill. Fee must not become the test point, reading, or contact-point input surface. Matrix Step quantity authority is the source; Basic Information remains an upstream default source only. Test Record and Report reuse remain future TASK_357E scope.

## 3. Confirmed By User

- TASK_357A contract is complete/accepted as downstream basis.
- TASK_357B Basic Information quantity defaults is complete/accepted.
- TASK_357C Matrix Step quantity setup is complete/accepted.
- Matrix Step setup is the final confirmation/override location for Step quantities.
- Fee Evaluation is a passive consumer.
- V1 fields remain:
  - `test_points_per_sample`
  - `readings_per_point`
  - `contact_points_per_sample`
  - derived `total_readings`
- Fee must not treat Basic Information defaults as final authority.
- TASK_357D must not implement Test Record/Report reuse.

## 4. Confirmed By Repository Evidence

- `docs/task_board.md` records TASK_357C complete/accepted and explicitly says downstream TASK_357D/E require separate lanes.
- Current `ConfirmedMatrixSnapshot` includes `step_quantities: tuple[ConfirmedMatrixStepQuantity, ...]`.
- `ConfirmedMatrixStepQuantity` carries `confirmed_group_id`, `confirmed_row_id`, `step_sequence`, `step_suffix_note`, `raw_token`, `test_points_per_sample`, `readings_per_point`, `contact_points_per_sample`, `source`, `review_required`, and `review_reason`.
- `backend/application/confirmed_matrix_fee_draft_service.py` currently builds Fee Evaluation lines from active Confirmed Matrix authority, row/group cells, parsed step tokens, and group sample quantity. It does not yet join/use confirmed Step quantities.
- `backend/modules/fee_evaluation/fee_default_fill.py` currently uses text parsing and `sample_quantity_expression` for per-reading, per-cycle, per-sample, duration, and current-based rules.
- `FeeDefaultFillContext` currently has test item, method, condition, requirement, sample quantity expression, spend time, and step tokens, but no structured Step quantity source.
- TASK_351 established backend-owned deterministic default-fill and field-level metadata, with text parsing as V1 behavior for LLCR/CR readings when explicit in Matrix text.

## 5. Planner Inferences

- TASK_357D should be a Fee backend-first lane with limited frontend metadata/display changes only if needed.
- The first safe consumption path is for per-reading/contact-resistance rules where Matrix Step quantities directly replace fragile readings/specimen text parsing.
- Duration, cycle, current, and per-sample rules should remain on existing TASK_351 logic unless Developer planning-first proves a direct Step-quantity mapping.
- Fee line items currently aggregate one row/group cell and may contain multiple step tokens. TASK_357D should define aggregation behavior for multiple Step quantities in one Fee line.
- Existing Fee editable `units` can remain an operator fee correction field, but edits must not write back to Matrix Step quantity authority.

## 6. Not Yet Confirmed

No blocker for Reviewer plan gate.

Implementation-level decisions for Developer planning-first:

1. Exact multiple-Step aggregation policy for one Fee line when a cell has multiple Step tokens.
2. Whether response DTOs need explicit quantity-source metadata or existing field metadata is enough.
3. Whether TASK_351 text parsing remains fallback for all affected rules or only for compatibility when no confirmed Step quantity exists.

## 7. Fee Passive-Consumer Contract

### 7.1 Source Priority

Recommended priority for affected Fee default-fill:

1. confirmed Matrix Step quantity authority;
2. existing TASK_351 deterministic text parsing compatibility fallback, only when Step quantity authority is absent/unmapped and Reviewer approves;
3. review-required/manual-required Fee row.

Fee must not read Basic Information quantity defaults directly as final authority.

### 7.2 Read-Only Consumption

Fee Evaluation may read:

- `confirmed_group_id`
- `confirmed_row_id`
- `step_sequence`
- `step_suffix_note`
- `raw_token`
- `test_points_per_sample`
- `readings_per_point`
- `contact_points_per_sample`
- derived `total_readings`
- source/review metadata

Fee Evaluation must not:

- edit Matrix Step quantities;
- create Matrix Step quantity records;
- write confirmed Matrix authority;
- back-propagate operator Fee edits into Matrix Step setup.

### 7.3 Rule Mapping Draft

Affected rules:

- LLCR / Contact Resistance Low Level:
  - prefer confirmed Step readings per sample from `total_readings` when available;
  - otherwise derive from `test_points_per_sample * readings_per_point` where both are valid;
  - otherwise use `contact_points_per_sample` as a contact/readings-per-sample candidate if Developer planning-first confirms rule semantics;
  - units should be group sample quantity multiplied by readings per sample;
  - unit-price tier should use readings per sample (`<=20` -> 1.5/reading, `>20` -> 1/reading).
- CR / Contact Resistance, Specified Current:
  - same source priority as LLCR for per-reading quantity;
  - current/tier specifics remain TASK_351 rule logic.

Rules likely unchanged in TASK_357D unless Developer planning-first proves mapping:

- Durability cycles: cycles are not a TASK_357A/C field, so keep explicit cycle parsing and review-required behavior.
- Hour/day duration rules: keep explicit duration parsing.
- Temperature Rise, force-family, sample preparation: keep group sample quantity behavior unless a confirmed Step quantity field is explicitly relevant.
- Microsecond discontinuity: keep fixed Units `1`.

### 7.4 Missing / Review-Required Behavior

If confirmed Step quantity record is missing, review-required, or ambiguous:

- do not invent units;
- preserve editable Fee row;
- emit compact review reason such as `Confirm Matrix Step quantity`;
- preserve field-level metadata so the operator understands which field is not auto-filled.

### 7.5 Multiple-Step Aggregation

V1 should avoid hidden averaging.

Recommended planning default:

- If a Fee line references multiple Step tokens and all mapped Step quantities produce the same readings-per-sample value, use that value once with a clear source.
- If multiple Step tokens produce different readings-per-sample values, mark the Fee line review-required.
- If Developer planning-first proposes summing across Step tokens, it must justify why that matches laboratory fee semantics and add tests.

## 8. May Touch

Current planning pass:

- `tasks/TASK_357D_FEE_PASSIVE_CONSUMES_MATRIX_STEP_QUANTITIES.md`
- `docs/task_357d_fee_passive_consumes_matrix_step_quantities_plan.md`
- `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_planner.md`
- `docs/task_board.md`

Future implementation draft:

- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/application/confirmed_matrix_fee_draft_models.py`
- `backend/modules/fee_evaluation/fee_default_fill.py`
- `backend/modules/fee_evaluation/fee_default_fill_models.py`
- `backend/modules/fee_evaluation/fee_default_fill_common.py` only for source metadata helpers if needed
- `backend/api/routes_confirmed_matrix_fee_draft.py` only if response DTOs expose quantity source/review metadata
- `frontend/src/api/client.ts` only for typed Fee draft metadata changes
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
- `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx` only if preview model wiring requires it
- focused backend Fee default-fill/draft service/API tests
- focused frontend Fee Evaluation model/table/page tests
- TASK_357D Developer/Reviewer/QA evidence and board updates

## 9. Must Not Touch / Locked Paths

Must not touch:

- Matrix Step setup authoring UI or authority mutation.
- Matrix Step quantity storage schema/migration, except read-only use of accepted TASK_357C fields.
- Basic Information quantity defaults or Basic Information schema/mutation behavior.
- Test Record / Report reuse implementation.
- StepInstance / execution persistence.
- Matrix parser/import rules.
- LTR workbook/public-drive authority.
- real workbook files, real folders, or public-drive data.
- release/settings/template residual cleanup.
- unrelated dirty files.

Locked paths:

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

## 10. Dependency Relationship

- Upstream: TASK_357A contract accepted.
- Upstream: TASK_357B Basic Information defaults accepted.
- Upstream: TASK_357C Matrix Step quantity setup accepted.
- This lane: TASK_357D Fee passive consumption of confirmed Matrix Step quantities.
- Downstream: TASK_357E Test Record / Report quantity reuse.

TASK_357E must not implement from TASK_357D evidence alone; it needs a separate lane.

## 11. Validation Gate Draft

Backend:

- Fee draft service maps confirmed Step quantities to row/group fee lines.
- LLCR/CR use confirmed Step readings-per-sample before text parsing.
- units are calculated from group sample quantity and Step readings-per-sample where deterministic.
- missing/review-required Step quantities produce review-required Fee rows.
- existing TASK_351 deterministic rules remain unchanged where Step quantities do not apply.
- Basic Information defaults are not read directly by Fee.
- Fee edits do not mutate Matrix Step quantities.

Frontend:

- Fee Evaluation still displays editable fee rows but does not expose point/reading/contact quantity setup fields.
- optional metadata/cue shows Matrix Step quantity source or review-required state if backend exposes it.
- existing update/export/readonly behavior remains compatible.

General:

- focused pytest for Fee draft/default-fill.
- focused `npm test` for Fee Evaluation model/table/page if UI metadata changes.
- `npm run build`.
- `git diff --check`.
- trailing whitespace scan.
- forbidden-scope scan for Matrix Editor, Basic Information, Test Record/Report, LTR/public-drive, real folder/workbook, release/settings residuals.

## 12. Merge Gate Draft

- Reviewer plan gate pass.
- User approval before Developer planning-first.
- Developer planning-first evidence must refine:
  - Step quantity lookup and aggregation;
  - fallback policy from TASK_351 text parsing;
  - Fee metadata/API response impact;
  - tests and package isolation.
- Reviewer implementation-readiness pass.
- User approval and source-of-truth reconciliation before Developer implementation.
- Reviewer implementation gate pass after code.
- QA required because this lane changes Fee default-fill behavior.
- Integrator packaging/readiness must isolate TASK_357D from external residuals.

## 13. Definition Of Ready

Ready for Reviewer plan gate: yes.

Not ready for implementation: yes, by design. Implementation requires Reviewer plan gate, user approval for Developer planning-first, Developer planning-first, Reviewer readiness, user implementation approval, and source-of-truth reconciliation.

## 14. Package Isolation Risks

The current worktree contains external residuals under Settings/LTR helper files, backend desktop/release helpers, `backend/api/dependencies.py`, `dist_release/**`, `packaging/**`, release scripts/tests/docs, frontend New Project test residuals, TASK_357A docs, and `temp_agents_stash.md`. TASK_357D must package only its task/plan/evidence/board planning files in this Planner pass and must not absorb those residuals.

## 15. Stop Point

Recommended next role: Reviewer plan gate.

Blocking summary: none.

Implementation remains unauthorized.

## 16. Developer Planning-First Refinement

Date: 2026-07-08
Role: Developer
Status: developer planning-first complete

This section refines the future implementation boundary after reading TASK_351 and TASK_357A/B/C accepted context plus current Fee Evaluation and confirmed Matrix code.

### 16.1 Implementation Boundary

TASK_357D should be implemented as a Fee Evaluation passive-consumer lane only.

Future implementation must:

- read `ConfirmedMatrixSnapshot.step_quantities` from the same active confirmed Matrix aggregate already used by `ConfirmedMatrixFeeDraftService`;
- match Step quantity records to each fee line by `confirmed_group_id`, `confirmed_row_id`, `step_sequence`, and normalized `step_suffix_note`;
- add structured Step quantity facts to the backend Fee default-fill context;
- let Fee default-fill consume those facts for mapped rules;
- keep Fee rows editable as fee-review rows only;
- never create, update, delete, or persist Matrix Step quantity authority from Fee.

Future implementation must not:

- call Basic Information repositories from Fee as a quantity source;
- mutate Matrix Step setup or confirmed Matrix authority;
- add Fee-side point/reading/contact input fields;
- change Matrix parser/import, StepInstance, Test Record, Report, LTR, public-drive, or real workbook/folder behavior.

### 16.2 Exact Future May Touch

Future implementation May Touch should be narrowed to:

- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/application/confirmed_matrix_fee_draft_models.py`
- `backend/modules/fee_evaluation/fee_default_fill.py`
- `backend/modules/fee_evaluation/fee_default_fill_models.py`
- `backend/modules/fee_evaluation/fee_default_fill_common.py` only if metadata helper additions are needed
- `backend/api/routes_confirmed_matrix_fee_draft.py` only if API DTOs expose new quantity source metadata
- `frontend/src/api/client.ts` only if DTO metadata changes require typed client updates
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
- `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx` only if metadata display wiring requires it
- `tests/unit/test_confirmed_matrix_fee_draft_service.py`
- `tests/unit/test_fee_default_fill.py`
- `tests/integration/test_confirmed_matrix_fee_draft_api.py` only if API response metadata changes
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx` only if UI metadata display changes
- TASK_357D developer/reviewer/QA evidence through normal lane flow

Do not include Matrix Editor files, Matrix Step quantity service/storage files, Basic Information files, Test Record/Report files, LTR/public-drive files, release/settings/template residuals, `.agents/**`, or `docs/project_management/**`.

### 16.3 Step Quantity Read Model

Build a local read-only lookup in `ConfirmedMatrixFeeDraftService`:

```text
(confirmed_group_id, confirmed_row_id, step_sequence, normalized_step_suffix_note)
  -> ConfirmedMatrixStepQuantity
```

Normalization must match TASK_357C: no suffix is treated as `""` for identity comparison while API/domain display can remain `None`.

Each parsed token from the confirmed Matrix cell should produce a lookup key:

- token sequence maps to `step_sequence`;
- token suffix maps to `step_suffix_note`;
- row/group come from the current fee line cell.

If a parsed Step token has no matching confirmed Step quantity record, that token is missing quantity authority for TASK_357D.

### 16.4 Fee Default-Fill Context Shape

Extend `FeeDefaultFillContext` with a tuple of Step quantity facts, not with Basic Information fields:

```text
step_quantities: tuple[FeeStepQuantityContext, ...]
```

Recommended `FeeStepQuantityContext` fields:

- `step_token`
- `step_sequence`
- `step_suffix_note`
- `test_points_per_sample`
- `readings_per_point`
- `contact_points_per_sample`
- `total_readings`
- `source`
- `review_required`
- `review_reason`
- `matched`

`total_readings` should be derived in Fee from the confirmed Step quantity values when both `test_points_per_sample` and `readings_per_point` are present and valid. It should not be persisted by Fee.

### 16.5 Rule Mapping Policy

TASK_357D V1 maps only rules where the Step quantity fields have clear fee semantics.

Mapped rules:

- `fee_rule_llcr`
- `fee_rule_contact_resistance_specified_current`

For these rules:

- `readings_per_sample` is `total_readings` when derivable from `test_points_per_sample * readings_per_point`;
- `contact_points_per_sample` is metadata for review and should not silently replace `total_readings` in V1 unless a later lane approves that semantic;
- unit-price tier uses `readings_per_sample`:
  - `<= 20` -> `1.5` per reading;
  - `> 20` -> `1` per reading;
- `units = group sample quantity * readings_per_sample`;
- `unit_label = reading`;
- field metadata for `units` and `testing_fee` should cite Matrix Step quantity authority, not text parsing.

Rules not mapped in TASK_357D:

- Durability, because cycles are not a TASK_357A/C quantity field.
- Hour/day duration rules, because duration remains text/rule parsing.
- Temperature Rise, because current is not a TASK_357A/C quantity field.
- Sample preparation, Report preparation, force-family, MFG, Vibration, Thermal Shock, Temperature Humidity, Microsecond discontinuity, Mechanical Shock, and generic fallback rules, unless they already use TASK_351 behavior.

### 16.6 Multiple-Step Aggregation Policy

For a single Fee line with multiple Step tokens:

- If every matched, non-review-required Step quantity produces the same `readings_per_sample`, use that value once for the row/group fee line.
- If Step quantities are missing for any token, mark the Fee line `review_required`.
- If any matched Step quantity itself has `review_required = true`, mark the Fee line `review_required`.
- If matched Step quantities produce different `readings_per_sample` values, mark the Fee line `review_required`.
- Do not sum multiple Step readings in V1. Summing may overcharge or double count unless a later business rule confirms the fee semantics.

This keeps aggregation explicit and conservative.

### 16.7 Fallback Policy

TASK_351 text parsing remains a compatibility fallback only when confirmed Step quantity authority is absent for the line, and only for rules that already used that parsing before TASK_357D.

Policy:

- If there are no confirmed Step quantity records for the parsed tokens in a line, existing TASK_351 text parsing may run unchanged.
- If some Step quantity records are present but missing/review-required/ambiguous, do not mix partial structured authority with text parsing. Return review-required with concise reason such as `Confirm Matrix Step quantity`.
- If a rule is unmapped by TASK_357D, keep existing TASK_351 behavior.
- Fee must never read Basic Information defaults directly as fallback.

### 16.8 Metadata / UI Policy

Prefer backend field metadata over new UI concepts.

Backend should expose existing `field_metadata` states for affected fields:

- `units`
- `unit_price`
- `testing_fee`

Recommended metadata source labels:

- `Matrix Step quantity`
- `Fee rule`
- existing rule display names where appropriate

Frontend should not add point/reading/contact edit controls. If API metadata changes are needed, Fee Evaluation UI should only display compact review cues already consistent with TASK_351:

- row remains editable for fee values;
- review cue is short, such as `Review: Confirm Matrix Step quantity`;
- no Matrix Step quantity setup table in Fee Evaluation.

### 16.9 Test Plan

Backend unit tests:

- LLCR uses confirmed Step quantity `3 * 2 = 6` readings per sample, group sample quantity `5`, units `30`, and unit price `1.5`.
- LLCR with readings per sample `25` uses unit price `1`.
- CR specified current follows the same Step quantity source policy while preserving current/tier logic from TASK_351.
- Missing Step quantity for a line with parsed Step tokens returns review-required instead of invented units when any Step quantity exists for that line context.
- Review-required Step quantity returns review-required Fee row.
- Multiple Step tokens with the same readings per sample calculate deterministically.
- Multiple Step tokens with different readings per sample return review-required.
- No Step quantity records for a line preserves TASK_351 text parsing compatibility.
- Unmapped rules such as Durability and duration rules retain existing TASK_351 behavior.
- Fee edits/default-fill do not call Matrix Step quantity repository write methods.

Backend integration/API tests if DTO metadata changes:

- Fee draft API returns field metadata showing Matrix Step quantity source on affected rows.
- Existing TASK_351 sample preparation/report preparation/manual default rows are unchanged.

Frontend tests only if UI/client metadata changes:

- Fee preview model preserves editable fee rows and does not create quantity-entry fields.
- Review-required metadata from Matrix Step quantity is shown as compact row cue.
- Existing `Update Fee` blocker behavior from TASK_355C remains intact.

General validation:

- focused pytest for Fee draft/default-fill;
- focused frontend Fee Evaluation tests if frontend touched;
- `npm run build` if frontend touched;
- `py -m py_compile` for touched backend modules;
- `git diff --check`;
- trailing whitespace scan;
- forbidden-scope scan for Matrix Editor, Basic Information, Test Record/Report, StepInstance, LTR/public-drive, real folders/workbooks, release/settings residuals, `.agents/**`, and `docs/project_management/**`.

### 16.10 Package Isolation Risks

Current worktree status shows external residuals including:

- `backend/api/dependencies.py` tracked residual;
- Settings/LTR/template services and tests;
- backend desktop/release helper files;
- `dist_release/**`, `packaging/**`, release scripts/tests/docs;
- frontend New Project test residual;
- TASK_357A docs/evidence residuals;
- `temp_agents_stash.md`.

TASK_357D implementation must isolate its package from these files and must not silently absorb release/settings/template/New Project residuals.

### 16.11 Readiness Decision

Developer planning-first found no blocker for Reviewer implementation-readiness.

Reviewer implementation-readiness passed, and user has now approved source-of-truth reconciliation plus Developer implementation.

## 17. Planner Source-Of-Truth Reconciliation

Date: 2026-07-08

Status: complete/accepted by Integrator.

Reconciled gate chain:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed as docs-only planning.
- Reviewer implementation-readiness passed.
- User approved source-of-truth reconciliation and Developer implementation.

Implementation authorization scope:

- Fee Evaluation passively consumes active `ConfirmedMatrixSnapshot.step_quantities` for units/default-fill.
- Step quantity matching is by `confirmed_group_id`, `confirmed_row_id`, `step_sequence`, and normalized suffix.
- `FeeDefaultFillContext` may receive structured Step quantity facts.
- V1 maps LLCR and CR specified-current per-reading rules only unless a later approved lane expands scope.
- `readings_per_sample` derives from `test_points_per_sample * readings_per_point` when deterministic.
- `contact_points_per_sample` remains review metadata.
- Multiple-Step aggregation remains conservative: same readings-per-sample may calculate, missing/review-required/different values must require review.
- TASK_351 text fallback remains only when structured Step quantity authority is absent or the rule is unmapped.
- Fee Evaluation remains a passive editable fee review surface with no point/reading/contact authoring UI.

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

Developer implementation pass, Reviewer B1 re-gate, QA gate, and Integrator packaging/readiness are complete.

## 18. Integrator Acceptance

Date: 2026-07-08

Status: complete/accepted by Integrator.

Accepted package:

- Fee Evaluation passive consumption of confirmed Matrix Step quantities.
- Focused backend default-fill/Fee draft implementation and tests.
- TASK_357D task, plan, Developer/Reviewer/QA/reconciliation evidence.
- `docs/task_board.md` closeout isolated from external residuals.

Validation summary:

- focused backend unit suite: 50 passed.
- focused backend integration suite: 20 passed.
- py_compile passed.
- frontend Fee Evaluation suite: 3 files / 55 tests passed with existing React act warnings only.
- `npm run build` passed with existing Vite chunk-size warning only.
- staged diff, whitespace, line-count, whitelist, and forbidden-scope checks passed.

Remote push was intentionally not performed.
