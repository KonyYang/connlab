# RELEASE_006B2 Reviewer Evidence

- TASK_ID: `RELEASE_006B2_MULTI_GROUP_BASE_FEE_FALLBACK_TEST`
- lane: `multi-group-base-fee-fallback-test`
- role: Reviewer
- gate: tests-only diff re-gate
- status: `reviewer_tests_only_diff_pass`
- reviewed_at: `2026-07-25`
- product_implementation_authorized: no
- tests_only_implementation: complete under prior User approval

## Finding

No current blocking finding.

The bounded tests-only candidate passes the Reviewer diff re-gate. The prior
source-of-truth blocker is closed, and the next legal role is QA. This gate
does not authorize product changes, integration, discard, cleanup, staging,
commit, or push.

## Independent Review

1. Scope ownership is exact.
   - The unique residual is the `22/0` multi-Group common Base Fee fallback
     service-integration node in
     `tests/unit/test_confirmed_matrix_fee_draft_service.py`.
   - The adjacent `16/13` `_snapshot`/groups/cells fixture generalization is
     support-only and remains excluded.
   - The sole future test May Touch is
     `tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py`.
   - The new module budget of at most 300 UTF-8 physical lines including blanks
     is feasible.

2. The fixture can use accepted public contracts without production changes.
   - `ConfirmedMatrixFeeDraftService` accepts a local confirmed snapshot store
     and loads the accepted active rule library by default.
   - The confirmed Matrix authority models expose all required version, group,
     row, cell, sample quantity, and stable identity fields.
   - `FeeEvaluationGroup` exposes `group_key` and `group_label`; each
     `FeeEvaluationLineItem` also exposes `confirmed_group_id`, so independent
     owning-Group identity can be asserted directly.
   - No shared fixture generalization or test-only rule injection is required.

3. The frozen expected behavior matches the accepted implementation.
   - Base Fee precedence remains manual provenance, then an accepted explicit
     rule Base Fee, then automatic zero.
   - The fallback is field-level and does not depend on
     `matrix_group_count`.
   - `CURRENT RATING` with condition `300A` resolves through the accepted
     `fee_rule_temperature_rise` rule.
   - For each owning Group with sample quantity 5, the accepted values are
     Unit Type `sample`, Unit Price 600, Units 5, Base Fee 0, discount 0, and
     Testing Fee 3000.
   - Base Fee metadata replacement leaves exactly one automatic entry with
     source `Matrix Fee automatic Base Fee fallback`.

4. The coverage and isolation strategy is sufficient.
   - The exact dirty residual node exists once and passed independently.
   - The same bounded coverage is absent from clean `HEAD`, so the planned
     clean-HEAD coverage RED is meaningful without manufacturing a product
     failure.
   - The old 683-line mixed test remains read-only and cannot be whole-file
     staged.
   - Focused Child 1/service, Child 2, and TASK_361L/TASK_363D V2 regressions,
     plus line, diff, whitelist, staging, and no-real-data checks, are adequate
     for the future tests-only pass.

## Implementation-Readiness Review

1. The one-build boundary is correct and testable.
   - `build_current_pricing_defaults("P1", service)` calls the service's
     `build_authority_result()` once.
   - The returned result contains the Fee draft, captured Confirmed Matrix,
     automatic values, ordered identities, row safety, and source context.
   - All assertions can be made from this result without a prior
     `build_draft()` call or a second provider read.

2. The refined public-dataclass fixture is constructible.
   - The exact version, row, two Groups, and two Cells use current public
     dataclass fields and accepted enum values.
   - A read-only probe of the proposed fixture produced one `g1` line and one
     `g2` line with distinct confirmed Group identities.
   - The probe returned `ready`, zero review-required rows, no warnings, and
     the exact accepted Current Rating values.

3. Identity, safety, and fingerprint assertions match the accepted contracts.
   - Ordered Matrix row identities are
     `matrix-b2:g1:row-current-rating:1:0` and
     `matrix-b2:g2:row-current-rating:1:0`, followed by two Sample preparation
     identities and one Report preparation identity.
   - Each Matrix row safety record is safe, uses
     `fee_rule_temperature_rise`, and contains exactly one selected Base Fee
     field with the accepted automatic fallback source and
     `required_for_rebase=True`.
   - The source-context automatic-default fingerprint equals
     `canonical_fingerprint(edited_values_to_payload(result.automatic_values))`.
     The test therefore uses the accepted serializer rather than duplicating
     product fingerprint logic or hard-coding an opaque hash.

4. TDD, budget, and package boundaries are ready.
   - Clean `HEAD` has no bounded B2 module or equivalent complete
     identity/metadata/fingerprint characterization, so coverage RED is
     meaningful.
   - GREEN requires only the new test against unchanged accepted production.
   - The proposed allocation fits the 300-line limit with adequate headroom.
   - Child 1/2/V2 regressions are read-only; the old mixed test and support
     helper hunk remain excluded from the candidate.

## Verification

- `HEAD`: `168871302b4ad3522b803391b8d7be9838e96570`
- upstream B1 accepted commit: same as `HEAD`
- index: empty
- future bounded test path: absent
- locked mixed test:
  - physical lines: 683
  - dirty numstat: `38/13`
  - SHA-256:
    `716D76D265FFC892146C0271F543455E004E8E649629733BAB125453B3FFBBF0`
- exact residual node:
  `tests/unit/test_confirmed_matrix_fee_draft_service.py::test_fee_draft_defaults_base_fee_to_zero_for_every_step_when_multiple_groups_exist`
- independent exact-node result: `1 passed`
- independent proposed-fixture probe:
  - provider calls: `1`
  - draft/groups: `ready`, `g1/g2`, one line each
  - exact identities, values, row safety, and fingerprint equality: passed
- accepted public-contract regressions:
  `test_confirmed_matrix_fee_draft_rule_resolution.py` plus
  `test_fee_pricing_draft_automatic_build_safety.py`: `22 passed`
- targeted UTF-8 trailing scan: clean
- targeted diff check: clean, except the existing task-board LF/CRLF notice
- no product, test, cleanup, discard, stage, commit, or push action performed

## Route

Next and only legal role action:

`User explicit tests-only implementation approval + Planner final
source-of-truth reconciliation`

Developer tests-only implementation cannot start until both actions complete.
Product implementation, QA, Integrator, discard, cleanup, commit, and push
remain unauthorized.

## Tests-Only Diff Gate History

### Findings

#### B1 - Source-of-truth status is stale

The tests-only candidate itself passes review, but the lane cannot route to QA
while its controlling governance files still describe the pre-implementation
state:

- `docs/task_board.md` says tests-only implementation is authorized and
  pending Developer implementation;
- `tasks/RELEASE_006B2_MULTI_GROUP_BASE_FEE_FALLBACK_TEST.md` says the same;
- `docs/release_006b2_multi_group_base_fee_fallback_test_plan.md` says the
  same;
- the Planner final authorization reconciliation stops at Developer
  implementation.

Developer evidence now records the bounded test as implemented and ready for
Reviewer. The mismatch must be closed by a docs-only Planner source-of-truth
reconciliation before QA. Reviewer must not repair the mixed board or rewrite
Planner-owned authorization history in this gate.

### Candidate Review

No product or tests-only blocking finding was found:

1. The candidate adds exactly the authorized path
   `tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py`.
2. The module is 276 UTF-8 physical lines, within the 300-line limit.
3. Its local public-dataclass fixture is self-contained and performs one
   provider read through one `build_current_pricing_defaults()` call.
4. It asserts distinct owning Group and flattened identities, exact
   `600/5/0/0/3000` results, exact automatic Base Fee metadata, safe row
   evidence, and the accepted canonical fingerprint.
5. It does not import the oversized mixed test, inject a rule, duplicate
   product calculations, or use `matrix_group_count`.
6. The old mixed test remains 683 lines with SHA-256
   `716D76D265FFC892146C0271F543455E004E8E649629733BAB125453B3FFBBF0`
   and existing `38/13` residual.
7. Backend product status and the staged index are empty.

Independent validation:

- new B2 + accepted Base Fee policy/rule-resolution tests: `18 passed`;
- accepted Child 2 duration/dependent-field tests: `21 passed`;
- accepted TASK_361L/TASK_363D automatic-build/attestation tests:
  `20 passed`;
- `py_compile`: passed;
- new test SHA-256:
  `E5AD7212F5751DB49E25535471DFE4A2EA9139E031668270B6E292E1D28A181D`;
- UTF-8 trailing and no-index diff check: clean, with only existing
  LF/CRLF notices;
- no real data, product edit, old-test edit, stage, commit, or push action.

### Blocked Route (Superseded)

Next and only legal role action:

`Planner docs-only source-of-truth reconciliation`

Planner must align board/task/plan/reconciliation to Developer implementation
complete and pending Reviewer tests-only diff re-gate. After that, return to
Reviewer; do not route QA directly from the stale state.

## Tests-Only Diff Re-Gate

### Resolution

The B1 source-of-truth blocker is closed:

- board header, active-task summary, execution-model bullet, and lane row all
  say Developer tests-only implementation complete / pending Reviewer
  tests-only diff re-gate;
- task and plan carry the same current status;
- Planner reconciliation records Developer implementation completion and the
  prior Reviewer governance-only blocker;
- no stale pending-Developer implementation state controls the active lane.

The candidate remained byte-for-byte stable across reconciliation:

- sole test path:
  `tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py`;
- physical lines: `276`;
- SHA-256:
  `E5AD7212F5751DB49E25535471DFE4A2EA9139E031668270B6E292E1D28A181D`;
- exact node rerun: `1 passed`;
- locked mixed test: 683 lines, unchanged SHA-256
  `716D76D265FFC892146C0271F543455E004E8E649629733BAB125453B3FFBBF0`,
  existing `38/13` residual;
- backend product status: empty;
- staged index: empty;
- trailing and no-index diff checks: clean except existing LF/CRLF notices.

No new candidate finding was introduced. The earlier independent
`18 + 21 + 20` regression results and py_compile result remain valid.

### Final Route

Next and only legal role action:

`QA tests-only gate`

QA must validate the bounded test in an isolated clean-HEAD package and retain
the old mixed test, product paths, B1/B3, Child C, cleanup, staging, commit,
and push exclusions. Integrator remains unauthorized until QA passes.
