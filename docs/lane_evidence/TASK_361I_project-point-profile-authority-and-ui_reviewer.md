# TASK_361I Reviewer Plan Gate

Status: reviewer_pass
Task: `TASK_361I_PROJECT_POINT_PROFILE_AUTHORITY_AND_UI`
Lane: `project-point-profile-authority-and-ui`
Date: 2026-07-14
Role: Reviewer

## Gate

Reviewer plan gate only. No product code, schema, migration, API/client, test, real
database, or file implementation was changed or authorized by this review.

Current phase: Phase 11, Project Workbench / Matrix / Approval Package controlled
foundation.
Current active task: `TASK_361I_PROJECT_POINT_PROFILE_AUTHORITY_AND_UI`, planned
only.
Why allowed: the board records TASK_361H as complete/accepted and TASK_361I as the
current planned lane whose next legal action is this Reviewer plan gate.

## Authority And Persistence Review

The three proposed additive tables are the minimum sufficient project-level authority
boundary. The existing Measurement Plan family snapshot is target-owned and its draft
lifecycle requires an active confirmed Matrix, so it cannot safely persist a profile
for a new project or a project with zero eligible targets. The planned profile root,
revision, and category snapshots solve that gap without copying categories into target
snapshots or altering the accepted six-table Measurement Plan authority.

The root pointers, root-local revision sequence, draft/confirmed/superseded state,
partial uniqueness, immutable revision snapshots, and additive rollback boundary make
the lifecycle reviewable. Save and confirm use the submitted ordered canonical payload
and one transaction. Exact editable revision and fingerprint checks give a typed stale
`409`; confirm saves, supersedes, promotes, and repoints atomically. A failed
validation, stale check, or storage command rolls back without partial authority
promotion.

The root-scoped backend `ppc-N` allocator is adequately specified: it derives a
historical high-water under the save transaction, never reuses removed identities, and
keeps identity stable through non-semantic row edits. Unicode label normalization and
the persisted resolved-prefix contract provide deterministic duplicate handling. The
required row-level validation and database constraints remain the final no-write guard.

## Compatibility And Product Flow Review

The legacy bridge is correctly read-only. A uniform active confirmed target-family set
may be offered as an explicit suggestion only; workspace GET does not create, import,
or confirm data. Divergent, absent, or unconfirmed target authority yields the local
starter-row path, so there is no silent data loss or implicit promotion of legacy
families.

The profile-first setup contract supports no-target projects, while a draft cannot
leak into the Matrix: the Matrix summary reads active confirmed profile categories,
total, revision, and newer-draft warning only. Confirm is the only operation that
updates that summary. The planned direct route stylesheet ownership, feature hook and
selectors, dense inline rows, keyboard-aware ordering/removal, no-modal-first layout,
and narrow-width browser smoke align with the ConnLab product register and frontend
architecture boundaries.

## Scope, Validation, And Isolation Review

The planned May Touch list confines persistence to new profile modules plus narrow
database/API composition, and confines the UI to the profile feature, typed client,
setup route, and Matrix summary wiring. Target coverage, Matrix Step mapping and
overrides, Fee rules/pricing/UI, TASK_360B/TASK_361D workbook behavior, generic Test
Record/Report, parser/import, LTR/public drive, real databases/files, and governance
paths remain locked. Hiding obsolete target/workbook controls is UI-surface-only and
does not authorize any backend or consumer behavior change.

Temporary SQLite migration and transaction tests, typed API stale/no-target tests,
normalization and legacy-suggestion tests, focused selector/model/component/route
tests, confirmed-summary regression, controlled browser smoke, static scope scans,
and Integrator package isolation are proportionate. No schema migration is authorized
by this pass.

## Validation Performed

- Re-read AGENTS, task board, lane protocol, task, plan, and Planner evidence.
- Verified current code facts: existing target family snapshots are target-owned and
  `ContactMeasurementPlanLifecycleService.open_draft()` requires an active confirmed
  Matrix; the current Matrix summary is target/coverage/workbook-oriented.
- Loaded `$impeccable` product context and read frontend architecture rules. The plan
  uses a product-register route and feature-owned state/style boundary.
- Confirmed current status isolates TASK_361I to its task, plan, and Planner evidence.
  Existing TASK_361F operational evidence, board work, and TASK_361H QA screenshots
  are external residuals and excluded.
- Targeted tracked-doc diff check reported only known LF/CRLF warnings; no trailing
  whitespace was found in the TASK_361I task, plan, or Planner evidence.

## Decision

`reviewer_pass`

Recommended next role/action: explicit User approval, then Developer planning-first.
Do not route Developer implementation or authorize schema/product work directly.

Blocking summary: none for the planned-only Reviewer plan gate.

---

# TASK_361I Reviewer Implementation-Readiness Gate

Status: reviewer_pass
Task: `TASK_361I_PROJECT_POINT_PROFILE_AUTHORITY_AND_UI`
Lane: `project-point-profile-authority-and-ui`
Date: 2026-07-14
Role: Reviewer

## Planning-First Verification

Developer planning-first is documentation-only. Current status contains the TASK_361I
task, plan, and Planner/Reviewer/Developer evidence, but no TASK_361I backend,
frontend, schema, migration, API-client, or test implementation change. The board now
records Developer planning-first complete and this readiness gate as the next legal
action. Existing TASK_361F operational evidence and TASK_361H QA screenshots remain
external residuals.

## Implementation Readiness

The exact three-table SQLite contract is ready to implement. It is additive to the
accepted Measurement Plan authority: a project-unique root with nullable revision
pointers, root-local immutable revisions with separate editable/confirmed partial
uniqueness, and ordered category snapshots with included-row normalization and count
constraints. The dedicated migration first semantically validates every existing
profile table/index, then creates only missing additive objects inside one immediate
transaction, re-reads the resulting shape, rolls back DDL failures, and fails closed
as `authority_corrupt` for incompatible existing state. It neither rebuilds an
existing table nor operates on a real database in validation.

The lifecycle is sufficiently exact for a bounded implementation: first save permits
null expected revision/fingerprint only if no editable revision exists; later save and
confirm require both exact values; `ppc-N` is issued by the backend under the root
transaction using historical plus retained ids; normalization/prefix resolution is
persisted; and confirmation saves, supersedes, promotes, and updates root pointers in
one rollback-safe command. Root-scoped ownership, forged/cross-root rejection, and
typed stale `409` close the concurrency and duplicate contracts.

The optional legacy adapter remains read-only and suggestion-only. No profile root is
created by workspace GET, so no-target projects start with the local blank row and
can persist only through an explicit save. The narrow project-only DTOs keep target
coverage, Matrix revisions, LLCR/CR readings, workbook state, and draft categories
out of the confirmed Matrix summary. A later draft therefore changes only its warning
flag until confirmation.

The profile-first route/component plan fits the established page -> feature -> typed
client boundary. The hook owns async state; selectors own local validation, total,
starter/template, and ordering derivation; the editor owns dense accessible inputs;
and the page directly imports feature CSS for deep-link parity. Focus handling,
keyboard reorder, local discard, 514px/desktop smoke, no-modal-first layout, and the
confirmed-only summary are explicitly covered. Existing target commands and
TASK_360B/TASK_361D workbook behavior are removed only from this V1 surface, not
changed in their backend/client contracts.

## Scope And Validation

The exact May Touch list is narrow and sufficient: new profile domain/application/
storage/repository/route modules; narrow database, dependency, and API composition;
typed client helpers; a profile feature hook/selectors/editor; direct route/setup/
summary wiring; focused tests and governance evidence. Matrix Test Type/Sample Type,
coverage, target snapshots, Step mappings, Fee, workbook projection/generation,
TASK_361D, generic Test Record/Report, parser/import, LTR/public drive, real
databases/files, and governance paths remain locked.

The temporary SQLite fresh/legacy-compatible migration, lifecycle and API no-write,
stale, history, legacy-suggestion, confirmed-only summary, selector/model/component/
route, 514px/desktop browser, regression, build, static, and package-isolation gates
are proportionate for the schema-plus-UI lane.

## Validation Performed

- Re-read AGENTS, task board, TASK_361I task/plan, Planner/Reviewer/Developer
  evidence, current authority lifecycle, storage startup, direct setup route, Matrix
  summary, and frontend architecture/product context.
- Verified current code requires an active confirmed Matrix for target-plan drafts and
  exposes target/coverage/workbook controls in the existing setup surface, confirming
  why the planned independent no-target profile boundary is necessary.
- Verified `init_db()` already registers models then runs dedicated compatibility
  migrations after `create_all`, matching the planned additive migration boundary.
- Confirmed status/diff isolation: no TASK_361I implementation path changed by the
  Developer pass. Tracked-doc diff check reported only known LF/CRLF warnings; UTF-8
  trailing-whitespace scans found no matches.

## Decision

`reviewer_pass`

Recommended next role/action: explicit User approval for schema and product
implementation, followed by Planner/source-of-truth reconciliation before Developer
implementation. Do not route Developer implementation directly.

Blocking summary: none for implementation readiness; implementation remains
unauthorized pending the stated approval and reconciliation.

---

# TASK_361I Reviewer Implementation Gate

Status: reviewer_blocked
Task: `TASK_361I_PROJECT_POINT_PROFILE_AUTHORITY_AND_UI`
Lane: `project-point-profile-authority-and-ui`
Date: 2026-07-14
Role: Reviewer

## Gate

Reviewer implementation gate only. No product code, schema, migration, test, real
database, or file was changed by this review.

Current phase: Phase 11, Project Workbench / Matrix / Approval Package controlled
foundation.
Current active task: `TASK_361I_PROJECT_POINT_PROFILE_AUTHORITY_AND_UI`, Developer
implementation complete and pending this gate.
Why allowed: the board and reconciliation evidence record the completed approval chain
and assign Reviewer implementation gate as the sole next action.

## Findings

### B1: Existing-database migration is not fail-closed against the authorized schema contract

`migrate_contact_point_profile_schema()` validates only the set of column names and
the four named partial indexes. It does not validate SQLite affinity/nullability/PK,
FK local/referred columns and actions, named full CHECK expressions, table UNIQUE
constraints, or non-partial unique index shape. Consequently, a pre-existing table
with the expected column names but weakened or missing foreign keys, checks, or unique
constraints is accepted as compatible. `create_all()` cannot repair that table, so
the claimed fail-closed authority boundary is bypassed.

This contradicts the frozen migration contract in the plan, which explicitly requires
semantic validation of columns, FKs, full CHECKs, unique constraints, index order and
predicates before DDL. The current schema test only asserts fresh-table existence and
two index names; it never opens a disposable malformed existing database through the
real `init_db()` boundary.

**Required Developer fix:** make the profile migration use the same exact semantic
shape posture as the accepted compatibility migrations: verify all three tables'
column types/nullability/PK, FKs and actions, named CHECK expressions, table UNIQUEs,
and all four partial unique indexes. Add disposable existing-DB tests for weakened or
missing FK/CHECK/UNIQUE shape, asserting `authority_corrupt`, rollback/no profile DDL,
and unchanged existing rows; retain fresh/idempotent compatible startup coverage.

### B2: Draft inheritance and `ppc-N` no-reuse are not implemented

When `_save_draft()` creates a revision after a confirmed profile, it sets the parent
id but does not copy the active confirmed category snapshots. The workspace hook then
hydrates a blank starter row whenever there is no editable revision. This violates the
task contract that a subsequent draft is copied from the confirmed profile and loses
the operator's confirmed setup at the start of the normal revision workflow.

In addition, `_issue_category_ids()` accepts any `ppc-N` found anywhere in root
history. A client can submit a previously removed historical id and resurrect it;
the implementation does not limit retained ids to the current editable snapshot.
That contradicts the root-scoped monotonic contract that removed ids never return.
Finally, prefix canonicalization runs before a new id exists, so an unparseable label
falls back to ordinal-based `C{N}` rather than the mandated persisted `C{ppc_number}`
after removals/reorder.

**Required Developer fix:** copy active confirmed categories into a new editable
revision in the same transaction, hydrate them as the initial next-draft editor state,
and permit submitted retained ids only when they belong to that editable revision.
Allocate new ids before final prefix canonicalization, or otherwise guarantee the
persisted fallback is `C{ppc_number}`. Add service/API regressions for confirmed ->
new draft copy, removed-id resurrection rejection/no write, cross-root rejection,
delete/reorder/add high-water allocation, and unparseable-label fallback stability.

### B3: Matrix summary consumes the editable workspace instead of the confirmed-only summary boundary

`MatrixEditorWorkspace` constructs `useProjectPointProfileModel`, whose first request
is `/workspace` and whose DTO contains editable revision categories. The summary card
does not render those categories, but the Matrix surface still reads draft authority
instead of calling the dedicated `/summary` endpoint. The accepted contract requires
the Matrix summary boundary to receive confirmed categories/total plus the newer-draft
flag only; draft categories must not be transported into that surface.

**Required Developer fix:** give Matrix summary wiring a typed confirmed-summary read
model/hook that calls `/summary`, while setup keeps the richer workspace endpoint.
Add a focused Matrix regression proving an editable draft category is neither fetched
nor rendered by the Matrix summary while the draft warning remains visible.

### B4: Count input silently truncates decimal data

The editor updates a count with `Number.parseInt(..., 10) || 0`. Entering `1.5`
therefore becomes the valid persisted value `1`, rather than producing the planned
decimal validation error and no write. This is silent operator data loss and violates
the category validation contract.

**Required Developer fix:** preserve the entered numeric value until validation, reject
non-integers visibly before calling the typed API, and add a focused component/model
test that `1.5` remains invalid and issues no save/confirm request. Keep the optional
prefix behind the planned progressive `More` control while touching this dense row.

## Validation Performed

- Re-read AGENTS, task board, TASK_361I task/plan/Planner/Developer/reconciliation
  evidence, current status/diff, and the candidate backend/frontend/API/test code.
- Verified the source divergences above in the migration, lifecycle repository/hook,
  Matrix summary wiring, and profile editor.
- Re-ran backend focused Point Profile suite: `8 passed`.
- Re-ran frontend profile suite: `3 files / 3 tests passed`; MatrixEditorWorkspace:
  `1 file / 47 tests passed`; frontend build passed with the existing Vite chunk-size
  warning only.
- Re-ran `py_compile` for candidate backend modules and `git diff --check`; no
  compiler errors or whitespace findings occurred, with only existing LF/CRLF
  warnings. These green checks do not cover B1-B4.
- Candidate status remains limited to the authorized Point Profile package plus
  external TASK_361F operational evidence and TASK_361H screenshots. No review
  finding requires Fee, workbook, generic output, parser, LTR, or real-file scope.

## Decision

`reviewer_blocked`

Recommended next role/action: bounded Developer fix pass for B1-B4 only, then
Reviewer implementation re-gate. Do not route QA or Integrator.

Blocking summary: exact fail-closed migration validation, confirmed-draft inheritance
and never-reused identity/prefix behavior, confirmed-only Matrix summary transport,
and decimal-preserving UI validation must be corrected before QA browser smoke.

---

# TASK_361I Reviewer Implementation Re-Gate: B1-B4

Status: reviewer_blocked
Task: `TASK_361I_PROJECT_POINT_PROFILE_AUTHORITY_AND_UI`
Lane: `project-point-profile-authority-and-ui`
Date: 2026-07-14
Role: Reviewer

## Closed

- B3 is closed. Matrix Editor now uses a dedicated typed summary hook that calls the
  confirmed-only `/summary` endpoint. The compact card receives confirmed categories,
  total, revision, and the newer-draft flag only; it no longer transports editable
  workspace categories.
- The B1 preflight now validates the required column shape, FK columns/actions,
  required unique shapes, required partial indexes, and required CHECK expressions
  for an already complete Point Profile schema.
- The B2 server-side id issue/prefix order is improved: retained ids are limited to
  the editable snapshot or the active parent while a new draft is made, and fallback
  prefix resolution runs after `ppc-N` allocation.
- B4 preserves raw count input and moves Prefix into a native, accessible `More`
  disclosure.

## Remaining Findings

### B1R: Compatible partial schema state is rejected instead of being completed atomically

The frozen plan explicitly allows a compatible partial prior Point Profile state to
receive only its missing additive tables/indexes and then be re-read and verified.
The implementation instead enters `migrate_contact_point_profile_schema()` before
`create_all()` whenever any profile table exists, and immediately raises
`authority_corrupt` unless all three profile tables already exist. It therefore cannot
perform the specified partial-startup recovery. The current migration also checks CHECK
expression presence but not the required CHECK constraint names, despite the exact
named-CHECK contract.

**Required Developer fix:** distinguish no schema, compatible partial schema, and
incompatible existing schema. Preflight all present objects first, create only the
missing canonical tables/indexes in the authorized atomic migration path, then
re-read/verify the complete exact schema. Require both the specified constraint name
and canonical expression. Add disposable `init_db()` regressions for a compatible
partial state that completes successfully and for same-expression/wrong-name CHECK
state that fails closed with no partial Point Profile DDL or authority writes.

### B2R: Discard after a confirmed profile still erases the visible local baseline

Initial hydration correctly falls back to `confirmed_revision.categories` when no
editable revision exists. `discard()`, however, still falls back directly to a blank
starter row in that same state. After an operator edits a confirmed-only profile,
Discard changes therefore clears the rows rather than restoring the last loaded
confirmed baseline. This violates the local-discard contract and makes the next save
look like an unintended deletion.

**Required Developer fix:** use the same editable-else-confirmed-else-starter baseline
for discard and add a hook/component regression covering confirmed-only edit then
discard, including retained ids and total restoration.

### B4R: Raw numeric-input preservation now rejects every ordinary typed integer

Changing a number input produces a string. The selector preserves that raw string, but
both `projectPointProfileTotal()` and `pointProfileValidation()` use
`Number.isInteger(row.count_per_sample)`. Thus a user-entered valid value such as
`"4"` is treated as non-integer, total remains zero, and Save/Confirm cannot proceed.
The test covers only the invalid `"1.5"` case, so this regression remains hidden.

**Required Developer fix:** add one shared raw-count parser that accepts canonical
positive integer strings and numeric integers, rejects empty/decimal/negative/overflow
values without coercion, derives totals from accepted values, and converts only valid
rows into the typed API payload. Add selector/model/component regressions for valid
typed `"4"`, invalid decimal/empty/negative/non-integer/overflow, and no request on
invalid rows.

## Validation Performed

- Re-read the updated Developer evidence, Reviewer B1-B4 findings, candidate code,
  task/plan, current board, and current status/diff.
- Re-ran backend focused Point Profile suite: `10 passed`.
- Re-ran frontend Profile plus Matrix suite: `4 files / 51 tests passed`.
- Re-ran frontend build: passed with only the known Vite chunk-size warning.
- B1R, B2R, and B4R are source-level contract violations not exercised by the green
  tests above. No Fee, workbook, generic output, Matrix Step, parser, LTR, or
  real-file scope expansion is needed to resolve them.

## Decision

`reviewer_blocked`

Recommended next role/action: bounded Developer fix pass for B1R, B2R, and B4R only,
then Reviewer implementation re-gate. Do not route QA or Integrator.

Blocking summary: exact partial-schema recovery/named CHECK validation, confirmed
baseline discard, and valid raw integer input handling remain incomplete.

---

# TASK_361I Reviewer Implementation Re-Gate: B1R/B2R/B4R

Status: reviewer_blocked
Task: `TASK_361I_PROJECT_POINT_PROFILE_AUTHORITY_AND_UI`
Lane: `project-point-profile-authority-and-ui`
Date: 2026-07-14
Role: Reviewer

## Closed In Source

- B2R is closed in the hook. Hydration records the editable-or-confirmed baseline and
  `discard()` restores that stored baseline, leaving the starter row only for a truly
  empty authority.
- B4R is closed in source. The raw-count parser accepts canonical positive integer
  strings such as `"4"`, keeps invalid input out of the typed command, derives totals
  from accepted values, and the editor retains Prefix in an accessible native `More`
  disclosure.
- B3 remains closed. Matrix Editor uses the separate confirmed-summary hook and the
  summary card receives no editable workspace categories.
- B1R's per-table present-shape checks and named-CHECK token checks are an improvement
  over the prior implementation.

## Remaining Finding

### B1R2: Partial-schema creation is still not the planned atomic migration

The preflight correctly permits a compatible root-only or root-plus-revision state,
but it then returns to `init_db()` and relies on `Base.metadata.create_all()` to create
the missing objects. The creation is not inside the planned dedicated `BEGIN
IMMEDIATE` transaction, and `migrate_contact_point_profile_schema()` itself performs
no create/read-verify transaction. A create-all failure or competing writer during
partial-state completion can leave a new partial schema, contrary to the frozen
all-preflight-before-DDL, atomic bootstrap, rollback, and idempotency contract.

The candidate test files also do not substantiate the fix claims: there is no
root-only/root-plus-revision successful `init_db()` case, no wrong-name or
missing-name CHECK case, no hook test for confirmed-only edit then Discard, and no
test that valid raw `"4"` is counted, serialized as numeric `4`, and can invoke Save.
The current green 10 backend and 51 frontend tests therefore cannot protect the
newly repaired authority paths.

**Required Developer fix:** move Point Profile partial-object creation and final
semantic re-read into a dedicated SQLite `BEGIN IMMEDIATE` transaction after all
present-object preflight, with rollback on DDL/read-verify/lock failure. Add disposable
`init_db()` regressions for root-only and root-plus-revision completion/idempotency,
and wrong/missing CHECK-name fail-closed with no partial Point Profile DDL or writes.
Add the narrowly missing hook/selector regressions for confirmed baseline Discard and
valid raw `"4"` save payload, alongside the already-required invalid no-write cases.

## Validation Performed

- Re-read updated Developer evidence and directly inspected the migration/database
  boundary, profile hook/selectors/editor, Matrix summary hook/card, task/plan, and
  current candidate status.
- Re-ran backend Point Profile focused suite: `10 passed`.
- Re-ran frontend Profile plus Matrix suite: `4 files / 51 tests passed`.
- Re-ran frontend build: passed with only the existing Vite chunk-size warning.
- The remaining B1R2 atomicity and specified regression coverage gaps are not
  exercised by those passing tests. No Fee, workbook, generic output, Matrix Step,
  parser, LTR, or real-file scope change is required to resolve them.

## Decision

`reviewer_blocked`

Recommended next role/action: bounded Developer fix pass for B1R2 and its required
regressions, then Reviewer implementation re-gate. Do not route QA or Integrator.

Blocking summary: Point Profile compatible partial-schema bootstrap must be explicit,
atomic, and tested before QA can exercise the UI.

---

# TASK_361I Reviewer Implementation Re-Gate: B1R2

Status: reviewer_blocked
Task: `TASK_361I_PROJECT_POINT_PROFILE_AUTHORITY_AND_UI`
Lane: `project-point-profile-authority-and-ui`
Date: 2026-07-14
Role: Reviewer

## Closed In Source

- Point Profile tables are now excluded from the generic `Base.metadata.create_all()`
  call. Existing non-Point-Profile metadata still initializes through the prior path.
- The Point Profile bootstrap preflights all present profile objects, uses `BEGIN
  IMMEDIATE`, creates missing objects in root/revision/category FK order, and wraps
  bootstrap errors as readable `authority_corrupt` failures.
- B2R, B3, and B4R remain correctly bounded in source: baseline discard, confirmed
  summary-only Matrix transport, and strict raw positive-count parsing are intact.

## Remaining Finding

### B1R3: Final canonical verification occurs after the bootstrap transaction commits

`bootstrap_contact_point_profile_schema()` commits the `BEGIN IMMEDIATE` transaction
immediately after creating missing tables, then calls `migrate_contact_point_profile_schema()` on a new connection. A
final canonical-shape read/verify failure therefore cannot roll back the Point Profile
objects that were just created. This does not meet the frozen atomic bootstrap
contract, which requires final read-verify before commit and zero partial objects on
injected DDL or final-verification failure.

The requested proof cases are also not present in the actual candidate test files:
the schema test still has only fresh registration and one malformed-category case;
there is no root-only/root-plus-revision real-`init_db()` completion/idempotency,
wrong/missing CHECK-name, injected final-verify/locked-writer rollback, confirmed
baseline Discard, or valid raw `"4"` payload regression. The repeated green 10 backend
and 51 frontend tests do not demonstrate the claimed B1R2 behavior.

**Required Developer fix:** perform the canonical final verification on the same
connection before `COMMIT`, so any DDL, lock, or verification failure rolls back every
new Point Profile object. Add the requested disposable startup/rollback tests and the
narrow missing UI regressions; retain the non-Point-Profile initialization order.

## Validation Performed

- Directly inspected the final bootstrap/database code and the actual backend/frontend
  candidate tests rather than relying on evidence claims.
- Re-ran backend Point Profile suite: `10 passed`.
- Re-ran frontend Profile plus Matrix suite: `4 files / 51 tests passed`.
- Re-ran frontend build: passed with only the known Vite chunk-size warning.
- The outstanding atomic-final-verify and missing-regression gaps are not represented
  by those passing tests. No locked downstream scope change is required to resolve
  them.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer bounded fix pass for B1R3 and its required
regressions, then Reviewer implementation re-gate. Do not route QA or Integrator.

Blocking summary: final Point Profile bootstrap verification must occur before commit,
with executable rollback and UI regression proof.

---

# TASK_361I Reviewer Implementation Re-Gate: B1R3 Final

Status: reviewer_pass
Task: `TASK_361I_PROJECT_POINT_PROFILE_AUTHORITY_AND_UI`
Lane: `project-point-profile-authority-and-ui`
Date: 2026-07-14
Role: Reviewer

## Re-Gate Result

- The dedicated Point Profile bootstrap now preflights existing profile tables,
  starts `BEGIN IMMEDIATE`, creates only missing tables in FK order, performs final
  canonical verification on that same connection, and commits only after verification
  succeeds. DDL and final-verification exceptions roll back the transaction.
- Actual disposable-SQLite regression nodes cover root-only and root-plus-revision
  completion/idempotency; wrong and missing named CHECKs failing before category DDL
  with unchanged schema; injected create and final-verification rollback; and locked
  writer zero-DDL followed by successful retry after release.
- Confirmed-baseline Discard restores the complete authority rows, so the following
  Save payload cannot silently delete confirmed categories. Strict count parsing keeps
  raw `"4"` in the live total and serializes it as numeric `4`; malformed values do
  not issue a write.
- The Matrix summary remains confirmed-only. An editable draft may produce its
  warning, but cannot replace displayed categories, totals, or revision identity.
- Candidate modules remain below the task hard limit. Fee, workbooks, generic Test
  Record/Report, Matrix Step, parser, LTR/public-drive, and real-file scope remain
  outside the candidate package.

## Validation Performed

- Re-ran the Point Profile backend focus (`fingerprint`, legacy suggestion, schema,
  lifecycle, API): `17 passed`.
- Re-ran the Profile plus Matrix frontend focus: `5 files / 55 tests passed`.
- Re-ran `py_compile` across the Point Profile backend modules: passed.
- Re-ran `npm run build`: passed with only the existing Vite chunk-size warning.
- `git diff --check` passed apart from existing LF/CRLF notices; candidate trailing
  whitespace scan found no matches. External TASK_361F operational evidence, board,
  and TASK_361H screenshot residuals remain excluded.

## Decision

`reviewer_pass`

Recommended next role/action: QA gate, including controlled disposable-fixture browser
smoke at desktop and 514px widths. Do not route Integrator from this gate.

Blocking summary: none for Reviewer implementation re-gate.
