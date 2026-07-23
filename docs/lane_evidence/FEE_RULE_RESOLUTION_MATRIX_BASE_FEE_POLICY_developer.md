# FEE_RULE_RESOLUTION_MATRIX_BASE_FEE_POLICY Developer Evidence

Status: ready_for_reviewer_implementation_re_gate
Date: 2026-07-23
Task: `FEE_RULE_RESOLUTION_MATRIX_BASE_FEE_POLICY`
Lane: `fee-rule-resolution-matrix-base-fee-policy`
Parent: `FEE_DEFAULT_FILL_RESIDUAL_PACKAGE_RECONCILIATION`
Role: Developer implementation pass
Implementation authorization: authorized and executed for Child 1 exact May Touch

## Gate Basis

The User explicitly approved Child 1 Developer planning-first only. This pass read the real Fee draft/default-fill/rule-resolution and accepted TASK_361L/TASK_363D provenance paths, then refined the implementation plan. It did not modify product code, tests, frontend, API contracts, schema, database, dependencies, or generated artifacts.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Why this action was allowed: the lane has explicit User authorization for docs-only planning-first, while Child 1 product implementation and Child 2/3 work remain unauthorized.

## Files Updated

- `docs/fee_rule_resolution_matrix_base_fee_policy_plan.md`
- `docs/lane_evidence/FEE_RULE_RESOLUTION_MATRIX_BASE_FEE_POLICY_developer.md`

No task-board or task-file status was changed by the Developer role. Planner owns source-of-truth reconciliation.

## Read-Only Findings

1. The current Base Fee candidate is multi-Group-specific and therefore violates the final all-lines precedence contract.
2. The current Base Fee candidate also contains generic temperature unit-label behavior that belongs outside Child 1.
3. The current rule-resolution candidate approves two rejected long-term labels and rewrites plain Contact Resistance to LLCR; both behaviors must be removed in a future authorized implementation.
4. The pre-persistence calculation layer cannot prove saved manual Base Fee provenance. It must emit a deterministic automatic baseline; accepted TASK_361L/TASK_363D provenance/rebase services remain responsible for preserving proven manual values.
5. Automatic values already bind the automatic-default/source-context fingerprints, while field metadata source binds TASK_363D row-safety. No schema, DTO, API, or token expansion is needed.
6. Existing oversized tests contain contradictory residual assertions. The future package uses three new bounded modules; the oversized files remain read-only unless Planner separately re-scopes exact nodes.

## Contract Refinement Completed

- Base Fee precedence is frozen as proven manual, then explicit accepted rule-specific, then automatic `0`.
- `matrix_group_count` is removed from the future policy boundary.
- The deterministic fallback metadata source is frozen as `Matrix Fee automatic Base Fee fallback`.
- Explicit rule-specific zero remains distinguishable from generic fallback through structured rule authority.
- Testing Fee derives only after Unit Price, Units, Base Fee, and discount are valid; unsafe dependencies remain unset/review-required.
- Only `Long-term high temperature zone load` is an accepted High temperature Life alias.
- Plain Contact Resistance never falls back to LLCR or Point Profile authority.
- TASK_361L/TASK_363D generation, CAS, token, current-v2, single-build, attestation, and reviewed-rebase semantics remain locked.

## Future Exact May Touch

Product:

- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/application/confirmed_matrix_fee_base_fee_policy.py`
- `backend/application/confirmed_matrix_fee_rule_resolution.py`

New bounded tests:

- `tests/unit/test_confirmed_matrix_fee_base_fee_policy.py`
- `tests/unit/test_confirmed_matrix_fee_rule_resolution.py`
- `tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py`

Everything else remains locked, including default-fill/common, seeds/manifest, V2 product modules, public API/client, frontend, schema/database, Child 2/3, real data/files, generated artifacts, and mixed residuals.

## Physical Line Facts And Budgets

Observed before this docs-only pass:

- `confirmed_matrix_fee_draft_service.py`: 486 physical lines
- `confirmed_matrix_fee_base_fee_policy.py`: 174 physical lines
- `confirmed_matrix_fee_rule_resolution.py`: 78 physical lines
- `tests/unit/test_confirmed_matrix_fee_draft_service.py`: 684 physical lines, read-only
- `tests/unit/test_fee_default_fill.py`: 912 physical lines, read-only
- three planned bounded test modules: absent

Future budgets:

- draft service target `<=480`, hard `<500`
- Base Fee helper `<=260`
- rule-resolution helper `<=180`
- Base Fee test `<=260`
- rule-resolution test `<=220`
- draft/V2 integration-style unit test `<=480`

Counts must use UTF-8 `Path.read_text(...).splitlines()` including blank lines.

## Planned Verification

The plan now names focused red/green tests for rule positives/negatives, Base Fee precedence, formula dependencies, metadata deduplication, single/multi equivalence, no CR fallback, V2 fingerprints, manual-field preservation, stale CAS no-write, and single-authority-build behavior.

Future implementation validation also includes `py_compile`, `git diff --check`, UTF-8 trailing whitespace, physical line counts, exact-path/forbidden-scope/no-real-data scans, and staging-empty verification.

## Planning Validation Results

- Product/test diff: none from this Developer pass.
- Real DB/files/generated artifacts: not accessed.
- Dependencies: unchanged.
- Stage/commit/push: not performed.
- Child 2 and Child 3: not started and remain unauthorized.
- UTF-8 physical line count using `Path.read_text(encoding='utf-8').splitlines()`: plan `259`; Developer evidence `106` before this result block was finalized. Both are documentation files; no Python line budget is affected.
- UTF-8 trailing-whitespace scan: clean for both touched documents.
- `git diff --no-index --check -- NUL <file>`: no whitespace errors for either new file; each returned the expected add-file exit `1`.
- Exact-path status: only the plan and Developer evidence are new in the Child 1 package.
- Existing `docs/task_board.md` modification is an external governance residual and was not touched by this Developer pass.
- Staging check: `git diff --cached --name-only` returned `0` paths.

## Authorized Implementation Pass

Planner reconciliation, Reviewer implementation-readiness, and explicit User product approval authorized Child 1 implementation. The implementation remained within the formal exact May Touch.

Product changes:

- `confirmed_matrix_fee_rule_resolution.py`
  - retains only the approved `Long-term high temperature zone load` alias;
  - preserves existing matcher results;
  - removes the plain Contact Resistance to LLCR fallback.
- `confirmed_matrix_fee_base_fee_policy.py`
  - removes `matrix_group_count` and generic temperature behavior;
  - selects structured explicit rule Base Fee before deterministic fallback `0`;
  - emits fallback source `Matrix Fee automatic Base Fee fallback`;
  - recalculates Testing Fee only when Unit Price, Units, and discount are present;
  - clears stale Testing Fee when dependencies are missing and preserves review metadata.
- `confirmed_matrix_fee_draft_service.py`
  - builds one row-rule map per confirmed snapshot;
  - removes Group-count policy plumbing;
  - applies the final policy once per Fee line;
  - preserves confirmed CR lineage as the Testing Fee metadata source;
  - retains TASK_363D's single-authority-build boundary.

New bounded tests:

- `tests/unit/test_confirmed_matrix_fee_rule_resolution.py`
- `tests/unit/test_confirmed_matrix_fee_base_fee_policy.py`
- `tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py`

## TDD Evidence

RED:

- first behavior run: `9 failed, 3 passed`;
- failures proved the two rejected aliases were being matched, plain CR was being rewritten to LLCR, and the policy still required `matrix_group_count`;
- service RED: `10 failed`, all at the obsolete Group-count call boundary.

GREEN:

- exact Child 1 modules: `23 passed in 0.80s`.

Covered contracts include:

- explicit rule Base Fee, including explicit zero, keeps rule-specific source;
- structured missing Base Fee uses automatic `0`;
- single/multi Group use identical precedence;
- non-explicit suggested Base Fee does not override the common fallback;
- Testing Fee uses final Unit Price, Units, Base Fee, and discount;
- missing dependencies leave Testing Fee unset/review-required;
- only the approved high-temperature alias resolves;
- plain CR never consumes LLCR authority;
- automatic values bind source-context fingerprint;
- Base Fee metadata source is visible in TASK_363D row safety;
- accepted V2 reviewed rebase preserves its proven manual price/base-fee/discount/notes/spend-time fields while automatic Units/Testing Fee follow the accepted refresh contract.

## Regression Results

- Child 1 plus CR/LLCR, TASK_361L/TASK_363D, and alias-units read-only regressions:
  - `73 passed, 1 deselected in 1.49s`.
- Confirmed Fee API and V2 persistence/attestation regressions:
  - `12 passed, 1 deselected in 3.41s`.
- Oversized read-only `test_confirmed_matrix_fee_draft_service.py`, excluding three frozen-contract contradictions:
  - `22 passed, 3 deselected in 0.76s`.

At the initial implementation gate, these contradictory nodes remained locked.
They were subsequently migrated only after the Planner authorized the bounded
tests-only pass recorded below:

- `test_plain_contact_resistance_uses_llcr_when_matrix_has_no_explicit_llcr` asserts the rejected CR-to-LLCR fallback.
- `test_fee_draft_uses_temperature_rise_rule_for_current_rating` asserts the old suggested Base Fee `500` instead of structured-rule/fallback precedence.
- two parameter instances of `test_fee_draft_defaults_non_rise_temperature_items_to_per_hour` assert the two rejected aliases.

The API node `test_fee_draft_api_uses_confirmed_point_profile_for_llcr_units` remains the known external LLCR profile residual (`expected 20`, current external worktree result `None`) and is excluded from Child 1. It was not changed or attributed to this package.

## Final Static Validation

- `py_compile`: passed for all three product files and three new tests.
- UTF-8 physical lines including blanks:
  - draft service `479`;
  - Base Fee helper `147`;
  - rule-resolution helper `51`;
  - Base Fee test `187`;
  - rule-resolution test `81`;
  - draft/V2 test `301`.
- All candidate Python files are below the 500-line hard limit; the service also meets the plan target `<=480`.
- UTF-8 trailing-whitespace scan: clean.
- Tracked `git diff --check`: passed.
- Five new-file `git diff --no-index --check` runs: no whitespace errors; expected add-file exit `1`.
- Exact status contains only the three authorized product files, three authorized new tests, and this lane's governance/evidence among Child 1 paths.
- Forbidden real-data/generated-output content scan: clean.
- Real DB/files/generated artifacts: not accessed.
- Frontend/dependencies/schema/API client: unchanged.
- Stage/commit/push: not performed.
- Staging: empty.

## Blockers

None for Reviewer implementation re-gate. The external LLCR profile residual
remains a documented exclusion, not an unreported candidate failure.

## Recommended Next Role

Reviewer implementation re-gate. Do not route QA or Integrator directly.

## Bounded Tests-Only Fix Pass

Planner reconciled a tests-only scope for four stale legacy expectations after
the product implementation was reviewed as contract-correct and locked. This
pass changed assertions only in:

- `tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py`
- `tests/unit/test_confirmed_matrix_fee_draft_service.py`

The migrated expectations now prove:

- plain Contact Resistance does not consume LLCR fallback authority and leaves
  Unit Price, Units, and Testing Fee unset under typed review;
- Temperature Rise uses the common automatic Base Fee `0`, so Testing Fee is
  derived as `600 * 5 + 0 = 3000`;
- only `Long-term high temperature zone load` remains the approved automatic
  High temperature Life alias;
- `Long-term temperature cycle with load` and `Long-term damp heat` remain
  unmatched/manual-review rows with no invented automatic values.

Exact authorized nodes:

- `test_plain_contact_resistance_uses_llcr_when_matrix_has_no_explicit_llcr`:
  `1 passed in 0.79s`.
- `test_fee_draft_uses_temperature_rise_rule_for_current_rating`:
  `1 passed in 0.80s`.
- `test_fee_draft_defaults_non_rise_temperature_items_to_per_hour[Long-term temperature cycle with load]`:
  `1 passed in 0.79s`.
- `test_fee_draft_defaults_non_rise_temperature_items_to_per_hour[Long-term damp heat]`:
  `1 passed in 0.80s`.

Regression results:

- both owning legacy modules: `34 passed in 0.86s`;
- Child 1 bounded suite: `23 passed in 0.87s`;
- accepted TASK_361L/TASK_363D and CR/alias regressions:
  `42 passed in 0.98s`.

Physical line counts, including blank lines:

- `test_confirmed_matrix_fee_draft_profile_consumer.py`: `222` (baseline
  `223`);
- `test_confirmed_matrix_fee_draft_service.py`: `683` (baseline `684`).

No product code, other test node, fixture contract, seed, V2 module, API,
frontend, Child 2/3, real data/file, or generated artifact was changed by this
tests-only pass. Stage/commit/push were not performed.

Final tests-only checks:

- `py_compile` passed for both touched test modules;
- tracked `git diff --check` passed with only the existing LF/CRLF notice;
- Developer evidence no-index diff-check reported no whitespace error;
- UTF-8 trailing-whitespace scan was clean;
- exact-path status showed only the two authorized legacy tests plus this
  lane's Developer evidence;
- staging was empty;
- no real database, public-drive path, attachment, or generated artifact was
  accessed.

Final status: `ready_for_reviewer_implementation_re_gate`. The next role is
Reviewer; QA and Integrator remain out of route.
