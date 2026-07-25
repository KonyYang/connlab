# RELEASE_006B3 Final Tests-Only Authorization Reconciliation

Date: 2026-07-25
Role: Planner
Status: Developer tests-only implementation complete / pending Reviewer tests-only diff re-gate
Task: `RELEASE_006B3_DAMP_HEAT_EXTRACT_ROW_DETAILS_INTEGRATION_TEST`
Lane: `damp-heat-extract-row-details-integration-test`
Parent: `RELEASE_006_POST_PUSH_WORKTREE_RESIDUAL_COMMIT_AND_CLEANUP_RECONCILIATION`

## Gate Record

- B1 and B2 are complete/accepted.
- Child B ownership audit passed.
- Reviewer B3 plan gate passed.
- Developer tests-only planning-first completed.
- Reviewer implementation-readiness passed.
- User standing micro-gate authorization applies to B3 tests-only
  implementation without another approval prompt.

## Exact Authorization

Only this path may be created:

```text
tests/unit/test_spec_section_damp_heat_integration.py
```

The file must remain `<=150` UTF-8 physical lines including blanks. It must
invoke the accepted public `extract_row_details()` and real accepted Damp Heat
parser with the frozen in-memory fixture and assert exactly:

```text
Damp Heat Condition: 85℃, 85% RH, 1000h (mated test)
```

No monkeypatch, private helper, parser reimplementation, product change, or
real file/data access is authorized.

## Locks

The old mixed parser test remains read-only:

```text
tests/unit/test_spec_section_text_extractor.py
786 UTF-8 physical lines including blanks
SHA-256 BC6D61558C7113003ADB8A338BB69D266C1642459D952D23C09530F9F063AF42
dirty numstat 51/0
```

Thermal Shock `19/0`, Voltage Surge `17/0`, parser production, accepted
TASK_365A/B/C, B1/B2, Child C, cleanup/discard, staging, commit, push, and all
external residuals remain locked.

## Developer Gate

Developer must prove clean-HEAD structural RED, unchanged-product GREEN, the
exact bounded node, accepted parser/dispatch/collector/TASK_365C regressions,
clean-HEAD legacy equivalence, py_compile, line/UTF-8/trailing/diff/whitelist,
forbidden-path, no-real-data, and staging-empty checks.

## Completed Candidate Checkpoint

```text
path       tests/unit/test_spec_section_damp_heat_integration.py
lines      18 UTF-8 physical lines including blanks
SHA-256    AD6FDCB4B7EA50B2B9507C8443F20B4A9BA2FF16D6BA54A05ABCBEEABD52AA58
exact      1 passed
focused    36 passed
pycompile  passed
```

Reviewer confirmed the real public extractor and real accepted Damp Heat
parser, exact canonical condition, unchanged 786-line mixed-test
SHA/`51/0`, empty parser-product status, and empty index.

## Next Legal Role

```text
Reviewer tests-only diff re-gate
```

Product and test candidates are locked. QA and Integrator remain later role
gates; no push is authorized.
