# TASK_351 Fee Evaluation Auto Default Fill Plan

Status: complete - Integrator accepted after hard-limit fix
Task: `TASK_351_FEE_EVALUATION_AUTO_DEFAULT_FILL`
Lane: `fee-evaluation-auto-default-fill`
Date: 2026-07-05
Role: Planner / Developer planning-first

## 1. Current Phase / Active Task / Role / Why Allowed

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current board state: `TASK_350C_MATRIX_IMPORT_REMOVE_NATIVE_CONFIRM_GUARD` is complete/accepted. TASK_351 Reviewer plan gate passed, user approved Developer planning-first, Developer planning-first completed, Reviewer implementation-readiness passed, and user approved reconciliation plus Developer implementation.
- Current role: Planner.
- Why allowed: the user and Orchestrator explicitly requested Planner source-of-truth reconciliation after Reviewer implementation-readiness pass and user approval for Developer implementation. This pass does not write product code.

## 2. User Goal Restatement

The Fee Evaluation page should reduce manual pricing input by automatically filling most pricing fields from a controlled first-version rule library. The operator still reviews and can correct the values before confirming fee or generating the Fee Form.

The target fields are:

- Man-hour
- Unit Price
- Unit Type
- Units
- Base Fee
- Discount
- Testing Fee
- Notes / review-required reasons

## 3. Confirmed By User

- The rule source should be the manually completed Testing Fee Evaluation `.xls` examples, especially Testing Prices and Unit Price Reference.
- Reference attachment `D:/Template/FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls` is the template authority version for planning/reference. V1 implementation may proceed with user-confirmed rules plus the existing seed JSON; it does not require making the attachment a controlled fixture before DoR.
- Unit Price Reference entries should enter the first rule-library layer.
- Auto-fill should only fill deterministic values.
- Complex, interval, multi-mode, or missing-source rules must be marked `review_required`.
- Base Fee should be filled only where explicit. Otherwise it should remain blank or require manual confirmation.
- Description aliases must be supported and expanded gradually.
- Sample preparation defaults Man-hour `0.5`, Unit Price `50`, Unit Type `per sample`, Units from Matrix group sample quantity, Discount `100%`.
- Visual Examination / Examination of Product defaults Man-hour `0.5`, Unit Price `10`, Unit Type `per photo`, Units `3`, Discount `100%`.
- LLCR uses Unit Price Reference tiers: `<=20 readings/specimen` is `1.5/reading`; `>20 readings/specimen` is `1/reading`. The 3 RMB per reading example is manual adjustment only.
- LLCR Units may start from Matrix group sample quantity. If readings/specimen can be derived, total readings should be computed; if not, mark review-required.
- Durability defaults Unit Type `per cycle`, Units = Matrix group sample quantity * cycles; Unit Price tiers are `<=50 cycles/specimen` -> `2/cycle`, `50~250 cycles/specimen` -> `1/cycle`, `>250 cycles/specimen` -> `0.5/cycle`; Base Fee is not hard-filled unless explicit.
- High temperature Life / Pre-High temperature Life defaults Unit Price `15`, Unit Type `per hour`, Units parsed from hours in description/condition.
- Thermal Shock defaults Unit Price `30`, Unit Type `per hour`, Units parsed from hours.
- Cycling Temperature & Humidity / Temperature Humidity / Thermal Disturbance defaults Unit Price `25`, Unit Type `per hour`, Units parsed from hours.
- MFG / Mixed Flowing Gas defaults to Class IIA, Unit Price `1000`, Unit Type `per day`, Units parsed from days. Discount is not hard-filled unless explicit.
- Vibration / Random Vibration V1 defaults Unit Price `300`, Unit Type `per hour`.
- Microsecond discontinuity maps to `300 per time`, Units `1`.
- Mechanical Shock defaults Unit Price `30`, Unit Type `per time`; Units remain review-required if not clear.
- Mating/Un-mating Force and force-family items default Unit Price `50`, Unit Type `per sample`, Units from Matrix group sample quantity. Base Fee is not hard-filled unless explicit.
- CR / Contact Resistance, Specified Current uses Unit Type `per reading` and Unit Price Reference tiers when required facts are available; otherwise review-required.
- Report preparation / Report defaults Man-hour `4`, Unit Price `600`, Unit Type `per report`, Units `1`, Discount `100%`.
- Temperature Rise / T-rise uses current tiers from Unit Price Reference:
  - `<=240A`: `500/specimen`
  - `>240A and <=500A`: `600/specimen`
  - `>500A and <=1000A`: `700/specimen`
  - `>1000A and <=2000A`: `800/specimen`
  - Units equals Matrix group sample quantity.
  - Man-hour equals `4`.
  - Base Fee defaults to `500`, but must be flagged for manual confirmation / review-required.
  - A 300A attachment example with 500/specimen is treated as manual discount/experience adjustment; the default rule uses 600/specimen for 300A.

## 4. Confirmed By Repository Evidence

- `backend/application/confirmed_matrix_fee_draft_service.py` already builds Fee Evaluation drafts from the active Confirmed Matrix authority.
- The backend draft already has `status`, `review_required`, `review_reason`, matched rule ID/name/version, calculation strategy, `unit_price`, `units`, `base_fee`, `discount_percent`, and `testing_fee`.
- The backend already loads a `FeeRuleLibrary` through `load_active_fee_rule_library()` and matches Matrix test items through `FeeRuleMatcher`.
- `backend/modules/fee_evaluation/seeds/fee_rules_v2026_06_03.json` already contains Unit Price Reference-style seed rules for LLCR, Visual exam, Vibration, Temperature rise, Report preparation, and other fee items.
- Current seed rules intentionally mark many complex rules as `review_required`.
- Current calculation only auto-calculates existing deterministic strategies such as `per_sample`, `per_specimen`, and `fixed_per_group` when base fee and unit price are numeric.
- Current `_review_reason_for_rule()` explicitly marks `per_photo`, `per_reading`, `per_cycle`, and `per_hour` as not yet derived.
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts` already maps backend draft rows into editable preview rows.
- `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx` already renders editable cells for Man-hour, Unit Price, Unit Type, Units, Base Fee, Discount, and Notes.
- `frontend/src/api/client.ts` already exposes typed Fee Evaluation draft and line-item fields.

## 5. Inferred By Planner

- TASK_351 should be a formal lane because it changes pricing default authority, backend rule semantics, API shape possibilities, frontend review indications, and validation coverage.
- The right architecture is not to hard-code pricing defaults in React. Backend should own rule matching and default-fill suggestions; frontend should display and preserve editability.
- The current seed JSON can remain the reviewed rule source, but the calculation layer needs richer strategy support for the user-confirmed deterministic cases.
- Some rules can be implemented as deterministic autofill now; others should stay review-required with partial suggestions.
- The first implementation can probably avoid database schema changes if it keeps defaults in the draft response and existing pricing draft persistence continues to store edited row values.
- Description alias expansion should stay data-driven in the rule library, not scattered in UI code.

## 6. Not Yet Confirmed

No blocking product questions remain for Reviewer plan gate.

Implementation-level details that Developer planning should make concrete:

- Exact extraction patterns for hours, days, cycles/specimen, readings/specimen, and current values from Matrix description, condition, or requirement text.
- Whether field-level source/review metadata is necessary in the API response, or whether row-level `review_required` and `review_reason` are sufficient for V1.
- Exact frontend visual treatment for auto-filled but review-required values.

## 7. Risks

- Pricing defaults can become business authority by accident if review-required fields are not clear.
- Attachment-derived examples can mix true defaults with manual discount/override behavior.
- Unit derivation can be wrong when Matrix sample quantity is not a plain numeric value.
- Existing editable frontend fields can hide which values were auto-filled versus operator-entered unless review metadata is surfaced.
- Export and pricing draft persistence must not silently drop new metadata or overwrite operator corrections.

## 8. Non-Goals

- No real workbook mutation.
- No runtime parsing or importing of external `.xls` files. The provided template path is planning/reference authority only for this lane.
- No Fee workbook template redesign.
- No Matrix parser, Confirmed Matrix authority, Test Record, Report, StepInstance, AI, permissions, LAN/server, multi-user, Folder Actions, Intake LTR, Projects registry/list, or release/settings cleanup.

## 9. May Touch Draft

- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/modules/fee_evaluation/fee_rule_models.py`
- `backend/modules/fee_evaluation/fee_rule_matcher.py`
- `backend/modules/fee_evaluation/fee_rule_seed_loader.py`
- `backend/modules/fee_evaluation/seeds/fee_rules_v2026_06_03.json`
- New helper under `backend/modules/fee_evaluation/` for default-fill rule evaluation if needed.
- `backend/api/routes_confirmed_matrix_fee_draft.py` only if response metadata changes.
- `frontend/src/api/client.ts` only if response metadata changes.
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
- `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
- Focused backend/frontend tests for Fee Evaluation default-fill.
- TASK_351 docs/evidence/board through normal lane flow.

## 10. Must Not Touch / Locked Paths Draft

Must not touch:

- Matrix parser/import/Confirmed Matrix authority semantics.
- Fee workbook Office gateway/template layout except regression checks.
- Real Testing Fee Evaluation `.xls` files, real public-drive files, real LTR workbook files, and user project folders.
- Folder Actions, Intake LTR, Projects registry/list, Project Workbench lifecycle, Matrix Editor unrelated behavior.
- StepInstance, Report generation, AI, permissions, LAN/server, multi-user.
- Release/settings/basic-information residual cleanup.

Locked paths:

- `backend/modules/test_plan/**`
- `frontend/src/features/matrix-editor/**`
- `frontend/src/features/new-project/**`
- `frontend/src/features/project-workbench/**`
- `frontend/src/pages/ProjectListPage.tsx`
- `backend/application/public_folder_*`
- `backend/application/*ltr*`
- `dist_release/**`
- `packaging/**`
- `.agents/**`
- `docs/project_management/**`

## 11. First Rule Library Design

The rule library should keep two related layers:

1. Rule library layer:
   - canonical fee rule ID and display name
   - aliases
   - source reference
   - unit label / unit type
   - unit price representation
   - base fee representation
   - calculation strategy
   - deterministic or review-required classification
   - review reason

2. Auto-fill layer:
   - decides which fields can be filled for one Matrix-derived row
   - records value source and review reason
   - keeps non-deterministic fields blank or partially suggested
   - returns a normal Fee Evaluation draft row that remains editable

Recommended V1 deterministic and partial rules:

| Rule | Default behavior |
|---|---|
| Sample preparation | Man-hour 0.5; Unit Price 50; Unit Type `per sample`; Units from Matrix group sample quantity; Discount 100 percent |
| Visual Examination / Examination of Product | Man-hour 0.5; Unit Price 10; Unit Type `per photo`; Units 3; Discount 100 percent |
| LLCR / Contact Resistance (Low Level) | Unit Type `per reading`; Unit Price 1.5/reading when <=20 readings/specimen and 1/reading when >20; calculate total readings when readings/specimen can be derived; otherwise review-required |
| Durability | Unit Type `per cycle`; Units = sample quantity * cycles; Unit Price 2/cycle when <=50 cycles/specimen, 1/cycle when 50-250, 0.5/cycle when >250; Base Fee review-required unless explicit |
| High temperature Life / Pre-High temperature Life | Unit Price 15; Unit Type `per hour`; Units parsed from hours |
| Thermal Shock | Unit Price 30; Unit Type `per hour`; Units parsed from hours |
| Cycling Temperature & Humidity / Temperature Humidity / Thermal Disturbance | Unit Price 25; Unit Type `per hour`; Units parsed from hours |
| MFG / Mixed Flowing Gas | Default Class IIA; Unit Price 1000; Unit Type `per day`; Units parsed from days; Discount review-required unless explicit |
| Vibration / Random Vibration | Unit Price 300; Unit Type `per hour`; Units review-required unless duration is explicit |
| Microsecond discontinuity | Unit Price 300; Unit Type `per time`; Units 1 |
| Mechanical Shock | Unit Price 30; Unit Type `per time`; Units review-required when unclear |
| Mating/Un-mating Force / force family | Unit Price 50; Unit Type `per sample`; Units from Matrix group sample quantity; Base Fee review-required unless explicit |
| CR / Contact Resistance, Specified Current | Unit Type `per reading`; apply Unit Price Reference tier only when the needed facts are explicit; otherwise review-required |
| Report preparation / Report | Man-hour 4; Unit Price 600; Unit Type `per report`; Units 1; Discount 100 percent |
| Temperature Rise / T-rise | Unit Price tier by current; Units from sample quantity; Man-hour 4; Base Fee 500 and review-required; 300A defaults to 600/specimen |

## 11.1 Description Alias Mechanism

The alias mechanism should stay rule-library driven:

- Each rule owns canonical display name and aliases.
- Aliases should include common English names, abbreviated lab names, and known workbook variants.
- Matching should continue using conservative normalization from `FeeRuleMatcher`.
- Ambiguous token matches must not auto-fill silently; they should remain review-required.
- Alias additions should be tested with focused matcher tests so future rule-library growth does not change unrelated matches.

## 12. Data / API / Frontend Boundaries

Backend:

- Owns fee rule loading, alias matching, deterministic default calculation, and review-required classification.
- Must not put fee rule logic in API route bodies.
- Should keep rule source version traceability in the existing draft header or row metadata.

API:

- Existing `GET /api/projects/{project_id}/confirmed-matrix/fee-draft` may remain the main read endpoint.
- Add response metadata only if frontend needs to distinguish `auto_filled`, `suggested`, `review_required`, and `manual_required` states.
- Avoid new endpoints unless Developer planning proves the current draft route cannot represent the state.

Frontend:

- Keeps the table editable.
- Shows compact review-required cues when backend marks a field or row uncertain.
- Does not compute pricing defaults itself.
- Does not expose long explanatory copy; ConnLab UI should stay dense and operational.

## 13. Acceptance Criteria Draft

- Fee Evaluation preview auto-fills deterministic values for the user-confirmed V1 rules.
- Non-deterministic rules preserve review-required state and a business-readable reason.
- User-confirmed V1 rules above are represented in the rule library layer.
- Alias matching remains deterministic and conservative.
- Operator can manually edit prefilled values.
- Edited values remain compatible with pricing draft persistence and workbook export payloads.
- Existing no-rule-match and warning behavior is preserved.
- Existing read-only Fee Evaluation state still disables edits.
- No unrelated product, Matrix, LTR, Folder, release, or governance residuals are packaged.

## 14. Validation Command Draft

Suggested focused backend validation:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_fee_draft_service.py tests/unit/test_fee_rule_matcher.py tests/unit/test_fee_rule_seed_loader.py -q
py -m pytest tests/integration/test_confirmed_matrix_fee_draft_api.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q
```

Suggested focused frontend validation:

```powershell
npm test -- FeeEvaluation --run
npm run build
```

Packaging validation:

```powershell
git diff --check
```

## 15. Definition Of Ready

Ready for a planned formal lane and Reviewer plan discussion: yes.

Ready for Reviewer plan gate: passed.

Ready for Developer planning-first: yes.

Ready for approved implementation: yes. Developer planning-first completed, Reviewer implementation-readiness passed, user approved reconciliation and Developer implementation, and Planner source-of-truth reconciliation recorded implementation authorization.

## 16. Recommended Next Role

Developer implementation pass. Developer must stay within the approved TASK_351 Fee Evaluation default-fill scope and update Developer evidence before review.

## 17. Source-Of-Truth Reconciliation

2026-07-05 Planner reconciliation records the following source-of-truth chain:

- Reviewer plan gate passed read-only and confirmed TASK_351 is a formal backend/frontend Fee Evaluation rule/default-fill lane, not a quick fix.
- Reviewer confirmed May Touch, Must Not Touch, Locked Paths, acceptance criteria, and validation gates are sufficient for Developer planning-first.
- User explicitly approved `TASK_351` entering Developer planning-first.
- Developer created a blocked checkpoint because repository source-of-truth still described TASK_351 as planned for Reviewer plan gate only.
- No product code was changed by Developer or Planner in the blocked/reconciliation passes.
- This historical reconciliation authorized Developer planning-first only; the later implementation reconciliation below authorizes implementation.

## 18. Developer Planning-First Refinement

Developer planning-first confirms the lane should remain one implementation lane because the rule-library changes, backend default-fill service, API metadata, frontend compact review cues, and focused tests are tightly coupled through the existing Fee Evaluation preview route. No database migration is required for V1.

Implementation must stay deterministic and explainable:

- Backend owns all extraction, default-fill, and review-required classification.
- Frontend owns only editable display, compact uncertainty cues, and user correction.
- Runtime parsing of `D:/Template/FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls` remains out of scope.
- The existing seed JSON remains the active rule source, with explicit V1 default-fill metadata added there instead of hardcoding pricing in UI.
- Fee workbook export remains driven by edited preview values and existing pricing draft payloads.

## 19. Extraction Pattern Decisions

All extraction must use existing Confirmed Matrix row/group facts only: test item, method, condition, requirement, group sample quantity expression, row day/duration text when already available, and rule-library aliases. Do not infer unavailable laboratory facts from Matrix cell count alone.

V1 extraction rules:

- Sample quantity: use only a plain non-negative numeric Matrix group sample quantity. Expressions such as `5+(5e)`, ranges, or annotated quantities remain review-required.
- Hours: match explicit hour text such as `10 h`, `10 hr`, `10 hrs`, `10 hour`, or `10 hours` from item/condition/requirement/duration text. Do not convert days to hours unless the rule is day-based.
- Days: for MFG only, match explicit day text such as `3 day`, `3 days`, or `3 d` in business context. Avoid matching `D` inside DL numbers, method names, or identifiers.
- Cycles: match explicit cycle text such as `50 cycles`; use sample quantity times cycles for Units. Missing cycles means Units and fee stay review-required.
- Current: for Temperature Rise, match explicit ampere text such as `300A`, `300 A`, `300 amp`, or `300 amps`; do not match `mA` or infer current from method text.
- Readings/specimen: for LLCR and specified-current contact resistance, use only explicit readings, points, contacts per specimen/sample wording. If readings/specimen is missing, keep Units and tiered Unit Price review-required.
- Mechanical Shock: default Unit Price and Unit Type can be suggested, but Units remain manual-required unless explicit count/time wording is present.
- Microsecond discontinuity: Units defaults to `1`.
- Force-family items: Units come from plain Matrix group sample quantity.
- Report preparation: use a trailing default row with the confirmed report defaults.
- Sample preparation: use the existing sample preparation row location but populate it from backend-controlled defaults rather than frontend-only zero placeholders.

## 20. Field-Level Metadata Decision

Developer planning-first recommends adding field-level metadata. The existing row-level `review_required` is not enough for partial-review rules such as Temperature Rise, where Unit Price and Units can be filled while Base Fee is a suggested value requiring confirmation.

Proposed API DTO addition:

```text
field_metadata: FeeEvaluationFieldMetadata[]
```

Proposed metadata shape:

```text
field: spend_time | unit_price | unit_label | units | base_fee | discount_percent | testing_fee
state: auto_filled | suggested_review | manual_required | not_available
source: short rule/source label or null
message: compact business-readable reason or null
```

Row-level `review_required` remains as a compatibility summary. A row is review-required when any required pricing field is `suggested_review`, `manual_required`, or `not_available`. `review_reason` should be a compact aggregate reason such as `Review base fee` or `Enter readings/specimen`.

Existing edited pricing draft payloads should not persist metadata. Metadata is recalculated from backend rules and shown in the current preview session. User edits remain the authority for export after saving the pricing draft.

## 21. Seed JSON Strategy

Implementation should extend the existing rule-library seed instead of adding UI-local pricing tables.

Preferred V1 structure:

- Add optional `default_fill` metadata to fee rules in `backend/modules/fee_evaluation/seeds/fee_rules_v2026_06_03.json`.
- Validate `default_fill` through `fee_rule_models.py` and `fee_rule_seed_loader.py`.
- Interpret `default_fill` in a new focused backend helper, for example `backend/modules/fee_evaluation/fee_default_fill.py`.
- Keep aliases rule-owned and matcher-driven.
- Keep ambiguous matches as review-required rather than silently filling.

If implementation finds the structured seed field too large for one safe patch, it may use a small backend mapping keyed by stable `rule_id` only after recording the tradeoff in Developer evidence. Frontend hardcoding is not allowed.

## 22. Compact Review-Required UI Treatment

The Fee Evaluation page should remain dense and operational.

Frontend behavior:

- Auto-filled fields display normal editable values with no extra visual noise.
- Suggested or manual-required fields remain editable and get a subtle cell-level state style plus a compact row cue.
- Row cue copy should be short, for example `Review base fee`, `Enter readings/specimen`, `Confirm duration`, or `Confirm units`.
- Do not write review copy into the editable Notes value unless the operator enters it.
- Do not add new cards, long help text, side stripes greater than 1px, gradient text, or decorative surfaces.
- Read-only Fee Evaluation state must still disable edits through existing lifecycle behavior.

Implementation should update `feeEvaluationPreviewModel.ts` to map backend metadata into row field metadata and update `FeeEvaluationPreviewTable.tsx` to render compact cues without changing pricing calculations in the frontend.

## 23. Future Implementation File List

Approved future implementation should be limited to:

- `backend/modules/fee_evaluation/fee_rule_models.py`
- `backend/modules/fee_evaluation/fee_rule_seed_loader.py`
- `backend/modules/fee_evaluation/fee_default_fill.py`
- `backend/modules/fee_evaluation/seeds/fee_rules_v2026_06_03.json`
- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/api/routes_confirmed_matrix_fee_draft.py`, only if response DTO exposure requires a route-level update
- `frontend/src/api/client.ts`, only for typed Fee Evaluation metadata DTOs
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
- `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`, only if existing save/confirm wiring needs metadata-safe state handling
- focused backend/frontend tests listed below
- TASK_351 plan/evidence docs

Locked paths remain: runtime external `.xls` parsing, real workbook/public-drive/folder mutation, Matrix parser/import, Confirmed Matrix authority, Fee workbook template redesign, lifecycle semantics, StepInstance, Report, AI, permissions, LAN/server, multi-user, release/settings residual cleanup, `.agents/**`, and `docs/project_management/**`.

## 24. Focused Test Plan

Backend tests:

- Seed validation accepts the V1 `default_fill` metadata and rejects invalid field names, unit labels, or unsupported extraction strategies.
- Alias matcher remains conservative and ambiguous aliases do not silently auto-fill.
- Sample preparation and report preparation defaults fill the confirmed values.
- Visual Examination fills `0.5`, `10`, `per photo`, `3`, and `100%`.
- LLCR fills tiered readings only when readings/specimen and sample quantity are derivable; otherwise marks relevant fields review-required.
- Durability parses cycles and applies the tiered per-cycle price.
- Hour/day rules parse explicit durations and mark missing duration review-required.
- Temperature Rise at `300A` fills Unit Price `600`, Units from sample quantity, Man-hour `4`, and Base Fee `500` with field-level review.
- Manual or unclear rules keep editable review-required values without breaking draft generation.

Frontend tests:

- API DTO mapping preserves field metadata.
- Auto-filled fields render editable values.
- Review-required fields render compact cues and subtle cell state without mutating Notes.
- User edits still update Testing Fee and pricing draft payloads.
- Read-only Fee Evaluation remains non-editable.
- Existing export/confirm flow remains compatible.

Suggested validation commands for implementation:

```powershell
py -m pytest tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_matcher.py tests/unit/test_fee_default_fill.py tests/unit/test_confirmed_matrix_fee_draft_service.py -q
py -m pytest tests/integration/test_confirmed_matrix_fee_draft_api.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q
npm test -- FeeEvaluation --run
npm run build
git diff --check
```

Static checks should include trailing whitespace and forbidden-scope status scans proving no Matrix import, New Project/LTR, Folder Actions, Workbench lifecycle, real workbook/public-drive, release/settings, `.agents/**`, or `docs/project_management/**` changes are packaged.

## 25. Implementation Authorization Reconciliation

2026-07-05 Planner implementation reconciliation records the following source-of-truth chain:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed and updated TASK_351 plan/evidence only.
- Reviewer implementation-readiness passed.
- User explicitly approved TASK_351 reconciliation and Developer implementation.
- TASK_351 is now implementation authorized and pending Developer implementation.

Authorized implementation scope:

- Fee Evaluation auto default-fill for Man-hour, Unit Price, Unit Type, Units, Base Fee, Discount, Testing Fee, and review-required/manual confirmation metadata.
- V1 uses user-confirmed rules plus the existing seed JSON.
- `D:/Template/FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls` remains template authority reference only; no runtime `.xls` ingestion.
- Unit Price Reference items enter the first-version rule-library layer.
- Auto-fill fills only deterministic fields; complex, interval, multi-mode, or missing-source cases remain `review_required`.
- Temperature Rise Base Fee defaults to `500` and remains review-required/manual confirmation.
- LLCR computes total readings only when readings/specimen and sample quantity are derivable; otherwise it remains review-required.
- Description aliases remain rule-library driven and extensible.

Still locked:

- No real workbook, public-drive, LTR workbook, or user folder mutation.
- No Matrix parser/import or Confirmed Matrix authority changes.
- No Fee workbook template redesign except regression checks.
- No schema change unless separately justified and re-gated.
- No StepInstance, Report generation, AI, permissions, LAN/server, multi-user, release/settings/basic-information residual cleanup.
- No `.agents/**` or `docs/project_management/**` changes.

## 26. Integrator Packaging Blocker

Date: 2026-07-05

Integrator gate: blocked.

Blocking finding:

- `backend/modules/fee_evaluation/fee_default_fill.py` is a new package file and is 533 lines, exceeding the AGENTS Python file hard limit of 500 lines.
- `backend/application/confirmed_matrix_fee_draft_service.py` grows from 396 lines in HEAD to 594 lines in the candidate package.
- Functional validation passed, but Integrator cannot accept a package that introduces or expands hard-limit violations.

Candidate package otherwise reviewed:

- Fee Evaluation backend default-fill helper, draft service, route DTO exposure, seed JSON, and focused backend/API tests.
- Fee Evaluation frontend API typing, preview model, preview table, focused frontend tests, and compact review metadata display.
- TASK_351 task/plan/evidence docs and `docs/task_board.md` closeout.

Validation accepted:

- Backend focused unit suite passed: 42 tests.
- Backend focused integration suite passed: 20 tests.
- Frontend Fee Evaluation suite passed: 3 files / 53 tests, with existing React `act(...)` warnings only.
- Backend `py_compile` passed for touched modules/routes.
- Frontend build passed with existing Vite chunk-size warning only.
- Diff, trailing whitespace, no-real-workbook/folder, and forbidden-scope checks passed.

Scope exclusions:

- No runtime external `.xls` parsing.
- No real workbook, public-drive, LTR workbook, or user folder mutation.
- No Matrix parser/import, Confirmed Matrix authority, ProjectList, Matrix Editor, New Project/LTR, Workbench Folder Actions, release/settings cleanup, `.agents/**`, or `docs/project_management/**` changes were packaged.
- Remote push was intentionally not performed.

Required next role:

- Developer fix pass to split or reduce backend default-fill/service code below hard limits without changing TASK_351 scope, then Reviewer/QA re-gate as needed.

## 27. Integrator Re-Gate Acceptance

Date: 2026-07-05

Integrator gate: accepted.

Developer hard-limit fix:

- Split default-fill DTOs into `backend/modules/fee_evaluation/fee_default_fill_models.py`.
- Split shared default-fill result builders into `backend/modules/fee_evaluation/fee_default_fill_common.py`.
- Split Confirmed Matrix Fee draft DTOs/protocols into `backend/application/confirmed_matrix_fee_draft_models.py`.
- Split backend-owned Sample preparation and Report preparation manual defaults into `backend/application/confirmed_matrix_fee_manual_defaults.py`.
- Kept `backend/modules/fee_evaluation/fee_default_fill.py` and `backend/application/confirmed_matrix_fee_draft_service.py` below the AGENTS Python file hard limit.

Acceptance:

- Reviewer re-gate passed and confirmed the prior Integrator hard-limit blocker is closed.
- QA re-gate was not required by Reviewer because the post-QA fix was a behavior-preserving backend module split.
- Integrator packaging/readiness accepted the package after focused regression validation and staged scope checks.
- Remote push was intentionally not performed.
