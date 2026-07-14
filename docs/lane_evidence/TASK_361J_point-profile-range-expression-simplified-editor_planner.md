# TASK_361J Point Profile Range Expression And Simplified Editor Planner Evidence

Date: 2026-07-14

Role: Planner

Status: package scope reconciled / pending Integrator package re-gate.

## Current Phase / Why Allowed

Phase 11 controlled Matrix foundation. TASK_361I is complete/accepted in local commit
`9bf765a894b1970f4a764c3b7fe466ca61582a59`. Initial Discovery was requested as
planned-only; the later gate chain and explicit implementation approval are recorded
in Authorization Reconciliation below.

## Confirmed User Outcome

Contact measurement setup becomes a compact confirm-only table. Each row has exact
operator Prefix plus a persisted canonical Test points expression. Counts are derived;
there is no expanded preview, draft save, template, Use/label/count/More/order UI, or
top Back action. Cancel is zero-write; Confirm atomically creates confirmed authority;
Matrix remains confirmed-only.

## Repository Evidence

- Accepted TASK_361I uses three Point Profile tables and revision history.
- Category snapshots lack an exact point-set field and currently store only count,
  label, prefix, and included.
- Current lifecycle/UI requires Save draft before Confirm and hydrates editable draft.
- Current prefix fallback uppercases/derives abbreviations, contrary to the new rule.
- Current summary exposes a newer-draft warning.
- Dedicated fail-closed schema migration and focused disposable test boundaries exist.

## Planner Decision

- Create TASK_361J as one planned corrective/incremental lane.
- Add nullable `point_expression` to category snapshots. Null means legacy count-only;
  non-null means canonical explicit points. Keep derived persisted count for consumers.
- Freeze bounded positive-integer/range grammar, deterministic set normalization,
  preserved ASCII prefix, exact legacy conversion, direct confirm-only transaction,
  draft endpoint typed no-write compatibility, and compact accessible table UI.
- Keep all consumer, coverage, workbook, generic-output, Office, parser, LTR, and real
  data/file scope locked.

## Package Isolation Finding

The working tree already contained mixed styling/button changes in
`frontend/src/contact-measurement-plan.css`,
`ContactMeasurementSetupWorkspace.tsx`, and `ProjectPointProfileEditor.tsx`. They are
now resolved at package scope: the user explicitly assigned the button/action-group
CSS definitions required by current TASK_361J JSX and the corresponding editor class
references to TASK_361J. The removed Setup Workspace Back-button class is historical
overlap only. Integrator may hunk-stage the three files, but file-wide staging and
unrelated-hunk absorption remain forbidden.

## Definition Of Ready

Satisfied first for planned lane creation and Reviewer plan gate. User workflow,
schema and legacy compatibility, grammar/limits, lifecycle/API, UX/accessibility,
exact May Touch, locks, acceptance criteria, validation, merge gates, and mixed-hunk
isolation are explicit. Blocking questions: none. The later implementation
authorization is recorded below.

## Authorization Reconciliation

- Reviewer plan gate passed.
- The user approved Developer planning-first.
- Developer completed the docs-only planning-first pass.
- Reviewer implementation-readiness passed with no blocker.
- The user explicitly approved TASK_361J source-of-truth reconciliation and product
  implementation.
- Implementation authorization is limited to nullable canonical `point_expression`
  additive migration with exact V1/V2 fail-closed bootstrap; bounded parser and
  canonicalizer with derived count; explicit legacy count-only `1-N` conversion;
  preserved user prefix without automatic abbreviation or uppercase; direct atomic
  confirm-only command, Cancel zero-write, typed draft `410` no-write; typed API/DTO/
  client/model; compact Prefix/Test points/delete table with header Add row and only
  Cancel/Confirm; confirmed-only Matrix summary and count/prefix compatibility; and
  focused tests plus desktop/514px browser smoke.
- Matrix Step Test/Sample Type, coverage/override, Fee rules/pricing/UI/consumer
  migration, TASK_360B/TASK_361D workbook behavior, Generic Test Record/Report,
  parser/import, LTR/public drive, real databases/files, and external residuals remain
  locked.
- Developer implementation/fixes completed, Reviewer implementation re-gates passed,
  and QA re-smoke passed before the package-scope reconciliation.
- The user explicitly authorized the required `contact-measurement-button`, action-
  group, primary/secondary/compact/disabled/responsive CSS hunks and matching current
  editor references as TASK_361J package inputs. This does not authorize unrelated
  hunks or reintroduction of the removed Setup Workspace Back action.

## Evidence Paths

- `tasks/TASK_361J_POINT_PROFILE_RANGE_EXPRESSION_AND_SIMPLIFIED_EDITOR.md`
- `docs/task_361j_point_profile_range_expression_and_simplified_editor_plan.md`
- `docs/lane_evidence/TASK_361J_point-profile-range-expression-simplified-editor_planner.md`
- `docs/lane_evidence/TASK_361J_point-profile-range-expression-simplified-editor_reconciliation_planner.md`
- `docs/lane_evidence/TASK_361J_point-profile-range-expression-simplified-editor_package_scope_reconciliation_planner.md`
- `docs/task_board.md`

## Validation Performed

- Read AGENTS, Planner/parallel/orchestration/role protocols, PRODUCT/DESIGN, frontend
  architecture, TASK_361I accepted evidence/commit, current Point Profile backend/API/
  frontend/tests, and actual worktree residuals.
- This pass changes governance docs only. No schema, backend, frontend, API client,
  tests, real database/file, staging, commit, or push action occurred.

## Next Legal Role

Integrator package re-gate. No Developer rerun is required.
