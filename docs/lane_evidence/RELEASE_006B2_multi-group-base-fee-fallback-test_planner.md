# RELEASE_006B2 Multi-Group Base Fee Fallback Test Planner Evidence

Date: 2026-07-25
Role: Planner
Status: Developer tests-only implementation complete / pending Reviewer tests-only diff re-gate
Task: `RELEASE_006B2_MULTI_GROUP_BASE_FEE_FALLBACK_TEST`
Lane: `multi-group-base-fee-fallback-test`
Parent: `RELEASE_006_POST_PUSH_WORKTREE_RESIDUAL_COMMIT_AND_CLEANUP_RECONCILIATION`
Product implementation authorization: none
Test implementation authorization: exact bounded B2 module only

## 1. Discovery Gate

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Current task:

```text
RELEASE_006B2_MULTI_GROUP_BASE_FEE_FALLBACK_TEST
Developer tests-only implementation complete / pending Reviewer tests-only diff re-gate
```

Why Planner may act:

- Child B ownership audit passed Reviewer;
- B1 is complete/accepted at
  `168871302b4ad3522b803391b8d7be9838e96570`;
- Reviewer passed the B2 plan and implementation-readiness gates;
- User explicitly approved the exact B2 tests-only implementation;
- Developer completed the bounded candidate and Reviewer confirmed its
  implementation contract and validation.

## 2. Confirmed Facts

Confirmed by User:

- formalize B2 only;
- move only the unique `22/0` behavior into a new bounded test;
- keep the old mixed test and `16/13` helper generalization read-only;
- preserve accepted Base Fee precedence and all product locks;
- route Reviewer plan gate only.

Confirmed by repository:

- HEAD is the accepted B1 commit;
- the index was empty before this formalization;
- old service test remains `683` lines, dirty `38/13`, SHA-256
  `716D76D265FFC892146C0271F543455E004E8E649629733BAB125453B3FFBBF0`;
- exact dirty split is `22/0` unique plus `16/13` support-only;
- future bounded path is absent;
- accepted Current Rating composition resolves:
  `fee_rule_temperature_rise`, Unit Price `600`, Units `5`, Base Fee `0`,
  Testing Fee `3000`;
- accepted Base Fee metadata uses state `auto_filled` and source
  `Matrix Fee automatic Base Fee fallback`;
- accepted Child 1 tests separately prove common fallback and explicit/manual
  precedence, but not every line of a two-Group service draft.

Planner inference:

- full task ID is
  `RELEASE_006B2_MULTI_GROUP_BASE_FEE_FALLBACK_TEST`;
- lane slug is `multi-group-base-fee-fallback-test`;
- one row, two Groups, and two Cells is the smallest real service-composition
  fixture that closes the unique coverage gap.

Not authorized:

- test or product implementation;
- old-test edits;
- B1/B3, duplicate/support, Child C, cleanup, stage, commit, or push.

No unresolved question changes B2 scope, behavior, or validation. Definition
of Ready is sufficient for a planned-only Reviewer gate.

## 3. Unique Hunk Ownership

Owned by B2:

```text
test_fee_draft_defaults_base_fee_to_zero_for_every_step_when_multiple_groups_exist
22 additions / 0 deletions
```

Not owned:

```text
_snapshot(group_count=1)
tuple-based groups/cells fixture generalization
16 additions / 13 deletions
```

The new test must implement its own fixture. No code from either dirty hunk is
copied into the old file or staged whole-file.

## 4. Frozen Behavior

Base Fee precedence:

```text
manual > explicit accepted rule-specific > automatic 0
```

Group count does not trigger the fallback. B2 proves that the same accepted
line policy is applied independently to both owning Groups.

Expected line tuple for each Group:

```text
fee_rule_temperature_rise
calculated / review_required false
sample / 600 / 5 / 0 / discount 0 / 3000
base_fee metadata auto_filled / Matrix Fee automatic Base Fee fallback
```

No cross-Group sum, authority lookup, or policy recreation is permitted.

## 5. Future May Touch

Only:

```text
tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py
```

Budget:

```text
<=300 UTF-8 physical lines including blanks
```

The module owns one local store, one local snapshot fixture, and one focused
test node. It may consume only accepted public domain/application types.

## 6. Fixture Identities

```text
matrix-b2
row-current-rating
group-1 / g1 / Group 1
group-2 / g2 / Group 2
cell-1 / cell-2
```

Both Groups use sample quantity `5`; both Cells use value `1`. The row is
`CURRENT RATING` with condition `300A`. Identities must remain distinct and
internally linked.

## 7. Validation

Future validation is frozen across:

- new B2 node;
- accepted Child 1 Base Fee policy and rule-resolution tests;
- clean-HEAD legacy service test;
- accepted Child 2 duration/dependent-field unit and API/V2 tests;
- accepted V2 attestation/automatic-build tests;
- py_compile;
- line count, UTF-8, trailing, diff-check, exact whitelist, forbidden-path,
  index, and no-real-data scans.

All commands are listed in the task and plan. No dirty test may be treated as
accepted evidence.

## 8. Old Residual Disposition

The old `22/0` node remains untouched until the bounded replacement is
accepted.

The `16/13` support hunk remains a duplicate/support discard candidate. It is
not required by the new local fixture.

Neither may be restored, deleted, staged, or committed without later Reviewer
confirmation and explicit User cleanup authorization.

## 9. Locked Scope

- all product files;
- old mixed service test;
- B1 accepted package and old frontend residual;
- B3 parser;
- all duplicate/support hunks and Child C;
- API/schema/database/seeds/manifests/frontend/dependencies;
- real data/files, generated artifacts, remote refs;
- stage, commit, push, cleanup, restore, and discard.

## 10. Planner Validation

Planner verified:

- one exact task ID/lane/path/budget across task, plan, evidence, and board;
- Developer tests-only implementation complete / pending Reviewer diff
  re-gate status;
- B1 accepted commit remains HEAD ancestor;
- old test line/hash/numstat unchanged;
- new bounded path is the sole tests-only candidate at 276 lines with the
  Reviewer-confirmed SHA-256;
- no product or test edits;
- index empty;
- UTF-8, trailing, diff-check, stale-status, and scope scans clean.

## 11. Next Legal Role

```text
Reviewer RELEASE_006B2 tests-only diff re-gate
```

The exact bounded B2 candidate and all product paths are locked pending
Reviewer re-gate. Do not route QA or Integrator or perform discard, cleanup,
stage, commit, or push.
