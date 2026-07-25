# RELEASE_006B3 Damp Heat Extract Row Details Integration Test Planner Evidence

Date: 2026-07-25
Role: Planner
Status: Developer tests-only implementation complete / pending Reviewer tests-only diff re-gate
Task: `RELEASE_006B3_DAMP_HEAT_EXTRACT_ROW_DETAILS_INTEGRATION_TEST`
Lane: `damp-heat-extract-row-details-integration-test`
Parent: `RELEASE_006_POST_PUSH_WORKTREE_RESIDUAL_COMMIT_AND_CLEANUP_RECONCILIATION`
Product implementation authorization: none
Tests-only implementation authorization: exact bounded module only

## 1. Discovery Gate

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Why Planner may act:

- B1 and B2 are complete/accepted;
- User explicitly authorized B3 Planner formalization;
- Child B Reviewer audit already froze the unique hunk, bounded replacement,
  dependencies, and exclusions.

Recommendation: continue. Definition of Ready is satisfied and no blocking
question remains.

## 2. Confirmed Facts

Confirmed by User:

- migrate only real Damp Heat `extract_row_details()` unique `15/0`;
- preserve Thermal Shock `19/0` and Voltage Surge `17/0` as excluded
  duplicate/support residuals;
- keep parser production and the old mixed test read-only;
- route Reviewer plan gate now;
- permit later controlled role gates and a local commit without repeated User
  prompts, but never push.

Confirmed by repository:

- HEAD is `4e492b4cc3537adb70ea161db0cce7c4ad44a089`;
- origin/master...HEAD is `0/3`;
- index is empty;
- accepted Damp Heat commit `44a6153f` is a HEAD ancestor;
- old test facts are 786 lines, SHA-256
  `BC6D61558C7113003ADB8A338BB69D266C1642459D952D23C09530F9F063AF42`,
  dirty `51/0`;
- exact old Damp Heat node is current lines 226-240;
- the bounded future path is absent;
- accepted parser/dispatch/collector plus the exact old Damp Heat node
  currently pass `28` tests.

## 3. Unique Coverage

The accepted parser unit test proves canonical output. The accepted extractor
dispatch test proves route priority using a monkeypatched parser. The unique
old node proves both real layers together.

B3 preserves exactly:

```text
real extract_row_details()
+ real extract_damp_heat_condition()
-> Damp Heat Condition: 85℃, 85% RH, 1000h (mated test)
```

No parser behavior is inferred or changed.

## 4. Exact Future Scope

Only implementation path:

```text
tests/unit/test_spec_section_damp_heat_integration.py
```

Maximum:

```text
<=150 UTF-8 physical lines including blanks
```

The module has one self-contained node and no monkeypatch.

Governance is limited to the B3 task, plan, role evidence, and exact board
hunks.

## 5. Locks

- old 786-line mixed test and all `51/0` hunks;
- parser, Damp Heat helper, collector, Thermal Shock, Voltage Surge, and
  Product Spec Matrix production;
- accepted B1/B2 and TASK_365A/B/C source/tests;
- frontend, Fee, API, schema, database, Matrix, LTR, release, seeds, and
  manifests;
- Child C, pure-empty-line, TASK_364A, stale governance, cleanup/discard, and
  all external residuals;
- real DB/files, public-drive files, attachments, generated artifacts, and
  remote refs.

## 6. Validation Evidence

Read-only Planner probe:

```text
28 passed in 0.20s
```

The command covered the exact dirty Damp Heat node plus accepted parser,
dispatch, and collector modules. It establishes the expected contract only;
the dirty old test is not accepted package evidence.

Future gates require:

- clean-HEAD structural RED;
- unchanged-product GREEN;
- exact bounded node;
- accepted parser/dispatch/collector/TASK_365C regressions;
- clean-HEAD legacy test equivalence;
- py_compile, line, UTF-8, trailing, diff, whitelist, forbidden-path,
  staging-empty, and no-real-data checks.

## 7. Residual Disposition

After B3 acceptance only, the old Damp Heat `15/0` hunk may become an exact
discard candidate. Thermal Shock `19/0` and Voltage Surge `17/0` remain
separate duplicate discard candidates. No cleanup action is authorized.

## 8. Standing Authorization

The User authorized automatic progression through the controlled B3
Planner/Reviewer/Developer/QA/Integrator micro-gates and one later local
commit. This does not remove role gates or expand May Touch. Push remains
unauthorized.

Reviewer plan and implementation-readiness gates passed, and Developer
tests-only planning-first completed. The User's standing authorization now
authorizes the exact bounded tests-only implementation without another
approval request.

Developer subsequently completed the 18-line bounded candidate. Reviewer
confirmed the implementation and blocked only on stale governance status.

## 9. Next Legal Role

```text
Reviewer RELEASE_006B3 tests-only diff re-gate
```

The exact bounded candidate and all product paths are locked pending Reviewer
re-gate. QA/Integrator routing, staging, commit, discard, cleanup, and push
remain unauthorized at this gate.
