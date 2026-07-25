# RELEASE_006B3 Developer Tests-Only Implementation Evidence

Date: 2026-07-25
Role: Developer bounded tests-only implementation
Status: `ready_for_reviewer_tests_only_diff_gate`
Task: `RELEASE_006B3_DAMP_HEAT_EXTRACT_ROW_DETAILS_INTEGRATION_TEST`
Lane: `damp-heat-extract-row-details-integration-test`
Parent: `RELEASE_006_POST_PUSH_WORKTREE_RESIDUAL_COMMIT_AND_CLEANUP_RECONCILIATION`
Product implementation authorization: none
Test implementation authorization: exact bounded module only after Reviewer readiness and Planner reconciliation

## Planning-First Gate (Historical)

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

This docs-only role action is legal because:

- upstream RELEASE_006B2 is complete/accepted at
  `4e492b4cc3537adb70ea161db0cce7c4ad44a089`;
- RELEASE_006B3 Reviewer evidence records `reviewer_plan_pass`;
- the User's standing micro-gate authorization explicitly allows Developer
  tests-only planning-first without another approval request.

The standing authorization does not authorize creation of the bounded test,
product changes, cleanup, staging, commit, or push.

## Required Reads

Read as UTF-8 and applied:

- `AGENTS.md`;
- `docs/task_board.md`;
- RELEASE_006B3 task, plan, Planner evidence, and Reviewer evidence;
- `docs/project_management/TASK_EXECUTION_SKILL.md`;
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`;
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`;
- accepted `spec_section_text_extractor.py`;
- accepted `damp_heat_condition_parser.py`;
- accepted `condition_text_collectors.py`;
- focused parser, dispatch, collector, TASK_365C, Thermal Shock, and Voltage
  Surge tests;
- the exact dirty legacy Damp Heat node and surrounding excluded hunks.

No implementation test, dependency installation, generated-output command,
database command, or product execution was run.

## Repository Baseline

```text
HEAD                 4e492b4cc3537adb70ea161db0cce7c4ad44a089
branch               master
origin/master...HEAD 0/3
index                empty
worktree             51 paths = 37 tracked + 14 untracked
accepted Damp Heat   44a6153ff4a16674bb15cb804887b774ebdae61f
accepted ancestor    yes
```

Locked legacy test:

```text
path      tests/unit/test_spec_section_text_extractor.py
lines     786 UTF-8 physical lines including blanks
SHA-256   BC6D61558C7113003ADB8A338BB69D266C1642459D952D23C09530F9F063AF42
numstat   51/0
```

The diff remains exactly:

```text
15/0 unique Damp Heat integration
19/0 excluded Thermal Shock duplicate coverage
17/0 excluded Voltage Surge duplicate coverage
```

Future bounded path:

```text
tests/unit/test_spec_section_damp_heat_integration.py
absent
```

## Technical Verification

### Public boundary

The future test can directly import:

```python
from backend.modules.test_plan.spec_section_text_extractor import (
    extract_row_details,
)
```

The public function is keyword-only and returns
`MatrixRowDetailExtraction`. The relevant observable is its public
`condition` field.

### Real production flow

The accepted call flow is:

```text
extract_row_details
  -> source cleaning and section-heading removal
  -> _extract_condition
  -> Damp Heat dispatch before generic humidity
  -> extract_damp_heat_condition
  -> collect_condition_segments
  -> explicit quantitative/source-fact filtering
  -> accepted fallback and normalization
  -> detail.condition
```

Accepted focused coverage currently proves:

- the parser's exact canonical Damp Heat output and negative boundaries;
- dispatch priority through a monkeypatched parser;
- collector ordering/filtering;
- accepted TASK_365C/Thermal Shock/Voltage Surge behavior.

It does not provide one accepted bounded node that uses the real extractor
and real Damp Heat parser together. The old `15/0` node is therefore unique.

### Exact fixture and output

The future test uses one in-memory fixture:

```text
section      8.9
test_item    Long-term damp heat
facts        Damp Heat Condition: 85℃, 85% RH, 1000h (mated test)
tail         After aging: Insulation resistance, withstand voltage and
             contact resistance shall meet the requirements.
```

Exact output:

```text
Damp Heat Condition: 85℃, 85% RH, 1000h (mated test)
```

Exact equality proves the trailing prose is excluded. Method, requirement,
notes, status, generic humidity negatives, Thermal Shock, and Voltage Surge
are intentionally outside this one-node contract.

## Executable Test Design

Future sole test May Touch:

```text
tests/unit/test_spec_section_damp_heat_integration.py
```

Frozen node:

```text
test_extract_row_details_uses_real_damp_heat_parser_for_canonical_condition
```

The module owns:

1. one public import;
2. one test function;
3. one local literal source block;
4. one public function call;
5. one exact `detail.condition` assertion.

Forbidden inside the test:

- monkeypatch;
- private parser/helper imports;
- copied parsing or condition-fact logic;
- filesystem, database, API, Office, network, or generated-output fixtures;
- method/requirement assertions from unrelated coverage;
- shared helper or dependency additions.

Estimated size is 20-35 UTF-8 physical lines. The frozen hard maximum is
`<=150`, including blanks.

## TDD And Validation

Coverage RED is structural:

- clean accepted HEAD has no bounded B3 path or node;
- `git grep` against clean HEAD has no equivalent accepted real-path
  assertion;
- accepted parser/dispatch tests split the two layers and do not close the
  integration gap.

Unchanged-product GREEN:

- add only the bounded test;
- run it against accepted production;
- require zero product diff and unchanged locked-test facts.

Future exact command:

```powershell
py -m pytest tests/unit/test_spec_section_damp_heat_integration.py -q
```

Future focused accepted regression:

```powershell
py -m pytest tests/unit/test_damp_heat_condition_parser.py tests/unit/test_spec_section_damp_heat_dispatch.py tests/unit/test_condition_text_collectors.py tests/unit/test_task_365c_product_spec_matrix_parser.py tests/unit/test_thermal_shock_condition_parser.py tests/unit/test_voltage_surge_condition_parser.py -q
```

Legacy equivalence must run in a disposable narrow archive reconstructed
from exact HEAD. Copy only the future bounded test into that archive; never
use or stage the dirty `51/0` legacy file as package evidence.

Static validation:

- `py_compile` for the bounded test;
- UTF-8 decode and blank-inclusive physical-line count;
- trailing-whitespace and no-index diff checks;
- exact whitelist and forbidden-path/content scans;
- old-test line/hash/numstat verification;
- product-diff and no-real-data checks;
- empty index.

## May Touch And Locks

Current docs-only writes:

- `docs/task_board.md` exact B3 status/route hunks only;
- `tasks/RELEASE_006B3_DAMP_HEAT_EXTRACT_ROW_DETAILS_INTEGRATION_TEST.md`;
- `docs/release_006b3_damp_heat_extract_row_details_integration_test_plan.md`;
- this Developer evidence.

Future implementation May Touch remains only:

```text
tests/unit/test_spec_section_damp_heat_integration.py
```

Locked:

- old 786-line mixed test and all `51/0` hunks;
- extractor, Damp Heat parser, and condition collector production;
- accepted parser/dispatch/collector/TASK_365C/Thermal Shock/Voltage Surge
  tests except read-only future execution;
- accepted B1/B2 source and tests;
- B3 duplicate/support residuals, Child C, cleanup, and historical
  governance residuals;
- Fee, frontend, API, schema, database, Matrix, LTR, release, seeds,
  manifests, dependencies, real DB/files, public-drive files, attachments,
  generated artifacts, and remote refs;
- discard, restore, cleanup, stage, commit, and push.

## Risk, Rollback, And Isolation

- False integration coverage: prohibited monkeypatch/private imports ensure
  both real layers execute.
- Parser duplication: the test asserts output only and contains no parser
  predicate.
- Trailing prose leak: exact equality catches accidental suffix inclusion.
- Dirty residual absorption: clean-HEAD archive validation and old-file
  hash/numstat checks isolate the candidate.
- Scope growth: one node and a 150-line cap prevent unrelated parser
  coverage from entering B3.

Before acceptance, rollback means omitting only the future bounded test. The
old `15/0` hunk does not become a discard candidate until later acceptance;
no cleanup action is part of this gate.

## Developer Self-Review

- Goal, input, output, modules, and public signature: verified.
- Unique integration gap: verified against real code and tests.
- Data fixture: complete, deterministic, and in memory.
- Expected canonical output: literal and source-faithful.
- No product/API/data/schema/Office boundary: confirmed.
- Line budget: executable with substantial headroom.
- TDD, regression, rollback, and package isolation: explicit.
- TODOs/placeholders: none.
- Out-of-scope implementation action: none.

## Planning Validation (Historical)

No pytest, pycompile, dependency, build, product execution, database,
generated-output, or real-file command was run in this docs-only pass.

```text
UTF-8 physical lines including blanks
  board       2402
  task         198
  plan         315
  evidence     291 before this validation update

UTF-8 trailing whitespace
  0 across board/task/plan/evidence

untracked task/plan/evidence no-index diff-check
  expected add-file exit 1
  no whitespace error

tracked repository git diff --check
  passed
  existing LF/CRLF notices only

locked old mixed test
  786 physical lines
  SHA-256 BC6D61558C7113003ADB8A338BB69D266C1642459D952D23C09530F9F063AF42
  existing numstat 51/0

future bounded test path
  absent

status alignment
  exact B3 board/task/plan/evidence hunks point to
  Reviewer implementation-readiness gate

product/test scope
  no product or test path created, edited, restored, or removed
  existing old mixed-test residual remains read-only

index
  empty
```

The board was already a mixed dirty governance file. This pass changed only
the exact B3 header, active-lane summary, and B3 row; no whole-file staging
or unrelated board reconciliation occurred.

## Planning Result (Historical)

```text
developer_plan_ready_for_reviewer_implementation_readiness_gate
```

Remaining blocker: none for Reviewer implementation-readiness.

Next legal role: Reviewer. Tests-only implementation, QA, Integrator,
discard, cleanup, staging, commit, and push remain unauthorized.

## Post-Readiness Source-Of-Truth Reconciliation

The planning-first checkpoint above is historical and remains valid.
Reviewer implementation-readiness subsequently passed, and Planner recorded
the User's standing micro-gate authorization. Current lane status is:

```text
tests-only implementation authorized / pending Developer implementation
```

The next legal role is Developer bounded tests-only implementation. Only
`tests/unit/test_spec_section_damp_heat_integration.py` may be created.
Product code, the old mixed test, QA/Integrator routing, discard, cleanup,
staging, commit, and push remain locked.

## Tests-Only Implementation

Created only:

```text
tests/unit/test_spec_section_damp_heat_integration.py
```

The bounded module contains one 18-line self-contained test. It:

- imports the accepted public `extract_row_details`;
- invokes the keyword-only entry with the frozen section, item, explicit
  Damp Heat facts, and trailing `After aging:` prose;
- uses the real accepted Damp Heat parser with no monkeypatch or private
  helper;
- asserts only the exact canonical `condition`;
- contains no copied parser logic, filesystem fixture, or unrelated
  Thermal Shock, Voltage Surge, method, requirement, or negative coverage.

No product or locked legacy test was modified.

## RED And GREEN Evidence

Structural clean-HEAD RED:

```text
git ls-tree HEAD
  no tests/unit/test_spec_section_damp_heat_integration.py

git grep planned node against HEAD
  no match
```

Unchanged-product GREEN:

```text
py -m pytest tests/unit/test_spec_section_damp_heat_integration.py -q
1 passed in 0.07s
```

Accepted focused parser/dispatch/collector/TASK_365C regression:

```text
36 passed in 0.32s
```

Clean-HEAD legacy equivalence:

- reconstructed a disposable narrow archive from exact `HEAD`;
- included accepted parser production and the HEAD blob of the old mixed
  test;
- copied only the bounded B3 test into the archive;
- ran the bounded test, six accepted focused modules, and clean-HEAD legacy
  module together;
- removed only the exact temporary archive/root after validation.

```text
86 passed in 0.22s
```

Compilation:

```text
py -m py_compile tests/unit/test_spec_section_damp_heat_integration.py
passed
```

## Implementation Package Checks

```text
new bounded test
  physical lines including blanks  18 (limit <=150)
  SHA-256                         AD6FDCB4B7EA50B2B9507C8443F20B4A9BA2FF16D6BA54A05ABCBEEABD52AA58
  UTF-8 trailing whitespace       0
  real/generated path references  0
  no-index diff-check             expected add-file exit 1; no whitespace error

locked old mixed test
  physical lines including blanks  786
  SHA-256                         BC6D61558C7113003ADB8A338BB69D266C1642459D952D23C09530F9F063AF42
  existing numstat                51/0

parser product status
  empty

repository checks
  tracked git diff --check passed; existing LF/CRLF notices only
  candidate test/evidence no-index diff-check has no whitespace error
  candidate test has no real/generated path reference

index
  empty
```

The worktree remains dirty with external residuals. They were neither
cleaned nor absorbed. No real database, public-drive file, attachment,
generated artifact, dependency, stage, commit, or push action occurred.

## Implementation Result

```text
ready_for_reviewer_tests_only_diff_gate
```

Remaining blocker: none for Reviewer tests-only diff gate.

Next legal role: Reviewer. QA, Integrator, discard, worktree cleanup,
staging, commit, and push remain unauthorized in this role action.
