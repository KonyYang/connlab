# Fee Default-Fill Dependent Field Corrections Plan

Status: complete / Integrator accepted pending controlled local package closeout
Date: 2026-07-24
Task: `FEE_DEFAULT_FILL_DEPENDENT_FIELD_CORRECTIONS`
Lane: `fee-default-fill-dependent-field-corrections`

This lane is backend-only and deliberately excludes pricing-draft API/frontend hydration. Child 1 `FEE_RULE_RESOLUTION_MATRIX_BASE_FEE_POLICY` is complete/accepted at local commit `c5d91c36c5e1d54885fc0a3b406c92ff9aa0cb6b`, verified as a HEAD ancestor; its general Base Fee fallback, manual/explicit accepted rule-specific precedence, single/multi-Group equivalence, and metadata contract are now the accepted baseline for Child 2.

The final Reviewer re-gate and QA gate passed on 2026-07-24. The only
frontend content in this lane is the approved type-only DTO and non-visual
Matrix payload preservation needed by the typed backend contract; no Fee UI
or visual behavior is included. Child 3 and the parent umbrella remain
blocked, and remote push is not authorized.

Child 2's Base Fee dependency is released, and User/Orchestrator approved Option 1: additive typed duration authority data contract/producer/persistence/API/model boundary. Reviewer plan/dependency-release and scope/implementation-readiness re-gates passed, Developer completed implementation, and final Reviewer and QA gates passed within the exact frozen scope.

## Candidate Field Ownership

- Unit Price: may be manual-required or automatic per rule/default-fill only.
- Units: may be automatic only when source data is explicit and the field is not manual-required.
- Base Fee: Child 1 owns final value and metadata for all lines: manual first, explicit accepted rule-specific second, otherwise automatic default `0`. Child 2 only reads the final accepted Child 1 outcome; it must not write, recalculate, classify, or re-attest Base Fee and must not use `matrix_group_count` as a Base Fee trigger.
- Testing Fee: derived, never independent operator input when upstream fields are incomplete. Missing/invalid Child 2 dependent fields leave Units and Testing Fee unset/Pending/review-required with typed diagnostics and do not write Base Fee.
- Discount: untouched.

## Explicit Hour Authority

Child 2 accepts explicit hour authority only from structured/typed duration authority produced and persisted through the Matrix import/edit/confirmation chain. Fee draft may consume only confirmed owning-row authority from the same single authority build.

Minimum data contract:

- `duration_value`;
- `duration_unit`;
- `normalized_hours`;
- owning draft/confirmed group and row identity;
- step `sequence` and `suffix_note` when applicable;
- source identity (`source_import_id`, `source_snapshot_id`, `source_row_snapshot_id`, and source field/path);
- revision/fingerprint/lineage binding;
- typed diagnostic/status.

Valid authority must be a single positive finite numeric duration with an hour-compatible unit normalized to hours. Supported units are `hour`, `hours`, `hr`, `hrs`, `day`, and `days`; days convert to hours by multiplying by `24`.

Invalid authority includes zero, negative numbers, NaN, Infinity, non-numeric values, empty values, unsupported units, multiple divergent duration facts, conflicting duration facts, missing lineage/fingerprint, stale lineage/fingerprint, wrong row/group source, and any source not bound to the owning Fee row.

Forbidden inference sources: arbitrary free text, `condition`, `requirement`, `day_expression`, another row or Group, readings counts, Point Profile, legacy Matrix fallback, legacy Step quantity, LLCR/CR authority, and stale saved draft values.

Approved calculation for `Long-term high temperature zone load`: Unit Price `15`, Unit Type `per hour`, Units equal normalized explicit hours, Testing Fee derived from Unit Price, Units, accepted Child 1 final Base Fee, and discount. Missing/invalid hours produce typed review/no-write for Units and Testing Fee; manual fields are never overwritten.

Rejected rows `Long-term temperature cycle with load` and `Long-term damp heat` remain no-rule/manual-review. Plain `CONTACT RESISTANCE` remains no-LLCR fallback.

## B3-B5 Discovery And Re-Scope

Read-only code discovery found no existing typed duration authority in the currently allowed Child 2 boundary:

- `FeeDefaultFillContext` currently has text fields, sample quantity, step tokens/quantities, and CR authority only.
- `ConfirmedMatrixFeeDraftService._calculate_line()` builds the context directly from `ConfirmedMatrixRow` text fields.
- Current duration defaults scan combined text, which the revised contract forbids as an authority source.
- TASK_363D's single authority build and V2 attestation can bind automatic defaults and row safety, but they do not create row-level duration value/unit facts by themselves.

Reviewer B4 required tracing the true upstream before treating helper/context transport as enough. Planner rechecked:

- `backend/domain/source_matrix_models.py` has Source Matrix row snapshots for text fields only: `test_item`, `source_section`, `method`, `condition`, and `requirement`.
- `backend/domain/project_matrix_draft_models.py` and `backend/domain/confirmed_matrix_authority_models.py` persist Matrix rows with `condition`, `requirement`, and `day_expression`, but no typed duration value/unit/source identity/lineage.
- `backend/api/routes_project_test_plan_matrix_edit.py` accepts `duration_value`, `duration_unit`, `estimated_duration_hours`, and related compatibility fields, but those are not carried through Source Matrix snapshots or Confirmed Matrix row authority.
- `backend/application/source_matrix_import_builder.py` stores imported row condition/requirement text and group tokens; it does not persist typed duration facts.
- Measurement Plan/contact authorities and Point Profile authorities do not represent temperature duration.

User/Orchestrator then approved Option 1. Current re-scope freezes an additive typed duration authority contract and keeps all free-text/legacy fallback paths forbidden. Confirm Matrix remains the publication boundary; editable draft authority is not consumed by Fee until confirmed. Legacy confirmed rows without typed duration authority produce typed manual-review/no-write for affected Units and Testing Fee.

Reviewer B5 requires an exact mechanical split before any future transport hunk. Current checked-out line count is:

- `backend/application/confirmed_matrix_fee_draft_service.py` = `479` blank-inclusive UTF-8 physical lines by `(Get-Content <path> -Encoding UTF8).Count`; prior `451` was the superseded non-blank `Measure-Object -Line` count.

Mandatory behavior-preserving split:

- New module: `backend/application/confirmed_matrix_fee_draft_line_builder.py` (`<500` lines, target `<=260`).
- Move these existing symbols/responsibilities from `confirmed_matrix_fee_draft_service.py`: `_build_groups`, `_build_cell_lookup`, `_build_group_lines`, `_missing_point_profile`, `_build_line_item`, `_calculate_line`, `_review`, and `_no_rule_match`.
- Keep `ConfirmedMatrixFeeDraftService` as the orchestration/read boundary: active Confirmed Matrix read, rule-library read, effective Measurement Plan/Point Profile read, warnings, manual report line, totals/header/status, and final `ConfirmedMatrixFeeAuthorityBuildResult`.
- Preserve behavior exactly before adding Child 2 duration behavior. Do not alter Base Fee precedence, rule resolution, LLCR, CR specified-current, Point Profile, Measurement Plan, or V2 attestation semantics.
- Final `confirmed_matrix_fee_draft_service.py` must remain `<470` UTF-8 physical lines including blanks after split and any later approved Child 2 transport hunk. No blank-line suppression.
- Regression commands must include the moved service/API focused tests, accepted Child 1 regression package, V2 attestation/currentness/rebase/CAS tests, and `py -m py_compile` for touched modules.

## B6-B8 Producer, Persistence, API, And Line-Count Refinement

Historical B6-B8 checkpoint (superseded by later readiness and authorization): the refined plan contract closed those findings while implementation and Developer planning-first were still unauthorized.

### Structured Import/Edit Inputs

Future Child 2 producers may write duration authority only from a structured per-group `duration_authorities` collection on the source-import row payload or Matrix edit command row. Fee/default-fill and Matrix producers are forbidden to populate duration authority by scanning `condition`, `requirement`, `day_expression`, method/test-item prose, legacy Step quantities, readings, Point Profile, Measurement Plan contact authority, LLCR/CR authority, saved Fee draft values, external files, or any arbitrary text.

Each non-null `duration_authorities` entry contains:

- `duration_value`: JSON number, positive finite non-zero.
- `duration_unit`: JSON string, trim/lowercase; allowed `hour`, `hours`, `hr`, `hrs`, `day`, `days`.
- `owning_group_key` / `owning_group_id`: JSON string for the owning group projection.
- `owning_row_key` / `owning_row_id`: JSON string for the owning row.
- `step_sequence`: positive JSON integer.
- `step_suffix_note`: JSON string or null, normalized to canonical empty string.
- `source_field`: structured producer field/path, trim, max 128 UTF-8 chars.
- `source_kind`: `import_structured` or `manual_edit`.
- `source_identity`: object containing owning source/draft row identity.

Derived fields are `normalized_hours`, source/revision/fingerprint/lineage, and typed status/diagnostic.

Update semantics:

- Omitted collection preserves existing editable draft authority collection.
- Explicit `null` clears editable draft authority for that row.
- Non-null collection replaces the entire authority collection after validation; partial entry updates are invalid.
- Import Replace may only carry import structured authority entries. Rows without structured entries remain legacy-null.
- Confirm Matrix publishes current valid draft authority to confirmed authority in the same transaction. Draft values are never Fee authority.
- Invalid shape/type/unit/value returns typed `400`/no-write. Stale root/source signature, stale CAS/currentness, mismatched row identity, multiple divergent values, or conflict returns typed `409`/no-write.
- Singular row-level authority is not persisted. Any future convenience fan-out is allowed only for a singleton owning group/sequence/suffix projection; otherwise the request must fail typed `409`/no-write. Identical duration values across groups must be represented as explicit per-group entries.

### Persistence Shape

Duration authority is owned by dedicated additive tables, not free-form Matrix text:

1. `source_matrix_duration_authorities`
2. `project_matrix_draft_duration_authorities`
3. `confirmed_matrix_duration_authorities`

Each table has the same logical shape. Parent columns are adapted to source/draft/confirmed ownership:

- parent id: `source_snapshot_id`, `project_matrix_draft_id`, or `confirmed_matrix_id` as `TEXT NOT NULL`.
- owning group id/key: `source_group_snapshot_id`, `draft_group_id`, or `confirmed_group_id` as `TEXT NOT NULL`.
- owning row id/key: `source_row_snapshot_id`, `draft_row_id`, or `confirmed_row_id` as `TEXT NOT NULL`.
- `step_sequence` `INTEGER NOT NULL`; `step_suffix_note` `TEXT NOT NULL DEFAULT ''`, with null/empty/whitespace canonicalized to empty string.
- `duration_value` `NUMERIC NOT NULL`; `duration_unit` `TEXT NOT NULL`; `normalized_hours` `NUMERIC NOT NULL`.
- `source_kind` `TEXT NOT NULL`; `source_field` `TEXT NOT NULL`; `source_import_id` `TEXT NULL`.
- `source_fingerprint` `TEXT NOT NULL`; `lineage_fingerprint` `TEXT NOT NULL`; `authority_revision` `TEXT NOT NULL`.
- `status` `TEXT NOT NULL`; `diagnostic_code` `TEXT NULL`; `diagnostic_message` `TEXT NULL`.
- `created_at` and `updated_at` `TEXT NOT NULL`.

Each table enforces a unique owning-row identity over `(parent id, owning group id/key, owning row id/key, step_sequence, step_suffix_note)` using non-null canonical `step_suffix_note`. SQLite `NULL` cannot participate in this unique key because duplicate NULL suffix rows would be allowed. Stored rows are usable authority rows; invalid producer inputs fail before write. Legacy absence is no row and maps to typed manual-review/no-write for Child 2 Units and Testing Fee.

Migration contract:

- Marker: `matrix_duration_authority_v1`.
- Zero-shape DB upgrades additively in one transaction.
- Partial-shape DB fails closed as `authority_corrupt` and must not publish duration authority.
- The migration transaction performs DDL, indexes/unique constraints, marker write, and read-verify via `PRAGMA table_info` and uniqueness checks; failure rolls back the attempt.
- Repeated `init_db` is idempotent and read-verifies full shape.
- Disposable SQLite tests must cover zero-shape upgrade, full-shape idempotency, partial-shape fail-close/no-write, injected rollback, and legacy-null manual-review/no-write.

### API / Model

- Request DTOs use a field-presence sentinel to distinguish omission, explicit `null`, and replacement.
- Responses round-trip the normalized effective object for source preview, editable draft, and confirmed Matrix where applicable.
- CAS/currentness/source snapshot/signature mismatches are typed `409`; invalid payload is typed `400`.
- Confirmed Fee draft consumes duration authority from the same single authority build and source-context fingerprint used by TASK_363D attestation; no second provider read is permitted.
- Frontend May Touch is exactly `frontend/src/api/client.ts` type-only unless a later Reviewer gate identifies a concrete compile failure requiring a named Matrix component. No Fee frontend hydration or visual UI work belongs to Child 2.

### Current Line Facts And Mechanical Split Strategy

Effective count command:

`(Get-Content <path> -Encoding UTF8).Count`

Current checked-out facts:

- `backend/infrastructure/storage/database.py` = `990`; prior `939` was the superseded non-blank `Measure-Object -Line` count.
- `backend/application/project_matrix_draft_persistence_service.py` = `507`; prior `448` was the superseded non-blank `Measure-Object -Line` count.
- `backend/api/routes_project_matrix_drafts.py` = `600`; prior `525` was the superseded non-blank `Measure-Object -Line` count.
- `backend/application/confirmed_matrix_fee_draft_service.py` = `479`; prior `451` was the superseded non-blank `Measure-Object -Line` count.

Required file strategy:

- `database.py`: must be split before adding duration schema. Move existing migration/bootstrap groups into `backend/infrastructure/storage/database_general_migrations.py` (`<=430` target) and `backend/infrastructure/storage/database_matrix_migrations.py` (`<=430` target); add `backend/infrastructure/storage/matrix_duration_authority_schema.py` (`<=260` target). `database.py` final `<=180` with only Base/engine/session/init runner orchestration.
- `project_matrix_draft_persistence_service.py`: current `507` is over the hard limit. It must be split before duration behavior. Move `_resolve_selected_group_keys`, `_build_draft_snapshot`, `_build_updated_snapshot`, `_normalized_group`, `_normalized_row`, `_normalize_optional_text`, and future duration normalization/serialization dispatch into `backend/application/project_matrix_duration_authority_payload.py` or a sibling bounded payload-builder module (`<=320` target); service final `<=430`.
- `routes_project_matrix_drafts.py`: must be split before duration DTO edits. Move request/response DTO classes `ProjectMatrixDraftCreateRequest` through `ConfirmedMatrixSnapshotResponse` to `backend/api/project_matrix_draft_dtos.py` (`<=280` target), and `_to_response` / `_to_confirmed_response` to `backend/api/project_matrix_draft_response_mappers.py` (`<=240` target). Route final `<=360`.
- `confirmed_matrix_fee_draft_service.py`: B5 line-builder split is mandatory before transport; final service `<470` after split plus transport.

All splits are behavior-preserving gates before new duration behavior. No blank-line suppression is allowed.

## Oversized Strategy

`fee_default_fill.py` is 470 physical lines. Any implementation must keep it below 500; if not possible, split approved helpers before adding behavior. The legacy oversized default-fill test remains read-only; new tests must be bounded.

`confirmed_matrix_fee_draft_service.py` cannot use an unspecified "if needed" split. The split listed in B3-B5 Discovery is mandatory for any future approved Child 2 transport.

## Future May Touch

- `backend/domain/source_matrix_models.py`, `backend/domain/project_matrix_draft_models.py`, `backend/domain/confirmed_matrix_authority_models.py`: additive typed duration authority domain shape.
- `backend/infrastructure/storage/models_matrix_source.py`, `backend/infrastructure/storage/models_project_matrix_draft.py`, `backend/infrastructure/storage/models_confirmed_matrix_authority.py`, `backend/infrastructure/storage/database.py`, `backend/infrastructure/storage/database_general_migrations.py`, `backend/infrastructure/storage/database_matrix_migrations.py`, `backend/infrastructure/storage/matrix_duration_authority_schema.py`: additive persistence/migration/bootstrap plus required mechanical split only; disposable SQLite validation required.
- `backend/infrastructure/storage/repositories/source_matrix_import.py`, `backend/infrastructure/storage/repositories/project_matrix_draft.py`, `backend/infrastructure/storage/repositories/confirmed_matrix_authority.py`: serialize/deserialize typed duration authority fields.
- `backend/application/source_matrix_import_builder.py`, `backend/application/project_matrix_draft_persistence_service.py`, `backend/application/project_matrix_duration_authority_payload.py`, `backend/application/project_test_plan_matrix_edit_service.py`: structured producer/normalizer/round-trip only.
- `backend/application/matrix_import_draft_builder.py`: selected-only source-to-draft authority id remapping; unselected/missing identities fail closed before persistence.
- `backend/application/confirmed_matrix_authority_service.py`: first Confirm Matrix authority publication in the same snapshot transaction.
- `backend/application/matrix_revision_flow_service.py` and new `backend/application/matrix_revision_snapshot_builder.py`: revision carry-forward/publication plus mandatory split. Move `_build_revision_draft_from_active`, `_build_confirmed_snapshot_from_revision_draft`, `_validate_draft_schedule`, `_normalize_optional_text`, and `_utc_now`; final service target `<=280`, builder target `<=380`, both `<500`.
- `backend/application/matrix_editor_session_service.py`, new `backend/application/matrix_editor_session_contracts.py`, `backend/application/matrix_editor_session_projection.py`, `backend/application/matrix_editor_session_signature.py`, `backend/application/matrix_editor_confirmed_snapshot_builder.py`, `backend/application/matrix_editor_session_publication.py`, and `backend/application/matrix_editor_session_draft_state.py`: source-replacement/first/revision publication, canonical authority signatures, draft state, and mandatory behavior-preserving split. Contracts/protocols/dataclasses, projections, signatures/lineage checks, confirmed snapshot construction, publication/fee-promotion methods, and draft-state/token/currentness helpers move to the named bounded modules. The public service retains seed/save/discard/confirm orchestration and compatibility re-exports. Final service target `<=450`; each new module target `<=380`; all remain `<500`.
- `backend/api/routes_project_test_plan_matrix_edit.py`, `backend/api/routes_project_matrix_drafts.py`, `backend/api/project_matrix_draft_dtos.py`, `backend/api/project_matrix_draft_response_mappers.py`: typed DTO validation/serialization, response mapping, and no-write errors.
- `backend/api/routes_matrix_editor_session.py`, new `backend/api/matrix_editor_session_dtos.py`, and new `backend/api/matrix_editor_session_response_mappers.py`: seed/save/confirm transport only, with a mandatory route split. Final route target `<=360`, DTO target `<=260`, mapper target `<=220`.
- `frontend/src/api/client.ts`: type-only structured authority DTO/client update.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`: non-visual preservation hunk only so seed-to-save/confirm mapping retains normalized `duration_authorities`; no control, copy, layout, state-machine, or inference change.
- `backend/application/confirmed_matrix_fee_duration_authority.py` (`<500` lines): confirmed owning-row duration authority consumer/helper.
- `backend/application/confirmed_matrix_fee_draft_line_builder.py` (`<500` lines, target `<=260`): mandatory behavior-preserving split target.
- `backend/application/confirmed_matrix_fee_draft_service.py`: post-split orchestration/import/transport hunk only; final `<470`.
- `backend/modules/fee_evaluation/fee_default_fill_models.py`: bounded `FeeDurationAuthority` DTO/context field only.
- `backend/modules/fee_evaluation/fee_default_fill.py` (`<500` final).
- `backend/modules/fee_evaluation/fee_default_fill_common.py`.

## Exact Bounded Test Package

- `tests/unit/test_fee_default_fill_explicit_hour_authority.py` (`<500` lines): Salt Spray and approved High temperature Life explicit-hour authority, invalid-hour matrix, rejected aliases, and no arbitrary text/legacy fallback.
- `tests/unit/test_fee_default_fill_temperature_rise_units.py` (`<500` lines): Temperature Rise sample Units while current is pending, valid/invalid sample quantity, and manual-field preservation.
- `tests/integration/test_confirmed_matrix_fee_draft_dependent_fields_api.py` (`<500` lines): confirmed Matrix draft API/service composition, single/multi-Group isolation, no cross-Group duration, no readings multiplier, and plain CONTACT RESISTANCE no LLCR fallback.
- `tests/integration/test_fee_default_fill_dependent_fields_v2_rebase.py` (`<500` lines): TASK_361L/TASK_363D V2 attestation/currentness/reviewed rebase/CAS no-write regression for Child 2 automatic non-Base-Fee fields and manual preservation.
- `tests/unit/test_confirmed_matrix_fee_duration_authority.py` (`<500` lines): exact row identity, unit normalization, conflict/multiple/malformed/stale/wrong-row diagnostics, source/fingerprint binding, and no fallback to disallowed sources.
- `tests/integration/test_matrix_typed_duration_authority_round_trip_api.py` (`<500` lines): import/edit/confirm persistence/API round-trip, legacy-null compatibility, and disposable DB migration proof.
- `tests/unit/test_matrix_duration_authority_projection.py` (`<500` lines): source-to-draft, first Confirm, revision carry-forward/confirm, and fail-closed identity projection.
- `tests/unit/test_matrix_duration_authority_session_signature.py` (`<500` lines): canonical authority signatures, omission/null/replacement, stale tokens, and source-replacement carry-forward.
- `tests/integration/test_matrix_duration_authority_publication_api.py` (`<500` lines): first/revision/source-replacement publication, rollback/no-write, and response/reload round-trip.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.durationAuthority.test.tsx`: bounded non-visual seed-to-save/confirm payload preservation.

The existing oversized `tests/unit/test_fee_default_fill.py`, `tests/unit/test_confirmed_matrix_authority_service.py`, `tests/unit/test_matrix_editor_session_service.py`, and `tests/integration/test_matrix_editor_session_api.py` are read-only regression execution only.

## Dependency-Release Reconciliation

- Child 1 accepted commit: `c5d91c36c5e1d54885fc0a3b406c92ff9aa0cb6b` (`feat(fee): resolve matrix base fee policy`).
- Released dependency: Base Fee metadata/default precedence is now read-only accepted baseline for Child 2.
- Historical gate fact: Child 2's formal Option 1 re-scope was initially limited to Reviewer plan/dependency-release re-gate; that restriction is superseded by the final authorization reconciliation.
- Child 2 locked boundary: it must not write Base Fee, recalculate Base Fee metadata, redefine Base Fee precedence, use `matrix_group_count` as trigger authority, fallback plain `CONTACT RESISTANCE` to LLCR, or map rejected temperature aliases.
- Historical next role (completed): Reviewer scope and implementation-readiness re-gate after Developer planning-first.

## Reviewer B1-B3 Fix

- Removed prior B1-overlap wording and froze Child 2 as having no Base Fee write/metadata ownership.
- Frozen Base Fee final value/metadata as accepted Child 1 exclusive ownership; Child 2 consumes it read-only for Testing Fee derivation.
- Frozen explicit-hour authority validity, invalid cases, forbidden inference sources, and typed no-write behavior.
- Frozen exact bounded test modules and retained the oversized legacy test as read-only only.
- Superseded the B3 Option A helper/context/transport checkpoint after B4 showed no existing legal typed duration authority source, then recorded User approval for Option 1 additive typed duration authority.

Historical checkpoint: Reviewer plan/dependency-release re-gate passed, User approved Developer docs-only planning-first, and Developer planning-first completed. That pre-readiness checkpoint is superseded by the final authorization reconciliation below. Child 3 and the umbrella remain blocked.

## Developer Planning-First Technical Refinement

Date: 2026-07-23

This docs-only refinement follows the passed Reviewer plan/dependency-release
re-gate and the User's explicit approval for Developer planning-first. It does
not authorize product or test implementation. Child 1 remains the read-only
accepted Base Fee baseline at
`c5d91c36c5e1d54885fc0a3b406c92ff9aa0cb6b`; Child 3 and the umbrella remain
blocked.

### Verified Code Facts

- Checked-out `HEAD` is the accepted Child 1 commit.
- `FeeDefaultFillContext` has text, sample quantity, Step quantity, and CR
  authority fields, but no typed duration authority.
- `_duration_hour_result()` still reads `_HOUR_PATTERN` from
  `_combined_text(context)`. That path cannot be reused for Child 2 authority.
- Child 1 applies final Base Fee and derived Testing Fee after default-fill in
  `apply_matrix_fee_line_policies()`. Child 2 must provide only valid
  non-Base-Fee inputs/metadata and must not rewrite, recalculate, or attest
  Base Fee.
- Source snapshot fingerprints currently include groups, rows, and cells only.
  A future structured duration authority must participate in canonical source
  root/row identity and TASK_261 replay verification.
- Project Matrix draft replacement currently replaces the aggregate children
  wholesale. Omission-preserve therefore must merge the prior authority
  collection before repository replacement; it cannot be implemented as a
  repository default.
- Generic `Base.metadata.create_all()` currently creates every registered
  non-Point-Profile table before dedicated migrations. The three duration
  authority tables must be excluded from that generic call so the dedicated
  all-or-nothing bootstrap owns zero-shape/partial-shape recognition.
- The blank-inclusive counts remain exactly `990`, `507`, `600`, and `479` for
  the four mandatory split files. `fee_default_fill.py` is `470`.
- Three current dirty May-Touch files are external residuals:
  `confirmed_matrix_fee_draft_service.py` (`6/20`),
  `fee_default_fill.py` (`18/3`), and `fee_default_fill_common.py` (`4/1`).
  This planning-first pass does not absorb, clean, or attribute those hunks.

### Required Planner May-Touch Reconciliation

At the historical planning-first checkpoint, read-only call-flow inspection
found publication/carry-forward sites missing from the then-current Future May
Touch list. Product implementation remained unauthorized until Planner
reconciled the exact solution later in this plan.

Required behavior owners:

- `backend/application/matrix_import_draft_builder.py`: maps immutable source
  authority identities to selected draft group/row ids. Without this hunk,
  source authority never reaches the editable draft created by the current
  Matrix import commit path.
- `backend/application/confirmed_matrix_authority_service.py`: first Confirm
  Matrix publication must map draft authority to confirmed group/row ids in
  the same snapshot transaction.
- `backend/application/matrix_revision_flow_service.py`: confirmed-to-draft
  carry-forward and revision-draft-to-confirmed publication must preserve the
  authority. The file is currently `491` blank-inclusive lines, so adding
  behavior requires a named mechanical extraction and a final `<500` result.
- `backend/application/matrix_editor_session_service.py`: the source
  replacement publisher builds a confirmed snapshot independently, and
  `build_project_matrix_draft_payload_signature()` currently omits duration
  authority. The file is `1901` blank-inclusive lines and cannot become a
  Child 2 candidate without an explicit Planner-approved split/package
  strategy.

Planner must choose and record one fail-closed route:

1. add the exact publication/carry-forward/signature call sites and bounded
   helper/split files to May Touch, with every touched Python file ending below
   500 physical lines; or
2. formally exclude a workflow only after proving it cannot create, edit,
   confirm, supersede, or silently drop typed duration authority.

Repository-side implicit lookup/copy is not an acceptable shortcut: repository
methods currently persist the supplied aggregate, and hidden draft reads would
make the returned domain snapshot disagree with persisted authority.

### Conditional File-Level Implementation Order

The following sequence is executable only after the May-Touch reconciliation
above and later explicit product authorization.

1. **Freeze the package and RED gates**
   - Record accepted HEAD and exact external dirty hunks.
   - Add only the six bounded test modules already named by this plan.
   - First RED cases cover zero/partial schema, source/draft/confirmed
     round-trip, omission/null/replacement, per-group identity, canonical
     suffix uniqueness, publication/carry-forward, exact Fee consumption, and
     V2 rebase/CAS.

2. **Perform behavior-preserving mechanical splits**
   - Move general migrations and Matrix migrations out of `database.py`;
     preserve `init_db()` call order and existing migration tests.
   - Move draft payload normalization/building out of
     `project_matrix_draft_persistence_service.py`.
   - Move DTOs and response mappers out of
     `routes_project_matrix_drafts.py`.
   - Move row-to-Fee-line composition out of
     `confirmed_matrix_fee_draft_service.py`.
   - Apply any additional Planner-approved revision/session split before
     duration behavior.
   - Run existing read-only regressions after each mechanical split.

3. **Add dedicated schema ownership**
   - Register ORM models but exclude the three duration tables from generic
     `Base.metadata.create_all()`.
   - Read all existing duration objects before DDL. Zero shape may proceed;
     any partial or malformed shape returns `authority_corrupt` before DDL.
   - In one dedicated transaction create the three tables, exact foreign keys,
     checks, unique identities, indexes, and marker; read-verify before commit.
   - Roll back every duration object on create or verification failure.

4. **Add domain aggregates and repositories**
   - Add ordered `duration_authorities` tuples to source, draft, and confirmed
     snapshots.
   - Repositories insert/load/delete the child rows in the same session as
     their owning aggregate.
   - Draft full replacement deletes/reinserts authority only after the
     application layer resolves omission/null/replacement.
   - Canonical identity is parent + owning group + owning row +
     `step_sequence` + non-null `step_suffix_note`.

5. **Normalize structured producers**
   - Legacy duration compatibility fields remain display/scheduling facts and
     never become Fee authority.
   - `duration_authorities` is validated independently for each group/row/step
     entry.
   - Source fingerprints and TASK_261 replay identity include the sorted
     canonical authority collection.
   - Selected-only draft construction remaps source ids to draft ids and drops
     entries for unselected groups without cross-group fan-out.

6. **Implement field-presence commands and typed API**
   - Pydantic nested row/step DTOs use `model_fields_set` to distinguish
     omitted from explicit `null`; Pydantic undefined values do not leak into
     application/domain types.
   - Application commands carry an explicit presence flag plus either clear or
     full replacement values.
   - Invalid shape is typed `400`; identity/source/CAS conflicts are typed
     `409`; every error is no-write.
   - Response mappers and `frontend/src/api/client.ts` round-trip normalized
     facts only. No visual frontend work is part of Child 2.

7. **Publish and carry authority without loss**
   - First confirmation, revision draft creation, revision confirmation, and
     every retained source-replacement path use the same pure id-remapping
     helper.
   - Unselected/nonexistent group or row identities are rejected before
     persistence.
   - Confirm Matrix remains the only draft-to-confirmed publication boundary.
   - Saved-payload/source signatures include sorted canonical duration facts.

8. **Consume authority in the single Fee build**
   - `confirmed_matrix_fee_duration_authority.py` performs exact
     confirmed-group/row/sequence/suffix matching and emits one typed
     `FeeDurationAuthority`.
   - The line builder passes that object in `FeeDefaultFillContext` from the
     already loaded confirmed snapshot; no provider reread is allowed.
   - Only approved duration rules consume it. The approved High temperature
     Life alias remains `15/hour`; rejected aliases and plain Contact
     Resistance retain their accepted manual/no-fallback behavior.
   - Child 1 final Base Fee and Base Fee metadata remain untouched. Testing Fee
     is derived only after Units and other dependencies are safe.

9. **Prove V2 and rollback boundaries**
   - TASK_363D row safety/automatic-default attestation includes the resulting
     non-Base-Fee automatic values through the existing single build.
   - Saved/current mismatch requires reviewed rebase; stale CAS is typed
     conflict/no-write.
   - Manual Unit Price, Units, Base Fee, discount, notes, and spend time remain
     protected by existing provenance.

### TDD And Validation Order

Run the bounded tests in this order:

1. schema/bootstrap and repository round-trip;
2. import/edit/confirm/revision authority transport;
3. exact duration helper and default-fill unit tests;
4. confirmed Fee draft single/multi-Group integration;
5. V2 attestation/currentness/rebase/CAS integration;
6. existing storage, Matrix import/session/revision, Fee, LLCR/CR, and Child 1
   regressions as read-only gates.

Every candidate Python file must be measured with
`(Get-Content <path> -Encoding UTF8).Count` and finish below 500 lines. Final
checks are `py_compile`, focused pytest, `git diff --check`, UTF-8 trailing
whitespace, exact-path/forbidden-scope scan, no-real-data scan, and
staging-empty.

### Rollback And Package Isolation

- All behavior additions are additive; rollback is code rollback plus leaving
  unused additive tables intact. No legacy data rewrite or destructive table
  rebuild is planned.
- Migration failure rolls back its own transaction and never guesses a repair
  for partial shape.
- Mixed May-Touch files require hunk-level packaging against accepted HEAD.
  Whole-file staging is forbidden.
- Child 1 product files are read-only except the exact Child 2 call hunk later
  authorized by Planner/User. Child 3, the twelve-path umbrella, real
  databases/files, frontend Fee hydration, seeds, and external residuals stay
  excluded.

### Superseded Planning-First Checkpoint

Developer planning-first identified the publication/carry-forward/signature
gap and originally stopped for Planner reconciliation. That checkpoint is
superseded by the Planner source-of-truth reconciliation below. At that
historical checkpoint, product implementation was unauthorized.

## Planner Source-Of-Truth Reconciliation

Date: 2026-07-23

The workflow exclusion option is rejected by repository evidence. Source import
selection, first Confirm Matrix, revision draft creation/confirmation, and
Matrix Editor source replacement are all legal publication paths. Excluding
any one would permit a structured duration authority to be omitted from the
returned aggregate, silently dropped during publication, or excluded from the
saved/source signature.

The exact additional application owners are therefore:

- `matrix_import_draft_builder.py` for selected source-to-draft remapping;
- `confirmed_matrix_authority_service.py` for first publication;
- `matrix_revision_flow_service.py` plus
  `matrix_revision_snapshot_builder.py` for revision carry-forward/publication;
- `matrix_editor_session_service.py` plus the bounded contracts, projection,
  signature, confirmed-snapshot, publication, and draft-state modules for
  source replacement and stale-token safety.

The current blank-inclusive facts are `matrix_import_draft_builder.py=152`,
`confirmed_matrix_authority_service.py=310`,
`matrix_revision_flow_service.py=491`,
`matrix_editor_session_service.py=1901`, and
`routes_matrix_editor_session.py=556`. The 491/1901/556 files require the
mandatory splits frozen in Future May Touch before any duration behavior.
Compatibility imports/re-exports must preserve existing external callers, so
locked composition files do not need incidental edits.

`MatrixEditorWorkspace.tsx` is admitted only for an exact non-visual
data-preservation hunk: its explicit row mapping must carry the normalized
authority collection through seed, autosave, and Confirm. `$impeccable`
product context and frontend architecture rules were read; no new UI control,
copy, layout, interaction, state machine, or business inference is in scope.

All new detailed assertions remain in bounded modules. Existing 502/1339/1107
line authority/session tests and the oversized default-fill test are read-only
regression gates.

## Final Authorization Reconciliation

Date: 2026-07-24

Historical authorization checkpoint (superseded by Reviewer B1): Reviewer
scope and implementation-readiness re-gate passed and User explicitly
authorized Child 2 product implementation. Developer subsequently completed
that implementation within the exact May Touch, mandatory split order,
bounded tests, and mixed-hunk package isolation frozen in this plan.

The authorization covers selected source-to-draft transport, first Confirm,
revision carry-forward/confirmation, Matrix Editor source replacement/session
persistence/canonical signatures, and confirmed Fee same-build consumption.
Confirm Matrix remains the publication boundary. Duration inference from text,
legacy Step quantity, readings, Point Profile, LLCR/CR, or another row/Group is
forbidden. Child 1 Base Fee value/metadata remains read-only, and
TASK_361L/TASK_363D attestation, currentness, reviewed rebase, CAS/no-write,
and manual-field protection remain authoritative. Child 3 and the umbrella
remain blocked.

## Reviewer B1 Tests-Only Fix Plan

Reviewer has accepted the production routing. No further product, schema,
storage, API, client, frontend, seed, or composition change is authorized in
this pass.

The only writable test hunks are the assertions inside these exact nodes:

- `tests/unit/test_fee_default_fill.py::test_temperature_named_duration_rules_default_base_fee_to_zero_without_duration[fee_rule_high_temperature_life-Temperature life-unit_price0]`;
- `tests/unit/test_fee_default_fill.py::test_salt_spray_uses_hour_duration_from_matrix_condition`;
- `tests/unit/test_confirmed_matrix_fee_draft_service.py::test_fee_draft_defaults_non_rise_temperature_items_to_per_hour[Long-term high temperature zone load]`;
- `tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py::test_approved_temperature_alias_uses_hours_and_common_base_fee[1]`;
- the same parameterized node at `[2]`;
- `tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py::test_approved_temperature_alias_without_hours_keeps_dependencies_pending`.

These are five assertion locations and six pytest cases. Migration may replace
only stale condition-text fallback or old generic diagnostic expectations:

- missing typed confirmed High-temperature/Salt Spray authority is
  manual-review/no-write;
- condition text is not duration authority;
- valid exact owning-row authority is required for Units and Testing Fee;
- missing/invalid diagnostics name the confirmed typed duration authority
  requirement.

Temperature & Humidity and every other legacy rule, fixture meaning, and
assertion remain unchanged. Current blank-inclusive test-file counts are
`912`, `683`, and `301`; the two oversized files cannot gain lines, and
line-neutral replacement is preferred. New assertions, if essential, may go
only into existing approved bounded Child 2 test modules.

Validation must run all six exact cases, the full three locked legacy modules,
the bounded Child 2 package, and scoped diff/trailing/line/staging checks.
Expected first gate is zero failures in the authorized nodes with no regression
outside them. Product code must have zero diff from the Reviewer B1 candidate.

Historical B2 note: the TASK_366C-owned missing `method_authority` composition
was excluded from this tests-only pass. Its owner subsequently restored the
composition and Reviewer closed those failures. Child 2 still cannot alter
`backend/api/dependencies.py` or any composition path. Child 3 and the umbrella
remain blocked.

Historical High/Salt tests-only route (completed): Developer bounded tests-only fix followed by Reviewer re-gate.

## External Fee-Rebase Fixture Context Plan

The High-temperature/Salt Spray tests-only pass is complete and Reviewer has
accepted Child 2 product behavior. Product code is locked.

The remaining Matrix Editor lifecycle failure is owned by one stale integration
fixture, not by Child 2 production, TASK_366C composition, or the rebase
algorithm. The fixture persists and queries `fee_rules_v2026_06_03`, while the
runtime's exact pending-rebase context uses accepted active
`fee_rules_v2026_07_17_r6`. TASK_361L/TASK_363D prohibit cross-context fallback,
so `preserved_count=0` is correct for the mismatched fixture.

Planner's proposed tests-only package, pending Reviewer confirmation:

- `tests/integration/test_matrix_editor_session_api.py` only;
- exact node:
  `test_matrix_editor_session_autosave_restore_confirm_and_discard`;
- exact helper/call-chain hunk: replace the obsolete version literal in
  `_seed_previous_pricing_draft()` and the promoted-draft repository lookup;
- replacement value: accepted active `fee_rules_v2026_07_17_r6`;
- line-neutral only; the file remains `1107` blank-inclusive physical lines;
- no assertion, pricing values, manual note, summary, product code, rebase key,
  provenance, CAS, API shape, or fallback change.

Preservation semantics are frozen:

1. `preserved_count` counts source rows matched to target rows by stable rebase
   identity in the exact current Matrix and rule context.
2. It does not count manual fields and does not authorize cross-version reuse.
3. Automatic values refresh from current backend defaults; only proven
   compatible manual provenance survives.
4. Testing Fee remains derived from final safe values.
5. Context/fingerprint mismatch remains typed blocked/no-write; load/Cancel
   remain zero-write.

Validation after any later authorization:

- the exact Matrix Editor lifecycle node;
- full `tests/integration/test_matrix_editor_session_api.py`;
- `test_matrix_fee_draft_rebase_service.py`;
- `test_matrix_fee_pending_rebase_service.py`;
- `test_matrix_fee_rebase_promotion_service.py`;
- TASK_361L/TASK_363D V2 contract, prior-default attestation, and safe-rebase
  focused modules;
- line count, diff/trailing, no-product-hunk, no-real-data, and staging checks.

No Developer fix is authorized yet. Next legal role: Reviewer tests-only scope
confirmation. Child 3 and the umbrella remain blocked.
