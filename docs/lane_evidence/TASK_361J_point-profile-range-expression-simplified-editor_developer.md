# TASK_361J Point Profile Range Expression And Simplified Editor Developer Evidence

Date: 2026-07-15

Role: Developer

Status: ready_for_reviewer_re_gate. Developer implementation complete; no staging,
commit, push, real database, or real-file mutation occurred.

## Current Phase / Active Task / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Active task: `TASK_361J_POINT_PROFILE_RANGE_EXPRESSION_AND_SIMPLIFIED_EDITOR`.
- The Reviewer plan gate passed and the user explicitly authorized this Developer
  planning-first pass only. No implementation, schema migration, test implementation,
  dependency change, real database/file action, staging, commit, or push occurred.

## Repository Facts Used

- TASK_361I currently persists count-only category snapshots in three additive Point
  Profile authority tables. The dedicated SQLite migration already verifies existing
  table shape fail-closed and bootstraps missing V1 tables inside `BEGIN IMMEDIATE`.
- The current lifecycle is draft-first: `save_draft()` precedes `confirm()`, current
  command DTOs accept label/count/prefix/included, and the frontend hydrates the
  editable revision before confirmed authority.
- Current prefix canonicalization uppercases/derives fallbacks; TASK_361J must replace
  that behavior with operator-preserved prefix validation. Current Matrix summary is
  confirmed-only but exposes an unconfirmed-draft warning that the new flow removes.
- The actual worktree contains external styling/button residuals in
  `frontend/src/contact-measurement-plan.css`,
  `ContactMeasurementSetupWorkspace.tsx`, and `ProjectPointProfileEditor.tsx`. This
  planning pass did not modify, clean, or claim those hunks.

## Future Implementation Boundary

1. Extend category snapshots with nullable V2 `point_expression TEXT` plus its exact
   named nonblank-if-present check. Recognize exact V1/V2 physical shapes; V1 upgrade
   preflights before `BEGIN IMMEDIATE`, adds only the field/check, final-verifies in
   the same transaction, then commits. Any malformed, partial, verify, or lock case
   is `authority_corrupt` with rollback and no row mutation.
2. Put the bounded expression grammar in one pure application module. It returns
   canonical text, sorted points, and derived count; it owns all grammar/limit errors.
3. Keep legacy `NULL` expressions explicit. A positive legacy count may render one
   contiguous suggestion but is not persisted or treated as sparse authority until a
   new direct-confirm revision is successfully written.
4. Replace save-draft plus confirm with one direct confirmed revision command. Local
   browser state is the only editable state. Cancel is zero-write, stale is typed
   `409`, and the old draft endpoint returns typed `410` without repository access.
5. Preserve exact trimmed user prefix spelling/case. Validate only nonempty ASCII
   `[A-Za-z][A-Za-z0-9_-]*`, length 1..64, and revision-local case-insensitive
   uniqueness. No auto abbreviation, uppercase, or label fallback remains.
6. Future UI is a direct-route semantic table with Prefix, Test points, and delete
   action. Add row belongs in the action header. Footer actions are only Cancel and
   Confirm. The model owns local state/commands, components remain declarative, and
   Matrix summary reads confirmed prefix/count/total/revision only.

## Exact Future May Touch

- Point Profile model, dedicated schema migration, repository, new expression module,
  fingerprint/lifecycle/read services, Point Profile route/dependencies only as needed,
  and focused temporary SQLite/API tests.
- Typed Point Profile API-client DTO surface only.
- Point Profile selectors/model/editor/workspace/confirmed summary/feature CSS and
  focused frontend/Matrix regressions only.
- TASK_361J task/plan/evidence/board governance files.

## Locked Paths And Consumer Boundary

No TASK_361E Fee rules/pricing/UI, TASK_360B/TASK_361D workbook behavior, generic Test
Record/Report, Measurement Plan target authority, Matrix Step mapping, parser/import,
LTR/public-drive, Settings/release, dependency additions, real DB/files, or
`.agents/**`/`docs/project_management/**` changes. Fee and workbook consumers only
retain their existing derived count/prefix reads; they do not gain expression semantics
in this lane.

## Validation Plan

- Test-first parser, V1/V2 SQLite migration, lifecycle/API, client/model/component,
  Matrix summary, direct-route a11y, and 514px/desktop smoke coverage as enumerated
  in the task plan.
- Disposable SQLite and controlled browser fixtures only. Validate rollback, stale,
  zero-write Cancel, old draft `410`, no expanded point preview, and no consumer
  semantic drift.
- Run focused pytest/npm suites, `py_compile`, `npm run build`, diff/trailing/line,
  exact whitelist/forbidden-scope, no-real-mutation, and hunk-level package scans.

## Planning Validation

- Re-read AGENTS, task board, TASK_361J task/plan/Planner/Reviewer evidence, accepted
  TASK_361I model/migration/lifecycle/read/API/frontend code, frontend architecture,
  and `$impeccable` Product/DESIGN context for the product-register table surface.
- `git diff --check` passed for the tracked worktree with only existing LF/CRLF notices;
  UTF-8 trailing-whitespace scans found no matches in the TASK_361J plan/evidence.
  Targeted status confirms this pass added only the Developer evidence and refined the
  TASK_361J plan; existing TASK_361F evidence, board, CSS, setup-workspace, editor,
  and TASK_361H artifacts remain external residuals. No product path was modified.

## Next Legal Role

Reviewer implementation gate.

## Developer Implementation Pass (2026-07-15)

- Added `point_expression` as nullable `TEXT` category-snapshot authority with a named
  nonblank-if-present check. Existing V1 category tables are recognized and upgraded
  inside the dedicated bootstrap transaction before final V2 validation and commit.
- Added the pure bounded expression parser. It accepts positive integers and ascending
  ranges, deduplicates/orders/compresses point sets, returns the canonical expression
  plus derived count, and rejects empty, decimal, exponent, negative, reverse, and
  non-numeric forms.
- Added direct atomic confirmed-revision creation. It derives count/prefix compatibility
  fields from the submitted Prefix/Test-points rows, carries forward project-owned ids,
  supersedes prior authority, and fingerprints the V2 snapshot. The obsolete draft PUT
  boundary now returns typed `410 contact_point_profile_draft_disabled` without writes.
- Workspace reads expose explicit versus legacy count-only expressions and a read-only
  legacy contiguous suggestion. Matrix summary continues to read confirmed prefix/count/
  total/revision and no longer displays a local draft warning.
- Replaced the draft-first editor with the compact Prefix/Test-points/delete table.
  Add row is in the action header; local edits never call the API; footer actions are
  only Cancel and Confirm point profile. Confirm is one typed command and Cancel is
  route navigation only.
- Preserved user-owned button-style hunks in the mixed CSS/workspace/editor files and
  added TASK_361J table/row hunks without rollback or whole-file cleanup.

### Validation

- `py -m pytest tests/unit/test_contact_point_profile_expression.py
  tests/unit/test_contact_point_profile_lifecycle.py
  tests/unit/test_contact_point_profile_schema.py
  tests/integration/test_contact_point_profile_api.py -q`: `24 passed`.
- `npm test -- projectPointProfileSelectors useProjectPointProfileModel
  ContactMeasurementSetupWorkspace ContactMeasurementPlanSummaryCard
  MatrixEditorWorkspace --run`: `5 files / 52 tests passed`.
- Candidate backend `py_compile`: passed.
- `npm run build`: passed, with the existing Vite chunk-size warning only.
- `git diff --check` and trailing-whitespace scan: passed with existing LF/CRLF
  working-tree warnings only. New Python modules are below the hard 500-line limit;
  no locked-path diff hit was found.

Browser residual: no disposable browser harness was started in this pass. The 514px
and desktop manual smoke remains for Reviewer/QA; focused DOM tests and the production
build cover the compact table structure and accessibility names.

## Reviewer B1-B3 Bounded Fix Pass (2026-07-15)

Status: `ready_for_reviewer_re_gate`. This pass changed only approved TASK_361J
lifecycle validation, V1-to-V2 bootstrap regression coverage, compact editor/model
behavior, focused tests, and this evidence. No staging, commit, push, real database,
or real-file action occurred.

### B1: Retained Identity Validation

- `_direct_categories()` now rejects a duplicate supplied non-null `ppc-*` category
  id before opening the repository transaction. The route continues to map the domain
  validation failure to typed `422 contact_point_profile_validation`, rather than
  leaking a SQLite or SQLAlchemy integrity error.
- `tests/unit/test_contact_point_profile_lifecycle.py::test_direct_confirm_rejects_duplicate_retained_ids_without_new_revision`
  proves the active pointer and root/revision/category row counts are unchanged.
- `tests/integration/test_contact_point_profile_api.py::test_point_profile_direct_confirm_maps_duplicate_retained_identity_to_typed_validation`
  proves the typed API response. Both passed.

### B2: Exact Legacy V1 Upgrade

- `tests/unit/test_contact_point_profile_schema.py::test_exact_v1_category_table_upgrades_in_place_and_preserves_legacy_row`
  creates an exact V1 category table with named checks, unique constraints, FK and
  partial indexes, inserts a legacy row, then runs production `init_db()`. It proves
  additive `point_expression` upgrade, legacy field preservation, `NULL` expression,
  named V2 check recognition, and idempotent second startup.
- `tests/unit/test_contact_point_profile_schema.py::test_malformed_exact_v1_category_shape_fails_before_additive_upgrade`
  proves malformed V1 fails `authority_corrupt` before the column DDL, with no
  partial mutation. Both passed with disposable SQLite only.

### B3: Compact Delete And 256-Category Boundary

- The row action is now an accessible compact trash icon with a `title` and an
  `aria-label` containing its row prefix or ordinal; no text `Delete` button remains.
- Add row disables at 256; selector, model, lifecycle and API validation fail closed
  for 257 rows. The backend error is business-readable and the rejected command does
  not write another revision.
- Passed nodes:
  `tests/unit/test_contact_point_profile_lifecycle.py::test_direct_confirm_allows_256_categories_and_rejects_257_without_writes`,
  `frontend/src/features/contact-measurement-plan/projectPointProfileSelectors.test.ts`,
  `frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.test.tsx`,
  and `frontend/src/features/contact-measurement-plan/ContactMeasurementSetupWorkspace.test.tsx`.

### Fix-Pass Validation

- Focused backend Point Profile suite: `33 passed`.
- Focused frontend Point Profile plus Matrix regression suite: `4 files / 54 tests passed`.
- `py -m py_compile` for the changed backend lifecycle/parser/migration/route: passed.
- `npm run build`: passed; existing Vite chunk-size warning only.
- `git diff --check`: passed with existing LF/CRLF working-tree notices only.
- UTF-8 trailing-whitespace scan: clean. Checked Python files are 58-282 lines,
  under the 500-line hard limit. TASK_361J candidate and forbidden-scope scans are
  clean; existing external residuals remain excluded.

## Next Legal Role

Reviewer implementation re-gate.

## QA B1 Keyboard Delete Fix Pass (2026-07-15)

Status: `ready_for_reviewer_focused_re_gate`. The only product change is the compact
Point Profile delete button's keyboard activation guard plus its focused component
test. No parser, schema, API, lifecycle, Confirm, Cancel, or 256-category behavior
changed. No real database/file access, staging, commit, or push occurred.

- Inspected the live component boundary: each action is an enabled native
  `type="button"` containing only an `aria-hidden` icon; no nested interactive element
  or pointer-event override exists.
- Added a narrow `onKeyDown` fallback for only `Enter` and `Space`: it skips disabled
  buttons, calls `preventDefault()` to avoid Space scrolling/native double activation,
  and calls the same `removeCategory(index)` action once. Pointer `onClick` remains
  the native path.
- Added `frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.test.tsx`.
  It uses `@testing-library/user-event` against a stateful editor harness and proves
  focused `Delete point profile row Signal` removes exactly once for both Enter and
  Space, pointer click removes only its own row, and disabled/empty editor states do
  not remove rows.

### QA B1 Validation

- Exact editor node: `4 passed`.
- Focused Point Profile plus Matrix frontend suite: `6 files / 59 tests passed`.
- Focused backend Point Profile suite: `33 passed`; `py_compile` passed.
- `npm run build`: passed with the existing Vite chunk-size warning only.
- `git diff --check`, UTF-8 trailing-whitespace, line-count, and forbidden-scope
  scans passed apart from existing LF/CRLF notices. User-owned button-style hunks and
  external residuals remain untouched/excluded.

Browser residual: the controlled browser harness was not restarted in this Developer
pass. Reviewer focused re-gate should precede the requested QA re-smoke.

## Next Legal Role

Reviewer focused implementation re-gate.

## Reviewer B2R Tests-Only Fix Pass (2026-07-15)

Status: `ready_for_reviewer_re_gate`. No migration, lifecycle, API, frontend, or
other product logic changed in this pass. Only the focused disposable SQLite schema
test and this evidence were updated; no real database/file access, staging, commit,
or push occurred.

- `tests/unit/test_contact_point_profile_schema.py::test_exact_v1_category_table_upgrades_in_place_and_preserves_legacy_row`
  now captures the actual V1 category table column list and every persisted category
  row before production `init_db()`. It compares every retained V1 field after the
  additive V2 upgrade in deterministic row order, asserts the sole appended
  `point_expression` is `NULL`, retains the named V2 CHECK assertion, and repeats the
  full V2 snapshot comparison after a second `init_db()`.
- This dynamic snapshot covers all actual V1 columns, including snapshot and revision
  identities, category id/order, label, normalized label key, count, prefix,
  normalized prefix key, included, and any future V1 fixture column. It proves row
  count, identity, and order are unchanged rather than comparing a post-upgrade subset.
- `tests/unit/test_contact_point_profile_schema.py::test_malformed_exact_v1_category_shape_fails_before_additive_upgrade`
  remains in place and passed, proving malformed V1 fails closed before column DDL.

### B2R Validation

- Exact B2R nodes: `2 passed`.
- Full focused Point Profile backend suite: `33 passed`.
- `py -m py_compile` for Point Profile lifecycle/parser/migration/route: passed.
- `git diff --check`, UTF-8 trailing whitespace, and forbidden-scope scans: clean
  apart from existing LF/CRLF notices. Schema test file is 284 lines, below the
  500-line hard limit.

## Next Legal Role

Reviewer implementation re-gate.
