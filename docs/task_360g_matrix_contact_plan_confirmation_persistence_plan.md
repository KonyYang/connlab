# TASK_360G Matrix Contact Plan Confirmation Persistence Plan

## Discovery Summary

TASK_360G corrects a session-confirm authority hole exposed by a live revision-draft workflow. The saved Contact Measurement Plan exists in the draft, but Matrix Editor reports `no_change` before inspecting it and its alternate snapshot builder omits Step quantities. The result is an unchanged active snapshot, so confirmed-only Fee and specialized workbook consumers correctly see no included targets.

## Current Phase / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Role: Integrator packaging/readiness.
- Upstream: TASK_360A/B and TASK_360C are accepted; TASK_360C acceptance is recorded in `5c1b10ab1aa85d478903d7e53947c23a6c7c9056`.
- Why allowed: Developer implementation and focused-validation fix pass completed; Reviewer B1 re-gate passed; QA gate passed; Integrator package isolation is the next legal gate.

## Facts

### Confirmed By User

- Draft contact plan save/apply works and shows Applied target coverage.
- Reconfirm does not yield a confirmed specialized-workbook target; no workbook is produced.
- Saved profile values do not reappear in the common plan controls.

### Confirmed By Repository

- Session `no_change` signatures omit Step quantities/contact plans.
- Session snapshot builder omits `step_quantities`; direct authority and revision-flow builders correctly include them.
- Repositories already persist draft and confirmed `contact_plan_json`.
- Common profile state is transient and has no hydration path from loaded Step-quantity items.

### Planner Decision

Use one focused backend/frontend lane. No schema, API, client, or consumer contract change is needed.

## Design

### Canonical Confirmation Comparison

Keep existing Matrix payload signature semantics, then add a pure canonical Step-quantity authority comparison in a new focused backend helper rather than extending the already 1,845-line session service. It maps draft and confirmed records by selected Group order, non-sample row order, Step sequence, and a trimmed null-to-empty suffix. It includes:

- `test_points_per_sample`, `readings_per_point`, `contact_points_per_sample`, source, review-required state, and normalized review reason;
- contact-plan kind, coverage status, inclusion, exclusion reason, override state, and derived `readings_per_sample`;
- ordered contact family records: family id, label, count per sample, record prefix, inclusion, and custom flag.

It excludes generated draft/confirmed ids, matrix ids, timestamps, and persistence ordering. Input ordering is normalized by the authority identity, while family order remains meaningful. `no_change` requires both the existing Matrix payload signature and the canonical quantity/contact-plan projection to match.

Before returning `no_change` for an active Matrix with an expected revision draft, load and validate that saved draft. A missing expected revision draft preserves the current Matrix-only no-change outcome. When one exists, compare its canonical projection with the active confirmed projection. If quantities differ, use the existing saved-revision publish path. The session snapshot builder must call existing `build_confirmed_step_quantities()` after it maps confirmed group/row ids, then attach the returned structured records to the new snapshot. It must not duplicate field copying or write repositories directly.

### Common Profile Hydration

Add a pure selector that reads completed draft quantity loads. For each contact kind, it hydrates the common profile only when every included, non-override target with a persisted plan has the same canonical ordered family definition and compatible derived readings. It converts those API family records into the existing editable profile shape without generating new ids. If no eligible persisted plan exists, retain defaults. If plans diverge, retain target-level authority and return a concise review result instead of copying an arbitrary target into the common form. The workspace applies hydration only at successful Step-quantity load completion, never on every render or after local family edits, so it cannot overwrite unsaved operator edits.

## Developer Planning-First Implementation Sequence

1. Create `matrix_step_quantity_authority_comparison.py` as a pure, bounded helper with canonical draft and confirmed projection functions plus an equality predicate.
2. Update `MatrixEditorSessionService.confirm_session()` so that Matrix-equal active revisions with an expected saved draft load that draft before `no_change`; only true Matrix-and-quantity equivalence returns `no_change`.
3. Update `_build_confirmed_snapshot_from_session_draft()` to reuse `build_confirmed_step_quantities()` and attach the structured result to the confirmed snapshot.
4. Add a selector-only uniform-profile hydration result. On successful Step-quantity load, apply its profile only for uniform persisted plans and surface short review copy for divergence without changing target plans.
5. Keep existing Confirm Matrix, Fee promotion, TASK_360B preview/generate, and generic Test Record code unchanged; they remain regressions proving the new confirmed snapshot is the only downstream source.

## May Touch

- `backend/application/matrix_editor_session_service.py`
- `backend/application/matrix_step_quantity_authority_comparison.py`
- `tests/unit/test_matrix_step_quantity_authority_comparison.py`
- `tests/unit/test_matrix_editor_session_service.py`
- `tests/integration/test_matrix_editor_session_api.py`
- `frontend/src/features/matrix-editor/matrixContactMeasurementPlanSelectors.ts`
- `frontend/src/features/matrix-editor/matrixContactMeasurementPlanSelectors.test.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- TASK_360G lane docs/evidence/board through normal gate flow

## Must Not Touch / Locked Paths

- No schema/models/repositories/migrations/routes/API client.
- No Fee default-fill logic, TASK_360B workbook projection/gateway/artifacts, generic Test Record, parser/import, Basic Information, LTR/public-drive, StepInstance, Report, release/settings, real files, `.agents/**`, or `docs/project_management/**`.

## Acceptance And Validation

1. Pure helper tests prove differing generated ids/timestamps/storage ordering remain equal, while a scalar, inclusion/coverage, derived-readings, or ordered-family difference is authoritative and unequal.
2. Session-service test proves a Matrix-equal contact-plan-only revision publishes `n + 1`, carries the complete structured family data into the confirmed snapshot, and leaves the previous active snapshot superseded only after publish.
3. Session API test saves Step quantities through the existing draft flow, confirms, then reads active authority to assert family counts and `readings_per_sample` survived. A truly identical saved revision remains `no_change`.
4. Selector tests prove uniform LLCR/CR target plans hydrate common profiles; absent plans retain defaults; divergent or override plans do not collapse and report review-required state.
5. Workspace tests prove hydration runs after a successful quantity load, preserves local edits until an explicit reload, and keeps target coverage unchanged.
6. Existing Fee and TASK_360B regression tests prove downstream consumers see new readings only after reconfirmation. Their implementation files are not modified.
7. Real controlled smoke: open revision draft, save LLCR `4/5/24` and CR `33`, apply/save, reconfirm, verify active confirmed preview has included targets, then generate/download one managed workbook. Never use LTR/public-drive paths.
8. Run focused `pytest`, focused `npm test`, `npm run build`, `py_compile`, line-count check for `matrix_editor_session_service.py`, `git diff --check`, trailing whitespace, forbidden-scope, package-isolation, and no-real-mutation scans.

## Definition of Ready / Dependencies

Reviewer plan re-gate, docs-only Developer planning-first, Reviewer implementation-readiness, Developer implementation, focused-validation fix pass, Reviewer B1 re-gate, QA gate, and Integrator package isolation are complete. TASK_360C remains an accepted upstream basis. TASK_360G is complete / accepted.

## Integrator Closeout

- Integrator gate: accepted.
- Accepted package: canonical Step quantity/contact-plan comparison helper, Matrix Editor session-confirm persistence changes, existing confirmed Step-quantity builder reuse, uniform-only common profile hydration, focused backend/frontend tests, TASK_360G task/plan/evidence, and TASK_360G board closeout.
- Excluded residuals: Fee rule/seed/test work, parser hotfix work, `frontend/src/workbench.css`, `tests/unit/test_frontend_shell_files.py`, `docs/superpowers/`, future TASK_360D-L files, schema/model/repository/migration/API-client changes, TASK_360B implementation changes, generic Test Record, Matrix parser/import, LTR/public-drive, StepInstance, Report, real workbook/folder paths, `.agents/**`, and `docs/project_management/**`.
- Remote push intentionally not performed.
