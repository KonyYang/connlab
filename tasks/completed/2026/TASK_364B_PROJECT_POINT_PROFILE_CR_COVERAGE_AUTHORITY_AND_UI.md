# TASK_364B Project Point Profile CR Coverage Authority And UI

## Status

`complete / Integrator accepted`

Initial Developer implementation completed locally on 2026-07-18. User acceptance
then requested corrective R1: row-level CR checkboxes, no LLCR checkbox column, new
rows selected by default, and all-selected normalized to `follow_llcr`. R1 Developer
implementation, focused Reviewer acceptance, controlled QA, and explicit user
acceptance are complete. TASK_364C has now accepted the required backend/API authority
baseline at `b34f2c2cbcc3b27266b480d6ff76a604f06be452`. Product implementation
remains frozen; TASK_364B may now return only to a client-plus-consumer package re-gate.

## Current Phase / Active Task / Why This Lane Is Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- The board's current action is TASK_364B package-boundary review only; no new product
  implementation lane is activated.
- TASK_363C/D and TASK_365C are accepted. TASK_364B remains isolated from TASK_364A,
  TASK_365A/B, and all external residuals.
- The user has approved TASK_364B implementation. Product changes remain limited to
  its Point Profile backend/frontend paths and focused tests.

## Goal

Extend the project-level confirmed Point Profile so it owns both:

1. the complete LLCR category/point catalog; and
2. a project-wide CR coverage policy that follows LLCR by default and can be
   customized to any non-empty set of whole current categories.

The policy is confirmed atomically with the Point Profile revision. Matrix groups do
not own separate CR selections; their different sample quantities affect downstream
totals only and are outside this task.

## Frozen Product Contract

- LLCR continues to use every confirmed Point Profile category.
- CR defaults to `follow_llcr`. In this mode, it always uses every category in that
  confirmed revision and stores no redundant category list.
- CR selection is edited directly on each category row. The operator may select any
  non-empty set of complete current categories.
- Category names are project data. No category name, including HP, LP, High Power, or
  Low Power, is hard-coded, matched heuristically, or treated as a universal rule.
- Custom selection is bound to the same category rows and persisted stable
  `category_id` values. A category's prefix or point expression is never used as its
  identity.
- Every category selected means `follow_llcr`; cancelling any category means `custom`.
  Re-selecting every category returns to follow and writes no selection rows.
- A newly added category starts selected for CR, including while another category is
  excluded in custom mode.
- Custom mode with zero selected categories is invalid and Confirm performs no write.
- Confirmation remains one atomic Point Profile command. Cancel remains zero-write.

## Authority And Persistence Contract

Keep the existing root, revision, and category tables. Add one table only:

`contact_point_profile_cr_category_selections`

Each row contains a selection id, revision id, category id, and selection ordinal.
The `(revision_id, category_id)` pair references a category snapshot in the same
revision. Uniqueness of `(revision_id, category_id)` and
`(revision_id, selection_ordinal)` plus a non-negative ordinal check are mandatory.

Mode is derived without adding a mutable flag to old revision rows:

- no selection rows for the revision -> `follow_llcr`;
- one or more selection rows -> `custom`.

Because empty custom coverage is invalid, the representation is unambiguous. Existing
revisions naturally read as `follow_llcr`; no history row or old fingerprint is
rewritten.

The schema bootstrap must:

- create four Point Profile tables on a fresh temporary database;
- recognize exact existing three-table V2 Point Profile authority and add only the
  selection table;
- preflight all existing Point Profile shapes before DDL;
- create and validate in one `BEGIN IMMEDIATE` transaction;
- be idempotent and fail closed as `authority_corrupt` for malformed or partial
  selection-table shapes;
- never rebuild tables, repair business rows, or touch an operator database.

## Command, Fingerprint, And Read Contract

The direct confirm request adds:

- `cr_coverage_mode: "follow_llcr" | "custom"`; and
- a per-category `cr_selected` boolean on the same ordered category input.

The per-row boolean allows a newly added category, which has no server-issued id yet,
to be selected in the same atomic confirmation. After category ids are retained or
issued, the application service converts selected rows to stable category ids and
writes the ordered selection snapshot.

Validation rules:

- follow mode rejects active custom-selection flags;
- custom mode requires at least one selected category;
- selection cannot reference a missing, excluded, duplicated, or foreign category;
- the existing category, expression, prefix, total, and stale-CAS rules remain
  authoritative.

New confirmed revisions use `point-profile:v3` fingerprints containing the ordered
canonical category snapshot plus the explicit CR mode and ordered selected category
ids. Existing V1/V2 fingerprints remain opaque persisted stale tokens and are never
recomputed.

Revision workspace/summary DTOs add a typed `cr_coverage` object:

- `mode`;
- `selected_category_ids` in current category order;
- `points_per_sample` derived from the selected categories, or the LLCR total in
  follow mode.

The existing revision `points_per_sample` remains the LLCR compatibility total.

## UX Contract

Use the existing Point Profile editor card. Keep the top `LLCR` heading and derived
points/sample. The main table shows `Point category`, `Range`, `CR`, and the existing
action column. Do not show an LLCR checkbox column because every category belongs to
LLCR. Render one accessible CR checkbox on each row and remove the separate
`CR coverage`, `Customize CR`, and `Use same as LLCR` surface.

Confirm persists LLCR rows and CR coverage together. Busy, disabled, error,
focus-visible, keyboard, accessible-label, desktop, and 514px states must use the
existing ConnLab product vocabulary. The Matrix Point Profile summary shows CR as
either `Same as LLCR` or a custom category/points summary so the operator can verify
confirmed authority after returning from Setup.

## Authorized May Touch After Explicit Plan Approval

### Backend

- `backend/infrastructure/storage/models_contact_point_profile.py`
- `backend/infrastructure/storage/contact_point_profile_schema_migration.py`
- `backend/infrastructure/storage/repositories/contact_point_profile_authority.py`
- `backend/infrastructure/storage/database.py` only for the Point Profile table set
- `backend/application/contact_point_profile_fingerprint.py`
- `backend/application/contact_point_profile_lifecycle_service.py`
- `backend/application/contact_point_profile_read_service.py`
- `backend/api/routes_contact_point_profile.py`
- focused Point Profile schema/fingerprint/lifecycle/API tests

### Frontend

- `frontend/src/api/client.ts` only for typed Point Profile DTO/command changes
- `frontend/src/features/contact-measurement-plan/projectPointProfileSelectors.ts`
- `frontend/src/features/contact-measurement-plan/projectPointProfileSelectors.test.ts`
- `frontend/src/features/contact-measurement-plan/projectPointProfileModelTypes.ts`
- `frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.ts`
- `frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.test.tsx`
- `frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.tsx`
- `frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.test.tsx`
- `frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.tsx`
- `frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.test.tsx`
- `frontend/src/contact-measurement-plan.css`
- focused Setup workspace regression only if required by the changed model contract

### Governance

- this task, its plan/evidence, and minimal `docs/task_board.md` updates

## Must Not Touch / Locked Paths

- No project- or Matrix-group-specific duplicate CR selection.
- No Matrix Group sample-quantity multiplication or total-reading calculation.
- No Measurement Plan target authority schema/lifecycle/commands or target-specific
  `llcr` / `cr_specified_current` mappings.
- No Fee rules, pricing drafts, Units calculation, rebase, export, or UI.
- No confirmed LLCR/CR workbook, draft workbook, Generic Test Record, Report, or other
  consumer projection.
- No category-name heuristics or hard-coded HP/LP policy.
- No parser/import, LTR/public drive, Office/XLSM/VBA/COM, release/dist, dependency
  addition, real database, real workbook, or real project folder.
- No TASK_363B files or absorption of unrelated dirty-worktree changes.
- No `.agents/**`, `docs/project_management/**`, destructive git operation, commit,
  remote push, or automatic next-task activation.

## Acceptance Criteria

1. A legacy or new confirmed revision with no selection rows reads CR as
   `follow_llcr`, with CR points/sample equal to LLCR points/sample.
2. Custom mode can select any dynamic categories, including a newly added row, and
   persists their issued stable ids atomically with the revision.
3. All-selected normalizes to `follow_llcr`; a later new row starts selected for CR.
4. Renaming a selected category while retaining its id does not detach the selection.
5. Custom empty, follow-with-selection, foreign/duplicate selection, invalid Point
   Profile, and stale CAS all fail with no partial revision or selection write.
6. Re-selecting all rows writes follow mode with no selection rows and restores
   dynamic all-category CR coverage.
7. Workspace/summary/API/client expose typed mode, selected ids, LLCR total, and CR
   total without changing existing LLCR compatibility semantics.
8. Setup shows one compact row-level CR checkbox column and no separate CR section or
   LLCR checkbox column; Matrix summary keeps showing the confirmed CR policy.
9. Desktop and 514px layouts have no horizontal overflow, overlap, inaccessible
   checkbox/action, or console error.
10. Focused backend/frontend tests, py_compile, frontend build, diff/trailing/line and
    no-real-mutation scans pass.

## Validation Gate

- Temporary SQLite fresh/current-three-table/four-table/idempotent/malformed/partial/
  rollback/lock tests only.
- Fingerprint tests proving V3 mode/selection sensitivity and old fingerprint opacity.
- Lifecycle/API tests for follow, arbitrary custom subset, custom all, new category,
  rename, return-to-follow, invalid selection, stale/no-write, and rollback.
- Read-only regression for the existing confirmed Point Profile LLCR consumer.
- Frontend selector/hook/component tests for default follow, arbitrary dynamic category
  selection, new-row selected default, add/delete re-derivation, custom-empty
  validation, all-selected return to follow, command shape, summary compatibility,
  busy/error/accessibility, and no name heuristic.
- Focused `py -m pytest`, `py -m py_compile`, focused `npm test`, `npm run build`, and
  disposable desktop/514px browser smoke.

## Merge Gate

Planner Discovery and executable-plan submission -> explicit user plan approval ->
TDD implementation -> Task Review Checklist -> focused Reviewer/QA validation ->
board closeout. Stop after TASK_364B; do not implement downstream consumer totals.

## Definition Of Ready

R1 behavior, frontend-only file boundary, unchanged API/authority contract, derived
mode rule, tests, responsive smoke, exclusions, and validation are documented. R1
implementation approval is passed.

## Historical User-Accepted R1 Packaging Boundary

This section records the user-accepted R1 boundary, but its direct Integrator route is
superseded by the package-boundary reconciliation below. Earlier backend/API/client/
summary entries remain outside the R1 package itself.

The following exact product files are eligible for Integrator hunk-level packaging:

- `frontend/src/features/contact-measurement-plan/projectPointProfileSelectors.ts`
- `frontend/src/features/contact-measurement-plan/projectPointProfileSelectors.test.ts`
- `frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.ts`
- `frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.test.tsx`
- `frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.tsx`
- `frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.test.tsx`
- `frontend/src/contact-measurement-plan.css`, exact TASK_364B R1 hunks only

Eligible governance/evidence is limited to this task, the base and R1 plans, TASK_364B
Planner/Developer/Reviewer/QA/final-reconciliation evidence, the exact board hunks, and
`docs/lane_evidence/artifacts/TASK_364B_qa/controlled_514_native_checkbox.png`.
The PNG is packaged under the existing lane-evidence artifact policy because it is the
controlled 514px user-acceptance proof; no temporary harness/profile is eligible.

`ContactMeasurementPlanSummaryCard.tsx` and its test, backend/API DTO/summary,
Matrix group totals, Measurement Plan authority, Fee/workbook/generic outputs,
parser/LTR, TASK_363C/D/TASK_365A/B/C, and all unrelated hunks remain excluded. Mixed
files require hunk-level staging; wholesale staging is forbidden.

## Historical Package-Boundary Reconciliation (Superseded)

At the time of the original blocker, accepted HEAD
`2dac189d9b45eb68382af216e8144c6140869a71` contained none of the
`cr_coverage` / `cr_selected` / `follow_llcr` contract. The exact 11-addition
`frontend/src/api/client.ts` type hunk therefore cannot make R1 self-contained: its
matching authority/API/storage implementation remains an unaccepted 596-addition/
17-deletion candidate across eight backend files and four focused tests. The eighth
product hunk is the required one-line `database.py` profile-table exclusion. QA also
proved the client hunk itself cannot typecheck without R1 consumers/fixtures.

Path B is complete: TASK_364C accepted the backend/API/storage baseline at `b34f2c2c`.
The TASK_364B re-gate candidate is now exactly:

- the seven previously user-accepted R1 files/hunks: selectors + test, model hook +
  test, editor + test, and feature CSS;
- `frontend/src/api/client.ts`, exact 11 additions for the five CR coverage type/field
  contract elements; and
- `ContactMeasurementPlanSummaryCard.test.tsx`, only the one-line fixture addition of
  `cr_coverage`. Its other current 8-addition/2-deletion visual assertion hunks and
  `ContactMeasurementPlanSummaryCard.tsx` remain excluded.

Expected exact source numstat is 355 additions / 23 deletions before governance and the
controlled QA PNG. Reviewer must reproduce the hunk boundary and prove an isolated
frontend build/typecheck. No whole-file client or SummaryCard-test staging,
optional-field weakening, extra compatibility product code, or direct Integrator retry
is allowed.

## Next Legal Role

Integrator packaging/readiness for the exact nine-path TASK_364B boundary.

## Completion Evidence

- `docs/lane_evidence/TASK_364B_project-point-profile-cr-coverage-authority-and-ui_developer.md`
- Backend Point Profile validation: `46 passed`.
- R1 frontend Contact Measurement Plan/Matrix regression: `91 passed`.
- Frontend production build, Python compile, scoped diff, package scan, and desktop/
  514px disposable browser smoke passed.
