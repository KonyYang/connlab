# Fee Rule Resolution Matrix Base Fee Policy - QA Evidence

Date: 2026-07-23

## Result

`qa_pass` for the authorized Child 1 product plus four-node tests-only migration.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation. The board records no global active task and an earlier pending tests-only state; the delegated Reviewer implementation re-gate and current evidence authorize this QA pass. QA did not alter the board.

## Disposable Validation

```powershell
py -m pytest tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py tests/unit/test_confirmed_matrix_fee_draft_service.py tests/unit/test_confirmed_matrix_fee_base_fee_policy.py tests/unit/test_confirmed_matrix_fee_rule_resolution.py tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py -q --basetemp tmp/qa_fee_rule_child1
```

- Child 1 plus both owning legacy suites: `57 passed in 0.93s`.
- Additional accepted V2 protection sweep: `40 passed in 2.60s` across pricing-draft persistence, prior-default attestation, rule-resolution/reviewed rebase, V2 API, CR Measurement Plan rebase, and Measurement Plan rebase-attestation modules.
- `py_compile` passed for the three product modules, three bounded tests, and two legacy test modules.
- Both disposable pytest roots were confirmed under `tmp/` and removed. No real database, workbook, public-drive path, attachment, or generated business artifact was accessed.

## Contract Verification

- Common Base Fee policy always produces the automatic baseline after calculation, while accepted TASK_361L/TASK_363D provenance/rebase preserves a proven manual Base Fee. Structured accepted rule `base_fee.amount`, including explicit zero, wins over fallback zero. Manual fields remain preserved in reviewed rebase coverage.
- Automatic fallback is `0` with source `Matrix Fee automatic Base Fee fallback`; focused tests verify automatic-default/source-context fingerprint and metadata binding.
- Single- and multi-Group coverage uses identical policy tests. `matrix_group_count` has no match in the three product candidates and is not a policy input.
- Testing Fee derives only when Unit Price, Units, and discount are present. Missing dependencies retain review-required/Pending behavior and do not fabricate a value.
- Plain `CONTACT RESISTANCE` does not consume LLCR rule/authority; it remains review-required under the no-fallback boundary.
- Only `Long-term high temperature zone load` resolves to High temperature Life. `Long-term temperature cycle with load` and `Long-term damp heat` remain unmatched/manual-review, including no automatic Unit Price, Units, or Testing Fee.
- The four stale legacy assertion migrations pass and express the accepted Base Fee/CR/temperature behavior.

## Static and Package Checks

- UTF-8 physical lines: draft coordinator `479`, Base Fee policy `147`, rule resolver `51`; bounded tests `187`, `81`, and `301`. Legacy modules are `222` and `683`, both below their pre-migration baselines (`223`/`684`).
- `git diff --check` and no-index checks for untracked bounded tests passed, with only existing LF/CRLF notices. UTF-8 trailing-whitespace and candidate forbidden-content scans were clean.
- Candidate status is limited to the three Child 1 product files, three bounded tests, and the two legacy test files. Staging is empty.
- The legacy test files have mixed historical hunks, including an earlier multi-Group fixture/regression hunk outside the four-node overlay. It was not attributed to this tests-only migration. Integrator must stage the exact four authorized assertion hunks only, not either whole legacy file or the unrelated hunk.
- Child 2/3, the twelve-path umbrella, default-fill/common, seeds/manifests, frontend/API/schema, and the external LLCR API residual remain excluded from this QA package.

## Handoff

Recommended next role: **Integrator packaging/readiness**. Packaging must use the Child 1 whitelist and hunk-level selection for the two mixed legacy test files; do not absorb the external LLCR residual or Child 2/3 paths.
