# TASK_361I Project Point Profile Authority And UI Plan

## Status

Developer implementation and bounded Reviewer fix passes are complete. The final
Reviewer implementation re-gate, QA disposable-data/browser gate, and Integrator
packaging/readiness gate passed. TASK_361I is complete/accepted for local
integration; remote push is outside this lane.

The authorization is limited to the three additive/non-destructive Point Profile
tables and fail-closed migration; draft/confirmed/superseded lifecycle; backend-owned
`ppc-N` identity, normalization, fingerprint, stale handling, and atomic save/confirm;
read-only legacy suggestion; typed profile API/DTO; profile-first setup UI;
confirmed-only Matrix summary; direct-route style ownership; and focused temporary
tests/browser smoke. All task locks remain controlling.

## Discovery Gate

### Current Phase / Active Task / Role / Why Allowed

- Phase: Phase 11 controlled Matrix foundation.
- TASK_361H is complete/accepted at `9e4c9e45`; no implementation lane is active.
- Role: Planner. The user approved a narrow first phase and requested planned-only
  task/plan/evidence rather than Developer execution.

### Confirmed By User

- V1 is project-wide Point Profile input, correct included-count total, draft/confirm,
  and confirmed Matrix summary only.
- Categories are completely freeform. HP/LP/Signal are optional examples.
- Setup is profile-first and must work with no eligible target or confirmed Matrix.
- Draft does not affect Matrix summary. Confirmation replaces active confirmed
  authority while retaining revision history.
- Coverage, Step applicability/overrides, Fee, and all workbook outputs are later lanes.

### Confirmed By Repository Evidence

- TASK_361H is accepted and provides target-level freeform families, normalization,
  stable `ff-*` identities, target PATCH validation, and confirmed consumer
  compatibility.
- `MeasurementPlanFamilySnapshotModel` requires a target snapshot FK. A target
  requires confirmed Matrix/group/row lineage, so it cannot persist a profile when no
  eligible target exists.
- `ContactMeasurementPlanLifecycleService.open_draft()` requires an active confirmed
  Matrix. Existing draft/confirm lifecycle is therefore target/Matrix-bound.
- Current setup begins with `Open measurement plan`, then target list/editor, impact
  controls, draft workbook panel, and target save/apply commands.
- Current Matrix summary shows target coverage, per-kind readings, Matrix/plan
  revisions, and specialized workbook controls.
- Current summary component imports the stylesheet, while the direct setup page does
  not own an explicit feature stylesheet import.

### Planner Decisions

- A first-class project authority is required. Frontend-only state or target copying
  would fail no-target persistence and authority separation.
- Use three additive Point Profile tables and separate lifecycle/read services. Do not
  add columns or semantics to the accepted six Measurement Plan authority tables.
- Keep profile category ids distinct from target family ids. TASK_361I does not map or
  apply profiles to targets.
- Reuse TASK_361H normalization behavior, but allocate profile ids as root-scoped
  `ppc-N` in the backend save transaction.
- `Discard changes` is local reset, avoiding a destructive draft-delete endpoint.
- Hide target coverage/workbook UI from the V1 profile-first surface; preserve all
  existing backend and consumer behavior for future lanes.

### Not Yet Confirmed

- None blocking. The optional read-only legacy-uniform suggestion may be omitted by
  Reviewer without changing the core V1 authority or acceptance path. It must never
  auto-import or auto-confirm.

## Data Ownership And Schema

The new `contact_point_profile_roots`, `contact_point_profile_revisions`, and
`contact_point_profile_categories` tables own project profile authority. Their exact
columns, FKs, state checks, partial unique indexes, normalized duplicate keys, and
included-count checks are frozen in the task.

No profile table has a Matrix FK. Revision history and root pointers provide
traceability. Existing target authority remains a separate downstream compatibility
source until a future coverage lane explicitly maps profile categories to targets.

### Developer Planning-First: Exact Additive SQLite Shape

The future implementation adds only these three physical tables. Names, scalar
types, and constraints are intentionally separate from the existing six
`measurement_plan_*` tables.

1. `contact_point_profile_roots`
   - `contact_point_profile_root_id VARCHAR(64) PRIMARY KEY NOT NULL`.
   - `project_id VARCHAR(64) NOT NULL UNIQUE REFERENCES projects(project_id)`.
   - `active_confirmed_revision_id VARCHAR(64) NULL REFERENCES
     contact_point_profile_revisions(contact_point_profile_revision_id)`.
   - `editable_revision_id VARCHAR(64) NULL REFERENCES
     contact_point_profile_revisions(contact_point_profile_revision_id)`.
   - `created_at VARCHAR(64) NOT NULL`, `updated_at VARCHAR(64) NOT NULL`.
   - The two revision pointers are nullable so first-draft creation and later
     confirmation can remain one transaction; they are never Matrix pointers.

2. `contact_point_profile_revisions`
   - `contact_point_profile_revision_id VARCHAR(64) PRIMARY KEY NOT NULL`.
   - `contact_point_profile_root_id VARCHAR(64) NOT NULL REFERENCES
     contact_point_profile_roots(contact_point_profile_root_id)`.
   - `revision_sequence INTEGER NOT NULL CHECK (revision_sequence > 0)` and
     `parent_revision_id VARCHAR(64) NULL REFERENCES
     contact_point_profile_revisions(contact_point_profile_revision_id)`.
   - `state VARCHAR(32) NOT NULL CHECK (state IN ('draft','confirmed','superseded'))`.
   - `revision_fingerprint VARCHAR(128) NOT NULL` and
     `bootstrap_provenance TEXT NULL UNIQUE`. Provenance is written only when a
     future operator explicitly saves a legacy suggestion; it never makes GET write.
   - `created_by VARCHAR(255) NOT NULL`, `created_at VARCHAR(64) NOT NULL`,
     `updated_at VARCHAR(64) NOT NULL`, `confirmed_by VARCHAR(255) NULL`,
     `confirmed_at VARCHAR(64) NULL`, `superseded_at VARCHAR(64) NULL`, and
     `superseded_reason TEXT NULL`.
   - `UNIQUE(contact_point_profile_root_id, revision_sequence)`;
     unique partial indexes `state = 'confirmed'` and `state = 'draft'`, each
     over `contact_point_profile_root_id`, enforce exactly zero or one active
     confirmed and editable revision without inventing an `editable` lifecycle state.

3. `contact_point_profile_categories`
   - `contact_point_profile_category_snapshot_id VARCHAR(64) PRIMARY KEY NOT NULL`.
   - `contact_point_profile_revision_id VARCHAR(64) NOT NULL REFERENCES
     contact_point_profile_revisions(contact_point_profile_revision_id)`.
   - `category_id VARCHAR(64) NOT NULL`, `category_ordinal INTEGER NOT NULL`,
     `label TEXT NOT NULL`, `normalized_label_key TEXT NOT NULL`,
     `count_per_sample INTEGER NOT NULL`, `record_prefix VARCHAR(64) NOT NULL`,
     `normalized_prefix_key VARCHAR(64) NOT NULL`, and `included BOOLEAN NOT NULL`.
   - `UNIQUE(contact_point_profile_revision_id, category_ordinal)` and
     `UNIQUE(contact_point_profile_revision_id, category_id)` preserve order and
     root-stable identity within each immutable confirmed snapshot.
   - `CHECK(category_ordinal >= 0 AND count_per_sample >= 0)` plus
     `CHECK(included = 0 OR count_per_sample > 0)` are the storage final guard.
   - Unique partial indexes over `(contact_point_profile_revision_id,
     normalized_label_key)` and `(contact_point_profile_revision_id,
     normalized_prefix_key)` where `included = 1` enforce the two normalized
     duplicate rules. Templates need no persisted vocabulary or special enum:
     selecting HP, LP, or Signal merely creates ordinary category values.

### Migration And Existing-Database Compatibility

Future implementation imports the new ORM module in `init_db()`, creates the
additive metadata, then runs a dedicated profile migration after the accepted
contact-measurement authority migration. The migration sequence is root, revision,
category, then the four profile partial indexes. SQLite permits the nullable
root-to-revision references during initial table creation; no existing table needs an
`ALTER`, rebuild, data repair, or data deletion.

For an existing database, the migration first opens one `BEGIN IMMEDIATE`
transaction and preflights every already-present Point Profile table before issuing
any DDL. The preflight compares required columns, SQLite affinities, nullability,
primary key, each FK local/referred column and action, normalized full CHECK
expressions, unique constraints, indexed column order, uniqueness flags, and exact
partial predicates. A same-name but semantically different table or index is
`authority_corrupt`; implementation must fail closed rather than guess a repair.
Compatible partial prior state may receive only its missing additive table/indexes,
then must be re-read and verified before commit. Lock/DDL failures roll back the
whole migration. A second clean startup is idempotent. Package rollback deliberately
leaves compatible additive tables unused by older code, without touching their rows.

No migration is authorized by this planning pass.

## Transaction Design

### Save Draft

1. Validate project and expected editable revision/fingerprint.
2. Normalize ordered rows and reject invalid/duplicate included categories.
3. Within one transaction, lock current root state, allocate never-reused `ppc-N`
   identities above historical high-water, and create or update one draft revision.
4. Replace only that draft revision's category snapshots, calculate total/fingerprint,
   update root/revision timestamps, flush, and commit.
5. Any concurrent draft, stale fingerprint, constraint failure, or storage error
   rolls back and returns an actionable typed error.

### Confirm

1. Repeat stale and category validation against the submitted current payload.
2. Require at least one included row and positive total.
3. In one transaction, save the submitted draft, supersede the prior active confirmed
   revision, confirm the editable revision, clear editable pointer, set active pointer,
   and commit.
4. Matrix and target authority are not read or written by this command.

### Lifecycle, Identity, And Validation Boundary

- Workspace GET is read-only. It does not create a root, draft, confirmed revision,
  legacy import, or Matrix target row. No root is therefore the valid no-target
  workflow, not an error.
- First draft save accepts `expected_revision_id = null` and
  `expected_revision_fingerprint = null` only when the transaction observes no
  editable revision. The first writer creates root plus draft; a concurrent first
  writer receives typed stale/conflict `409`, never a second editable revision.
- Later saves and confirms require the exact editable revision id and fingerprint.
  The lifecycle service owns SHA-256 canonicalization over root/revision identity,
  ordered rows, stored `ppc-N` ids, normalized keys, persisted prefixes, counts, and
  inclusion. A stale mismatch returns a typed `409` with a reload-safe message.
- `ppc-N` is server-issued inside the save transaction. New request rows carry no
  persisted id; existing rows must refer to an id already owned by the root. The
  repository calculates `max(historical persisted ppc number, submitted retained
  ppc number) + 1`. Removed ids never return, and reorder, label, count, prefix, and
  inclusion changes retain their retained id. Forged, duplicate, cross-root, or
  malformed ids fail without a write.
- Label keys use `unicodedata.normalize('NFKC', value).strip().casefold()`.
  Prefix resolution uses the accepted freeform rule once: NFKC, trim, uppercase,
  strip to ASCII `A-Z0-9`, accept length `1..64`; an empty or unparseable candidate
  resolves to the normalized label when valid, otherwise `C{ppc_number}`. The
  resolved value and its normalized key persist, so later rename/reorder/reload does
  not recompute it. Legacy target prefixes and ids are not normalized or rewritten.
- Empty or invalid included labels, non-integer/negative/overflow counts, included
  zero counts, duplicate included normalized labels/prefixes, and invalid identities
  are typed validation errors with row context and no write. A draft may contain
  only excluded valid rows; confirm requires an included positive total.
- Save mutates only the editable revision's snapshots. Confirm performs save,
  validation, old-confirmed supersession, new-confirmed promotion, root pointer
  update, and fingerprint persistence in one transaction. Any validation, stale,
  uniqueness, or storage error rolls back all lifecycle state.

## API And UI Flow

1. Setup deep link GETs profile workspace immediately.
2. No saved profile renders one local starter row; no technical open-plan gate.
3. Save draft creates/updates the editable revision. Refresh rehydrates it.
4. Confirm saves and promotes the editable revision atomically.
5. Matrix summary GETs confirmed-only profile summary. A newer draft changes only the
   warning flag, not displayed categories/total.
6. Target/impact/workbook controls are absent from the V1 setup/summary surface.

### Narrow DTO And API Contract

The future route module is project-id-only and follows the existing typed FastAPI
route to application-service boundary. It has no user-provided Matrix id, target key,
or file path.

- `GET /api/projects/{project_id}/contact-point-profile/workspace` returns
  `status`, `project_id`, `editable_revision`, `confirmed_revision`,
  `has_unconfirmed_draft`, ordered category rows, derived totals, diagnostics, and an
  optional read-only `legacy_uniform_suggestion`. Revision DTOs expose id, sequence,
  state, fingerprint, actor/time metadata, categories, and `points_per_sample`.
- `GET /api/projects/{project_id}/contact-point-profile/summary` returns only the
  active confirmed revision/categories/total, `has_unconfirmed_draft`, and concise
  diagnostics. It must return `not_started` without using Matrix target coverage,
  Matrix revision, LLCR/CR readings, or any workbook state.
- `PUT /api/projects/{project_id}/contact-point-profile/draft` accepts actor,
  expected editable id/fingerprint (both null only on first draft), and ordered
  editable category fields. It returns the reloaded workspace revision/fingerprint.
- `POST /api/projects/{project_id}/contact-point-profile/confirm` accepts the same
  expected id/fingerprint and submitted ordered category fields. It returns the
  promoted confirmed revision plus the reloaded workspace. The client reloads after
  every successful command and presents stale `409` as explicit reload/discard
  recovery, never automatic reapply.

The optional legacy suggestion service is a read-only adapter over the active
confirmed target authority. It may return only a canonically uniform included family
set across eligible non-override targets. It returns no suggestion for no Matrix, no
targets, divergent target families, an incomplete authority, or a missing active
confirmed plan. The frontend may copy a suggestion into unsaved local rows only after
an explicit user action. It may never create a profile revision, overwrite a saved
draft, alter target rows, or reverse-copy project categories to targets.

### File-Level Frontend Implementation Order

1. Add typed DTOs and four helpers in `frontend/src/api/client.ts`; it remains the
   sole fetch boundary.
2. Add `projectPointProfileSelectors.ts` for local canonical display validation,
   derived included total, deterministic ordinal movement, starter/template rows, and
   button eligibility. It cannot assign persisted `ppc-N` ids.
3. Add `useProjectPointProfileModel.ts` for workspace load, local draft rows, save,
   confirm, discard-to-last-loaded, status/error/stale state, and command reload.
   The hook owns async workflow state, not the page or display editor.
4. Add `ProjectPointProfileEditor.tsx`: one compact primary profile surface with
   category, include toggle, count, optional Prefix under a progressive More control,
   accessible ordering/removal, template menu, live `points / sample`, and the four
   commands. It uses standard inputs/buttons, inline validation, visible focus, and
   no modal-first or nested-card layout.
5. Retain the direct `/projects/{projectId}/contact-measurement-setup` route and
   `ProjectContactMeasurementSetupPage` ownership. The page imports the feature CSS
   directly, focuses its heading after load, returns to Matrix through the existing
   callback, and composes the new profile workspace instead of the target-first
   Measurement Plan editor. This preserves deep-link behavior while avoiding a new
   route family.
6. Narrow `ContactMeasurementSetupWorkspace.tsx` to the profile-first composition.
   It removes visible target lists, impact controls, draft-workbook panel, and target
   apply/save actions from this route, without changing their backend hooks or APIs.
7. Rework `ContactMeasurementPlanSummaryCard.tsx` and its narrow
   `MatrixEditorWorkspace.tsx` wiring to call the Point Profile summary only. The
   Matrix surface displays confirmed category rows, total, revision/state, a setup
   action, and a newer-draft warning. It hides target coverage, Matrix binding,
   LLCR/CR readings, and TASK_360B/361D workbook controls from this V1 summary; it
   must not change those consumers or their backend behavior.

The product register is a dense operational Windows workbench: status precedes
actions, semantic color is paired with text, controls have focus/disabled/error
states, and the layout remains a single unframed workflow surface rather than a grid
of decorative cards. At `514px`, rows switch to stable field stacks, action labels
wrap rather than shrink, and no bottom/dock control obscures Save or Confirm.

## File Plan

The task's exact May Touch list is controlling. New backend modules isolate profile
models, migration, repository, fingerprint, lifecycle, read projection, optional
legacy suggestion, and routes. Existing composition files are touched narrowly.
Frontend adds a profile editor/selectors/hook and rewires the existing setup route and
Matrix summary. Existing target/workbook services and hooks remain intact.

## Risks And Controls

- **Parallel authority risk:** profile and target authority are named separately;
  no automatic target copy or consumer fallback is allowed.
- **Migration risk:** additive tables only, temporary SQLite validation, no existing
  table ALTER/rebuild/data repair.
- **Draft leakage:** Matrix summary DTO contains confirmed categories only.
- **Stale overwrite:** exact revision/fingerprint checks and atomic transactions.
- **Identity drift:** backend root-scoped monotonic allocation and persisted prefix.
- **Legacy loss:** target families remain untouched; optional import is suggestion
  only and requires operator action.
- **UI regression:** feature-owned CSS import, focused route tests, desktop/narrow
  smoke, and existing Matrix/workbook regressions.
- **Existing-db collision:** semantic shape preflight before DDL, additive-only
  creation, and fail-closed `authority_corrupt` protect operator data.
- **Profile/target conflation:** no Point Profile DTO exposes target coverage or
  mutates target snapshots; the legacy bridge remains suggestion-only.
- **Package contamination:** do not stage accepted TASK_361B-H or external
  TASK_361F operational/board residual hunks. Keep each new backend module below the
  AGENTS hard limit and split validation/fingerprint concerns before either grows.

## Dependencies And Sequencing

- Serial prerequisite: TASK_361H complete/accepted.
- TASK_361I is one combined authority + minimal UI lane because the user-visible
  no-target workflow cannot be tested without both boundaries.
- Future target coverage/Step override, Fee, and workbook lanes are serially blocked
  on TASK_361I acceptance and require separate Discovery/approval.
- Backend schema/lifecycle and frontend local editor can be developed in parallel only
  after Reviewer readiness freezes the DTO and migration contract.

## Validation And Merge Gates

Future implementation validation is deliberately split by boundary:

- Temporary SQLite fresh and existing-compatible migration tests cover exact three
  table shapes, FKs/CHECKs/partial indexes, missing-table creation, idempotency,
  incompatible-shape fail-closed behavior, and transaction rollback. Fixtures never
  open, copy, or modify `data/connlab.sqlite3` or an operator database.
- Repository/lifecycle tests cover no-root read, first-save race, `ppc-N`
  high-water/no-reuse, canonical normalization, snapshot order, draft refresh,
  history, supersession, stale `409`, atomic confirm rollback, and no target writes.
- API tests cover no-target workspace, legacy-suggestion absence/presence without
  writes, validation no-write, workspace/summary draft separation, and confirmed-only
  Matrix summary. Existing target authority, consumer, workbook, and generic-record
  regressions stay read-only.
- Frontend selectors/model/component/route tests cover a starter blank row, optional
  template, arbitrary add/remove/reorder/inclusion, immediate `4 + 5 + 24 = 33`,
  draft reload, discard, stale recovery, confirmed-only summary, later-draft warning,
  focus/keyboard movement, and no target/workbook controls. API calls are mocked only
  through the typed client.
- A controlled disposable project browser smoke checks the direct route at desktop
  and 514px: create HP 4, LP 5, Signal 24, save, reload, confirm, open Matrix,
  create a later draft, and verify the summary remains 33 plus a draft warning. No
  generate/download/write-file action is invoked.
- Run focused `py -m pytest`, `py -m py_compile`, focused `npm test`, and
  `npm run build`, then `git diff --check`, UTF-8 trailing-whitespace, Python
  line-count, allowed-path/forbidden-content, and no-real-database/file scans.

No real DB/file or workbook generation is part of validation.

## Definition Of Ready

Satisfied for Developer implementation within the exact authorized boundary. Reviewer
plan gate, user-approved Developer planning-first, Developer docs-only planning-first,
Reviewer implementation-readiness, and explicit user approval for reconciliation plus
schema/product implementation are complete. Persistence, compatibility, lifecycle,
read boundary, UI ownership, tests, package isolation, and rollback constraints remain
controlling for implementation and later gates.

## Next Role

Developer implementation pass.
