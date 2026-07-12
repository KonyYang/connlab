# TASK_361G Contact Measurement Schema CHECK Compatibility Bootstrap Corrective Reviewer Evidence

Status: reviewer_pass
Task: `TASK_361G_CONTACT_MEASUREMENT_SCHEMA_CHECK_COMPATIBILITY_BOOTSTRAP_CORRECTIVE`
Lane: `contact-measurement-schema-check-compatibility-bootstrap-corrective`
Date: 2026-07-13
Role: Reviewer

## Gate

Reviewer plan gate only. No product code, migration, real database, API/client, or
test implementation was changed or authorized by this review.

Current phase: Phase 11, Project Workbench / Matrix / Approval Package controlled
foundation.
Current active task: `TASK_361G_CONTACT_MEASUREMENT_SCHEMA_CHECK_COMPATIBILITY_BOOTSTRAP_CORRECTIVE`,
planned-only.
Why allowed: TASK_361F is complete/accepted at `983633b7`; the board records the
separate pre-index CHECK compatibility blocker and makes TASK_361G the current lane.
TASK_361E is paused by user and cannot be resumed or expanded here.

## Review Findings

### Formal corrective boundary

TASK_361G is correctly a formal, planned-only backend-storage corrective rather than
a quick fix. The current migration rejects missing named CHECKs before the accepted
TASK_361F semantic-index bootstrap can run, and SQLite cannot add table CHECKs without
a prohibited table rebuild. The plan confines the remedy to the existing migration and
disposable temporary SQLite tests; Matrix routes only serve as startup regression
probes and receive no behavior or contract change.

### Exact CHECK and guard semantics

The five required predicates are explicit: target Group-anchor XOR, target Row-anchor
XOR, target stable-key prefix, impact subject-key prefix, and impact identity-key
prefix. Existing table CHECKs qualify only under exact canonical-expression matching,
regardless of name. Wider, weaker, combined, ambiguous, or same-name wrong
expressions fail closed.

The four canonical triggers correctly cover five predicates as two table-level pairs:
target INSERT plus relevant-anchor/key UPDATE covers all three target checks, and
impact INSERT plus relevant-key UPDATE covers both impact checks. Their specified
`RAISE(ABORT, ...)` messages, table/event/update-column sets, and exact SQL
reinspection make the guard behavior reviewable. Existing-row preflight prevents an
unrelated update from preserving an already invalid legacy row.

### Atomicity, compatibility, and isolation

The plan requires all missing-CHECK row preflights and the unchanged TASK_361F index
preflights to complete before any DDL. Missing guards and still-missing canonical
indexes then share one `BEGIN IMMEDIATE` transaction, followed by exact recognition
and read verification. Wrong/mixed guard or CHECK shapes, invalid/indeterminate
rows, DDL failure, and busy/locked startup remain `authority_corrupt` or readable
fail-closed outcomes, with no partial schema success or data repair.

The proposed temporary tests cover all-five/each-missing, exact alternate CHECKs,
mixed CHECK/guard states, populated valid/invalid rows, trigger INSERT/UPDATE
enforcement, same-name wrong trigger, rollback/lock/idempotency, TASK_361F index
regression, and `init_db()` Matrix-session/read-only-Test-Record probes. This is
proportionate for a global startup repair.

The May Touch list is sufficiently narrow. Real `data/connlab.sqlite3`, any operator
database, table rebuild or writable-schema work, data update/delete/repair, models,
repositories, lifecycle, routes/DTOs, frontend/API client, TASK_361D, paused
TASK_361E, Fee/Test Record/Report behavior, parser, LTR/public drive, real files,
release/settings, `.agents/**`, and `docs/project_management/**` remain locked.

## Validation Performed

- Re-read AGENTS, board, orchestration controls, TASK_361G task/plan/Planner evidence,
  accepted TASK_361F and TASK_361B-D context, the operational smoke evidence, and the
  current authority migration.
- Confirmed the board records five missing CHECK semantics as a pre-index startup
  blocker, TASK_361F as accepted, and TASK_361E as paused.
- Confirmed Planner work is governance-only. I did not open, copy, or modify any real
  database. Targeted docs diff-check produced only the known board LF/CRLF warning;
  UTF-8 trailing-whitespace scans found no matches. External residuals are excluded.

## Decision

`reviewer_pass`

Recommended next role/action: explicit User approval, then Developer planning-first.
Do not route Developer implementation directly. A later implementation needs
source-of-truth reconciliation and Reviewer implementation-readiness review.

Blocking summary: none for the planned-only Reviewer plan gate.

---

# TASK_361G Reviewer Implementation-Readiness Gate

Status: reviewer_pass
Task: `TASK_361G_CONTACT_MEASUREMENT_SCHEMA_CHECK_COMPATIBILITY_BOOTSTRAP_CORRECTIVE`
Lane: `contact-measurement-schema-check-compatibility-bootstrap-corrective`
Date: 2026-07-13
Role: Reviewer

## Gate

Reviewer implementation-readiness gate only. Developer planning-first is docs-only;
no migration, test, API/client, real database, or product behavior was changed or
authorized by this review.

Current phase: Phase 11, Project Workbench / Matrix / Approval Package controlled
foundation.
Current active task: `TASK_361G_CONTACT_MEASUREMENT_SCHEMA_CHECK_COMPATIBILITY_BOOTSTRAP_CORRECTIVE`.
Why allowed: Reviewer plan gate passed and the user approved only Developer
planning-first. The Developer evidence records that docs-only refinement as complete.
TASK_361E remains paused by user and cannot be resumed by this gate.

## Readiness Assessment

### Exact predicate and trigger contract

The refined plan is implementation-ready. It freezes five individual semantic CHECK
predicates, four exact canonical trigger names, their `BEFORE INSERT` and relevant
`BEFORE UPDATE OF` events, and stable `RAISE(ABORT, ...)` messages. The target trigger
pair covers the two anchor-XOR predicates plus the target-key prefix; the impact pair
covers subject- and identity-key prefixes. `IS NOT 1` is correctly required in both
row preflight and guards so false and NULL/unknown expressions fail closed.

Physical table CHECKs are accepted only for exact canonical expressions, regardless
of name. Canonical trigger SQL is separately recognized by exact normalized form;
same-name wrong triggers and combined, weaker, stronger, or grouping-altered CHECKs
are corrupt. Unknown alternate triggers are neither removed nor treated as proof.

### Atomic bootstrap and failure behavior

The proposed sequence first retains TASK_361F's non-index and semantic-index
validation, classifies every physical CHECK and trigger, and completes all missing
CHECK row preflights plus unchanged index duplicate/NULL preflights before DDL. One
`BEGIN IMMEDIATE` transaction then re-reads classifications, creates only absent guard
pairs and still-missing accepted indexes, and exact-read-verifies all objects before
commit. DDL/read-verification failure rolls back all new guards and indexes; locked or
busy startup returns a readable fail-closed error. This avoids partial schema success
without changing TASK_361F's accepted index semantics.

### Tests and locked scope

The temporary SQLite plan covers all-five/each-missing and mixed states, exact
alternate CHECKs, wrong/combined expressions, invalid/NULL legacy rows, exact trigger
INSERT/UPDATE enforcement, valid lifecycle writes, rollback, idempotency, lock/busy,
and schema/row preservation. The planned Matrix session and read-only confirmed Test
Record preview probes validate only startup recovery; Cancel/Delete and generation
remain outside scope.

Future changes remain limited to the existing migration and named temporary tests.
Real/operator databases, table rebuild/writable-schema/data repair, model/repository/
lifecycle/API/client/frontend changes, TASK_361D, paused TASK_361E, Fee/Test Record/
Report/formal-workbook behavior, parser, LTR/public drive, real files, release/
settings, `.agents/**`, and `docs/project_management/**` remain locked.

## Source-Of-Truth Residual

Technical readiness passes, but the board and current Planner reconciliation still
state `ready_for_developer_planning_first` even though Developer evidence records the
pass completed. This is not implementation authorization. Before any Developer
implementation, Planner must reconcile board/task/plan/evidence to this readiness
outcome and a user must explicitly approve implementation. TASK_361E remains paused.

## Validation Performed

- Re-read AGENTS, board, orchestration controls, TASK_361G task/updated plan,
  Planner, prior Reviewer, Developer, and currently available reconciliation evidence,
  plus accepted TASK_361F migration context.
- Confirmed Developer planning-first is docs-only; visible MCR/parser/test, TASK_360Q/
  R/S, TASK_361E governance, operational evidence, and other dirty worktree entries
  remain external and excluded.
- Verified the frozen trigger SQL, exact recognition, `IS NOT 1`, pre-DDL ordering,
  single-transaction requirements, temporary probes, and locked scopes. No real
  database was opened, copied, or modified.
- Targeted docs diff-check produced only the known board LF/CRLF warning; UTF-8
  trailing-whitespace scans found no matches.

## Decision

`reviewer_pass`

Recommended next role/action: explicit User implementation approval, then
Planner/source-of-truth reconciliation before Developer implementation. Do not route
Developer implementation directly from this gate.

Blocking summary: none for technical implementation readiness; source-of-truth
reconciliation remains mandatory before implementation.

---

# TASK_361G Reviewer Implementation Gate

Status: reviewer_blocked
Task: `TASK_361G_CONTACT_MEASUREMENT_SCHEMA_CHECK_COMPATIBILITY_BOOTSTRAP_CORRECTIVE`
Lane: `contact-measurement-schema-check-compatibility-bootstrap-corrective`
Date: 2026-07-13
Role: Reviewer

## Finding

### B1: CHECK-shape recognition is not scoped to its table

`_missing_check_specs()` combines `get_check_constraints()` results from target
snapshots and impacts into one flat `values` set. When target-key CHECK is absent but
an exact physical impact-subject CHECK exists, the target-key marker `cmp-target:v1|`
is found inside the impact expression. The code then raises `authority_corrupt`
instead of classifying the target CHECK as missing and bootstrapping the target guard
pair. This violates the accepted mixed physical-CHECK/guard compatibility contract.

The current twelve-test compatibility module has no mixed table-CHECK/guard case, so
the all-missing and all-alternate tests do not expose this cross-table collision.

**Required Developer fix pass:** preserve CHECK expressions by owning table in the
recognition registry and evaluate marker/shape ambiguity only among CHECKs on the
same `spec.table`. Add a disposable mixed legacy fixture with an exact physical
impact-subject CHECK while the target-key CHECK remains absent; prove `init_db()`
creates the required target compatibility guards rather than failing. Do not alter
predicate semantics, trigger SQL, transaction logic, real-database policy, or any
locked product scope.

## Verified Non-Blocking Scope

- The candidate uses the frozen `IS NOT 1` trigger/preflight contract and shares a
  `BEGIN IMMEDIATE` create/read-verify transaction with TASK_361F index bootstrap.
- The candidate migration contains no real database path, table rebuild, writable
  schema, data repair/delete, `database.py`, API/client, or downstream consumer
  changes. TASK_361E remains paused.

## Validation Performed

- Re-read task, plan, evidence, actual migration, and temporary compatibility tests.
- Re-ran the declared temporary authority/startup/API suite: `51 passed`.
- `py_compile` passed; migration/test files are 409/414 lines, below the 500-line
  hard limit. Diff, trailing-whitespace, forbidden-scope, and no-real-path scans are
  clean apart from existing LF/CRLF warnings.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer fix pass limited to B1 table-scoped CHECK
recognition and its mixed-state regression. Do not route QA or Integrator. TASK_361E
remains paused.

---

# TASK_361G Reviewer Implementation Re-Gate: B1

Status: reviewer_blocked
Task: `TASK_361G_CONTACT_MEASUREMENT_SCHEMA_CHECK_COMPATIBILITY_BOOTSTRAP_CORRECTIVE`
Lane: `contact-measurement-schema-check-compatibility-bootstrap-corrective`
Date: 2026-07-13
Role: Reviewer

## B1 Resolution

The per-table `actual_by_table` registry now scopes CHECK name/expression/marker
matching to `spec.table`. The new mixed fixture uses `init_db()` with target-key CHECK
absent and impact-subject physical CHECK present, correctly producing only the target
canonical guard pair. Predicate, trigger SQL, transaction ordering, and locked scope
did not change.

## Finding

### B2: Trigger enforcement does not cover all five predicates and four events

The focused trigger test currently exercises target-key failure on target INSERT and
target UPDATE, plus impact-identity failure on impact INSERT. It does not exercise
the target Group-anchor XOR predicate, target Row-anchor XOR predicate, impact-subject
prefix predicate, or the `trg_cmp_impact_checks_update_v1` event. This falls short of
the lane's explicit five-predicate/four-event guard acceptance contract.

**Required Developer fix pass:** add tests only, using the existing disposable
fixture, that prove invalid Group-anchor XOR, Row-anchor XOR, target-key, impact-
subject, and impact-identity values each abort through the appropriate guard. Ensure
at least one case reaches each of target INSERT, target relevant UPDATE, impact INSERT,
and impact relevant UPDATE, while valid authority writes remain accepted. Do not change
migration behavior, trigger SQL, transactions, or locked paths. Keep the focused test
module below the 500-line hard limit, preferably by parameterizing the current guard
test rather than adding a second broad fixture.

## Validation Performed

- Directly reviewed the B1 per-table registry and mixed `init_db()` fixture.
- Re-ran the full temporary authority/startup/API suite: `52 passed`.
- `py_compile` passed; migration/test line counts are 412/446, below the 500-line hard
  limit. Diff, trailing-whitespace, forbidden-scope, and no-real-path scans are clean
  apart from existing LF/CRLF warnings.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer tests-only fix pass for B2. Do not route QA
or Integrator. TASK_361E remains paused.

---

# TASK_361G Reviewer Implementation Re-Gate: B2

Status: reviewer_pass
Task: `TASK_361G_CONTACT_MEASUREMENT_SCHEMA_CHECK_COMPATIBILITY_BOOTSTRAP_CORRECTIVE`
Lane: `contact-measurement-schema-check-compatibility-bootstrap-corrective`
Date: 2026-07-13
Role: Reviewer

## B1 and B2 Verification

The B1 per-table CHECK registry remains correct: target and impact physical CHECK
name/expression/marker recognition is isolated by owning table, so a valid impact
subject CHECK cannot satisfy or corrupt target-key recognition.

The B2 disposable SQLite guard-enforcement module is parameterized and covers all
five frozen predicates. Target Group-anchor XOR, Row-anchor XOR, and stable target
key prefix each exercise target `BEFORE INSERT` and relevant `BEFORE UPDATE` guards.
Impact subject-key and identity-key prefixes each exercise impact `BEFORE INSERT` and
`trg_cmp_impact_checks_update_v1`. Every scenario proves an invalid insert leaves no
row, an invalid relevant update rolls back to the prior valid value, and a valid
authority write remains accepted. This closes the previously missing impact-update
coverage without changing migration, predicate, trigger SQL, or transaction behavior.

## Validation Performed

- Re-ran the complete temporary SQLite authority/startup/API suite with an isolated
  `--basetemp`: `57 passed`.
- `py_compile` passed for the migration and both CHECK compatibility/enforcement
  modules.
- Line counts remain under the hard limit: migration 412, CHECK compatibility startup
  test 468, and parameterized guard-enforcement test 172 lines.
- `git diff --check` reported only existing LF/CRLF warnings. Trailing-whitespace,
  locked-scope, and no-real-database scans are clean; the B2 pass adds tests only.
- No frontend/API-client, TASK_361D/E, Fee, workbook, parser, LTR/public-drive,
  real-database, table-rebuild, data-repair, or release/settings behavior changed.
  TASK_361E remains paused by user instruction.

## Decision

`reviewer_pass`

Recommended next role/action: QA gate using disposable legacy SQLite startup and
Matrix-session/read-only Test Record API smoke. Do not route Integrator yet.

Blocking summary: none. B1 table-scoped recognition and B2 five-predicate/four-event
trigger enforcement coverage are closed.
