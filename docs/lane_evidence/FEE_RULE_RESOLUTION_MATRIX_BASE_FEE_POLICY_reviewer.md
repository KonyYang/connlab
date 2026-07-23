# Fee Rule Resolution Matrix Base Fee Policy - Reviewer Evidence

Date: 2026-07-23
Role: Reviewer
Status: `reviewer_implementation_readiness_pass / pending User product implementation approval and Planner final reconciliation`

Task: `FEE_RULE_RESOLUTION_MATRIX_BASE_FEE_POLICY`
Lane: `fee-rule-resolution-matrix-base-fee-policy`
Parent: `FEE_DEFAULT_FILL_RESIDUAL_PACKAGE_RECONCILIATION`

## Gate Context

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task: none. This Child 1 lane is explicitly ready for this implementation-readiness review, not for product implementation.
- Why this review is allowed: Reviewer umbrella/Child 1 plan re-gate passed, the User approved Child 1 Developer planning-first, and Developer completed a docs-only planning-first pass. Product implementation remains unauthorized.

## Readiness Result

Pass. The Child 1 contract is implementable without widening to Child 2, Child 3, the twelve-path umbrella, or accepted TASK_361L/TASK_363D authority modules.

## Verified Contract And Boundaries

- Final Base Fee precedence is sufficiently exact: V2-proven manual Base Fee is preserved by accepted provenance/rebase, then an explicit structured matched-rule `base_fee.amount` wins, otherwise the automatic baseline is Decimal `0` for every Fee line. `matrix_group_count` is not an authority and must not be an input to the replacement policy.
- The existing calculation layer cannot prove persisted manual provenance. The planned split correctly leaves that responsibility with accepted TASK_361L/TASK_363D generation, CAS, token, current-v2, reload, attestation, and reviewed-rebase paths. Existing V2 merge logic includes `base_fee` among preserved manual fields.
- The planned policy must replace only Base Fee and Testing Fee metadata entries, preserve unrelated metadata, use `Matrix Fee automatic Base Fee fallback` for fallback zero, and retain an explicit rule display name for a rule-specific Base Fee, including explicit zero. Final automatic values and field metadata flow through the existing automatic-default/source-context and row-safety fingerprints without schema, DTO, API, or token changes.
- Testing Fee remains derived only after valid Unit Price, Units, Base Fee, and discount are available. Missing or review-required dependencies remain unset/review-required; Child 1 must not fabricate dependent values.
- Rule resolution is narrow and deterministic: only normalized `Long-term high temperature zone load` may resolve to the existing High temperature Life rule. `Long-term temperature cycle with load`, `Long-term damp heat`, and plain `CONTACT RESISTANCE` remain no-rule/manual-review paths. The resolver neither reads providers nor uses global LLCR-row presence.
- Future product scope is limited to the fee-draft coordinator plus the Base Fee and rule-resolution helpers. Existing default-fill/common, seeds/manifests, V2 persistence/attestation modules, routes/DTOs, frontend, schema/database, and Child 2/3 stay locked. The current mixed worktree hunks must be replayed at hunk level from the accepted baseline; no wholesale mixed-file absorption is authorized.
- The three bounded new test modules cover the required rule, precedence, metadata, single/multi equivalence, no-CR-fallback, V2 preservation/currentness/CAS, and single-authority-build regressions. Oversized legacy suites remain read-only regression execution only. Product candidates must remain below 500 UTF-8 physical lines; the coordinator must stop for Planner re-scope if narrow edits cannot retain that limit.

## Verification Performed

- Read `AGENTS.md`, `docs/task_board.md`, the Child 1 task/plan, Planner/Developer/reconciliation evidence, umbrella Reviewer evidence, Child 2/3 dependency gates, and actual fee-draft, Base Fee, rule-resolution, default-fill, and V2 provenance/rebase code.
- Confirmed the current unaccepted Base Fee helper still uses a `matrix_group_count > 1` blanket policy and generic temperature behavior, while the current resolver contains the two rejected aliases and plain-CR-to-LLCR fallback. The plan correctly requires these candidate behaviors to be replaced, not preserved.
- Confirmed no product code, test, schema, database, real DB/file, public-drive, generated-artifact, stage, commit, or push action was performed by this review.

## Next Legal Role

User product implementation approval for Child 1, followed by Planner final source-of-truth reconciliation. Do not route Developer implementation directly. Child 2 and Child 3 remain blocked, and the umbrella is not an implementation authorization.

## Implementation Gate

Date: 2026-07-23

### Result

Blocked pending a formal, tests-only scope reconciliation. The product implementation itself matches the reviewed Child 1 contract, but its green package relies on deselecting existing locked assertions that now directly contradict that contract.

### Verified Product Behavior

- The new bounded Child 1 suite passed: `23 passed`.
- The policy selects structured `FeeRule.base_fee.amount`, including an explicit zero, before the deterministic automatic-zero fallback. Its API no longer takes `matrix_group_count`; the coordinator applies it once per line.
- The policy clears an obsolete Testing Fee value when Unit Price, Units, or discount is unavailable while preserving the existing review-required metadata. It does not fabricate a missing dependency.
- The resolver retains only the approved normalized high-temperature alias and no longer rewrites plain Contact Resistance to LLCR. The actual plain-CR row remains the existing specified-current CR rule path.
- V2 preservation is provenance-based, not non-null-value based: accepted V2 payload `row_provenance` identifies preserved fields, and `base_fee` is included in the reviewed-rebase manual field set. Child 1 only produces the automatic baseline and associated metadata/fingerprints.
- `py_compile` passed for the three product modules. All six Child 1 product/test candidates are below 500 UTF-8 physical lines.

### B1 - Locked stale assertions require a tests-only migration authorization

The exact locked nodes were independently run with a disposable pytest base temp directory. Results were `4 failed, 1 passed`:

- `tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py::test_plain_contact_resistance_uses_llcr_when_matrix_has_no_explicit_llcr` still expects the rejected plain-CR-to-LLCR fallback.
- `tests/unit/test_confirmed_matrix_fee_draft_service.py::test_fee_draft_uses_temperature_rise_rule_for_current_rating` still expects the superseded suggested Base Fee `500` / Testing Fee `3500` outcome.
- The `Long-term temperature cycle with load` and `Long-term damp heat` parameter instances of `tests/unit/test_confirmed_matrix_fee_draft_service.py::test_fee_draft_defaults_non_rise_temperature_items_to_per_hour` still expect the two rejected aliases. The approved `Long-term high temperature zone load` instance passes.

Those failures exactly reflect the accepted Child 1 contract and are not product regressions. Nevertheless, the two legacy files are explicitly locked/read-only for Child 1, so persistent deselection cannot substitute for the required regression migration before QA. The known external LLCR profile API residual remains separately excluded and was not reviewed as part of this finding.

### Required Bounded Follow-Up

Route Planner for a docs-only tests-only scope reconciliation. It must authorize only the listed assertion migrations, preserve unrelated legacy nodes, and then route a Developer tests-only fix pass. No product, seed, V2, API, frontend, Child 2/3, or external LLCR changes are authorized by this finding.

### Verification

- `py -m pytest tests/unit/test_confirmed_matrix_fee_base_fee_policy.py tests/unit/test_confirmed_matrix_fee_rule_resolution.py tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py -q`: `23 passed`.
- Exact locked-node run: `4 failed, 1 passed`, with only the contract contradictions above failing.
- Temporary pytest base directory was not retained.

## Next Legal Role

Planner docs-only tests-only scope reconciliation. Do not route QA, Integrator, or a product Developer fix until that authorization exists.

## Implementation Re-Gate: Tests-Only B1

Date: 2026-07-23

### Result

Pass. The formally authorized stale assertions now express the accepted Child 1 contract, and no product behavior was changed in this pass.

### Exact Migration Review

- The plain-CR assertion now requires the specified-current CR rule, typed review, no LLCR Unit Price/Units/Testing Fee, and automatic Base Fee `0`. It no longer consumes LLCR authority.
- The Temperature Rise assertion now requires calculated `600 * 5 + 0 = 3000`, reflecting common automatic Base Fee fallback rather than the superseded suggested Base Fee `500`.
- The two rejected long-temperature parameter cases now require unmatched/manual-review with no invented Unit Price, Units, or Testing Fee. The still-approved `Long-term high temperature zone load` parameter remains the only automatic High temperature Life case.
- The allowed current-worktree line baselines were `223` and `684`; the files are now `222` and `683` UTF-8 physical lines. There is no line increase.
- The current whole-file diff contains an earlier multi-Group regression and fixture hunk. It was present at the preceding Reviewer implementation gate and is outside this tests-only overlay; this pass neither expanded nor absorbed it. No other assertion/fixture change is attributed to this tests-only fix.

### Verification

- Exact authorization nodes passed individually.
- `py -m pytest tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py tests/unit/test_confirmed_matrix_fee_draft_service.py tests/unit/test_confirmed_matrix_fee_base_fee_policy.py tests/unit/test_confirmed_matrix_fee_rule_resolution.py tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py -q --basetemp tmp\\review_child1_tests_only`: `57 passed`.
- The disposable pytest base temp directory was removed after the run.
- Child 2, Child 3, V2 product modules, seeds, frontend/API, and the external LLCR profile residual remain excluded.

## Next Legal Role

QA gate. Do not route Integrator directly.
