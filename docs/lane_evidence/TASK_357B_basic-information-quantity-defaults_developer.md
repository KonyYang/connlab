# TASK_357B Basic Information Quantity Defaults Developer Evidence

Status: implementation complete - pending Reviewer implementation gate
Task: `TASK_357B_BASIC_INFORMATION_QUANTITY_DEFAULTS`
Lane: `basic-information-quantity-defaults`
Date: 2026-07-08
Role: Developer

## Routing Summary

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current board state: TASK_357A is accepted as the contract/downstream basis; TASK_357B is planned with Reviewer plan gate passed.
- Why allowed: user explicitly approved TASK_357B Developer planning-first.
- Stop point: Developer planning-first only. Product implementation remains not authorized.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `$impeccable` product context via `node .agents/skills/impeccable/scripts/load-context.mjs`
- `.agents/skills/impeccable/reference/product.md`
- `tasks/TASK_357B_BASIC_INFORMATION_QUANTITY_DEFAULTS.md`
- `docs/task_357b_basic_information_quantity_defaults_plan.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_planner.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_reviewer.md`
- `docs/lane_evidence/TASK_357A_matrix-quantity-authority-contract_reconciliation_planner.md`
- TASK_357A task/plan/planner/developer/reviewer/discovery context
- `backend/application/project_basic_information_service.py`
- `backend/api/routes_project_basic_information.py`
- `backend/infrastructure/storage/repositories/project_basic_information.py`
- `backend/infrastructure/storage/models.py`
- `backend/infrastructure/storage/database.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-basic-information/basicInformationFieldConfig.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx`
- `frontend/src/features/project-basic-information/useProjectBasicInformationModel.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`
- `tests/unit/test_project_basic_information_service.py`
- Matrix/Fee/Test Record downstream facts from TASK_357A and targeted searches
- `git status --short`

## Repository Facts Confirmed

- Basic Information records store `values_json` and `source_signature_json`; repository domain objects expose `values: dict[str, str]`.
- Basic Information API request/response DTOs already use a generic `values` map.
- Basic Information frontend fields are generated from `basicInformationFieldConfig.ts`; the page should stay config-driven.
- Existing service tests cover draft save, confirmed priority, source review, required fields, and versioning.
- No existing product code defines `test_points_per_sample`, `readings_per_point`, `contact_points_per_sample`, or persisted `total_readings` outside TASK_357 docs.
- Matrix/Fee/Test Record code paths do not consume Basic Information quantity defaults today and must stay locked for this lane.

## Planning Decisions Written

Updated `docs/task_357b_basic_information_quantity_defaults_plan.md` with:

- backend strategy to store the first three quantity defaults in the existing Basic Information values map;
- no schema migration for V1 unless implementation proves the values-map strategy cannot satisfy validation;
- service-level optional decimal validation and business-readable confirm errors;
- API strategy to keep existing endpoints and values-map shape;
- draft versus confirmed semantics and downstream TASK_357C source precedence;
- `total_readings` decision: do not store as primary Basic Information input in V1; treat as derived/read-only display or omit until Matrix Step setup;
- UI strategy using a compact `Quantity defaults` group in the existing Basic Information config-driven surface;
- exact future May Touch and locked paths;
- focused backend/frontend validation plan and package isolation risks.

## May Touch Used

- `docs/task_357b_basic_information_quantity_defaults_plan.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_developer.md`

## Must Not Touch / Locked Scope Observed

No backend, frontend, tests, API client, Matrix Editor, Fee Evaluation, Matrix authority, Test Record/Report, LTR workbook/public-drive authority, real workbook/folder data, `.agents/**`, or `docs/project_management/**` files were modified by this Developer planning-first pass.

External residuals remain visible in the worktree, including Settings/LTR helper files, backend desktop/release helpers, `dist_release/**`, `packaging/**`, frontend New Project test residuals, release/settings tests, `temp_agents_stash.md`, and pre-existing TASK_357A/357B docs/board files. They are excluded from TASK_357B.

## Validation

- Required docs/evidence existence check passed:
  - `docs/task_357b_basic_information_quantity_defaults_plan.md`
  - `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_developer.md`
  - `tasks/TASK_357B_BASIC_INFORMATION_QUANTITY_DEFAULTS.md`
  - `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_planner.md`
  - `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_reviewer.md`
- `git diff --check -- docs/task_357b_basic_information_quantity_defaults_plan.md docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_developer.md` passed with no findings.
- Trailing whitespace scan on the TASK_357B plan and Developer evidence returned no matches.
- Targeted status for TASK_357B plan/evidence plus backend/frontend/tests/API client/governance locked paths shows this pass changed only TASK_357B planning/evidence docs.
- The same targeted status still shows pre-existing external residuals under backend Settings/LTR helpers, backend desktop/release helpers, frontend New Project tests, and focused release/settings tests. They were not modified by this TASK_357B Developer planning-first pass and remain excluded.

## Decision

Completion status: developer planning-first complete.

Recommended next role: Reviewer implementation-readiness gate.

Blocking summary: none.

Historical planning-first note: at that checkpoint, implementation remained unauthorized until Reviewer readiness, user approval, and source-of-truth reconciliation. The implementation pass below records the later authorization and completed Developer implementation.

---

## Implementation Pass

Date: 2026-07-08

Authorization read:

- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_reconciliation_planner.md`
- `tasks/TASK_357B_BASIC_INFORMATION_QUANTITY_DEFAULTS.md`
- `docs/task_357b_basic_information_quantity_defaults_plan.md`
- TASK_357A accepted contract context

Current authorization: implementation authorized / pending Developer implementation.

## Changed Files

- `backend/application/project_basic_information_service.py`
- `backend/application/project_basic_information_source.py`
- `backend/api/routes_project_basic_information.py`
- `frontend/src/features/project-basic-information/basicInformationFieldConfig.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`
- `tests/unit/test_project_basic_information_service.py`
- `tests/unit/test_project_basic_information_repository.py`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_developer.md`

## Implementation Summary

- Added Basic Information project-level quantity defaults in the existing values-map contract:
  - `test_points_per_sample`
  - `readings_per_point`
  - `contact_points_per_sample`
- Kept `total_readings` out of Basic Information persistence/UI for V1, matching the plan decision that it is derived/downstream rather than an operator-owned project default.
- Added backend confirm-time validation for optional quantity defaults:
  - blank values are allowed and cleaned out as before;
  - non-blank values must be non-negative decimals;
  - invalid values return a structured 422 with business-readable invalid field labels.
- Kept draft save permissive so operators can preserve work-in-progress and correct invalid values before confirmation.
- Added a compact `Quantity defaults` group to the existing config-driven Basic Information Laboratory execution panel.
- Added frontend confirm blocking and compact validation copy for invalid quantity defaults.
- Preserved closed/readonly Basic Information behavior; quantity default fields are disabled with the rest of the Basic Information form.
- Extracted Basic Information source suggestion assembly into `backend/application/project_basic_information_source.py` so `project_basic_information_service.py` remains under the AGENTS hard line limit after this implementation.

## Boundary Confirmation

- No schema migration was needed; quantity defaults use existing `values_json`.
- No Matrix Step override implementation.
- No Fee Evaluation consumption.
- No Test Record/Report reuse.
- No Matrix parser/import, LTR workbook/public-drive, or storage schema changes.
- No `.agents/**` or `docs/project_management/**` changes.
- Existing external residuals under Settings/LTR, desktop/release packaging, TASK_357A docs, New Project tests, and `temp_agents_stash.md` remain excluded.

## Validation Results

- `py -m pytest tests/unit/test_project_basic_information_service.py tests/unit/test_project_basic_information_repository.py -q` -> 19 passed.
- `py -m py_compile backend/application/project_basic_information_service.py backend/application/project_basic_information_source.py backend/api/routes_project_basic_information.py` -> passed.
- `npm test -- ProjectBasicInformationWorkspace --run` from `frontend` -> 1 file / 20 tests passed.
- `npm run build` from `frontend` -> passed with existing Vite chunk-size warning.
- `git diff --check` -> passed with existing LF/CRLF warnings only.
- Trailing whitespace scan on TASK_357B touched files -> no matches.
- Line-count check:
  - `backend/application/project_basic_information_service.py` -> 454 lines.
  - `backend/application/project_basic_information_source.py` -> 153 lines.
- Forbidden-scope status scan for Matrix/Fee/Workbench/API client/storage schema/`.agents`/`docs_project_management` locked paths -> no TASK_357B changes.

## Decision

Completion status: implementation complete - pending Reviewer implementation gate.

Recommended next role: Reviewer implementation gate.

Blocking summary: none.
