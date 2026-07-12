# TASK_361F Contact Measurement Schema Compatibility Bootstrap Corrective Reviewer Evidence

Status: reviewer_pass
Task: `TASK_361F_CONTACT_MEASUREMENT_SCHEMA_COMPATIBILITY_BOOTSTRAP_CORRECTIVE`
Lane: `contact-measurement-schema-compatibility-bootstrap-corrective`
Date: 2026-07-13
Role: Reviewer

## Gate

Reviewer plan gate only. No product code, schema migration, real database, API, client,
or test implementation was changed or authorized by this review.

Current phase: Phase 11, Project Workbench / Matrix / Approval Package controlled
foundation.
Current active task: `TASK_361F_CONTACT_MEASUREMENT_SCHEMA_COMPATIBILITY_BOOTSTRAP_CORRECTIVE`,
planned-only.
Why allowed: TASK_361B-D are accepted; the board records the observed global startup
compatibility failure and makes TASK_361F the current corrective lane. TASK_361E is
explicitly paused and cannot receive this defect or any route from this gate.

## Review Findings

### Root cause and correct repair boundary

Repository inspection confirms `database.init_db()` registers models, runs
`Base.metadata.create_all()`, then calls
`migrate_contact_measurement_plan_authority_schema()`. The current migration first
requires four index names and therefore fails before its semantic index validators can
accept an equivalent SQLite object. This is the correct narrow boundary for the
corrective: neither Matrix Editor routes nor Fee/formal-consumer logic belongs in the
repair.

The plan correctly treats `create_all()` as fresh-schema registration rather than an
existing-table index evolution mechanism. SQLite-only migration logic, temporary
database fixtures, and unchanged runtime API behavior are appropriate.

### Four invariant definitions and safe bootstrap order

The four required unique semantics match the accepted authority models:

- one `confirmed` revision per root;
- one `draft` or `needs_review` revision per root;
- unique `(measurement_plan_revision_id, stable_target_key)`;
- unique `(editable_revision_id, impact_identity_key)`.

The planned classification distinguishes canonical, exact alternate-name or SQLite
autoindex equivalence, absence, and corruption by unique flag, ordered columns,
partial/full kind, and canonical partial predicate. A same-name wrong-shape object is
still corrupt and is neither dropped nor replaced.

The required order is safe: validate all non-index table/column/CHECK/FK invariants;
classify every required semantic index; complete duplicate preflight for every missing
invariant before any DDL; create only missing canonical unique indexes in a contained
SQLite transaction; then re-inspect every semantic invariant. Duplicate keys,
malformed non-index schema, wrong predicates/columns, invalid checks, or invalid
foreign keys block with `authority_corrupt` and make no schema or row change. The
plan explicitly forbids table rebuild, column alteration, data rewrite, deletion,
or guessed repair.

### Regression, real-data, and package isolation

Disposable existing-database tests cover all-four-missing, independently missing,
alternate exact-equivalent recognition, repeatable startup, duplicate preflight,
wrong-shape corruption, and preservation of all authority rows plus non-index schema.
Focused Matrix session, draft-cancel, and Test Record API checks exercise the global
startup path on temporary SQLite only. Fresh TASK_361B schema tests remain regression
coverage.

The May Touch list is adequate for the existing migration module and focused tests.
`data/connlab.sqlite3` and all operator databases are locked, as are table/model/
repository/lifecycle redesign, frontend/API client, TASK_361E consumer migration,
TASK_361D draft output, Fee/Test Record/Report semantics, parser, LTR/public drive,
real files, release/settings, `.agents/**`, and `docs/project_management/**`.

## Validation Performed

- Re-read AGENTS, task board, Planner Discovery and orchestration/parallel/role
  controls, TASK_361F task/plan/Planner evidence, and accepted TASK_361B-D context.
- Verified the board declares TASK_361F planned-only and TASK_361E paused by explicit
  user instruction.
- Inspected `init_db()`, the current authority migration, authority ORM declarations,
  and focused schema/API regression locations. The current migration is name-first;
  the four planned semantic unique shapes match the ORM declarations.
- Confirmed Planner work is governance-only. No real database was opened, copied, or
  modified. Targeted diff-check produced only the known board LF/CRLF warning and
  UTF-8 trailing-whitespace scans found no matches. External residuals remain
  excluded.

## Decision

`reviewer_pass`

Recommended next role/action: explicit User approval, then Developer planning-first.
Do not route Developer implementation directly. Any later implementation remains
subject to source-of-truth reconciliation and a Reviewer implementation-readiness
gate.

Blocking summary: none for the planned-only Reviewer plan gate.

---

# TASK_361F Reviewer Implementation-Readiness Gate

Status: reviewer_pass
Task: `TASK_361F_CONTACT_MEASUREMENT_SCHEMA_COMPATIBILITY_BOOTSTRAP_CORRECTIVE`
Lane: `contact-measurement-schema-compatibility-bootstrap-corrective`
Date: 2026-07-13
Role: Reviewer

## Gate

Reviewer implementation-readiness gate only. Developer planning-first is docs-only;
no migration code, schema, test implementation, real database, API/client, or product
behavior was changed or authorized by this review.

Current phase: Phase 11, Project Workbench / Matrix / Approval Package controlled
foundation.
Current active task: `TASK_361F_CONTACT_MEASUREMENT_SCHEMA_COMPATIBILITY_BOOTSTRAP_CORRECTIVE`,
ready for Reviewer implementation-readiness.
Why allowed: the board, task, plan, Planner/Reviewer/Developer evidence, and Planner
reconciliation agree that plan review and user-approved planning-first are complete,
while product implementation remains unauthorized. TASK_361E remains paused by user.

## Readiness Assessment

### Exact SQLite semantic-index contract

The strategy defines all four invariants as structured SQLite semantic specifications,
not index-name checks: confirmed-per-root and editable-per-root partial unique indexes
on `measurement_plan_root_id`; full target identity uniqueness on
`(measurement_plan_revision_id, stable_target_key)`; and full impact identity
uniqueness on `(editable_revision_id, impact_identity_key)`. It correctly requires
exact unique flag, ordered columns, partial/full type, canonical predicate, and
practical NULL coverage. SQLite-generated or alternate names may be accepted only on
exact semantic equivalence; same-name or alternate wrong shapes are
`authority_corrupt` and are never drop/replace candidates.

### Bootstrap, failure, and concurrency safety

The sequence is implementation-ready: validate all non-index authority invariants;
classify all four indexes; preflight every absent invariant before DDL, including
partial-predicate key scope and forbidden NULL identity cases; then create only absent
canonical indexes in one SQLite transaction and re-recognize every invariant before
commit. Duplicate, nullable-identity, malformed non-index schema, or incompatible
index states fail closed with `authority_corrupt`, preserving rows and schema objects.

The plan explicitly treats a DDL exception after partial creation as a rollback event,
not a partial success. Repeated startup is a no-op after a valid bootstrap. Two
independently opened temporary engines provide a proportionate idempotency/serialization
check; lock/busy errors remain readable startup failures and never trigger a guessed
fallback or data repair.

### Scope and temporary regression design

Implementation is constrained to the existing authority schema migration plus focused
temporary SQLite schema/bootstrap and startup API regression tests. The existing
`init_db()` order remains read-only evidence, so no call-order, route, or DTO change is
permitted. Disposable legacy-shaped fixtures cover all-four/each-missing, exact
alternate equivalence, duplicates, partial-predicate variants, wrong columns, nullable
identity substitutions, non-index CHECK/FK/table corruption, DDL rollback, and
row/non-index-DDL preservation.

Matrix session, draft Cancel, and current Test Record requests are regression probes
only against temporary database paths. Real `data/connlab.sqlite3` and every operator
database remain locked. So do table rebuilds, deletes, repairs, backfills, authority
model/repository/lifecycle changes, frontend/API client, TASK_361D, paused TASK_361E,
Fee/Test Record/Report semantics, parser, LTR/public drive, real files, release/
settings, `.agents/**`, and `docs/project_management/**`.

## Source-Of-Truth

The board and reconciliation evidence consistently record TASK_361F as ready for this
readiness gate and not implementation-authorized. The earlier plan-gate language is
historical governance context only. A further explicit user implementation approval
and Planner/source-of-truth reconciliation are required before a Developer may change
the migration or tests. TASK_361E remains paused and cannot be resumed or absorbed by
this lane.

## Validation Performed

- Re-read AGENTS, task board, orchestration/parallel controls, TASK_361F task/updated
  plan, Planner, prior Reviewer, Developer, and reconciliation evidence.
- Reconfirmed the existing `init_db()` ordering, authority migration validators, ORM
  non-null unique-pair declarations, and temporary schema/API regression locations.
- Confirmed Developer planning-first is docs-only. Existing MCR/parser/test,
  TASK_360Q/R/S, TASK_361E governance, superpowers, and other dirty worktree entries
  remain external and excluded.
- Targeted documentation diff-check reports only the known board LF/CRLF warning;
  UTF-8 trailing-whitespace scans found no matches.

## Decision

`reviewer_pass`

Recommended next role/action: explicit User approval, then Planner/source-of-truth
reconciliation before Developer implementation. Do not route Developer implementation
from this gate.

Blocking summary: none for implementation readiness.

---

# TASK_361F Reviewer Implementation Gate

Status: reviewer_blocked
Task: `TASK_361F_CONTACT_MEASUREMENT_SCHEMA_COMPATIBILITY_BOOTSTRAP_CORRECTIVE`
Lane: `contact-measurement-schema-compatibility-bootstrap-corrective`
Date: 2026-07-13
Role: Reviewer

## Finding

### B1: Four-invariant existing-database bootstrap is not regression-proven

The migration is implemented generically for all four semantic invariants, but the
new compatibility tests exercise only the two named partial revision indexes. In
`tests/unit/test_contact_measurement_plan_schema.py`, the added bootstrap, alternate,
duplicate, nullable, rollback, and lock cases use `_PARTIAL_SEMANTIC_INDEX_NAMES`;
the startup API probe likewise drops only the two partial indexes. No disposable
existing-database fixture proves that both full unique-pair semantics,
`(measurement_plan_revision_id, stable_target_key)` and
`(editable_revision_id, impact_identity_key)`, can be absent and then safely
recognized/created through `init_db()`.

This leaves the lane's critical acceptance claim, all four missing semantic indexes,
unverified. It also does not prove that a duplicate or prohibited NULL in a missing
full target/impact pair blocks before *any* partial or full canonical index DDL.

**Required Developer fix pass:** add a disposable legacy-shaped SQLite fixture with
all four authority semantic indexes absent, then verify `init_db()` creates or
recognizes every invariant while preserving authority rows and non-index schema. Add
full-pair target and impact duplicate/NULL preflight cases, asserting
`authority_corrupt` and that no canonical index from the same bootstrap attempt was
created. Use temporary paths only; do not rebuild or touch a real database.

## Verified Non-Blocking Scope

- The current migration implements SQLite-only semantic recognition, `BEGIN
  IMMEDIATE`, rollback on DDL failure, read verification, and readable lock failure.
- Existing same-name partial wrong-shape and non-index CHECK/FK validation remain
  fail-closed. The migration is 350 lines, below the 500-line hard limit.
- `TASK_361E` remains paused. No real database, table rebuild, data repair/deletion,
  `database.py` ordering change, frontend/API client, TASK_361D/E, Fee, generic Test
  Record/Report, parser, or LTR/public-drive hunk appears in the candidate package.

## Validation Performed

- Re-read AGENTS, board, TASK_361F task/plan/Planner/Developer/reconciliation
  evidence, and actual migration/test diff.
- Ran the declared temporary SQLite authority/startup/API regression suite:
  `33 passed`.
- `py_compile` passed for the migration; `git diff --check` produced only existing
  LF/CRLF warnings; trailing-whitespace and forbidden-scope scans were clean.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer fix pass limited to B1 regression coverage.
Do not route QA or Integrator. Product behavior must not be expanded, and TASK_361E
remains paused.

---

# TASK_361F Reviewer Implementation Re-Gate: B1

Status: reviewer_blocked
Task: `TASK_361F_CONTACT_MEASUREMENT_SCHEMA_COMPATIBILITY_BOOTSTRAP_CORRECTIVE`
Lane: `contact-measurement-schema-compatibility-bootstrap-corrective`
Date: 2026-07-13
Role: Reviewer

## Finding

### B1R: The new all-four fixture does not yet prove the required startup boundary

The new disposable legacy-shaped fixture correctly removes the two partial indexes and
both full-pair table constraints, and it now exercises target/impact duplicate and
nullable states. However, its successful all-four bootstrap test directly calls
`migrate_contact_measurement_plan_authority_schema(recovered_engine)` rather than
`init_db(recovered_engine)`. The task acceptance is specifically an existing database
that completes global startup through `init_db()`, the failure boundary that caused
Matrix Editor routes to return `500`.

The duplicate and NULL assertions also use `assert not _all_canonical_indexes(...)`.
That only proves fewer than all four canonical indexes exist; it would still pass if a
partial bootstrap created one or more canonical indexes before the failure. B1 requires
proof of no canonical DDL from the failed attempt.

**Required Developer fix pass:** keep the fixture disposable and tests-only, but run
the all-four success path through `init_db()`. For target/impact duplicate and NULL
failure cases, assert the complete canonical-index set is absent across all three
tables, not merely that all four are not present. Preserve the current real-database,
table-rebuild-in-migration, product-behavior, and paused-TASK_361E locks.

## Validation Performed

- Directly inspected the new legacy-shaped fixture and B1 test code.
- Re-ran the full temporary TASK_361F authority/startup/API suite: `38 passed`.
- `py_compile` passed; migration line count is 350; diff/trailing/forbidden-scope and
  no-real-database-path scans are clean aside from existing LF/CRLF warnings.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer fix pass limited to B1R test assertions and
the `init_db()` startup boundary. Do not route QA or Integrator. TASK_361E remains
paused.

---

# TASK_361F Reviewer Implementation Re-Gate: B1R Resolution

Status: reviewer_pass
Task: `TASK_361F_CONTACT_MEASUREMENT_SCHEMA_COMPATIBILITY_BOOTSTRAP_CORRECTIVE`
Lane: `contact-measurement-schema-compatibility-bootstrap-corrective`
Date: 2026-07-13
Role: Reviewer

## B1R Verification

The disposable legacy-shaped success fixture now invokes `init_db(recovered_engine)`,
the production startup boundary, after removing both partial revision indexes and the
two full target/impact table constraints. It then read-verifies all four canonical
semantic indexes and preserves target/impact rows plus the fixture's non-index table
schema.

Target and impact duplicate fixtures, as well as the nullable full-pair identity
fixtures, now assert exact equality with the empty canonical-index set across
revisions, target snapshots, and impacts. They therefore prove that no partial or
full canonical DDL is accepted before `authority_corrupt`. The nullable cases contain
actual NULL values under a nullable schema and correctly exercise the non-null shape
guard.

## Scope and Regression Check

This fix is tests-only: the migration implementation is unchanged from the prior
candidate, and no real database, `database.py` call order, model, repository,
lifecycle, frontend/API client, TASK_361D/E, Fee, generic Test Record/Report, parser,
LTR/public-drive, or real-file behavior changed. TASK_361E remains paused.

## Validation Performed

- Re-read the updated Developer evidence and directly inspected the all-four success,
  duplicate, NULL, canonical-index-set, and temporary-fixture assertions.
- Re-ran the full temporary TASK_361F authority/startup/API suite: `38 passed`.
- `py_compile` passed; migration line count is 350 and compatibility test line count
  is 299, both below the 500-line hard limit. Diff, trailing-whitespace,
  forbidden-scope, and no-real-database-path scans are clean apart from existing
  LF/CRLF warnings.

## Decision

`reviewer_pass`

Recommended next role/action: QA gate using disposable existing-database startup/API
smoke. Do not route Integrator yet. TASK_361E remains paused.

Blocking summary: B1 and B1R are closed.
