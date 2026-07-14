# TASK_361J Point Profile Range Expression And Simplified Editor Plan

## Status

Complete/accepted locally after Integrator package re-gate. Developer implementation
and focused fixes, Reviewer implementation re-gates, QA re-smoke, and the explicit
button-style dependency reconciliation all passed. Product behavior and prior
Reviewer/QA conclusions remain unchanged; remote push was intentionally not performed.

Authorization is limited to nullable canonical `point_expression` additive migration
with V1/V2 fail-closed bootstrap; bounded expression parsing/canonicalization and
derived count; explicit legacy count-only `1-N` conversion; case-preserved user prefix;
direct atomic confirm-only command, Cancel zero-write, and typed draft `410` no-write;
typed API/DTO/client/model; compact Prefix/Test points/delete table with header Add row
and only Cancel/Confirm; confirmed-only Matrix summary; count/prefix compatibility;
and focused tests plus desktop/514px smoke. All locks and hunk-isolation rules remain
controlling.

## Discovery Gate

### Current Phase / Active Task / Role / Why Allowed

- Phase: Phase 11 controlled Matrix foundation.
- TASK_361I is complete/accepted at `9bf765a894b1970f4a764c3b7fe466ca61582a59`.
- Active task: TASK_361J package scope reconciled / pending Integrator package re-gate.
- Role: Planner. Initial Discovery was planned-only; the completed gate chain and
  later explicit implementation approval are recorded in Status and reconciliation
  evidence.

### Confirmed By User

- Prefix and point expression are the only business inputs per row.
- Prefix is never guessed, translated, or auto-abbreviated.
- Point expressions must persist canonically so sparse sets remain reconstructable.
- Counts are derived compatibility/read-model data, not operator input.
- Editing is local-only; only Confirm writes. Cancel is zero-write navigation.
- Matrix summary is confirmed-only and carries no local/draft warning.
- No expanded point preview, templates, Use, label/count inputs, ordering controls,
  draft commands, or top Back action remain.
- This lane excludes coverage, Step semantics, Fee, workbooks, generic outputs, Office,
  parser/import, LTR/public drive, and real data/files.

### Confirmed By Repository Evidence

- TASK_361I persists three authority tables. Category snapshots currently store
  `label`, `count_per_sample`, `record_prefix`, and `included`, but no exact point set.
- The current lifecycle saves an editable draft first and confirms that draft. The
  frontend therefore exposes Save draft and requires it before Confirm.
- Current workspace hydration prefers editable revision over confirmed revision.
- The current summary reads the confirmed endpoint but displays category label/count
  and a newer-draft warning.
- Prefix canonicalization currently uppercases and strips characters, which conflicts
  with the new operator-owned display contract.
- `init_db()` already delegates Point Profile table creation/shape checking to the
  dedicated fail-closed profile migration.
- The accepted package has focused temporary SQLite, API, selector/model/component,
  Matrix summary, and browser test boundaries that TASK_361J can extend.

### Planner Decisions

- Use one nullable canonical expression column on the existing category snapshot
  table. A child point-members table adds persistence and join complexity not needed
  for V1; storing only free text cannot guarantee count/materialization consistency.
- Keep `count_per_sample` persisted as a derived compatibility field so existing
  count/prefix consumers remain stable.
- Use `NULL` expression as the explicit legacy count-only marker. Do not invent a
  sparse set during migration.
- Preserve the existing project-rooted revision history and monotonic `ppc-N`
  category identities. Confirm directly creates the next confirmed revision.
- Keep the old draft route as a typed no-write `410` compatibility boundary rather
  than deleting it or allowing obsolete clients to create hidden drafts.
- Keep this as one lane because schema/API/local editor/summary behavior form one
  testable operator flow. Consumer migration and point-list workbook use remain later,
  separately approved work.

### Not Yet Confirmed

No blocking product question remains. The V1 ASCII prefix and numeric safety limits
are Planner-frozen implementation constraints for Reviewer evaluation. Any request to
support spaces, Unicode prefixes, larger limits, or point-list consumers requires a
separate scope change/re-gate.

## Options Assessed

1. **Recommended: nullable canonical expression on category snapshots.** Smallest
   additive migration, preserves revision snapshots, keeps count compatibility, and
   distinguishes exact expressions from legacy count-only rows.
2. **Point-members child table.** Strong relational point membership but multiplies
   rows, schema, repository, fingerprint, and migration work for no current consumer.
3. **Expression only, derive count only at read time.** Simpler storage but risks
   breaking accepted consumers that already depend on persisted count and makes
   rollback compatibility harder.

Option 1 is controlling for TASK_361J.

## Data And Migration Design

### V2 Category Shape

Add `point_expression TEXT NULL` to
`contact_point_profile_categories`. Fresh table DDL includes a named nonblank-if-set
check. Existing columns, FKs, unique constraints, partial indexes, and category rows
remain unchanged.

Semantics:

- `point_expression IS NULL`: legacy count-only authority.
- `point_expression IS NOT NULL`: canonical explicit point-set authority.
- `count_per_sample`: parser-derived cardinality for explicit rows; original persisted
  compatibility value for legacy rows.
- `record_prefix`: exact trimmed display prefix.
- `label`: compatibility mirror of prefix for new confirmed revisions.
- `included`: always true for new confirm-only revisions; legacy value is preserved in
  historical revisions.

### Existing SQLite Transaction

1. Read sqlite metadata and classify profile category table as exact V1, exact V2, or
   incompatible before DDL.
2. Fail closed on partial column/check shape, wrong type/nullability, or any existing
   TASK_361I constraint/index mismatch.
3. For exact V1 only, enter `BEGIN IMMEDIATE` and add the nullable expression column
   with the named nonblank-if-set check.
4. Run exact V2 columns/FKs/checks/index validation before commit.
5. Roll back the schema transaction on any failure and return `authority_corrupt`.
6. Exact V2 startup is idempotent. No business row update, table rebuild, writable
   schema trick, delete, or repair is permitted.

## Expression Service

Create `backend/application/contact_point_profile_expression.py` so parsing does not
inflate the fingerprint or lifecycle modules.

The service:

- accepts at most 1024 source characters;
- tokenizes positive integers and ascending inclusive ranges with optional ASCII
  whitespace;
- rejects empty tokens, trailing commas, reverse ranges, zero/negative/decimal/
  exponent/non-numeric input;
- enforces index `<=9999`, distinct category size `<=4096`, profile total `<=8192`,
  and category count `<=256`;
- uses a bounded integer set, then sorts and compresses maximal consecutive runs;
- returns canonical text, immutable ordered point numbers, and derived cardinality;
- never emits expanded point labels to the UI.

Prefix validation preserves the trimmed ASCII display text exactly, validates
`[A-Za-z][A-Za-z0-9_-]*` with maximum length 64, and compares case-insensitive keys.
No label-to-prefix fallback survives in the new confirm command.

## Confirm-Only Authority Flow

### Read

The workspace read model exposes confirmed revision as the only editing baseline.
Explicit rows return canonical expression. Legacy rows return null expression,
`legacy_count_only`, and a computed contiguous suggestion when count is positive and
included. The suggestion is presentation input, not persisted authority.

An old editable draft may be reported as `legacy_draft_present`, but its rows do not
hydrate the editor and Matrix never shows a draft warning.

### Local Edit And Cancel

The hook creates local rows from confirmed authority or one blank row. Add/delete/
typing/reordering-by-current-row-order are local React state only. There is no autosave
or draft request. Cancel calls the existing Matrix navigation callback directly and
makes no request. Browser reload discards local edits.

### Confirm Transaction

Request:

```text
actor
expected_confirmed_revision_id | null
expected_confirmed_revision_fingerprint | null
categories[]: category_id | null, prefix, point_expression
```

Application order:

1. Parse every expression and prefix before persistence; derive canonical expressions
   and counts; reject the whole command on any error.
2. Start one repository transaction and load the project root/active confirmed state.
3. Match both expected confirmed values. A first-confirm race is a typed stale `409`.
4. Retain project-owned category ids; allocate new monotonic `ppc-N` ids without
   reuse; reject foreign/duplicate ids.
5. If a legacy editable revision exists, mark it superseded with an explicit reason
   and clear `editable_revision_id`. Preserve its rows/history.
6. Supersede the current confirmed revision.
7. Allocate `revision_sequence` as `max(all revisions for root)+1`, not active+1, so a
   retained legacy draft cannot collide. Insert the next revision directly as
   confirmed, with the prior confirmed revision as parent, persist ordered categories
   with canonical expression plus derived count, and set the root active pointer.
8. Fingerprint ordered ids, prefixes, expressions, counts, compatibility keys, and
   revision identity under an explicit `point-profile:v2` payload marker; flush and
   commit atomically. Existing V1 fingerprints remain opaque expected-value tokens and
   are not recomputed by migration or reads.

Any validation, uniqueness, stale, or database failure leaves active pointers,
revision states, category rows, and history unchanged.

### Obsolete Draft Boundary

`PUT /draft` stays registered but always returns HTTP `410` with code
`contact_point_profile_draft_disabled` and performs no repository call. The current
client removes `saveProjectPointProfileDraft`; the UI has no draft controls. Existing
workspace compatibility fields may remain during this lane, but current selectors do
not hydrate or advertise drafts.

## API And DTO Changes

- Category read DTO adds `point_expression: string | null`,
  `expression_status: explicit | legacy_count_only`, and
  `legacy_contiguous_suggestion: string | null`.
- Existing `label`, `record_prefix`, `count_per_sample`, and `included` response fields
  remain for accepted compatibility paths.
- Confirm input uses `prefix` and `point_expression`; it does not accept authoritative
  label/count/included/ordinal values.
- Workspace exposes confirmed baseline and optional `legacy_draft_present` diagnostic.
- Summary remains confirmed-only. Matrix renders `record_prefix` and derived count,
  total, and revision; it ignores all draft flags.
- No API route, page, or client parses expressions outside the application grammar
  service except a matching frontend display validator used for immediate feedback.

## Simplified Product UI

The operator is at a daytime Windows lab workstation and needs a compact ledger-like
entry surface. Use the existing restrained ConnLab palette and feature-owned CSS.

- One semantic table, no nested cards.
- Header shows `N categories` and `M points / sample`.
- Columns: Prefix, Test points, action.
- Action header contains Add row; each body row has a compact delete icon button with
  title/tooltip and row-specific `aria-label`.
- No point chips/list/preview. `Signal 1-128` only changes the numeric total.
- Footer contains secondary Cancel and primary Confirm point profile.
- Inline errors identify row and field. Confirm is disabled for invalid/empty state or
  while a command is running.
- On stale `409`, preserve local entries, disable further Confirm, and direct the user
  to Cancel/reopen. Do not auto-rebase or silently overwrite.
- Confirm success navigates to Matrix, whose summary reloads confirmed authority.
- At 514px, use fixed table tracks, compact action width, wrapping status copy, and
  inputs with `min-width:0`; do not switch to oversized cards or allow horizontal
  overflow.

## TDD And File-Level Order

1. Add failing expression/prefix tests, then the new application expression service.
2. Add V1/V2/malformed/rollback schema tests, then update model/migration.
3. Add failing direct-confirm/legacy/stale/no-write tests, then repository, fingerprint,
   lifecycle, read, and route changes.
4. Update typed client contract.
5. Add selector/hook tests for local-only state and canonical totals, then update
   selectors/model hook.
6. Add editor/workspace/summary tests for exact controls, Cancel/Confirm navigation,
   legacy display, accessibility, and no draft warning, then update components/CSS.
7. Run accepted TASK_361I and downstream count/prefix regressions, build, browser
   smoke, and package scans.

New parser/normalizer code belongs in the new focused module. Existing files remain
under AGENTS line limits; split rather than grow a service beyond its responsibility.

## Worktree Isolation

The user resolved the Integrator blocker by assigning the exact style dependencies
required by the implemented simplified editor to TASK_361J:

- CSS hunks for `contact-measurement-button`, `contact-measurement-action-group`,
  primary, secondary, compact, disabled, focus/hover, and responsive behavior;
- matching class references in `ProjectPointProfileEditor.tsx`; and
- the prior `ContactMeasurementSetupWorkspace.tsx` Back-button class hunk as historical
  overlap only. Because TASK_361J removed the Back action, no obsolete UI or dead class
  reference is required.

Integrator may hunk-stage these three mixed files so the final commit contains the
implemented JSX and its required styling. Integrator must not stage any file wholesale
or absorb unrelated CSS/workspace/editor changes. Other board hunks, TASK_361F evidence,
TASK_361H artifacts, and locked product residuals remain excluded.

## May Touch

The task's exact Authorized May Touch list controls future implementation. It is
limited to Point Profile model/migration/repository/expression/fingerprint/lifecycle/
read/API files, typed Point Profile client surface, Point Profile selectors/hook/editor,
setup workspace, confirmed summary, feature CSS, focused tests, and TASK_361J
governance.

## Must Not Touch / Locked Paths

- Existing Measurement Plan target authority schema/lifecycle and all Matrix Step
  Test Type/Sample Type, Group/Step coverage/applicability/override mapping.
- TASK_361E Fee source plus all Fee rules/pricing/UI/default-fill/export behavior.
- TASK_360B/TASK_361D and all specialized or generic workbook/output generation.
- Generic Test Record/Report, StepInstance, parser/import, LTR/public drive,
  XLSM/VBA/COM, real DB/files/folders.
- Dependencies, Settings/release, `.agents/**`, `docs/project_management/**`, external
  residual cleanup, destructive git, commit, and remote push.

## Validation Gate

- Backend unit/integration/API suites described in the task, using temporary SQLite
  only.
- Frontend selector/hook/component/Matrix summary suites.
- Desktop and 514px browser smoke covering no-confirmed, canonicalization, Cancel,
  Confirm, summary reload, legacy conversion, no expanded preview, and no console
  errors.
- `py -m py_compile`, focused `py -m pytest`, focused `npm test`, `npm run build`.
- Seed/real path scan, no operator DB/file access, diff-check, UTF-8 trailing whitespace,
  line-count, exact whitelist, forbidden-content, and mixed-hunk package review.

## Merge Gate

Reviewer plan gate -> explicit User approval for Developer planning-first -> Developer
docs-only planning-first -> Reviewer implementation-readiness -> explicit User schema/
product approval -> Developer implementation/fixes -> Reviewer implementation re-gates
-> QA re-smoke -> Planner package-scope reconciliation -> Integrator hunk-level package
re-gate and acceptance (complete).

## Definition Of Ready

Satisfied and accepted. The operator flow, authority ownership, exact additive field,
V1/V2 migration, grammar, prefix policy, legacy conversion, direct confirm
transaction, API/client/UI boundary, validation, locks, and exact hunk-level package
ownership were verified in the accepted package.

## Next Legal Role

Orchestrator/User decision for any later separately approved lane. No Developer rerun
is required.

## Developer Planning-First Refinement (2026-07-15)

### Exact SQLite V1/V2 Recognition

The current V1 table is the exact TASK_361I category shape validated by
`contact_point_profile_schema_migration.py`: all existing columns, foreign key,
named checks, table unique constraints, and required partial unique indexes must
remain structurally valid before the new field is considered. V2 is V1 plus exactly:

```sql
point_expression TEXT NULL
CONSTRAINT ck_contact_point_profile_point_expression_nonblank
  CHECK (point_expression IS NULL OR length(trim(point_expression)) > 0)
```

The V2 field has SQLite `TEXT` affinity, remains nullable, and does not change V1
indexes or rewrite rows. New model DDL must create V2. Existing exact V1 may be
upgraded only through a disposable-fixture-proven `ALTER TABLE ... ADD COLUMN`
column definition that preserves the named check in `sqlite_master`; the migration
must first confirm that this SQLite form has the same named constraint recognition as
fresh V2 DDL.

Future migration algorithm, all in the dedicated Point Profile schema migration:

1. Open a read connection and classify the physical category table as exact V1,
   exact V2, or incompatible. Existing root/revision/category shapes must all pass
   their current fail-closed verification first.
2. For exact V1, begin `BEGIN IMMEDIATE`; do no business-row reads or writes before
   schema preflight completes.
3. Add only the V2 column/check, then run transaction-visible V2 canonical shape
   verification with `PRAGMA table_info`, FK/index metadata, and named-check SQL.
4. Commit only after that verification. Any DDL, verification, or lock failure rolls
   back and surfaces `authority_corrupt`; no rebuild, writable-schema operation, row
   repair, deletion, or fallback is allowed.
5. Exact V2 reruns are idempotent. A V1/V2 partial or wrong affinity/nullability/check
   shape is fail-closed before DDL.

### Expression And Legacy Contract

`backend/application/contact_point_profile_expression.py` will be a pure module with
one parse result value containing canonical expression, sorted immutable point set,
and derived count. It accepts bounded positive integers, commas, ascending inclusive
ranges, and optional ASCII surrounding whitespace. It rejects empty source/token,
trailing comma, zero, negative, decimal, exponent, alphabetic input, reverse range,
source length over 1024, point index over 9999, more than 4096 points/category, more
than 256 rows, and profile total over 8192. Valid input deduplicates, orders, and
compresses maximal runs. Error taxonomy remains typed application validation errors,
never route-local parsing.

`point_expression IS NULL` remains an explicit `legacy_count_only` marker. A positive
included legacy count can only be shown as a non-authoritative contiguous `1-N`
suggestion. It becomes explicit authority only when the operator confirms a new V2
revision. Legacy rows are never silently rewritten, and a suggested contiguous set
never claims to describe a historical sparse layout.

### Implementation File Order

1. Add parser/normalizer unit tests, then the new expression module.
2. Add temporary SQLite fresh/V1/V2/malformed/rollback tests, then update the Point
   Profile model and schema migration only.
3. Add lifecycle/repository/fingerprint/read/API red tests for direct confirm,
   stale, legacy conversion, obsolete draft `410`, and atomic rollback; then change
   the corresponding existing Point Profile files.
4. Update only the typed Point Profile API client DTO/commands.
5. Add selector/model tests first, then replace the draft-first model with local-only
   Prefix/Test-points state and direct confirm.
6. Add component and Matrix summary tests first, then change the editor/workspace/
   confirmed-only summary/CSS. The direct route owns navigation; it does not collect
   business state.

The direct confirm command must use the latest confirmed revision id/fingerprint,
write one confirmed revision atomically, and return a typed stale `409` without an
automatic retry. `PUT /draft` becomes an intentional `410
contact_point_profile_draft_disabled` no-write boundary. Prefix uses only trim,
length, ASCII shape, and case-insensitive uniqueness validation. It must preserve the
operator's spelling and case, never synthesize or uppercase an abbreviation.

### Exact Test Matrix And Package Rule

- Parser: canonical expression, duplicate/overlap/order compression, each rejected
  syntax/limit, and count derivation.
- Storage: fresh V2, V1-to-V2, exact V2 idempotency, malformed/partial preflight,
  transactional create/final-verification rollback, and lock failure using temporary
  SQLite only.
- API/lifecycle: first confirm, reconfirm, stale, concurrent first confirm,
  legacy-contiguous conversion, old-draft `410` no-write, and rollback.
- Frontend: one blank row, 4+5+24 total 33, Add/delete, local-only edit, Cancel
  zero-call navigation, Confirm command/reload, invalid/no-call, exact control
  absence, 514px and desktop accessibility smoke.
- Compatibility: Matrix remains confirmed-only and shows prefix/count/total/revision
  without a local-draft warning; Fee/workbook regression only proves continued
  derived-count/prefix reads and does not migrate consumer semantics.

The CSS, setup workspace, and editor files contain mixed hunks. The later user package
decision assigns only the required button/action-group style definitions and current
simplified-editor class references to TASK_361J. Integrator must hunk-stage those
dependencies and exclude every unrelated hunk; the removed Back-button class is only
historical overlap and must not be reintroduced.
