# TASK_357C Matrix Step Quantity Setup Developer Evidence

Status: implementation complete - ready for Reviewer implementation gate
Task: `TASK_357C_MATRIX_STEP_QUANTITY_SETUP`
Lane: `matrix-step-quantity-setup`
Date: 2026-07-08
Role: Developer

## Routing Summary

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active task: `TASK_357C_MATRIX_STEP_QUANTITY_SETUP`.
- Why allowed: `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_reconciliation_planner.md` records Reviewer plan gate passed, Developer planning-first complete, Reviewer readiness passed, User approved reconciliation and Developer implementation, and implementation authorized / pending Developer implementation.
- Stop point: Developer implementation complete. Recommended next role is Reviewer implementation gate.

## Source-Of-Truth Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `$impeccable` context via `node .agents/skills/impeccable/scripts/load-context.mjs`
- `.agents/skills/impeccable/reference/product.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `tasks/TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT.md`
- `docs/task_357a_matrix_quantity_authority_contract_plan.md`
- `docs/lane_evidence/TASK_357A_matrix-quantity-authority-contract_reconciliation_planner.md`
- `tasks/TASK_357B_BASIC_INFORMATION_QUANTITY_DEFAULTS.md`
- `docs/task_357b_basic_information_quantity_defaults_plan.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_developer.md`
- `tasks/TASK_357C_MATRIX_STEP_QUANTITY_SETUP.md`
- `docs/task_357c_matrix_step_quantity_setup_plan.md`
- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_planner.md`
- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_reviewer.md`
- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_reconciliation_planner.md`
- Current Basic Information quantity defaults, Matrix draft/confirmed authority, Matrix revision, Matrix Editor, API client, storage model, and focused test files.

## Changed Files

- `backend/domain/project_matrix_draft_models.py`
- `backend/domain/confirmed_matrix_authority_models.py`
- `backend/domain/__init__.py`
- `backend/application/matrix_step_quantity_service.py`
- `backend/application/matrix_step_quantity_authority_builder.py`
- `backend/application/confirmed_matrix_authority_service.py`
- `backend/application/matrix_revision_flow_service.py`
- `backend/infrastructure/storage/models_project_matrix_draft.py`
- `backend/infrastructure/storage/models_confirmed_matrix_authority.py`
- `backend/infrastructure/storage/repositories/project_matrix_draft.py`
- `backend/infrastructure/storage/repositories/confirmed_matrix_authority.py`
- `backend/api/routes_matrix_step_quantities.py`
- `backend/api/main.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/matrixStepQuantitySelectors.ts`
- `frontend/src/features/matrix-editor/MatrixStepQuantityPanel.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_matrix_step_quantity_service.py`
- `tests/integration/test_matrix_step_quantity_api.py`
- `tests/unit/test_confirmed_matrix_authority_service.py`
- `tests/unit/test_project_matrix_draft_repository.py`
- `tests/unit/test_confirmed_matrix_authority_repository.py`
- `docs/lane_evidence/TASK_357C_matrix-step-quantity-setup_developer.md`

`backend/api/dependencies.py` and `backend/api/routes_project_matrix_drafts.py` have no TASK_357C content diff. `backend/api/dependencies.py` still appears in `git status` only because of LF/CRLF working-tree noise.

## Implementation Summary

- Added draft Matrix Step quantity authority records for each parsed Step token in selected Matrix draft cells.
- Added confirmed Matrix Step quantity authority records copied from draft setup during Matrix confirmation.
- Added revision carry-forward for confirmed Step quantity setup when confirmed group/row lineage maps cleanly; ambiguous or missing rows remain review-required.
- Added a focused Matrix Step quantity service that imports project-level Basic Information defaults read-only, with precedence:
  1. saved Matrix Step override;
  2. latest confirmed Basic Information defaults;
  3. latest draft Basic Information defaults;
  4. blank review-required Step setup.
- Added V1 fields: `test_points_per_sample`, `readings_per_point`, `contact_points_per_sample`.
- Added read-only derived `total_readings = test_points_per_sample * readings_per_point`; no sample quantity multiplication and no Fee consumption.
- Added GET/PUT project Matrix draft Step quantity API endpoints under `routes_matrix_step_quantities.py`.
- Added typed frontend API helpers and a compact Matrix Editor Step quantity setup panel scoped to the selected Matrix group.
- Kept Matrix parser/import rules unchanged.
- Kept Basic Information storage/schema unchanged; TASK_357C only reads existing Basic Information defaults.
- Did not implement Fee Evaluation, Test Record, Report, StepInstance, or execution persistence scope.

## Validation

- TDD red check before implementation:
  - `py -m pytest tests/unit/test_matrix_step_quantity_service.py -q` failed with `ModuleNotFoundError: backend.application.matrix_step_quantity_service`.
- Backend focused tests:
  - `py -m pytest tests/unit/test_matrix_step_quantity_service.py tests/integration/test_matrix_step_quantity_api.py tests/unit/test_project_matrix_draft_repository.py::test_project_matrix_draft_repository_replaces_step_quantities tests/unit/test_confirmed_matrix_authority_repository.py::test_confirmed_matrix_authority_repository_roundtrips_step_quantities tests/unit/test_confirmed_matrix_authority_service.py tests/unit/test_matrix_revision_flow_service.py tests/integration/test_matrix_revision_flow_api.py -q`
  - Result: `26 passed`.
- Frontend focused tests:
  - `npm test -- MatrixEditorWorkspace --run` from `frontend`
  - Result: `1 file / 39 tests passed`.
- Frontend build:
  - `npm run build` from `frontend`
  - Result: passed with existing Vite chunk-size warning only.
- Python compile:
  - `py -m py_compile backend/application/matrix_step_quantity_service.py backend/application/matrix_step_quantity_authority_builder.py backend/application/confirmed_matrix_authority_service.py backend/application/matrix_revision_flow_service.py backend/infrastructure/storage/repositories/project_matrix_draft.py backend/infrastructure/storage/repositories/confirmed_matrix_authority.py backend/api/routes_matrix_step_quantities.py backend/api/main.py backend/domain/project_matrix_draft_models.py backend/domain/confirmed_matrix_authority_models.py`
  - Result: passed.
- Line-count check:
  - `backend/application/matrix_step_quantity_service.py`: 411 lines.
  - `backend/application/matrix_step_quantity_authority_builder.py`: 120 lines.
  - `backend/application/confirmed_matrix_authority_service.py`: 310 lines.
  - `backend/application/matrix_revision_flow_service.py`: 491 lines.
  - `backend/infrastructure/storage/repositories/project_matrix_draft.py`: 383 lines.
  - `backend/infrastructure/storage/repositories/confirmed_matrix_authority.py`: 325 lines.
  - `backend/api/routes_matrix_step_quantities.py`: 180 lines.
  - Result: all TASK_357C changed Python files are under the AGENTS hard limit.
- `git diff --check`
  - Result: passed with LF/CRLF warnings only.
- Trailing whitespace scan on TASK_357C touched files:
  - Result: no matches.
- Forbidden-scope scan:
  - `git diff --name-only --ignore-cr-at-eol` was scanned for Fee, Test Record, Report, LTR/public-drive, Project Workbench, Projects registry, `.agents/**`, `docs/project_management/**`, release/package scripts, `dist_release`, and `temp_agents_stash`.
  - Result: no TASK_357C content diff matched forbidden scope.

## External Residuals Excluded

The working tree remains dirty with pre-existing/external residuals. They are not part of TASK_357C and were not cleaned or packaged:

- `docs/task_board.md` source-of-truth/reconciliation residual.
- release/desktop/packaging files under `backend/desktop/**`, `dist_release/**`, `packaging/**`, and release scripts/tests.
- Settings/LTR/template helper residuals such as `backend/api/routes_settings.py`, LTR workbook settings services, template resource services, and their tests.
- New Project residual `frontend/src/features/new-project/newProjectRequiredState.test.ts`.
- TASK_357A and discovery docs/evidence residuals.
- `temp_agents_stash.md`.

## Known Residuals / Reviewer Notes

- `backend/api/routes_project_matrix_drafts.py` remains over 500 lines from existing code, but TASK_357C has no content diff in that file.
- `backend/api/dependencies.py` appears in `git status` because of line-ending noise only; `git diff -- backend/api/dependencies.py backend/api/routes_project_matrix_drafts.py` shows no content diff.
- Browser smoke was not run in this Developer thread. QA should smoke Matrix Editor group selection, Step quantity editing, save, reload, confirmation copy, and revision carry-forward if a seeded project is available.

## B1 Developer Fix Pass

Reviewer blocker: no-suffix Matrix Step quantity identity uniqueness was not enforced because SQLite allows duplicate `NULL` values in unique constraints, and `MatrixStepQuantityService.save_draft` did not reject duplicate payload identities before persistence.

Fix summary:

- Changed draft and confirmed Step quantity storage models so `step_suffix_note` is non-null and no-suffix records are persisted as `""` for unique-constraint identity.
- Kept API/domain read shape stable by converting the persisted `""` suffix back to `None` when loading repository domain records.
- Added shared service-level identity normalization for suffix values so `None`, empty, and whitespace suffixes compare as the same no-suffix Step identity.
- Added service-level duplicate payload rejection before persistence with `MatrixStepQuantityValidationError`.
- Added focused regression tests for service duplicate payload rejection, API duplicate payload rejection, draft repository no-suffix storage uniqueness, and confirmed authority no-suffix storage uniqueness.
- Did not change Fee, Test Record, Report, StepInstance, Matrix parser, Basic Information mutation, LTR/public-drive, Project Workbench, Projects registry, release/package, `.agents/**`, or `docs/project_management/**` scope.

B1 validation:

- Red checks before fix:
  - `py -m pytest tests/unit/test_matrix_step_quantity_service.py::test_step_quantity_save_rejects_duplicate_no_suffix_payload_identities -q` failed because no validation error was raised.
  - `py -m pytest tests/unit/test_project_matrix_draft_repository.py::test_project_matrix_draft_repository_rejects_duplicate_no_suffix_step_quantity -q` failed because duplicate no-suffix draft rows committed.
  - `py -m pytest tests/unit/test_confirmed_matrix_authority_repository.py::test_confirmed_matrix_authority_repository_rejects_duplicate_no_suffix_step_quantity -q` failed because duplicate no-suffix confirmed rows committed.
  - `py -m pytest tests/integration/test_matrix_step_quantity_api.py::test_matrix_step_quantity_api_rejects_duplicate_no_suffix_payload -q` failed with `200` instead of `422`.
- Focused B1 regression checks after fix:
  - Each of the four red checks above passed.
- Backend focused suite:
  - `py -m pytest tests/unit/test_matrix_step_quantity_service.py tests/integration/test_matrix_step_quantity_api.py tests/unit/test_project_matrix_draft_repository.py::test_project_matrix_draft_repository_replaces_step_quantities tests/unit/test_project_matrix_draft_repository.py::test_project_matrix_draft_repository_rejects_duplicate_no_suffix_step_quantity tests/unit/test_confirmed_matrix_authority_repository.py::test_confirmed_matrix_authority_repository_roundtrips_step_quantities tests/unit/test_confirmed_matrix_authority_repository.py::test_confirmed_matrix_authority_repository_rejects_duplicate_no_suffix_step_quantity tests/unit/test_confirmed_matrix_authority_service.py tests/unit/test_matrix_revision_flow_service.py tests/integration/test_matrix_revision_flow_api.py -q`
  - Result: `30 passed`.
- Frontend focused tests:
  - `npm test -- MatrixEditorWorkspace --run`
  - Result: `1 file / 39 tests passed`.
- Frontend build:
  - `npm run build`
  - Result: passed with existing Vite chunk-size warning only.
- Python compile:
  - `py -m py_compile backend/application/matrix_step_quantity_service.py backend/application/matrix_step_quantity_authority_builder.py backend/application/confirmed_matrix_authority_service.py backend/application/matrix_revision_flow_service.py backend/infrastructure/storage/repositories/project_matrix_draft.py backend/infrastructure/storage/repositories/confirmed_matrix_authority.py backend/api/routes_matrix_step_quantities.py backend/api/main.py backend/domain/project_matrix_draft_models.py backend/domain/confirmed_matrix_authority_models.py backend/infrastructure/storage/models_project_matrix_draft.py backend/infrastructure/storage/models_confirmed_matrix_authority.py`
  - Result: passed.
- Line-count check after fix:
  - `backend/application/matrix_step_quantity_service.py`: 421 lines.
  - `backend/application/matrix_step_quantity_authority_builder.py`: 120 lines.
  - `backend/application/confirmed_matrix_authority_service.py`: 310 lines.
  - `backend/application/matrix_revision_flow_service.py`: 491 lines.
  - `backend/infrastructure/storage/repositories/project_matrix_draft.py`: 394 lines.
  - `backend/infrastructure/storage/repositories/confirmed_matrix_authority.py`: 329 lines.
  - `backend/api/routes_matrix_step_quantities.py`: 180 lines.
  - Result: all checked TASK_357C Python files remain under the AGENTS hard limit.
- `git diff --check`
  - Result: passed with LF/CRLF warnings only.
- Trailing whitespace scan on TASK_357C touched files:
  - Result: no matches.
- Forbidden-scope content diff scan:
  - Result: no TASK_357C content diff in Fee/Test Record/Report/LTR/public-drive/Project Workbench/Projects registry/`.agents/**`/`docs_project_management/**`/release/package scopes.

## Decision

Completion status: B1 fix pass complete - ready for Reviewer implementation re-gate.

Recommended next role: Reviewer implementation re-gate.

Blocking summary: none.
