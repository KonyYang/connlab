# RELEASE_006B3 Damp Heat Extract Row Details Integration Test Plan

Date: 2026-07-25
Status: Developer tests-only implementation complete / pending Reviewer tests-only diff re-gate
Task: `RELEASE_006B3_DAMP_HEAT_EXTRACT_ROW_DETAILS_INTEGRATION_TEST`
Lane: `damp-heat-extract-row-details-integration-test`
Role: Planner post-implementation source-of-truth reconciliation
Product implementation authorization: none
Tests-only implementation authorization: exact bounded module only

## 1. Planning Decision

Create one bounded tests-only lane for the unique `15/0` real Damp Heat
extractor integration coverage identified by the RELEASE_006 Child B audit.

This is not a parser implementation or behavior change. It moves no code and
does not edit the old mixed test.

## 2. Baseline

```text
HEAD                 4e492b4cc3537adb70ea161db0cce7c4ad44a089
origin/master...HEAD 0/3
index                empty
accepted Damp Heat   44a6153ff4a16674bb15cb804887b774ebdae61f
```

Locked old test:

```text
path      tests/unit/test_spec_section_text_extractor.py
lines     786 UTF-8 physical lines including blanks
SHA-256   BC6D61558C7113003ADB8A338BB69D266C1642459D952D23C09530F9F063AF42
numstat   51/0
```

Residual arithmetic:

```text
15 unique Damp Heat + 19 duplicate Thermal Shock + 17 duplicate Voltage Surge = 51
```

The new bounded path is absent from HEAD and the working tree.

## 3. Coverage Gap

Accepted tests already prove:

- `extract_damp_heat_condition()` canonical parsing and negatives;
- extractor dispatch ordering through a monkeypatched parser;
- condition collector behavior;
- Thermal Shock and Voltage Surge parser and Product Spec Matrix integration.

The unique gap is one node that invokes real `extract_row_details()` and the
real Damp Heat parser together and asserts the exact canonical condition.

## 4. Exact Implementation Design

New module:

```text
tests/unit/test_spec_section_damp_heat_integration.py
```

Budget:

```text
<=150 UTF-8 physical lines including blanks
```

One node:

```text
test_extract_row_details_uses_real_damp_heat_parser_for_canonical_condition
```

The test directly imports the public `extract_row_details`, provides a local
section/test-item/text fixture, and asserts:

```text
Damp Heat Condition: 85℃, 85% RH, 1000h (mated test)
```

It uses no monkeypatch, private helper, filesystem fixture, parser
reimplementation, or product-side branch.

## 5. Exact Fixture

```python
section = "8.9"
test_item = "Long-term damp heat"
section_text = (
    "8.9 Long-term damp heat. "
    "Damp Heat Condition: 85℃, 85% RH, 1000h (mated test). After aging: "
    "Insulation resistance, withstand voltage and contact resistance shall meet "
    "the requirements."
)
```

The assertion is condition-only. Method and requirement behavior are outside
the unique hunk and remain covered by accepted tests.

## 5.1 Verified Public Call And Data Flow

The future test imports exactly:

```python
from backend.modules.test_plan.spec_section_text_extractor import (
    extract_row_details,
)
```

It calls the keyword-only public signature:

```python
extract_row_details(
    *,
    section: str,
    section_text: str,
    test_item: str | None = None,
    applicable_specifications: str | None = None,
) -> MatrixRowDetailExtraction
```

The accepted production path is:

```text
extract_row_details
  -> clean and strip the 8.9 heading
  -> _extract_condition
  -> exact "damp heat" dispatch
  -> extract_damp_heat_condition
  -> collect_condition_segments
  -> quantitative-fact filtering
  -> accepted fallback/normalization pipeline
  -> MatrixRowDetailExtraction.condition
```

The fixture supplies all data in memory. There is no repository, database,
filesystem, Office, network, API, frontend, or generated-artifact boundary.
The test must assert only:

```python
assert detail.condition == (
    "Damp Heat Condition: 85℃, 85% RH, 1000h (mated test)"
)
```

That equality also proves the trailing `After aging:` requirement prose does
not leak into the canonical condition. The test must not assert method,
requirement, notes, or status because those are not part of the unique
residual contract.

## 6. Exact May Touch

Implementation:

```text
tests/unit/test_spec_section_damp_heat_integration.py
```

Governance:

```text
tasks/RELEASE_006B3_DAMP_HEAT_EXTRACT_ROW_DETAILS_INTEGRATION_TEST.md
docs/release_006b3_damp_heat_extract_row_details_integration_test_plan.md
docs/lane_evidence/RELEASE_006B3_damp-heat-extract-row-details-integration-test_planner.md
future exact B3 role evidence
docs/task_board.md exact B3 hunks
```

Mixed files may never be staged whole.

## 7. Locked Paths

Read-only:

```text
tests/unit/test_spec_section_text_extractor.py
tests/unit/test_damp_heat_condition_parser.py
tests/unit/test_spec_section_damp_heat_dispatch.py
tests/unit/test_condition_text_collectors.py
tests/unit/test_task_365c_product_spec_matrix_parser.py
tests/unit/test_thermal_shock_condition_parser.py
tests/unit/test_voltage_surge_condition_parser.py
backend/modules/test_plan/spec_section_text_extractor.py
backend/modules/test_plan/damp_heat_condition_parser.py
backend/modules/test_plan/condition_text_collectors.py
```

All product, frontend, Fee, API, schema, database, Matrix, LTR, release,
cleanup, historical-governance, real-data, file-authority, and generated
artifact paths are forbidden.

## 8. TDD

RED is structural and coverage-specific:

- exact clean HEAD has no bounded B3 path/node;
- accepted coverage lacks one real extractor + real parser exact-condition
  integration node.
- `git grep` against clean HEAD must find no accepted node with the frozen
  name or equivalent real-path assertion.

GREEN adds only the new bounded test against unchanged accepted production.

No product change is permitted to make GREEN pass.

The future module should fit in approximately 20-35 physical lines:

- 3-5 import lines;
- one test definition;
- one local literal fixture;
- one public call;
- one exact assertion.

No shared fixture, helper, parametrization, monkeypatch, copied parser
predicate, or dependency is justified. The hard package maximum remains
`<=150` UTF-8 physical lines including blanks.

## 9. Regression Commands

Exact node:

```powershell
py -m pytest tests/unit/test_spec_section_damp_heat_integration.py -q
```

Accepted parser/dispatch/collector/TASK_365C gate:

```powershell
py -m pytest tests/unit/test_damp_heat_condition_parser.py tests/unit/test_spec_section_damp_heat_dispatch.py tests/unit/test_condition_text_collectors.py tests/unit/test_task_365c_product_spec_matrix_parser.py tests/unit/test_thermal_shock_condition_parser.py tests/unit/test_voltage_surge_condition_parser.py -q
```

Legacy equivalence:

- create a disposable narrow archive from exact `HEAD` containing accepted
  parser production and only the frozen read-only regression modules;
- copy only the new bounded test into that archive;
- run the HEAD blob of `tests/unit/test_spec_section_text_extractor.py`
  there;
- never use or stage the dirty `51/0` old-file residual as candidate evidence.
- verify the disposable archive is outside the repository and remove only
  that exact temporary path after validation.

Static gates:

```powershell
py -m py_compile tests/unit/test_spec_section_damp_heat_integration.py
git diff --check
git diff --cached --name-only
```

Also verify exact whitelist, new-file line count, UTF-8, trailing whitespace,
old-test hash/line/numstat, no product diff, no real data, and empty index.

Implementation evidence must record:

- structural clean-HEAD RED;
- exact bounded-node GREEN;
- accepted focused parser/dispatch/collector/TASK_365C result;
- clean-HEAD legacy equivalence result;
- `py_compile`;
- new-file physical lines and SHA-256;
- locked old-file `786` lines, SHA-256
  `BC6D61558C7113003ADB8A338BB69D266C1642459D952D23C09530F9F063AF42`,
  and unchanged `51/0` numstat;
- product/test whitelist, no-real-data, and empty-index checks.

## 10. Package Boundary

The future implementation package contains:

- the one new bounded test;
- B3 task/plan/role evidence;
- exact B3 board hunks.

It excludes the old mixed test and every existing residual. Integrator may
create one local tests-only commit only after Reviewer and QA gates pass.
Remote push remains unauthorized.

## 11. Rollback And Cleanup

Before acceptance, omit the new test. After acceptance, revert only the B3
local commit.

The old Damp Heat `15/0` hunk becomes a discard candidate only after B3
acceptance. Thermal Shock `19/0` and Voltage Surge `17/0` remain separate
duplicate discard candidates. No discard/restore action is in this lane.

## 12. Gate Sequence

User standing authorization covers the controlled micro-gates, not scope
expansion:

```text
Reviewer plan
-> Developer tests-only planning-first
-> Reviewer readiness
-> Developer tests-only implementation
-> Reviewer diff
-> QA
-> Integrator local commit
```

Every role must update evidence and stop at its gate. No role may push.

## 13. Current Stop

```text
Reviewer RELEASE_006B3 tests-only diff re-gate
```

Developer completed the exact 18-line bounded test. Reviewer independently
confirmed SHA-256
`AD6FDCB4B7EA50B2B9507C8443F20B4A9BA2FF16D6BA54A05ABCBEEABD52AA58`,
exact `1`, focused `36`, and pycompile. Product and test candidates are locked
pending Reviewer re-gate. QA, Integrator, staging, commit, cleanup, discard,
and push remain unauthorized until their later role gates.
