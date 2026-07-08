# TASK_357C Reviewer Evidence - Matrix Step Quantity Setup

## Plan Gate

- Date: 2026-07-08
- Role: Reviewer
- TASK_ID: `TASK_357C_MATRIX_STEP_QUANTITY_SETUP`
- Lane: `matrix-step-quantity-setup`
- Status: `reviewer_plan_gate_pass`
- Recommended next role: User approval / Developer planning-first
- Blocking summary: none

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `$impeccable` product context from `PRODUCT.md` / `DESIGN.md`
- `tasks/TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT.md`
- `docs/task_357a_matrix_quantity_authority_contract_plan.md`
- `docs/lane_evidence/TASK_357A_matrix-quantity-authority-contract_reconciliation_planner.md`
- `tasks/TASK_357B_BASIC_INFORMATION_QUANTITY_DEFAULTS.md`
- `docs/task_357b_basic_information_quantity_defaults_plan.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_developer.md`
- `tasks/TASK_357C_MATRIX_STEP_QUANTITY_SETUP.md`
- `docs/task_357c_matrix_step_quantity_setup_plan.md`
- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_planner.md`
- Current Matrix draft / confirmed authority models
- Current Matrix Editor workspace references
- Current Basic Information quantity default implementation references
- Current Fee Evaluation and Test Record downstream references
- Current `git status --short`

## Review Findings

No blocking findings.

TASK_357C correctly inherits TASK_357A and TASK_357B:

- Basic Information remains a default source only.
- Matrix Step setup is planned as the final quantity confirmation and override authority.
- V1 granularity is one quantity parameter set per Matrix Step.
- V1 fields are aligned to `test_points_per_sample`, `readings_per_point`, `contact_points_per_sample`, and derived/display/downstream `total_readings`.
- TASK_357B's implementation boundary is preserved: Basic Information exposes only the first three optional defaults and does not persist `total_readings`.

Scope is appropriately limited for a planned lane:

- TASK_357C plans Matrix Step quantity setup model/UI/persistence and confirmed Matrix copy semantics.
- Fee Evaluation consumption remains locked for TASK_357D.
- Test Record / Report reuse remains locked for TASK_357E.
- StepInstance, execution persistence, Report generation, AI, permissions, LAN/server, multi-user, LTR workbook/public-drive, real workbook/folder mutation, release/settings/template cleanup, `.agents/**`, and `docs/project_management/**` remain locked.

Repository facts support the plan:

- Current Matrix draft models have root metadata, groups with `sample_quantity_expression`, rows, and sparse cells, but no structured per-Step quantity parameters.
- Current confirmed Matrix authority models have groups, rows, and cells, but no confirmed Step quantity authority fields.
- Current Matrix Editor handles groups, rows, sample quantity expressions, import, and confirmation workflow, but has no dedicated Step quantity setup surface.
- Current Fee Evaluation still uses confirmed Matrix text, parsed step tokens, and group sample quantity fallback; it does not consume structured Step quantities.
- Current Test Record preview still emits conservative quantity-basis text and has no structured Step quantity source.

Open implementation questions are correctly left for Developer planning-first rather than hidden:

- exact stable V1 Step identity;
- persistence shape and whether schema migration is needed;
- DTO/API shape;
- Matrix Editor UI placement;
- revision/stale carry-forward versus review-required behavior.

## Validation Run By Reviewer

- `git diff --check -- docs/task_board.md tasks/TASK_357C_MATRIX_STEP_QUANTITY_SETUP.md docs/task_357c_matrix_step_quantity_setup_plan.md docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_planner.md` passed with the existing `docs/task_board.md` LF/CRLF warning only.
- Trailing whitespace scan on TASK_357C docs/board/evidence returned no matches.
- Targeted repository fact checks confirmed current Matrix authority lacks structured per-Step quantity fields and Fee/Test Record consumers remain downstream/fallback-only.
- Current `git status --short` shows TASK_357C docs/board/evidence plus known external release/settings/desktop/New Project residuals; no TASK_357C product implementation is authorized.

## Decision

`reviewer_plan_gate_pass`

TASK_357C is ready for User approval / Developer planning-first.

Do not route Developer implementation from this gate. Developer planning-first should refine exact Step identity, persistence/migration strategy, DTO/API shape, Matrix Editor UI placement, revision/stale behavior, focused tests, and package isolation before any implementation authorization.

---

## Implementation-Readiness Gate

- Date: 2026-07-08
- Role: Reviewer
- TASK_ID: `TASK_357C_MATRIX_STEP_QUANTITY_SETUP`
- Lane: `matrix-step-quantity-setup`
- Status: `reviewer_readiness_pass`
- Recommended next role: User approval + Planner/source-of-truth reconciliation before Developer implementation
- Blocking summary: none

## Evidence Read For Readiness

- `AGENTS.md`
- `docs/task_board.md`
- `tasks/TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT.md`
- `docs/task_357a_matrix_quantity_authority_contract_plan.md`
- `docs/lane_evidence/TASK_357A_matrix-quantity-authority-contract_reconciliation_planner.md`
- `tasks/TASK_357B_BASIC_INFORMATION_QUANTITY_DEFAULTS.md`
- `docs/task_357b_basic_information_quantity_defaults_plan.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_developer.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_reviewer.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_qa.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_reconciliation_planner.md`
- `tasks/TASK_357C_MATRIX_STEP_QUANTITY_SETUP.md`
- `docs/task_357c_matrix_step_quantity_setup_plan.md`
- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_planner.md`
- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_reviewer.md`
- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_developer.md`
- `docs/lane_evidence/DISCOVERY_matrix-step-quantity-authority_planner.md`
- Current Matrix draft / confirmed authority domain and storage models
- Current Matrix draft persistence / confirmed authority services
- Current runtime projection token reference code
- Current Matrix Editor workspace/test files by read/search
- Current Fee Evaluation and Test Record downstream references
- Current `git status --short`

## Readiness Findings

No blocking findings.

Developer planning-first was docs-only:

- Updated `docs/task_357c_matrix_step_quantity_setup_plan.md`.
- Created `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_developer.md`.
- No TASK_357C product implementation files were modified by this planning-first pass.
- Visible backend/frontend/tests/release/settings residuals are external and remain excluded.

The implementation strategy is concrete enough for a future implementation pass after explicit authorization:

- Step identity is defined as token-based and Matrix-owned, using draft/confirmed group + row lineage, `step_sequence`, and `step_suffix_note`.
- The plan correctly avoids making a pipe-delimited runtime token reference the only persisted identity.
- Schema additions are justified: current draft and confirmed Matrix authority storage models have no safe JSON/values extension for per-Step quantity metadata.
- Proposed draft and confirmed Step quantity tables match the Matrix authority boundary and avoid polluting Matrix cells or Basic Information values.
- The migration strategy is bounded to empty table creation with no guessed backfill.
- DTO/API shape is specific enough for Developer implementation planning: draft candidate read, batch save, confirmed authority copy, and optional response expansion or narrow confirmed endpoint.
- Basic Information default import precedence is correct: existing Step override, confirmed Basic Information, draft Basic Information, empty review-required state.
- Manual actions are clear: accept defaults, override, clear, and explicit refresh only.
- `total_readings` remains read-only derived display from `test_points_per_sample * readings_per_point`; group sample multiplication and Fee-specific formulas are deferred to TASK_357D.
- Revision/stale behavior is explicitly conservative: carry forward only on stable identity, otherwise mark review-required.
- Matrix Editor UI placement is concrete and appropriately bounded to a compact `Step quantity setup` panel, new helpers/components, and `MatrixEditorWorkspace.tsx` as composition point only.

Schema boundary decision:

- Readiness passes, but the future implementation requires explicit User approval and source-of-truth reconciliation because it adds Matrix draft/confirmed authority tables.
- This is a Matrix authority schema boundary, not a Basic Information schema change.
- Developer implementation must not start from the current board wording. `docs/task_board.md` still records TASK_357C as planned for Reviewer plan gate / implementation not authorized.

Locked scope remains intact:

- No Fee Evaluation consumption/default-fill implementation.
- No `backend/modules/fee_evaluation/**` changes authorized.
- No `frontend/src/features/fee-evaluation/**` changes authorized.
- No Test Record / Report reuse implementation.
- No StepInstance, execution persistence, evidence/image asset, AI, permissions, LAN/server, or multi-user work.
- No Matrix parser/import rule changes.
- No Basic Information quantity default mutation behavior beyond read-only source consumption.
- No LTR workbook/public-drive authority changes.
- No real workbook/folder mutation.
- No release/settings/template cleanup.
- No `.agents/**` or `docs/project_management/**` changes.

Validation plan is adequate:

- Backend tests cover candidate construction from draft cells/token parsing, default import precedence, existing override precedence, manual override, clear, invalid numeric values, derived `total_readings`, confirm copy, missing setup review-required records, revision carry-forward, migration, and API behavior.
- Frontend tests cover compact Matrix Editor panel rendering, API-provided defaults, accept/override/clear/save flows, invalid numeric feedback, readonly/lifecycle disabling, confirm/revision guard preservation, and absence of Fee input UI.
- General gates include focused pytest, focused Matrix Editor tests, build, diff/trailing scans, forbidden-scope scans, and line-count scan.

## Validation Run By Reviewer

- `git status --short -- docs\task_357c_matrix_step_quantity_setup_plan.md docs\lane_evidence\TASK_357C_matrix-step-quantity-setup_developer.md backend frontend tests frontend\src\api\client.ts .agents docs\project_management` showed TASK_357C plan/evidence as untracked docs and external backend/frontend/tests residuals excluded from this lane.
- `git diff --check -- docs\task_357c_matrix_step_quantity_setup_plan.md docs\lane_evidence\TASK_357C_matrix-step-quantity-setup_developer.md` passed.
- Trailing whitespace scan on TASK_357C plan and Developer evidence returned no matches.
- Repository fact checks confirmed current Matrix draft/confirmed storage models lack Step quantity metadata fields and current runtime projection has token-reference identity that should be reused as a reference, not sole persisted identity.

## Readiness Decision

`reviewer_readiness_pass`

Recommended next role/action:

- User approval + Planner/source-of-truth reconciliation before Developer implementation.
- Reconciliation must explicitly authorize the Matrix draft/confirmed authority schema additions for TASK_357C.
- Do not route Developer implementation directly from this readiness gate.

---

## Implementation Gate

- Date: 2026-07-08
- Role: Reviewer
- TASK_ID: `TASK_357C_MATRIX_STEP_QUANTITY_SETUP`
- Lane: `matrix-step-quantity-setup`
- Status: `reviewer_blocked`
- Recommended next role: Developer fix pass
- Blocking summary: B1 - no-suffix Matrix Step quantity identity uniqueness is not enforced.

## Evidence Read For Implementation Gate

- `AGENTS.md`
- `docs/task_board.md`
- `tasks/TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT.md`
- `docs/lane_evidence/TASK_357A_matrix-quantity-authority-contract_reconciliation_planner.md`
- `tasks/TASK_357B_BASIC_INFORMATION_QUANTITY_DEFAULTS.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_developer.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_reviewer.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_qa.md`
- `tasks/TASK_357C_MATRIX_STEP_QUANTITY_SETUP.md`
- `docs/task_357c_matrix_step_quantity_setup_plan.md`
- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_planner.md`
- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_reviewer.md`
- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_developer.md`
- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_reconciliation_planner.md`
- Current `git status --short`
- TASK_357C backend domain/storage/repository/service/API diffs
- TASK_357C Matrix Editor UI/API-client/test diffs

## Scope Review

No scope blocker was found outside the implementation blocker below.

The actual TASK_357C package is limited to Matrix Step quantity setup:

- Matrix draft and confirmed authority domain/storage/repository additions for Step quantity records.
- Matrix Step quantity service/API and dependency wiring.
- Confirmed Matrix authority copy and revision carry-forward support.
- Matrix Editor panel, selectors, API-client helpers, and focused tests.

Locked scopes remain excluded:

- No Fee Evaluation consumption/default-fill implementation.
- No Test Record / Report reuse implementation.
- No StepInstance or execution persistence.
- No Matrix parser/import rule changes.
- No Basic Information mutation behavior.
- No LTR workbook/public-drive authority changes.
- No Project Workbench, Projects registry, release/package, `.agents/**`, or `docs/project_management/**` TASK_357C content diff.

## Blocking Findings

### B1 - no-suffix Matrix Step quantity identity uniqueness is not enforced

Files:

- `backend/infrastructure/storage/models_project_matrix_draft.py`
- `backend/infrastructure/storage/models_confirmed_matrix_authority.py`
- `backend/application/matrix_step_quantity_service.py`

The draft and confirmed Step quantity tables use a unique constraint that includes nullable `step_suffix_note`. SQLite treats `NULL` values as distinct in unique constraints, so normal Step identities with no suffix can be duplicated. This violates the TASK_357A/TASK_357C contract of one quantity parameter set per Matrix Step.

Reviewer temp probe inserted two `ProjectMatrixDraftStepQuantityModel` rows with the same `project_matrix_draft_id`, `draft_group_id`, `draft_row_id`, and `step_sequence`, both with `step_suffix_note = NULL`; SQLite committed both rows and returned count `2`.

`MatrixStepQuantityService.save_draft` also does not reject duplicate payload identities before replacing draft quantities, so the API can accept duplicate no-suffix Step identities even before relying on the database constraint.

Minimum fix required:

- Make no-suffix identity uniqueness robust for both draft and confirmed Step quantity records. Prefer normalizing no suffix to a non-null sentinel/empty string and making persisted identity comparison non-null, or otherwise enforce equivalent storage-level uniqueness.
- Reject duplicate draft save payload identities before persistence.
- Add focused tests proving duplicate no-suffix identities cannot persist for draft and confirmed authority tables.
- Add API/service coverage showing duplicate no-suffix save payloads are rejected and do not create duplicate Matrix Step quantity authority records.

## Validation Run By Reviewer

- Focused backend subset passed: `py -m pytest tests/unit/test_matrix_step_quantity_service.py tests/integration/test_matrix_step_quantity_api.py tests/unit/test_project_matrix_draft_repository.py::test_project_matrix_draft_repository_replaces_step_quantities tests/unit/test_confirmed_matrix_authority_repository.py::test_confirmed_matrix_authority_repository_roundtrips_step_quantities tests/unit/test_confirmed_matrix_authority_service.py -q` -> `16 passed`.
- `py -m py_compile` passed for touched TASK_357C backend modules/routes/domain files.
- Focused frontend tests passed: `npm test -- MatrixEditorWorkspace --run` -> `1 file / 39 tests`.
- `npm run build` passed with existing Vite chunk-size warning only.
- `git diff --check` returned LF/CRLF normalization warnings only.
- Trailing whitespace scan on TASK_357C package files returned no matches.
- Line-count scan passed for changed TASK_357C Python files; largest checked file was `backend/application/matrix_revision_flow_service.py` at 491 lines.
- Forbidden-scope content diff scan returned no TASK_357C content diff in Fee/Test Record/Report/LTR/public-drive/Project Workbench/Projects registry/.agents/docs_project_management/release/package scopes.
- Reviewer duplicate-identity probe reproduced B1 with SQLite accepting duplicate no-suffix draft Step quantity identities.

## Implementation Gate Decision

`reviewer_blocked`

Recommended next role/action:

- Developer fix pass for B1.
- Do not route QA until the no-suffix Matrix Step quantity identity uniqueness blocker is closed and re-gated.

---

## Implementation Re-Gate For B1 Fix

- Date: 2026-07-08
- Role: Reviewer
- TASK_ID: `TASK_357C_MATRIX_STEP_QUANTITY_SETUP`
- Lane: `matrix-step-quantity-setup`
- Status: `reviewer_pass`
- Recommended next role: QA gate
- Blocking summary: none

## Re-Gate Scope

This re-gate only reviewed closure of B1 and checked that the TASK_357C package did not expand beyond Matrix Step quantity setup.

## B1 Closure Review

B1 is closed.

Developer fixed the nullable uniqueness hole by making `step_suffix_note` non-null in both Step quantity storage models and normalizing no-suffix identities to `""` before persistence:

- `ProjectMatrixDraftStepQuantityModel.step_suffix_note` is now `nullable=False, default=""`.
- `ConfirmedMatrixStepQuantityModel.step_suffix_note` is now `nullable=False, default=""`.
- Draft and confirmed repository mappers convert `None`/blank suffix values to the same persisted identity value and convert persisted blank suffixes back to `None` for domain/API read shape.
- `MatrixStepQuantityService.save_draft` now tracks normalized payload identities and rejects duplicate save items before persistence.

The fix preserves the public/domain no-suffix shape while making SQLite uniqueness effective for normal no-suffix Matrix Step identities.

## Regression Coverage Reviewed

New/updated coverage closes the original failure modes:

- Service rejects duplicate no-suffix save payload identities.
- API rejects duplicate no-suffix save payload identities.
- Draft repository rejects duplicate no-suffix Step quantity rows through storage uniqueness.
- Confirmed authority repository rejects duplicate no-suffix Step quantity rows through storage uniqueness.

No new scope expansion was found:

- No Fee Evaluation consumption/default-fill implementation.
- No Test Record / Report reuse.
- No StepInstance or execution persistence.
- No Matrix parser/import rule changes.
- No Basic Information mutation behavior.
- No LTR workbook/public-drive authority changes.
- No Project Workbench, Projects registry, `.agents/**`, `docs/project_management/**`, release/package, or unrelated cleanup content diff attributable to TASK_357C.

## Validation Run By Reviewer For Re-Gate

- Focused backend B1/TASK_357C suite passed: `py -m pytest tests/unit/test_matrix_step_quantity_service.py tests/integration/test_matrix_step_quantity_api.py tests/unit/test_project_matrix_draft_repository.py::test_project_matrix_draft_repository_replaces_step_quantities tests/unit/test_project_matrix_draft_repository.py::test_project_matrix_draft_repository_rejects_duplicate_no_suffix_step_quantity tests/unit/test_confirmed_matrix_authority_repository.py::test_confirmed_matrix_authority_repository_roundtrips_step_quantities tests/unit/test_confirmed_matrix_authority_repository.py::test_confirmed_matrix_authority_repository_rejects_duplicate_no_suffix_step_quantity tests/unit/test_confirmed_matrix_authority_service.py tests/unit/test_matrix_revision_flow_service.py tests/integration/test_matrix_revision_flow_api.py -q` -> `30 passed`.
- `py -m py_compile` passed for touched TASK_357C backend service/repository/route/domain/storage files.
- Focused frontend tests passed: `npm test -- MatrixEditorWorkspace --run` -> `1 file / 39 tests`.
- `npm run build` passed with existing Vite chunk-size warning only.
- `git diff --check` returned LF/CRLF normalization warnings only.
- Trailing whitespace scan on TASK_357C package files returned no matches.
- Line-count scan passed: largest checked TASK_357C Python file is `backend/application/matrix_revision_flow_service.py` at 491 lines; all checked TASK_357C Python files remain below AGENTS hard limit.
- Forbidden-scope content diff scan returned no TASK_357C content diff in Fee/Test Record/Report/LTR/public-drive/Project Workbench/Projects registry/.agents/docs_project_management/release/package scopes.

## Re-Gate Decision

`reviewer_pass`

Recommended next role/action:

- QA gate for Matrix Editor Step quantity setup browser smoke / integration smoke when seeded data is available.
- Do not route Integrator before QA because Developer browser smoke was not run and this lane includes Matrix Editor UI behavior.
