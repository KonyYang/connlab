# FEE_DEFAULT_FILL_DEPENDENT_FIELD_CORRECTIONS Developer Evidence

Status: `ready_for_reviewer_regate`
Date: 2026-07-24
Task: `FEE_DEFAULT_FILL_DEPENDENT_FIELD_CORRECTIONS`
Lane: `fee-default-fill-dependent-field-corrections`
Parent: `FEE_DEFAULT_FILL_RESIDUAL_PACKAGE_RECONCILIATION`
Role: Developer implementation
Implementation authorization: authorized by final Planner/User reconciliation

## Gate Basis

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package
controlled foundation.

This implementation was allowed because Reviewer scope and
implementation-readiness passed, the User explicitly approved Child 2 product
implementation, and the task/plan/final reconciliation all authorize the exact
typed duration-authority transport and bounded dependent-field changes.

The implementation re-read `AGENTS.md`, `docs/task_board.md`, the Child 2 task
and plan, Planner/dependency/final reconciliation evidence, Reviewer evidence,
and the real source/draft/confirmed/Matrix Editor/Fee authority paths.

## Implemented Contract

- Added typed per-Group duration authority to Source Matrix, editable Matrix
  draft, and Confirmed Matrix domain/storage aggregates.
- Added a dedicated additive SQLite bootstrap for the three duration-authority
  tables. It validates existing affinity/nullability/PK/FK/UNIQUE/named-CHECK
  shape before DDL, creates all missing tables in one transaction, and
  read-verifies the final canonical shape.
- Preserved structured authority through import, selected-only draft
  projection, first Confirm, revision carry-forward/Confirm, Matrix Editor
  source preview/draft/signature/publication, typed API responses, and
  non-visual frontend seed/save/confirm payloads.
- Implemented omission-preserve, explicit-null-clear, and non-null
  full-replacement semantics at the editable draft command boundary.
- Canonicalized non-null `step_suffix_note` and bound source/lineage
  fingerprints without deriving authority from Matrix prose.
- Added exact confirmed authority resolution by owning Group, row, step
  sequence, and suffix. Missing, stale, conflicting, malformed, wrong-Group,
  wrong-row, and missing-lineage cases return typed review-required results.
- Only structured authority can supply Salt Spray and the approved
  `Long-term high temperature zone load` duration. Units use
  `normalized_hours`; no condition/requirement/day text, Step quantity,
  readings, Point Profile, LLCR/CR, saved Fee draft, or other row/Group
  fallback remains.
- Preserved plain Contact Resistance no-LLCR-fallback behavior and Temperature
  Rise sample-unit behavior with pending current.
- Kept accepted Child 1 Base Fee value/metadata untouched. TASK_361L/TASK_363D
  attestation, currentness, reviewed merge, CAS/no-write, and manual-field
  ownership remain the existing authority.

## Reviewer B1 Bounded Fix

Reviewer found that the first implementation routed all six duration-based
rules through the new typed authority helper. That incorrectly changed four
rules outside Child 2 scope.

The bounded fix now uses explicit routing:

- `fee_rule_high_temperature_life` and `fee_rule_salt_spray_nss` continue to
  require typed confirmed duration authority.
- `fee_rule_pre_high_temperature_life`, `fee_rule_thermal_shock`,
  `fee_rule_temperature_humidity`, and `fee_rule_vibration` use their accepted
  legacy text-hour behavior.
- Legacy missing-duration behavior remains `Confirm duration` with Child 1's
  automatic Base Fee `0`.
- Prices remain `15`, `30`, `25`, and `300` respectively; calculated Units,
  Testing Fee, and metadata source retain the accepted legacy contract.

The routing fix is confined to `fee_default_fill.py`,
`fee_default_fill_common.py`, and the existing bounded Child 2 duration test.
No seed, manifest, API, frontend, V2, authority, or TASK_366C composition file
was changed.

## Tests-Only Reconciliation Fix

Planner authorized a product-locked migration of five exact assertion
locations covering six pytest cases. Only those locations were changed:

- High-temperature missing-duration diagnostic in direct default-fill.
- Salt Spray condition text no longer acting as duration authority.
- High-temperature Fee draft condition-text fallback.
- High-temperature one-Group and two-Group rule-resolution expectations.
- High-temperature missing-duration rule-resolution diagnostic.

The updated cases require `review_required`, the typed
`Missing confirmed duration authority` diagnostic, and unset Units/Testing
Fee. Temperature & Humidity and every other legacy rule assertion remain
unchanged.

Tests-only validation:

- Six exact authorized cases: `6 passed`.
- Three complete legacy modules: `113 passed`.
- Child 2 bounded package: `38 passed`.
- Blank-inclusive physical lines remained exactly `912`, `683`, and `301`;
  neither oversized test file increased.
- Product SHA-256 stayed unchanged across the tests-only pass:
  - `fee_default_fill.py`:
    `5B997F5F397EA85E18BE2631410E89CB27467A796B09D59E0F7EB6E6335B12A5`
  - `fee_default_fill_common.py`:
    `A7B747C9C016D9D98EF49F6178BC62F389D7AD76EE5ACF71CCDAB63492D8A8E9`
- Scoped diff-check and UTF-8 trailing-whitespace checks passed.
- Staging remained empty; `backend/api/dependencies.py`, real-data paths, and
  generated-output paths remained untouched.

## Mechanical Splits

The required oversized modules were split without changing their public
orchestration contracts:

- `database.py` delegates general and Matrix migrations.
- Project Matrix draft persistence delegates typed duration payload handling.
- Project Matrix draft routes delegate DTOs and response mapping.
- Matrix revision flow delegates snapshot construction.
- Matrix Editor session delegates contracts, projection, signature, confirmed
  snapshot construction, publication, and draft-state helpers.
- Matrix Editor routes delegate DTOs and response mapping.
- Confirmed Matrix Fee draft service delegates row/group composition to the
  bounded line builder while preserving compatibility re-exports.

All 51 candidate Python modules/tests measured with blank-inclusive
`(Get-Content <path> -Encoding UTF8).Count` are below the 500-line hard limit.
Highest counts:

- `project_matrix_draft.py`: 499
- `source_matrix_import_builder.py`: 498
- `fee_default_fill.py`: 482
- `project_matrix_duration_authority_payload.py`: 474
- `database_general_migrations.py`: 460
- `matrix_editor_session_signature.py`: 451
- `database_matrix_migrations.py`: 442

All new bounded tests are at or below 265 physical lines.

## Focused Validation

Passed:

- Child 2 bounded unit/API/V2/publication package after B1: `38 passed`.
- Source/draft/confirmed repositories, draft save/from-source, first Confirm,
  and revision flow regressions: `40 passed`.
- TASK_363D automatic-build safety, prior-default attestation, Measurement Plan
  transition/rebase, and CR persistence regressions: `29 passed`.
- Accepted Child 1 Base Fee policy: `6 passed`.
- Confirmed Matrix Fee Point Profile/CR no-fallback regression: `9 passed`.
- Frontend duration-authority model regression: `2 passed`.
- Existing Matrix Editor workspace regression: `44 passed`.
- B1 legacy-rule plus Child 1/Base Fee/CR/TASK_363D regression package:
  `52 passed, 3 deselected`. The deselected nodes are the explicitly deferred
  High-temperature condition-text assertions.
- `py -m py_compile` passed for all touched backend modules and all new Python
  tests.
- `npm run build` passed. The only output was the existing Vite chunk-size
  warning.
- Scoped `git diff --check` passed; only existing LF/CRLF notices were emitted.
- UTF-8 trailing-whitespace scan passed across 54 candidate files.
- Physical line-count gate passed for every candidate Python file.
- `git status --short -- data dist_release frontend/dist` returned empty.
- Staged index is empty. No stage, commit, or push was performed.
- No real database, public-drive file, attachment, or generated business
  artifact was accessed.

## External Regression Residual

The authorized stale High/Salt assertion migration is complete and all three
legacy modules are green. One external composition residual remains:

Production Matrix Editor API composition currently inherits an external
TASK_366C residual: `MatrixImportCommitService` is constructed without its
required locked `method_authority` dependency. The Child 2 API publication
test therefore covers first Confirm and revision publication; Matrix Editor
signature/source transport is covered by bounded unit and frontend tests.

No fallback was restored and no assertion outside the five authorized
locations, TASK_366C composition, Fee frontend hydration, seed/manifest,
Child 3, umbrella, or external dirty residual was modified.

## Package Isolation

The worktree contains extensive pre-existing mixed residuals. Child 2 changes
remain confined to its authorized domain/storage/repository/application/API
transport, type-only frontend client, non-visual Matrix Editor preservation,
bounded tests, and this Developer evidence. Mixed files were edited only at
the relevant hunks. No whole-file staging was performed.

## Blocker Summary

No blocker remains in the Child 2 implementation, Reviewer B1 bounded fix, or
the authorized tests-only assertion migration. The external TASK_366C Matrix
Editor dependency-composition residual remains outside this lane and still
blocks QA routing until its owner resolves it.

## Stop Point

Status is `ready_for_reviewer_regate`. The next legal role is Reviewer
implementation re-gate. Do not route QA, Integrator, Child 3, or the parent
umbrella from this Developer pass.

## Matrix Session DTO Forward-Reference Fix

Date: 2026-07-24

Status: `ready_for_reviewer_regate`

Reviewer authorized one bounded Child 2 fix after the accepted TASK_366C
composition correction exposed five Matrix Editor confirm-response failures.
`MatrixEditorSessionConfirmResponse` had moved to
`matrix_editor_session_dtos.py`, but its nested
`ConfirmedMatrixSnapshotResponse` type existed only in the route module's
globals and therefore could not be resolved by Pydantic.

Implementation:

- `matrix_editor_session_dtos.py` now imports the existing response DTO
  directly from `project_matrix_draft_dtos.py`.
- The import graph stays DTO-to-DTO; no route-to-route cycle, copied business
  model, manual `model_rebuild()`, or response-validation relaxation was
  introduced.
- The bounded publication regression now validates both real first-confirm and
  revision-confirm payloads through `MatrixEditorSessionConfirmResponse` and
  verifies that its generated schema contains
  `ConfirmedMatrixSnapshotResponse`.
- The accepted TASK_366C `dependencies.py` composition hunk, Matrix session
  route, and response mapper were read-only in this pass.

TDD and validation:

- RED: the bounded first/revision publication node failed with Pydantic
  `class-not-fully-defined` at `MatrixEditorSessionConfirmResponse.model_validate`.
- GREEN: the exact node passed after the direct DTO import.
- Child 2 bounded unit/API/V2/publication package: `38 passed`.
- TASK_366C import/replace/replay/authority gate: `29 passed`.
- Full `test_matrix_editor_session_api.py`: the five Pydantic forward-reference
  failures are closed. Current result is `10 passed, 1 failed`; the remaining
  node reaches normal response handling and fails only the locked external Fee
  rebase fixture assertion `preserved_count >= 1` (actual `0`). No Base Fee,
  rebase, or fixture behavior was changed in this DTO-only pass.
- `py_compile` passed for the DTO, route, mapper, and bounded publication test.
- UTF-8 physical lines including blanks:
  - `matrix_editor_session_dtos.py`: `260`.
  - `routes_matrix_editor_session.py`: `326`.
  - `matrix_editor_session_response_mappers.py`: `116`.
  - `test_matrix_duration_authority_publication_api.py`: `118`.
- Pre/post SHA-256 remained unchanged for the locked files:
  - `backend/api/dependencies.py`:
    `AF4270423716E9B90925AE6A53435E4C8B65243D2F9FE8024F64824021273D27`.
  - `backend/api/routes_matrix_editor_session.py`:
    `C2F2BB9C81B93435E9A4842D86F84561EAC750626F13E470DC74C8C26E77AEE2`.
  - `backend/api/matrix_editor_session_response_mappers.py`:
    `C3B8BB3A07A53C54EBB639AF9BF69A54DCBB1CE9A6AB8273A92AE67B0F9C3512`.
- Scoped diff/trailing checks passed; staging and real-data/generated-output
  status remained empty. No real database, workbook, public-drive file, or
  generated business artifact was accessed.

The Child 2 DTO forward-reference blocker is closed and ready for Reviewer
implementation re-gate. Do not route directly to QA or Integrator from this
Developer pass.

## Matrix Session Fee-Rule Fixture Context Fix

Date: 2026-07-24

Status: `ready_for_reviewer_regate`

Reviewer authorized a tests-only, line-neutral correction in
`tests/integration/test_matrix_editor_session_api.py`. The active manifest and
runtime rebase context use `fee_rules_v2026_07_17_r6`, while the autosave
fixture seeded and queried a saved pricing draft under the obsolete
`fee_rules_v2026_06_03` identity. The repository correctly refused that
cross-version match, yielding `preserved_count=0`.

Implementation:

- Replaced exactly the two authorized `fee_rules_v2026_06_03` literals with
  `fee_rules_v2026_07_17_r6`: the saved-draft fixture and the promoted-draft
  lookup in the same autosave/restore/confirm/discard node.
- No assertion, pricing/manual fixture value, summary expectation, product
  code, manifest/seed, provenance, CAS, API, or fallback behavior changed.
- The tracked diff is exactly `2 additions / 2 deletions`; the oversized
  legacy test remains exactly `1107` UTF-8 physical lines including blanks.

Validation:

- Exact autosave/restore/confirm/discard node: `1 passed`.
- Complete Matrix Editor session API module: `11 passed`.
- TASK_361L/TASK_363D V2 persistence, contract, repository, attestation,
  safe-rebase, Measurement Plan, CR, and API package: `47 passed`.
- Focused Matrix Fee pending/promotion/rebase package: `46 passed, 1 failed`.
  The remaining failure is a separate locked test file's obsolete r3
  soft-removed-row fixture. Its strict-version mismatch confirms there is no
  cross-version fallback; this pass did not have authorization to migrate it.
- Targeted diff-check and UTF-8 trailing-whitespace checks passed with only
  existing LF/CRLF notices.
- Staging and `data`/`dist_release`/`frontend/dist` status are empty. No real
  database, workbook, public-drive file, attachment, or generated artifact was
  accessed.

The authorized two-literal fixture-context fix is complete. Route only to
Reviewer implementation re-gate; do not route QA or Integrator directly.

## Soft-Removed Row Fixture Context Fix

Date: 2026-07-24

Status: `ready_for_reviewer_regate`

Reviewer authorized one additional tests-only, line-neutral correction in:

`tests/unit/test_matrix_fee_rebase_promotion_service.py::test_soft_removed_hidden_rows_survive_autosave_and_restore_when_reselected`

The node's saved `FeeEvaluationPricingDraftSnapshot` and
`RebaseAfterMatrixAutosaveCommand` both used the obsolete
`fee_rules_v2026_06_03` identity while their basic-fill/default context used
the active `fee_rules_v2026_07_17_r6` contract. Strict repository matching
therefore correctly omitted the inactive source row.

Implementation and isolation:

- Replaced only those two authorized literals with
  `fee_rules_v2026_07_17_r6`.
- No assertion, fixture business value, product rebase/provenance/CAS/API
  behavior, fallback, manifest/seed, other test node, Matrix session fixture,
  Child 3, or umbrella scope changed.
- The tracked diff is exactly `2 additions / 2 deletions`; the legacy test
  remains exactly `871` UTF-8 physical lines including blanks.

Validation:

- Exact soft-removed restore node: `1 passed`.
- Three Matrix Fee rebase service modules: `42 passed`.
- Complete Matrix Editor session API module: `11 passed`.
- TASK_361L/TASK_363D V2 persistence, contract, repository, attestation,
  safe-rebase, Measurement Plan, CR, and API package: `47 passed`.
- `py_compile`, targeted diff-check, and UTF-8 trailing-whitespace checks
  passed with only existing LF/CRLF notices.
- Staging and `data`/`dist_release`/`frontend/dist` status are empty. No real
  database, workbook, public-drive file, attachment, or generated artifact was
  accessed.

The authorized soft-removed fixture-context fix is complete. Route only to
Reviewer implementation re-gate; do not route QA or Integrator directly.
