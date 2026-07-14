# TASK_361J Reviewer Plan Gate

Date: 2026-07-15
Role: Reviewer
Status: reviewer_pass
Task: `TASK_361J_POINT_PROFILE_RANGE_EXPRESSION_AND_SIMPLIFIED_EDITOR`
Lane: `point-profile-range-expression-simplified-editor`

## Gate Scope

This is a read-only plan gate. TASK_361J remains planned only; schema, backend,
frontend, API-client, and test implementation are not authorized.

## Review Result

- A single nullable `point_expression` category-snapshot column is an appropriately
  small additive authority extension. The V1/V2 recognition, present-shape preflight,
  same-transaction V1 upgrade, final V2 verification, rollback, and fail-closed
  incompatible-shape contract preserve existing revision history without table rebuild,
  row rewrite, repair, or real-database access.
- The canonical expression grammar is bounded and deterministic: it rejects unsafe
  syntax and limits, deduplicates/sorts/compresses valid point sets, and derives the
  persisted compatibility count. Prefix handling preserves the trimmed user value and
  case while validating a narrow existing-consumer-compatible ASCII boundary; it does
  not invent or translate abbreviations.
- Legacy `count + prefix` data remains explicit `legacy_count_only` authority. Its
  contiguous `1-N` value is a read-only conversion suggestion, becomes authority only
  through a new confirmed revision, and never fabricates a sparse set. Existing count
  and prefix consumers stay compatible without a Fee/workbook semantic migration.
- The direct confirm-only command has a complete atomicity and stale contract:
  expected confirmed id/fingerprint, first-confirm race handling, monotonic category
  identities, legacy-draft supersession, revision sequencing, canonical v2
  fingerprinting, and all-or-nothing failure behavior. The retained draft endpoint's
  typed no-write `410` is a suitable old-client compatibility boundary.
- The UI plan is suitably narrow for ConnLab: an accessible Prefix/Test-points table,
  icon deletion with accessible naming, local-only edits, Cancel zero-write, and
  confirm-only persistence. It explicitly removes the accepted draft editor's
  unnecessary controls and keeps Matrix summary confirmed-only without a local-draft
  warning. The desktop and 514px acceptance criteria are concrete.
- May Touch, locks, temporary SQLite/browser validation, and hunk-level package
  isolation are adequate. In particular, the existing CSS, setup-workspace, and
  editor modifications are external residuals; a future implementation must isolate
  only TASK_361J hunks against accepted TASK_361I HEAD `9bf765a8`.

## Validation Performed

- Re-read AGENTS, task board, lane orchestration protocol, role registry, TASK_361J
  task/plan/Planner evidence, accepted TASK_361I migration/lifecycle/editor/model,
  and frontend architecture/product-design guidance.
- Board status is consistent: TASK_361J is the current planned-only task and Reviewer
  plan gate is the next legal action.
- Reviewed current status/diff. The only current product diffs are the explicitly
  excluded CSS/setup-workspace/editor residuals; TASK_361J Planner pass is docs-only.
- Task/plan/Planner-evidence diff check passed with existing LF/CRLF notices only;
  trailing-whitespace scan found no matches.

## Decision

`reviewer_pass`

Recommended next role/action: User approval, then Developer planning-first only. Do
not authorize Developer implementation from this gate.

Blocking summary: none for Reviewer plan gate.

---

# TASK_361J Reviewer Implementation-Readiness Gate

Date: 2026-07-15
Role: Reviewer
Status: reviewer_pass
Task: `TASK_361J_POINT_PROFILE_RANGE_EXPRESSION_AND_SIMPLIFIED_EDITOR`
Lane: `point-profile-range-expression-simplified-editor`

## Readiness Result

- Developer planning-first is docs-only. No product, schema, API-client, test, real
  database/file, staging, commit, or push action was taken in that pass.
- The V1/V2 shape is implementable: existing Point Profile root/revision/category
  shape is preflighted before DDL; only exact V1 may add nullable
  `point_expression` plus the named nonblank-if-set CHECK; transaction-visible V2
  verification occurs before commit; incompatible/partial/lock/verification failures
  fail closed with no row mutation or partial schema.
- The planned expression service has a bounded grammar, canonical string and point-set
  result, derived count, explicit limits, and application-owned validation errors.
  Frontend validation is display feedback only and cannot become persistence authority.
- Legacy count-only rows remain distinguished from exact points. A read-only `1-N`
  suggestion is converted only by the operator's successful direct confirm, so sparse
  historical data is neither guessed nor rewritten.
- The direct confirm transaction, stale/first-confirm checks, revision/category
  identity rules, supersession, v2 fingerprint, rollback, Cancel zero-write behavior,
  latest-confirmed reload, and typed `410` legacy-draft boundary are sufficiently
  concrete for implementation.
- API/client/editor/model/summary responsibilities remain narrow. The editor is a
  compact, accessible local table with Prefix/Test points/delete, header Add row, and
  only Cancel/Confirm actions. Matrix remains confirmed-only; Fee/workbook consumers
  retain derived prefix/count reads without receiving expression semantics.
- May Touch, locked paths, temporary fixtures, TDD sequence, desktop/514px smoke,
  and mandatory hunk-level isolation from the existing CSS/setup/editor residuals are
  explicit. The package must stop for reconciliation if isolated TASK_361J hunks
  cannot be staged independently of those residuals.

## Validation Performed

- Re-read the updated TASK_361J plan and Developer evidence, task board, accepted
  TASK_361I migration/lifecycle/read/API/frontend facts, and frontend architecture/
  product-design context.
- Current status confirms the Developer pass added/refined TASK_361J governance docs
  only. Existing CSS, setup-workspace, and editor diffs remain external residuals.
- Developer-reported docs diff check passes with only existing LF/CRLF notices;
  TASK_361J docs trailing-whitespace scan is clean.

## Decision

`reviewer_pass`

Recommended next role/action: explicit User approval, followed by Planner/source-of-
truth reconciliation before Developer implementation. This gate does not authorize
schema or product implementation.

Blocking summary: none for implementation-readiness.

---

# TASK_361J Reviewer Implementation Gate

Date: 2026-07-15
Role: Reviewer
Status: reviewer_blocked
Task: `TASK_361J_POINT_PROFILE_RANGE_EXPRESSION_AND_SIMPLIFIED_EDITOR`
Lane: `point-profile-range-expression-simplified-editor`

## Findings

### B1: Direct confirm does not reject duplicate retained category IDs before persistence

`confirm_direct()` accepts a payload containing the same active `ppc-*` id twice.
`_issue_category_ids()` verifies only that each supplied id exists in the retained set;
it does not verify uniqueness within the incoming command. The later category insert
therefore raises SQLite `UNIQUE (revision_id, category_id)` `IntegrityError` rather
than the required typed validation/no-write error. A disposable SQLite reproduction
confirmed this path.

**Required fix:** reject duplicate submitted non-null category IDs in the direct
command before any revision/root/category mutation, return the existing typed command
validation response, and add lifecycle/API rollback regressions for duplicate retained
IDs and foreign IDs.

### B2: The migration lacks an executable exact V1 category-table upgrade regression

The schema suite covers fresh V2 and root/revision-only partial bootstrap, but no test
creates the accepted TASK_361I V1 category table with a persisted legacy category row,
runs production `init_db()`, and proves the one-column V1-to-V2 upgrade. Consequently
the candidate does not prove that the named CHECK is preserved and recognized after
SQLite `ALTER TABLE`, that the legacy row retains its fields with
`point_expression IS NULL`, or that a second startup is V2-idempotent.

**Required fix:** add a disposable exact V1 fixture using the accepted TASK_361I
physical schema and legacy row; call real `init_db()`; assert only the additive column/
CHECK change, retained legacy values and `NULL` expression, exact V2 revalidation, and
idempotent rerun. Keep malformed/partial V1/V2 cases fail-closed before DDL.

### B3: The compact editor does not meet the required icon-delete and local category-limit guards

The row action is a visible text `Delete` button rather than the frozen compact delete
icon with accessible label/tooltip. Also `pointProfileValidation()` has no `256`
category limit despite the backend command limit: the UI can enable Confirm for 257
otherwise-valid rows, issue a request, and only then receive a generic failure. The
contract requires invalid limits to be visible locally and to prevent the command.

**Required fix:** use the established icon mechanism (without adding a dependency) for
the compact delete action while retaining title and row-specific `aria-label`; add the
maximum-category selector guard and tests proving 257 rows disable/no-call. Preserve
the exact Prefix/Test-points/delete table and hunk-level isolation.

## Validation Performed

- Directly inspected actual migration, expression, lifecycle, repository, API, client,
  model, compact editor, summary, focused tests, and mixed-file diff.
- Re-ran backend expression/lifecycle/schema/API suite: `24 passed`.
- Re-ran frontend Profile/Matrix suite: `5 files / 52 tests passed`.
- Reproduced the duplicate-retained-id failure with disposable SQLite: it reaches
  SQLite `IntegrityError` for the revision/category unique constraint.
- Re-ran candidate `py_compile`, `git diff --check`, and trailing-whitespace scan:
  passed apart from existing LF/CRLF notices. Existing TASK_361F evidence, board, and
  CSS/setup-workspace/editor residuals remain excluded.

## Decision

`reviewer_blocked`

Recommended next role/action: bounded Developer fix pass for B1-B3, then Reviewer
implementation re-gate. Do not route QA or Integrator.

Blocking summary: direct-confirm identity validation, exact V1 migration proof, and
the frozen compact-editor guards must be completed before QA.

---

# TASK_361J Reviewer Implementation Re-Gate: B1-B3

Date: 2026-07-15
Role: Reviewer
Status: reviewer_blocked
Task: `TASK_361J_POINT_PROFILE_RANGE_EXPRESSION_AND_SIMPLIFIED_EDITOR`
Lane: `point-profile-range-expression-simplified-editor`

## Closed

- B1 is closed. Direct category parsing rejects duplicate supplied non-null category
  ids before the repository transaction; lifecycle proof preserves authority counts
  and the route maps the condition to typed HTTP `422`.
- B3 is closed. The compact table has an accessible icon-only delete control, retains
  Add row in the action header, blocks additions at 256 rows, and selector/model/
  lifecycle validation blocks a hydrated 257th row without a confirm request/write.
- The original direct-confirm, expression, legacy, Cancel, and confirmed-only summary
  boundaries remain intact. No locked consumer or real-file scope change was found.

## Remaining Finding

### B2R: V1 upgrade regression does not prove full legacy-row preservation

`test_exact_v1_category_table_upgrades_in_place_and_preserves_legacy_row` correctly
creates an exact V1 physical table and invokes production `init_db()`, but it asserts
only a subset of the migrated row (`category_id`, ordinal, count, record prefix,
included, and new expression). Its post-upgrade comparison is taken only after the
upgrade, so it cannot detect a migration that changed the legacy snapshot id,
revision id, label, normalized label key, or normalized prefix key.

**Required tests-only fix:** capture the complete V1 category row before `init_db()`
and compare it after migration field-for-field, with only `point_expression=NULL`
added. Include snapshot/revision ids, label, both normalized keys, count, prefix,
included, and ordinal. Retain the existing named-CHECK, V2 idempotency, and malformed
pre-DDL fail-closed assertions. No product implementation change is needed.

## Validation Performed

- Directly re-read the B1/B2/B3 implementation and regressions.
- Re-ran backend Point Profile focus: `29 passed`.
- Re-ran frontend focused suite: `4 files / 8 tests passed`.
- Re-ran frontend build: passed with only the existing Vite chunk-size warning.
- Candidate `py_compile`, diff check, and trailing-whitespace scan passed with only
  existing LF/CRLF notices. External TASK_361F, board, CSS/setup/editor residuals
  remain excluded.

## Decision

`reviewer_blocked`

Recommended next role/action: tests-only Developer fix pass for B2R, then Reviewer
implementation re-gate. Do not route QA or Integrator.

Blocking summary: the V1 upgrade proof must verify complete legacy snapshot
preservation, not only selected fields.

---

# TASK_361J Reviewer Implementation Re-Gate: B2R Final

Date: 2026-07-15
Role: Reviewer
Status: reviewer_pass
Task: `TASK_361J_POINT_PROFILE_RANGE_EXPRESSION_AND_SIMPLIFIED_EDITOR`
Lane: `point-profile-range-expression-simplified-editor`

## Re-Gate Result

- B2R is closed. The exact V1 fixture dynamically captures every physical legacy
  category column and ordered row before production `init_db()`. After V2 upgrade it
  compares every original value, permits only the appended
  `point_expression=NULL`, checks the named V2 CHECK, and repeats the complete
  snapshot comparison after the idempotent second startup.
- The malformed V1 pre-DDL fail-closed regression remains active. B1 duplicate-id
  rejection remains pre-transaction and typed; B3 retains the compact accessible
  delete icon plus frontend/backend 256-category no-write limits.
- Direct confirm, expression canonicalization, legacy suggestion semantics, Cancel
  zero-write navigation, confirmed-only Matrix summary, and locked consumer boundaries
  remain unchanged by the tests-only B2R pass.

## Validation Performed

- Directly inspected the B2R test source and the unchanged B1/B3 implementation.
- Re-ran full Point Profile backend focus: `33 passed`.
- Re-ran frontend Profile plus Matrix focus: `5 files / 55 tests passed`.
- Re-ran candidate `py_compile`, `git diff --check`, and frontend production build:
  passed with only existing LF/CRLF notices and the existing Vite chunk-size warning.
- External TASK_361F evidence, board, and mixed CSS/setup/editor residuals remain
  excluded. No real database/file, staging, commit, or push action occurred.

## Decision

`reviewer_pass`

Recommended next role/action: QA gate for disposable SQLite/API and controlled desktop
plus 514px browser smoke. Do not route Integrator from this gate.

Blocking summary: none for Reviewer implementation re-gate.

---

# TASK_361J Reviewer Focused Implementation Re-Gate: QA B1 Keyboard Delete

Date: 2026-07-15
Role: Reviewer
Status: reviewer_pass
Task: `TASK_361J_POINT_PROFILE_RANGE_EXPRESSION_AND_SIMPLIFIED_EDITOR`
Lane: `point-profile-range-expression-simplified-editor`

## Re-Gate Result

- QA B1 is closed. The compact icon button remains a native `type="button"` with
  its pointer `onClick` path. Its narrow `onKeyDown` fallback handles only `Enter`
  and Space, checks the busy/disabled state, calls `preventDefault()` before invoking
  the existing `removeCategory(index)` action, and leaves all other keys untouched.
  That prevents Space scrolling and the native keyboard click from double-activating
  the same deletion.
- The new stateful `user-event` regression focuses the Signal row and asserts one
  `removeCategory(2)` call for Enter and for Space, then verifies that only that row
  disappears while HP remains. It therefore checks callback cardinality as well as
  visible row state. The pointer regression independently asserts one call for LP and
  preserves both adjacent rows. Disabled and empty states continue to have no delete
  action.
- The control retains its compact trash icon, `title="Delete row"`, and row-specific
  `aria-label`. The focused fix does not alter parser, migration/schema, API,
  lifecycle, Confirm/Cancel, the 256-category boundary, or the separately owned CSS
  hunks. No locked consumer, workbook, Fee, real-file, or real-database scope change
  was found.

## Validation Performed

- Directly inspected `ProjectPointProfileEditor.tsx` and its stateful focused test.
- Re-ran frontend Point Profile plus Matrix suite: `6 files / 59 tests passed`.
- Re-ran frontend production build: passed with only the established Vite chunk-size
  warning.
- Re-ran temporary Point Profile backend focus: `33 passed`; candidate `py_compile`
  passed.
- `git diff --check`, UTF-8 trailing-whitespace, line-count, and candidate scope
  checks passed apart from existing LF/CRLF notices. External board, TASK_361F,
  artifact, and user-owned style residuals remain excluded. No real database/file,
  staging, commit, or push action occurred.

## Decision

`reviewer_pass`

Recommended next role/action: QA re-smoke with the existing disposable controlled
browser fixture, including focused trash-button Enter/Space validation and the
remaining desktop plus 514px visual checks. Do not route Integrator from this gate.

Blocking summary: none for this focused Reviewer re-gate.
