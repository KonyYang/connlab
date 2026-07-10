# TASK_360A Matrix Contact Measurement Plan Developer Evidence

Status: ready_for_review - B1-B3 Developer fix pass complete, pending Reviewer re-gate
Task: `TASK_360A_MATRIX_CONTACT_MEASUREMENT_PLAN`
Lane: `matrix-contact-measurement-plan`
Date: 2026-07-10
Role: Developer

## Routing Summary

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active task: `TASK_360A_MATRIX_CONTACT_MEASUREMENT_PLAN`.
- Why allowed: Reviewer plan gate passed in `docs/lane_evidence/TASK_360A_matrix-contact-measurement-plan_reviewer.md`, and User/Orchestrator approved Developer planning-first.
- Stop point: Developer planning-first only. Product implementation remains not authorized.

## Source-Of-Truth Note

`docs/task_board.md` still records TASK_360A as planned for Reviewer plan gate / implementation not authorized. Reviewer evidence records `reviewer_plan_gate_pass`, and this delegation records User approval for Developer planning-first. This pass treats that as authorization for docs-only planning-first, not implementation authorization.

Before implementation, source-of-truth should be reconciled to record:

- Reviewer plan gate passed;
- User approved Developer planning-first;
- Developer planning-first complete;
- next legal gate: Reviewer implementation-readiness.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_360A_MATRIX_CONTACT_MEASUREMENT_PLAN.md`
- `docs/task_360a_matrix_contact_measurement_plan.md`
- `docs/lane_evidence/TASK_360A_matrix-contact-measurement-plan_planner.md`
- `docs/lane_evidence/TASK_360A_matrix-contact-measurement-plan_reviewer.md`
- TASK_357A reconciliation evidence
- TASK_357B Developer evidence
- TASK_357C Developer evidence
- TASK_357D Developer evidence
- TASK_357E Developer evidence
- TASK_358A Developer evidence
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixStepQuantityPanel.tsx`
- `frontend/src/features/matrix-editor/matrixStepQuantitySelectors.ts`
- `frontend/src/workbench.css`
- `backend/domain/project_matrix_draft_models.py`
- `backend/domain/confirmed_matrix_authority_models.py`
- `backend/application/matrix_step_quantity_service.py`
- `backend/application/matrix_step_quantity_authority_builder.py`
- `backend/application/confirmed_matrix_authority_service.py`
- `backend/application/matrix_revision_flow_service.py`
- `backend/application/confirmed_matrix_fee_step_quantities.py`
- `backend/modules/fee_evaluation/fee_default_fill_models.py`
- `backend/modules/fee_evaluation/fee_step_quantity_defaults.py`
- Test Record preview/document generation code was inspected by targeted search.
- Current `git status --short`.

## Repository Facts Confirmed

- TASK_357C introduced generic Matrix Step quantity fields:
  - `test_points_per_sample`
  - `readings_per_point`
  - `contact_points_per_sample`
  - derived `total_readings`
- TASK_357D Fee consumption now passively consumes confirmed generic Step quantity facts for LLCR/CR per-reading calculations.
- TASK_357E Test Record preview/API exposes generic Step quantity metadata.
- TASK_358A removed Basic Information quantity defaults from UI and added a compact Matrix Editor selected-group default strip.
- Current `MatrixStepQuantityPanel` still exposes generic `Test points / sample`, `Readings / point`, and `Contact points / sample` inputs.
- Current Matrix main table is followed by `Project Schedule`, and selected-group Step workspace contains the generic Step quantity panel.
- Current Fee code computes readings from generic Step quantities and requires review when quantities are missing/conflicting.
- Current generic Test Record output is separate from the future LLCR/CR specialized workbook.

## Developer Planning Decisions

### Product Direction

- `Contact Measurement Plan` is a Matrix-wide functional card below the main Matrix table.
- The card is adjacent to `Project Schedule`, not nested in it.
- The card owns LLCR/CR contact breakdown planning.
- The existing selected-group generic Step quantity panel remains compatibility/non-contact behavior unless a future implementation migrates or hides it for LLCR/CR targets.
- No modal-first design and no extra card stack.
- Fee remains passive.
- Test Record remains generic; specialized LLCR/CR Excel record workbook is downstream `TASK_360B`.

### LLCR/CR Eligibility

A contact-plan target is produced only when all of these are true:

- the Matrix group is included;
- the Matrix row is not a sample row;
- the normalized row test item is LLCR / Low Level Contact Resistance or CR / Contact Resistance specified-current style;
- the group-row cell is non-empty;
- the cell has at least one parsed Step token.

No target is produced for:

- empty groups;
- excluded groups;
- non-LLCR/CR rows;
- blank cells;
- rows without Step tokens;
- non-eligible Step tokens.

Ambiguous eligibility should become `review_required` instead of inferred contact authority.

### Include / Exclude Policy

- Default Matrix-wide coverage applies to all included eligible targets.
- Operator include/exclude is target-level metadata inside the contact plan.
- Excluding a target requires a short reason and does not delete Matrix row/cell data.
- Common-profile apply only affects included, eligible, blank/unconfirmed targets.
- Explicit Group/Step overrides and confirmed/carry-forward data remain stronger than the common profile.

### Custom Contact V1 Metadata

V1 custom contact family records use:

- stable `family_id`;
- `family_label`;
- `count_per_sample`;
- deterministic `record_label`;
- deterministic `record_prefix`.

Built-in family labels:

- `High Power Pin`
- `Low Power Pin`
- `Signal Pin`

V1 derives `readings_per_sample` as the sum of selected contact family `count_per_sample` values. It does not expose duplicate `test_points_per_sample`, `readings_per_point`, or `contact_points_per_sample` inputs for the contact measurement workflow.

Deterministic label/prefix policy:

- built-in record labels use display labels;
- custom record labels are trimmed and de-duplicated by stable suffix in display order;
- built-in prefixes are `HP`, `LP`, and `SIG`;
- custom prefixes use normalized abbreviation plus display-order fallback such as `CUST1`;
- prefix collisions are resolved deterministically.

## Future Implementation Strategy

1. Add non-destructive draft contact plan and confirmed contact snapshot records.
2. Build deterministic eligibility from current Matrix draft groups/rows/cells and existing Step token parser.
3. Add a backend service for load/preview/save of Matrix contact measurement plan state.
4. Add blank-only common-profile apply and explicit target override handling.
5. Copy resolved contact snapshots into confirmed Matrix authority on Matrix Confirm.
6. Carry forward contact snapshots on stable revision lineage.
7. Update Fee LLCR/CR default-fill to prefer confirmed contact snapshots and consume only `readings_per_sample`.
8. Keep generic Step quantity data for compatibility/non-contact flows.
9. Preserve generic Test Record output and defer specialized workbook generation to TASK_360B.

## Exact Future May Touch

Backend:

- `backend/domain/project_matrix_draft_models.py`
- `backend/domain/confirmed_matrix_authority_models.py`
- `backend/application/matrix_contact_measurement_plan_service.py`
- `backend/application/matrix_contact_measurement_authority_builder.py`
- `backend/application/confirmed_matrix_authority_service.py`
- `backend/application/matrix_revision_flow_service.py`
- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/application/confirmed_matrix_fee_contact_measurements.py`
- `backend/modules/fee_evaluation/fee_contact_measurement_defaults.py`
- `backend/modules/fee_evaluation/fee_default_fill.py`
- `backend/modules/fee_evaluation/fee_default_fill_models.py`
- `backend/infrastructure/storage/models_project_matrix_draft.py`
- `backend/infrastructure/storage/models_confirmed_matrix_authority.py`
- `backend/infrastructure/storage/repositories/project_matrix_draft.py`
- `backend/infrastructure/storage/repositories/confirmed_matrix_authority.py`
- `backend/api/routes_matrix_contact_measurement_plan.py`
- `backend/api/main.py`
- `backend/api/dependencies.py` only for focused dependency wiring.

Frontend:

- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/MatrixContactMeasurementPlanCard.tsx`
- `frontend/src/features/matrix-editor/matrixContactMeasurementPlanSelectors.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/workbench.css`

Tests:

- focused backend unit/integration tests for contact plan service/API, authority builder, confirm/revision copy, and Fee consumption;
- focused frontend Matrix Editor tests;
- focused generic Test Record regression tests.

Docs/evidence:

- TASK_360A task/plan/evidence/board through normal lane flow.

## Must Not Touch / Locked Scope

- No product code in this planning-first pass.
- No implementation authorization from this evidence.
- No Basic Information quantity default UI restoration.
- No destructive deletion or migration of existing generic Step quantity schema/data.
- No LLCR/CR specialized workbook generation.
- No change to existing generic `Test record` button/output semantics.
- No Matrix parser/import changes.
- No StepInstance/execution persistence.
- No Fee-side contact authoring UI.
- No full Report generation.
- No LTR/public-drive/workbook authority changes.
- No real `D:/LabOfficeAuto`, `D:/Test Project`, `D:/PublicProject`, public-drive, or workbook mutation.
- No release/settings/template cleanup.
- No `.agents/**`.
- No `docs/project_management/**`.
- No commit/push.

## Package Isolation Risks

- `backend/api/dependencies.py` is already dirty from external residuals. Future TASK_360A wiring must isolate any dependency hunk.
- Fee files currently have visible external residuals in `git status`; future implementation must separate TASK_360A Fee contact-measurement hunks from those residuals.
- `docs/task_board.md` is already modified externally and should be reconciled by Planner/Integrator, not silently rewritten by this Developer planning-first pass.
- Current TASK_360A task/plan/Planner/Reviewer docs are untracked in this worktree; this pass updates only TASK_360A plan and Developer evidence.

## Validation Plan

Future implementation should run:

- focused backend contact-plan service tests;
- focused backend contact-plan API tests;
- Matrix confirm/revision contact snapshot tests;
- Fee LLCR/CR tests proving `readings_per_sample * group sample qty`, no cross-Step aggregation, and review-required behavior;
- generic Test Record regression tests;
- focused frontend Matrix Editor tests for card placement and blank-only apply;
- `npm run build`;
- `py -m py_compile` for touched backend files;
- `git diff --check`;
- trailing whitespace scan;
- Python line-count scan;
- forbidden-scope and no-real-mutation scans.

## Planning-First Validation

- Required TASK_360A docs/evidence existence check passed:
  - `tasks/TASK_360A_MATRIX_CONTACT_MEASUREMENT_PLAN.md`
  - `docs/task_360a_matrix_contact_measurement_plan.md`
  - `docs/lane_evidence/TASK_360A_matrix-contact-measurement-plan_planner.md`
  - `docs/lane_evidence/TASK_360A_matrix-contact-measurement-plan_reviewer.md`
  - `docs/lane_evidence/TASK_360A_matrix-contact-measurement-plan_developer.md`
- `git diff --check -- docs/task_360a_matrix_contact_measurement_plan.md docs/lane_evidence/TASK_360A_matrix-contact-measurement-plan_developer.md` passed.
- New-file `git diff --no-index --check` against empty files for the TASK_360A plan and Developer evidence passed with LF/CRLF warnings only.
- Trailing whitespace scan on the TASK_360A plan and Developer evidence returned no matches.
- Targeted status confirms this pass changed only TASK_360A planning docs/evidence. Visible backend Fee/test residuals are external and were not modified by this pass.

## Decision

Planning-first completion status: developer planning-first complete.

Planning-first recommended next role: Reviewer implementation-readiness gate.

Planning-first blocking summary: none for Reviewer readiness. Product implementation remained unauthorized at that gate.

## Implementation Pass - 2026-07-10

Status: implementation complete pending Reviewer implementation gate.

Authorization source:

- `docs/lane_evidence/TASK_360A_matrix-contact-measurement-plan_reconciliation_planner.md` records `implementation_authorized`.
- User delegation requested a controlled Developer implementation pass for `TASK_360A_MATRIX_CONTACT_MEASUREMENT_PLAN`.

### Changed Files

TASK_360A implementation files:

- `backend/application/matrix_step_quantity_service.py`
- `frontend/src/features/matrix-editor/MatrixContactMeasurementPlanCard.tsx`
- `frontend/src/features/matrix-editor/matrixContactMeasurementPlanSelectors.ts`
- `frontend/src/features/matrix-editor/matrixContactMeasurementPlanSelectors.test.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/features/matrix-editor/MatrixStepQuantityPanel.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_matrix_step_quantity_service.py`
- `docs/lane_evidence/TASK_360A_matrix-contact-measurement-plan_developer.md`

External residuals still visible in `git status` and excluded from this pass:

- `backend/modules/fee_evaluation/fee_default_fill.py`
- `backend/modules/fee_evaluation/seeds/fee_rules_v2026_06_03.json`
- `docs/task_board.md`
- `tests/unit/test_confirmed_matrix_fee_draft_service.py`
- `tests/unit/test_fee_default_fill.py`
- `tests/unit/test_fee_rule_matcher.py`
- existing untracked TASK_360A Planner/Reviewer/reconciliation/task/plan docs created by lane flow.

### Implementation Summary

- Added a standalone `Contact Measurement Plan` card below the Matrix main table, adjacent to `Project Schedule` and outside the Project Schedule component.
- Added Matrix-wide LLCR and CR specified-current profiles with contact family labels, counts, include/exclude toggles, and deterministic prefixes.
- Added deterministic target selection for LLCR / Low Level Contact Resistance and specified-current/Power-style CR rows.
- Added blank-only common apply:
  - only blank eligible contact targets are filled;
  - existing manual or carried values are not overwritten;
  - derived `readings_per_sample` is stored as the authority value through the existing Matrix Step quantity save path using `source = matrix_contact_plan`.
- Hid eligible LLCR/CR contact targets from the legacy selected-group generic Step quantity panel so operators are not asked to enter duplicate `Test points`, `Readings / point`, or `Contact points` for this workflow.
- Kept the existing confirmed Matrix Step snapshot / Fee passive path intact. The implementation uses a compatibility bridge: the contact card derives `readings_per_sample`, writes it as `test_points_per_sample = readings_per_sample`, `readings_per_point = 1`, and `contact_points_per_sample = readings_per_sample` under `matrix_contact_plan`; confirmed Matrix and Fee continue to consume the confirmed Step snapshot authority without Fee-side authoring.
- Kept generic Test Record and TASK_360B specialized workbook scope untouched.

### Validation Results

- `py -m pytest tests/unit/test_matrix_step_quantity_service.py -q`
  - Passed: 5 tests.
- `py -m pytest tests/unit/test_matrix_step_quantity_service.py tests/unit/test_confirmed_matrix_fee_draft_service.py tests/unit/test_fee_default_fill.py -q`
  - Passed: 38 tests.
- `py -m py_compile backend/application/matrix_step_quantity_service.py`
  - Passed.
- `npm test -- MatrixEditorWorkspace matrixContactMeasurementPlanSelectors --run`
  - Passed: 2 files / 44 tests.
- `npm test -- MatrixEditorWorkspace --run -t "applies Matrix Step quantity defaults"`
  - Passed: 1 selected test.
- `npm run build`
  - Passed with existing Vite chunk-size warning only.
- `git diff --check`
  - Passed with LF/CRLF warnings only.
- Trailing whitespace scan on touched TASK_360A files
  - No matches.
- Line-count check:
  - `backend/application/matrix_step_quantity_service.py`: 423 lines.
  - `frontend/src/features/matrix-editor/MatrixContactMeasurementPlanCard.tsx`: 110 lines.
  - `frontend/src/features/matrix-editor/matrixContactMeasurementPlanSelectors.ts`: 209 lines.
  - `tests/unit/test_matrix_step_quantity_service.py`: 308 lines.
- Forbidden-scope content scan:
  - No TASK_360B workbook generation, Matrix parser/import, StepInstance, Report generation, LTR/public-drive, `.agents/**`, or `docs/project_management/**` implementation hunks were introduced.
  - Existing Basic Information references in `MatrixStepQuantityPanel.tsx` and `matrix_step_quantity_service.py` are pre-existing generic quantity default compatibility labels, not TASK_360A Basic Information scope.

### Known Residuals

- Superseded by the Reviewer B1-B3 fix pass below. Contact family and target policy metadata now persist as typed nested Matrix Step authority data in both draft and confirmed snapshots. TASK_360B remains responsible only for consuming that authority to generate its separate workbook.
- Browser smoke was not run in this Developer thread; no dev server/browser harness was started for this pass. Recommend Reviewer/QA smoke the Matrix Editor page for placement and interaction.

### Recommendation

Recommended next role: Reviewer implementation gate.

Blocking summary: none known for Reviewer gate. Implementation is complete within the controlled compatibility-bridge scope; external Fee seed/rule/test residuals remain excluded.

## Reviewer B1-B3 Fix Pass - 2026-07-10

Status: ready_for_review. This pass addresses only the Reviewer implementation blockers B1, B2, and B3.

### B1: Structured Authority Persistence

- Added typed `MatrixStepContactPlan` and `MatrixStepContactFamily` domain records. The contact plan includes contact kind, coverage status, inclusion, exclusion reason, override flag, derived `readings_per_sample`, and family records with stable id, label, count, deterministic record label/prefix, inclusion, and custom marker.
- Added non-destructive `contact_plan_json` persistence for both draft and confirmed Matrix Step quantity authority records, plus a SQLite migration for existing local tables.
- Extended the existing Matrix Step quantity API contract with typed nested `contact_plan` data. The Step quantity read/save path now round-trips structured target policy and family records without using `review_reason` as a data transport channel.
- Matrix confirm copies the structured contact plan into the immutable confirmed Step quantity snapshot. Repository and API tests prove draft save/load and confirm snapshot round-trips.

### B2: Target Coverage Policy

- The Contact Measurement Plan card now renders each eligible LLCR/CR Group-Step target with user-visible coverage state: Eligible, Applied, Excluded, or Manual override.
- Operators can include or exclude a blank eligible target. Exclusion requires a short reason and persists as target metadata. Blank-only apply skips excluded targets; existing manual/carry-forward values remain manual overrides and are not overwritten.
- Service validation rejects excluded target saves that omit a reason. Excluded target metadata is verified through the API and confirmed snapshot test path.

### B3: Custom Contact Entries

- Added restrained add, edit, and remove controls for custom LLCR/CR contact families. Custom entries require a label, non-negative count, and deterministic uppercase prefix. The backend canonicalizes the record label as `<label> contact` unless the label already ends in `contact`.
- Built-in HP/LP/Signal entries remain defaults. All selected family counts derive the single `readings_per_sample`; the frontend does not restore generic contact quantity inputs.

### Fee Authority Bridge

- Fee remains passive. When a confirmed Step has an included structured contact plan, Fee now prefers the confirmed `readings_per_sample` and treats it as one reading-per-sample quantity for the same Group-Step. The existing generic fields remain only as V1 compatibility data.
- No cross-Step aggregation, Fee-side authoring, generic Test Record changes, or TASK_360B workbook behavior was added.

### Fix-Pass Files

- `backend/domain/matrix_contact_measurement_models.py`
- `backend/application/matrix_contact_plan_validation.py`
- `backend/application/matrix_step_quantity_service.py`
- `backend/application/matrix_step_quantity_authority_builder.py`
- `backend/application/confirmed_matrix_fee_step_quantities.py`
- `backend/api/routes_matrix_step_quantities.py`
- `backend/infrastructure/storage/matrix_contact_measurement_schema_migration.py`
- Matrix draft/confirmed domain models, storage models, repositories, and database initialization for the non-destructive contact payload column.
- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/MatrixContactMeasurementPlanCard.tsx`
- `frontend/src/features/matrix-editor/matrixContactMeasurementPlanSelectors.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- Focused unit, integration, selector, and Matrix Editor tests listed in this evidence.

### Fix-Pass Validation

- `py -m pytest tests/unit/test_matrix_step_quantity_service.py tests/unit/test_matrix_contact_measurement_schema_migration.py tests/unit/test_confirmed_matrix_authority_service.py tests/unit/test_confirmed_matrix_authority_repository.py tests/unit/test_confirmed_matrix_fee_step_quantities.py tests/unit/test_confirmed_matrix_fee_draft_service.py tests/unit/test_fee_default_fill.py tests/integration/test_matrix_step_quantity_api.py -q`
  - Passed: 64 tests.
- `npm test -- MatrixEditorWorkspace matrixContactMeasurementPlanSelectors --run`
  - Passed: 2 files / 45 tests.
- `npm run build`
  - Passed. Existing Vite chunk-size warning remains.
- `py -m py_compile` for all changed TASK_360A backend authority, API, and migration modules
  - Passed.
- `git diff --check`
  - Passed with existing LF/CRLF warnings only.
- Trailing whitespace scan over changed TASK_360A files
  - No matches.
- Python line-count check
  - Largest touched Python file is `backend/application/matrix_step_quantity_service.py` at 404 lines, below the 500-line hard limit.
- Forbidden-scope scan
  - No TASK_360B specialized workbook, generic Test Record, Matrix parser/import, StepInstance, Report, LTR/public-drive, `.agents/**`, or `docs/project_management/**` implementation hunk was found.

### Remaining Residuals

- Browser smoke was not run in this Developer fix thread. Reviewer or QA should smoke the Matrix Editor card placement, target exclusion reason, custom-family edit flow, and disabled/readonly behavior.
- Existing external Fee seed/rule/test residuals, `docs/task_board.md`, and lane governance files remain excluded and untouched by this fix pass.

### Re-Gate Recommendation

Recommended next role: Reviewer implementation re-gate.

Blocking summary: none known. B1 structured persistence and confirmed snapshot copying, B2 persisted target coverage policy, and B3 custom family entry/validation are now covered by focused tests.

## Reviewer Re-Gate B3 Minimal Fix - 2026-07-10

Status: ready_for_review. This pass handles only the custom-family ID collision reported by the Reviewer re-gate.

### Root Cause And Fix

- The old frontend helper generated `custom-${kind}-${currentCustomCount + 1}`. Removing an earlier custom family reduced the active count, so a subsequent add could reuse an ID that still belonged to another active family.
- `addCustomContactFamily` now scans both active profile IDs and IDs already persisted on loaded Matrix Step contact targets. It uses the highest existing `custom-${kind}-<n>` sequence and emits `n + 1`.
- The Matrix Editor passes persisted family IDs from current Step quantity contact plans into the helper. This prevents collisions after draft reload as well as add/remove/add interaction.

### Regression Coverage And Validation

- Selector regression proves add A, add B, remove A, add C produces `custom-llcr-1`, `custom-llcr-2`, `custom-llcr-3`; it also proves an occupied persisted `custom-llcr-3` yields `custom-llcr-4` and the resulting save payload has no duplicate family IDs.
- `npm test -- matrixContactMeasurementPlanSelectors --run`
  - Passed: 1 file / 5 tests.
- `npm test -- MatrixEditorWorkspace matrixContactMeasurementPlanSelectors --run`
  - Passed: 2 files / 46 tests.
- `npm run build`
  - Passed with the existing Vite chunk-size warning only.
- `git diff --check`
  - Passed with existing LF/CRLF warnings only.
- Trailing whitespace scan on the changed selector, Matrix Editor, and Developer evidence files
  - No matches.

### Scope Check

- Changed product logic is limited to `frontend/src/features/matrix-editor/matrixContactMeasurementPlanSelectors.ts` and the existing Matrix Editor call site, with the focused selector test.
- No TASK_360B workbook, generic Test Record, Matrix parser/import, StepInstance, Report, LTR/public-drive, or Fee behavior was modified.

### Re-Gate Recommendation

Recommended next role: Reviewer implementation re-gate.

Blocking summary: none known. The B3 duplicate ID sequence is collision-free for active and persisted/reloaded custom family IDs.
