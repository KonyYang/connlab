# TASK_357E Test Record / Report Reuse Matrix Step Quantities Developer Evidence

Status: implementation complete - ready for Reviewer implementation gate
Task: `TASK_357E_TEST_RECORD_REPORT_REUSE_MATRIX_STEP_QUANTITIES`
Lane: `test-record-report-reuse-matrix-step-quantities`
Date: 2026-07-08
Role: Developer

## Routing Summary

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active task: `TASK_357E_TEST_RECORD_REPORT_REUSE_MATRIX_STEP_QUANTITIES`.
- Why allowed: Reviewer plan gate passed in `docs/lane_evidence/TASK_357E_test-record-report-reuse-matrix-step-quantities_reviewer.md`, and User/Orchestrator approved Developer planning-first.
- Stop point: Developer planning-first only. Product implementation remains not authorized.

## Source-Of-Truth Note

`docs/task_board.md` still contains older wording that says TASK_357E is planned for Reviewer plan gate and implementation is not authorized. The Reviewer evidence and the current delegation establish the later legal route for Developer planning-first only. This pass does not treat the delegation as implementation authorization and does not write product code.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `$impeccable` product context via `node .agents/skills/impeccable/scripts/load-context.mjs`
- `tasks/TASK_357E_TEST_RECORD_REPORT_REUSE_MATRIX_STEP_QUANTITIES.md`
- `docs/task_357e_test_record_report_reuse_matrix_step_quantities_plan.md`
- `docs/lane_evidence/TASK_357E_test-record-report-reuse-matrix-step-quantities_planner.md`
- `docs/lane_evidence/TASK_357E_test-record-report-reuse-matrix-step-quantities_reviewer.md`
- `docs/lane_evidence/TASK_357A_matrix-quantity-authority-contract_reconciliation_planner.md`
- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_developer.md`
- `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_developer.md`
- `backend/domain/confirmed_matrix_authority_models.py`
- `backend/application/confirmed_matrix_test_record_preview_service.py`
- `backend/application/confirmed_matrix_test_record_document_generation_service.py`
- `backend/application/test_record_fee_dataset_preview_service.py`
- `backend/infrastructure/office/test_record_document_gateway.py`
- `backend/api/routes_confirmed_matrix_test_record_preview.py`
- focused Test Record preview/document tests by targeted read/search
- current `git status --short`

## Repository Facts Confirmed

- `ConfirmedMatrixSnapshot.step_quantities` is available as confirmed Matrix authority data.
- Current Test Record preview builds groups/steps from active confirmed Matrix cells and parsed Step tokens, but it does not attach Step quantity facts.
- Current Test Record preview route exposes only existing step fields and no quantity metadata.
- Current Test Record document generation consumes preview groups, which makes preview projection the right shared source for document generation.
- The Word gateway writes current group/step facts into template rows and has no quantity-specific placement today.
- `TestRecordFeeDatasetPreviewService` is a legacy draft-payload preview path, not the confirmed Matrix authority path.
- No concrete current full Report generation consumer was identified for this lane.

## Planning Decisions Written

Updated `docs/task_357e_test_record_report_reuse_matrix_step_quantities_plan.md` with:

- backend-led shared Step quantity projection strategy;
- proposed projection dataclass shape and status policy;
- Test Record preview/document V1 consumer boundary;
- Report boundary decision: projection/read-model only, no full Report generation;
- exact future May Touch list;
- Must Not Touch / Locked Paths;
- focused backend/API/frontend validation plan;
- package isolation risks.

## Future Implementation Boundary

Recommended implementation shape:

1. Create a focused projection helper under `backend/application/confirmed_matrix_step_quantity_projection.py`.
2. Join projection facts by confirmed group id, confirmed row id, step sequence, and normalized suffix.
3. Extend Test Record preview steps with optional quantity metadata or compact warnings.
4. Reuse preview projection facts in document generation.
5. Touch route DTOs only if metadata is exposed through the API.
6. Keep Report support as a future-ready projection boundary only.

## Locked Scope Observed

No product code was modified by this Developer planning-first pass.

Locked scope remains:

- no Fee Evaluation default-fill or Fee-side quantity editing;
- no Matrix Step setup/storage mutation or schema/migration;
- no Basic Information mutation or final authority consumption;
- no StepInstance/execution persistence;
- no full Report generation;
- no Matrix parser/import changes;
- no LTR workbook/public-drive authority;
- no real workbook/folder/public-drive mutation;
- no release/settings/template residual cleanup;
- no `.agents/**`;
- no `docs/project_management/**`.

## External Residuals Excluded

The current worktree contains external residuals that are not part of TASK_357E:

- `backend/api/dependencies.py` tracked residual.
- Settings/LTR/template helper services and tests.
- backend desktop/release helper files.
- `dist_release/**`, `packaging/**`, release scripts/tests/docs.
- frontend New Project test residual.
- TASK_357A docs/evidence residuals.
- `temp_agents_stash.md`.

They were not modified or cleaned by this pass.

## Validation

- Required TASK_357E docs/evidence existence check passed:
  - `tasks/TASK_357E_TEST_RECORD_REPORT_REUSE_MATRIX_STEP_QUANTITIES.md`
  - `docs/task_357e_test_record_report_reuse_matrix_step_quantities_plan.md`
  - `docs/lane_evidence/TASK_357E_test-record-report-reuse-matrix-step-quantities_planner.md`
  - `docs/lane_evidence/TASK_357E_test-record-report-reuse-matrix-step-quantities_reviewer.md`
  - `docs/lane_evidence/TASK_357E_test-record-report-reuse-matrix-step-quantities_developer.md`
- `git diff --check` for TASK_357E plan/developer evidence passed with LF/CRLF warnings only from existing external files.
- Trailing whitespace scan on TASK_357E plan/developer evidence returned no matches.
- Targeted status confirms this pass changed only TASK_357E plan/developer evidence. Existing external residuals remain visible and excluded.

## Developer Implementation Pass - 2026-07-08

### Authorization Read

- `docs/lane_evidence/TASK_357E_test-record-report-reuse-matrix-step-quantities_reconciliation_planner.md` records `implementation_authorized / ready_for_developer`.
- Scope remains limited to backend shared confirmed Matrix Step quantity projection and Test Record preview/document generation as the V1 concrete consumer.
- Report support remains projection/read-model boundary only; no full Report generation was implemented.

### Changed Files

- `backend/application/confirmed_matrix_step_quantity_projection.py`
- `backend/application/confirmed_matrix_test_record_preview_service.py`
- `backend/api/routes_confirmed_matrix_test_record_preview.py`
- `tests/unit/test_confirmed_matrix_test_record_preview_service.py`
- `tests/unit/test_confirmed_matrix_test_record_document_generation_service.py`
- `tests/integration/test_confirmed_matrix_test_record_preview_api.py`
- `docs/lane_evidence/TASK_357E_test-record-report-reuse-matrix-step-quantities_developer.md`

No frontend product code was changed. No Fee, Matrix Step setup/storage, Basic Information, StepInstance, full Report generation, Matrix parser/import, LTR/public-drive, release/settings, `.agents/**`, or `docs/project_management/**` code was changed by this pass.

### Implementation Summary

- Added `ConfirmedMatrixTestRecordStepQuantity` and a focused projection helper in `backend/application/confirmed_matrix_step_quantity_projection.py`.
- Test Record preview now builds a read-only Step quantity projection from active `ConfirmedMatrixSnapshot.step_quantities`, keyed by confirmed group id, confirmed row id, step sequence, and normalized suffix.
- Preview step quantity statuses:
  - `ready` when matching confirmed Step quantity values can derive `total_readings`;
  - `missing` when an active confirmed Matrix has Step quantity authority records but the parsed preview Step has no matching record;
  - `review_required` when the confirmed Step quantity record is review-required or cannot derive total readings.
- `total_readings` is derived only as `test_points_per_sample * readings_per_point`; `contact_points_per_sample` is carried as metadata only.
- The confirmed Matrix Test Record preview API now exposes optional per-step `quantity` metadata.
- Test Record document generation continues to consume preview groups. Quantity projection is passed through the same preview group/step objects to the writer; no Word template placement or full Report generation was added.

### TDD Red Checks

- `py -m pytest tests/unit/test_confirmed_matrix_test_record_preview_service.py::test_preview_projects_confirmed_step_quantities_for_matching_step tests/unit/test_confirmed_matrix_test_record_preview_service.py::test_preview_marks_missing_step_quantity_when_other_step_quantities_are_present tests/unit/test_confirmed_matrix_test_record_preview_service.py::test_preview_preserves_review_required_step_quantity -q` failed before implementation with `AttributeError: 'ConfirmedMatrixTestRecordPreviewStep' object has no attribute 'quantity'`.
- `py -m pytest tests/integration/test_confirmed_matrix_test_record_preview_api.py::test_confirmed_matrix_test_record_preview_api_returns_step_quantity_metadata -q` failed before implementation with `KeyError: 'quantity'`.
- `py -m pytest tests/unit/test_confirmed_matrix_test_record_document_generation_service.py::test_generation_service_passes_step_quantity_projection_to_writer -q` failed before implementation with `ImportError: cannot import name 'ConfirmedMatrixTestRecordStepQuantity'`.

### Validation

- Red checks above passed after implementation.
- `py -m pytest tests/unit/test_confirmed_matrix_test_record_preview_service.py tests/unit/test_confirmed_matrix_test_record_document_generation_service.py tests/integration/test_confirmed_matrix_test_record_preview_api.py tests/integration/test_confirmed_matrix_test_record_generation_api.py -q` -> 30 passed.
- `py -m py_compile backend/application/confirmed_matrix_step_quantity_projection.py backend/application/confirmed_matrix_test_record_preview_service.py backend/application/confirmed_matrix_test_record_document_generation_service.py backend/api/routes_confirmed_matrix_test_record_preview.py` -> passed.
- `npm run build` -> passed with existing Vite chunk-size warning only.
- `git diff --check` -> passed with LF/CRLF warnings only.
- Trailing whitespace scan on TASK_357E touched files -> no matches.
- Line-count check:
  - `backend/application/confirmed_matrix_step_quantity_projection.py`: 133 lines.
  - `backend/application/confirmed_matrix_test_record_preview_service.py`: 255 lines.
  - `backend/application/confirmed_matrix_test_record_document_generation_service.py`: 451 lines.
  - `backend/api/routes_confirmed_matrix_test_record_preview.py`: 138 lines.
- Forbidden-scope scan found no TASK_357E content diff in Fee Evaluation, Matrix Step setup/storage mutation, Basic Information mutation, StepInstance, full Report generation, Matrix parser/import, LTR/public-drive, `.agents/**`, `docs/project_management/**`, release/package paths, or real-folder/workbook paths.

### External Residuals Still Excluded

Existing unrelated residuals remain visible and were not cleaned or packaged by this pass, including `backend/api/dependencies.py`, `docs/task_board.md`, Settings/LTR/template helper files, backend desktop/release helper files, release packaging paths, frontend New Project test residuals, TASK_357A docs/evidence, and `temp_agents_stash.md`.

## Decision

Completion status: implementation complete - ready for Reviewer implementation gate.

Recommended next role: Reviewer implementation gate.

Blocking summary: none.

Implementation authorization was recorded by Planner reconciliation. Product implementation is complete within the TASK_357E scope and awaits Reviewer gate.
