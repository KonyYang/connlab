# TASK_361J Point Profile Range Expression And Simplified Editor

## Status

Complete/accepted locally after Integrator package re-gate. Developer implementation
and focused fixes, Reviewer implementation re-gates, QA re-smoke, and the
package-scope reconciliation passed. The accepted package includes only the explicit
TASK_361J button-style dependencies required for its self-contained editor; remote
push was intentionally not performed.

## Lane

`point-profile-range-expression-simplified-editor`

## Current Phase / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Upstream `TASK_361I_PROJECT_POINT_PROFILE_AUTHORITY_AND_UI` is complete/accepted in
  local commit `9bf765a894b1970f4a764c3b7fe466ca61582a59`.
- Current role: Integrator closeout completed after the Planner package-scope
  reconciliation.
- Authorization is limited to the exact Point Profile expression migration,
  confirm-only authority, typed API/client, simplified editor/summary, and focused
  validation boundaries below. No product file changes in this reconciliation pass.

## Goal

Replace the TASK_361I category/count/draft editor with a compact confirm-only Point
Profile table. Each row contains only the operator-entered Prefix and a deterministic
Test points expression. The backend persists the canonical expression and continues
to expose a derived `count_per_sample` compatibility field, so later consumers can
keep reading count and prefix without learning the point-list grammar in this lane.

## Frozen Product Contract

- The editor is a compact table with `Prefix`, `Test points`, and a delete action.
- The Add row command is placed in the action/delete table header.
- Prefix is operator-owned text. ConnLab does not translate `High Power` to `HP`,
  change case, or invent an abbreviation.
- Test points accepts page-number style expressions such as `1-4`, `1,2,3,4`, and
  `1-3,5,8-10`.
- The UI shows category row count and total points/sample only. It never renders an
  expanded point preview.
- Local editing performs no backend write. `Cancel` discards local state and returns
  to Matrix. `Confirm point profile` atomically writes and confirms a new authority
  revision, then returns to Matrix.
- Reopening setup loads the latest confirmed authority, never a saved draft.
- Matrix summary remains confirmed-only and shows persisted prefix, derived count,
  total, and revision. Local edits create no draft warning.
- Use, Category label, Count per sample, More, Up/Down, text Remove, templates, Save
  draft, Discard changes, and the top Back to Matrix action are removed from the UI.

## Expression Grammar And Canonical Form

- Source text maximum: `1024` characters.
- Tokens are comma-separated positive integers or ascending inclusive ranges
  `start-end`. Optional ASCII whitespace around tokens, commas, and hyphens is
  accepted and removed during normalization.
- Point indices are `1..9999`.
- Maximum distinct points per category: `4096`.
- Maximum categories per profile: `256`; maximum distinct-point total across the
  profile: `8192`.
- Empty input, empty tokens, trailing commas, zero, negative values, decimals,
  exponents, non-numeric text, and reverse ranges are invalid.
- Duplicate, overlapping, and out-of-order valid tokens are accepted, expanded into
  a bounded set, deduplicated, sorted, and compressed into maximal consecutive runs.
  Therefore `1,2,3,4` becomes `1-4`, `3,1-2,2` becomes `1-3`, and
  `1-3,3-5,8` becomes `1-5,8`.
- `count_per_sample` equals the size of the canonical distinct-point set. The backend
  derives it; clients cannot submit it as authority.
- Confirm requires at least one valid row and a positive profile total. The local
  empty state keeps one blank row; deleting the last row restores one blank row.

## Prefix Contract

- Stored/display prefix is the user's value with outer whitespace trimmed only; case
  is preserved.
- V1 accepts `1..64` ASCII characters matching `[A-Za-z][A-Za-z0-9_-]*` to remain
  compatible with existing workbook-oriented prefix usage.
- Uniqueness uses a trimmed case-insensitive normalized key within one revision, so
  `HP` and `hp` conflict. Duplicate prefix blocks Confirm with no write.
- Future materialization is exact `prefix + point integer`, for example persisted
  `HP` plus `1-3,5` can produce `HP1`, `HP2`, `HP3`, `HP5`.
- New confirmed snapshots keep the legacy compatibility fields by writing
  `record_prefix=prefix`, `label=prefix`, `normalized_prefix_key` and
  `normalized_label_key` from the same normalized key, and `included=true`.

## Additive Persistence And Migration Contract

- Keep the three TASK_361I authority tables and all revision/category history.
- Add exactly one nullable column to `contact_point_profile_categories`:
  `point_expression TEXT NULL`.
- Non-null values are canonical explicit point sets. `NULL` is the durable,
  unambiguous marker for a legacy count-only row. It must not be interpreted as a
  sparse set.
- Add a named semantic check equivalent to
  `point_expression IS NULL OR length(trim(point_expression)) > 0`.
- Fresh databases create the V2 shape. Existing exact TASK_361I V1 tables are the only
  legacy shape eligible for additive `ALTER TABLE ... ADD COLUMN` bootstrap.
- Migration preflights the entire V1 or V2 shape before DDL, uses one `BEGIN
  IMMEDIATE` transaction, applies only the missing column/check, validates the exact
  V2 shape before commit, and rolls back on failure.
- A partial, wrong-type, wrong-check, or otherwise incompatible shape fails closed as
  `authority_corrupt`. No table rebuild, row rewrite, data repair, or deletion is
  allowed.

## Legacy Compatibility

- Existing confirmed rows retain their stored prefix, label, count, included state,
  category identity, and revision history. Migration writes no fabricated expression.
- Read DTOs classify categories as `explicit` or `legacy_count_only`.
- For a positive included legacy count, the workspace may return a read-only
  contiguous suggestion: count `1` -> `1`; count `N>1` -> `1-N`. This is not
  authority until the operator explicitly confirms it.
- The editor may prefill that suggestion with concise legacy-conversion guidance.
  `Cancel` leaves the original row untouched; `Confirm` writes an explicit expression
  in a new confirmed revision. Legacy zero/excluded rows have no suggestion and must
  be assigned points or removed before Confirm.
- Existing saved drafts are retained as history and are not loaded as the new editing
  baseline. The workspace may expose `legacy_draft_present` diagnostics. First
  successful confirm-only command supersedes that draft and clears the editable
  pointer atomically; no draft data is physically deleted.

## Confirm-Only Lifecycle And API

- `GET /api/projects/{project_id}/contact-point-profile/workspace` remains the setup
  read boundary and returns latest confirmed authority plus expression/legacy status.
- `GET /api/projects/{project_id}/contact-point-profile/summary` remains confirmed-
  only and keeps count/prefix compatibility fields.
- `POST /api/projects/{project_id}/contact-point-profile/confirm` becomes a direct
  confirm-only command with actor, expected active confirmed revision id/fingerprint,
  and ordered `{category_id, prefix, point_expression}` rows.
- With no confirmed authority, both expected values must be null. Otherwise both must
  exactly match the active confirmed revision. First-confirm races and stale values
  return typed `409` with no partial write.
- One transaction validates and canonicalizes all rows, retains or issues monotonic
  project-owned `ppc-N` identities, supersedes any legacy editable revision, supersedes
  the prior confirmed revision, allocates `revision_sequence` as the maximum across all
  root revisions plus one, inserts the new confirmed snapshot with the prior confirmed
  revision as parent, updates the root, and commits.
- New fingerprints use an explicit `point-profile:v2` payload marker and include
  ordered category id, preserved prefix, canonical expression, derived count, and
  compatibility fields. Existing V1 fingerprints remain opaque persisted stale tokens
  and are never recomputed during migration.
- `PUT /draft` remains as a compatibility route but returns typed `410
  contact_point_profile_draft_disabled` and performs no write. The current typed client
  and UI remove draft-save calls.

## UX And Accessibility Contract

- Use a semantic table with stable columns for Prefix, Test points, and row action.
- The action header owns a compact Add row button. Row deletion is an icon button with
  tooltip/title and `aria-label` naming the row. No icon dependency is added.
- Inputs have explicit labels/header association, inline field errors, keyboard focus
  visibility, and stable disabled/loading states.
- At `514px`, columns remain within the viewport through fixed table layout, bounded
  action width, `min-width: 0`, and wrapping status text. No horizontal overflow or
  footer overlap is allowed.
- Footer actions are only `Cancel` and `Confirm point profile`. During Confirm both
  are disabled. Failure keeps local input; stale `409` blocks retry and tells the user
  to Cancel and reopen the latest confirmed profile.
- Confirm success refreshes authority and returns to Matrix; Cancel invokes existing
  route navigation without an API call.

## Authorized May Touch For Implementation

### Backend

- `backend/infrastructure/storage/models_contact_point_profile.py`
- `backend/infrastructure/storage/contact_point_profile_schema_migration.py`
- `backend/infrastructure/storage/repositories/contact_point_profile_authority.py`
- `backend/application/contact_point_profile_expression.py` (new)
- `backend/application/contact_point_profile_fingerprint.py`
- `backend/application/contact_point_profile_lifecycle_service.py`
- `backend/application/contact_point_profile_read_service.py`
- `backend/api/routes_contact_point_profile.py`
- focused Point Profile schema/expression/fingerprint/lifecycle/API tests

### Frontend

- `frontend/src/api/client.ts` only for typed Point Profile contract changes
- `frontend/src/features/contact-measurement-plan/projectPointProfileSelectors.ts`
- `frontend/src/features/contact-measurement-plan/projectPointProfileSelectors.test.ts`
- `frontend/src/features/contact-measurement-plan/projectPointProfileModelTypes.ts`
- `frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.ts`
- `frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.test.tsx`
- `frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.tsx`
- `frontend/src/features/contact-measurement-plan/ContactMeasurementSetupWorkspace.tsx`
- `frontend/src/features/contact-measurement-plan/ContactMeasurementSetupWorkspace.test.tsx`
- `frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.tsx`
- `frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.test.tsx`
- `frontend/src/contact-measurement-plan.css`
- focused Matrix summary/workspace regression tests only if required
- TASK_361J task/plan/evidence and `docs/task_board.md`

## Must Not Touch / Locked Paths

- No Matrix Step Test Type/Sample Type, Group/Step coverage, applicability, target
  override, or profile-to-target mapping.
- No Fee rules, pricing, UI, default-fill, or confirmed-consumer semantic migration.
- No TASK_360B/TASK_361D or LLCR/CR/IR/DWV workbook generation/artifact behavior.
- No Generic Test Record, Report, StepInstance, Matrix parser/import, LTR/public drive,
  XLSM/VBA/COM, real database, real workbook, or real project folder.
- No existing Measurement Plan target authority schema/lifecycle/commands.
- No dependency additions, Settings/release cleanup, `.agents/**`,
  `docs/project_management/**`, remote push, or unrelated TASK_360/361 residual.

## Worktree And Package Isolation

At planning time, mixed uncommitted hunks already existed in:

- `frontend/src/contact-measurement-plan.css`
- `frontend/src/features/contact-measurement-plan/ContactMeasurementSetupWorkspace.tsx`
- `frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.tsx`

The user has now explicitly assigned only the style dependencies required by the
implemented TASK_361J editor to this package:

- `contact-measurement-button`, `contact-measurement-action-group`, primary,
  secondary, compact, disabled, focus/hover, and responsive hunks in
  `frontend/src/contact-measurement-plan.css`;
- the corresponding button-class references used by the simplified
  `ProjectPointProfileEditor.tsx`; and
- the prior Setup Workspace Back-button class hunk only as historical overlap. The
  Back action was removed by TASK_361J, so no dead button or obsolete class reference
  is required in the package.

Integrator may hunk-stage the three mixed files to include these exact dependencies
and form a self-contained commit. File-wide staging or absorption of unrelated CSS,
workspace, or editor hunks remains forbidden. TASK_361F evidence, TASK_361H artifacts,
unrelated board changes, and every locked product area remain external.

## Acceptance Criteria

1. Setup loads latest confirmed rows, or one blank row when none is confirmed.
2. `HP` plus `1-4` derives `4`.
3. `LP` plus `1,2,3,4,5` reloads as `1-5`; cumulative total is `9`.
4. `Signal` plus `1-24` makes total `33`; `1-128` shows count `128` without rendering
   128 preview values.
5. `HP` plus `1-3,5` persists/reloads exactly as canonical `1-3,5` and can later
   materialize `HP1`, `HP2`, `HP3`, `HP5`.
6. Duplicate/overlap/out-of-order valid input normalizes deterministically. Invalid
   input, duplicate normalized prefix, or limits violation shows a clear error and
   Confirm performs no write.
7. Add row and delete icon work; Use, label/count inputs, More, ordering controls,
   templates, Save draft, Discard, and top Back are absent.
8. Cancel performs zero writes and returns to Matrix; reopening loads confirmed data.
9. Confirm atomically creates a confirmed revision and returns to Matrix; summary
   shows confirmed prefixes/counts/total/revision.
10. Local edits never create a draft warning or alter Matrix summary.
11. Legacy confirmed profiles remain readable; explicit contiguous conversion is
    reversible by revision history; migration is idempotent and rolls back on failure.
12. Desktop and `514px` use ConnLab table/button styling with no horizontal overflow,
    overlap, inaccessible icon action, or console error.

## Validation Gate

- Expression unit matrix for grammar, canonicalization, limits, prefix preservation,
  duplicate normalized prefix, and derived counts.
- Temporary SQLite fresh/V1/V2/malformed/partial/rollback/idempotency tests. Never open
  or copy `data/connlab.sqlite3` or an operator database.
- Lifecycle/API tests for first confirm, reconfirm, stale/first-confirm race, legacy
  conversion, old draft supersession, draft endpoint `410` no-write, and rollback.
- Frontend selector/model/component tests for local-only editing, Cancel no-call,
  confirm navigation, error/no-write, compact controls, confirmed-only summary, and
  no expanded preview.
- Browser smoke at desktop and `514px`, using disposable API/database fixtures only.
- Existing TASK_361I summary and TASK_361E/TASK_360B/TASK_361D count/prefix regression
  tests as read-only compatibility checks.
- Focused `py -m pytest`, `py -m py_compile`, focused `npm test`, `npm run build`,
  diff/trailing/line-count/whitelist/forbidden-scope/no-real-mutation scans.

## Merge Gate

Reviewer plan gate, user-approved Developer planning-first, Developer docs-only
planning-first, Reviewer implementation-readiness, explicit product/schema approval,
Developer implementation/fixes, Reviewer implementation re-gates, QA re-smoke,
package-scope reconciliation, and Integrator hunk-level package re-gate are complete.

## Definition Of Ready

Satisfied and accepted. User workflow, grammar, canonical form, limits, schema
compatibility, lifecycle, API, UX, May Touch, locks, validation, and exact
style-hunk ownership were verified in the isolated package.

## Next Legal Role

Orchestrator/User decision for any later separately approved lane. No Developer rerun
is required for this completed task.

## Blocking Questions

None.
