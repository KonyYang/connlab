# TASK_357D Fee Passive Consumes Matrix Step Quantities Developer Evidence

Status: implementation complete - ready for Reviewer implementation gate
Task: `TASK_357D_FEE_PASSIVE_CONSUMES_MATRIX_STEP_QUANTITIES`
Lane: `fee-passive-consumes-matrix-step-quantities`
Date: 2026-07-08
Role: Developer

## Routing Summary

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active task: `TASK_357D_FEE_PASSIVE_CONSUMES_MATRIX_STEP_QUANTITIES`.
- Why allowed: Reviewer plan gate passed in `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_reviewer.md`, and User/Orchestrator approved Developer planning-first.
- Stop point: Developer planning-first only. Product implementation remains not authorized.

## Source-Of-Truth Note

`docs/task_board.md` still contains older wording that says TASK_357D is planned for Reviewer plan gate and implementation is not authorized. The task, planner evidence, reviewer evidence, and this delegation establish the later legal route for Developer planning-first only. This pass does not treat the delegation as implementation authorization and does not write product code.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `$impeccable` product context via `node .agents/skills/impeccable/scripts/load-context.mjs`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `tasks/TASK_357D_FEE_PASSIVE_CONSUMES_MATRIX_STEP_QUANTITIES.md`
- `docs/task_357d_fee_passive_consumes_matrix_step_quantities_plan.md`
- `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_planner.md`
- `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_reviewer.md`
- `docs/lane_evidence/TASK_351_fee-evaluation-auto-default-fill_developer.md`
- `docs/lane_evidence/TASK_357A_matrix-quantity-authority-contract_reconciliation_planner.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_developer.md`
- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_developer.md`
- `backend/application/confirmed_matrix_fee_draft_models.py`
- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/modules/fee_evaluation/fee_default_fill.py`
- `backend/modules/fee_evaluation/fee_default_fill_common.py`
- `backend/modules/fee_evaluation/fee_default_fill_models.py`
- `backend/domain/confirmed_matrix_authority_models.py`
- focused Fee Evaluation backend/frontend tests and selectors by targeted search
- current `git status --short`

## Repository Facts Confirmed

- `ConfirmedMatrixSnapshot` now includes `step_quantities`.
- `ConfirmedMatrixStepQuantity` carries confirmed group, row, step sequence, suffix, raw token, `test_points_per_sample`, `readings_per_point`, `contact_points_per_sample`, source, review metadata, and confirmation timestamp.
- TASK_357C fixed no-suffix identity normalization and storage uniqueness for draft/confirmed Step quantity records.
- `ConfirmedMatrixFeeDraftService` already builds fee lines from the active confirmed Matrix snapshot, confirmed groups/rows/cells, parsed Step tokens, and group sample quantity.
- `ConfirmedMatrixFeeDraftService` does not yet join `snapshot.step_quantities`.
- `FeeDefaultFillContext` currently has text fields, sample quantity expression, spend time, and step tokens, but no structured Step quantity facts.
- `fee_default_fill.py` currently calculates LLCR/CR readings from text parsing and sample quantity.
- TASK_351 sample preparation and report preparation are backend-owned manual default rows and must stay backend-owned.
- Frontend Fee Evaluation consumes backend rows and field metadata; it should not become a point/reading/contact quantity authoring surface.

## Planning Decisions Written

Updated `docs/task_357d_fee_passive_consumes_matrix_step_quantities_plan.md` with:

- exact future May Touch list narrowed to Fee draft/default-fill backend, optional Fee API/client metadata wiring, Fee Evaluation display tests if metadata changes, and TASK_357D evidence;
- explicit read-only Step quantity lookup keyed by `confirmed_group_id`, `confirmed_row_id`, `step_sequence`, and normalized suffix;
- proposed `FeeStepQuantityContext` carried through `FeeDefaultFillContext`;
- V1 rule mapping limited to LLCR and CR specified-current per-reading rules;
- `readings_per_sample = test_points_per_sample * readings_per_point` where deterministic;
- `contact_points_per_sample` retained as review metadata, not a silent replacement for total readings in V1;
- multiple-Step aggregation policy: same readings-per-sample can calculate; missing, review-required, or differing Step quantities become review-required; no summing in V1;
- TASK_351 text parsing fallback policy: only when structured Step quantity authority is absent/unmapped, never when partially present and ambiguous;
- backend field metadata/UI policy: compact review cues only, no Fee-side quantity setup controls;
- focused backend/frontend/API validation plan;
- package isolation risks from current residuals.

## Future Implementation Boundary

Recommended implementation shape:

1. Build Step quantity context in `ConfirmedMatrixFeeDraftService` from `snapshot.step_quantities` and parsed tokens for the current row/group cell.
2. Extend `FeeDefaultFillContext` with structured Step quantity facts.
3. Update LLCR and CR specified-current default-fill logic to prefer structured Step quantity readings per sample.
4. Preserve existing TASK_351 text parsing when no structured Step quantity authority is available or when the rule is unmapped.
5. Return review-required for missing, review-required, partial, or conflicting Step quantity facts.
6. Optionally expose source/review metadata through existing `field_metadata`; avoid new UI concepts unless required by Reviewer readiness.

## Locked Scope Observed

No product code was modified by this Developer planning-first pass.

Locked scope remains:

- no Fee-side editing of Matrix Step quantities;
- no Matrix Step setup UI or authority mutation;
- no Matrix Step quantity storage schema/migration;
- no Basic Information quantity default mutation or final-authority consumption by Fee;
- no Test Record / Report reuse;
- no StepInstance / execution persistence;
- no Matrix parser/import rules;
- no LTR workbook/public-drive authority;
- no real workbook/folder/public-drive mutation;
- no release/settings/template residual cleanup;
- no `.agents/**`;
- no `docs/project_management/**`.

## External Residuals Excluded

The current worktree contains external residuals that are not part of TASK_357D:

- `backend/api/dependencies.py` tracked residual.
- Settings/LTR/template helper services and tests.
- backend desktop/release helper files.
- `dist_release/**`, `packaging/**`, release scripts/tests/docs.
- frontend New Project test residual.
- TASK_357A docs/evidence residuals.
- `temp_agents_stash.md`.

They were not modified or cleaned by this pass.

## Validation

- Required TASK_357D docs/evidence existence check passed:
  - `tasks/TASK_357D_FEE_PASSIVE_CONSUMES_MATRIX_STEP_QUANTITIES.md`
  - `docs/task_357d_fee_passive_consumes_matrix_step_quantities_plan.md`
  - `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_planner.md`
  - `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_reviewer.md`
  - `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_developer.md`
- `git diff --check --no-index` against an empty temp file for the TASK_357D plan and Developer evidence passed with LF/CRLF warnings only.
- Trailing whitespace scan on the TASK_357D plan and Developer evidence returned no matches.
- Targeted status for TASK_357D plan/developer evidence plus backend/frontend/tests locked areas shows only TASK_357D plan/developer evidence as this pass's intended touched files. Existing external residuals remain visible under `backend/api/dependencies.py`, Settings/LTR/template helpers, backend desktop/release helpers, frontend New Project test residual, and release/settings tests; they were not modified or cleaned by this planning-first pass.

## Developer Implementation Pass - 2026-07-08

### Authorization Read

- `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_reconciliation_planner.md` records implementation authorized / ready for Developer.
- Scope remains limited to Fee Evaluation passive consumption of active `ConfirmedMatrixSnapshot.step_quantities`.
- Locked scope preserved: no Fee-side Step quantity editing, no Matrix Step setup/storage mutation, no Basic Information mutation, no Test Record/Report/StepInstance/Matrix parser/LTR/public-drive/release/settings scope, no `.agents/**`, and no `docs/project_management/**`.

### Changed Files

- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/application/confirmed_matrix_fee_step_quantities.py`
- `backend/modules/fee_evaluation/__init__.py`
- `backend/modules/fee_evaluation/fee_default_fill.py`
- `backend/modules/fee_evaluation/fee_default_fill_models.py`
- `backend/modules/fee_evaluation/fee_step_quantity_defaults.py`
- `tests/unit/test_confirmed_matrix_fee_draft_service.py`
- `tests/unit/test_fee_default_fill.py`
- `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_developer.md`

No frontend product code was changed.

### Implementation Summary

- Added `FeeStepQuantityContext` and threaded structured Step quantity facts through `FeeDefaultFillContext`.
- Joined active confirmed Matrix Step quantities in `ConfirmedMatrixFeeDraftService` by `confirmed_group_id`, `confirmed_row_id`, `step_sequence`, and normalized suffix.
- LLCR and CR specified-current per-reading rules now prefer structured Matrix Step quantities when present.
- `readings_per_sample` is calculated as `test_points_per_sample * readings_per_point`; `contact_points_per_sample` remains metadata only.
- Conservative multiple-Step behavior implemented:
  - same readings-per-sample across matched steps can calculate;
  - missing, review-required, invalid, or conflicting Step quantities produce review-required;
  - text parsing fallback is preserved only when structured Step quantity authority is absent/unmapped.
- Field metadata for structured calculated units/testing fee uses `Matrix Step quantity` source cues through the existing backend-owned metadata path.
- Line-count hard limit preserved after implementation: `confirmed_matrix_fee_draft_service.py` = 495 lines; `fee_default_fill.py` = 491 lines.

### Validation

- TDD red checks before implementation:
  - `py -m pytest tests/unit/test_fee_default_fill.py::test_llcr_prefers_matrix_step_quantity_over_text_readings tests/unit/test_fee_default_fill.py::test_llcr_marks_review_when_matrix_step_quantities_conflict -q` failed because `FeeStepQuantityContext` was not yet implemented.
  - `py -m pytest tests/unit/test_confirmed_matrix_fee_draft_service.py::test_fee_draft_uses_confirmed_step_quantities_for_llcr_units tests/unit/test_confirmed_matrix_fee_draft_service.py::test_fee_draft_marks_conflicting_step_quantities_review_required tests/unit/test_confirmed_matrix_fee_draft_service.py::test_fee_draft_preserves_text_fallback_when_step_quantities_are_absent -q` failed on structured quantity consumption/review behavior; fallback case passed.
- `py -m pytest tests/unit/test_fee_default_fill.py tests/unit/test_confirmed_matrix_fee_draft_service.py tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_matcher.py -q` -> 50 passed.
- `py -m pytest tests/integration/test_confirmed_matrix_fee_draft_api.py tests/integration/test_fee_evaluation_pricing_draft_api.py tests/integration/test_confirmed_fee_version_api.py -q` -> 20 passed.
- `npm test -- FeeEvaluation --run` -> 3 files / 55 tests passed, with existing React `act(...)` warnings only.
- `py -m py_compile backend/application/confirmed_matrix_fee_draft_service.py backend/application/confirmed_matrix_fee_draft_models.py backend/modules/fee_evaluation/fee_default_fill.py backend/modules/fee_evaluation/fee_default_fill_common.py backend/modules/fee_evaluation/fee_default_fill_models.py backend/modules/fee_evaluation/__init__.py` -> passed.
- `npm run build` -> passed with existing Vite chunk-size warning only.
- `git diff --check` -> passed with LF/CRLF warnings only.
- Trailing whitespace scan on TASK_357D touched files -> no matches.
- Forbidden-scope/status scan -> no TASK_357D diff in Matrix parser, Step quantity setup/storage, Basic Information, Test Record, Report, LTR/public-drive, `.agents/**`, `docs/project_management/**`, release/package paths, or frontend Fee-side quantity editing surfaces.

### External Residuals Still Excluded

Existing unrelated residuals remain visible and were not cleaned or packaged by this pass, including `backend/api/dependencies.py`, `docs/task_board.md`, Settings/LTR/template helper files, backend desktop/release helper files, release packaging paths, frontend New Project test residuals, TASK_357A docs/evidence, and `temp_agents_stash.md`.

## Developer Fix Pass - Reviewer B1 - 2026-07-08

### Reviewer Blocker

B1 reported that the implementation left `backend/application/confirmed_matrix_fee_draft_service.py` at 495 lines and `backend/modules/fee_evaluation/fee_default_fill.py` at 491 lines, too close to the AGENTS 500-line hard limit. Reviewer also noted that blank lines between top-level functions had been compressed rather than using clearer module boundaries.

### Fix Summary

- Moved confirmed Matrix Step quantity lookup/context construction out of `confirmed_matrix_fee_draft_service.py` into `backend/application/confirmed_matrix_fee_step_quantities.py`.
- Moved Step-quantity-aware LLCR/CR per-reading default-fill helper logic out of `fee_default_fill.py` into `backend/modules/fee_evaluation/fee_step_quantity_defaults.py`.
- Restored clear top-level function spacing in the core files.
- Preserved TASK_357D behavior and scope: Fee remains a passive consumer; no Matrix Step setup/storage mutation, no Basic Information mutation, no Test Record/Report/StepInstance/Matrix parser/LTR/public-drive/release/settings changes.

### Line-Count Headroom After Fix

- `backend/application/confirmed_matrix_fee_draft_service.py`: 413 lines.
- `backend/application/confirmed_matrix_fee_step_quantities.py`: 127 lines.
- `backend/modules/fee_evaluation/fee_default_fill.py`: 426 lines.
- `backend/modules/fee_evaluation/fee_step_quantity_defaults.py`: 123 lines.
- `backend/modules/fee_evaluation/fee_default_fill_models.py`: 81 lines.

### Fix-Pass Validation

- `py -m pytest tests/unit/test_fee_default_fill.py tests/unit/test_confirmed_matrix_fee_draft_service.py tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_matcher.py -q` -> 50 passed.
- `py -m pytest tests/integration/test_confirmed_matrix_fee_draft_api.py tests/integration/test_fee_evaluation_pricing_draft_api.py tests/integration/test_confirmed_fee_version_api.py -q` -> 20 passed.
- `py -m py_compile backend/application/confirmed_matrix_fee_draft_service.py backend/application/confirmed_matrix_fee_step_quantities.py backend/modules/fee_evaluation/fee_default_fill.py backend/modules/fee_evaluation/fee_step_quantity_defaults.py backend/modules/fee_evaluation/fee_default_fill_models.py backend/modules/fee_evaluation/__init__.py` -> passed.
- `npm test -- FeeEvaluation --run` -> 3 files / 55 tests passed, with existing React `act(...)` warnings only.
- `npm run build` -> passed with existing Vite chunk-size warning only.
- `git diff --check` -> passed with LF/CRLF warnings only.
- Trailing whitespace scan on TASK_357D touched files -> no matches.
- Forbidden-scope scan -> no TASK_357D diff in Matrix parser, Matrix Step setup/storage, Basic Information, Test Record, Report, LTR/public-drive, `.agents/**`, `docs/project_management/**`, release/package paths, or frontend Fee-side quantity editing surfaces.

### Remaining Residuals

Existing unrelated residuals remain excluded and untouched, including `backend/api/dependencies.py`, `docs/task_board.md`, Settings/LTR/template helper files, backend desktop/release helper files, release packaging paths, frontend New Project test residuals, TASK_357A docs/evidence, and `temp_agents_stash.md`.

## Decision

Completion status: implementation fix pass complete - ready for Reviewer re-gate.

Recommended next role: Reviewer implementation re-gate.

Blocking summary: none.

Implementation authorization was recorded by Planner reconciliation. Product implementation and B1 headroom fix are complete within the TASK_357D scope and await Reviewer re-gate.
