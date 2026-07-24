# FEE_DEFAULT_FILL_DEPENDENT_FIELD_CORRECTIONS

Status: complete / Integrator accepted pending controlled local package closeout
Lane: `fee-default-fill-dependent-field-corrections`
Parent: `FEE_DEFAULT_FILL_RESIDUAL_PACKAGE_RECONCILIATION`
Implementation authorization: completed; Reviewer and QA gates passed
Date: 2026-07-24

## Purpose

Own backend default-fill dependent-field corrections after the accepted Child 1 rule-resolution/Base Fee precedence baseline:

- Salt Spray explicit hours as per-hour default.
- Temperature-duration rows with explicit valid hours versus missing/invalid duration diagnostics.
- Temperature rise sample Units while current is pending.
- `manual_required()` carrying automatic Units only when the field is not manual-required.

## Dependency / Precedence

Child 1 `FEE_RULE_RESOLUTION_MATRIX_BASE_FEE_POLICY` is complete/accepted at local commit `c5d91c36c5e1d54885fc0a3b406c92ff9aa0cb6b` (`feat(fee): resolve matrix base fee policy`), verified as a HEAD ancestor. That accepted package releases Child 2's metadata/default precedence dependency.

This lane cannot select or redefine Base Fee ownership. The accepted Child 1 contract is the source of truth: every Fee line uses manual Base Fee first, explicit accepted rule-specific Base Fee second, otherwise automatic Base Fee `0`; single-Group and multi-Group use identical precedence and `matrix_group_count` is not a trigger. Child 2 must not override manual Base Fee, reimplement Base Fee precedence, recalculate Base Fee metadata, or re-attest Base Fee.

No default-fill hunk may override proven manual Unit Price, Units, Base Fee, discount, notes, or spend time. Any changed automatic non-Base-Fee value must be captured by TASK_363D attestation and existing V2 currentness/rebase guards.

For missing or invalid duration, affected rows keep Units and Testing Fee unset/Pending/review-required with an accurate typed diagnostic; Child 1 remains the only source for final Base Fee value and Base Fee metadata.

High-temperature alias source-of-truth for this child:

- Only `Long-term high temperature zone load` is approved as High temperature Life at `15/per hour`.
- Units only from explicit hour authority; missing/invalid hours produce typed review/no automatic write.
- `Long-term temperature cycle with load` and `Long-term damp heat` are not approved and remain no-rule/manual-review.

## Typed Duration Authority Contract

User approved Option 1: add an additive typed duration authority data contract, producer, persistence/API/model boundary, and single-build Fee draft transport. This is the only approved path for `Long-term high temperature zone load` automatic `15/per hour`. Fee code must not scan `condition`, `requirement`, `day_expression`, legacy Step quantity, arbitrary free text, another row/Group, Point Profile, LLCR/CR authority, saved pricing draft values, or external files to infer duration.

Minimum typed authority fields:

- `duration_value`;
- `duration_unit`;
- `normalized_hours`;
- owning `confirmed_group_id` / `draft_group_id` and `confirmed_row_id` / `draft_row_id`;
- parsed `step_sequence` and `step_suffix_note` when applicable;
- source identity (`source_import_id`, `source_snapshot_id`, `source_row_snapshot_id`, source field name/path);
- revision, fingerprint, and lineage for the confirmed Matrix authority carrying the value;
- diagnostic/status (`usable`, `missing`, `invalid`, `conflict`, `multiple`, `stale`, `wrong_row`, `unsupported_unit`, `authority_corrupt`, or equivalent typed states).

Producer boundary:

- Authority must be produced as a structured field in the Matrix import/edit/confirmation chain and saved before or during Confirm Matrix publication.
- Confirm Matrix remains the publication boundary. Editable draft values are not fee authority until confirmed.
- Fee draft consumes confirmed owning-row authority only, from the same single authority build used to produce the Fee draft and TASK_363D automatic-default attestation.
- Legacy confirmed rows without typed duration authority remain typed manual-review/no-write for the affected Units and Testing Fee.

Numeric rules:

- Valid value is positive, finite, and numeric.
- Supported units are `hour`, `hours`, `hr`, `hrs`, `day`, and `days`, normalized deterministically to hours (`day(s) * 24`, hour aliases unchanged).
- Zero, negative, NaN, Infinity, non-numeric, empty, unsupported unit, conflict, multiple divergent values, stale lineage/fingerprint, missing authority, missing source identity, wrong row/group, and malformed payload all produce typed no-write/review-required.

For approved `Long-term high temperature zone load` with valid typed duration authority: Unit Price is `15`, Unit Type is `per hour`, Units equal `normalized_hours`, and Testing Fee is safely derived from Unit Price, Units, accepted Child 1 final Base Fee, and discount. Manual fields are never overwritten.

## B3-B5 Discovery / Re-Scope

Reviewer B3 confirmed that current `FeeDefaultFillContext` exposes only text fields, sample quantity, step tokens/quantities, and CR authority. It does not carry typed duration value/unit, row identity, lineage, fingerprint, or diagnostic. `ConfirmedMatrixFeeDraftService` currently constructs that context from Matrix row text, and existing default-fill duration logic scans combined text. That cannot satisfy the strict owning-row typed duration authority contract.

Reviewer B4 further confirmed that adding helper/DTO/transport is insufficient unless the underlying `ConfirmedMatrixRow` or its source authority contains a legal duration fact. Planner rechecked the real upstream:

- Source Matrix snapshots persist row text only for `test_item`, `source_section`, `method`, `condition`, and `requirement`; they do not persist duration value/unit.
- Editable and confirmed Matrix row models persist `condition`, `requirement`, and `day_expression`, but no typed duration value/unit/source identity/lineage.
- The project test-plan matrix edit route has compatibility inputs such as `duration_value`, `duration_unit`, and `estimated_duration_hours`, but those are normalized into preview/edit payload fields and are not published as confirmed Matrix row authority.
- Measurement Plan/contact authorities are point/readings authorities, not duration authorities.
- TASK_363D automatic-default attestation can bind defaults and row safety, but it cannot invent or prove row-level duration authority absent from the single authority build.

User/Orchestrator approved Option 1 after that discovery. This paragraph records the historical planning-first checkpoint: the prior blocked state was superseded, Reviewer plan/dependency-release re-gate passed, User approved Developer docs-only planning-first, and Developer planning-first completed. The later Reviewer scope/readiness pass and User product authorization are recorded in the current status and Final Authorization Reconciliation below.

Reviewer B5 also requires a concrete mechanical split before any future transport implementation. Current checked-out `backend/application/confirmed_matrix_fee_draft_service.py` is `479` blank-inclusive UTF-8 physical lines by `(Get-Content <path> -Encoding UTF8).Count`; the `451` figure is a superseded non-blank `Measure-Object -Line` count. Any future Child 2 transport scope must first freeze and execute a behavior-preserving split:

- New target module: `backend/application/confirmed_matrix_fee_draft_line_builder.py` (`<500` lines, target `<=260`).
- Move existing row-to-line composition responsibilities from `confirmed_matrix_fee_draft_service.py`: `_build_groups`, `_build_cell_lookup`, `_build_group_lines`, `_missing_point_profile`, `_build_line_item`, `_calculate_line`, `_review`, and `_no_rule_match`, plus only the imports those symbols require.
- Keep `ConfirmedMatrixFeeDraftService` responsible for dependency reads, single authority build orchestration, top-level totals/header/status assembly, and returning `ConfirmedMatrixFeeAuthorityBuildResult`.
- The split must be behavior-preserving and must not change Base Fee, rule matching, LLCR, CR specified-current, Point Profile, Measurement Plan, or V2 attestation semantics.
- Final `confirmed_matrix_fee_draft_service.py` must be `<470` UTF-8 physical lines including blanks after split and after any later approved Child 2 transport hunk; no blank-line suppression may be used to pass the limit.
- Regression before business behavior: focused Fee draft service/API tests, accepted Child 1 regression tests, V2 attestation/currentness/rebase/CAS tests, and `py -m py_compile` for touched modules.

## B6-B8 Structured Authority / Persistence / Size Refinement

Reviewer B6-B8 are now frozen as part of the current effective plan. This section supersedes any earlier wording that only said "additive nullable shape" or "if needed mechanical split".

### Structured Producer Inputs

Child 2 may populate duration authority only from explicit structured fields, never by parsing row prose. The only future producer fields are:

- Source import row payload collection: `duration_authorities`.
- Matrix edit command row collection: `duration_authorities`.

`duration_authorities` is an optional field-presence-aware array. Each array entry is one authority for exactly one owning group/row/sequence/suffix identity and has these effective fields:

- `duration_value`: JSON number, required when the object is non-null.
- `duration_unit`: JSON string, required when the object is non-null; accepted values are `hour`, `hours`, `hr`, `hrs`, `day`, `days`, case-insensitive after trim.
- `owning_group_key` / `owning_group_id`: JSON string matching the current import/edit row's owning group projection.
- `owning_row_key` / `owning_row_id`: JSON string matching the current import/edit row.
- `step_sequence`: positive JSON integer.
- `step_suffix_note`: JSON string or null; normalized to canonical empty string for persistence and uniqueness.
- `source_field`: JSON string naming the structured producer field/path, required; max 128 UTF-8 characters after trim.
- `source_kind`: JSON string enum `import_structured` or `manual_edit`, required.
- `source_identity`: JSON object containing the current source/draft row identity that produced the value; required for import and edit paths.

Normalization:

- `duration_unit` is trimmed and lowercased.
- `duration_value` must be positive, finite, numeric, and non-zero.
- `normalized_hours` is derived only from the validated pair: hour aliases remain unchanged, day aliases multiply by `24`.
- The owning authority identity is the current group id/key, row id/key, `step_sequence` integer, and canonical non-null `step_suffix_note` string.

Producer semantics:

- Omitted `duration_authorities` preserves the existing editable draft authority collection for that row.
- Explicit `duration_authorities: null` clears the editable draft authority collection for that row and persists no confirmed Fee authority until later valid values are confirmed.
- Non-null replacement validates and atomically replaces the entire row authority collection; partial entry updates are forbidden.
- Import Replace uses only import structured `duration_authorities` entries; rows without entries remain legacy-null and later produce manual-review/no-write for Child 2 automatic Units/Testing Fee.
- Manual Matrix edit may set or clear authority only through the structured collection field; editing `condition`, `requirement`, `day_expression`, or other text cannot create, update, or clear duration authority.
- Confirm Matrix is the only publication boundary: it copies current valid editable draft duration authority into confirmed authority in the same publication transaction. Unconfirmed draft authority is never Fee authority.
- Conflicting values for the same owning row/source, mismatched group/row/sequence/suffix identity, multiple divergent source values, stale root/source signature, or stale CAS produce typed `409`/no-write.
- Invalid type, invalid unit, missing required object field, overlength `source_field`, malformed `source_identity`, zero/negative/non-finite/non-numeric values, or partial object shape produce typed `400`/no-write.
- Singular row-level authority is not a valid persisted contract. If a future UI convenience supplies one value for a row, the application layer may fan out only when the exact owning group/sequence/suffix collection is singleton and the response records the concrete entry; otherwise it must reject as typed `409`/no-write. Identical values across groups must be represented as explicit per-group entries, not implicit cross-Group fan-out.

Producer/parser prohibition:

- Source import, Matrix edit, Confirm Matrix, and Fee code must not infer duration from `condition`, `requirement`, `day_expression`, test item text, method text, legacy Step quantities, readings, Point Profile, Measurement Plan contact authorities, LLCR/CR authorities, saved Fee draft values, files, or any arbitrary free text.

### Persistence Contract

The additive storage owner is a dedicated duration-authority schema, not ad hoc JSON inside Matrix row text. Future implementation must create all three tables as one shape:

1. `source_matrix_duration_authorities`
2. `project_matrix_draft_duration_authorities`
3. `confirmed_matrix_duration_authorities`

Each table uses the same logical columns and SQLite affinities, with parent-id column names adapted to source/draft/confirmed ownership:

- parent id: `source_snapshot_id`, `project_matrix_draft_id`, or `confirmed_matrix_id` as `TEXT NOT NULL`.
- owning group id/key: `source_group_snapshot_id`, `draft_group_id`, or `confirmed_group_id` as `TEXT NOT NULL`.
- owning row id/key: `source_row_snapshot_id`, `draft_row_id`, or `confirmed_row_id` as `TEXT NOT NULL`.
- `step_sequence` as `INTEGER NOT NULL`.
- `step_suffix_note` as `TEXT NOT NULL DEFAULT ''`, normalized null/empty/whitespace to canonical empty string.
- `duration_value` as `NUMERIC NOT NULL`.
- `duration_unit` as `TEXT NOT NULL`.
- `normalized_hours` as `NUMERIC NOT NULL`.
- `source_kind` as `TEXT NOT NULL`.
- `source_field` as `TEXT NOT NULL`.
- `source_import_id` as `TEXT NULL`.
- `source_fingerprint` as `TEXT NOT NULL`.
- `lineage_fingerprint` as `TEXT NOT NULL`.
- `authority_revision` as `TEXT NOT NULL`.
- `status` as `TEXT NOT NULL`.
- `diagnostic_code` as `TEXT NULL`.
- `diagnostic_message` as `TEXT NULL`.
- `created_at` and `updated_at` as `TEXT NOT NULL`.

Each table must enforce a unique owning-row identity on `(parent id, owning group id/key, owning row id/key, step_sequence, step_suffix_note)` using the non-null canonical `step_suffix_note`. SQLite `NULL` is forbidden in the unique key because it would allow duplicate nullable suffix rows. Each stored row must be internally usable; invalid producer input is rejected before write rather than stored as a usable authority. Legacy absence is represented by no authority row and maps to typed manual-review/no-write for Child 2 automatic Units and Testing Fee.

Migration/bootstrap:

- The migration marker is `matrix_duration_authority_v1`.
- Zero-shape existing databases are upgraded additively in one transaction.
- Partial-shape databases fail closed as `authority_corrupt` and must not auto-create missing fragments outside the single transaction.
- The transaction performs DDL, nullable legacy backfill/no-op recognition, index/unique creation, marker write, and read-verify through `PRAGMA table_info` plus uniqueness checks before returning success.
- Failure rolls back all duration-authority DDL for that attempt; repeated `init_db` is idempotent and read-verifies the same shape.
- Disposable SQLite tests must cover zero-shape upgrade, full-shape idempotency, partial-shape fail-close/no-write, rollback on injected DDL/read-verify failure, and legacy confirmed rows producing manual-review/no-write.

### API / Model Contract

- API request DTOs must use a field-presence sentinel so omitted, explicit `null`, and non-null replacement are distinct.
- Omission preserves existing editable draft authority.
- Explicit null clears the editable draft authority.
- Non-null replacement writes the full normalized object only after validation.
- Invalid shape returns typed `400`/no-write; stale CAS/source signature/currentness returns typed `409`/no-write.
- Response DTOs must round-trip the normalized effective object (`duration_value`, `duration_unit`, `normalized_hours`, source identity, lineage/fingerprint, status/diagnostic) for source preview, editable draft, and confirmed Matrix summary where applicable.
- Confirm Matrix response and Fee draft single-build source context must bind the same confirmed authority fingerprint; no second provider read may be introduced to fetch duration facts.
- Frontend May Touch is limited to `frontend/src/api/client.ts` type-only DTO/client updates unless a later Reviewer gate proves a specific Matrix component compile failure. No visual component, Fee frontend, or hydration change is authorized in Child 2.

### Oversized File Strategy / Current Counts

The current effective blank-inclusive physical-line command is:

`(Get-Content <path> -Encoding UTF8).Count`

Current checked-out facts by that command:

- `backend/infrastructure/storage/database.py` = `990`; prior `939` was the superseded non-blank `Measure-Object -Line` count.
- `backend/application/project_matrix_draft_persistence_service.py` = `507`; prior `448` was the superseded non-blank `Measure-Object -Line` count.
- `backend/api/routes_project_matrix_drafts.py` = `600`; prior `525` was the superseded non-blank `Measure-Object -Line` count.
- `backend/application/confirmed_matrix_fee_draft_service.py` = `479`; prior `451` was the superseded non-blank `Measure-Object -Line` count.

Mandatory line strategy before any Child 2 implementation:

- `database.py`: must first be mechanically split. Move existing non-Base bootstrap/migration responsibilities into bounded modules `backend/infrastructure/storage/database_general_migrations.py` (`<=430` target), `backend/infrastructure/storage/database_matrix_migrations.py` (`<=430` target), and new `backend/infrastructure/storage/matrix_duration_authority_schema.py` (`<=260` target). `database.py` must keep only `Base`, URL/engine/session factory, `init_db`, and narrow calls to the migration runners, final `<=180` lines. Behavior-preserving regression: full existing storage/bootstrap tests plus disposable duration-authority migration tests.
- `project_matrix_draft_persistence_service.py`: current `507` is already over the hard limit by the blank-inclusive command. It must be mechanically split before any duration behavior. Move `_resolve_selected_group_keys`, `_build_draft_snapshot`, `_build_updated_snapshot`, `_normalized_group`, `_normalized_row`, `_normalize_optional_text`, and future duration authority normalization/serialization dispatch into `backend/application/project_matrix_duration_authority_payload.py` or a sibling bounded payload-builder module (`<=320` target); final service `<=430`.
- `routes_project_matrix_drafts.py`: must first be mechanically split. Move request/response DTO classes `ProjectMatrixDraftCreateRequest` through `ConfirmedMatrixSnapshotResponse` to `backend/api/project_matrix_draft_dtos.py` (`<=280` target), and move `_to_response` / `_to_confirmed_response` to `backend/api/project_matrix_draft_response_mappers.py` (`<=240` target). Route module final `<=360` before adding duration field handling.
- `confirmed_matrix_fee_draft_service.py`: current `479` has no safe headroom. The B5 split to `backend/application/confirmed_matrix_fee_draft_line_builder.py` is mandatory before transport changes; final service `<470` after split and transport.

No blank-line suppression may be used to pass line gates.

## Future May Touch

- `backend/domain/source_matrix_models.py`: additive typed duration authority field/model only.
- `backend/domain/project_matrix_draft_models.py`: additive editable draft duration authority field/model only.
- `backend/domain/confirmed_matrix_authority_models.py`: additive confirmed duration authority field/model only.
- `backend/infrastructure/storage/models_matrix_source.py`, `backend/infrastructure/storage/models_project_matrix_draft.py`, `backend/infrastructure/storage/models_confirmed_matrix_authority.py`, `backend/infrastructure/storage/database.py`, `backend/infrastructure/storage/database_general_migrations.py`, `backend/infrastructure/storage/database_matrix_migrations.py`, and `backend/infrastructure/storage/matrix_duration_authority_schema.py`: additive duration-authority shape/migration/bootstrap plus required mechanical split only; disposable DB validation required; no destructive rewrite.
- `backend/infrastructure/storage/repositories/source_matrix_import.py`, `backend/infrastructure/storage/repositories/project_matrix_draft.py`, and `backend/infrastructure/storage/repositories/confirmed_matrix_authority.py`: round-trip typed authority fields only.
- `backend/application/source_matrix_import_builder.py`, `backend/application/project_matrix_draft_persistence_service.py`, `backend/application/project_matrix_duration_authority_payload.py`, and `backend/application/project_test_plan_matrix_edit_service.py`: structured authority producer/normalizer/serializer only; no free-text duration inference in Fee.
- `backend/application/matrix_import_draft_builder.py`: selected-only source-to-draft authority remapping. It may copy only validated source authority entries whose source group/row identities map to selected draft group/row identities; unselected or missing identities fail closed before persistence.
- `backend/application/confirmed_matrix_authority_service.py`: first Confirm Matrix draft-to-confirmed authority remapping in the same snapshot transaction.
- `backend/application/matrix_revision_flow_service.py` and new `backend/application/matrix_revision_snapshot_builder.py`: confirmed-to-revision-draft carry-forward and revision-draft-to-confirmed publication. The split is mandatory before duration behavior: move `_build_revision_draft_from_active`, `_build_confirmed_snapshot_from_revision_draft`, `_validate_draft_schedule`, `_normalize_optional_text`, and `_utc_now` to the bounded builder; keep store protocols, commands, active/currentness checks, and transaction orchestration in the service. Final service target `<=280`; builder target `<=380`; both must remain `<500`.
- `backend/application/matrix_editor_session_service.py`, new `backend/application/matrix_editor_session_contracts.py`, `backend/application/matrix_editor_session_projection.py`, `backend/application/matrix_editor_session_signature.py`, `backend/application/matrix_editor_confirmed_snapshot_builder.py`, `backend/application/matrix_editor_session_publication.py`, and `backend/application/matrix_editor_session_draft_state.py`: source-replacement/first/revision publication, draft state, canonical signatures, and behavior-preserving mechanical split only. The current `1901`-line service must be split before duration behavior: contracts/protocols/dataclasses move to `matrix_editor_session_contracts.py`; draft/source/manual projections move to `matrix_editor_session_projection.py`; schedule validation, canonical draft/confirmed/source signatures, expected-token helpers, and source-lineage comparisons move to `matrix_editor_session_signature.py`; `_build_confirmed_snapshot_from_session_draft` plus its pure normalization/time helpers move to `matrix_editor_confirmed_snapshot_builder.py`; fee-promotion and `_publish_*` methods move behind `matrix_editor_session_publication.py`; draft lookup/token/save/currentness helpers move behind `matrix_editor_session_draft_state.py`. The public service keeps seed/save/discard/confirm orchestration and compatibility re-exports. Final service target `<=450`; every new module target `<=380`; all Python files must remain `<500`.
- `backend/api/routes_project_test_plan_matrix_edit.py`, `backend/api/routes_project_matrix_drafts.py`, `backend/api/project_matrix_draft_dtos.py`, and `backend/api/project_matrix_draft_response_mappers.py`: typed request/response DTO additions, response mapping, field-presence sentinel, and validation errors only.
- `backend/api/routes_matrix_editor_session.py`, new `backend/api/matrix_editor_session_dtos.py`, and new `backend/api/matrix_editor_session_response_mappers.py`: Matrix Editor seed/save/confirm duration-authority request/response transport only. The current `556`-line route must first move its request/response DTOs and pure mappers into the bounded modules; final route target `<=360`, DTO module target `<=260`, mapper target `<=220`.
- `frontend/src/api/client.ts`: type-only DTO/client contract update for the structured duration-authority collection.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`: non-visual data-preservation hunk only. Existing draft-to-session/save/confirm payload mapping must retain normalized `duration_authorities`; no new control, copy, layout, state machine, or inference is authorized.
- `backend/application/confirmed_matrix_fee_duration_authority.py` (`<500` lines): confirmed owning-row typed duration authority consumer/helper.
- `backend/application/confirmed_matrix_fee_draft_line_builder.py` (`<500` lines, target `<=260`): mandatory behavior-preserving split target.
- `backend/application/confirmed_matrix_fee_draft_service.py`: post-split orchestration/import/transport hunk only; final `<470`.
- `backend/modules/fee_evaluation/fee_default_fill_models.py`: bounded `FeeDurationAuthority` context DTO only.
- `backend/modules/fee_evaluation/fee_default_fill.py`; final file `<500`, split before implementation if needed.
- `backend/modules/fee_evaluation/fee_default_fill_common.py`.
- Future frontend tests may be added only for API client/Matrix editor field round-trip if required by the DTO update; no visual redesign or Fee frontend hydration belongs to Child 2.
- `tests/unit/test_fee_default_fill_explicit_hour_authority.py` (`<500` lines): Salt Spray and approved High temperature Life explicit-hour authority, invalid-hour matrix, rejected aliases, and no arbitrary text/legacy fallback.
- `tests/unit/test_fee_default_fill_temperature_rise_units.py` (`<500` lines): Temperature Rise sample Units while current is pending, valid/invalid sample quantity, manual-field preservation.
- `tests/unit/test_confirmed_matrix_fee_duration_authority.py` (`<500` lines): identity, lineage, unit normalization, invalid matrix, and no fallback.
- `tests/integration/test_matrix_typed_duration_authority_round_trip_api.py` (`<500` lines): import/edit/confirm persistence/API round-trip, per-group collection semantics, singleton fan-out rejection/allowance rules, SQLite non-null suffix uniqueness, and legacy-null compatibility.
- `tests/unit/test_matrix_duration_authority_projection.py` (`<500` lines): selected-only source-to-draft remapping, first confirmation, revision carry-forward, revision confirmation, and missing/unselected identity fail-closed behavior.
- `tests/unit/test_matrix_duration_authority_session_signature.py` (`<500` lines): canonical authority ordering in draft/confirmed/source signatures, omission/null/replacement preservation, stale-token detection, and source-replacement carry-forward.
- `tests/integration/test_matrix_duration_authority_publication_api.py` (`<500` lines): first Confirm, revision Confirm, Matrix Editor source replacement, transaction rollback/no-write, and immediate response/reload round-trip.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.durationAuthority.test.tsx`: bounded non-visual regression proving seed-to-save/confirm payload preservation and no mutation of authority data.
- `tests/integration/test_confirmed_matrix_fee_draft_dependent_fields_api.py` (`<500` lines): confirmed Matrix draft API/service composition, single/multi-Group isolation, no cross-Group duration, no readings multiplier, plain CONTACT RESISTANCE no LLCR fallback.
- `tests/integration/test_fee_default_fill_dependent_fields_v2_rebase.py` (`<500` lines): TASK_361L/TASK_363D V2 attestation/currentness/reviewed rebase/CAS no-write regression for Child 2 automatic non-Base-Fee fields and manual preservation.

## Must Not Touch

- Existing oversized `tests/unit/test_fee_default_fill.py`, `tests/unit/test_confirmed_matrix_authority_service.py`, `tests/unit/test_matrix_editor_session_service.py`, and `tests/integration/test_matrix_editor_session_api.py` except read-only execution; no new assertions or fixture edits in those files for Child 2.
- Base Fee policy helper and rule-resolution helper except read-only dependency checks.
- Pricing-draft route, Fee frontend model/page/tests, visual UI redesign, seeds/manifest, real DB/files, stage/commit/push.

## Validation Gate

Future validation must cover additive typed duration authority migration/bootstrap, API/model/client serialization, import/edit/confirm round-trip, legacy rows without typed authority manual-review/no-write, selected temperature/default-field contract, Salt Spray explicit hours, approved High temperature Life explicit hours, invalid hour authority, rejected temperature aliases, Temperature Rise pending-current Units, single/multi-Group isolation, existing MFG/DWV/IR/LLCR/CR no-regression, V2 attestation/currentness/rebase/CAS no-write, `py_compile`, and line-count gates. Base Fee value and metadata are read-only accepted Child 1 baseline in these tests.

## Stop Point

Historical authorization checkpoint (superseded by Reviewer B1): Reviewer scope and implementation-readiness re-gate passed, and User explicitly authorized Child 2 product implementation. Developer then completed that implementation. Child 3 and the twelve-path umbrella remained blocked.

## Final Authorization Reconciliation

On 2026-07-24, Planner reconciled the passed Reviewer scope/readiness gate and explicit User product approval. Authorization is limited to the complete typed duration-authority transport, frozen mandatory mechanical splits, bounded tests, and hunk-level May Touch in this task and plan.

Confirm Matrix remains the publication boundary. Fee consumes only confirmed owning-row authority from the same authority build. Child 2 cannot infer duration from text, legacy Step quantities, readings, Point Profile, LLCR/CR, or another row/Group, and cannot write, recalculate, or re-attest Child 1 Base Fee value or metadata. TASK_361L/TASK_363D protections and manual-field preservation remain authoritative. Child 3 and the parent umbrella remain blocked.

## Reviewer B1 Tests-Only Scope Reconciliation

Reviewer B1 passed the production routing and locked all Child 2 product code. Only `fee_rule_high_temperature_life` and `fee_rule_salt_spray_nss` use typed confirmed duration authority. `fee_rule_pre_high_temperature_life`, `fee_rule_thermal_shock`, `fee_rule_temperature_humidity`, and `fee_rule_vibration` retain accepted legacy behavior.

The bounded tests-only fix is limited to these exact existing assertion nodes:

1. `tests/unit/test_fee_default_fill.py::test_temperature_named_duration_rules_default_base_fee_to_zero_without_duration[fee_rule_high_temperature_life-Temperature life-unit_price0]`.
2. `tests/unit/test_fee_default_fill.py::test_salt_spray_uses_hour_duration_from_matrix_condition`.
3. `tests/unit/test_confirmed_matrix_fee_draft_service.py::test_fee_draft_defaults_non_rise_temperature_items_to_per_hour[Long-term high temperature zone load]`.
4. `tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py::test_approved_temperature_alias_uses_hours_and_common_base_fee[1]`.
5. `tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py::test_approved_temperature_alias_uses_hours_and_common_base_fee[2]`.
6. `tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py::test_approved_temperature_alias_without_hours_keeps_dependencies_pending`.

Items 4 and 5 are the two parameterized cases of one assertion location; the scope therefore remains five exact assertion locations.

Each migrated expectation must enforce the accepted Child 2 contract: without typed confirmed owning-row duration authority, High-temperature/Salt Spray is typed manual-review/no-write and cannot use condition/text fallback; only valid owning-row authority may produce Units and Testing Fee; missing or invalid authority diagnostics must identify the confirmed typed duration authority requirement.

No other fixture or assertion may change. In particular, Temperature & Humidity remains an unchanged B1 regression guard. Current blank-inclusive physical lines are `test_fee_default_fill.py=912`, `test_confirmed_matrix_fee_draft_service.py=683`, and `test_confirmed_matrix_fee_draft_rule_resolution.py=301`; the oversized files must not increase, with line-neutral assertion replacement preferred. Any additional coverage belongs only in already approved bounded modules.

Historical B2 note: the external TASK_366C `method_authority` dependency-composition residual was excluded from Child 2. Its owner has since restored the composition, and Reviewer closed the original Pydantic/composition failures. It is not the current QA blocker. Child 3 and the umbrella remain blocked.

Historical High/Salt tests-only route (completed): Developer bounded tests-only fix followed by Reviewer re-gate. Product code remained locked.

## External Fee-Rebase Fixture Ownership Reconciliation

The preceding High-temperature/Salt Spray tests-only fix is complete and Reviewer passed it. Child 2 product code remains locked.

The sole QA blocker is now:

`tests/integration/test_matrix_editor_session_api.py::test_matrix_editor_session_autosave_restore_confirm_and_discard`

Read-only tracing proves this is a stale fixture-context issue:

- `_seed_previous_pricing_draft()` writes `fee_rule_version_id="fee_rules_v2026_06_03"`;
- the exact test later queries the promoted draft with the same obsolete id;
- Matrix Editor pending rebase correctly requests the accepted active rule context `fee_rules_v2026_07_17_r6`;
- exact-context lookup therefore returns no source pricing draft and `preserved_count=0`;
- an in-memory disposable replay replacing only both old literals with the accepted r6 id passed the full test node.

This is not a Child 2, TASK_366C, or Matrix/Fee rebase production defect. TASK_361L/TASK_363D require exact Matrix/rule/source context and fail-closed no-fallback behavior.

Proposed tests-only scope, pending Reviewer confirmation:

- May Touch only `tests/integration/test_matrix_editor_session_api.py`;
- exact hunk only the two `fee_rules_v2026_06_03` literals inside `_seed_previous_pricing_draft()` and the promoted-draft lookup in the named test;
- replace both with accepted active `fee_rules_v2026_07_17_r6`;
- no assertion, pricing values, manual note, summary, fixture identity, product, CAS, provenance, rebase algorithm, or fallback change;
- preserve the current `1107` blank-inclusive physical-line count through line-neutral replacement.

`preserved_count` means the count of source Fee rows matched to target Matrix rows by stable rebase key under an exact current Matrix/rule context. It does not count manual fields. Under a context mismatch, `0` and no fallback are correct. Under exact context, current automatic defaults remain authoritative and only proven compatible manual fields may survive; Testing Fee remains derived. TASK_361L/TASK_363D currentness, attestation, reviewed rebase, CAS/no-write, and load/Cancel zero-write remain unchanged.

Next legal role: Reviewer tests-only scope confirmation. Developer is not yet authorized for this fixture migration. Child 3 and the umbrella remain blocked.

## Integrator Closeout

The final Reviewer re-gate and QA gate passed on 2026-07-24. The controlled
package contains only the approved typed duration-authority transport,
bounded regression coverage, and the four authorized line-neutral r3-to-r6
fixture literals. Child 1 remains read-only; Child 3 and the parent umbrella
remain blocked. Remote push is not authorized.
