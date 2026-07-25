# RELEASE_006B2 Developer Tests-Only Implementation Evidence

Date: 2026-07-25
Role: Developer tests-only implementation
Status: `ready_for_reviewer_tests_only_diff_gate`
Task: `RELEASE_006B2_MULTI_GROUP_BASE_FEE_FALLBACK_TEST`
Lane: `multi-group-base-fee-fallback-test`
Parent: `RELEASE_006_POST_PUSH_WORKTREE_RESIDUAL_COMMIT_AND_CLEANUP_RECONCILIATION`
Product implementation authorization: none
Test implementation authorization: explicit and limited to the bounded module

## Gate

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

This role action is allowed because:

- B1 is complete/accepted at
  `168871302b4ad3522b803391b8d7be9838e96570`;
- RELEASE_006B2 Reviewer implementation-readiness passed;
- the User explicitly approved the exact tests-only implementation;
- Planner final reconciliation records
  `tests_only_implementation_authorized_pending_developer`.

That approval authorizes only the bounded test module. Product edits,
cleanup, staging, commit, and push remain unauthorized.

## Required Reads

Read as UTF-8 and applied:

- `AGENTS.md`;
- `docs/task_board.md`;
- RELEASE_006B2 task and plan;
- RELEASE_006B2 Planner and Reviewer evidence;
- `docs/project_management/TASK_EXECUTION_SKILL.md`;
- public Confirmed Matrix authority dataclasses;
- `ConfirmedMatrixFeeDraftService` and its command/store contract;
- accepted automatic-default build, identity, serializer, fingerprint, and
  row-safety contracts;
- accepted Base Fee policy and focused Child 1 rule-resolution tests;
- the exact dirty legacy B2 node and its local fixture dependency;
- final Planner authorization reconciliation.

## Planning Baseline

```text
HEAD             168871302b4ad3522b803391b8d7be9838e96570
branch           master
origin/master    580fbb5ecc5a7fb8ffbdd151fb5198bd1db51db5
left/right       0/2
index            empty
worktree         51 paths = 37 tracked + 14 untracked
```

Locked legacy test:

```text
path      tests/unit/test_confirmed_matrix_fee_draft_service.py
lines     683 UTF-8 physical lines including blanks
SHA-256   716d76d265ffc892146c0271f543455e004e8e649629733bab125453b3ffbbf0
numstat   38/13
```

Future bounded path:

```text
tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py
absent
```

The `38/13` legacy diff remains split into the unique `22/0` B2 node and the
excluded `16/13` support-only fixture generalization. Neither was edited.

## Confirmed Public Contracts

### Service boundary

`ConfirmedMatrixFeeDraftService` accepts a
`ConfirmedMatrixAuthorityStore`. Its default rule-library path resolves the
accepted active library; the bounded test does not inject a custom rule.

`build_current_pricing_defaults("P1", service)` performs one
`build_authority_result()` call and returns:

- the unflattened Fee draft;
- the captured Confirmed Matrix;
- flattened automatic values;
- ordered row identities;
- pre-flattening row safety;
- the exact V2 source context.

The test uses this one result for both draft and fingerprint
assertions. Calling `build_draft()` first would create an unnecessary second
authority build.

### Domain fixture

The public frozen authority types provide every required field:

- `ConfirmedMatrixVersion`;
- `ConfirmedMatrixGroup`;
- `ConfirmedMatrixRow`;
- `ConfirmedMatrixCell`;
- `ConfirmedMatrixSnapshot`;
- `ConfirmedMatrixStatus.CONFIRMED`.

One row, two Groups, and two Cells are sufficient. No step quantity, duration
authority, Measurement Plan, Point Profile, manual pricing draft, text
fallback, or second row is required.

### Accepted output

`CURRENT RATING` plus condition `300A` resolves to:

```text
matched_rule_id      fee_rule_temperature_rise
status               calculated
review_required      false
review_reason        null
spend_time           4
unit_label           sample
unit_price           600
units                5
base_fee             0
discount_percent     0
testing_fee          3000
```

The accepted Base Fee metadata contains one `base_fee` entry:

```text
state    auto_filled
source   Matrix Fee automatic Base Fee fallback
message  null
```

The fallback is line-level. Group count is not an authority, policy input, or
trigger.

## Executed Test Design

The bounded module is:

```text
tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py
<=300 UTF-8 physical lines including blanks
```

It owns:

1. one local store returning the snapshot only for project `P1`;
2. one explicit public-dataclass snapshot;
3. one metadata selector;
4. one behavior node.

Exact snapshot identities:

```text
matrix-b2 / draft-b2 / import-b2 / snapshot-b2
row-current-rating / draft-row-current-rating / source-row-current-rating
group-1 / draft-group-1 / source-group-1 / g1 / Group 1
group-2 / draft-group-2 / source-group-2 / g2 / Group 2
cell-1 / cell-2
```

Both Groups use sample quantity `5`; both Cells contain Step token `1`.
`sample_received_date` is set so no unrelated root warning is introduced.

The one node must assert:

- draft `ready`, review count zero, warnings empty;
- ordered `g1`, `g2` Groups with one line each;
- distinct line, Group, row, and flattened row identities;
- exact accepted Current Rating values on both lines;
- exactly one Base Fee metadata entry per line with the fallback source;
- per-line Testing Fee `3000`, without a cross-Group total assertion;
- exact full ordered identity tuple, including backend-owned sample/report
  manual rows;
- matching safe row-safety identities and automatic Base Fee evidence;
- exact automatic-default fingerprint equality using
  `canonical_fingerprint(edited_values_to_payload(result.automatic_values))`.

The expected fingerprint is validated through the accepted canonical
serializer. The test does not hard-code an opaque hash or duplicate product
calculation logic.

## TDD And Validation Contract

Coverage RED:

- clean accepted HEAD lacks the bounded module;
- clean accepted coverage lacks the exact two-Group per-line
  identity/metadata/fingerprint tuple.

Unchanged-product GREEN:

- add only the bounded test;
- run it against accepted product;
- require zero product and legacy-test diff.

The plan's three suites are:

1. new B2 + Child 1 + clean-HEAD legacy service;
2. accepted Child 2 duration/dependent-field regressions;
3. accepted TASK_361L/TASK_363D V2 regressions;
4. `py_compile`, physical-line, UTF-8, trailing, diff, whitelist,
   forbidden-path, staging, and no-real-data checks.

The old service test must be sourced from clean HEAD in validation, never
from its dirty `38/13` working-tree copy.

## May Touch And Locks

Sole test May Touch:

```text
tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py
```

Evidence May Touch:

- B2 plan;
- this Developer evidence;
- narrow B2 governance status alignment.

Locked:

- all product code;
- the 683-line mixed test and both old hunks;
- accepted Child 1/2/V2 source and tests except read-only future execution;
- B1 accepted package and old frontend residual;
- B3 parser, Child C, duplicate/support hunks, and every external residual;
- schema, database, API, frontend, rules, seed, manifest, dependencies;
- real DB/files, generated artifacts, remote refs;
- discard, restore, cleanup, stage, commit, and push.

## Risk, Rollback, And Package Isolation

- Default-library drift: assert exact accepted rule id, values, metadata, and
  fingerprint without injecting a test rule.
- Identity collapse: assert both owning line identities and full ordered
  automatic-default identities.
- Double authority read: use only the single automatic-default build result.
- Policy duplication: assert outputs; do not calculate fallback or Testing
  Fee in fixture code.
- Dirty legacy absorption: reconstruct clean HEAD and whitelist one new test.
- Rollback before acceptance: omit only the new test candidate; never alter
  either legacy hunk.

No product/data/generated-output rollback is required because none is
authorized.

## Developer Self-Review

- Goal/input/output/modules: explicit.
- Public types and signatures: verified from current code.
- Test data and identities: complete and internally consistent.
- Expected values and metadata: literal and independently specified.
- V2 fingerprint assertion: uses accepted canonical boundary.
- TDD RED/GREEN and regression commands: executable.
- File limit: Reviewer-approved `<=300`, with headroom.
- Placeholders/TODOs: none.
- Out-of-scope implementation or test action: none.

## Validation

No pytest, py_compile, implementation, dependency, build, generated-output,
database, or file-authority command was run.

Final docs-only checks:

```text
UTF-8 physical lines including blanks
  board      2400
  task        268
  plan        652
  evidence    294 before this validation update

trailing whitespace
  0 across board/task/plan/evidence

tracked board git diff --check
  passed; existing LF/CRLF notice only

untracked task/plan/evidence no-index diff --check
  expected add-file exit 1; no whitespace error

status
  task, plan, evidence, and B2 board hunks agree on
  Developer planning-first complete / pending Reviewer readiness

legacy test
  683 physical lines
  SHA-256 716d76d265ffc892146c0271f543455e004e8e649629733bab125453b3ffbbf0
  dirty numstat 38/13

future bounded test path
  absent

product/test scope
  no B2 product or test edit
  existing legacy backend and frontend test residuals remain read-only

index
  empty

repository checks
  tracked git diff --check passed; existing LF/CRLF notices only
  candidate files have zero UTF-8 trailing whitespace
  bounded test contains no real-data or generated-output path
  backend product status is unchanged
```

The only current-role writes are B2 plan, Developer evidence, task status,
and narrow B2 board status/summary hunks. No product or test path was
created, edited, restored, deleted, staged, committed, or pushed.

## Tests-Only Implementation Result

Created only:

```text
tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py
```

The 276-line bounded module uses public Confirmed Matrix dataclasses to
construct one Current Rating row, two Groups, and two owning Cells. Its
single test calls `build_current_pricing_defaults("P1", service)` exactly
once and proves the store was read exactly once.

The test asserts:

- exact owning line and flattened identities for both Groups;
- complete ordered identities including both sample-preparation rows and
  the report-preparation row;
- `fee_rule_temperature_rise`;
- Unit Price `600`, Units `5`, Base Fee `0`, discount `0`, and Testing Fee
  `3000` independently for each Group;
- exact automatic Base Fee metadata;
- safe pre-flattening row-safety evidence;
- the accepted canonical automatic-default fingerprint boundary.

No product file or locked legacy test was changed by this pass.

### RED/GREEN evidence

Coverage RED:

```text
accepted HEAD does not contain
tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py
or the exact bounded test node
```

Unchanged-product GREEN:

```text
py -m pytest \
  tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py::\
test_multi_group_draft_applies_common_base_fee_fallback_per_owning_line -q

1 passed in 0.76s
```

### Clean-HEAD regression evidence

A narrow temporary archive was reconstructed from `HEAD`, containing the
accepted backend and only the frozen read-only regression modules. The new
bounded test was copied into that disposable archive; no dirty legacy test
or product hunk was used. The archive and extracted directory were removed
after validation.

```text
new B2 + Child 1 + clean-HEAD legacy service
  42 passed in 1.29s

accepted Child 2 duration/dependent-field regressions
  21 passed in 1.59s

accepted TASK_361L/TASK_363D V2 regressions
  20 passed in 1.18s

py -m py_compile \
  tests/unit/test_confirmed_matrix_fee_draft_multi_group_base_fee.py
  passed
```

### Package checks

```text
new bounded test
  physical lines including blanks  276 (limit <=300)
  SHA-256                         e5ad7212f5751db49e25535471dfe4a2ea9139e031668270b6e292e1d28a181d
  UTF-8 trailing whitespace       0
  no-index diff-check             expected add-file exit 1; no whitespace error

locked legacy mixed test
  physical lines including blanks  683
  SHA-256                         716d76d265ffc892146c0271f543455e004e8e649629733bab125453b3ffbbf0
  existing numstat                38/13

index
  empty
```

External dirty worktree paths remain present and were neither cleaned nor
absorbed. No real database, public-drive file, attachment, generated
artifact, dependency, stage, commit, or push action occurred.

Status:

```text
ready_for_reviewer_tests_only_diff_gate
```

Remaining blocker: none for the Reviewer tests-only diff gate.

Next legal role: Reviewer. QA, Integrator, discard, worktree cleanup,
staging, commit, and push remain unauthorized.
