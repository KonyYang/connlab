# TASK_361I Project Point Profile Authority And UI

## Status

Developer implementation and bounded Reviewer fix passes are complete. The final
Reviewer implementation re-gate, QA disposable-data/browser gate, and Integrator
packaging/readiness gate passed. TASK_361I is complete/accepted for local
integration; remote push is outside this lane.

## Lane

`project-point-profile-authority-and-ui`

## Current Phase / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current role: Integrator closeout. Reviewer and QA gates have passed, so controlled
  local packaging is allowed; this task does not activate a follow-on lane.
- TASK_361H is complete/accepted in local commit `9e4c9e45`; remote push is outside
  this lane.
- The authorized implementation remains limited to the exact Point Profile schema,
  backend/API, profile-first UI, confirmed-only Matrix summary, and focused validation
  boundaries below. No product code is changed by this reconciliation pass.

## Goal

Add a first-class project Point Profile that operators can draft and confirm without
a confirmed Matrix or eligible LLCR/CR target. The setup workspace becomes
profile-first: operators define arbitrary included categories and counts, see the
included total, save a draft, and confirm a revision. Matrix shows only the active
confirmed profile plus a concise warning when a newer draft exists.

This lane does not apply profile categories to Matrix targets and does not generate
workbooks. Target coverage, Step applicability/overrides, Fee consumption, and output
generation remain separate future work.

## Product Contract

### Point Profile Authority

- Project Point Profile is an independent project-level authority. It is not stored
  by copying rows into `measurement_plan_target_snapshots`.
- One project may have one editable profile revision and one active confirmed profile
  revision. Confirm replaces the active pointer and retains prior confirmed revisions
  as `superseded` history.
- Draft changes never change Matrix summary. Matrix summary reads only the active
  confirmed profile.
- A subsequent draft is copied from the confirmed profile. It remains non-authority
  until explicitly confirmed.
- Profile revisions are independent of Matrix revision and `Confirm Matrix`.

### Category Contract

- Categories are arbitrary user-defined rows. High Power, Low Power, and Signal are
  optional templates only.
- Persisted fields: stable `category_id`, ordinal, label, positive integer
  `count_per_sample` when included, resolved record prefix, and included state.
- `points_per_sample` is derived as the sum of included category counts. It is never
  independently editable.
- New persisted ids use root-scoped monotonic `ppc-N`. Removed ids are never reused.
  Reorder, label, count, prefix, and included edits retain identity; remove plus add
  creates a new identity.
- Label normalization is Unicode NFKC + trim + casefold for duplicate detection.
  Prefix resolution reuses the accepted TASK_361H rule: NFKC, trim, uppercase,
  ASCII `A-Z0-9`, `1..64`; blank resolves once from label or `C{N}` and persists.
- Included normalized labels and prefixes must be unique within one profile revision.
  Invalid, duplicate, zero, negative, decimal, overflow, or empty included rows block
  save/confirm with row-level guidance and no write.
- Save draft may contain zero included categories if every persisted row is otherwise
  valid. Confirm requires at least one included category and a positive total.

### Optimistic Concurrency And Commands

- Workspace read returns editable and confirmed revisions together.
- Initial save supplies null expected revision/fingerprint. It succeeds only when no
  editable revision exists; a concurrent draft returns typed stale `409`.
- Subsequent save/confirm requires exact editable revision id and fingerprint.
- Fingerprint is SHA-256 over root/revision identity and the ordered canonical
  category payload.
- `Discard changes` is frontend-local reset to the last loaded/saved revision. It
  does not delete persisted draft or confirmed history and needs no destructive API.
- Confirm atomically validates/saves the submitted profile, supersedes the old active
  confirmed revision, confirms the editable revision, updates root pointers, and
  commits. Any validation/stale/storage failure rolls back the whole command.

## Additive Schema Contract

Implementation requires three new tables only; existing TASK_361A-H tables and data
remain unchanged.

1. `contact_point_profile_roots`
   - `contact_point_profile_root_id` primary key.
   - unique non-null `project_id` FK to `projects.project_id`.
   - nullable FKs `active_confirmed_revision_id` and `editable_revision_id`.
   - `created_at`, `updated_at`.
2. `contact_point_profile_revisions`
   - revision id, root FK, positive root-local sequence, nullable parent revision.
   - state limited to `draft`, `confirmed`, `superseded`.
   - fingerprint, optional bootstrap provenance, actor/timestamps, confirmation and
     supersession metadata.
   - unique root+sequence plus SQLite partial unique indexes for one confirmed and
     one editable revision per root.
3. `contact_point_profile_categories`
   - snapshot id, revision FK, root-stable `category_id`, ordinal, label,
     `normalized_label_key`, count, resolved prefix, `normalized_prefix_key`, included.
   - unique revision+ordinal and revision+category id.
   - partial unique revision+normalized label/prefix where included.
   - CHECK constraints for nonnegative ordinal/count and positive included count.

Migration is additive and idempotent. It creates missing new tables/indexes only in
temporary or operator databases during authorized implementation/startup. It must not
ALTER, rebuild, rewrite, repair, or delete the six accepted Measurement Plan authority
tables or their rows. A package rollback may leave unused additive tables intact;
older code ignores them.

## Legacy Compatibility And Bootstrap

- Existing TASK_361H target families remain readable and unchanged.
- GET is read-only and never silently creates or confirms a Point Profile.
- When no Point Profile root exists, read-only GET may expose
  `legacy_uniform_profile_available` if the active confirmed Measurement Plan has one
  canonically uniform included family set across eligible non-override targets. The
  operator must explicitly import that suggestion into local draft rows and then save;
  GET never writes, imports, or confirms it.
- Divergent targets, no targets, or no confirmed Measurement Plan produce no legacy
  suggestion. The operator starts with one local blank category row.
- No profile revision writes back to target snapshots in TASK_361I. Later coverage
  work must define explicit mapping and re-gate it.

## API And Read Model

Planned project-id-only endpoints:

- `GET /api/projects/{project_id}/contact-point-profile/workspace`
- `GET /api/projects/{project_id}/contact-point-profile/summary`
- `PUT /api/projects/{project_id}/contact-point-profile/draft`
- `POST /api/projects/{project_id}/contact-point-profile/confirm`

Workspace DTO includes `status`, project id, editable revision/categories/total,
confirmed revision/categories/total, `has_unconfirmed_draft`, optional legacy
suggestion, and diagnostics. Summary DTO includes confirmed revision/categories/total
and `has_unconfirmed_draft` only. It never exposes target coverage, Matrix revision,
LLCR/CR per-kind readings, or workbook actions.

## UX Contract

- The direct setup route immediately renders `Project point profile` as the first and
  primary section. No `Open measurement plan` placeholder is shown.
- Empty state has one editable starter row. Row controls: Use, Category, Count per
  sample, accessible move up/down, and remove. Prefix is under `More` and is not a
  primary burden.
- Commands: `Add category`, optional connector template, `Save draft`, `Confirm point
  profile`, and `Discard changes`.
- The included total updates immediately, e.g. `33 points / sample` for `4 + 5 + 24`.
- Draft and Confirmed authority are visually distinct with concise status, revision,
  saved/confirmed time, and stale/error feedback. No modal-first editor or nested cards.
- The setup feature entry imports its stylesheet directly so deep-link navigation has
  the same ConnLab controls, density, focus states, and narrow layout as in-app routing.
- Matrix `Contact Measurement Plan` summary shows only confirmed category rows, total,
  profile status/revision, setup action, and a concise newer-draft warning.
- Coverage `0/0`, LLCR/CR empty readings, Matrix revision, and Preview/Generate
  workbook controls are hidden from this summary in V1. Existing workbook backend and
  hooks are not changed.

## Authorized May Touch For Implementation

### Backend

- `backend/domain/contact_point_profile_models.py` (new)
- `backend/application/contact_point_profile_fingerprint.py` (new)
- `backend/application/contact_point_profile_lifecycle_service.py` (new)
- `backend/application/contact_point_profile_read_service.py` (new)
- `backend/application/contact_point_profile_legacy_suggestion_service.py` (new,
  read-only suggestion only)
- `backend/infrastructure/storage/models_contact_point_profile.py` (new)
- `backend/infrastructure/storage/contact_point_profile_schema_migration.py` (new)
- `backend/infrastructure/storage/repositories/contact_point_profile_authority.py` (new)
- `backend/infrastructure/storage/repositories/__init__.py`
- `backend/infrastructure/storage/database.py` only to register/run the additive
  profile migration
- `backend/api/routes_contact_point_profile.py` (new)
- `backend/api/dependencies.py` and `backend/api/main.py` only for narrow composition
- focused temporary-SQLite unit/integration/API tests

### Frontend

- `frontend/src/api/client.ts` only for typed Point Profile DTOs/helpers
- `frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.tsx` (new)
- `frontend/src/features/contact-measurement-plan/projectPointProfileSelectors.ts` (new)
- `frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.ts` (new)
- focused tests beside those files
- `frontend/src/features/contact-measurement-plan/ContactMeasurementSetupWorkspace.tsx`
- `frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.tsx`
- `frontend/src/pages/ProjectContactMeasurementSetupPage.tsx` for direct style loading
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` only for summary
  wiring and removal of visible workbook compatibility controls
- focused Matrix/route/workspace tests
- `frontend/src/contact-measurement-plan.css`
- TASK_361I task/plan/evidence and `docs/task_board.md`

## Must Not Touch / Locked Paths

- No existing Measurement Plan authority schema/model/migration/root/revision/target/
  family/impact/audit mutation or lifecycle-command semantic change.
- No profile-to-target copy, Matrix Step Test Type/Sample Type/applicability, Group
  sample quantity, coverage, target override, or Step mapping rule.
- No TASK_361E confirmed consumer/Fee source, pricing/rules/default-fill/manual/export/UI.
- No TASK_360B/TASK_361D workbook projection/generation/artifact/API/client behavior;
  only hide their Matrix/setup controls in this first-phase UI.
- No Generic Test Record, Report, StepInstance, Matrix parser/import, Basic
  Information, LTR/public drive, XLSM/VBA/COM, real database/workbook/folder, or
  unrelated TASK_360/361 residual.
- No Settings UI/config persistence, `.agents/**`, `docs/project_management/**`,
  destructive git operation, commit, or remote push.

## Acceptance Criteria

1. A new project or project with zero eligible targets can immediately edit a profile.
2. Included counts `4 + 5 + 24` display `33 points / sample` in real time.
3. Add/remove/disable/reorder updates total and order deterministically.
4. A valid saved draft survives reload.
5. Draft changes do not alter Matrix confirmed summary.
6. Confirm immediately updates Matrix summary with categories, total, and revision.
7. A later draft does not replace the prior confirmed summary before confirmation.
8. Duplicate/invalid categories and stale fingerprints produce row-level or typed
   `409` feedback with no partial write.
9. Setup deep link has ConnLab styling, focus behavior, and no narrow-width overflow.
10. No workbook, artifact, real file, target-family, Fee, or consumer mutation occurs.

## Validation Gate

- Temporary SQLite fresh/additive migration, constraints/indexes, idempotency,
  transaction rollback, history, stale `409`, and no-target API tests.
- Unit tests for canonical normalization, `ppc-N` monotonic identity, fingerprint,
  total, validation, and read-only legacy suggestion.
- Frontend selector/model/component/route tests for starter, arbitrary rows, template,
  total, reorder, local discard, draft/confirmed separation, stale recovery, and
  Matrix confirmed-only summary.
- Regression tests prove TASK_361B-H authority, TASK_361E consumer, TASK_360B/361D
  workbook behavior, generic Test Record, and Matrix import are unchanged.
- `py -m pytest` focused suites, `py -m py_compile`, focused `npm test`,
  `npm run build`, diff/trailing/line-count/forbidden-scope/no-real-file scans.
- Disposable project browser smoke at desktop and narrow width: deep-link setup,
  enter HP4/LP5/Signal24, save, reload, confirm, open Matrix, create a newer draft,
  and verify confirmed summary remains 33 with a draft warning.

## Merge Gate

Reviewer plan gate, user-approved Developer planning-first, Developer docs-only
planning-first, Reviewer implementation-readiness, and explicit schema/product
implementation approval are complete. Developer implementation, Reviewer
implementation re-gate, QA disposable-data/browser gate, and Integrator hunk-level
package isolation remain required. TASK_361I must not package workbook, Fee,
target-authority, parser, LTR, real-file, or external residual hunks.

## Definition Of Ready

Satisfied for Developer implementation within the explicit authorization above. User
workflow, independent authority, exact additive schema, API/data ownership,
normalization, stale/transaction semantics, compatibility, UX, May Touch, locks,
validation, and merge gates are explicit.

## Blocking Questions

None.
