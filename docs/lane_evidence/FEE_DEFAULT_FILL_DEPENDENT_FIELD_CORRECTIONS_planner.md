# FEE_DEFAULT_FILL_DEPENDENT_FIELD_CORRECTIONS Planner Evidence

Date: 2026-07-24
Role: Planner
Status: `reviewer_pass_qa_blocked_by_stale_fee_rebase_fixture_pending_reviewer_scope_confirmation`

Created as Child 2 of the Fee/default-fill residual umbrella. User clarified the final Child 1 Base Fee contract: every Fee line uses manual Base Fee first, explicit accepted rule-specific Base Fee second, otherwise automatic Base Fee `0`; single-Group and multi-Group use identical precedence.

Child 1 `FEE_RULE_RESOLUTION_MATRIX_BASE_FEE_POLICY` is complete/accepted at local commit `c5d91c36c5e1d54885fc0a3b406c92ff9aa0cb6b` (`feat(fee): resolve matrix base fee policy`), verified as a HEAD ancestor. That accepted baseline releases Child 2's metadata/default precedence dependency.

Implementation is authorized for Child 2 only after Reviewer scope/readiness passed and User explicitly approved product implementation.

## Dependency-Release Source Of Truth

- Reviewer/QA/Integrator accepted Child 1; Child 1 is now read-only baseline for Child 2.
- Reviewer plan/dependency-release re-gate passed, User approved Developer docs-only planning-first, and Developer planning-first is complete.
- Reviewer scope and implementation-readiness re-gate passed.
- Historical authorization route (completed): User explicitly authorized Child 2 product implementation and Developer completed it before Reviewer B1.
- Child 3 remains blocked until Child 1 and Child 2 metadata/default contracts are both accepted.
- The twelve-path umbrella is planning evidence only and is not an implementation authorization.

## Frozen Child 2 Boundary

- Child 2 may plan dependent-field corrections and approved temperature-duration behavior.
- Base Fee final value and metadata are owned exclusively by accepted Child 1. Child 2 consumes them read-only and must not write, recalculate, classify, or re-attest Base Fee.
- Missing/invalid duration leaves Units and Testing Fee unset/Pending/review-required with accurate typed diagnostics; it does not write Base Fee.
- Only `Long-term high temperature zone load` maps to High temperature Life at `15/per hour`, with Units from explicit hour authority; missing/invalid hours stay typed review/no-write.
- `Long-term temperature cycle with load` and `Long-term damp heat` remain no-rule/manual-review.
- Plain `CONTACT RESISTANCE` must not fallback to LLCR.
- Child 2 must not redefine Base Fee precedence or use `matrix_group_count` as a Base Fee trigger.
- Manual Unit Price, Units, Base Fee, discount, notes, and spend time remain protected.
- TASK_361L/TASK_363D attestation/currentness/reviewed rebase/CAS/no-write remain authoritative.

## Reviewer B1-B3 Docs-Only Fix

Planner closed the Reviewer B1-B3 governance blockers as follows:

- Removed the prior B1-overlap wording and froze Child 2 as having no Base Fee write/metadata ownership.
- Froze accepted Child 1 as the exclusive Base Fee value/metadata owner. Child 2 only reads the final accepted Child 1 Base Fee outcome when deriving Testing Fee from safe fields.
- Froze explicit hour authority: a single positive finite numeric duration from structured/typed owning-row data, with hour-compatible unit normalized to hours. Zero, negative, NaN, Infinity, non-numeric, unsupported unit, conflicting/multiple values, missing/stale lineage or fingerprint, wrong row/group, and unbound source are invalid typed no-write.
- Forbid inference from arbitrary free text, other rows/groups, readings, Point Profile, legacy fallback, LLCR/CR authority, or stale saved draft values.
- Froze the approved 15/hour behavior for `Long-term high temperature zone load`: Unit Price `15`, Unit Type `per hour`, Units equal normalized explicit hours, Testing Fee derived from Unit Price, Units, accepted Child 1 final Base Fee, and discount.
- Froze exact bounded test modules:
  - `tests/unit/test_fee_default_fill_explicit_hour_authority.py`
  - `tests/unit/test_fee_default_fill_temperature_rise_units.py`
  - `tests/integration/test_confirmed_matrix_fee_draft_dependent_fields_api.py`
  - `tests/integration/test_fee_default_fill_dependent_fields_v2_rebase.py`
- Existing oversized `tests/unit/test_fee_default_fill.py` remains read-only regression execution only.

## B3-B5 Discovery / Re-Scope Result

Read-only code discovery confirmed the Reviewer B3 concern:

- `FeeDefaultFillContext` currently exposes text fields, sample quantity, step tokens/quantities, and CR authority, but no typed duration value/unit, row identity, lineage, fingerprint, or diagnostic.
- `ConfirmedMatrixFeeDraftService._calculate_line()` builds that context directly from owning `ConfirmedMatrixRow` text fields.
- Current duration behavior scans combined text, which cannot satisfy the strict typed owning-row authority contract.
- `ConfirmedMatrixFeeAuthorityBuildResult` already provides the single-build boundary for draft, confirmed Matrix, rule library, effective Measurement Plan, and Point Profile facts; TASK_363D attestation binds automatic defaults and row safety but does not create row-level duration facts.

Reviewer B4 required checking whether the authority fact exists before authorizing helper/DTO/transport. Planner rechecked the actual upstream:

- Source Matrix snapshots persist condition/requirement text and group tokens; no typed duration value/unit/source identity/lineage is stored.
- Editable and confirmed Matrix row models persist `condition`, `requirement`, and `day_expression`, but not typed duration value/unit/source identity/lineage.
- The Matrix edit route accepts compatibility fields such as `duration_value`, `duration_unit`, and `estimated_duration_hours`, but those are not published as confirmed Matrix authority.
- Measurement Plan and Point Profile authorities cover contact/readings data, not temperature duration.

Current conclusion from B4 remains: no existing legal non-text authority source exists for the strict owning-row duration contract. The earlier Option A helper/DTO/transport wording is superseded.

User/Orchestrator approved Option 1. Planner now freezes an additive typed duration authority contract/producer/persistence/API/model boundary for Reviewer re-gate:

- fields: `duration_value`, `duration_unit`, `normalized_hours`, owning group/row/sequence/suffix identity, source identity, revision/fingerprint/lineage, and diagnostic/status;
- producer: Matrix import/edit/confirmation chain only; Confirm Matrix remains publication; Fee draft consumes confirmed owning-row authority only;
- legacy rows: missing typed authority means typed manual-review/no-write;
- forbidden: Fee-layer scans of `condition`, `requirement`, `day_expression`, arbitrary free text, legacy Step quantity, readings, Point Profile, LLCR/CR authority, stale draft values, or another row/Group;
- units: `hour`, `hours`, `hr`, `hrs`, `day`, and `days`, with day(s) converted to hours by `* 24`; zero/negative/NaN/Infinity/non-numeric/unsupported/conflict/multiple/stale/missing/wrong-row are typed no-write.

Reviewer B5 also required a concrete service split. Current checked-out `backend/application/confirmed_matrix_fee_draft_service.py` is `479` blank-inclusive UTF-8 physical lines by `(Get-Content <path> -Encoding UTF8).Count`; the prior `451` line fact was a superseded non-blank `Measure-Object -Line` count.

Frozen mechanical split for any future approved Child 2 transport:

- New module `backend/application/confirmed_matrix_fee_draft_line_builder.py` (`<500`, target `<=260`).
- Move existing `_build_groups`, `_build_cell_lookup`, `_build_group_lines`, `_missing_point_profile`, `_build_line_item`, `_calculate_line`, `_review`, and `_no_rule_match` from `confirmed_matrix_fee_draft_service.py`.
- Leave `ConfirmedMatrixFeeDraftService` with provider reads, top-level authority build orchestration, warnings/header/status/totals/manual report line, and `ConfirmedMatrixFeeAuthorityBuildResult`.
- Behavior must be unchanged before any duration behavior; Base Fee, LLCR, CR specified-current, Point Profile, Measurement Plan, rule resolution, and V2 attestation remain locked.
- Final `confirmed_matrix_fee_draft_service.py` after split and any later approved transport must be `<470` UTF-8 physical lines including blanks; no blank-line suppression.

Exact re-scoped May Touch now includes additive Matrix/source/confirmed domain, storage, repositories, Matrix edit/confirm API DTOs, optional `frontend/src/api/client.ts` type-only update, the duration authority helper, the mandatory line-builder split, default-fill context/default-fill modules, and bounded tests/disposable DB validation. Fee frontend hydration, pricing-draft route, seeds/manifest, Base Fee policy/rule-resolution production, real DB/files, and Child 3 remain locked.

## B6-B8 Refinement

Reviewer B6-B8 required the typed duration authority producer, persistence, API/model, and hard line-budget contracts to be executable before plan/dependency-release re-gate. Planner froze the following current source-of-truth:

- Structured producer input is only a field-presence-aware per-group `duration_authorities` collection on source-import row payloads and Matrix edit row commands.
- Each collection entry contains `duration_value`, `duration_unit`, owning group/row id or key, `step_sequence`, canonical non-null `step_suffix_note`, `source_field`, `source_kind`, and `source_identity`; derived/persisted facts include `normalized_hours`, source/revision/fingerprint/lineage, status, and diagnostic.
- Omitted preserves existing editable draft authority collection; explicit `null` clears it; non-null replacement is full-collection validation/replacement only.
- Import Replace may only carry structured authority; manual Matrix edit may only set/clear through the structured field; Confirm Matrix is the sole publication boundary. Unconfirmed draft authority is never Fee authority.
- Invalid shape/type/unit/value is typed `400`/no-write; stale CAS/currentness/source signature, row identity mismatch, or divergent/conflicting values are typed `409`/no-write.
- Producers and Fee consumers are explicitly forbidden to parse `condition`, `requirement`, `day_expression`, test item/method prose, legacy Step quantities, readings, Point Profile, Measurement Plan contact authorities, LLCR/CR authorities, saved Fee draft values, files, or arbitrary text.
- Singular row-level authority is not a persisted contract. Any convenience fan-out is legal only for a singleton owning group/sequence/suffix projection; otherwise it is typed `409`/no-write. Identical values across groups require explicit per-group entries.

Persistence is frozen to three dedicated additive tables:

1. `source_matrix_duration_authorities`
2. `project_matrix_draft_duration_authorities`
3. `confirmed_matrix_duration_authorities`

Each table has adapted parent/group/row id columns, `step_sequence INTEGER NOT NULL`, `step_suffix_note TEXT NOT NULL DEFAULT ''`, `duration_value NUMERIC NOT NULL`, `duration_unit TEXT NOT NULL`, `normalized_hours NUMERIC NOT NULL`, `source_kind TEXT NOT NULL`, `source_field TEXT NOT NULL`, `source_import_id TEXT NULL`, `source_fingerprint TEXT NOT NULL`, `lineage_fingerprint TEXT NOT NULL`, `authority_revision TEXT NOT NULL`, `status TEXT NOT NULL`, nullable diagnostic fields, and `created_at` / `updated_at TEXT NOT NULL`. Each table must have a unique owning-row identity using the non-null canonical suffix; SQLite NULL unique-key semantics are forbidden. Marker `matrix_duration_authority_v1` gates zero-shape upgrade, partial-shape fail-close, read-verify, rollback, and idempotent repeated init.

API/model freezes a field-presence sentinel, normalized round-trip responses, typed `400/409`, source snapshot/signature/CAS binding, same-build Fee consumption, and no second provider read. Frontend May Touch is only `frontend/src/api/client.ts` type-only unless a later Reviewer gate identifies an exact Matrix compile failure.

Current line facts now use the single blank-inclusive physical-line command `(Get-Content <path> -Encoding UTF8).Count`:

- `backend/infrastructure/storage/database.py` = `990`; prior `939` was the superseded non-blank `Measure-Object -Line` count.
- `backend/application/project_matrix_draft_persistence_service.py` = `507`; prior `448` was the superseded non-blank `Measure-Object -Line` count.
- `backend/api/routes_project_matrix_drafts.py` = `600`; prior `525` was the superseded non-blank `Measure-Object -Line` count.
- `backend/application/confirmed_matrix_fee_draft_service.py` = `479`; prior `451` was the superseded non-blank `Measure-Object -Line` count.

Mandatory size strategy:

- Split `database.py` into `database_general_migrations.py`, `database_matrix_migrations.py`, and `matrix_duration_authority_schema.py`; final `database.py <=180`.
- Split `project_matrix_draft_persistence_service.py` before duration behavior because it is already `507` blank-inclusive lines. Move `_resolve_selected_group_keys`, `_build_draft_snapshot`, `_build_updated_snapshot`, `_normalized_group`, `_normalized_row`, `_normalize_optional_text`, and duration dispatch into `project_matrix_duration_authority_payload.py` or a sibling bounded payload-builder; final service `<=430`.
- Split `routes_project_matrix_drafts.py` into `project_matrix_draft_dtos.py` and `project_matrix_draft_response_mappers.py`; route final `<=360`.
- Split `confirmed_matrix_fee_draft_service.py` into the already frozen `confirmed_matrix_fee_draft_line_builder.py`; final service `<470`.

Historical B6-B11 checkpoint: no blank-line suppression was allowed, Child 1 remained read-only, Child 3 and the umbrella remained blocked, and Developer planning-first/implementation were not yet authorized.

That pre-readiness route is superseded: Developer planning-first completed, Reviewer scope/readiness passed, and User product authorization is now recorded in the Final Authorization Reconciliation.

## Developer Planning-First Source-Of-Truth Reconciliation

Developer read-only call-flow inspection proved that the earlier May Touch list
did not cover all legal authority publication paths. Planner independently
confirmed the checked-out owners and rejects fail-closed workflow exclusion:

- `matrix_import_draft_builder.py` maps selected source ids to draft ids;
- `confirmed_matrix_authority_service.py` owns first Confirm publication;
- `matrix_revision_flow_service.py` owns confirmed-to-draft carry-forward and
  revision confirmation;
- `matrix_editor_session_service.py` owns source-replacement publication,
  saved-payload signatures, and session draft persistence.

The exact additional May Touch and mandatory split modules are now frozen in
the task and plan. Current blank-inclusive counts are `152`, `310`, `491`,
`1901`, and `556` respectively for the import builder, first-confirm service,
revision service, Matrix Editor service, and Matrix Editor route. The revision
builder split targets service `<=280` and helper `<=380`. The Matrix Editor
split moves contracts, projections, signatures, confirmed snapshot building,
publication, and draft-state helpers to six bounded modules; its public service
must finish `<=450`. The Matrix Editor route must split DTOs/mappers and finish
`<=360`.

`frontend/src/api/client.ts` is type-only. `MatrixEditorWorkspace.tsx` is
allowed only to preserve normalized `duration_authorities` through its explicit
seed/save/confirm row mapping. No visual, copy, interaction, or state-machine
change is authorized. This boundary follows the loaded `$impeccable` product
context and frontend architecture rules.

New bounded projection, signature, publication API, and frontend preservation
tests own the new assertions. Existing oversized authority/session/default-fill
tests remain read-only regression execution. Child 1 remains accepted and
read-only; Child 3 and the umbrella remain blocked.

## Final Authorization Reconciliation

Reviewer scope and implementation-readiness re-gate passed on the frozen
transport and split contract. User then explicitly authorized Child 2 product
implementation. Current status is `implementation authorized / pending
Developer implementation`.

Authorization is limited to the task/plan exact May Touch, complete structured
duration-authority transport, mandatory behavior-preserving splits, bounded
tests, disposable validation, and mixed-file hunk isolation. Confirm Matrix is
the publication boundary; confirmed owning-row same-build consumption is the
only Fee authority. No text/legacy/contact/other-row fallback is allowed.
Accepted Child 1 Base Fee value/metadata is read-only. TASK_361L/TASK_363D and
manual-field safeguards remain authoritative. Child 3 and the umbrella remain
blocked.

## Reviewer B1 Tests-Only Scope Reconciliation

Reviewer B1 passed Child 2 production routing and locked all product code.
Planner authorizes only five exact legacy assertion locations, comprising six
pytest cases because the approved temperature alias node has `[1]` and `[2]`
parameters:

- `test_fee_default_fill.py::test_temperature_named_duration_rules_default_base_fee_to_zero_without_duration[fee_rule_high_temperature_life-Temperature life-unit_price0]`;
- `test_fee_default_fill.py::test_salt_spray_uses_hour_duration_from_matrix_condition`;
- `test_confirmed_matrix_fee_draft_service.py::test_fee_draft_defaults_non_rise_temperature_items_to_per_hour[Long-term high temperature zone load]`;
- `test_confirmed_matrix_fee_draft_rule_resolution.py::test_approved_temperature_alias_uses_hours_and_common_base_fee[1]` and `[2]`;
- `test_confirmed_matrix_fee_draft_rule_resolution.py::test_approved_temperature_alias_without_hours_keeps_dependencies_pending`.

Only stale High-temperature/Salt Spray text-fallback and diagnostic expectations
may be migrated. Missing typed confirmed owning-row authority must remain
manual-review/no-write; valid owning-row authority alone may produce Units and
Testing Fee. Temperature & Humidity and every other legacy behavior/assertion
remain locked.

Current blank-inclusive file counts are `912`, `683`, and `301`. Existing
oversized files cannot increase; line-neutral replacement is preferred, and
new coverage can use only approved bounded modules. Product code is locked.

Historical B2 note: the TASK_366C-owned `method_authority` composition defect
was excluded from Child 2. Its owner subsequently repaired it and Reviewer
closed the original composition/Pydantic failures. It is not the current QA
blocker. Child 3 and the umbrella remain blocked. The High/Salt tests-only route
also completed and Reviewer passed it.

## External Fee-Rebase Fixture Ownership Reconciliation

Read-only tracing classifies the sole remaining Matrix Editor lifecycle failure
as stale fixture context:

- the fixture seeds and queries `fee_rules_v2026_06_03`;
- the runtime correctly requests accepted active `fee_rules_v2026_07_17_r6`;
- exact-context lookup therefore has no source row and reports
  `preserved_count=0`;
- an in-memory disposable replay replacing only both obsolete literals with r6
  passed the complete exact node.

This is not Child 2 or TASK_366C production ownership. Cross-rule-version
fallback would violate TASK_361L/TASK_363D.

Proposed May Touch is test-only and pending Reviewer confirmation:
`tests/integration/test_matrix_editor_session_api.py`, exact node
`test_matrix_editor_session_autosave_restore_confirm_and_discard`, and only the
two obsolete rule-version literals in `_seed_previous_pricing_draft()` and the
promoted-draft lookup. Replacement is line-neutral with accepted r6; the file
remains `1107` lines. Assertions, pricing values, manual note, product code,
rebase behavior, provenance, CAS, and fallbacks remain locked.

`preserved_count` counts exact-context source-row identity matches, not manual
fields. Automatic defaults refresh; only proven manual provenance survives;
context mismatch remains fail-closed/no-write. Child 3 and the umbrella remain
blocked.

Next legal role: Reviewer tests-only scope confirmation. Do not route Developer
until Reviewer confirms this exact fixture migration.
