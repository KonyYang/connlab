# RELEASE_006B2 Final Authorization Reconciliation

Date: 2026-07-25
Role: Planner
Status: Developer tests-only implementation complete / pending Reviewer tests-only diff re-gate
Task: `RELEASE_006B2_MULTI_GROUP_BASE_FEE_FALLBACK_TEST`
Lane: `multi-group-base-fee-fallback-test`
Parent: `RELEASE_006_POST_PUSH_WORKTREE_RESIDUAL_COMMIT_AND_CLEANUP_RECONCILIATION`

## 1. Gate Record

- Child B ownership audit passed.
- B1 is complete/accepted at
  `168871302b4ad3522b803391b8d7be9838e96570`.
- Reviewer passed the B2 plan gate.
- User approved Developer tests-only planning-first.
- Developer completed docs-only planning-first.
- Reviewer passed the B2 implementation-readiness gate.
- User explicitly approved B2 tests-only implementation.
- Developer completed the exact bounded tests-only implementation.
- Reviewer confirmed the candidate and blocked only on stale governance
  source-of-truth.

Product implementation, cleanup, discard, staging, commit, and push remain
unauthorized.

## 2. Exact Authorized Path

The only implementation May Touch is:

```text
tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py
```

The module must remain at or below 300 UTF-8 physical lines including blanks.
No existing test or product file may be edited.

## 3. Frozen Test Contract

The test owns one self-contained public-dataclass fixture:

- one Confirmed Matrix row;
- two Groups;
- one Cell per Group;
- deterministic Current Rating rule resolution.

It calls `build_current_pricing_defaults("P1", service)` once. The local
provider/store counter must prove one authority read. The same build result
supplies the Fee draft, automatic values, ordered identities, row safety, and
source context; a preliminary `build_draft()` call or second provider read is
forbidden.

For each Group-owned Matrix line, the exact result is:

```text
Unit Price  600
Units       5
Base Fee    0
discount    0
Testing Fee 3000
```

The exact Matrix identities are:

```text
matrix-b2:g1:row-current-rating:1:0
matrix-b2:g2:row-current-rating:1:0
```

The full ordered identity sequence must also retain both owning
sample-preparation rows and the report-preparation row. Both Matrix row-safety
records must be safe, identify `fee_rule_temperature_rise`, and include the
required `base_fee` automatic field with source
`Matrix Fee automatic Base Fee fallback`. The source-context
automatic-default fingerprint must equal the canonical fingerprint of the
accepted serialized automatic-values payload.

## 4. Locked Contract

Base Fee precedence remains:

```text
proven manual > accepted rule-specific > automatic 0
```

Single-Group and multi-Group use the same precedence.
`matrix_group_count` is not a trigger or authority. The test must consume
existing public behavior and must not recreate product policy.

The old mixed test remains read-only:

```text
tests/unit/test_confirmed_matrix_fee_draft_service.py
683 UTF-8 physical lines including blanks
SHA-256 716D76D265FFC892146C0271F543455E004E8E649629733BAB125453B3FFBBF0
dirty numstat 38/13
support-only hunk 16/13 excluded
```

B1 old `114/0`, B3, Child C, all product/API/schema/database/frontend paths,
duplicate/support residuals, and cleanup/discard actions remain locked.

## 5. Developer Validation Gate

Developer must prove:

- clean-HEAD coverage RED;
- unchanged-product GREEN;
- exact bounded node passes;
- focused Child 1, Child 2, and V2 regressions pass;
- the new module is at or below 300 physical lines;
- py_compile, UTF-8, trailing, diff-check, whitelist, forbidden-path,
  no-real-data, and staging-empty checks pass.

## 6. Completed Candidate Checkpoint

```text
path       tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py
lines      276 UTF-8 physical lines including blanks
SHA-256    E5AD7212F5751DB49E25535471DFE4A2EA9139E031668270B6E292E1D28A181D
regression 18 + 21 + 20 passed
py_compile passed
```

Reviewer confirmed the single provider read, exact two-Group identities,
`600/5/0/0/3000` values, automatic Base Fee metadata, safe row-safety
evidence, and canonical fingerprint. The old 683-line mixed test, backend
product status, and index remained unchanged.

## 7. Next Legal Role

```text
Reviewer tests-only diff re-gate
```

The product and test candidate are locked. Do not route QA or Integrator
until Reviewer passes the tests-only diff re-gate.
