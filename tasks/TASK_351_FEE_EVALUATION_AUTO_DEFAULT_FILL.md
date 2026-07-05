# TASK_351_FEE_EVALUATION_AUTO_DEFAULT_FILL

Status: complete - Integrator accepted after hard-limit fix
Lane: fee-evaluation-auto-default-fill
Owner: Planner / Reviewer
Created: 2026-07-05

## Goal

Plan the first controlled Fee Evaluation auto default-fill lane so the Fee Evaluation page can prefill most pricing fields from the reviewed Unit Price Reference rule layer while keeping operator review and manual correction available before confirmation.

The target fields are Man-hour, Unit Price, Unit Type, Units, Base Fee, Discount, Testing Fee, and review-required notes where a rule is not deterministic.

## Why This Is A Formal Lane

This is not a quick UI-only edit. The work touches the current Confirmed-Matrix-backed Fee Evaluation draft service, fee rule seed semantics, typed API responses, editable frontend preview rows, pricing draft persistence expectations, and workbook export inputs. It must pass Planner, Reviewer, Developer planning-first, implementation review, QA, and Integrator gates before implementation can be accepted.

## Current Phase And Authorization

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current board state: TASK_350C complete/accepted; TASK_351 Reviewer plan gate passed; user approved Developer planning-first; Developer planning-first completed; Reviewer implementation-readiness passed; user approved reconciliation and Developer implementation.
- This task is implementation authorized and pending Developer implementation.
- Developer implementation must stay within the approved Fee Evaluation auto default-fill scope and update Developer evidence before review.
- Reviewer implementation gate, QA gate, and Integrator packaging/readiness remain required before completion.

## Confirmed User Rules

- Fee Evaluation should reduce manual input by auto-filling most fields while preserving final human confirmation and correction.
- Reference attachment `D:/Template/FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls` is the template authority version for rule reference. TASK_351 V1 may proceed with user-confirmed rules plus the existing seed JSON; it does not require making that attachment a controlled fixture before Definition of Ready.
- Unit Price Reference items should enter the rule-library layer.
- Auto-fill should fill only deterministic fields; complex, interval, or multi-mode rules must remain review-required.
- Base Fee is filled only when explicit; otherwise leave blank or flag manual confirmation.
- Description aliases must be supported and grow over time.
- Sample preparation defaults: Man-hour 0.5, Unit Price 50, Unit Type per sample, Units from Matrix group sample quantity, Discount 100 percent.
- Visual Examination / Examination of Product defaults: Man-hour 0.5, Unit Price 10, Unit Type per photo, Units 3, Discount 100 percent.
- LLCR default rule: <=20 readings/specimen uses 1.5 per reading; >20 readings/specimen uses 1 per reading. The observed 3 RMB per reading attachment value is a manual adjustment, not the default.
- LLCR Units may start from Matrix group sample quantity; when readings/specimen can be derived, calculate total readings. If reading count is insufficient, mark review-required.
- Durability defaults: Unit Type per cycle, Units = Matrix group sample quantity * cycles; Unit Price tiers <=50 cycles/specimen 2/cycle, 50-250 cycles/specimen 1/cycle, >250 cycles/specimen 0.5/cycle; Base Fee remains manual unless explicit.
- High temperature Life / Pre-High temperature Life defaults: Unit Price 15, Unit Type per hour, Units parsed from hours in description/condition.
- Thermal Shock defaults: Unit Price 30, Unit Type per hour, Units parsed from hours.
- Cycling Temperature & Humidity / Temperature Humidity / Thermal Disturbance defaults: Unit Price 25, Unit Type per hour, Units parsed from hours.
- MFG / Mixed Flowing Gas defaults to Class IIA: Unit Price 1000, Unit Type per day, Units parsed from days; Discount not hard-filled unless explicit.
- Vibration / Random Vibration V1 follows the attachment habit: Unit Price 300, Unit Type per hour.
- Microsecond discontinuity must map to 300 per time, Units 1.
- Mechanical Shock defaults: Unit Price 30, Unit Type per time; Units remain review-required when not clear.
- Mating/Un-mating Force and force-family items default: Unit Price 50, Unit Type per sample, Units from Matrix group sample quantity; Base Fee remains manual unless explicit.
- CR / Contact Resistance, Specified Current uses Unit Type per reading and Unit Price Reference tiers when the required count/current facts are available; otherwise review-required.
- Report preparation / Report defaults: Man-hour 4, Unit Price 600, Unit Type per report, Units 1, Discount 100 percent.
- Temperature Rise / T-rise defaults from the Unit Price Reference current tier: <=240A 500/specimen; >240A and <=500A 600/specimen; >500A and <=1000A 700/specimen; >1000A and <=2000A 800/specimen. Units come from Matrix group sample quantity. Man-hour is 4. Base Fee may default to 500 but must be flagged for manual confirmation.
- For Temperature Rise, an attachment example at 300A using 500/specimen is treated as manual discount/experience adjustment. Default rule should use 600/specimen for 300A.

## Repository Evidence

- `backend/application/confirmed_matrix_fee_draft_service.py` already builds read-only Fee Evaluation drafts from active Confirmed Matrix authority and exposes `review_required`, matched rule identity, unit price, units, base fee, discount, testing fee, and warnings.
- `backend/modules/fee_evaluation/seeds/fee_rules_v2026_06_03.json` already contains a reviewed Unit Price Reference seed with LLCR, Visual exam, Vibration, Temperature rise, Report preparation, and other items.
- `backend/modules/fee_evaluation/fee_rule_models.py` and `fee_rule_matcher.py` already provide rule models, allowed strategy/unit vocabularies, alias matching, and deterministic no-match handling.
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts` already maps draft values into editable preview rows for Man-hour, Unit Price, Unit Type, Units, Base Fee, Discount, Testing Fee, and Notes.
- `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx` already renders editable cells for the target pricing fields and keeps read-only gating support.
- `frontend/src/api/client.ts` already has typed `FeeEvaluationDraft` and `FeeEvaluationLineItem` shapes with review and pricing fields.

## Planned Scope

In scope for a future implementation after approval:

- Extend the Fee Evaluation rule library and calculation layer to represent the user-confirmed deterministic defaults.
- Keep non-deterministic pricing as review-required with business-readable reasons.
- Add or update calculation strategies only where required for the confirmed rules.
- Preserve existing editable preview behavior so auto-filled values can still be corrected before confirmation.
- Add focused backend and frontend tests proving defaults, review flags, manual edit compatibility, and export payload compatibility.

Out of scope:

- Direct parsing of external `.xls` attachments during runtime. The provided template path may be used as planning/reference context only unless a later approved lane adds controlled fixture ingestion.
- Real public-drive or workbook mutation.
- Matrix parser changes.
- Confirmed Matrix authority changes.
- Fee workbook template redesign.
- Persistent schema changes unless Developer planning proves they are necessary and Reviewer re-gates the plan.
- StepInstance, Report generation, AI, permissions, LAN/server, multi-user, Folder Actions, Intake LTR, Projects registry/list, release/settings cleanup, or unrelated residual cleanup.

## May Touch

- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/modules/fee_evaluation/fee_rule_models.py`
- `backend/modules/fee_evaluation/fee_rule_matcher.py`
- `backend/modules/fee_evaluation/fee_rule_seed_loader.py`
- `backend/modules/fee_evaluation/seeds/fee_rules_v2026_06_03.json`
- New focused backend fee default-fill helper under `backend/modules/fee_evaluation/` if it keeps rule evaluation out of API routes.
- `backend/api/routes_confirmed_matrix_fee_draft.py` only if typed response fields need source/review metadata.
- `frontend/src/api/client.ts` only if the response shape changes.
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
- `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
- Focused backend/frontend tests for Fee Evaluation draft rules and preview behavior.
- TASK_351 docs, evidence, and board rows through normal lane flow.

## Must Not Touch

- Matrix parser/import/Confirmed Matrix authority business rules.
- Fee workbook template layout or Office export gateway behavior except compatibility tests.
- Real external Testing Fee Evaluation `.xls` files unless explicitly provided as controlled fixtures.
- Real public-drive files, real LTR workbook files, or user project folders.
- Folder Actions, Intake LTR, Projects registry/list, Project Workbench lifecycle, Matrix Editor unrelated behavior.
- StepInstance, Report generation, AI, permissions, LAN/server, multi-user.
- Release/settings/basic-information residual cleanup.
- `.agents/**`
- `docs/project_management/**`

## Locked Paths

- `backend/modules/test_plan/**`
- `frontend/src/features/matrix-editor/**`
- `frontend/src/features/new-project/**`
- `frontend/src/features/project-workbench/**`
- `frontend/src/pages/ProjectListPage.tsx`
- `backend/application/public_folder_*`
- `backend/application/*ltr*`
- `backend/infrastructure/office/**` except read-only tests if a Reviewer-approved fixture boundary is added later.
- `dist_release/**`
- `packaging/**`
- Real `D:\Test Project/**`, `D:\PublicProject/**`, public-drive roots, and external workbook authority files.

## Acceptance Criteria Draft

- Existing Fee Evaluation draft loading remains based on active Confirmed Matrix authority.
- Deterministic rules auto-fill the target fields without requiring manual entry.
- Review-required rules keep useful partial defaults where safe and set review reasons where values are uncertain.
- LLCR uses the user-confirmed Unit Price Reference tier and does not use the 3 RMB per reading attachment adjustment as the default.
- LLCR calculates total readings when readings/specimen can be derived; otherwise it marks the line review-required.
- Visual Examination defaults Man-hour 0.5, Unit Price 10, Unit Type per photo, Units 3, and Discount 100 percent.
- Sample preparation defaults Man-hour 0.5, Unit Price 50, Unit Type per sample, Units from Matrix group sample quantity, and Discount 100 percent.
- Durability calculates cycle units and Unit Price tier when cycles/specimen can be derived.
- High temperature Life, Thermal Shock, Cycling Temperature & Humidity / Temperature Humidity / Thermal Disturbance, and MFG derive hour/day Units only from explicit text.
- Vibration defaults to 300 per hour while keeping uncertain duration review-required.
- Microsecond discontinuity defaults to 300 per time, Units 1.
- Mechanical Shock and force-family rules follow the confirmed V1 defaults and keep unclear Units/Base Fee review-required.
- Report preparation defaults Man-hour 4, Unit Price 600, Unit Type per report, Units 1, and Discount 100 percent.
- Temperature Rise / T-rise uses the current-tier unit price, Matrix sample quantity, Man-hour 4, and a Base Fee 500 suggestion flagged for manual confirmation.
- Operators can edit all prefilled fields before confirming fee.
- No unrelated workflow, Matrix, workbook authority, or release residual files are included.

## Validation Gate Draft

- Backend focused tests for fee rule loading, matching, and default-fill calculations.
- Backend draft service tests for LLCR, Visual Examination, Vibration, Microsecond discontinuity, Report preparation, Temperature Rise tiers, no-match review behavior, and group sample quantity handling.
- API tests if response metadata changes.
- Frontend focused tests for editable default-filled rows, review-required indicators/reasons, manual override preservation, and read-only behavior.
- Export/persistence regression tests proving edited/default values still serialize through existing Fee Evaluation payloads.
- Suggested commands:
  - `py -m pytest tests/unit/test_confirmed_matrix_fee_draft_service.py tests/unit/test_fee_rule_matcher.py tests/unit/test_fee_rule_seed_loader.py -q`
  - `py -m pytest tests/integration/test_confirmed_matrix_fee_draft_api.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q`
  - `npm test -- FeeEvaluation --run`
  - `npm run build`
  - `git diff --check`

## Merge Gate Draft

- Reviewer plan gate passed by conversational callback.
- User explicitly approved Developer planning-first.
- Developer planning-first must confirm implementation details and update developer evidence.
- Reviewer implementation-readiness passed by conversational callback.
- User explicitly approved implementation authorization and source-of-truth reconciliation.
- Reviewer implementation gate, QA gate, and Integrator packaging/readiness must pass before completion.

## Source-Of-Truth Reconciliation

2026-07-05 Planner reconciliation records the following chain for repository source-of-truth:

- Reviewer plan gate passed read-only and found the planned lane sufficient for Developer planning-first.
- User explicitly approved `TASK_351` entering Developer planning-first.
- Developer stopped before planning-first because board/task/plan/evidence had not yet recorded the Reviewer pass and user approval.
- No product code was changed by the Developer blocked checkpoint.
- At that checkpoint, the task remained implementation-locked and the only authorized role was Developer planning-first.

## Implementation Authorization Reconciliation

2026-07-05 Planner implementation reconciliation records the following chain:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed and updated TASK_351 plan/evidence only.
- Reviewer implementation-readiness passed.
- User explicitly approved TASK_351 reconciliation and Developer implementation.
- This task is now implementation authorized and pending Developer implementation.

Authorization scope:

- Implement Fee Evaluation auto default-fill for Man-hour, Unit Price, Unit Type, Units, Base Fee, Discount, Testing Fee, and review-required/manual confirmation metadata.
- Use user-confirmed V1 rules plus the existing seed JSON.
- Keep `D:/Template/FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls` as template authority reference only; no runtime `.xls` ingestion.
- Preserve operator review/correction before confirmation.
- Preserve locks against runtime external workbook parsing, real workbook/public-drive/folder mutation, Matrix parser/import/Confirmed Matrix authority changes, Fee workbook template redesign beyond regression checks, schema changes without separate re-gate, future StepInstance/Report/AI/permissions/LAN/multi-user/release/settings cleanup, `.agents/**`, and `docs/project_management/**`.

## User-Resolved Discovery Blockers

1. Reference source resolved: `D:/Template/FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls` is the template authority reference, but V1 implementation may proceed using user-confirmed rules plus existing seed JSON without requiring the attachment as a controlled fixture.
2. Temperature Rise Base Fee resolved: prefill `500` and mark the line or field for manual confirmation / review-required.
3. LLCR Units resolved: compute total readings when readings/specimen can be derived; otherwise mark review-required.

## Definition Of Ready

Ready for planned lane review: yes.

Ready for Reviewer plan gate: passed.

Ready for Developer planning-first: yes.

Ready for approved implementation: yes. Developer planning-first completed, Reviewer implementation-readiness passed, user approved implementation, and Planner source-of-truth reconciliation recorded implementation authorization.

## Model Fit Assessment

GPT-5.3-codex is suitable for this task after approval because the work is deterministic rule modeling, typed backend/frontend boundary updates, and focused test expansion. It is not suitable to mutate real workbook/public-drive data or infer new pricing rules beyond the user-confirmed V1 set without separate Reviewer/user approval.

## Integrator Packaging Blocker

Date: 2026-07-05

Integrator gate: blocked.

Blocking finding:

- `backend/modules/fee_evaluation/fee_default_fill.py` is a new package file and is 533 lines, exceeding the AGENTS Python file hard limit of 500 lines.
- `backend/application/confirmed_matrix_fee_draft_service.py` grows from 396 lines in HEAD to 594 lines in the package, also exceeding the same hard limit.
- Functional validation passed, but Integrator cannot accept a package that creates or expands hard-limit violations.

Validation facts before block:

- Reviewer implementation gate passed after the B1 fix moved Sample preparation and Report preparation defaults back to backend ownership.
- QA gate passed with focused backend unit, backend integration, frontend Fee Evaluation, build, compile, diff, trailing whitespace, no-real-workbook, and forbidden-scope checks.
- Candidate package scope was otherwise limited to Fee Evaluation backend default-fill/API/service/seed changes, Fee Evaluation frontend preview/table/model/API typing changes, focused tests, TASK_351 docs/evidence, and `docs/task_board.md` closeout.
- Backend owns Sample preparation and Report preparation through `manual_line_items`; frontend fallback is non-authoritative `Pending` / manual-required display only.
- Runtime external `.xls` parsing, real workbook/public-drive/folder mutation, Matrix parser/import, Confirmed Matrix authority semantics, Fee workbook template redesign, New Project/LTR, ProjectList, Matrix Editor, Settings/LTR, release/desktop/packaging, `.agents/**`, and `docs/project_management/**` residuals remained excluded.
- Remote push was intentionally not performed.

Required next role:

- Developer fix pass to split or reduce the backend default-fill/service implementation below Python file hard limits without expanding TASK_351 scope, then return through Reviewer and QA as needed.

## Integrator Re-Gate Acceptance

Date: 2026-07-05

Integrator gate: accepted.

Acceptance facts:

- Developer split the oversized backend implementation into focused modules.
- Reviewer re-gate passed and confirmed the Integrator hard-limit blocker is closed.
- Split backend files are below the AGENTS 500-line Python hard limit:
  - `backend/modules/fee_evaluation/fee_default_fill.py`
  - `backend/modules/fee_evaluation/fee_default_fill_common.py`
  - `backend/modules/fee_evaluation/fee_default_fill_models.py`
  - `backend/application/confirmed_matrix_fee_draft_service.py`
  - `backend/application/confirmed_matrix_fee_draft_models.py`
  - `backend/application/confirmed_matrix_fee_manual_defaults.py`
- The behavior accepted by Reviewer/QA remains unchanged: backend owns default-fill and manual default rows; frontend consumes backend rows/metadata.
- QA re-gate was not required by Reviewer because the post-QA change was a behavior-preserving backend module split with focused regression rerun.
- Remote push was intentionally not performed.
