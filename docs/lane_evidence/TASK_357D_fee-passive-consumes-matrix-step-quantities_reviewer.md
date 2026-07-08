# TASK_357D Reviewer Evidence - Fee Passive Consumes Matrix Step Quantities

## Plan Gate

- Date: 2026-07-08
- Role: Reviewer
- TASK_ID: `TASK_357D_FEE_PASSIVE_CONSUMES_MATRIX_STEP_QUANTITIES`
- Lane: `fee-passive-consumes-matrix-step-quantities`
- Status: `reviewer_plan_gate_pass`
- Recommended next role: User approval / Developer planning-first
- Blocking summary: none

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_357D_FEE_PASSIVE_CONSUMES_MATRIX_STEP_QUANTITIES.md`
- `docs/task_357d_fee_passive_consumes_matrix_step_quantities_plan.md`
- `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_planner.md`
- `docs/lane_evidence/TASK_357A_matrix-quantity-authority-contract_reconciliation_planner.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_developer.md`
- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_reviewer.md`
- `docs/lane_evidence/TASK_351_fee-evaluation-auto-default-fill_developer.md`
- Current Fee draft/default-fill code references:
  - `backend/application/confirmed_matrix_fee_draft_service.py`
  - `backend/application/confirmed_matrix_fee_draft_models.py`
  - `backend/modules/fee_evaluation/fee_default_fill.py`
  - `backend/modules/fee_evaluation/fee_default_fill_models.py`
  - `backend/modules/fee_evaluation/fee_default_fill_common.py`
- Current confirmed Matrix Step quantity domain facts in `backend/domain/confirmed_matrix_authority_models.py`
- Current `git status --short`

## Review Findings

No blocking findings.

TASK_357D correctly inherits the accepted TASK_357A/B/C contract:

- Matrix Step confirmed quantity records are the quantity authority source.
- Basic Information remains an upstream default source only and is not a final Fee authority.
- Fee Evaluation is scoped as a passive consumer for units/default-fill, not a point/reading/contact quantity entry surface.
- Test Record / Report reuse remains downstream TASK_357E scope.

The plan matches repository facts:

- `ConfirmedMatrixSnapshot` now includes `step_quantities`.
- `ConfirmedMatrixStepQuantity` carries Step identity, `test_points_per_sample`, `readings_per_point`, `contact_points_per_sample`, source, review metadata, and confirmation timestamp.
- Current Fee draft service builds Fee rows from confirmed Matrix groups/rows/cells, parsed Step tokens, and group sample quantity, but does not yet join/use confirmed Step quantities.
- Current `FeeDefaultFillContext` includes Matrix text facts, sample quantity expression, spend time, and Step tokens, but no structured Step quantity facts.
- TASK_351 already established backend-owned deterministic default-fill and field metadata; TASK_357D plans to extend that contract rather than moving authority into frontend UI.

The fallback and review-required contract is plan-gate sufficient:

- Confirmed Step quantities are preferred for affected Fee rules.
- Missing, review-required, ambiguous, or unmapped Step quantities must not invent units.
- Existing TASK_351 text parsing remains compatibility fallback only when Step quantity authority is absent/unmapped and Developer planning-first justifies exact fallback behavior.
- Multiple-Step aggregation is explicitly not hidden: same readings-per-sample may be used, differing readings-per-sample should become review-required unless Developer planning-first proves a safe summed policy.

Scope locks are adequate:

- No Fee-side editing of Step quantities.
- No Matrix Step setup authoring UI or authority mutation.
- No Matrix Step storage schema/migration work.
- No Basic Information mutation or direct final-authority consumption.
- No Test Record / Report reuse.
- No StepInstance / execution persistence.
- No Matrix parser/import changes.
- No LTR workbook/public-drive authority changes.
- No real workbook/folder/public-drive data mutation.
- No release/settings/template residual cleanup.
- `.agents/**` and `docs/project_management/**` remain locked.

The future May Touch list is narrow enough for Developer planning-first:

- backend Fee draft/default-fill service/model/rule files;
- Fee draft API route only if response metadata changes;
- `frontend/src/api/client.ts` only for typed Fee metadata changes;
- Fee Evaluation preview model/table/page only if metadata/display wiring requires it;
- focused backend/frontend tests and lane evidence.

## Validation Run By Reviewer

- `git diff --check -- docs/task_board.md tasks/TASK_357D_FEE_PASSIVE_CONSUMES_MATRIX_STEP_QUANTITIES.md docs/task_357d_fee_passive_consumes_matrix_step_quantities_plan.md docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_planner.md` passed with the existing `docs/task_board.md` LF/CRLF warning only.
- Trailing whitespace scan on TASK_357D docs/board/evidence returned no matches.
- Targeted status showed TASK_357D planning docs/board plus existing external `backend/api/dependencies.py`, Settings/LTR, release/desktop, New Project, and test residuals; no TASK_357D product code is authorized or included in this plan gate.
- Repository fact checks confirmed current Fee default-fill does not yet consume structured Matrix Step quantities and current confirmed Matrix domain now exposes accepted TASK_357C Step quantity records.

## Decision

`reviewer_plan_gate_pass`

Recommended next role/action:

- User approval / Developer planning-first.
- Do not route Developer implementation from this gate.
- Developer planning-first must refine Step quantity lookup, LLCR/CR mapping, multiple-Step aggregation, TASK_351 text fallback policy, API/metadata impact, tests, and package isolation before any implementation authorization.

---

## Implementation-Readiness Gate

- Date: 2026-07-08
- Role: Reviewer
- TASK_ID: `TASK_357D_FEE_PASSIVE_CONSUMES_MATRIX_STEP_QUANTITIES`
- Lane: `fee-passive-consumes-matrix-step-quantities`
- Status: `reviewer_readiness_pass`
- Recommended next role: User approval + Planner/source-of-truth reconciliation before Developer implementation
- Blocking summary: none

## Evidence Read For Readiness

- `AGENTS.md`
- `docs/task_board.md`
- `tasks/TASK_357D_FEE_PASSIVE_CONSUMES_MATRIX_STEP_QUANTITIES.md`
- `docs/task_357d_fee_passive_consumes_matrix_step_quantities_plan.md`
- `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_planner.md`
- `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_reviewer.md`
- `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_developer.md`
- `docs/lane_evidence/TASK_357A_matrix-quantity-authority-contract_reconciliation_planner.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_developer.md`
- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_developer.md`
- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_reviewer.md`
- `docs/lane_evidence/TASK_351_fee-evaluation-auto-default-fill_developer.md`
- Current Fee draft/default-fill code references:
  - `backend/application/confirmed_matrix_fee_draft_service.py`
  - `backend/application/confirmed_matrix_fee_draft_models.py`
  - `backend/modules/fee_evaluation/fee_default_fill.py`
  - `backend/modules/fee_evaluation/fee_default_fill_models.py`
  - `backend/modules/fee_evaluation/fee_default_fill_common.py`
- Current confirmed Matrix Step quantity domain facts in `backend/domain/confirmed_matrix_authority_models.py`
- Current `git status --short`

## Readiness Findings

No blocking findings.

Developer planning-first was docs-only:

- Updated `docs/task_357d_fee_passive_consumes_matrix_step_quantities_plan.md`.
- Created `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_developer.md`.
- No TASK_357D product implementation files were modified by this planning-first pass.
- Visible backend/frontend/tests/release/settings residuals are external and remain excluded.

The future implementation plan is concrete enough for Developer implementation after explicit authorization:

- Step quantity source is clearly defined as the active `ConfirmedMatrixSnapshot.step_quantities` already loaded by `ConfirmedMatrixFeeDraftService`.
- Lookup identity is specific and aligned with TASK_357C: `confirmed_group_id`, `confirmed_row_id`, `step_sequence`, and normalized `step_suffix_note`.
- The plan adds structured `FeeStepQuantityContext` into `FeeDefaultFillContext`, avoiding direct Basic Information reads and keeping Fee passive.
- Rule mapping is appropriately narrow for V1: LLCR and Contact Resistance specified-current per-reading rules only.
- `readings_per_sample` is derived from confirmed Matrix Step `test_points_per_sample * readings_per_point`; `contact_points_per_sample` remains review metadata and is not silently treated as total readings.
- Multiple-Step aggregation is conservative: same readings-per-sample can calculate once, missing/review-required/different values become review-required, and summing is explicitly rejected for V1.
- Fallback policy is safe: TASK_351 text parsing can remain only when structured Step quantity authority is absent/unmapped; partial or ambiguous structured authority must not be mixed with text parsing.
- Fee rows remain editable fee review rows only; no point/reading/contact authoring UI is introduced in Fee Evaluation.
- API/UI metadata impact is bounded to existing `field_metadata` style cues where needed.

Scope locks remain intact:

- No Fee-side editing of Matrix Step quantities.
- No Matrix Step setup UI or authority mutation.
- No Matrix Step quantity storage schema/migration.
- No Basic Information mutation or final-authority consumption by Fee.
- No Test Record / Report reuse.
- No StepInstance / execution persistence.
- No Matrix parser/import changes.
- No LTR workbook/public-drive authority changes.
- No real workbook/folder/public-drive mutation.
- No release/settings/template residual cleanup.
- No `.agents/**` or `docs/project_management/**` changes.

Validation planning is adequate:

- Backend tests cover LLCR/CR mapped structured quantity use, unit-price tiering, units calculation, missing/review-required/different Step quantities, same-value multi-Step aggregation, TASK_351 fallback preservation, unmapped rules, and no Matrix Step write calls.
- API tests are required only if DTO/metadata changes.
- Frontend tests are required only if client/UI metadata display changes.
- General gates include focused pytest, optional Fee frontend tests, `npm run build` if frontend touched, `py_compile`, diff/trailing scans, forbidden-scope scans, and package isolation checks.

Source-of-truth caveat:

- `docs/task_board.md` still records TASK_357D as planned for Reviewer plan gate / implementation not authorized.
- Readiness passes, but Developer implementation must wait for explicit User approval and Planner/source-of-truth reconciliation.

## Validation Run By Reviewer For Readiness

- `git diff --check -- docs/task_357d_fee_passive_consumes_matrix_step_quantities_plan.md docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_developer.md` passed.
- Trailing whitespace scan on TASK_357D plan and Developer evidence returned no matches.
- Targeted status showed TASK_357D plan/developer evidence as untracked docs plus existing external residuals under `backend/api/dependencies.py`, Settings/LTR/template helpers, desktop/release helpers, frontend New Project test residual, and release/settings tests; no TASK_357D product code is included in this planning-first pass.
- Repository fact checks confirmed current Fee default-fill still consumes Matrix text/sample quantity/Step tokens, while accepted TASK_357C confirmed Matrix domain exposes structured Step quantity records.

## Readiness Decision

`reviewer_readiness_pass`

Recommended next role/action:

- User approval + Planner/source-of-truth reconciliation before Developer implementation.
- Do not route Developer implementation directly from this readiness gate.

---

## Implementation Gate

- Date: 2026-07-08
- Role: Reviewer
- TASK_ID: `TASK_357D_FEE_PASSIVE_CONSUMES_MATRIX_STEP_QUANTITIES`
- Lane: `fee-passive-consumes-matrix-step-quantities`
- Status: `reviewer_blocked`
- Recommended next role: Developer fix pass
- Blocking summary: B1 - TASK_357D implementation leaves two core Python files too close to the AGENTS hard line limit.

## Evidence Read For Implementation Gate

- `AGENTS.md`
- `docs/task_board.md`
- `tasks/TASK_357D_FEE_PASSIVE_CONSUMES_MATRIX_STEP_QUANTITIES.md`
- `docs/task_357d_fee_passive_consumes_matrix_step_quantities_plan.md`
- `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_planner.md`
- `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_reviewer.md`
- `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_developer.md`
- `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_reconciliation_planner.md`
- `docs/lane_evidence/TASK_351_fee-evaluation-auto-default-fill_developer.md`
- `docs/lane_evidence/TASK_357A_matrix-quantity-authority-contract_reconciliation_planner.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_developer.md`
- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_reviewer.md`
- TASK_357D actual diff/status
- Fee default-fill backend code/tests
- Confirmed Matrix Step quantity domain/read-model references

## Functional Review

No functional blocking finding was found in the structured quantity behavior.

The implementation matches the approved TASK_357D behavior:

- Fee reads active `ConfirmedMatrixSnapshot.step_quantities`.
- Step quantity matching uses `confirmed_group_id`, `confirmed_row_id`, `step_sequence`, and normalized suffix.
- LLCR and CR specified-current per-reading rules prefer structured Matrix Step quantity facts.
- `readings_per_sample` is derived from `test_points_per_sample * readings_per_point`.
- `contact_points_per_sample` remains metadata and is not silently treated as total readings.
- Missing, review-required, invalid, or conflicting structured Step quantities produce `review_required`.
- Text fallback remains available when structured Step quantity authority is absent for the line.
- Fee remains a passive fee review surface; no Fee-side point/reading/contact authoring UI was added.

Scope remained clean:

- No Matrix Step setup/storage mutation.
- No Basic Information mutation or final-authority consumption.
- No Test Record / Report reuse.
- No StepInstance / execution persistence.
- No Matrix parser/import changes.
- No LTR workbook/public-drive authority changes.
- No real workbook/folder/public-drive mutation.
- No `.agents/**` or `docs/project_management/**` changes.

## Blocking Findings

### B1 - core Python files are too close to the AGENTS hard line limit

Files:

- `backend/application/confirmed_matrix_fee_draft_service.py` - 495 lines
- `backend/modules/fee_evaluation/fee_default_fill.py` - 491 lines

AGENTS sets a Python file hard limit of 500 lines and a target below 300 lines. TASK_357D leaves two core Fee files within 5 and 9 lines of the hard limit. The diff also removes blank lines between several top-level functions in these files, which suggests the package is fitting under the hard limit by compression rather than by maintaining clear module boundaries.

This is an implementation-scoped blocker because Integrator packaging/readiness is likely to reject the package or any tiny follow-up in these files as soon as the limit is crossed. TASK_351 previously hit the same class of hard-limit issue and required a split before acceptance.

Minimum fix required:

- Split or move the new TASK_357D Step-quantity helper logic into a focused module so both core files have meaningful headroom below 500 lines.
- Keep behavior unchanged: Fee remains a passive consumer; no scope expansion.
- Preserve the same focused validations after the split.
- Rerun line-count scan and show the affected files have safe headroom, not just one or two spare lines.

## Validation Run By Reviewer

- Focused backend unit suite passed: `py -m pytest tests/unit/test_fee_default_fill.py tests/unit/test_confirmed_matrix_fee_draft_service.py tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_matcher.py -q` -> `50 passed`.
- Focused backend integration suite passed: `py -m pytest tests/integration/test_confirmed_matrix_fee_draft_api.py tests/integration/test_fee_evaluation_pricing_draft_api.py tests/integration/test_confirmed_fee_version_api.py -q` -> `20 passed`.
- `py -m py_compile backend/application/confirmed_matrix_fee_draft_service.py backend/application/confirmed_matrix_fee_draft_models.py backend/modules/fee_evaluation/fee_default_fill.py backend/modules/fee_evaluation/fee_default_fill_common.py backend/modules/fee_evaluation/fee_default_fill_models.py backend/modules/fee_evaluation/__init__.py` passed.
- Focused frontend suite passed: `npm test -- FeeEvaluation --run` -> `3 files / 55 tests passed`, with existing React `act(...)` warnings only.
- `npm run build` passed with existing Vite chunk-size warning only.
- `git diff --check` returned LF/CRLF normalization warnings only.
- Trailing whitespace scan on TASK_357D touched files returned no matches.
- Forbidden-scope content diff scan returned no TASK_357D content diff in Matrix Editor, Matrix Step setup/storage, Basic Information, Test Record/Report, LTR/public-drive, `.agents/**`, `docs_project_management/**`, release/package, or real-folder/workbook scopes.
- Line-count scan reproduced the B1 risk:
  - `backend/application/confirmed_matrix_fee_draft_service.py`: 495 lines
  - `backend/modules/fee_evaluation/fee_default_fill.py`: 491 lines
  - `backend/modules/fee_evaluation/fee_default_fill_models.py`: 81 lines
  - `backend/modules/fee_evaluation/fee_default_fill_common.py`: 95 lines
  - `backend/modules/fee_evaluation/__init__.py`: 85 lines

## Implementation Gate Decision

`reviewer_blocked`

Recommended next role/action:

- Developer fix pass for B1.
- Do not route QA until the line-count hard-limit proximity blocker is fixed and re-gated.

---

## Implementation Re-Gate For B1 Fix

- Date: 2026-07-08
- Role: Reviewer
- TASK_ID: `TASK_357D_FEE_PASSIVE_CONSUMES_MATRIX_STEP_QUANTITIES`
- Lane: `fee-passive-consumes-matrix-step-quantities`
- Status: `reviewer_pass`
- Recommended next role: QA gate
- Blocking summary: none

## B1 Closure Review

B1 is closed.

Developer split the near-limit implementation into focused helper modules:

- `backend/application/confirmed_matrix_fee_step_quantities.py` owns confirmed Matrix Step quantity lookup and Fee context construction.
- `backend/modules/fee_evaluation/fee_step_quantity_defaults.py` owns Step-quantity-aware LLCR/CR per-reading default-fill behavior.
- `backend/application/confirmed_matrix_fee_draft_service.py` now delegates lookup/context construction instead of holding that logic inline.
- `backend/modules/fee_evaluation/fee_default_fill.py` now delegates per-reading Step quantity behavior instead of holding that logic inline.

Line-count headroom is now acceptable:

- `backend/application/confirmed_matrix_fee_draft_service.py`: 413 lines.
- `backend/application/confirmed_matrix_fee_step_quantities.py`: 127 lines.
- `backend/modules/fee_evaluation/fee_default_fill.py`: 426 lines.
- `backend/modules/fee_evaluation/fee_step_quantity_defaults.py`: 123 lines.
- `backend/modules/fee_evaluation/fee_default_fill_models.py`: 81 lines.

The split preserves the approved TASK_357D behavior:

- Fee remains a passive consumer of active `ConfirmedMatrixSnapshot.step_quantities`.
- LLCR and CR specified-current per-reading rules still prefer structured Matrix Step quantities.
- `readings_per_sample` still comes from `test_points_per_sample * readings_per_point`.
- Missing, review-required, invalid, or conflicting structured Step quantities still produce `review_required`.
- TASK_351 text fallback remains available only when structured Step quantity authority is absent for the line.
- No Fee-side point/reading/contact authoring UI was introduced.

Scope remains clean:

- No Matrix Step setup/storage mutation.
- No Basic Information mutation.
- No Test Record / Report reuse.
- No StepInstance / execution persistence.
- No Matrix parser/import changes.
- No LTR workbook/public-drive authority changes.
- No real workbook/folder/public-drive mutation.
- No `.agents/**` or `docs/project_management/**` changes.

## Validation Run By Reviewer For Re-Gate

- Focused backend unit suite passed: `py -m pytest tests/unit/test_fee_default_fill.py tests/unit/test_confirmed_matrix_fee_draft_service.py tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_matcher.py -q` -> `50 passed`.
- Focused backend integration suite passed: `py -m pytest tests/integration/test_confirmed_matrix_fee_draft_api.py tests/integration/test_fee_evaluation_pricing_draft_api.py tests/integration/test_confirmed_fee_version_api.py -q` -> `20 passed`.
- `py -m py_compile backend/application/confirmed_matrix_fee_draft_service.py backend/application/confirmed_matrix_fee_step_quantities.py backend/modules/fee_evaluation/fee_default_fill.py backend/modules/fee_evaluation/fee_step_quantity_defaults.py backend/modules/fee_evaluation/fee_default_fill_models.py backend/modules/fee_evaluation/__init__.py` passed.
- Focused frontend suite passed from the frontend directory: `npm test -- FeeEvaluation --run` -> `3 files / 55 tests passed`, with existing React `act(...)` warnings only.
- `npm run build` passed from the frontend directory with the existing Vite chunk-size warning only.
- `git diff --check` returned LF/CRLF normalization warnings only.
- Trailing whitespace scan on TASK_357D touched files returned no matches.
- Forbidden-scope content diff scan returned no TASK_357D content diff in Matrix Editor, Matrix Step setup/storage, Basic Information, Test Record/Report, LTR/public-drive, `.agents/**`, `docs/project_management/**`, release/package, or real-folder/workbook scopes.
- Reviewer initially reran `npm test -- FeeEvaluation --run` and `npm run build` from the repository root and both failed because root has no `package.json`; rerun from `frontend/` passed as recorded above.

## Implementation Re-Gate Decision

`reviewer_pass`

Recommended next role/action:

- QA gate.
- Rationale: B1 is closed and functional/scope validations pass, but TASK_357D changes Fee default-fill behavior and should receive QA smoke before Integrator packaging/readiness.
