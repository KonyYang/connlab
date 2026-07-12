# TASK_361B Contact Measurement Plan Authority Backend Plan

## Status

Complete / Integrator accepted on 2026-07-12 after Developer implementation,
Reviewer final implementation re-gate, QA gate, and controlled Integrator
packaging/readiness. B3R2, B4R4/B4R5, B5R, and B6 are closed.

## Upstream Authority

TASK_361A is complete/accepted as the frozen contract basis. Matrix remains the
execution-map authority. A confirmed independent Measurement Plan revision owns
contact families, inclusion, target overrides, and review decisions. Drafts never
feed formal consumers.

## Exact Additive Schema Proposal

All ids are opaque `String(64)`, timestamps are UTC ISO-8601 `String(64)`, actor
fields are `String(255)`, fingerprints are lowercase SHA-256 strings, and enum-like
values are checked by application validation plus SQLite `CHECK` constraints.
Existing Matrix tables and `contact_plan_json` columns are not altered.

### `measurement_plan_roots`

- `measurement_plan_root_id` primary key
- `project_id` non-null foreign key to `projects.project_id`, unique
- `active_confirmed_revision_id` nullable revision id
- `editable_revision_id` nullable revision id
- `created_at`, `updated_at` non-null

Root pointers are updated in the same repository transaction as revision state
transitions. They never point to another Project's revision.

### `measurement_plan_revisions`

- `measurement_plan_revision_id` primary key
- `measurement_plan_root_id` non-null indexed foreign key
- `revision_sequence` positive integer
- `parent_revision_id` nullable self reference
- `state` in `draft`, `needs_review`, `confirmed`, `superseded`
- `revision_fingerprint` non-null
- `base_confirmed_matrix_id` non-null foreign key
- `base_matrix_revision` positive integer
- `matrix_binding_fingerprint` non-null
- `bootstrap_provenance` nullable unique text
- `created_by`, `created_at`, `updated_at` non-null
- `confirmed_by`, `confirmed_at`, `superseded_by_revision_id`, `superseded_at`,
  `superseded_reason` nullable

Constraints/indexes: unique `(measurement_plan_root_id, revision_sequence)`; one
partial unique index per root for `state = 'confirmed'`; one partial unique index per
root for `state IN ('draft', 'needs_review')`.

### `measurement_plan_target_snapshots`

- `measurement_plan_target_snapshot_id` primary key
- `measurement_plan_revision_id` non-null indexed foreign key
- `stable_target_key` non-null text using the frozen `cmp-target:v1` format
- `source_group_snapshot_id`, `source_row_snapshot_id` nullable lineage evidence
- `manual_group_anchor_id`, `manual_row_anchor_id` nullable plan-owned anchors
- `confirmed_matrix_id`, `confirmed_group_id`, `confirmed_row_id` non-null binding
  locators
- `matrix_revision`, `step_sequence` positive integers
- `step_suffix_note`, `group_label`, `test_item`, `contact_kind`,
  `sample_quantity_expression` non-null
- `method`, `condition`, `requirement` nullable display evidence
- `eligible`, `included`, `is_override` non-null booleans
- `coverage_state`, `exclusion_reason`, `impact_status`, `impact_reason` nullable
- `binding_evidence_fingerprint` non-null
- `readings_per_sample` non-negative integer

Constraints:

- unique `(measurement_plan_revision_id, stable_target_key)`;
- Group-axis XOR check: exactly one of a non-empty `source_group_snapshot_id` or a
  non-empty `manual_group_anchor_id` is present;
- Row-axis XOR check: exactly one of a non-empty `source_row_snapshot_id` or a
  non-empty `manual_row_anchor_id` is present;
- `stable_target_key` is non-empty, begins with `cmp-target:v1|`, and application
  validation must parse it, rebuild it from the persisted lineage/step/suffix
  columns, and require byte-for-byte canonical equality before insert/update;
- `contact_kind` is `llcr` or `cr_specified_current`.

Generated Matrix ids remain locators only and never replace the stable key. ORM and
repository validation duplicate the SQLite checks so malformed commands fail before
write with typed `422` details.

The migration emits the per-axis checks in this exact SQL shape (with the row column
names substituted for the second check):

```sql
CHECK (
  (source_group_snapshot_id IS NOT NULL
   AND length(trim(source_group_snapshot_id)) > 0
   AND manual_group_anchor_id IS NULL)
  OR
  (source_group_snapshot_id IS NULL
   AND manual_group_anchor_id IS NOT NULL
   AND length(trim(manual_group_anchor_id)) > 0)
)
```

### `measurement_plan_family_snapshots`

- `measurement_plan_family_snapshot_id` primary key
- `measurement_plan_target_snapshot_id` non-null indexed foreign key
- `family_id`, `family_ordinal`, `label`, `count_per_sample`, `record_label`,
  `record_prefix`, `included`, `is_custom` non-null

`family_ordinal` is non-negative. `count_per_sample` is a canonical non-negative
integer string; no decimal coercion or rounding is allowed. Constraints are unique
`(measurement_plan_target_snapshot_id, family_ordinal)` and
`(measurement_plan_target_snapshot_id, family_id)`. Target
`readings_per_sample` equals the sum of included positive family counts.

### `measurement_plan_impacts`

- `measurement_plan_impact_id` primary key
- `measurement_plan_root_id`, `editable_revision_id` non-null indexed foreign keys
- `stable_target_key` nullable for a newly discovered unmatched candidate
- `impact_subject_key` non-null canonical text
- `impact_identity_key` non-null canonical text
- `category` in `unchanged`, `text_refresh_compatible`,
  `sample_quantity_compatible`, `unrelated`, `structural_review_required`,
  `projection_review_required`
- `severity` in `info`, `review_required`
- `before_evidence_fingerprint`, `after_evidence_fingerprint` nullable
- `resolution_state` in `open`, `accepted`, `rebound`, `excluded`, `resolved`
- `selected_replacement_target_key`, `reason` nullable
- `created_at`, `resolved_at`, `resolved_by` nullable as appropriate

Nullable evidence is never part of dedupe identity. `impact_subject_key` is:

- the canonical `cmp-target:v1|...` key for an existing/deleted bound target; or
- for a new/unmatched Matrix candidate,
  `cmp-candidate:v1|matrix:<confirmed_matrix_id>|group:<confirmed_group_id>|row:<confirmed_row_id>|step:<positive integer>|suffix:<normalized suffix>`.

`impact_identity_key` is always non-null and is constructed exactly as:

```text
cmp-impact:v1|
category:<category>|
subject:<impact_subject_key>|
before:<fingerprint | none>|
after:<fingerprint | none>
```

The literal sentinel `none` replaces absence; empty strings are invalid. A unique
SQLite index on `(editable_revision_id, impact_identity_key)` is the sole refresh
dedupe constraint. Repeated classifier refresh and partial recovery perform an
upsert/read-verify by this key. Existing equal rows are reused; missing rows are
inserted; any same-key payload divergence returns `authority_corrupt` and rolls back
the refresh rather than inserting a duplicate or overwriting evidence.

### `measurement_plan_audits`

- `measurement_plan_audit_id` primary key
- `measurement_plan_root_id` non-null indexed foreign key
- `measurement_plan_revision_id`, `stable_target_key` nullable
- `action` in `bootstrap`, `save`, `impact_refresh`, `accept_suggestion`, `rebind`,
  `include`, `exclude`, `confirm`, `supersede`
- `actor`, `occurred_at` non-null
- `reason`, `before_fingerprint`, `after_fingerprint` nullable

Audits are append-only through repository APIs.

## Stable Identity

The identity service emits exactly:

```text
cmp-target:v1|
group:<source_group_snapshot_id | manual_group_anchor_id>|
row:<source_row_snapshot_id | manual_row_anchor_id>|
step:<positive integer>|
suffix:<trimmed normalized suffix>
```

Imported lineage uses immutable source snapshot ids. The first independent binding
allocates opaque plan-owned anchors for manual Group/Row lineage. Later revisions
must not auto-match manual anchors by label, order, generated id, group key, or test
text; an unmatched candidate requires explicit rebind in `needs_review`.

## Migration, Bootstrap, Compatibility, And Rollback

1. Register the new model module in `init_db()` and run a dedicated SQLite migration
   that creates only the six tables, foreign keys, checks, and indexes with
   `IF NOT EXISTS`/metadata inspection. No existing table is rebuilt or altered.
2. Run legacy bootstrap lazily inside the authority application service on first
   read/create for a Project, not as an unbounded startup write.
3. Read only the active confirmed Matrix Step quantities and typed
   `contact_plan_json`. Never read an open Matrix draft.
4. If no eligible valid legacy plan exists, create no empty plan revision. The
   compatibility read model reports `not_started`; invalid legacy JSON reports a
   readable `legacy_blocked` reason and performs no authority write.
5. For eligible legacy state, use provenance
   `cmp-bootstrap:v1|project:<project_id>|matrix:<confirmed_matrix_id>|legacy:<canonical_fingerprint>`.
   In one transaction per Project, create/reuse the root, confirmed revision,
   targets, families, audit, and root pointer. A unique provenance constraint plus
   deterministic canonical fingerprints makes interrupted/repeated runs idempotent.
6. A partially bootstrapped Project is resumed by provenance: existing canonical
   child rows are verified, missing rows are inserted, divergent rows block with a
   diagnostic; they are never silently replaced.
7. Legacy JSON is never rewritten or deleted. Until an independent root exists,
   the read-only compatibility adapter may expose the current legacy projection.
   Once a root exists, consumers of the new API must not fall back to legacy JSON.
8. Target rows are validated before partial recovery. If either lineage axis has
   both source and manual values, neither value, an empty value, or a stable key that
   does not exactly match its canonical columns, the Project is reported as
   `authority_corrupt`; the current transaction rolls back, no row is repaired or
   guessed, and no formal projection is returned. Once an independent root exists,
   malformed authority rows do not trigger silent legacy fallback. Recovery requires
   a separately reviewed maintenance action outside TASK_361B.
9. Rollback ownership is exactly `backend/shared/config.py` on the existing frozen
   `Settings` dataclass. TASK_361B may add
   `contact_measurement_plan_authority_enabled: bool = True`, loaded only from
   `CONNLAB_CONTACT_MEASUREMENT_PLAN_AUTHORITY_ENABLED` through a new private parser
   owned in the same module. Absent/blank means the default `true`; accepted true
   tokens are `1`, `true`, `yes`, `on`; accepted false tokens are `0`, `false`, `no`,
   `off`; any other non-blank token raises a configuration `ValueError` instead of
   silently choosing a mode. The existing `_bool_setting` and all LTR/settings
   parsing remain unchanged. There is no local-config key, database setting,
   Settings UI, settings API, LTR/public config, or runtime write endpoint.
10. `backend/api/dependencies.py` reads the already loaded `Settings` value and
    injects it into the authority resolver/lifecycle dependency. Routes and
    application services must not call `os.getenv` or load Settings themselves.
    Unit tests inject the boolean directly into the resolver/service; config tests
    use `monkeypatch.setenv` and `Settings.load()`.
11. When disabled, read operations select the existing read-only legacy adapter and
    independent write commands return a typed unavailable/disabled result. Neither
    legacy JSON nor additive authority tables/audits are changed or deleted. This is
    the complete rollback boundary; it is not an operator-facing product setting.

## Lifecycle Service

- `create_editable_revision(project_id, expected_matrix_binding_fingerprint)` creates
  one `draft`, or one `needs_review` when classifier output requires review.
- `save_revision(command)` requires `expected_revision_fingerprint` and updates only
  the editable revision in one transaction; mismatch returns typed `409` summary.
- `refresh_impacts(command)` requires the latest active Matrix id/binding fingerprint
  and recomputes from current authority; stale input returns `409`.
- `accept_compatible_suggestions(command)` accepts only text/sample compatible
  suggestions and cannot rebind manual candidates or overwrite explicit overrides.
- `rebind_target`, `set_target_inclusion`, and `replace_target_families` are explicit,
  audited draft-only commands.
- `confirm_revision(command)` requires revision id/fingerprint and current Matrix
  binding fingerprint, rejects unresolved review impacts, supersedes the prior
  confirmed revision, promotes the editable revision, and updates root pointers in
  one transaction.

Confirmed and superseded revisions are immutable. Drafts never enter formal
projection.

## Impact Classifier Interface

```python
class ContactMeasurementPlanImpactClassifier(Protocol):
    def classify(
        self,
        *,
        confirmed_plan: MeasurementPlanRevisionSnapshot,
        current_matrix: ConfirmedMatrixSnapshot,
    ) -> MeasurementPlanImpactResult: ...
```

The classifier is pure: it performs no repository writes. Its ordered result has
`matrix_binding_fingerprint`, compatible target projections, impact rows, and an
overall `unchanged`, `compatible_refresh`, or `needs_review` status. Category rules
are exactly those frozen in TASK_361A. Application service code alone persists the
result and creates/refreshes a review draft.

## Partial-Compatible Projection

`ContactMeasurementPlanProjectionService.get_effective_confirmed_projection()`
joins the root's active confirmed plan to the latest active confirmed Matrix by
stable target key and classifier result:

- unchanged/text-compatible/sample-compatible targets are returned;
- current Matrix display text and valid sample quantity are projected without
  mutating the confirmed plan snapshot;
- structural, invalid-quantity, new, deleted, and unmatched targets are omitted with
  target-level reasons;
- response status is `complete`, `partial_compatible`, `needs_review`, or
  `not_started`;
- no editable revision and no obsolete legacy JSON enters the formal projection
  after an independent root exists.

TASK_361B exposes this projection but does not migrate Fee or workbook consumers;
that ownership remains TASK_361E.

## Typed API Foundation

Future routes in `routes_contact_measurement_plan.py` remain thin and delegate to
application services:

- `GET /api/projects/{project_id}/contact-measurement-plan/summary`
- `GET /api/projects/{project_id}/contact-measurement-plan/workspace`
- `GET /api/projects/{project_id}/contact-measurement-plan/effective-projection`
- `POST /api/projects/{project_id}/contact-measurement-plan/revisions`
- `PUT /api/projects/{project_id}/contact-measurement-plan/revisions/{revision_id}`
- `POST .../revisions/{revision_id}/impacts/refresh`
- `POST .../revisions/{revision_id}/suggestions/accept-compatible`
- `POST .../revisions/{revision_id}/targets/rebind`
- `PATCH .../revisions/{revision_id}/targets`
- `POST .../revisions/{revision_id}/confirm`

Requests carry expected fingerprints where required. Responses use typed Pydantic
DTOs and business-readable `409`/`422` details. No Office, filesystem, Matrix write,
or frontend logic belongs in route bodies. Draft workbook endpoints are excluded.

## Authorized File-Level Implementation Plan

1. Add pure authority records and enums in
   `backend/domain/contact_measurement_plan_authority_models.py`.
2. Add exact ORM tables and additive migration in
   `models_contact_measurement_plan_authority.py` and
   `contact_measurement_plan_authority_schema_migration.py`; narrowly register them
   in `database.py`.
3. Add the one backend-only runtime flag in `backend/shared/config.py`, test it in
   `tests/unit/test_config.py`, and inject it only through
   `backend/api/dependencies.py`. Do not touch Settings UI/routes or local config.
4. Add repository transaction/state invariants in
   `repositories/contact_measurement_plan_authority.py`.
5. Add identity, bootstrap, classifier, lifecycle, and projection application
   services in the named TASK_361B modules.
6. Add typed routes and dependency/main wiring only after service tests pass.
7. Add focused unit/integration tests; do not touch frontend or existing consumers.

### TASK_361B Implementation Module Split Clarification

The following two application helpers are part of this lane's exact backend-only
module split, not downstream UI or consumer scope:

- `backend/application/contact_measurement_plan_revision_snapshot_helpers.py`:
  draft target/family snapshot copy, canonical replacement, and idempotent impact
  persistence only.
- `backend/application/contact_measurement_plan_revision_fingerprint.py`:
  deterministic editable-revision optimistic-concurrency fingerprint only.

Both remain below the Python hard limit and are covered by the same focused
temporary-SQLite lifecycle/API tests. No TASK_361C-E ownership is implied.

## Developer Planning-First Implementation Lockdown

### Exact SQLite Types, FKs, Checks, And Indexes

The six tables remain additive. `VARCHAR(64)` is used for opaque ids, `VARCHAR(128)`
for SHA-256/fingerprint values, `TEXT` for operator text and canonical keys, and
`VARCHAR(64)` for UTC timestamps. SQLite booleans are `BOOLEAN NOT NULL CHECK (value
IN (0, 1))`. All foreign keys use `ON DELETE RESTRICT`; history is never cascade
deleted.

1. `measurement_plan_roots`
   - `measurement_plan_root_id VARCHAR(64) PRIMARY KEY`
   - `project_id VARCHAR(64) NOT NULL REFERENCES projects(project_id)`, unique
   - `active_confirmed_revision_id VARCHAR(64) NULL REFERENCES measurement_plan_revisions(measurement_plan_revision_id)`
   - `editable_revision_id VARCHAR(64) NULL REFERENCES measurement_plan_revisions(measurement_plan_revision_id)`
   - `created_at VARCHAR(64) NOT NULL`, `updated_at VARCHAR(64) NOT NULL`
   - index `ix_measurement_plan_roots_project_id`; application transaction verifies
     each pointer belongs to this root because the circular root/revision relation
     cannot be expressed as a single SQLite row check.
2. `measurement_plan_revisions`
   - `measurement_plan_revision_id VARCHAR(64) PRIMARY KEY`
   - `measurement_plan_root_id VARCHAR(64) NOT NULL REFERENCES measurement_plan_roots(measurement_plan_root_id)`
   - `revision_sequence INTEGER NOT NULL CHECK (revision_sequence > 0)`
   - `parent_revision_id VARCHAR(64) NULL REFERENCES measurement_plan_revisions(measurement_plan_revision_id)`
   - `state VARCHAR(32) NOT NULL CHECK (state IN ('draft','needs_review','confirmed','superseded'))`
   - `revision_fingerprint VARCHAR(128) NOT NULL`, `base_confirmed_matrix_id VARCHAR(64) NOT NULL REFERENCES confirmed_matrix_versions(confirmed_matrix_id)`, `base_matrix_revision INTEGER NOT NULL CHECK (base_matrix_revision > 0)`, `matrix_binding_fingerprint VARCHAR(128) NOT NULL`
   - `bootstrap_provenance TEXT NULL`, actor/timestamp and confirmation/supersession columns already listed above
   - unique `(measurement_plan_root_id, revision_sequence)`; unique non-null `bootstrap_provenance`; indexes on `(measurement_plan_root_id, state)` and `base_confirmed_matrix_id`; partial unique indexes `WHERE state = 'confirmed'` and `WHERE state IN ('draft','needs_review')` per root.
3. `measurement_plan_target_snapshots`
   - Add exact types to the existing proposal: lineage/manual anchors and Matrix ids are `VARCHAR(64)`; `stable_target_key TEXT NOT NULL`; `step_sequence INTEGER NOT NULL CHECK (step_sequence > 0)`; `step_suffix_note VARCHAR(255) NOT NULL DEFAULT ''`; `matrix_revision INTEGER NOT NULL CHECK (matrix_revision > 0)`; display/source evidence is `TEXT NOT NULL` except method/condition/requirement; flags are checked booleans; `readings_per_sample INTEGER NOT NULL CHECK (readings_per_sample >= 0)`.
   - FKs: revision id, confirmed matrix version, confirmed group, and confirmed row. `contact_kind CHECK (contact_kind IN ('llcr','cr_specified_current'))`; `coverage_state CHECK (coverage_state IN ('included','excluded','manual_override'))`; `impact_status CHECK (impact_status IN ('unchanged','text_refresh_compatible','sample_quantity_compatible','structural_review_required','projection_review_required'))`.
   - The two source/manual XOR checks in the existing plan are mandatory. `stable_target_key` has `CHECK (length(trim(stable_target_key)) > 0 AND stable_target_key GLOB 'cmp-target:v1|*')`, plus canonical rebuild equality in the domain/repository layer. Unique `(measurement_plan_revision_id, stable_target_key)` and indexes `(measurement_plan_revision_id, impact_status)` and `(confirmed_matrix_id, confirmed_group_id, confirmed_row_id, step_sequence, step_suffix_note)` are required.
4. `measurement_plan_family_snapshots`
   - `measurement_plan_family_snapshot_id VARCHAR(64) PRIMARY KEY`, `measurement_plan_target_snapshot_id VARCHAR(64) NOT NULL REFERENCES measurement_plan_target_snapshots(measurement_plan_target_snapshot_id)`, `family_id VARCHAR(64) NOT NULL`, `family_ordinal INTEGER NOT NULL CHECK (family_ordinal >= 0)`, `label TEXT NOT NULL`, `count_per_sample INTEGER NOT NULL CHECK (count_per_sample >= 0)`, `record_label TEXT NOT NULL`, `record_prefix VARCHAR(64) NOT NULL`, `included BOOLEAN NOT NULL CHECK (included IN (0,1))`, `is_custom BOOLEAN NOT NULL CHECK (is_custom IN (0,1))`.
   - Unique `(measurement_plan_target_snapshot_id, family_ordinal)` and `(measurement_plan_target_snapshot_id, family_id)`; index on target snapshot id. Application validation requires nonblank labels/prefixes for included positive-count families and verifies target `readings_per_sample` against the sum before write.
5. `measurement_plan_impacts`
   - `measurement_plan_impact_id VARCHAR(64) PRIMARY KEY`, `measurement_plan_root_id VARCHAR(64) NOT NULL REFERENCES measurement_plan_roots(measurement_plan_root_id)`, `editable_revision_id VARCHAR(64) NOT NULL REFERENCES measurement_plan_revisions(measurement_plan_revision_id)`, `stable_target_key TEXT NULL`, `impact_subject_key TEXT NOT NULL`, `impact_identity_key TEXT NOT NULL`, `category VARCHAR(48) NOT NULL`, `severity VARCHAR(32) NOT NULL`, `before_evidence_fingerprint VARCHAR(128) NOT NULL`, `after_evidence_fingerprint VARCHAR(128) NOT NULL`, `before_evidence_json TEXT NOT NULL`, `after_evidence_json TEXT NOT NULL`, `resolution_state VARCHAR(32) NOT NULL`, `selected_replacement_target_key TEXT NULL`, `reason TEXT NULL`, `created_at VARCHAR(64) NOT NULL`, `resolved_at VARCHAR(64) NULL`, `resolved_by VARCHAR(255) NULL`.
   - Checks: nonblank `impact_subject_key` and `impact_identity_key`; prefixes `cmp-target:v1|` or `cmp-candidate:v1|` for subject and `cmp-impact:v1|` for identity; category, severity, and resolution-state sets exactly as named in the existing plan; evidence fingerprints must be `none` or nonblank lowercase SHA-256 values. Unique `(editable_revision_id, impact_identity_key)` is the only classifier refresh dedupe key; indexes `(measurement_plan_root_id, resolution_state)` and `(editable_revision_id, category)`.
6. `measurement_plan_audits`
   - `measurement_plan_audit_id VARCHAR(64) PRIMARY KEY`, `measurement_plan_root_id VARCHAR(64) NOT NULL REFERENCES measurement_plan_roots(measurement_plan_root_id)`, `measurement_plan_revision_id VARCHAR(64) NULL REFERENCES measurement_plan_revisions(measurement_plan_revision_id)`, `stable_target_key TEXT NULL`, `action VARCHAR(48) NOT NULL`, `actor VARCHAR(255) NOT NULL`, `occurred_at VARCHAR(64) NOT NULL`, `reason TEXT NULL`, `before_fingerprint VARCHAR(128) NULL`, `after_fingerprint VARCHAR(128) NULL`, `details_json TEXT NULL`.
   - `action` check is the frozen action set in this plan; indexes `(measurement_plan_root_id, occurred_at)` and `(measurement_plan_revision_id, occurred_at)`. Repository exposes append only and no update/delete API.

### Migration Sequence And Corruption Boundary

1. Import the new ORM model module in `init_db()`. `Base.metadata.create_all()` creates all six tables for new databases.
2. Run `migrate_contact_measurement_plan_authority_schema(engine)` in the existing database initialization sequence. In one `engine.begin()` transaction, enable/verify SQLite foreign keys, create roots, revisions, targets, families, impacts, and audits, then create partial/lookup indexes after their tables exist.
3. Use `PRAGMA table_info`, `foreign_key_list`, and `index_list` to read-verify existing tables before any recovery. Existing compatible objects are reused. Missing objects are created. A table or index of the same name with incompatible columns/constraints raises a readable migration error; it is never rebuilt or dropped in this lane.
4. The root-to-revision pointer FKs are declared when roots are created and are initially null; SQLite permits the referenced revision table to be created later in the same schema initialization. Runtime pointer ownership verification remains mandatory.
5. Bootstrap is not part of schema migration. It runs lazily per Project after schema success.

`impact_subject_key` is canonical `cmp-target:v1` for known targets and canonical `cmp-candidate:v1` for unmatched current Matrix candidates. `impact_identity_key` is rebuilt from category, subject, and non-null before/after fingerprint where absence is the literal `none`. Repository refresh uses `INSERT ... ON CONFLICT(editable_revision_id, impact_identity_key) DO NOTHING`, immediately reads the row, compares every persisted canonical payload field, and either reuses the equal row or raises `authority_corrupt`. It never uses nullable-UNIQUE behavior or `DO UPDATE` to overwrite evidence.

Target source/manual axes are rebuilt into `cmp-target:v1` before each insert and read. Any both/neither/empty XOR failure, key mismatch, noncanonical suffix, missing required family rows, or target/family readings mismatch is `authority_corrupt`: the transaction rolls back, the root remains present, the resolver returns a blocked result, and legacy fallback is prohibited. This is intentionally distinct from a legacy project with no root.

### Typed Backend API Contract

Routes remain in `backend/api/routes_contact_measurement_plan.py` with typed Pydantic DTOs defined in that module or a narrowly named DTO module. The read DTO family is `ContactMeasurementPlanSummaryResponse`, `ContactMeasurementPlanWorkspaceResponse`, `ContactMeasurementPlanImpactResponse`, and `EffectiveContactMeasurementPlanProjectionResponse`. Each includes `status`, `root_id`/`revision_id` only for internal client correlation, display-safe revision sequence, current Matrix id/revision, fingerprints only where commands must echo them, target summaries, diagnostics, and `legacy_mode`/`disabled` indicators.

Command DTOs are:

- `CreateContactMeasurementPlanRevisionRequest(expected_matrix_binding_fingerprint, actor)`;
- `SaveContactMeasurementPlanRevisionRequest(expected_revision_fingerprint, actor, common_profiles, target_edits)`;
- `RefreshContactMeasurementPlanImpactsRequest(expected_matrix_binding_fingerprint, actor)`;
- `AcceptCompatibleSuggestionsRequest(expected_revision_fingerprint, expected_matrix_binding_fingerprint, actor)`;
- `RebindContactMeasurementPlanTargetRequest(expected_revision_fingerprint, candidate_subject_key, replacement_target_key, actor, reason)`;
- `PatchContactMeasurementPlanTargetRequest(expected_revision_fingerprint, stable_target_key, included, exclusion_reason, family_override, actor)`;
- `ConfirmContactMeasurementPlanRevisionRequest(expected_revision_fingerprint, expected_matrix_binding_fingerprint, actor, reason)`.

Reads map `not_started`, `complete`, `partial_compatible`, `needs_review`, `legacy_blocked`, `authority_corrupt`, and `disabled` to typed responses. Writes return `503`/business code `contact_measurement_plan_authority_disabled` when disabled, `409` for stale fingerprints, and `422` for invalid command/identity/family data. Routes never load Settings or environment values directly, mutate Matrix authority, invoke Office, or fall back to legacy after a root exists.

### Config Injection And Adapter Decision

`Settings.contact_measurement_plan_authority_enabled` is the only allowed flag. It defaults to `True` and is loaded solely from `CONNLAB_CONTACT_MEASUREMENT_PLAN_AUTHORITY_ENABLED`; absent or blank means true, `1/true/yes/on` and `0/false/no/off` are accepted case-insensitively, and every other nonblank token raises `ValueError`. A task-local private parser is required; existing `_bool_setting` and LTR/local-config semantics remain untouched.

`backend/api/dependencies.py` owns the single composition point: it passes the loaded boolean into the contact-plan resolver/lifecycle service constructor. Domain/application modules accept the boolean or adapter protocol by injection, never call `Settings.load()` or `os.getenv`. Disabled reads use the read-only legacy Matrix `contact_plan_json` adapter only until a root exists; disabled writes are blocked before repository mutation. The flag is not surfaced through Settings UI, settings APIs, local TOML, database rows, or LTR configuration.

### Module Split And Exact Future Package

Keep each new Python module below the AGENTS 500-line hard limit:

- `contact_measurement_plan_authority_models.py`: records/enums/value objects only.
- `contact_measurement_plan_identity.py`: target/candidate/impact canonical builders and parsers only.
- `contact_measurement_plan_impact_classifier.py`: pure Matrix-versus-plan comparison only.
- `contact_measurement_plan_bootstrap_service.py`: lazy legacy conversion/recovery only.
- `contact_measurement_plan_lifecycle_service.py`: revision commands and transactions only.
- `contact_measurement_plan_projection_service.py`: effective/disabled/legacy read adapter only.
- `contact_measurement_plan_revision_fingerprint.py`: deterministic
  optimistic-concurrency fingerprint over editable authority target/family snapshots
  only; current implementation is 46 lines.
- `contact_measurement_plan_revision_snapshot_helpers.py`: lifecycle-internal target
  and family snapshot copy, canonical target replacement, and idempotent impact
  persistence only; current implementation is 193 lines.
- storage model, migration, and repository modules remain separate; the API route remains thin.

The exact Authorized May Touch includes both revision helper paths above. They are
module-size decomposition inside TASK_361B identity/classifier/lifecycle authority,
not a new feature boundary. Future implementation may additionally add only focused
test files named for these modules and
`tests/integration/test_contact_measurement_plan_api.py`; it must not amend existing
Matrix revision/session services just to inject the new lifecycle.
`backend/shared/config.py`, `backend/api/dependencies.py`, `backend/api/main.py`, and
the narrow database registration paths are allowed only as specified above. All
frontend, client, consumer, workbook, parser/import, LTR/public-drive, generic Test
Record, StepInstance, Report, release/settings UI, and external parser residuals
remain locked.

## Validation Gate

- Migration/repository: fresh and existing temporary SQLite, additive tables/indexes,
  revision constraints, per-axis XOR checks, canonical stable-key equality, malformed
  both/neither/empty lineage rejection, immutable history, transaction rollback, no
  legacy changes.
- Bootstrap: no-legacy, valid eligible legacy, invalid JSON, rerun, interrupted
  partial state, malformed target partial state, divergent partial state, provenance
  uniqueness, rollback adapter.
- Identity/classifier: imported continuity, manual-anchor review, each frozen impact
  category, repeated unmatched-candidate refresh dedupe, `none` sentinel stability,
  same-key divergence blocking, deterministic ordering/fingerprints, invalid sample
  quantity.
- Lifecycle: one editable/confirmed revision, stale `409`, audit records, explicit
  rebind/override, confirm/supersede atomicity.
- Projection/API: complete/partial/not-started responses, omission diagnostics,
  no draft leakage, no post-root legacy fallback, thin typed routes.
- Config/rollback: default enabled, strict environment true/false parsing, explicit
  dependency injection, invalid-token startup failure, disabled read-only legacy
  selection, disabled write blocker, no table/JSON mutation, and no Settings
  UI/API/local-config surface.
- Commands: focused `py -m pytest`, Python compile checks, `git diff --check`, trailing
  whitespace, forbidden frontend/consumer/real-file scans.

## Merge Gate And Package Isolation

The accepted package includes only TASK_361B backend foundation files, focused
tests, TASK_361A/B source-of-truth documents/evidence, and precise
`docs/task_board.md` closeout. TASK_361C UI, TASK_361D workbook, TASK_361E
consumer changes, parser residuals, TASK_360Q/R/S, release/settings residuals,
real files, `.agents/**`, `docs/project_management/**`, and other unrelated
residuals are excluded. Planning/readiness/user authorization, Developer,
Reviewer implementation, QA, and Integrator gates are complete.

## Dependencies And Parallelism

1. TASK_361A: complete/accepted contract basis.
2. TASK_361B: complete/accepted backend authority foundation.
3. TASK_361C: dedicated setup workspace, only after TASK_361B acceptance.
4. TASK_361D: draft workbook output, only after TASK_361B acceptance; may proceed in
   controlled parallel with TASK_361C after separate gates and shared-route ownership
   declaration.
5. TASK_361E: confirmed Fee/specialized-workbook consumer migration, serial last and
   re-gated after TASK_361C/D integration facts.

## Definition Of Ready

Complete. The accepted scope remains limited to the exact additive
schema/migration/backend/API/config/test package, including the two reconciled
internal revision helpers. Later TASK_361C/D/E lanes must not reuse this closeout
as approval for UI, workbook, Fee/consumer, or other future-scope work.
