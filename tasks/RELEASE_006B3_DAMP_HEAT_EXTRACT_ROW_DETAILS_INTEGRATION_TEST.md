# RELEASE_006B3 Damp Heat Extract Row Details Integration Test

Date: 2026-07-25
Status: Developer tests-only implementation complete / pending Reviewer tests-only diff re-gate
Lane: `damp-heat-extract-row-details-integration-test`
Parent: `RELEASE_006_POST_PUSH_WORKTREE_RESIDUAL_COMMIT_AND_CLEANUP_RECONCILIATION`
Source audit: `RELEASE_006B_TEST_RESIDUAL_OWNERSHIP_AUDIT`
Upstream B2: complete/accepted at `4e492b4cc3537adb70ea161db0cce7c4ad44a089`
Product implementation authorization: none
Tests-only implementation authorization: exact bounded module only
Discard authorization: none
Push authorization: none

## 1. Goal

Move the one unique real Damp Heat `extract_row_details()` integration
contract out of the oversized mixed parser test and into a bounded tests-only
module.

The exact source residual is:

```text
tests/unit/test_spec_section_text_extractor.py
test_long_term_damp_heat_extracts_temperature_humidity_and_duration
15/0 unique hunk
```

Thermal Shock `19/0` and Voltage Surge `17/0` are accepted semantic
duplicates. They are not part of this lane.

## 2. Discovery Decision

Confirmed by User:

- formalize B3 only;
- migrate the unique Damp Heat `15/0` integration coverage;
- keep the old mixed parser test read-only;
- preserve parser production unchanged;
- run the controlled Reviewer, Developer, QA, and Integrator sequence;
- allow only a later controlled local commit, never an automatic push.

Confirmed by repository:

- current HEAD is
  `4e492b4cc3537adb70ea161db0cce7c4ad44a089`;
- accepted Damp Heat parser package
  `44a6153ff4a16674bb15cb804887b774ebdae61f` is a HEAD ancestor;
- the old test is 786 UTF-8 physical lines including blanks, SHA-256
  `BC6D61558C7113003ADB8A338BB69D266C1642459D952D23C09530F9F063AF42`,
  and dirty `51/0`;
- accepted bounded tests prove parser behavior and dispatch separately, but
  the dispatch test monkeypatches the parser;
- no accepted bounded node calls real `extract_row_details()` and asserts the
  exact canonical Damp Heat condition;
- the proposed new path is absent.

Planner inference:

- the audit-frozen path and `<=150` budget are narrower than the User's
  `<=250` maximum and therefore control this lane.

No unresolved assumption affects scope, validation, or ownership.

## 3. Accepted Behavior

The new bounded test must call the accepted public function:

```python
extract_row_details(
    section="8.9",
    section_text=(
        "8.9 Long-term damp heat. "
        "Damp Heat Condition: 85℃, 85% RH, 1000h (mated test). After aging: "
        "Insulation resistance, withstand voltage and contact resistance shall meet "
        "the requirements."
    ),
    test_item="Long-term damp heat",
)
```

The exact assertion is:

```text
Damp Heat Condition: 85℃, 85% RH, 1000h (mated test)
```

This proves the real extractor dispatches to the real accepted Damp Heat
parser and excludes trailing prose. It must not monkeypatch, copy, or
reimplement parser logic.

## 4. Exact Future May Touch

Tests-only implementation:

```text
tests/unit/test_spec_section_damp_heat_integration.py
```

Governance:

```text
tasks/RELEASE_006B3_DAMP_HEAT_EXTRACT_ROW_DETAILS_INTEGRATION_TEST.md
docs/release_006b3_damp_heat_extract_row_details_integration_test_plan.md
docs/lane_evidence/RELEASE_006B3_damp-heat-extract-row-details-integration-test_planner.md
future role evidence for this exact lane
docs/task_board.md exact B3 hunks only
```

No other path is authorized.

## 5. Must Not Touch

- `tests/unit/test_spec_section_text_extractor.py`;
- `backend/modules/test_plan/spec_section_text_extractor.py`;
- `backend/modules/test_plan/damp_heat_condition_parser.py`;
- `backend/modules/test_plan/condition_text_collectors.py`;
- accepted Damp Heat, TASK_365A/B/C, B1, and B2 source/tests;
- Thermal Shock `19/0` and Voltage Surge `17/0` old hunks;
- Fee, frontend, API, schema, database, seeds, manifests, Matrix, LTR, and
  release packaging;
- pure-empty-line, TASK_364A, governance, cleanup, and external residuals;
- real DB/files, public-drive files, attachments, and generated artifacts.

The old mixed test is read-only regression input. Whole-file or hunk staging
from it is forbidden.

## 6. Bounded Test Contract

The new module:

- contains one self-contained fixture/node;
- imports only the accepted public `extract_row_details`;
- uses no monkeypatch and no private parser helper;
- asserts the exact canonical condition;
- remains `<=150` UTF-8 physical lines including blanks;
- adds no dependency and writes no real data.

Accepted parser-unit and dispatch tests own negative/parser-isolation
coverage. B3 must not duplicate Thermal Shock, Voltage Surge, missing-fact, or
generic-humidity cases.

## 7. Validation

RED:

- from exact clean HEAD, the bounded path/node is absent;
- no accepted bounded test provides this exact real-path assertion.

GREEN:

```powershell
py -m pytest tests/unit/test_spec_section_damp_heat_integration.py -q
```

Focused accepted regressions:

```powershell
py -m pytest tests/unit/test_damp_heat_condition_parser.py tests/unit/test_spec_section_damp_heat_dispatch.py tests/unit/test_condition_text_collectors.py tests/unit/test_task_365c_product_spec_matrix_parser.py tests/unit/test_thermal_shock_condition_parser.py tests/unit/test_voltage_surge_condition_parser.py -q
```

The accepted HEAD version of the old mixed parser test must be executed from
an isolated clean-HEAD package. Validation also requires py_compile, UTF-8
decode, physical-line, trailing, diff-check, whitelist, forbidden-path,
staging-empty, and no-real-data checks.

## 8. Residual And Rollback

The original Damp Heat `15/0` hunk becomes an exact discard candidate only
after the bounded replacement is accepted. This task authorizes no discard,
restore, cleanup, or old-test edit.

Before acceptance, rollback omits the new bounded test. After a later accepted
tests-only local commit, rollback reverts only that commit.

## 9. Gate Sequence

The User's standing authorization permits the following controlled sequence
without a new approval request at every micro-gate:

1. Reviewer plan gate;
2. Developer tests-only planning-first;
3. Reviewer implementation-readiness gate;
4. Developer tests-only implementation;
5. Reviewer tests-only diff gate;
6. QA isolated validation;
7. Integrator exact package validation and local commit.

Each role must still stop at its own gate and update evidence. No push is
authorized.

## 10. Implementation Checkpoint

```text
tests/unit/test_spec_section_damp_heat_integration.py
18 UTF-8 physical lines including blanks
SHA-256 AD6FDCB4B7EA50B2B9507C8443F20B4A9BA2FF16D6BA54A05ABCBEEABD52AA58
```

Reviewer confirmed the exact node, focused `36` regressions, pycompile, real
public extractor/parser path, canonical condition, and all old-test/product
locks.

## 11. Current Stop

```text
Reviewer RELEASE_006B3 tests-only diff re-gate
```

Product and test candidates are locked pending Reviewer re-gate. QA,
Integrator, staging, commit, discard, cleanup, and push remain unauthorized
at this gate.
