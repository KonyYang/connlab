# SPEC_PARSER Damp Heat Residual Package Reconciliation - Reviewer Evidence

Date: 2026-07-22

Role: Reviewer

Status: `reviewer_blocked / Planner docs-only fix required`

Task: `SPEC_PARSER_DAMP_HEAT_RESIDUAL_PACKAGE_RECONCILIATION`

Lane: `spec-parser-damp-heat-residual-package-reconciliation`

Implementation authorization: none.

## Review Scope

- Read `AGENTS.md`, the task board, this task, the reconciliation plan, Planner
  evidence, accepted TASK_365A/B/C boundaries, the two residual diffs, and the
  current extractor/test module shape.
- Performed no product or test edits, no real-file/data access, staging, commit, or
  push.

## Findings

### B1: The authorized existing test module cannot be modified under the Python hard limit

The plan marks `tests/unit/test_spec_section_text_extractor.py` as future May Touch
for a Damp Heat integration assertion, but the checked-out file is already 670 UTF-8
physical lines. Adding the current 51-line residual or any new assertion keeps a
touched Python file above the project hard limit of 500 lines.

The same dirty hunk also carries Thermal Shock and Voltage Surge replay tests, which
must not be absorbed into this Damp Heat package because TASK_365C is accepted and
locked. Keeping that whole-file test edit in the candidate would therefore violate
both the size and accepted-package isolation contracts.

### B2: Helper plus narrow dispatch does not make the current extractor compliant

`backend/modules/test_plan/spec_section_text_extractor.py` is 527 UTF-8 physical
lines. The current residual adds five Damp Heat lines. Replacing those lines with a
new helper import and narrow dispatch removes only the residual body; it cannot by
itself reduce the touched extractor to 500 lines or fewer.

The current plan requires every touched/new Python file to remain below 500 lines but
does not identify an exact behavior-preserving extraction of at least 27 physical
lines, its companion module ownership, or regression coverage. Leaving that choice to
implementation would make the file-size contract non-executable.

## Required Planner Docs-Only Fix

1. Remove `tests/unit/test_spec_section_text_extractor.py` from future May Touch for
   this lane. Treat it as read-only regression execution. Move the Damp Heat
   integration case into a new bounded test module, distinct from the new helper unit
   test module. Explicitly exclude the existing dirty Thermal Shock/Voltage Surge
   replay hunk from this candidate; it must not be staged or modified.
2. Freeze an exact, behavior-preserving extractor-size plan that brings
   `spec_section_text_extractor.py` to 500 UTF-8 physical lines or fewer without
   blank-line suppression. Name the minimum additional helper/module and its exact
   responsibility, adjust May Touch/locks accordingly, and add focused regression
   nodes proving accepted non-Damp-Heat paths retain their existing outputs. Do not
   defer the required reduction to Developer discretion.
3. Retain the otherwise sound Damp Heat contract: branch priority before generic
   humidity, source-faithful explicit facts only, EIA-method exclusion, no inference,
   parser-only zero-write behavior, and all TASK_365A/B/C/Fee/UI/API/schema/real-file
   locks.

## Validation Performed

- Board/task/plan/Planner evidence consistently describe this as planned-only and
  implementation unauthorized.
- Current residuals are limited to `5/0` in the extractor and `51/0` in the existing
  test module; the existing focused parser suite is recorded as `52 passed`.
- Confirmed current physical counts: extractor 527 and existing parser test module
  670. Governance diff check is clean aside from the repository LF/CRLF notice; the
  index is empty.

## Next Legal Route

Route only to **Planner docs-only fix pass**. Do not request user approval or route
Developer planning-first, Developer implementation, QA, or Integrator.

## Plan Re-Gate

Date: 2026-07-22

Status: `reviewer_pass`

Implementation authorization: none.

### B1/B2 Closure

- `tests/unit/test_spec_section_text_extractor.py` is now a read-only regression
  dependency, not a May Touch path. The lane instead defines three bounded new test
  modules for Damp Heat parsing, extractor dispatch, and mechanical collector
  equivalence. The mixed Thermal Shock/Voltage Surge dirty replay hunk remains
  explicitly excluded as accepted TASK_365C scope.
- The plan precisely moves `_CONDITION_TOKEN_RE`,
  `_collect_condition_segments(...)`, and `_collect_condition_tokens(...)` into
  `condition_text_collectors.py`, preserving the current cleaner/output semantics.
  It limits extractor changes to imports, the listed generic collector call sites,
  and the Damp Heat dispatch; method/requirement/MFG/Thermal Shock/Voltage Surge/
  Reseating ownership stays locked.
- The existing collector block is sufficient to reduce the current 527-line extractor
  below 500 physical UTF-8 lines after the narrow imports/dispatch are added. The
  plan forbids blank-line suppression, fixes line budgets for every new module, and
  requires old parser regression plus focused collector, dispatch, and Damp Heat
  tests.

### Package Boundary

The contract remains parser-only and self-contained: no Fee/default-fill, UI/API,
schema/database, Matrix, LTR, release, real-file, generated-artifact, or accepted
TASK_365A/B/C behavior may change. Rollback is limited to the new helpers/tests and
the mechanical extractor hunks.

## Validation Performed

- Re-read task, plan, Planner evidence, board, the earlier Reviewer blockers, and
  the live collector/condition source boundaries.
- Confirmed current facts remain extractor 527 lines, old parser test 670 lines,
  focused read-only parser regression `52 passed`, targeted governance diff clean
  apart from the existing LF/CRLF notice, and an empty index.

## Next Legal Route

Route only to **User approval / Developer planning-first**. Implementation remains
unauthorized; do not route Developer implementation, QA, or Integrator directly.

## Implementation-Readiness Gate

Date: 2026-07-22

Status: `reviewer_blocked / Planner docs-only fix required`

Implementation authorization: none.

### B3: The collector helper has conflicting controlling line budgets

The physical-line source of truth is now correctly reconciled to extractor `596` and
old parser test `786`, using checked-out UTF-8 `Get-Content(...).Count`; the older
nonblank `527` / `670` values are properly historical only. The expanded mechanical
split is otherwise implementation-ready: it identifies the collector regex/functions
and four pure condition helpers, exact public helper names/call sites, parity tests,
read-only old-test behavior, and an extractor target below 500.

However, the controlling task gives the new
`backend/modules/test_plan/condition_text_collectors.py` a target **under 120**
physical lines, while the plan gives the same helper a budget **`<=150`**. Both cannot
be the future acceptance rule. The helper carries 110 current source lines before its
imports/private cleaner and should have one explicit, consistent budget before a
Developer is asked to implement it.

## Required Planner Docs-Only Fix

Choose one maximum for `condition_text_collectors.py` and make task, plan, Planner,
Developer, reconciliation, board, and future validation scan use that exact same
threshold. Preserve the current public-helper/call-site list, `<=500` project hard
limit, no-blank-line-suppression rule, read-only 786-line test, mechanical parity
matrix, and all accepted TASK_365A/B/C/package locks. Do not change product or test
code.

## Validation Performed

- Re-read the reconciled task/plan/Planner/Developer evidence and live extractor
  helper ranges.
- Confirmed checked-out physical counts with `Get-Content(...).Count`: extractor
  `596`, old test `786`; nonblank `Measure-Object -Line` values are `527` / `670`.
- Confirmed the only active readiness discrepancy is the task's under-120 versus
  plan's `<=150` collector-helper budget. Governance diff checks are clean apart
  from the existing LF/CRLF notice; the index remains empty.

## Next Legal Route

Route only to **Planner docs-only fix pass**. Do not request implementation approval
or route Developer implementation, QA, or Integrator.

## Implementation-Readiness Re-Gate

Date: 2026-07-22

Status: `reviewer_pass`

Implementation authorization: none.

### B3 Closure

The single effective `condition_text_collectors.py` budget is now `<=150` UTF-8
physical lines including blanks across the task, plan, Planner evidence,
reconciliation evidence, board, and validation command. The earlier under-120 target
is explicitly superseded. This budget accommodates the frozen 110-line mechanical
source extraction and remains well below the project 500-line hard limit.

The rest of the readiness contract remains precise and unchanged:

- checked-out physical facts are extractor `596` and read-only old parser test `786`;
- the extractor must end below `500` through the enumerated generic collector plus
  electrical, temperature-rise, dust, and durability helper move;
- all collector APIs/call sites, cleaner parity, dispatch priority, focused tests,
  and line scans are specified;
- the old test and its mixed TASK_365C replay hunk remain excluded; TASK_365A/B/C and
  all non-parser scopes stay locked.

## Validation Performed

- Re-read task, plan, Planner and reconciliation evidence, board, prior Reviewer
  B3 finding, and current source count facts.
- Confirmed no active under-120 collector budget remains in the controlling sources;
  `<=150` is used by the future validation command.
- Governance diff check is clean apart from the existing LF/CRLF notice; index is
  empty. No product/test, real-data/file, staging, commit, or push operation occurred.

## Next Legal Route

Route only to **User product implementation approval + Planner final source-of-truth
reconciliation**. Do not route Developer implementation, QA, or Integrator directly.

## Implementation Gate

Date: 2026-07-22

Status: `reviewer_blocked / Developer bounded fix required`

### B4: Generic humidity prose is accepted as a Damp Heat condition

`extract_damp_heat_condition()` delegates to the generic collector with `humidity` as
one of its labels, then treats every surviving non-label string as a condition fact.
That accepts prose with no explicit condition value:

```python
extract_damp_heat_condition("Humidity exposure shall not cause damage.")
# current result: "Humidity exposure shall not cause damage"
```

This violates the frozen contract: Damp Heat must return only source-supported,
explicit condition facts; unsupported prose is a normal `None` no-match and must not
become Condition text. It can also turn a requirement-like sentence into a Condition.

## Required Developer Bounded Fix

In `damp_heat_condition_parser.py`, require an explicit quantitative/source condition
fact before returning a collected segment. Preserve valid labelled temperature/RH/
duration facts and the canonical source-faithful result; do not invent values or alter
the shared collector. Add focused helper regressions for generic humidity prose and
for any label-only/unsupported segment that must return `None`, then rerun the
declared bounded parser suite. Do not alter the read-only old parser test or any
TASK_365A/B/C code/test.

## Review Evidence

- Mechanical extraction is otherwise narrow: the new collector copies the planned
  regex/functions, extractor call sites map to the approved public helpers, and the
  Damp Heat dispatch precedes generic humidity.
- Current candidate counts meet limits: extractor `488`, collector `128`, Damp Heat
  helper `27`, and all three new test modules are bounded. The old parser-test SHA-256
  remains `BC6D61558C7113003ADB8A338BB69D266C1642459D952D23C09530F9F063AF42` and
  its external `51/0` hunk is not absorbed.
- The reported 86-test suite, compile, whitespace, line, and scope checks are useful
  regression evidence but do not cover the prose-only no-match boundary above.

## Next Legal Route

Route only to **Developer bounded fix pass**. Do not route QA or Integrator.

## Implementation Re-Gate

Date: 2026-07-22

Status: `reviewer_pass`

### B4 Closure

The Damp Heat helper now filters each shared-collected segment through a private,
bounded fact predicate. It retains only numeric temperature, humidity percentage,
duration/cycle, or explicitly marked `Damp Heat Condition: A/1` source facts. Generic
humidity prose, label-only text, pending-review wording, and unsupported procedure
text return `None`; a prose segment beside a valid source segment is dropped without
rewriting the valid segment.

This closes the Reviewer reproduction while retaining the narrow architecture:

- the shared collectors and extractor dispatch did not change in B4;
- Damp Heat continues to dispatch before generic humidity;
- the mechanical collector migration, accepted MFG/Thermal Shock/Voltage Surge
  behaviors, and old test isolation remain intact.

### Verification

- Declared combined parser regression:
  `96 passed`.
- `py_compile` passed for the extractor and both new helpers.
- UTF-8 physical counts: extractor `488`, collectors `128`, Damp Heat helper `41`,
  new tests `80` / `102` / `67`; all within frozen limits.
- Read-only old parser test SHA-256 remains
  `BC6D61558C7113003ADB8A338BB69D266C1642459D952D23C09530F9F063AF42`; its external
  `51/0` hunk remains outside the lane.
- Diff/whitespace, scope, and index checks are clean apart from existing LF/CRLF
  notices. No real data/file, staging, commit, or push operation occurred.

## Next Legal Route

Route only to **QA gate**. QA must preserve the same path/hunk isolation and may not
modify the old parser-test residual or route directly to Integrator.
