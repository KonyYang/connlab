# FEE_DEFAULT_FILL_DEPENDENT_FIELD_CORRECTIONS Dependency Release Reconciliation - Planner Evidence

Date: 2026-07-24
Role: Planner
Status: `reviewer_pass_qa_blocked_by_stale_fee_rebase_fixture_pending_reviewer_scope_confirmation`
Task: `FEE_DEFAULT_FILL_DEPENDENT_FIELD_CORRECTIONS`
Lane: `fee-default-fill-dependent-field-corrections`
Parent: `FEE_DEFAULT_FILL_RESIDUAL_PACKAGE_RECONCILIATION`

## Current Gate

The User/Orchestrator requested a docs-only Planner dependency-release and source-of-truth reconciliation for Child 2 after Child 1 acceptance.

Reviewer plan/dependency-release re-gate passed. User approved Developer
docs-only planning-first, and Developer planning-first is complete.

Historical dependency-release route (completed): Reviewer scope/readiness
passed, User authorized Child 2 product implementation, and Developer completed
the product candidate.

Historical route (completed): Developer bounded tests-only fix for the five
exact Reviewer-listed assertion locations. Reviewer passed that migration and
product code remains locked.

## Accepted Dependency

Child 1 `FEE_RULE_RESOLUTION_MATRIX_BASE_FEE_POLICY` is complete/accepted at local commit `c5d91c36c5e1d54885fc0a3b406c92ff9aa0cb6b` (`feat(fee): resolve matrix base fee policy`).

Planner verified that commit is a HEAD ancestor. This releases Child 2's metadata/default precedence dependency.

Child 1 is now a read-only accepted baseline for Child 2. Child 2 must not reopen or redefine Child 1 Base Fee precedence.

## Frozen Source Of Truth For Child 2

- Manual Base Fee > explicit accepted rule-specific Base Fee > automatic Base Fee `0`, owned by accepted Child 1.
- Child 2 must not redefine or override Base Fee precedence.
- Child 2 must not use `matrix_group_count` as a Base Fee trigger.
- Child 2 may only plan dependent-field corrections and approved temperature-duration behavior.
- Base Fee final value and metadata are owned exclusively by accepted Child 1; Child 2 reads that result only and must not write, recalculate, classify, or re-attest Base Fee.
- Missing/invalid duration leaves Units and Testing Fee unset/Pending/review-required with accurate typed diagnostics and does not write Base Fee.
- Only `Long-term high temperature zone load` maps to High temperature Life at `15/per hour`.
- Units for that approved temperature row must come from explicit hour authority; missing/invalid hours remain typed review/no-write.
- `Long-term temperature cycle with load` and `Long-term damp heat` remain no-rule/manual-review.
- Plain `CONTACT RESISTANCE` must not fallback to LLCR.
- Testing Fee derives only from final safe effective Unit Price, Units, Base Fee, and discount.
- Manual Unit Price, Units, Base Fee, discount, notes, and spend time are never overwritten.
- TASK_361L/TASK_363D attestation, currentness, reviewed rebase, CAS, and no-write behavior remain authoritative.

## Explicit Hour Authority

Valid explicit hour authority must be a single positive finite numeric duration from structured/typed owning-row data with an hour-compatible unit normalized to hours. Valid authority must be bound to the current source lineage and fingerprint.

Invalid authority includes zero, negative values, NaN, Infinity, non-numeric values, empty values, unsupported units, conflicting or multiple divergent duration facts, missing lineage/fingerprint, stale lineage/fingerprint, wrong row/group source, and any source not bound to the owning Fee row.

Child 2 must not infer duration from arbitrary free text, another row or Group, readings quantity, Point Profile, legacy Matrix fallback, LLCR/CR authority, or stale saved draft values.

For `Long-term high temperature zone load` with valid explicit hour authority, Unit Price is `15`, Unit Type is `per hour`, Units equal normalized hours, and Testing Fee derives from Unit Price, Units, accepted Child 1 final Base Fee, and discount. Manual fields are never overwritten.

## Boundary

The earlier default-fill-only boundary is superseded by the User-approved
Option 1 authority producer/persistence/API/model scope and the completed
planning-first reconciliation. Exact current May Touch is controlled by the
task and plan. It includes the structured source/draft/confirmed authority
shape, repositories, bounded migration/API splits, selected source-to-draft
projection, first/revision/source-replacement publication, canonical
signatures, same-build Fee consumption, non-visual Matrix Editor payload
preservation, and bounded tests.

Locked for Child 2 at this gate:

- Child 1 accepted Base Fee product code and tests except read-only dependency
  checks and the exact Child 2 authority transport call sites named by the
  current task/plan.
- Child 3 pricing-draft/frontend hydration.
- The twelve-path umbrella package.
- Existing oversized `tests/unit/test_fee_default_fill.py`,
  `tests/unit/test_confirmed_matrix_authority_service.py`,
  `tests/unit/test_matrix_editor_session_service.py`, and
  `tests/integration/test_matrix_editor_session_api.py` except read-only
  regression execution.
- Pricing-draft route, Fee frontend model/page/tests, visual Matrix Editor
  changes, seeds/manifest, real DB/files, generated artifacts,
  stage/commit/push, and unrelated residuals.

## Validation Summary

- Verified Child 1 commit `c5d91c36c5e1d54885fc0a3b406c92ff9aa0cb6b` is a HEAD ancestor.
- Updated Child 2 task, plan, Planner evidence, umbrella task/plan/Planner evidence, and `docs/task_board.md` source-of-truth wording.
- No product code or tests were modified.
- No real DB/files/generated artifacts were accessed.
- No stage/commit/push was performed.
- Reviewer B1-B3 docs-only blockers were addressed by removing Base Fee write ownership from Child 2, freezing explicit-hour authority, and naming the exact bounded test package.

## B3 Discovery / Re-Scope Addendum

Reviewer re-gate identified that the strict typed duration authority contract is not implementable inside the earlier Child 2 May Touch list. Planner performed read-only code discovery and confirmed:

- `FeeDefaultFillContext` lacks typed duration value/unit, row identity, source lineage, fingerprint, and diagnostic.
- `ConfirmedMatrixFeeDraftService._calculate_line()` currently passes only row text, sample quantity, step tokens/quantities, and CR authority into default-fill.
- Existing duration behavior scans combined text and therefore cannot satisfy the strict authority contract.
- `ConfirmedMatrixFeeAuthorityBuildResult` and TASK_363D attestation provide the single-build and V2 binding boundary but not a row-level duration fact.

Reviewer B4 required proving a legal authority source before approving the helper/DTO/transport plan. Planner rechecked the actual source flow:

- Source Matrix row snapshots persist only text fields (`test_item`, `source_section`, `method`, `condition`, `requirement`) plus group tokens.
- Editable and confirmed Matrix row models persist `condition`, `requirement`, and `day_expression`, but no typed duration value/unit/source identity/lineage.
- Matrix edit compatibility fields (`duration_value`, `duration_unit`, `estimated_duration_hours`, and related hints) are not published as confirmed Matrix authority.
- Measurement Plan and Point Profile facts are contact/readings authorities, not temperature-duration authorities.

Current conclusion: no existing legal non-arbitrary-text duration authority exists. The prior Option A statement is superseded.

User/Orchestrator approved Option 1. The current effective Child 2 re-scope is additive typed duration authority:

- Data contract: `duration_value`, `duration_unit`, `normalized_hours`, owning group/row/sequence/suffix identity, source identity, revision/fingerprint/lineage, and diagnostic/status.
- Producer: Matrix import/edit/confirmation chain emits and persists structured authority. Confirm Matrix is the publication boundary.
- Consumer: Fee draft uses confirmed owning-row typed authority from the same single authority build only.
- Compatibility: legacy rows without typed authority produce typed manual-review/no-write for Units and Testing Fee.
- Forbidden fallback: no Fee-layer parsing of `condition`, `requirement`, `day_expression`, arbitrary free text, legacy Step quantity, readings, Point Profile, LLCR/CR authority, stale draft values, or another row/Group.
- Units: `hour`, `hours`, `hr`, `hrs`, `day`, and `days`; day(s) convert to hours by `* 24`.
- Invalid matrix: zero, negative, NaN, Infinity, non-numeric, unsupported, conflict, multiple, stale, missing, wrong-row, missing lineage/fingerprint, and malformed payload all typed no-write.

Reviewer B5 also required a concrete mechanical split. Current checked-out `backend/application/confirmed_matrix_fee_draft_service.py` is `479` blank-inclusive UTF-8 physical lines by `(Get-Content <path> -Encoding UTF8).Count`; prior `451` was the superseded non-blank `Measure-Object -Line` count. Any future approved Child 2 transport must first perform a behavior-preserving split:

- New bounded module: `backend/application/confirmed_matrix_fee_draft_line_builder.py` (`<500`, target `<=260`).
- Move existing `_build_groups`, `_build_cell_lookup`, `_build_group_lines`, `_missing_point_profile`, `_build_line_item`, `_calculate_line`, `_review`, and `_no_rule_match`.
- Keep provider reads, top-level orchestration, warnings/header/status/totals/manual report line, and `ConfirmedMatrixFeeAuthorityBuildResult` in `ConfirmedMatrixFeeDraftService`.
- Final `confirmed_matrix_fee_draft_service.py` must remain `<470` UTF-8 physical lines including blanks after split and any future approved transport hunk.

## B6-B8 Refinement Source Of Truth

Reviewer B6-B8 are addressed as docs-only refinement, not implementation authorization.

### Structured Producer Contract

- Allowed inputs are only a structured per-group `duration_authorities` collection on source-import row payloads and Matrix edit command rows.
- Non-null entry fields: `duration_value` number, `duration_unit` string, owning group/row id or key, `step_sequence`, canonical non-null `step_suffix_note`, `source_field` string, `source_kind` enum `import_structured` / `manual_edit`, and `source_identity` object.
- Derived/serialized fields: `normalized_hours`, source/revision/fingerprint/lineage, status, and diagnostic.
- Omission preserves editable draft authority collection; explicit `null` clears it; non-null replacement replaces the full authority collection after validation.
- Import Replace can use only import structured authority. Manual Matrix edit can set/clear only the structured object. Confirm Matrix is the publication boundary; draft authority is never Fee authority.
- Invalid shape/type/unit/value returns typed `400`/no-write. Stale CAS/currentness/source signature, mismatched row identity, or multiple/conflicting values return typed `409`/no-write.
- Producer/parser prohibition is absolute: no parsing of `condition`, `requirement`, `day_expression`, method/test-item prose, legacy Step quantities, readings, Point Profile, Measurement Plan contact authorities, LLCR/CR authority, saved Fee draft values, external files, or arbitrary text.
- Singular row-level authority is not persisted. Convenience fan-out is legal only for a singleton owning group/sequence/suffix projection; otherwise typed `409`/no-write. Identical duration values across groups must be explicit per-group entries.

### Persistence / Migration Contract

Dedicated additive tables:

- `source_matrix_duration_authorities`
- `project_matrix_draft_duration_authorities`
- `confirmed_matrix_duration_authorities`

Each table adapts parent/group/row id names to its ownership and includes `step_sequence INTEGER NOT NULL`, `step_suffix_note TEXT NOT NULL DEFAULT ''`, `duration_value NUMERIC NOT NULL`, `duration_unit TEXT NOT NULL`, `normalized_hours NUMERIC NOT NULL`, `source_kind TEXT NOT NULL`, `source_field TEXT NOT NULL`, `source_import_id TEXT NULL`, `source_fingerprint TEXT NOT NULL`, `lineage_fingerprint TEXT NOT NULL`, `authority_revision TEXT NOT NULL`, `status TEXT NOT NULL`, nullable diagnostics, and `created_at` / `updated_at TEXT NOT NULL`. Each table enforces unique owning-row identity using the non-null canonical suffix; SQLite NULL unique-key semantics are forbidden.

Migration marker: `matrix_duration_authority_v1`. Zero-shape upgrades run additively in one transaction; partial-shape DBs fail closed as `authority_corrupt`; the migration performs DDL, indexes, marker write, read-verify through `PRAGMA table_info` and uniqueness checks, rollback on failure, and idempotent repeated init. Legacy nullable/no-row maps to manual-review/no-write.

### API / Model / Frontend

- Field-presence sentinel distinguishes omission, explicit `null`, and replacement.
- Responses round-trip normalized authority for source preview/editable draft/confirmed Matrix where applicable.
- CAS/currentness/source snapshot/signature mismatches return typed `409`; invalid payload returns typed `400`.
- Fee draft consumption uses the same single authority build/source-context fingerprint as TASK_363D attestation; no second provider read.
- Frontend scope is `frontend/src/api/client.ts` type-only unless later Reviewer finds an exact compile failure requiring a named Matrix component.

### Current Counts And Mechanical Split

Effective blank-inclusive physical-line command: `(Get-Content <path> -Encoding UTF8).Count`.

- `backend/infrastructure/storage/database.py` = `990`; prior `939` was the superseded non-blank `Measure-Object -Line` count.
- `backend/application/project_matrix_draft_persistence_service.py` = `507`; prior `448` was the superseded non-blank `Measure-Object -Line` count.
- `backend/api/routes_project_matrix_drafts.py` = `600`; prior `525` was the superseded non-blank `Measure-Object -Line` count.
- `backend/application/confirmed_matrix_fee_draft_service.py` = `479`; prior `451` was the superseded non-blank `Measure-Object -Line` count.

Frozen split/package plan:

- `database.py`: mandatory mechanical split into `database_general_migrations.py` (`<=430`), `database_matrix_migrations.py` (`<=430`), and `matrix_duration_authority_schema.py` (`<=260`); final `database.py <=180`.
- `project_matrix_draft_persistence_service.py`: already over hard limit at `507`; mandatory split before duration behavior. Move `_resolve_selected_group_keys`, `_build_draft_snapshot`, `_build_updated_snapshot`, `_normalized_group`, `_normalized_row`, `_normalize_optional_text`, and duration dispatch into `project_matrix_duration_authority_payload.py` or a sibling bounded payload-builder; service final `<=430`.
- `routes_project_matrix_drafts.py`: mandatory split of DTO classes to `project_matrix_draft_dtos.py` (`<=280`) and response mappers to `project_matrix_draft_response_mappers.py` (`<=240`); route final `<=360`.
- `confirmed_matrix_fee_draft_service.py`: mandatory line-builder split before transport; final `<470`.

Validation additions: disposable migration/read-verify/rollback/idempotency tests, import/edit/confirm round-trip tests, API `400/409` sentinel tests, single-build V2 attestation/currentness/CAS tests, behavior-preserving split regressions, line-count gates, and `py_compile`.

## Callback

## Planning-First Scope Reconciliation

The legal Matrix workflows cannot be excluded without violating the approved
no-silent-loss and stale-signature contract. The task/plan now adds exact
hunk-level ownership for selected source-to-draft projection, first Confirm,
revision carry-forward/confirmation, Matrix Editor source replacement, saved
draft persistence, and canonical authority signatures.

Mandatory bounded splits are frozen for the current `491`-line revision
service, `1901`-line Matrix Editor service, and `556`-line Matrix Editor route.
The split names, moved symbols/responsibilities, compatibility re-exports,
final budgets, and bounded regressions are recorded in the controlling task
and plan. The Matrix Editor frontend scope is limited to DTO typing and a
non-visual seed/save/confirm payload-preservation hunk.

Historical planning-first route (superseded): Reviewer scope and
implementation-readiness re-gate for Child 2. That gate has now passed and the
User has authorized product implementation.

## Final Authorization Reconciliation

Current status is `implementation authorized / pending Developer
implementation`. The released Child 1 dependency remains read-only. Child 2
authorization includes only the exact structured duration authority transport,
mandatory splits, bounded tests, disposable validation, and hunk ownership
frozen in the task/plan.

Confirm Matrix remains the publication boundary, Fee consumes confirmed
owning-row authority from the same build only, and all forbidden fallbacks
remain no-write/manual-review. Child 2 does not modify or re-attest Base Fee.
TASK_361L/TASK_363D safeguards remain authoritative. Child 3 and the umbrella
twelve-path implementation remain blocked. Route Developer implementation;
do not route QA or Integrator before the implementation/review gates.

## Reviewer B1 Tests-Only Scope Update

Reviewer passed the production routing and identified five exact stale
High-temperature/Salt Spray assertion locations, including `[1]` and `[2]`
parameter cases. Current tests-only authority is controlled by
`FEE_DEFAULT_FILL_DEPENDENT_FIELD_CORRECTIONS_tests_only_scope_reconciliation_planner.md`.

No product code, Temperature & Humidity assertion, other fixture semantics, or
fallback may change. Existing oversized test files cannot gain lines. The
external TASK_366C `method_authority` composition defect was excluded and has
since been fixed by its owner; Reviewer closed those failures. Child 3 and the
umbrella remain blocked.

Current next legal role: Reviewer confirmation of the separately documented
stale Fee-rebase fixture-context tests-only scope. Developer is not yet
authorized for that migration.
