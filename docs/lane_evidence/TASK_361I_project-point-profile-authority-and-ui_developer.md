# TASK_361I Project Point Profile Authority And UI Developer Evidence

Date: 2026-07-14

Role: Developer

Status: ready_for_reviewer_re_gate. Developer implementation is complete; no staging,
commit, push, real database access, or real-file mutation occurred.

## Current Phase / Active Task / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Active task: `TASK_361I_PROJECT_POINT_PROFILE_AUTHORITY_AND_UI`.
- The reconciled task, plan, Planner, Reviewer, and Developer evidence authorize
  this implementation pass. The package remains pending Reviewer implementation
  gate, then QA and Integrator acceptance.

## Implementation Result

- Added the independent additive Point Profile root, revision, and category
  authority tables. SQLite initialization registers the new models and rejects
  incompatible existing Point Profile table/index shapes fail-closed.
- Added canonical category normalization, positive included-count validation,
  deterministic normalized label/prefix duplicate protection, server-issued
  root-scoped monotonic `ppc-N` identities, project-owned id verification,
  revision fingerprints, and stale rejection.
- Added draft/confirmed/superseded lifecycle commands. `confirm` saves the
  canonical draft snapshot and transitions the active revision in one repository
  transaction; a later draft does not replace the confirmed summary.
- Added narrow typed workspace/summary/draft/confirm endpoints. Workspace and
  summary expose only Point Profile state; no Matrix target, coverage, or workbook
  controls are returned by the new boundary.
- Replaced the target-first contact setup surface with the Profile-first direct
  setup editor: starter blank category, add/remove/reorder, optional HP/LP/Signal
  templates, included counts, live points-per-sample total, Save draft, Confirm
  point profile, and Discard.
- Replaced the Matrix compact target-contact summary with a confirmed-only Point
  Profile summary. It shows confirmed revision/categories/total, warns about a
  newer unconfirmed draft, and removes coverage/per-kind/workbook controls from
  this V1 summary.

## Exact Changed Files

- Backend: `backend/api/dependencies.py`, `backend/api/main.py`,
  `backend/api/routes_contact_point_profile.py`,
  `backend/application/contact_point_profile_fingerprint.py`,
  `backend/application/contact_point_profile_legacy_suggestion.py`,
  `backend/application/contact_point_profile_lifecycle_service.py`,
  `backend/application/contact_point_profile_read_service.py`,
  `backend/infrastructure/storage/database.py`,
  `backend/infrastructure/storage/contact_point_profile_schema_migration.py`,
  `backend/infrastructure/storage/models_contact_point_profile.py`, and
  `backend/infrastructure/storage/repositories/contact_point_profile_authority.py`.
- Frontend: `frontend/src/api/client.ts`,
  `frontend/src/contact-measurement-plan.css`,
  `frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.tsx`,
  `projectPointProfileModelTypes.ts`, `projectPointProfileSelectors.ts`,
  `useProjectPointProfileModel.ts`,
  `ContactMeasurementSetupWorkspace.tsx`,
  `ContactMeasurementPlanSummaryCard.tsx`,
  `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, and
  `frontend/src/pages/ProjectContactMeasurementSetupPage.tsx`.
- Focused tests: `tests/unit/test_contact_point_profile_fingerprint.py`,
  `tests/unit/test_contact_point_profile_legacy_suggestion.py`,
  `tests/unit/test_contact_point_profile_lifecycle.py`,
  `tests/unit/test_contact_point_profile_schema.py`,
  `tests/integration/test_contact_point_profile_api.py`,
  `projectPointProfileSelectors.test.ts`,
  `ContactMeasurementSetupWorkspace.test.tsx`,
  `ContactMeasurementPlanSummaryCard.test.tsx`, and the scoped Matrix workspace
  mock update in `MatrixEditorWorkspace.test.tsx`.
- Governance: `docs/task_board.md` and this evidence file. Existing TASK_361F
  operational evidence and TASK_361H screenshots remain external residuals.

## Validation

- `py -m pytest tests/unit/test_contact_point_profile_fingerprint.py tests/unit/test_contact_point_profile_legacy_suggestion.py tests/unit/test_contact_point_profile_schema.py tests/unit/test_contact_point_profile_lifecycle.py tests/integration/test_contact_point_profile_api.py -q`:
  `8 passed`.
- `py -m py_compile` across all TASK_361I backend API/application/storage files:
  passed.
- `npm test -- projectPointProfileSelectors ContactMeasurementPlanSummaryCard ContactMeasurementSetupWorkspace --run`:
  `3 files / 3 tests passed`.
- `npm test -- MatrixEditorWorkspace --run`: `1 file / 47 tests passed`.
- `npm run build`: passed. Existing Vite chunk-size warning remains (`553.33 kB`)
  and is unrelated to this lane.
- `git diff --check`: passed with existing LF/CRLF working-tree warnings only.
- UTF-8 trailing-whitespace scan across new TASK_361I backend/frontend/test files:
  no matches.
- Python line counts: largest new backend module is 143 lines; all new Python
  modules are below the 500-line hard limit.
- Scope/status inspection confirms no changes to Fee, workbook generation,
  generic Test Record/Report, parser/import, LTR/public drive, real databases,
  `.agents/**`, or `docs/project_management/**`. No real DB or file path was
  opened or mutated by this pass.

## Browser Residual

No disposable browser server/harness was started in this implementation pass.
The responsive 514px/Desktop smoke remains a Reviewer/QA browser follow-up; build
and focused DOM regressions cover the rendered Profile-first controls.

## Next Legal Role

Reviewer implementation gate. Review the additive migration shape, stale/atomic
lifecycle, no-target direct setup path, project-owned `ppc-N` identity guard,
confirmed-only Matrix summary, typed API/client boundary, and package isolation
before QA or Integrator routing.

## Reviewer B1-B4 Fix Pass (2026-07-14)

- B1: strengthened the SQLite Point Profile preflight to compare affinity,
  nullability, primary-key position, foreign-key local/referred columns and
  actions, required table unique shapes, named checks, and every required partial
  unique index. `init_db()` now validates a partially existing profile schema before
  `create_all`, so malformed existing profile tables fail with `authority_corrupt`
  without profile DDL or authority writes. Disposable malformed-table startup
  coverage verifies the boundary.
- B2: the next local draft hydrates confirmed categories in the setup model. The
  lifecycle permits retained ids only from the editable snapshot, or its active
  confirmed parent when creating that draft, so deleted historical `ppc-N` ids cannot
  be resurrected. Prefix fallback is resolved only after backend id issuance, making
  an unparseable new `ppc-24` persist as `C24`.
- B3: Matrix Editor now uses the narrow `fetchProjectPointProfileSummary()` model;
  it no longer transports the editable workspace into its compact summary. Only the
  confirmed revision/categories/total and `has_unconfirmed_draft` warning are read.
- B4: category counts retain their raw input until validation. Decimal, empty,
  negative, and non-integer values cannot enter the typed command; the Prefix field
  now lives under an accessible per-row `More` disclosure.

### Fix-Pass Validation

- Backend Point Profile focused suite: `10 passed`.
- Frontend focused Profile + Matrix suite: `4 files / 51 tests passed`.
- `npm run build`: passed, with the existing Vite chunk-size warning only.
- Candidate backend `py_compile`: passed.
- `git diff --check`: passed with existing LF/CRLF warnings only; trailing-whitespace
  scans are clean. No staging, commit, push, real database, or real file access.

Next legal role remains: Reviewer implementation re-gate only.

## Reviewer B1R/B2R/B4R Fix Pass (2026-07-14)

- B1R: existing profile tables are now validated independently before `create_all`.
  Compatible root-only or root-plus-revision states may be completed by the same
  additive startup; malformed existing tables fail before missing-object DDL. Named
  checks require both their constraint name and canonical expression.
- B2R: the frontend records a confirmed/draft baseline on hydrate and reload, so
  Discard restores the current authority categories rather than a blank starter.
- B4R: raw count strings are parsed only by a strict positive safe-integer parser;
  `"4"` becomes payload number `4`, while decimals, signed values, exponent forms,
  whitespace, zero, and unsafe values remain invalid and issue no command.

Validation: Point Profile backend focus `10 passed`; Profile + Matrix frontend focus
`4 files / 51 tests passed`; build and py_compile passed. No staging, commit, push,
or real DB/file access. Next legal role: Reviewer implementation re-gate.

## Reviewer B1R2 Bootstrap Fix Pass (2026-07-14)

- Removed Point Profile tables from the general `Base.metadata.create_all()` set.
  The dedicated SQLite bootstrap now validates every existing profile table before
  opening `BEGIN IMMEDIATE`, creates absent Point Profile tables in FK order inside
  that one transaction, rolls back a bootstrap exception, and revalidates the final
  canonical shape. Other registered model initialization remains unchanged.
- Compatible partial table states are preflighted per existing table; an incompatible
  named check still fails before any missing Point Profile object is created.
- Baseline and strict-count model changes from B2R/B4R remain local to the profile
  editor and were not expanded into the already-closed summary boundary.

Validation: backend Point Profile suite `10 passed`; py_compile passed; previous
focused Profile + Matrix suite `4 files / 51 tests` and build remain green. No real
database/file access, staging, commit, or push. Next legal role: Reviewer
implementation re-gate.

## Reviewer B1R3 Checkpoint (2026-07-14)

Implemented transaction-visible final verification before `COMMIT` in the dedicated
SQLite bootstrap. The bootstrap now rolls back newly created Point Profile tables when
either DDL or in-transaction canonical verification raises. Added and passed these
disposable test nodes in `tests/unit/test_contact_point_profile_schema.py`:

- `test_root_only_partial_profile_schema_bootstraps_and_is_idempotent`
- `test_root_and_revision_partial_profile_schema_bootstraps_and_is_idempotent`
- `test_injected_create_failure_rolls_back_new_profile_tables`
- `test_transaction_visible_final_verify_failure_rolls_back_new_profile_tables`

Also extended `projectPointProfileSelectors.test.ts` with strict raw-count parsing:
`"4"` contributes `4`; decimal, blank, whitespace, zero, sign, exponent, trailing,
and unsafe forms are invalid. Current runs: backend Point Profile suite `14 passed`;
frontend focused suite `4 files / 52 tests passed`.

This checkpoint is **not ready for Reviewer re-gate**: the exact named-CHECK
same-expression/missing-name fixture, locked-writer fixture, and the requested
component-level Discard/payload node tests remain to be added. They are not claimed as
passing. No real DB/file access, staging, commit, or push occurred.

## Reviewer B1R3 Mandatory Regression Completion (2026-07-14)

The Point Profile bootstrap keeps its final canonical verification inside the same
`BEGIN IMMEDIATE` transaction as the missing-object DDL. Verification succeeds before
`COMMIT`; a create or transaction-visible verification failure rolls back every new
Point Profile object. The model file was also restored to its intended single hook
implementation after an interrupted local patch left a duplicate fragment; no new
product behavior was added beyond the already-approved confirmed-baseline Discard and
strict count command boundary.

Mandatory regression nodes, all passing:

- A: `tests/unit/test_contact_point_profile_schema.py::test_root_only_partial_profile_schema_bootstraps_and_is_idempotent`
  verifies root-only existing DB through real `init_db()`, canonical completion, and
  idempotent second startup.
- B: `tests/unit/test_contact_point_profile_schema.py::test_root_and_revision_partial_profile_schema_bootstraps_and_is_idempotent`
  verifies root-plus-revision completion and idempotency.
- C: `tests/unit/test_contact_point_profile_schema.py::test_named_revision_check_mismatch_fails_before_missing_category_ddl[ck_profile_wrong_name]`
  and `tests/unit/test_contact_point_profile_schema.py::test_named_revision_check_mismatch_fails_before_missing_category_ddl[]`
  verify same-expression wrong-name and unnamed/missing named CHECK cases fail
  `authority_corrupt` before category DDL, with `sqlite_master` unchanged.
- D: `tests/unit/test_contact_point_profile_schema.py::test_injected_create_failure_rolls_back_new_profile_tables`
  verifies injected DDL failure leaves zero partial Point Profile tables.
- E: `tests/unit/test_contact_point_profile_schema.py::test_transaction_visible_final_verify_failure_rolls_back_new_profile_tables`
  verifies final verification failure rolls back before commit.
- F: `tests/unit/test_contact_point_profile_schema.py::test_locked_writer_fails_closed_then_bootstraps_after_release`
  verifies a disposable SQLite writer lock fails closed with zero DDL, then succeeds
  after release.
- G: `frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.test.tsx::useProjectPointProfileModel > restores the confirmed baseline after local delete and saves every confirmed row`
  verifies confirmed order/count/prefix hydration, local edit/delete, Discard restore,
  and a complete subsequent save payload without deletion.
- H: `frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.test.tsx::useProjectPointProfileModel > serializes raw whole-number input as a number and includes it in the live total`
  verifies raw `"4"` gives live total `4` and save payload numeric `4`.
- I: `frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.test.tsx::useProjectPointProfileModel > keeps invalid raw count formats from writing`
  verifies decimal, blank, whitespace, nonpositive, exponent, sign, trailing, and
  overflow forms do not call the draft API.

Final validation:

- The seven explicit schema nodes A-F: `7 passed`.
- Full Point Profile backend focus (`fingerprint`, legacy suggestion, schema,
  lifecycle, API): `17 passed`.
- Profile + Matrix frontend focus including the model regressions: `5 files / 55 tests
  passed`.
- Candidate backend `py_compile`: passed.
- `npm run build`: passed; existing Vite chunk-size warning (`553.95 kB`) remains.
- No browser smoke was run because this bounded regression pass used disposable
  SQLite/DOM fixtures only; no real database or file was opened or modified.

The new Python modules remain under the 500-line hard limit. `database.py` is an
existing 925-line shared initializer in `HEAD`; this task only adds the narrow Point
Profile bootstrap ordering and does not attempt an out-of-scope refactor. No staging,
commit, or push occurred.

Next legal role: Reviewer implementation re-gate only.
