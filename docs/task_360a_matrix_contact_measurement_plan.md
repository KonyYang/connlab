# TASK_360A Matrix Contact Measurement Plan

## Discovery Summary

`TASK_360A_MATRIX_CONTACT_MEASUREMENT_PLAN` is a planned Matrix Editor lane for a project-wide LLCR/CR Contact Measurement Plan. It replaces the current generic quantity-entry mental model for this business workflow with structured contact breakdown and derived `readings_per_sample`.

The user suggested `TASK_359A`, but the repository already uses `TASK_359A_MATRIX_RESEATING_DEFAULT_DETAILS_HOTFIX`. This plan therefore uses `TASK_360A` and records the numbering adjustment as source-of-truth.

Planner Discovery and the subsequent gates are complete. This reconciliation authorizes the next Developer implementation pass only within this plan's stated boundaries; it does not mark implementation complete.

## Current Phase / Active Task / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Active board state before planning: `TASK_359A_MATRIX_RESEATING_DEFAULT_DETAILS_HOTFIX` complete.
- Role: Planner source-of-truth reconciliation.
- Why allowed: Reviewer plan gate passed; the user approved Developer planning-first; Developer planning-first completed as docs-only; Reviewer implementation-readiness passed; and the user then approved reconciliation plus Developer implementation.

## User Goal

Create a Matrix-wide Contact Measurement Plan for LLCR/CR that applies to all included eligible groups and steps, derives `readings_per_sample` from structured contact family counts, preserves explicit Group/Step overrides, feeds Fee Evaluation passively, and becomes the authority for a later specialized LLCR/CR record workbook lane.

## Confirmed By User

- The plan is Matrix-wide and all-included-groups oriented.
- It is not Basic Information and not a current selected Group local panel.
- UI belongs below the Matrix Editor main table near `Project Schedule`, not inside `Project Schedule`.
- V1 must stop exposing the generic duplicate quantity fields for this business workflow.
- V1 Fee quantity is `readings_per_sample`, derived from structured breakdown such as HP + LP + Signal.
- LLCR/CR Fee lines are already per Group + Step and require no cross-Step aggregation.
- Fee units are `readings_per_sample * group sample qty`.
- Fee does not need contact family details.
- The future specialized LLCR/CR record workbook does need contact family breakdown and must remain separate from generic Test Record output.
- Matrix-wide common plan updates must not silently overwrite confirmed or manually overridden Step values.
- LLCR and CR may use different contact families.
- Confirmed Matrix Step contact snapshot is the authority after Matrix Confirm.
- `TASK_358A` is accepted, and the current generic Step quantity UI is not suitable for this business requirement.

## Confirmed By Repository Evidence

- `docs/task_board.md` records `TASK_357B`, `TASK_357C`, `TASK_357D`, `TASK_357E`, `TASK_358A`, and `TASK_359A` as complete.
- `MatrixStepQuantityPanel` still uses generic quantity labels and a selected-group defaults strip.
- `matrixStepQuantitySelectors` stores generic `test_points_per_sample`, `readings_per_point`, and `contact_points_per_sample`.
- `matrix_step_quantity_service` imports Basic Information draft/confirmed defaults and saves generic Step quantity values.
- Confirmed Matrix authority currently copies generic Step quantity facts.
- Fee default-fill currently reads generic Step quantity facts and derives per-reading units from `total_readings` or `test_points_per_sample * readings_per_point`.
- Test Record projection currently exposes generic Step quantity metadata.
- Existing Test Record generation is generic and separate from the proposed LLCR/CR specialized workbook.

## Planner Inference

- `TASK_360A` should own the product/data authority contract and implementation boundary for structured LLCR/CR contact measurement planning.
- `TASK_360A` may require non-destructive schema additions for draft contact plans and confirmed contact snapshots.
- Existing generic quantity data should remain for compatibility and historical records, but LLCR/CR Fee and downstream specialized workbook behavior should prefer the new confirmed contact snapshot after implementation.
- The old generic Matrix Step quantity panel should be migrated, hidden, or limited so operators are not asked to enter duplicate `Test points`, `Readings / point`, and `Contact points` for LLCR/CR.
- The specialized workbook should be a serial downstream lane because it depends on confirmed contact snapshots.

## Not Yet Confirmed

- Exact `TASK_360B` workbook template mapping from the legacy `.xlsm` file.
- Whether custom contact entries need only a label/count pair in V1 or richer metadata such as pin names/ranges.
- Whether eligible LLCR/CR steps should be detected entirely by normalized test item text or also require an operator include/exclude control.

These are not blocking for planned `TASK_360A`; they must be handled before `TASK_360B` or during Developer planning-first if Reviewer asks.

## Data Authority And Compatibility Proposal

### Draft Contact Plan

Create Matrix-owned draft contact plan state with:

- common LLCR and CR plan definitions;
- selected contact families and counts;
- custom contact entries if needed;
- derived `readings_per_sample`;
- eligible Group-Step coverage;
- explicit per Group-Step overrides.

### Confirmed Snapshot

At Matrix Confirm, copy the resolved contact plan into a confirmed Matrix Step contact snapshot:

- confirmed group identity;
- confirmed row/step identity;
- LLCR/CR kind;
- selected contact breakdown;
- derived `readings_per_sample`;
- source/status metadata.

### Compatibility

- Do not delete existing generic Step quantity tables/data.
- Treat existing generic fields as legacy/non-LLCR compatibility unless an approved later lane removes them.
- Fee/Test Record consumers should not infer LLCR/CR readings from Basic Information or Fee-side fields once confirmed contact snapshots exist.

## UI Placement And Interaction Design

- Add a `Contact measurement plan` card below the main Matrix Editor table.
- Place it beside or near `Project Schedule`; do not embed it in the schedule card.
- Provide project-wide common LLCR/CR controls.
- Show derived `readings / sample`.
- Show eligible included Group-Step rows with source/status and override controls.
- Applying the common plan must be explicit, blank/unconfirmed-only, and must not overwrite manual overrides or confirmed values.
- Hide or remove the generic quantity labels from this LLCR/CR workflow.

## Fee Per-Step Semantics

- Fee Evaluation is passive.
- Each LLCR/CR Fee line reads only its corresponding confirmed Matrix Step `readings_per_sample`.
- Units are `readings_per_sample * group sample qty`.
- No Fee cross-Step aggregation.
- HP/LP/Signal/custom detail remains outside Fee and is reserved for the specialized workbook.
- Missing or review-required contact snapshots should produce review-required/manual fee rows.

## Specialized Excel Record Boundary

`TASK_360B_LLCR_CR_SPECIALIZED_RECORD_WORKBOOK` should be a downstream lane.

It should:

- generate a dedicated LLCR/CR record workbook;
- expand confirmed contact snapshots by Group, Step, contact family, and custom contact entries;
- remain independent from the existing generic Test Record button/output;
- use controlled fixtures/temp files and never mutate the legacy workbook in planning/tests.

`TASK_360A` must not implement this workbook.

## May Touch Draft

- Backend domain models for Matrix draft/confirmed authority contact snapshots.
- Backend storage models/repositories/database migration for non-destructive contact plan tables.
- Backend application services for contact plan preview/save/authority build.
- Matrix confirm/revision/carry-forward services only as needed to copy contact snapshots.
- Backend API routes/dependencies for contact measurement plan.
- `frontend/src/api/client.ts` for typed DTO/helpers if required.
- Matrix Editor feature components/selectors/CSS/tests for the below-table plan card.
- Fee default-fill helpers/tests to consume derived confirmed `readings_per_sample`.
- TASK_360A docs/evidence/board.

## Must Not Touch / Locked Paths

- No product code in this Planner pass.
- No Basic Information quantity default entry restoration.
- No destructive schema/data deletion.
- No specialized LLCR/CR workbook generation in `TASK_360A`.
- No existing generic Test Record output changes.
- No Matrix parser/import changes.
- No StepInstance/execution persistence.
- No Fee-side contact authoring UI.
- No full Report generation.
- No LTR/public-drive/workbook authority changes.
- No real `D:/LabOfficeAuto`, `D:/Test Project`, `D:/PublicProject`, public-drive, or workbook mutation.
- No release/settings cleanup.
- No `.agents/**`, `docs/project_management/**`, or remote push.

## Validation Gate Draft

- Backend unit/integration tests for common plan, derived readings, override preservation, blank-only apply, CR/LLCR different family selection, confirmed snapshot copy, and legacy quantity compatibility.
- Fee tests for per Group-Step units with no cross-Step aggregation.
- Frontend tests for card placement, common plan controls, overrides, derived reading display, and no generic labels in this workflow.
- Regression tests for Project Schedule isolation and existing generic Test Record output.
- `py -m pytest` focused suites.
- `npm test` focused Matrix Editor/Fee tests.
- `npm run build`.
- `git diff --check`, trailing whitespace, forbidden-scope, and no-real-mutation scans.

## Developer Planning-First Refinement

Status: Developer planning-first complete and Reviewer implementation-readiness passed. Product implementation is now authorized after user-approved reconciliation.

### Current Product Direction

- Matrix main table keeps the Matrix as the primary visual surface.
- `Contact Measurement Plan` is a standalone functional card below the Matrix main table, adjacent to `Project Schedule`, not nested in it.
- The card replaces the LLCR/CR business workflow's generic quantity mental model. It must not duplicate `Test points / sample`, `Readings / point`, or `Contact points / sample` as independent operator inputs for eligible LLCR/CR steps.
- Matrix-wide draft profile applies only to blank eligible Group+Step targets.
- Explicit Group/Step overrides retain precedence over the common profile.
- Plan edits never silently overwrite manual overrides, saved Step overrides, confirmed snapshots, or carry-forward authority.
- Fee Evaluation remains passive. Each existing LLCR/CR Group+Step Fee line uses that same Group+Step's confirmed `readings_per_sample * group sample qty`; no cross-Step aggregation.
- Specialized LLCR/CR Excel record workbook generation is downstream `TASK_360B` only. It is separate from the current top `Test record` / generic Test Record output.

### LLCR/CR Eligibility And Include/Exclude Policy

Default coverage is Matrix-wide for all included groups, but target creation is deterministic and scoped:

- A target exists only when the Matrix has:
  - an included Matrix group;
  - a non-sample Matrix row whose normalized test item is LLCR / Low Level Contact Resistance or CR / Contact Resistance specified-current style;
  - a non-empty cell for that group/row;
  - at least one parsed Step token in that cell.
- Empty groups do not produce targets.
- Groups marked excluded in the Matrix do not produce targets.
- Rows with no LLCR/CR match do not produce targets.
- Eligible rows with blank cells for a group do not produce targets for that group.
- Individual parsed Step tokens that are not part of an eligible LLCR/CR row are not contact-plan targets.
- If eligibility is ambiguous, V1 should mark the target `review_required` rather than infer a contact plan.
- Operator include/exclude is allowed only inside the contact plan surface for deterministic edge cases:
  - default `included` for deterministic eligible targets;
  - default `not_applicable` for non-targets, with no visible target row unless a diagnostic view is later approved;
  - operator may exclude a deterministic target with a short reason, but exclusion must be persisted as plan metadata and must not delete the Matrix row/cell.

### Contact Family Metadata Contract

V1 contact family entries must be granular enough for Fee and downstream workbook reuse without reintroducing duplicate quantity fields:

- Built-in family keys:
  - `high_power_pin`
  - `low_power_pin`
  - `signal_pin`
- Built-in family display labels:
  - `High Power Pin`
  - `Low Power Pin`
  - `Signal Pin`
- Custom family entry fields:
  - stable `family_id`;
  - operator `family_label`;
  - `count_per_sample`;
  - deterministic `record_label`;
  - deterministic `record_prefix`.
- V1 does not expose separate `test_points_per_sample`, `readings_per_point`, or `contact_points_per_sample` inputs for the contact workflow.
- `readings_per_sample` is derived as the sum of selected contact family `count_per_sample` values.
- If a count is blank, invalid, negative, or conflicting, the target is `review_required` and Fee receives review-required metadata instead of invented units.
- Deterministic record-label policy:
  - built-ins use their display labels;
  - custom labels are trimmed and de-duplicated by suffixing a stable numeric suffix in display order when needed;
  - prefixes are generated from a normalized label abbreviation and display order, e.g. `HP`, `LP`, `SIG`, `CUST1`;
  - custom prefix collisions are resolved deterministically by appending the display-order index.

### Draft / Confirmed Authority Shape

Future implementation should add focused, non-destructive Matrix-owned records rather than altering the generic Step quantity schema in place:

- Draft common profile:
  - `project_matrix_draft_id`
  - `measurement_kind` (`llcr` or `cr_specified_current`)
  - contact family entries
  - derived `readings_per_sample`
  - status/review metadata
- Draft target override:
  - draft group id, row id, Step sequence, normalized suffix
  - target eligibility status
  - include/exclude status
  - source (`common_profile`, `group_step_override`, `carry_forward`, `manual_required`)
  - contact family entries
  - derived `readings_per_sample`
  - review metadata
- Confirmed contact snapshot:
  - confirmed group id, confirmed row id, Step sequence, normalized suffix
  - `measurement_kind`
  - included/excluded status
  - contact family entries
  - derived `readings_per_sample`
  - source/review metadata
  - confirmed timestamp

Existing generic Step quantity records remain compatibility data. They should not be destructively deleted or migrated in TASK_360A.

### Implementation Strategy

1. Add backend domain/read models for draft common profiles, draft Group+Step targets, and confirmed contact snapshots.
2. Add storage and repository support with narrowly scoped, non-destructive tables.
3. Build eligibility from current Matrix draft rows/groups/cells and existing Step token parsing.
4. Add an application service that can preview/load/save contact plans for a Matrix draft.
5. Implement blank-only common-profile apply:
   - fill only missing eligible target contact families;
   - preserve group/step overrides and confirmed/carry-forward values;
   - never overwrite excluded targets.
6. Extend Matrix confirm/revision/carry-forward to copy resolved contact snapshots.
7. Update Fee LLCR/CR default-fill to prefer confirmed contact snapshots and consume only `readings_per_sample`.
8. Keep generic Test Record preview/document generation unchanged except regression tests proving it is not replaced by the specialized workbook.
9. Keep downstream specialized workbook generation out of scope for TASK_360A.

### Exact Future May Touch

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
- `backend/api/dependencies.py` only for dependency wiring, with package isolation from external residuals.

Frontend:

- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/MatrixContactMeasurementPlanCard.tsx`
- `frontend/src/features/matrix-editor/matrixContactMeasurementPlanSelectors.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/workbench.css`

Tests:

- focused backend unit tests for contact eligibility, common profile, overrides, confirmed copy, carry-forward, and Fee consumption;
- focused backend integration tests for contact plan API and Matrix confirm snapshot;
- focused frontend Matrix Editor tests for card placement and interaction;
- focused Fee tests for per Group+Step `readings_per_sample * sample qty`;
- generic Test Record regression tests.

Docs/evidence:

- TASK_360A plan/evidence/board via normal lane flow.

### Must Not Touch / Locked Paths For Implementation

- Do not restore Basic Information quantity default UI.
- Do not remove existing generic Step quantity schema/data.
- Do not implement specialized LLCR/CR workbook generation.
- Do not change the existing generic `Test record` button/output semantics.
- Do not change Matrix parser/import rules.
- Do not implement StepInstance/execution persistence.
- Do not add Fee-side contact authoring controls.
- Do not implement full Report generation.
- Do not change LTR/public-drive/workbook authority.
- Do not mutate real `D:/LabOfficeAuto`, `D:/Test Project`, `D:/PublicProject`, public-drive, or workbook files.
- Do not clean release/settings/template residuals.
- Do not touch `.agents/**` or `docs/project_management/**`.
- Do not commit or push.

### Focused Validation Plan

- Backend unit:
  - deterministic LLCR/CR eligibility from included group + row + non-empty cell + Step token;
  - empty groups and excluded groups produce no targets;
  - non-LLCR/CR rows produce no targets;
  - blank eligible cells produce no targets;
  - common profile applies only to blank eligible targets;
  - manual Group+Step overrides are preserved;
  - custom contact family label/count/record label/prefix derive deterministically;
  - `readings_per_sample` is sum of selected family counts;
  - invalid/ambiguous counts produce review-required state.
- Backend integration/API:
  - load/preview contact plan for a draft;
  - save common profile and explicit override;
  - Matrix confirm copies confirmed contact snapshots;
  - revision carry-forward preserves eligible contact snapshots where lineage is stable.
- Fee:
  - LLCR uses matching confirmed contact snapshot `readings_per_sample * group sample qty`;
  - CR specified-current uses its own matching snapshot;
  - no cross-Step aggregation;
  - missing/review-required snapshot yields review-required Fee row.
- Frontend:
  - `Contact Measurement Plan` card renders below Matrix table adjacent to `Project Schedule`;
  - card is not nested inside Project Schedule;
  - generic quantity labels are absent from the LLCR/CR contact workflow;
  - common profile apply is blank-only;
  - overrides survive common profile edits;
  - readonly/stale states disable edits without losing display.
- Regression:
  - TASK_358A Matrix Step quantity behavior remains compatible for non-contact workflows;
  - generic Test Record preview/document generation still works and is not replaced;
  - no downstream specialized workbook path is introduced.
- General:
  - focused `py -m pytest`;
  - focused `npm test`;
  - `npm run build`;
  - `git diff --check`;
  - trailing whitespace scan;
  - line-count scan for Python files;
  - forbidden-scope and no-real-mutation scans.

## Merge Gate Draft

- Reviewer plan gate.
- User approval for Developer planning-first.
- Developer planning-first evidence.
- Reviewer implementation-readiness gate.
- User implementation authorization with Planner reconciliation.
- Developer implementation.
- Reviewer implementation gate.
- QA gate.
- Integrator package isolation/readiness.

## Parallel / Serial Assessment

- `TASK_360A` and `TASK_360B` must be serial.
- `TASK_360A` creates the confirmed contact snapshot authority.
- `TASK_360B` consumes that authority for the specialized workbook and should not begin until `TASK_360A` is accepted.

## Definition Of Ready

Satisfied for a complete/accepted lane after Developer implementation, Reviewer pass, QA pass, and Integrator packaging/readiness.

Implementation completed and accepted.

## Recommended Next Role

Orchestrator/User routing decision for the next approved lane. `TASK_360B_LLCR_CR_SPECIALIZED_RECORD_WORKBOOK` remains a future serial lane and must not start without separate approval.

## Integrator Acceptance

- Status: complete/accepted by Integrator.
- Accepted scope: Matrix-wide Contact Measurement Plan authority/storage/API/frontend/tests; structured `contact_plan` family and coverage metadata; persisted include/exclude/reason and override state; confirmed Matrix Step contact snapshot copy; passive Fee `readings_per_sample` bridge; TASK_360A task/plan/evidence/board closeout.
- Excluded scope: downstream TASK_360B workbook generation, generic Test Record semantic changes, Matrix parser/import, StepInstance, Report, LTR/public-drive, release/settings/desktop/packaging residuals, `.agents/**`, `docs/project_management/**`, real workbook/folder mutation, and unrelated Fee seed/rule/test residuals.
- Validation accepted: backend contact plan/service/API/Fee suite `64 passed`; generic Test Record regression `30 passed`; frontend Matrix Editor/selectors `2 files / 46 tests passed`; frontend build passed with existing Vite chunk-size warning only; py_compile passed; diff-check/trailing/line-count/staged whitelist/forbidden-path/no-real-mutation scans passed.
- Browser smoke remains a non-blocking tooling residual due missing bundled Chromium and system Chrome EPERM.
- Remote push intentionally not performed.
