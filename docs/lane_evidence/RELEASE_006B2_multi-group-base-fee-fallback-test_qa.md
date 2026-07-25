# RELEASE_006B2 QA Evidence

Date: 2026-07-25
Role: QA / Smoke Owner
Status: `qa_pass`
Task: `RELEASE_006B2_MULTI_GROUP_BASE_FEE_FALLBACK_TEST`
Lane: `multi-group-base-fee-fallback-test`

## Isolated Validation Source

- Exact committed baseline: `168871302b4ad3522b803391b8d7be9838e96570`.
- Created a disposable archive under `%TEMP%` and injected only
  `tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py`.
- The archive test copy and candidate SHA-256 matched:
  `e5ad7212f5751db49e25535471dfe4a2ea9139e031668270b6e292e1d28a181d`.
- No dirty legacy test or product path was copied into the isolated test input.
- Per the active instruction, the temporary archive is retained; no cleanup action was run.

## Commands And Results

```text
py -m pytest --basetemp .qa_b2_exact \
  tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py::\
  test_multi_group_draft_applies_common_base_fee_fallback_per_owning_line -q
=> 1 passed

py -m pytest --basetemp .qa_b2_child1 \
  tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py \
  tests/unit/test_confirmed_matrix_fee_base_fee_policy.py \
  tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py \
  tests/unit/test_confirmed_matrix_fee_draft_service.py -q
=> 42 passed

Child 2 duration/default regressions
=> 21 passed

TASK_361L/TASK_363D V2 automatic-build/attestation regressions
=> 20 passed

py -m py_compile tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py
=> passed
```

The exact node proved one provider read, distinct two-Group identities, one Current Rating line per owning Group, `600/5/0/0/3000` outputs, Base Fee auto-fill metadata, safe row records, and the canonical automatic-default fingerprint.

## Scope Checks

- Candidate is strict UTF-8, `276` physical lines (`<=300`), and has no trailing whitespace.
- Locked mixed test remains `683` lines, SHA-256 `716d76d265ffc892146c0271f543455e004e8e649629733bab125453b3ffbbf0`, with its existing excluded `38/13` residual.
- No B2 diff in `backend/**`, API client, `package.json`, or `package-lock.json`.
- `git diff --check` and `git diff --cached --check` passed; index remains empty.
- Candidate static scan found no real-data, public-drive, workbook, or generated-artifact path.
- B1 old `114/0`, B3, Child C, support/generalization hunk, and all external residuals remain excluded.

QA gate: pass.

Recommended next role: Integrator packaging/readiness. Package only the bounded B2 test and approved B2 governance/evidence; do not stage the old mixed test or any residual.
