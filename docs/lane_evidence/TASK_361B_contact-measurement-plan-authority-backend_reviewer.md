# TASK_361B Contact Measurement Plan Authority Backend Reviewer Evidence

Status: reviewer_plan_blocked
Task: `TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND`
Lane: `contact-measurement-plan-authority-backend`
Date: 2026-07-12
Role: Reviewer

## Gate

Reviewer plan gate only. No schema, product code, API, migration, or test implementation was changed.

Current phase: Phase 11, Project Workbench / Matrix / Approval Package controlled foundation.
Current active task: `TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND`.
Why allowed: the board records TASK_361B as the current planned-only backend foundation lane after TASK_361A contract acceptance.

## Findings

### B1 - Schema keys do not yet enforce stable identity or idempotent impact recovery

The proposed `measurement_plan_impacts` uniqueness key contains nullable `stable_target_key`, `before_evidence_fingerprint`, and `after_evidence_fingerprint`. SQLite unique indexes allow multiple rows when a participating value is `NULL`, so the stated key cannot prevent duplicate unmatched-candidate impact rows during repeated refresh/partial recovery. This conflicts directly with the lane's idempotent bootstrap and partial-run recovery guarantee.

The target snapshot proposal also permits both or neither of `source_group_snapshot_id` / `manual_group_anchor_id`, and likewise for the row axis. That permits malformed `cmp-target:v1` lineage even though the identity contract requires exactly one imported lineage or plan-owned manual anchor on each axis.

Smallest fix: specify non-null normalized identity columns and exact SQLite constraints/indexes. For impacts, add a deterministic non-null `impact_identity_key` (or equivalent normalized candidate key) and make the refresh uniqueness constraint depend on it, not nullable lineage/evidence fields. For target snapshots, add per-axis XOR checks for source lineage versus manual anchor, plus non-empty/format validation for the persisted stable key. Include migration tests for repeated unmatched refresh, partial recovery, and invalid/both/neither lineage combinations.

### B2 - Rollback feature-flag ownership is outside the declared implementation boundary

The plan requires rollback through a backend configuration flag, but neither the Exact Future May Touch list nor the file-level plan identifies the configuration owner, default, persistence mechanism, or lifecycle of that flag. Without an owned boundary, TASK_361B either cannot implement the promised rollback or will expand into an unreviewed settings path.

Smallest fix: name the exact existing backend configuration module/file and the flag's default/read boundary in May Touch, or replace the flag with an explicitly scoped existing configuration mechanism. State that the rollback only selects the read-only legacy adapter, never mutates legacy JSON or deletes the additive tables, and add a focused enable/disable compatibility test.

## Assessment

The remaining plan is appropriately narrow: six additive tables, `cmp-target:v1`, lazy active-confirmed bootstrap, immutable lifecycle, pure classifier, partial-compatible projection, thin typed API, and downstream separation are all consistent with the accepted TASK_361A contract. Frontend/UI, draft workbook, Fee/formal consumer migration, generic Test Record, parser/import, LTR/public-drive, StepInstance, Report, real files, release/settings cleanup, `.agents/**`, and `docs/project_management/**` remain locked.

## Validation

- Read AGENTS, board, TASK_361A reconciliation/contract evidence, TASK_361B task/plan/Planner evidence, and current Matrix contact-plan persistence/authority context.
- Confirmed the worktree is docs-only for the Planner pass; visible parser test residuals and TASK_360Q artifacts are external and excluded.
- Targeted docs `git diff --check` passed with the existing board LF/CRLF warning only; no product file was modified for TASK_361B planning.

## Decision

`reviewer_blocked`

Recommended next role/action: Planner fix pass for B1 and B2 documentation only. Do not route Developer planning-first or any schema/product implementation until the exact constraints and rollback configuration owner are reconciled.

Blocking summary: B1 stable-identity/idempotency constraint gap; B2 rollback configuration-boundary gap.

---

# TASK_361B Reviewer Plan Re-Gate - B1/B2 Closure

Status: reviewer_pass
Task: `TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND`
Lane: `contact-measurement-plan-authority-backend`
Date: 2026-07-12
Role: Reviewer

## Gate

Reviewer plan re-gate only. No schema, migration, backend/API product code, or tests
were implemented or authorized by this review.

Current phase: Phase 11, Project Workbench / Matrix / Approval Package controlled
foundation.
Current active task: `TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND`.
Why allowed: the board records the planned-only backend foundation lane as pending
this Reviewer re-gate after the B1/B2 documentation fix.

## B1 Closure - Canonical Identity And Corruption Recovery

The amended contract closes the SQLite nullable-UNIQUE hole. `measurement_plan_impacts`
now requires non-null `impact_subject_key` and `impact_identity_key`. Existing targets
use canonical `cmp-target:v1` identity; unmatched candidates use the deterministic
`cmp-candidate:v1` subject; absent evidence is the literal `none`. The sole refresh
unique key is `(editable_revision_id, impact_identity_key)`, with upsert/read-verify
semantics. Equal recovered rows are reused and same-key payload divergence blocks as
`authority_corrupt` with transaction rollback.

Target snapshots now require independent non-empty Group and Row source-lineage XOR
manual-anchor checks. The persisted `cmp-target:v1` value must be reconstructed from
the stored axes and compare byte-for-byte before insert or update. Both/neither/empty
axis values and canonical-key mismatches are explicit corruption blockers. Once a
root exists, malformed authority state cannot silently fall back to legacy JSON.

## B2 Closure - Flag Ownership And Rollback Boundary

The rollback flag now has a narrow, implementable owner: the frozen `Settings`
dataclass in `backend/shared/config.py`. Its single field defaults to enabled and
reads only `CONNLAB_CONTACT_MEASUREMENT_PLAN_AUTHORITY_ENABLED` through a task-local
strict parser. The stated token set, blank/default behavior, and invalid-token
`ValueError` preserve existing `_bool_setting` and LTR/settings behavior.

`backend/api/dependencies.py` is the sole injection boundary. Routes and application
services must receive the boolean rather than load `Settings` or environment values.
The disabled path selects only the read-only legacy adapter and blocks independent
writes; it neither mutates legacy JSON nor removes or mutates additive authority
tables/audits. The task locks Settings UI/routes, local config, database settings,
and LTR/public configuration. Focused configuration and direct service-injection
tests are explicitly required.

## Scope And Validation

Future May Touch is sufficiently exact for the six new backend authority modules,
narrow database and API registration, the one config field/load path, and focused
backend tests. Frontend/client/UI, existing Matrix compatibility JSON mutation, Fee
and formal consumers, generic Test Record, parser/import, LTR/public-drive, real
files, Settings UI/API/local config, StepInstance, Report, `.agents/**`, and
`docs/project_management/**` remain locked.

The required temporary-SQLite migration/bootstrap/recovery tests, impact identity
tests, config injection/rollback tests, typed API tests, compile/static checks, and
forbidden-scope scans are proportionate for the later implementation lane.

## Validation

- Re-read AGENTS, task board, orchestration protocol, role registry, TASK_361A
  accepted context, TASK_361B task/plan/Planner evidence, and prior Reviewer block.
- Verified the B1 SQL/identity/recovery contract and B2 config/dependency contract
  against the existing `Settings` and dependency patterns.
- Confirmed the Planner pass is docs-only. Current parser/test, TASK_360Q,
  release/settings, and other visible worktree residuals are external and excluded.
- Targeted documentation `git diff --check` passed with only the known board
  LF/CRLF warning; trailing-whitespace scan found no matches.

## Decision

`reviewer_pass`

Recommended next role/action: explicit User approval, then Developer planning-first.
The board/evidence must be reconciled before any later schema or product
implementation authorization. This plan-gate pass does not authorize implementation.

Blocking summary: none for the plan re-gate; B1 and B2 are closed in the reviewed
documentation contract.

---

# TASK_361B Reviewer Implementation-Readiness Gate

Status: reviewer_pass
Task: `TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND`
Lane: `contact-measurement-plan-authority-backend`
Date: 2026-07-12
Role: Reviewer

## Gate

Reviewer implementation-readiness only. Developer planning-first is docs-only. No
schema, migration, backend/API product code, configuration, tests, client, workbook,
or real-file implementation was changed or authorized by this review.

Current phase: Phase 11, Project Workbench / Matrix / Approval Package controlled
foundation.
Current active task: `TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND`.
Why allowed: the user approved the documentation-only Developer planning-first pass
after the Reviewer plan re-gate; implementation remains a separately gated action.

## Readiness Assessment

The plan is implementation-ready for its narrowly defined backend foundation:

- Six additive SQLite tables have explicit types, foreign keys, lifecycle checks,
  partial indexes, target/family uniqueness, and immutable audit boundaries.
- Migration is additive and read-verifies existing SQLite objects before creating
  missing ones. It neither rebuilds existing tables nor runs legacy bootstrap as a
  startup-wide mutation.
- Bootstrap is per-project, active-confirmed-only, provenance-idempotent,
  transactional, partial-run recoverable, and non-destructive. Canonical impact
  dedupe, per-axis target XOR, stable-key reconstruction, and `authority_corrupt`
  rollback prevent unsafe repair or post-root legacy fallback.
- The lifecycle, impact classifier, partial-compatible confirmed projection, stale
  fingerprint commands, typed DTOs, disabled/read-only behavior, and backend-only
  configuration injection form a coherent service/API boundary.
- The exact module split keeps models, identity, classifier, bootstrap, lifecycle,
  projection, storage/migration/repository, and thin routes separate and below the
  repository size limits. Focused temporary-SQLite, API, configuration, compile, and
  scope-isolation tests are proportional to the risks.

The scope remains correctly bounded: no frontend/client, Matrix session-service
amendment, existing `contact_plan_json` mutation, TASK_361C UI, TASK_361D workbook,
TASK_361E consumer migration, Fee/formal consumer change, generic Test Record,
parser/import, LTR/public-drive, StepInstance, Report, real-file, Settings UI/API,
local configuration, or unrelated residual cleanup.

## Source-Of-Truth Prerequisite

`docs/task_board.md` still says the Reviewer B1/B2 plan re-gate is pending and names
that re-gate as the next task, while this Reviewer evidence already records its
`reviewer_pass` result and the Developer planning-first evidence relies on it. This
is a governance inconsistency, not a product-code finding, but it is a hard
pre-implementation prerequisite: Planner or Integrator must reconcile the board and
lane source of truth before any implementation authorization. User approval is also
still required. Neither this readiness pass nor the Developer evidence authorizes
schema/product work.

## Validation

- Re-read AGENTS, board, orchestration protocol, role registry, TASK_361A accepted
  reconciliation, TASK_361B task/plan/Planner/Reviewer/Developer evidence, current
  Settings and dependency patterns, and worktree status.
- Confirmed Developer planning-first only changed the TASK_361B plan and Developer
  evidence. No candidate schema/domain/application/API/test/client path is changed.
- Confirmed external parser/test, TASK_360Q/R, release/settings, board, and other
  residuals are excluded from the TASK_361B planning package.
- Targeted docs diff checks passed with only existing LF/CRLF working-copy warnings;
  trailing-whitespace scans found no matches.

## Decision

`reviewer_pass`

Recommended next role/action: User approval plus Planner source-of-truth
reconciliation. Only after both are complete may Developer implementation be
authorized. No direct implementation route is permitted now.

Blocking summary: no implementation-design blocker; board/source-of-truth
reconciliation and explicit user implementation approval remain mandatory
pre-implementation gates.

---

# TASK_361B Reviewer Implementation Gate

Status: reviewer_blocked
Task: `TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND`
Lane: `contact-measurement-plan-authority-backend`
Date: 2026-07-12
Role: Reviewer

## Gate

Reviewer implementation gate only. No product code was changed by this review.

Current phase: Phase 11, Project Workbench / Matrix / Approval Package controlled
foundation.
Current active task: `TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND`.
Why allowed: the reconciled board now records the exact backend implementation as
authorized and the Developer package is `ready_for_review`.

## Blocking Findings

### B3 - New Matrix candidates are persisted with the wrong impact subject identity

The approved contract requires a new or unmatched Matrix candidate to use a
canonical `cmp-candidate:v1` `impact_subject_key`, with the command/API carrying
that candidate subject separately from an existing stable target. The implementation
instead has the classifier emit new `cmp-target:v1` keys and passes them directly to
`persist_impacts()`. `_persist_impact()` then assigns that stable target key to both
`stable_target_key` and `impact_subject_key`. The rebind request likewise exposes
only `stable_target_key`, not the approved `candidate_subject_key` contract.

This collapses the required unmatched-candidate identity boundary and leaves the
API unable to faithfully address the persisted candidate diagnostic. Existing tests
only assert the new key is `cmp-target:v1`; they do not exercise candidate identity,
same-candidate dedupe, or rebind through a candidate subject.

Smallest fix: add a canonical candidate builder from current Matrix binding
locators, persist `stable_target_key = NULL` and `impact_subject_key =
cmp-candidate:v1|...` for unmatched candidates, update the typed rebind DTO/service
to accept that subject, and add lifecycle/API regressions for repeated candidate
refresh, candidate-to-target rebind, and no duplicate evidence.

### B4 - Existing-database migration accepts authority tables without the required constraints

The migration's compatibility check verifies only required column names. It does not
inspect foreign keys, CHECK constraints, unique/partial indexes, or the required
SQLite constraint/index definitions. Consequently, a pre-existing table with the
right columns but missing target lineage XOR, impact identity uniqueness, or revision
partial indexes is accepted instead of failing as an incompatible authority schema.
The same gap exists in the ORM model: target rows have the two axis XOR checks, but
there is no storage-level stable-key format/non-empty check; impacts also lack the
approved storage-level canonical subject/identity and enum/check constraints.

This defeats the lane's explicit B1 guarantee that partial recovery and existing-db
migration cannot continue on a malformed authority schema.

Smallest fix: make migration compare the required FK/check/index set, including the
two partial revision indexes and `(editable_revision_id, impact_identity_key)`, and
fail readably on divergence. Add database checks for stable-key/canonical impact
shape and allowed impact values, keep application parse/rebuild validation, and add
temporary-SQLite migrations/tests that seed same-column-but-incompatible tables and
prove rejection.

### B5 - Two application modules fall outside the exact authorized package

`backend/application/contact_measurement_plan_revision_fingerprint.py` and
`backend/application/contact_measurement_plan_revision_snapshot_helpers.py` are
both new production modules, but neither appears in the task's or plan's exact
future May Touch/module split. The helpers may be reasonable for file-size control,
but the package cannot be treated as exact-scope isolated until they are either
reconciled into the source-of-truth scope or replaced with an approved arrangement.

Smallest fix: Planner scope reconciliation that adds only these two named helpers,
their responsibilities, and focused tests to TASK_361B May Touch, or a narrow
Developer restructuring that stays within the already approved module list and the
hard size limits.

### B6 - Disabled-write API status disagrees with the approved typed contract

The reviewed plan specifies `503` with business code
`contact_measurement_plan_authority_disabled` when the feature is disabled. The
route maps `authority_disabled` to HTTP `409` and a different code
`authority_disabled`. This makes the rollback behavior contract inconsistent for
callers and tests.

Smallest fix: align the route error mapping and focused API regression with the
approved `503`/`contact_measurement_plan_authority_disabled` contract, or obtain a
Planner/Reviewer contract reconciliation before changing the advertised behavior.

## Positive Findings

- The backend-only feature flag is owned by `backend/shared/config.py` and injected
  from `backend/api/dependencies.py`; routes/services do not load environment values
  directly.
- No frontend/API-client, Fee/default-fill, workbook consumer, Matrix parser,
  LTR/public-drive, real-file, StepInstance, Report, or Settings UI/local-config
  product scope was introduced. Visible parser/test and other worktree residuals are
  external and excluded.
- The reviewed Python modules are below the 500-line hard limit; focused tests,
  `py_compile`, diff checks, and trailing-whitespace checks pass. These checks do
  not cover B3/B4/B6.

## Validation

- Re-read AGENTS, board, task/plan, prior Planner/Reviewer/Developer evidence, and
  actual candidate diff/status.
- Inspected identity, classifier, lifecycle helper, repository, ORM, migration,
  dependency/config, route, and focused tests directly.
- Re-ran the focused authority suite: `18 passed`; `py_compile` passed; diff check
  passed with existing LF/CRLF warnings; trailing-whitespace scan found no matches.
- Confirmed the Developer-reported 27 count includes additional surrounding checks;
  the five task-specific authority test files currently present execute 18 tests.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer fix pass for B3, B4, and B6, with a Planner
scope reconciliation for B5 if the two helper modules remain necessary. Do not route
QA or Integrator while these authority-contract and exact-package blockers remain.

Blocking summary: unmatched candidate identity/rebind contract is not implemented;
existing-schema constraint verification and storage-level canonical checks are
incomplete; two production helpers are outside the exact May Touch list; disabled
API status/code diverges from the approved contract.

---

# TASK_361B Reviewer Implementation Re-Gate - B3/B6 Partial Closure

Status: reviewer_blocked
Task: `TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND`
Lane: `contact-measurement-plan-authority-backend`
Date: 2026-07-12
Role: Reviewer

## Gate

Reviewer implementation re-gate only. No product code was changed by this review.

## Closure Assessment

- B6 is closed. Disabled writes now map to HTTP `503` with business code
  `contact_measurement_plan_authority_disabled`, and focused API coverage asserts it.
- B3 is only partially closed. New Matrix candidates now persist a non-null
  `cmp-candidate:v1` subject with `stable_target_key = NULL`; the typed rebind path
  accepts a candidate subject rather than overloading the replacement key.
- B4 and B5 remain open for the findings below.

## Blocking Findings

### B3R - Rebind does not resolve its candidate impact, so Confirm remains blocked

`rebind_target()` replaces the draft target and writes an audit row, but it never
finds the corresponding open candidate impact and changes its `resolution_state` to
`rebound` (or otherwise resolves it). `confirm()` rejects any open
review-required impact. Consequently, after a successful rebind the exact candidate
impact remains open and confirmation is still blocked. No focused test executes a
rebind followed by confirm.

Smallest fix: add a repository operation that resolves the matching open candidate
impact atomically by `editable_revision_id` and `candidate_subject_key`, record the
rebound target/reason where the schema permits, recompute the editable revision
fingerprint after the rebind, and add a lifecycle/API regression proving
candidate-refresh -> rebind -> confirm succeeds while an unrelated open impact still
blocks confirmation.

### B4R - Schema migration still checks names, not the required SQLite schema shape

The new migration verifies required column names, check names, and index names, but
does not inspect foreign keys at all. It also does not verify that a named index is
unique or carries the required SQLite partial predicate, nor that a named CHECK has
the required expression. Thus an existing database can supply same-name ordinary
indexes or placeholder checks and pass validation despite lacking the revision
partial-unique, target XOR, or impact identity guarantees. This is not the approved
FK/CHECK/UNIQUE/partial-index/schema SQL-shape verification.

Smallest fix: use SQLite metadata/`sqlite_master` (or equivalent inspector details)
to compare required foreign-key targets, unique-column sets, partial-index predicates,
and canonical check expressions. Add temporary-SQLite regressions for same-name
non-unique and non-partial indexes, placeholder check expressions, and a missing or
wrong foreign key, each requiring readable incompatibility failure.

### B5R - Helper scope is still absent from the task source of truth

The plan now lists the two helper modules, but
`tasks/TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND.md` still omits
`contact_measurement_plan_revision_fingerprint.py` and
`contact_measurement_plan_revision_snapshot_helpers.py` from its exact Authorized
May Touch list. The task is the scope source of truth, so plan-only wording does not
make the implementation package exact-scope compliant.

Smallest fix: Planner source-of-truth reconciliation adds exactly these two backend
helpers and their stated responsibilities to the task's Authorized May Touch list,
or Developer restructures within the existing list without violating size limits.

## Validation

- Re-read the updated Developer evidence, task/plan/reconciliation evidence, actual
  identity/classifier/helper/migration/model/route code, and focused tests.
- Re-ran the full reported focused suite including config coverage: `27 passed`.
- `py_compile` passed; `git diff --check` passed with existing LF/CRLF warnings;
  trailing-whitespace scan found no matches.
- Confirmed no frontend/API client/TASK_361C-E/Fee/workbook/parser/LTR/public-drive,
  StepInstance, Report, or real-file scope was introduced. External residuals remain
  excluded.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer fix pass for B3R and B4R, with Planner
source-of-truth reconciliation for B5R if the two helpers remain. Do not route QA
or Integrator.

Blocking summary: candidate rebind cannot clear its own review blocker; migration
does not validate actual FK/CHECK/unique/partial-index shape; task May Touch omits
two shipped helper modules. B6 is closed.

---

# TASK_361B Reviewer Implementation Re-Gate - B3R/B4R Partial Closure

Status: reviewer_blocked
Task: `TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND`
Lane: `contact-measurement-plan-authority-backend`
Date: 2026-07-12
Role: Reviewer

## Gate

Reviewer implementation re-gate only. No product code was changed by this review.

## Closure Assessment

- B5R is closed: task, plan, and reconciliation evidence now list both lifecycle
  helper modules with narrow responsibilities.
- B6 remains closed: disabled writes retain the required
  `503/contact_measurement_plan_authority_disabled` response.
- B3R is partially closed: candidate impacts now resolve to `rebound`, repeated
  rebind is accepted, and the integration path can confirm afterward.
- B4R is partially closed: migration now reads foreign-key target tables, named
  checks, SQL fragments, and the two partial-index predicates.

## Blocking Findings

### B3R2 - Rebind mutates authority without advancing the revision fingerprint

`rebind_target()` replaces a target and resolves an impact but leaves
`revision.revision_fingerprint` unchanged. The method also returns no refreshed
fingerprint. Therefore, a client holding the pre-rebind token can still call Confirm
after another operator rebounded the authority, defeating the declared optimistic
concurrency guard. The current rebind->confirm test passes precisely because it
reuses the unchanged fingerprint.

Smallest fix: after the target and impact mutation, recompute and persist the
editable revision fingerprint before the audit/flush, return or expose that new
fingerprint through the typed rebind response/workspace reload contract, and add a
regression proving the pre-rebind fingerprint is rejected while the refreshed token
can confirm. Preserve idempotent repeated rebind behavior.

### B4R2 - Migration still does not validate full FK/index SQL shape

The migration verifies only the set of referenced FK table names. It does not verify
the local FK columns, referenced target columns, or `ON UPDATE`/`ON DELETE` actions.
For indexes, it verifies names and the two partial `WHERE` fragments but not the
`UNIQUE` property or indexed column set. A same-name ordinary partial index, or a
foreign key on the wrong column pointing to the same table, can therefore pass the
current checker. The supplied schema test still covers only a missing-column table,
not these same-name shape divergences.

Smallest fix: compare `PRAGMA foreign_key_list` entries at the column/action level;
compare each required index's uniqueness, columns, and partial predicate from SQLite
metadata/`sqlite_master`; add temporary-SQLite regressions for wrong local/referred
FK columns/actions and same-name non-unique or wrong-column partial indexes. Such
shape mismatch must return the documented `authority_corrupt` failure before use.

## Validation

- Re-read the updated Developer evidence, task/plan/reconciliation, actual rebind,
  repository, migration, route, and focused test code.
- Re-ran the complete focused suite: `27 passed`.
- `py_compile` passed; diff check passed with existing LF/CRLF warnings;
  trailing-whitespace scan found no matches; all candidate Python files remain below
  the 500-line hard limit.
- Confirmed no frontend/client/TASK_361C-E/Fee/workbook/parser/LTR/public-drive,
  StepInstance, Report, real-file, or other locked scope was added.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer fix pass for B3R2 and B4R2. Do not route
QA or Integrator.

Blocking summary: rebind does not advance optimistic-concurrency state; existing-db
migration accepts same-name FK/index objects with incompatible column/uniqueness
shape. B5R and B6 are closed.

---

# TASK_361B Reviewer Implementation Re-Gate - B3R2 Closure / B4R2 Follow-Up

Status: reviewer_blocked
Task: `TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND`
Lane: `contact-measurement-plan-authority-backend`
Date: 2026-07-12
Role: Reviewer

## Gate

Reviewer implementation re-gate only. No product code was changed by this review.

## Closure Assessment

- B3R2 is closed. The rebind transaction now resolves the exact candidate impact,
  flushes target mutation, recomputes the editable revision fingerprint, and rejects
  the pre-rebind token before allowing confirmation with the refreshed token.
  Repeated equal rebind is read-verified/idempotent.
- B5R remains closed: both helper paths are now in the task, plan, and reconciliation
  exact May Touch records.
- B6 remains closed: disabled writes retain the typed HTTP `503` contract.
- B4R2 is only partially closed. FK local/referred/action/match shape and the two
  full unique index shapes are now inspected.

## Blocking Finding

### B4R3 - Revision partial unique indexes are not checked for unique flag or indexed columns

The migration checks the `WHERE` text for the two revision partial indexes, but it
does not verify that either index is `UNIQUE` or that its ordered indexed column set
is exactly `measurement_plan_root_id`. A same-name ordinary partial index, or a
same-name unique partial index over a different column, still passes the current
predicate-only validation. Likewise, the table CHECK inspection remains fragment
matching rather than validation of each complete canonical expression.

This leaves the one-confirmed/one-editable-per-root lifecycle invariant vulnerable
on an existing database with same-name malformed schema, contrary to the requested
exact unique/index columns-or-expressions/partial predicate validation.

Smallest fix: add a shape validator for each revision partial index that requires
SQLite `unique = 1`, ordered `measurement_plan_root_id` columns (or equivalent
expression metadata), and the exact normalized `WHERE` predicate. Strengthen CHECK
comparison to the full normalized canonical expressions. Add temporary-SQLite tests
for same-name non-unique partial indexes, same-name unique wrong-column indexes, and
placeholder/rewired CHECK expressions; each must block as `authority_corrupt`.

## Validation

- Re-read the B3R2/B4R2 Developer checkpoint, task/plan/reconciliation, actual
  lifecycle/repository/migration code, schema tests, and worktree scope.
- Re-ran the complete focused TASK_361B suite: `27 passed`.
- `py_compile` passed; diff check passed with existing LF/CRLF warnings;
  trailing-whitespace scan found no matches; all candidate application modules are
  below the 500-line hard limit.
- Confirmed no frontend/client/TASK_361C-E/Fee/workbook/parser/LTR/public-drive,
  StepInstance, Report, real-file, or other locked scope changed.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer fix pass for B4R3. Do not route QA or
Integrator.

Blocking summary: revision partial-index shape validation still permits same-name
non-unique or wrong-column indexes, and CHECK shape validation is still fragment
based. B3R2, B5R, and B6 are closed.

---

# TASK_361B Reviewer Implementation Re-Gate - B4R3 Partial Closure

Status: reviewer_blocked
Task: `TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND`
Lane: `contact-measurement-plan-authority-backend`
Date: 2026-07-12
Role: Reviewer

## Gate

Reviewer implementation re-gate only. No product code was changed by this review.

## Closure Assessment

- B3R2 remains closed: the rebind transaction advances the fingerprint and stale
  pre-rebind confirmation is rejected by regression coverage.
- B5R and B6 remain closed.
- B4R3 is partially closed: partial revision indexes now require `unique = 1`,
  `partial = 1`, and ordered `measurement_plan_root_id`; named CHECKs are compared
  more strongly than the prior fragment-only pass.

## Blocking Finding

### B4R4 - Schema comparisons are still containment/parenthesis-erasing, not exact canonical shape

`_validate_partial_index_shape()` accepts any index SQL containing the expected
normalized `WHERE` fragment rather than requiring equality of the actual predicate.
For example, `WHERE state = 'confirmed' AND revision_sequence > 0` would pass even
though it narrows the one-confirmed-per-root invariant. `_canonical_sql()` removes
all parentheses before comparing named CHECK expressions, so differently grouped
AND/OR expressions with the same token order can also pass despite different SQLite
semantics.

This does not meet the requested exact predicate and full canonical CHECK-expression
validation for existing authority databases.

Smallest fix: extract the actual predicate after `WHERE` and compare it for equality
to a whitespace/case-normalized canonical predicate. Normalize CHECK expressions
without deleting meaningful parentheses, allowing only optional outer wrapping
parentheses. Add temporary-SQLite regressions for an extra partial-index predicate
and a same-token, different-parenthesization CHECK; both must fail as
`authority_corrupt`.

## Validation

- Re-read the B4R3 Developer checkpoint, current migration implementation, schema
  tests, rebind regression, task/plan/evidence, and status.
- Re-ran the complete focused suite: `27 passed`.
- `py_compile` passed; diff check passed with existing LF/CRLF warnings;
  trailing-whitespace scan found no matches; candidate application modules remain
  below the 500-line hard limit.
- Confirmed no locked frontend/client/TASK_361C-E/Fee/workbook/parser/LTR/public-drive,
  StepInstance, Report, or real-file scope changed.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer fix pass for B4R4. Do not route QA or
Integrator.

Blocking summary: existing-db partial-index and CHECK validation is not yet exact;
B3R2, B5R, and B6 remain closed.

---

# TASK_361B Reviewer Implementation Re-Gate - B4R4 Code Closure / Test Gap

Status: reviewer_blocked
Task: `TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND`
Lane: `contact-measurement-plan-authority-backend`
Date: 2026-07-12
Role: Reviewer

## Gate

Reviewer implementation re-gate only. No product code was changed by this review.

## Closure Assessment

- B3R2 remains closed: candidate rebind resolves the exact impact, advances the
  revision fingerprint in the same transaction, rejects the old token, and supports
  idempotent repeat rebind.
- B5R and B6 remain closed.
- The B4R4 implementation itself is now correct on review: partial index validation
  checks unique/partial flags, exact root-id columns, and exact token-normalized
  `WHERE` equality; CHECK comparison preserves nested parentheses and boolean
  grouping while allowing only an optional outer wrapper.

## Blocking Finding

### B4R5 - Required malformed existing-schema regressions are not present

The requested migration regressions for a same-name wrong partial predicate and a
same-token/different-parenthesization CHECK expression are absent from the focused
test files. `test_contact_measurement_plan_schema.py` still tests only a missing
partial table. The complete 27-test suite passes, but it does not prove the two
specific existing-database corruption cases that motivated B4R4.

Smallest fix: add temporary-SQLite tests that construct the complete authority table
set with (1) a same-name unique partial revision index carrying an extra or wrong
predicate and (2) a named target CHECK with the same tokens but different AND/OR
grouping. Both `init_db()` calls must fail with the authority-corrupt incompatibility
result, with no table rebuild or mutation. Include the cases in the focused suite.

## Validation

- Re-read the B4R4 Developer checkpoint, migration implementation, schema tests,
  task/plan/evidence, and current package status.
- Re-ran the complete focused TASK_361B suite: `27 passed`.
- `py_compile` passed; diff check passed with existing LF/CRLF warnings;
  trailing-whitespace scan found no matches; candidate application modules remain
  below the 500-line hard limit.
- Confirmed no locked frontend/client/TASK_361C-E/Fee/workbook/parser/LTR/public-drive,
  StepInstance, Report, real-file, or unrelated scope change.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer fix pass for B4R5 test coverage only. Do
not route QA or Integrator.

Blocking summary: B4R4 code is acceptable, but the two required malformed existing
SQLite schema regressions are missing. B3R2, B5R, and B6 remain closed.

---

# TASK_361B Reviewer Implementation Re-Gate - Final

Status: reviewer_pass
Task: `TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND`
Lane: `contact-measurement-plan-authority-backend`
Date: 2026-07-12
Role: Reviewer

## Gate

Final Reviewer implementation re-gate. No product code was changed by this review.

## B3R2-B6 Closure

- Candidate impacts use `cmp-candidate:v1`, rebind resolves the exact impact,
  repeated equal rebind is idempotent, and rebind atomically advances the revision
  fingerprint. The old token is rejected and the refreshed token can confirm.
- Existing-database migration verifies required FK targets/columns/actions/match,
  exact full unique index shape, exact partial unique root-id index shape and
  token-normalized `WHERE` equality, plus named full CHECK expressions that preserve
  nested parentheses and AND/OR grouping.
- The two lifecycle helpers now appear in the task, plan, and reconciliation exact
  May Touch records. Disabled writes retain the approved typed HTTP `503` contract.

## Validation

- Inspected the B4R5 temp-SQLite tests directly. Each starts from an existing
  authority database, introduces either a same-name extra partial predicate or a
  same-token changed CHECK grouping, re-enters `init_db()`, and asserts an
  `authority_corrupt` incompatibility failure. The migration path is metadata/read
  validation only and does not write authority or legacy data on those failures.
- Re-ran the complete focused TASK_361B suite: `29 passed`.
- `py_compile` passed; `git diff --check` passed with existing LF/CRLF warnings;
  trailing-whitespace scan found no matches; candidate application modules remain
  below the 500-line hard limit.
- Confirmed the implementation remains backend-only within the reconciled May Touch
  package. No frontend/client, TASK_361C-E, Fee/workbook consumer, Matrix parser,
  LTR/public-drive, StepInstance, Report, real-file, Settings UI/local-config, or
  external residual scope was introduced.

## Decision

`reviewer_pass`

Recommended next role/action: QA gate. QA should run temporary-SQLite API/migration
smoke for bootstrap, stale/rebind/confirm, disabled mode, malformed existing-schema
rejection, and no legacy mutation. No Integrator route is authorized before QA pass.

Blocking summary: none for Reviewer implementation gate. B3R2, B4R4/B4R5, B5R, and
B6 are closed.
