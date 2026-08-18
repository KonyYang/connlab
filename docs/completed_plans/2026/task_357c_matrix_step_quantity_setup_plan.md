# TASK_357C Matrix Step Quantity Setup Plan

Status: complete/accepted by Integrator
Task: `TASK_357C_MATRIX_STEP_QUANTITY_SETUP`
Lane: `matrix-step-quantity-setup`
Date: 2026-07-08
Role: Planner / Developer planning-first

## 1. Current Phase / Active Task / Role / Why Allowed

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current board state: `TASK_357B_BASIC_INFORMATION_QUANTITY_DEFAULTS` is complete/accepted. It added Basic Information project-level defaults for `test_points_per_sample`, `readings_per_point`, and `contact_points_per_sample`, while keeping `total_readings` out of Basic Information V1 persistence/input.
- Current role: Planner.
- Why allowed: User/Orchestrator requested creation of the next planned downstream lane after TASK_357A and TASK_357B. This pass creates source-of-truth docs only and does not authorize implementation.

## 2. User Goal Restatement

Matrix Step setup should own the final structured quantity values for each Step. Each Step can import Basic Information draft/confirmed defaults, and the operator can accept or override those values. Once confirmed through Matrix authority, these Step quantities become the source for later Fee Evaluation, Test Record, and Report outputs. Fee Evaluation remains a passive consumer and is explicitly out of scope for TASK_357C implementation.

## 3. Confirmed By User

- TASK_357A is complete/accepted as the quantity authority contract.
- TASK_357B is complete/accepted and Basic Information now has project-level quantity defaults.
- Matrix Step setup is the final confirmation/override location.
- V1 uses one quantity parameter set per Matrix Step.
- V1 fields inherit TASK_357A:
  - `test_points_per_sample`
  - `readings_per_point`
  - `contact_points_per_sample`
  - `total_readings`
- Basic Information draft and confirmed defaults may be imported into Step setup.
- Fee Evaluation is not a quantity input surface and remains downstream TASK_357D scope.
- Test Record / Report reuse remains later TASK_357E scope.

## 4. Confirmed By Repository Evidence

- `docs/task_board.md` marks TASK_357B complete/accepted and records that no Matrix Step override/model/UI, Fee Evaluation consumption, Test Record/Report reuse, Matrix parser/import, LTR workbook/public-drive authority, schema migration, or API client changes were included in TASK_357B.
- `docs/task_357a_matrix_quantity_authority_contract_plan.md` defines the chain: Basic Information draft/confirmed defaults -> Matrix Step final override -> Fee passive consumption -> future Test Record/Report reuse.
- `docs/task_357b_basic_information_quantity_defaults_plan.md` confirms Basic Information V1 stores/exposes the first three default fields and leaves `total_readings` derived/read-only or omitted from Basic Information V1.
- `backend/domain/project_matrix_draft_models.py` currently stores draft Matrix root metadata, groups with `sample_quantity_expression`, rows, and sparse cells, but no structured Step quantity parameters.
- `backend/domain/confirmed_matrix_authority_models.py` currently stores confirmed groups, rows, and cells, but no confirmed Step quantity authority fields.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` currently manages groups, row/cell content, sample quantity expressions, imports, and confirmation workflow; it has no dedicated Step quantity setup surface.
- `backend/application/confirmed_matrix_fee_draft_service.py` and `backend/modules/fee_evaluation/fee_default_fill.py` still use confirmed Matrix text, parsed step tokens, and group `sample_quantity_expression` for Fee defaults; they do not consume structured Matrix Step quantities.
- `backend/application/test_record_fee_dataset_preview_service.py` still emits conservative quantity-basis text and has no structured Step quantity source.

## 5. Planner Inferences

- TASK_357C should own both Matrix draft persistence and confirmed Matrix authority copy semantics for Step quantities.
- The current repository may not have a first-class Step record. Developer planning-first must define the closest stable V1 Step identity, likely row plus parsed Step token identity, without changing parser/import rules in this lane.
- `total_readings` should be computed or displayed in Matrix Step setup from explicit Step fields and later downstream context. It should not be silently invented when inputs are missing.
- If `total_readings` needs sample/group multiplication, TASK_357C should expose source fields and metadata; TASK_357D can decide the Fee-specific consumption formula from confirmed Matrix Step quantities plus group sample quantity.
- UI should fit inside Matrix Editor as an operational setup surface, not as a new standalone workflow or Fee input panel.

## 6. Not Yet Confirmed

No blocker for Reviewer plan gate.

Implementation-level decisions for Developer planning-first:

1. The exact V1 Step identity used to persist one quantity set per Step.
2. Whether Step quantity persistence needs a schema migration or can use an existing JSON/values structure.
3. Exact Matrix Editor UI placement for Step setup without crowding the Matrix table.

## 7. Data Contract

### 7.1 Source Chain

```text
Basic Information defaults
  -> Matrix Step setup imported defaults
  -> Matrix Step manual override
  -> confirmed Matrix Step quantity authority
  -> later Fee / Test Record / Report consumers
```

### 7.2 Default Source Precedence

Recommended import precedence for Step setup:

1. existing Matrix Step override when editing an existing Step setup;
2. confirmed Basic Information defaults;
3. draft Basic Information defaults;
4. empty/manual review state.

Imported defaults must carry source metadata. They do not become final authority until the operator accepts or overrides them in Matrix Step setup.

### 7.3 Per-Step Granularity

V1 uses one quantity parameter set per Matrix Step.

V1 must not split quantities by:

- group;
- condition;
- sample size;
- individual cell token beyond the stable Step identity selected by Developer planning-first.

### 7.4 Manual Override Semantics

The operator can accept imported defaults, clear them, or override each field.

Persisted metadata should include:

- `source`: `basic_information_confirmed`, `basic_information_draft`, `matrix_step_override`, `derived`, or `manual_required`.
- `review_required`: boolean.
- `review_reason`: short business-readable text.

If source data changes after Step setup is confirmed, the system must not silently rewrite Step quantities. Refresh behavior should be explicit and reviewable, or deferred to a later lane.

### 7.5 `total_readings` Policy

`total_readings` is not a Basic Information V1 input.

TASK_357C should treat `total_readings` as:

- derived/display when `test_points_per_sample` and `readings_per_point` or contact-point inputs are sufficient;
- manually confirmable only if Developer planning-first shows a clear need and Reviewer approves;
- `review_required` when inputs are insufficient or ambiguous.

TASK_357D may later combine confirmed Matrix Step quantities with group sample quantity for Fee-specific units. TASK_357C should not implement Fee formulas.

### 7.6 Matrix Confirmation Policy

Matrix draft Step quantities should copy into the confirmed Matrix authority when the Matrix is confirmed.

Matrix revision behavior should be explicit:

- carry quantities forward when Step identity is stable;
- mark review-required when rows/steps change enough that the prior quantity cannot be trusted;
- never invent quantity values from text without source metadata.

## 8. May Touch

Current planning pass:

- `tasks/TASK_357C_MATRIX_STEP_QUANTITY_SETUP.md`
- `docs/task_357c_matrix_step_quantity_setup_plan.md`
- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_planner.md`
- `docs/task_board.md`

Future implementation draft:

- `backend/domain/project_matrix_draft_models.py`
- `backend/domain/confirmed_matrix_authority_models.py`
- backend Matrix draft / confirmed Matrix persistence services and repositories identified by Developer planning-first
- backend Matrix draft / confirmation / revision route DTOs and APIs as needed
- `backend/application/project_basic_information_service.py` only for read-only default retrieval or helper reuse; no Basic Information mutation behavior
- `frontend/src/features/matrix-editor/**`
- `frontend/src/api/client.ts` only for typed Matrix quantity DTO/client helpers
- focused backend Matrix draft/confirmed authority/revision tests
- focused frontend Matrix Editor tests
- TASK_357C Developer/Reviewer/QA evidence and board updates

## 9. Must Not Touch / Locked Paths

Must not touch:

- Fee Evaluation consumption/default-fill implementation.
- Test Record / Report reuse implementation.
- Basic Information quantity default implementation beyond read-only default source consumption.
- Matrix parser/import rules.
- LTR workbook/public-drive authority.
- StepInstance, execution persistence, image/evidence assets, Report generation, AI, permissions, LAN/server, multi-user.
- release/settings/template residual cleanup.
- unrelated dirty files.

Locked paths:

- `backend/modules/fee_evaluation/**`
- `backend/application/confirmed_matrix_fee_draft_service.py`
- `frontend/src/features/fee-evaluation/**`
- Test Record / Report implementation paths
- Matrix parser/import implementation paths unless only stable type references are required
- real workbook files
- real public-drive folders
- real local project folders
- `D:\Test Project/**`
- `D:\PublicProject/**`
- `.agents/**`
- `docs/project_management/**`
- `dist_release/**`
- `packaging/**`
- release scripts/tests/docs
- `temp_agents_stash.md`

## 10. Dependency Relationship

- Upstream: TASK_357A contract accepted.
- Upstream: TASK_357B Basic Information defaults accepted.
- This lane: TASK_357C Matrix Step quantity setup model/UI/persistence planning.
- Downstream: TASK_357D Fee Evaluation passive Matrix quantity consumption.
- Later: TASK_357E Test Record / Report quantity reuse.

TASK_357D must wait for a confirmed Matrix Step quantity read model. TASK_357E may be planned later but must not implement StepInstance, Report generation, or execution persistence from TASK_357C.

## 11. Validation Gate Draft

Backend:

- tests for importing confirmed Basic Information defaults into Matrix Step setup;
- tests for importing draft Basic Information defaults when confirmed values are absent or explicitly requested;
- tests for operator override persistence in Matrix draft state;
- tests for Matrix confirmation copying Step quantities into confirmed Matrix authority;
- tests for revision carry-forward versus review-required behavior;
- tests proving missing/ambiguous quantities do not invent values.

Frontend:

- Matrix Editor tests for Step quantity setup rendering and source metadata;
- tests for accepting imported defaults, manual override, clearing values, and readonly/lifecycle disabled behavior;
- tests that no Fee input UI is introduced in Matrix Step setup;
- tests that `total_readings` is display/derived/review-required according to available fields.

General:

- focused pytest for Matrix draft/confirmed authority services;
- focused `npm test` for Matrix Editor;
- `npm run build`;
- `git diff --check`;
- trailing whitespace scan;
- forbidden-scope scan for Fee/Test Record/Report/LTR/public-drive/release/settings/real folder changes.

## 12. Merge Gate Draft

- Reviewer plan gate pass.
- User approval before Developer planning-first.
- Developer planning-first evidence must refine:
  - Step identity;
  - persistence/data migration strategy;
  - DTO/API shape;
  - Matrix Editor UI placement;
  - revision/stale handling.
- Reviewer implementation-readiness pass.
- User approval and source-of-truth reconciliation before Developer implementation.
- Reviewer implementation gate pass after code.
- QA required because this lane changes Matrix Editor UI and Matrix authority persistence.
- Integrator packaging/readiness must isolate TASK_357C from external release/settings/template residuals.

## 13. Definition Of Ready

Ready for Reviewer plan gate: yes.

Not ready for implementation: yes, by design. Implementation requires Reviewer plan gate, user approval for Developer planning-first, Developer planning-first, Reviewer readiness, user implementation approval, and source-of-truth reconciliation.

## 14. Package Isolation Risks

The current worktree contains external residuals under Settings/LTR helper files, backend desktop/release helpers, `dist_release/**`, `packaging/**`, release scripts/tests/docs, frontend New Project test residuals, TASK_357A docs, and `temp_agents_stash.md`. TASK_357C must package only its task/plan/evidence/board planning files in this Planner pass and must not absorb those residuals.

## 15. Stop Point

Recommended next role: Reviewer plan gate.

Blocking summary: none.

Implementation remains unauthorized.

---

## 16. Developer Planning-First Refinement

Date: 2026-07-08
Role: Developer
Status: developer planning-first complete

This refinement is based on the accepted TASK_357A/TASK_357B contract, current Matrix draft/confirmed authority code, current runtime projection token reference code, Basic Information quantity defaults implementation, and current Matrix Editor structure.

### 16.1 Repository Facts From Developer Read

- `backend/domain/project_matrix_draft_models.py` currently models Matrix draft as root record, groups, rows, and sparse group/row cells. It has no Step child table or quantity metadata field.
- `backend/domain/confirmed_matrix_authority_models.py` currently models confirmed Matrix authority as immutable root, groups, rows, and cells. It has no confirmed Step quantity authority field.
- `backend/infrastructure/storage/models_project_matrix_draft.py` and `backend/infrastructure/storage/models_confirmed_matrix_authority.py` have no safe JSON/values extension column for Step quantity metadata.
- `backend/modules/runtime_projection/token_projection_builder.py` already defines deterministic Step token identity from project, matrix, group, sequence, and suffix note. This is the closest existing Step identity contract.
- Current runtime projection token references include `matrix_reference`, so references are stable inside one Matrix version/draft but naturally change across Matrix revisions.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` currently owns large Matrix draft UI state, group selection, sample quantity expressions, Step token validation, Step preview rows, and confirm/revision actions. Future implementation should avoid growing it further with inline quantity setup JSX.
- TASK_357B exposes Basic Information defaults through the existing Basic Information values-map keys:
  - `test_points_per_sample`
  - `readings_per_point`
  - `contact_points_per_sample`

### 16.2 Step Identity Decision

V1 Step identity should be token-based, not parser-rule-based and not Fee-specific.

Draft Step quantity identity:

- `project_matrix_draft_id`
- `draft_group_id`
- `draft_row_id`
- `step_sequence`
- `step_suffix_note`

Confirmed Step quantity identity:

- `confirmed_matrix_id`
- `confirmed_group_id`
- `confirmed_row_id`
- `step_sequence`
- `step_suffix_note`

API DTOs may also expose a generated `token_reference` for UI/runtime navigation, built with the existing runtime projection reference shape. Persistence should keep the normalized identity columns above so revision carry-forward can compare draft/confirmed lineage without parsing a pipe-delimited string.

Step suffix policy:

- `null` means no suffix.
- Preserve normalized suffix notes such as `(a)`, `*`, or `#` from the existing parser.
- Raw token text can be stored for display/debug only. It must not become the only identity.

### 16.3 Persistence / Migration Strategy

A schema addition is required for a clean implementation. This is not a product-code implementation in planning-first, but it must be explicitly approved by Reviewer/User before Developer implementation.

Recommended new draft table:

```text
project_matrix_draft_step_quantities
  draft_step_quantity_id TEXT primary key
  project_matrix_draft_id TEXT not null
  draft_group_id TEXT not null
  draft_row_id TEXT not null
  step_sequence INTEGER not null
  step_suffix_note TEXT null
  raw_token TEXT null
  test_points_per_sample TEXT null
  readings_per_point TEXT null
  contact_points_per_sample TEXT null
  source TEXT not null
  review_required BOOLEAN not null
  review_reason TEXT null
  updated_at TEXT not null
  unique(project_matrix_draft_id, draft_group_id, draft_row_id, step_sequence, step_suffix_note)
```

Recommended new confirmed table:

```text
confirmed_matrix_step_quantities
  confirmed_step_quantity_id TEXT primary key
  confirmed_matrix_id TEXT not null
  confirmed_group_id TEXT not null
  confirmed_row_id TEXT not null
  draft_group_id TEXT not null
  draft_row_id TEXT not null
  step_sequence INTEGER not null
  step_suffix_note TEXT null
  raw_token TEXT null
  test_points_per_sample TEXT null
  readings_per_point TEXT null
  contact_points_per_sample TEXT null
  source TEXT not null
  review_required BOOLEAN not null
  review_reason TEXT null
  confirmed_at TEXT not null
  unique(confirmed_matrix_id, confirmed_group_id, confirmed_row_id, step_sequence, step_suffix_note)
```

Why table-based migration rather than storing JSON in Matrix cells:

- Matrix cells are source/authority Step token maps and should not be polluted with operator setup metadata.
- Basic Information values-map is project-level defaults only and must not become Step authority.
- Confirmed Matrix authority is immutable; Step quantity records should copy into confirmed authority with the same immutability.
- Later Fee/Test Record/Report lanes need a stable confirmed read model, not frontend-only state.

Migration boundary:

- Add SQLAlchemy models and `init_db` SQLite migration helpers in the same storage style as existing Matrix draft/confirmed migrations.
- Migration should create empty tables only and must not backfill guessed quantity values.
- Existing projects remain valid; missing records should surface as `review_required`, not fabricated values.

### 16.4 DTO / API Shape

Recommended backend DTO names:

- `MatrixStepQuantityFields`
- `MatrixStepQuantitySource`
- `MatrixStepQuantityDraftItem`
- `MatrixStepQuantityDraftResponse`
- `MatrixStepQuantityDraftSaveRequest`
- `ConfirmedMatrixStepQuantityItem`

Field shape:

```json
{
  "token_reference": "project|matrix|group|2|(a)",
  "group_id": "pmdg-...",
  "row_id": "pmdr-...",
  "step_sequence": 2,
  "step_suffix_note": "(a)",
  "raw_token": "2(a)",
  "test_item": "LLCR",
  "test_points_per_sample": "3",
  "readings_per_point": "2",
  "contact_points_per_sample": "4",
  "total_readings": "6",
  "source": "basic_information_confirmed",
  "review_required": false,
  "review_reason": null
}
```

Draft APIs:

- `GET /api/projects/{project_id}/matrix-drafts/{project_matrix_draft_id}/step-quantities`
  - Builds current parsed Step list from draft rows/cells.
  - Joins persisted draft quantity records.
  - Applies Basic Information defaults only for missing draft records or explicit import preview.
  - Marks missing or ambiguous values as `review_required`.
- `PUT /api/projects/{project_id}/matrix-drafts/{project_matrix_draft_id}/step-quantities`
  - Saves a batch of Step quantity records.
  - Validates identity belongs to the current draft and parsed Step set.
  - Accepts manual overrides, accepted defaults, and cleared values.

Confirmed authority:

- Existing confirm endpoints should copy draft Step quantities into `confirmed_matrix_step_quantities`.
- If a parsed selected Step has no quantity record at confirmation, create a confirmed review-required record with empty fields and reason `Quantity setup not confirmed`.
- Existing active confirmed Matrix snapshot response may include `step_quantities` if Reviewer approves response expansion; alternatively add a read-only confirmed quantities endpoint to reduce blast radius.

Basic Information default source:

- Backend should resolve Basic Information defaults server-side, using latest confirmed values first, then draft values.
- Frontend should not fetch Basic Information separately to invent quantity defaults for persistence.

### 16.5 Default Import / Update Policy

Import precedence for a Step row in the draft quantity API:

1. Existing draft Step quantity record.
2. Latest confirmed Basic Information default.
3. Current Basic Information draft default.
4. Empty fields with `review_required=true`.

Operator actions:

- `Accept defaults`: persists current Basic Information-derived fields into draft Step quantity records with source `basic_information_confirmed` or `basic_information_draft`.
- `Override`: persists edited values with source `matrix_step_override`.
- `Clear`: stores empty values with source `manual_required` and `review_required=true`.
- `Refresh from Basic Information`: explicit batch action only, never automatic overwrite.

Source changes:

- If Basic Information defaults change after a Step quantity override exists, do not silently rewrite the Step value.
- The API may return a non-blocking `source_changed` review reason for values that still match an older imported source, but automatic rewrite is out of scope unless Reviewer approves it.

### 16.6 Validation / Derived `total_readings`

Accepted numeric shape:

- blank or non-negative decimal text for the three stored fields;
- normalize surrounding whitespace;
- reject negative, alphabetic, and mixed-unit values in the save API with field-level labels.

Derived display:

- `total_readings` is read-only in V1.
- Compute `total_readings = test_points_per_sample * readings_per_point` when both values are present.
- Do not multiply by group sample quantity in TASK_357C. Fee-specific sample multiplication belongs to TASK_357D.
- `contact_points_per_sample` remains a separate stored quantity field for downstream interpretation.
- If required inputs are missing, `total_readings=null` and `review_required=true`.

### 16.7 Matrix Revision / Stale Behavior

Revision draft creation should attempt carry-forward from active confirmed quantities when Step identity is stable enough.

Recommended carry-forward matching order:

1. same confirmed lineage mapped to new draft group/row plus same `step_sequence` and `step_suffix_note`;
2. same group key/label plus same row technical identity (`test_item`, `source_section`, `method`, `condition`, `requirement`) plus same sequence/suffix;
3. otherwise no carry-forward and mark `review_required=true`.

Carry-forward records should use source `confirmed_matrix_carry_forward` and preserve review metadata. If a row/group changed enough that identity is ambiguous, do not guess.

### 16.8 Matrix Editor UI Placement

UI should remain a quiet operational supplement to the Matrix table.

Recommended frontend structure:

- New component: `frontend/src/features/matrix-editor/MatrixStepQuantityPanel.tsx`
- New selector/model helpers: `frontend/src/features/matrix-editor/matrixStepQuantitySelectors.ts`
- Optional hook if needed: `frontend/src/features/matrix-editor/useMatrixStepQuantityModel.ts`
- Keep `MatrixEditorWorkspace.tsx` as the entry/composition point only.

Placement:

- Put a compact `Step quantity setup` panel near the existing selected group / Step preview area, not as a separate route and not above the Matrix table.
- The panel should show the selected group, parsed Step list, source badge, three editable fields, read-only `Total readings`, and a short review reason.
- Use familiar form controls, restrained density, no nested cards, no side stripes, no long explanation.

Copy:

- `Step quantity setup`
- `Import Basic Information defaults`
- `Accept defaults`
- `Override`
- `Clear`
- `Review required`
- `Total readings`

Readonly behavior:

- Respect existing lifecycle readonly and confirmed/revision guards.
- Disable Step quantity edits while save/confirm is in progress.
- Closed/stopped readonly surfaces should display values and source/review state without mutation actions.

### 16.9 Exact Future May Touch

Backend domain/application/storage/API:

- `backend/domain/project_matrix_draft_models.py`
- `backend/domain/confirmed_matrix_authority_models.py`
- `backend/application/project_matrix_draft_persistence_service.py`
- `backend/application/confirmed_matrix_authority_service.py`
- `backend/application/matrix_revision_flow_service.py`
- new `backend/application/matrix_step_quantity_service.py`
- `backend/infrastructure/storage/models_project_matrix_draft.py`
- `backend/infrastructure/storage/models_confirmed_matrix_authority.py`
- `backend/infrastructure/storage/repositories/project_matrix_draft.py`
- `backend/infrastructure/storage/repositories/confirmed_matrix_authority.py`
- `backend/infrastructure/storage/database.py`
- `backend/api/routes_project_matrix_drafts.py`
- new `backend/api/routes_matrix_step_quantities.py` if separate endpoints are cleaner
- `backend/api/dependencies.py`
- `backend/api/main.py` only if a new route module is added
- `backend/application/project_basic_information_service.py` or `backend/application/project_basic_information_source.py` only for read-only default retrieval/helper reuse

Frontend:

- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixStepQuantityPanel.tsx`
- `frontend/src/features/matrix-editor/matrixStepQuantitySelectors.ts`
- optional `frontend/src/features/matrix-editor/useMatrixStepQuantityModel.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- focused tests for any new Matrix Editor helpers/components
- `frontend/src/workbench.css` only for compact Matrix Step quantity panel styling if existing classes are insufficient

Tests:

- `tests/unit/test_matrix_step_quantity_service.py`
- `tests/unit/test_project_matrix_draft_persistence_service.py`
- `tests/unit/test_confirmed_matrix_authority_service.py`
- `tests/unit/test_matrix_revision_flow_service.py`
- `tests/unit/test_project_matrix_draft_repository.py`
- `tests/unit/test_confirmed_matrix_authority_repository.py`
- focused Matrix draft/confirmation/revision API integration tests
- focused Matrix Editor frontend tests

Docs/evidence:

- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_developer.md`
- TASK_357C Reviewer/QA evidence and board updates through normal lane flow

### 16.10 Must Not Touch / Locked Paths For Future Implementation

- No Fee Evaluation consumption or default-fill changes.
- No `backend/modules/fee_evaluation/**`.
- No `frontend/src/features/fee-evaluation/**`.
- No Test Record / Report generation or reuse implementation.
- No StepInstance, execution persistence, evidence/image asset, AI, permissions, LAN/server, or multi-user work.
- No Matrix parser/import rule changes.
- No Basic Information quantity default mutation behavior beyond read-only source consumption.
- No LTR workbook/public-drive authority changes.
- No real workbook/folder mutation.
- No release/settings/template cleanup.
- No `.agents/**`.
- No `docs/project_management/**`.
- No `dist_release/**`, `packaging/**`, release scripts/tests/docs, or `temp_agents_stash.md`.

### 16.11 Focused Test Plan

Backend:

- Service builds parsed Step quantity candidates from Matrix draft cells and existing token parser.
- Confirmed Basic Information defaults outrank draft defaults when importing.
- Draft Basic Information defaults are used when no confirmed defaults exist.
- Existing draft Step quantity records outrank imported defaults.
- Manual override persists with source `matrix_step_override`.
- Clear persists review-required state.
- Invalid numeric input returns business-readable field errors.
- `total_readings` derives only from `test_points_per_sample * readings_per_point` and does not multiply group samples.
- Matrix confirm copies draft Step quantities into confirmed Matrix authority.
- Missing setup creates review-required confirmed Step quantity records.
- Revision draft carry-forward preserves stable Step identities and marks ambiguous/missing ones review-required.
- Migration creates empty draft/confirmed Step quantity tables without backfill guesses.

Frontend:

- Matrix Editor displays compact Step quantity setup for selected group/step.
- `Import Basic Information defaults` populates fields from API defaults, not frontend-invented values.
- Operator can accept defaults, override, clear, and save.
- Invalid numeric values show field-level review copy and disable save/confirm for the quantity action.
- Readonly/lifecycle states disable mutation actions and keep values visible.
- Matrix confirm/revision buttons preserve existing guards and include Step quantity validation status.
- No Fee input UI appears in Matrix Editor.
- Matrix table remains the primary visual surface.

Validation commands:

- focused `py -m pytest` for Matrix Step quantity services/repositories/API;
- focused `npm test -- MatrixEditorWorkspace MatrixStepQuantity --run`;
- `npm run build`;
- `git diff --check`;
- trailing whitespace scan;
- forbidden-scope scan for Fee/Test Record/Report/LTR/public-drive/release/settings/real folder paths;
- line-count scan for new/changed Python files.

### 16.12 Readiness Notes / Blockers

Developer planning-first finds no blocker to Reviewer implementation-readiness, but readiness should explicitly approve the required Matrix draft/confirmed authority schema additions.

Reviewer readiness passed and user approval has now authorized Developer implementation after Planner source-of-truth reconciliation.

Recommended next role: Developer implementation pass.

---

## 17. Planner Source-Of-Truth Reconciliation

Date: 2026-07-08
Role: Planner
Status: complete/accepted by Integrator

Facts reconciled:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed docs-only.
- Reviewer implementation-readiness gate passed.
- User approved TASK_357C source-of-truth reconciliation and Developer implementation.

Schema boundary authorization:

- Reviewer readiness explicitly identified Matrix draft/confirmed authority schema additions as reasonably required.
- User approval is recorded for TASK_357C implementation, including narrowly scoped Matrix draft/confirmed Step quantity authority tables.
- This authorization is limited to Matrix Step quantity setup authority. It does not authorize StepInstance/execution persistence, Fee Evaluation consumption/default-fill, Test Record/Report reuse, Matrix parser/import rule changes, Basic Information schema/mutation changes, LTR/public-drive/real workbook/folder changes, or release/settings/template residual cleanup.

Implementation authorization scope:

- one quantity parameter set per Matrix Step;
- import Basic Information draft/confirmed defaults;
- operator accept/override/clear semantics;
- Matrix draft persistence and confirmed Matrix authority copy for Step quantities;
- `total_readings` derived/read-only display/downstream policy;
- compact Matrix Editor Step quantity setup surface;
- focused backend/frontend tests and validation gates from this plan.

Next role:

- Integrator packaging/readiness accepted this lane after Developer implementation, Reviewer B1 fix re-gate pass, QA pass, package isolation, and validation.

Blocking summary: none.
