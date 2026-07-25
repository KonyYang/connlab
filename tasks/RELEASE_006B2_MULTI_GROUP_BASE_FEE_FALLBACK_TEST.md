# RELEASE_006B2 Multi-Group Base Fee Fallback Test

Date: 2026-07-25
Status: Developer tests-only implementation complete / pending Reviewer tests-only diff re-gate
Lane: `multi-group-base-fee-fallback-test`
Parent: `RELEASE_006_POST_PUSH_WORKTREE_RESIDUAL_COMMIT_AND_CLEANUP_RECONCILIATION`
Source audit: `RELEASE_006B_TEST_RESIDUAL_OWNERSHIP_AUDIT`
Upstream B1: complete/accepted at `168871302b4ad3522b803391b8d7be9838e96570`
Implementation authorization: tests-only, exact bounded module only
Discard authorization: none
Commit authorization: none
Push authorization: none

## 1. Goal

Move one unique service-integration contract from an oversized mixed test into
a new bounded tests-only module.

The exact unique residual is the `22/0` test:

```text
test_fee_draft_defaults_base_fee_to_zero_for_every_step_when_multiple_groups_exist
```

currently present only in the dirty working-tree copy of:

```text
tests/unit/test_confirmed_matrix_fee_draft_service.py
```

The separate `16/13` `_snapshot` generalization in that file is support-only
and is not part of this lane.

## 2. Why This Lane Is Allowed

- Child B Planner and Reviewer audits classify the `22/0` behavior as unique.
- Reviewer named the bounded replacement
  `test_confirmed_matrix_fee_draft_multi_group_base_fee.py` with a `<=300`
  physical-line maximum.
- RELEASE_006B1 is complete/accepted and remains read-only.
- The User explicitly authorized Planner formalization and subsequently
  approved Developer tests-only planning-first for B2.
- Reviewer passed the B2 plan gate.
- Reviewer passed the Developer-plan / implementation-readiness gate.
- The User explicitly approved tests-only implementation for the exact
  bounded module frozen by this task.
- Developer completed the exact bounded tests-only implementation.
- Reviewer confirmed the candidate behavior and validation; the current
  blocker is governance source-of-truth reconciliation only.

Product implementation remains unauthorized. Test implementation is
authorized only for:

```text
tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py
```

## 3. Accepted Business Contract

Base Fee precedence remains:

```text
proven manual Base Fee
> explicit accepted rule-specific Base Fee
> automatic Base Fee 0
```

The precedence applies identically to single-Group and multi-Group drafts.
`matrix_group_count` is not an authority or trigger for automatic zero.

B2 verifies only that the accepted common fallback is independently present
on every Fee line of a deterministic multi-Group draft. It does not implement,
recalculate, or redefine the product policy.

Testing Fee remains derived from each line's final safe Unit Price, Units,
Base Fee, and discount. No value may be aggregated across Groups.

## 4. Frozen Local Fixture

The future bounded test must build its own local Confirmed Matrix snapshot.
It must not import or edit helpers from the oversized mixed test.

Version:

```text
confirmed_matrix_id  matrix-b2
project_id           P1
confirmed_revision   1
status               confirmed
active authority     true
```

One row:

```text
confirmed_row_id     row-current-rating
row_order            1
test_item            CURRENT RATING
condition            300A
method               EIA-364
requirement          No damage
```

Two Groups:

```text
group-1 / g1 / Group 1 / sample quantity 5
group-2 / g2 / Group 2 / sample quantity 5
```

Two Cells:

```text
cell-1 -> row-current-rating + group-1, value 1
cell-2 -> row-current-rating + group-2, value 1
```

Every identity must be unique and internally consistent. There is no second
row, Step quantity, duration authority, Point Profile, LLCR/CR authority, or
manual pricing draft.

## 5. Exact Assertions

The draft must contain two Groups in order and one Current Rating Fee line per
Group.

For both lines:

```text
matched_rule_id   fee_rule_temperature_rise
status            calculated
review_required   false
review_reason     null
unit_label        sample
unit_price        600
units             5
base_fee          0
discount_percent  0
testing_fee       3000
```

Each line must retain its owning Group identity. The test must also prove that
the `base_fee` metadata is:

```text
state   auto_filled
source  Matrix Fee automatic Base Fee fallback
```

The result must not depend on `matrix_group_count`, cross-Group aggregation,
or an explicit rule-specific Base Fee.

## 5.1 Frozen Single-Build V2 Assertions

The bounded test must call:

```text
build_current_pricing_defaults("P1", service)
```

exactly once against a local provider/store whose call count proves one
authority read. It must use that single result for the draft, flattened
automatic values, ordered identities, row safety, and source context. A
preliminary `build_draft()` call or any second provider read is forbidden.

The two Matrix line identities are:

```text
matrix-b2:g1:row-current-rating:1:0
matrix-b2:g2:row-current-rating:1:0
```

The ordered automatic-default identities must also retain the two owning
sample-preparation identities and the report-preparation identity defined by
the accepted service contract. Both Matrix row-safety records must be safe,
identify `fee_rule_temperature_rise`, and contain the required automatic Base
Fee source. The source-context automatic-default fingerprint must equal the
canonical fingerprint of the accepted serialized automatic values payload.

## 6. Exact Future May Touch

Test-only:

```text
tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py
```

Governance:

```text
tasks/RELEASE_006B2_MULTI_GROUP_BASE_FEE_FALLBACK_TEST.md
docs/release_006b2_multi_group_base_fee_fallback_test_plan.md
docs/lane_evidence/RELEASE_006B2_multi-group-base-fee-fallback-test_planner.md
docs/task_board.md
future role evidence for this exact lane
```

The new Python test module must remain `<=300` UTF-8 physical lines including
blank lines, and in all cases below the project hard limit of 500.

## 7. Must Not Touch

- `tests/unit/test_confirmed_matrix_fee_draft_service.py`;
- its `22/0` unique hunk and `16/13` support hunk;
- all Fee production, API, schema, database, seed, manifest, and frontend code;
- accepted Child 1/2/V2 production and tests, except read-only execution;
- RELEASE_006B1 and its old frontend `114/0` residual;
- RELEASE_006B3 parser coverage;
- Child C, duplicate/support hunks, and every external residual;
- real databases/files, generated artifacts, staging, commits, and remote refs.

Whole-file staging of the 683-line mixed legacy test is forbidden.

## 8. TDD And Validation

This is a characterization-coverage lane. Accepted production already
satisfies the observed result.

Coverage RED:

- clean accepted HEAD has no bounded B2 module;
- accepted tests do not prove common fallback on every line of a two-Group
  deterministic service draft.

Unchanged-product GREEN:

- create only the bounded test module;
- run it against clean accepted production;
- require zero product diff and zero legacy-test diff.

Focused and read-only regression commands:

```powershell
py -m pytest `
  tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py `
  tests/unit/test_confirmed_matrix_fee_base_fee_policy.py `
  tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py `
  tests/unit/test_confirmed_matrix_fee_draft_service.py -q

py -m pytest `
  tests/unit/test_confirmed_matrix_fee_duration_authority.py `
  tests/unit/test_fee_default_fill_explicit_hour_authority.py `
  tests/integration/test_confirmed_matrix_fee_draft_dependent_fields_api.py `
  tests/integration/test_fee_default_fill_dependent_fields_v2_rebase.py -q

py -m pytest `
  tests/unit/test_fee_pricing_draft_prior_defaults_attestation.py `
  tests/unit/test_fee_pricing_draft_automatic_build_safety.py `
  tests/integration/test_fee_pricing_draft_measurement_plan_rebase_attestation.py -q

py -m py_compile tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py
```

The old service test in validation must come from clean accepted HEAD, not the
dirty `38/13` working-tree residual.

## 9. Package Isolation And Rollback

The future candidate package may contain only the new bounded test and
approved B2 governance/evidence. It must show:

- one new test file only;
- no product diff;
- no old mixed-test diff;
- no B1/B3, support/duplicate, Child C, or external residual;
- line-budget, UTF-8, trailing, diff-check, whitelist, forbidden-path,
  py_compile, and no-real-data checks.

Before acceptance, rollback is omission of the new test from the candidate.
After a later accepted tests-only commit, rollback reverts only that commit.

## 10. Old Residual Disposition

Neither old hunk may be changed in this lane.

Only after the bounded B2 replacement is accepted may:

- the original `22/0` node become an exact discard/restore candidate;
- the support-only `16/13` helper generalization remain a separately confirmed
  discard/restore candidate.

Reviewer confirmation and explicit User cleanup authorization are still
required. This planned lane authorizes no cleanup action.

## 11. Acceptance Criteria

- local two-Group fixture is self-contained and identity-consistent;
- both owning lines have the exact deterministic Current Rating result;
- both lines use automatic Base Fee `0` with exact fallback metadata;
- one authority build/provider read produces the draft, flattened values,
  ordered identities, row safety, and source context;
- the two exact Matrix identities, required automatic Base Fee safety, and
  canonical automatic-default fingerprint are asserted;
- no `matrix_group_count` trigger or cross-Group aggregation is asserted or
  introduced;
- new test is `<=300` physical lines;
- focused Child 1, Child 2, V2, legacy service, and py_compile gates pass in an
  isolated clean-HEAD package;
- no product, old-test, B1/B3, Child C, cleanup, stage, commit, or push action.

## 12. Implementation Checkpoint

The exact candidate is:

```text
tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py
276 UTF-8 physical lines including blanks
SHA-256 E5AD7212F5751DB49E25535471DFE4A2EA9139E031668270B6E292E1D28A181D
```

Reviewer independently confirmed the single provider read, both Group
identities, exact `600/5/0/0/3000` values, automatic Base Fee metadata, safe
row-safety evidence, canonical fingerprint, and `18 + 21 + 20` passing
regressions plus py_compile.

## 13. Stop Point

Route only:

```text
Reviewer tests-only diff re-gate
```

Product and test candidates are now locked pending Reviewer re-gate. Do not
route QA or Integrator, and do not discard, clean up, stage, commit, or push.
