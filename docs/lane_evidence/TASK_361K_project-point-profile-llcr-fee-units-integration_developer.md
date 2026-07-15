# TASK_361K Developer Planning-First Evidence

Date: 2026-07-15

Role: Developer

Task: `TASK_361K_PROJECT_POINT_PROFILE_LLCR_FEE_UNITS_INTEGRATION`

Lane: `project-point-profile-llcr-fee-units-integration`

Status: `ready_for_review / pending_reviewer_implementation_gate`

## Authorization And Scope

The initial planning-first pass was docs-only. The later user-approved Developer
implementation pass added only the authorized read-only Fee consumer integration,
focused disposable tests, and this evidence update. No schema, frontend/API client,
Fee pricing/rule/UI, workbook consumer behavior, real database/file access, staging,
commit, or push was performed.

Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled
foundation`.

Active task: `TASK_361K_PROJECT_POINT_PROFILE_LLCR_FEE_UNITS_INTEGRATION`.

Why allowed: the Planner/User reconciliation evidence records the Reviewer
implementation-readiness re-gate and explicit implementation approval for TASK_361K.

## Repository Facts Re-Verified

- `ConfirmedMatrixFeeDraftService` obtains an effective confirmed Measurement Plan,
  then `_build_group_lines()` calls `build_step_quantity_contexts()` before default
  fill.
- The existing context builder emits `Confirm Matrix Step quantity` when no
  `ConfirmedMatrixStepQuantity` matches a parsed token. A Profile branch added after
  that result would violate TASK_361K.
- `ContactMeasurementPlanConfirmedConsumerAdapter` already exposes exact target
  lineage, `not_started`/`disabled` rollback states, and active-root review states.
- `build_reading_result()` already computes `sample quantity * readings per sample`,
  preserves the `<=20`/`>20` LLCR tier, and returns `Confirm sample quantity` for an
  invalid group quantity.
- Point Profile storage already provides a root, active confirmed revision, ordered
  categories, revision sequence/fingerprint, and expression-derived count. Its
  existing workspace read service is UI-shaped, so a narrow consumer adapter must read
  the repository directly rather than reuse a mutable UI projection.
- Normal Fee preview composition injects the Measurement Plan adapter, while direct
  export, required forms, child-process export, and rebase default construction have
  separate `ConfirmedMatrixFeeDraftService` construction paths. All must receive the
  same future read-only Profile adapter.

## Frozen Implementation Strategy

1. Add a read-only confirmed Point Profile consumer adapter with typed confirmed,
   missing/draft/stale/corrupt, and disabled outcomes plus revision/fingerprint lineage.
2. Make LLCR-only context selection occur before legacy Step quantity lookup when the
   existing Measurement Plan status is `not_started` or `disabled`.
3. Keep active Measurement Plan target decisions first: exact included targets win;
   omissions, exclusions, affected/unmatched, empty/review, and corrupt states block
   without Profile/text/legacy fallback.
4. Direct Profile contexts use only parsed Confirmed Matrix LLCR token/line, confirmed
   Profile readings per sample, and the current Matrix group sample quantity. They do
   not read or require `ConfirmedMatrixStepQuantity`; therefore they cannot return
   `Confirm Matrix Step quantity` merely because legacy Step quantities are absent.
5. Preserve CR specified-current and all non-LLCR paths. Do not alter Fee rules,
   pricing, discounts, UI, workbooks, Profile writes, or API client contracts.
6. Compose the same adapter in Fee preview, direct export, required forms,
   child-process export, and rebase-created default drafts. Saved pricing drafts and
   manual edits remain untouched.

The detailed file sequence, source metadata, rollback boundary, test matrix, and
package isolation conditions are recorded in
`docs/task_361k_project_point_profile_llcr_fee_units_integration_plan.md`.

## Planned Validation

- Disposable SQLite read-adapter and Fee/API tests for confirmed Profile total,
  `P / 1-4` times group quantity `5` equals Units `20`, profile lineage, draft
  isolation, reconfirm preview behavior, and typed unavailable states.
- `not_started`/`disabled` Measurement Plan LLCR tests with no
  `ConfirmedMatrixStepQuantity`; active-root no-fallback tests; invalid group quantity
  review/no-write; target override/no-double-count; CR/non-LLCR regressions.
- Fee preview/direct export/required forms/child-process/rebase composition tests.
- Focused pytest, py_compile, Python line-count, diff/trailing/whitelist/
  forbidden-scope/no-real-mutation scans.

## Package Isolation

Only the TASK_361K adapter, narrow Fee context/composition files, focused disposable
tests, and TASK_361K governance are eligible for a future package. Existing
TASK_361F operational evidence, TASK_361H image artifacts, the board change, and all
other working-tree residuals remain external and unowned.

## Developer Implementation Pass (2026-07-15)

### Implemented Boundary

- Added `ContactPointProfileConfirmedConsumerAdapter`, a read-only adapter over the
  existing Point Profile authority repository. It accepts only a complete active
  confirmed revision with valid fingerprint and positive included-category total;
  `not_started`, draft, stale, corrupt, and disabled outcomes remain typed and
  non-authoritative.
- LLCR uses the confirmed Point Profile direct context only while the effective
  Measurement Plan is `not_started` or `disabled`. The context is derived from the
  parsed LLCR token, confirmed Profile readings per sample, and the current confirmed
  Matrix group sample quantity. It never reads `ConfirmedMatrixStepQuantity`.
- Active Measurement Plan authority remains first: its target-specific included source
  stays authoritative; omissions, exclusion/affected/unmatched/review states remain
  review-required with no Profile or text fallback.
- `fee_step_quantity_defaults` now carries one homogeneous selected source through the
  calculation result and existing `FeeFieldMetadata`. Profile Units expose deterministic
  `Confirmed Project Point Profile: revision <sequence> (<id>; <fingerprint>)`
  lineage. Legacy Matrix Step and confirmed Measurement Plan source strings remain
  unchanged; mixed/divergent/missing source facts block calculation.
- Production composition injects the read-only adapter into normal Fee preview, direct
  export, required forms, child-process export, and Matrix Fee rebase default drafts.
  CR specified-current and non-LLCR behavior remain on their existing paths.

### Exact Candidate Files

- `backend/application/contact_point_profile_confirmed_consumer_adapter.py`
- `backend/application/confirmed_matrix_fee_step_quantities.py`
- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/modules/fee_evaluation/fee_step_quantity_defaults.py`
- `backend/api/dependencies.py`
- `backend/infrastructure/office/fee_evaluation_export_child.py`
- `backend/application/matrix_fee_rebase_promotion_service.py`
- `backend/application/matrix_fee_rebase_promotion_values.py`
- Focused unit/integration tests for adapter, contexts, default-fill provenance, Fee
  draft API, Fee export paths, and rebase promotion.

`matrix_fee_rebase_promotion_values.py` is a TASK_361K-local maintainability split of
pure value-mapping helpers previously in the authorized rebase service. It keeps the
rebase service below the 500-line hard limit without changing its public behavior.
The Fee draft regression suite was likewise split into small Step-quantity and Profile
consumer modules; its shared disposable fixture remains unchanged.

### Validation

- `py -m pytest tests/unit/test_contact_point_profile_confirmed_consumer_adapter.py tests/unit/test_confirmed_matrix_fee_step_quantities.py tests/unit/test_fee_default_fill.py tests/unit/test_confirmed_matrix_fee_draft_service.py tests/unit/test_confirmed_matrix_fee_draft_step_quantities.py tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py tests/integration/test_confirmed_matrix_fee_draft_api.py tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_fee_evaluation_export_subprocess_runner.py tests/integration/test_fee_evaluation_export_child_transaction.py tests/unit/test_matrix_fee_rebase_promotion_service.py -q` -> `94 passed`.
- `py -m py_compile` for all touched production Python modules -> passed.
- `git diff --check` -> passed; only existing working-copy LF/CRLF warnings.
- Targeted trailing-whitespace scan -> no matches.
- Targeted line-count scan: all new/split TASK_361K modules and focused tests are
  below 500 lines; the pre-existing `backend/api/dependencies.py` remains a legacy
  1,897-line composition module and was changed only for the narrow required
  dependency wiring.
- No frontend changed, so `npm run build` is not applicable. Browser smoke is not
  applicable to this backend-only, disposable-fixture pass.
- No real database, real file, workbook, LTR/public-drive, or external residual was
  accessed or modified. No staging, commit, or push occurred.

### Package Isolation

External TASK_361F evidence, TASK_361H screenshots, board state, Fee rule/seed
residuals, parser residue, and all other dirty-worktree files remain excluded. The
candidate does not touch frontend/API client, Point Profile schema/parser/editor/
lifecycle, Fee rules/pricing/discount/UI, workbook generation, generic Test Record/
Report, Matrix parser/import, or LTR/public-drive paths.

## Next Legal Role

Reviewer implementation gate.

## Reviewer Readiness B1 Planning Fix (2026-07-15)

The Reviewer identified a plan contradiction: the direct Profile context can carry
lineage, but the current `fee_step_quantity_defaults.build_reading_result()` overwrites
successful context sources with `Matrix Step quantity`. This docs-only fix makes
`backend/modules/fee_evaluation/fee_step_quantity_defaults.py` an explicit narrow
provenance-propagation change within the existing May Touch boundary.

The implementation must select numeric readings and exactly one homogeneous source
together, then pass it to `calculated_result()` and existing
`FeeFieldMetadata.source`. Confirmed Profile contexts use the deterministic revision/
id/fingerprint lineage string; legacy Matrix Step and exact confirmed Measurement Plan
contexts keep their current sources. Missing, mixed, or divergent sources are
review-required/no-write even when readings agree. No DTO/API, pricing, rule, or
frontend change is planned.

The implementation completed this planned provenance behavior with disposable
regressions for Profile metadata lineage, legacy and target-specific source
preservation, and source-conflict no-write behavior.
