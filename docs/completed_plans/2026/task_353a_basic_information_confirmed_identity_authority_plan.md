# TASK_353A Basic Information Confirmed Identity Authority Plan

Status: complete/accepted - Integrator packaging/readiness accepted
Task: `TASK_353A_BASIC_INFORMATION_CONFIRMED_IDENTITY_AUTHORITY`
Lane: `basic-information-confirmed-identity-authority`
Date: 2026-07-07
Role: Planner

## Discovery Gate

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task/lane: TASK_353A is complete/accepted after controlled Developer, Reviewer, QA, and Integrator gates.

Why allowed: the user explicitly asked Planner to run Discovery Gate and authorized approved lane creation if Definition of Ready is satisfied. The lane later passed Developer implementation, Reviewer implementation gate, QA gate, and Integrator packaging/readiness.

## User Goal Restatement

ConnLab should show one project identity across Workbench, Matrix Editor, Fee Evaluation, Project list, and Basic Information: DL number + Product Description + Test Item. Intake setup values remain the creation-time draft/default identity. Once the user confirms Basic Information, confirmed Product Description and Test Item become the local display authority. This must not mutate original intake data, LTR notes, LTR Excel, or public-drive authority.

## Evidence Read

Governance:

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `$impeccable` product context from `PRODUCT.md` / `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`

Repository/code facts:

- `frontend/src/pages/IntakeInboxPage.tsx`
- `backend/application/new_project_completion_service.py`
- `backend/application/project_basic_information_service.py`
- `backend/application/project_basic_information_output.py`
- `backend/infrastructure/storage/repositories/project_basic_information.py`
- `backend/application/project_identity.py`
- `backend/application/project_registry_summary_service.py`
- `backend/api/routes_project.py`
- `backend/api/routes_project_basic_information.py`
- `backend/api/dependencies.py`
- `frontend/src/features/projectIdentity.ts`
- `frontend/src/features/project-basic-information/useProjectBasicInformationModel.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
- `frontend/src/pages/ProjectListPage.tsx`
- focused backend/frontend tests around project registry, Basic Information, Workbench, Matrix Editor, Fee Evaluation, and Project list identity displays.

## Confirmed By User

- Intake setup Sample Description / Test Item are pre-project draft values and may be manually corrected before project creation.
- Apply LTR Number / project creation should use these setup values as the project initial identity source.
- Basic Information initial Product Description / Test Item should prefer this initial identity.
- Confirmed Basic Information Product Description / Test Item become the current local project display identity authority.
- All top/display identity surfaces should update after Confirm.
- Without confirmed Basic Information, existing Intake/LTR identity fallback remains.
- Basic Information Confirm must not write back to original application form, intake raw parsed data, LTR notes, LTR Excel, or public-drive authority.

## Confirmed By Repository Evidence

- Intake autosave persists `project_setup` in `IntakeInboxPage.tsx`.
- New Project completion serializes setup values into `new_project_setup_confirmation` operator notes in `new_project_completion_service.py`.
- Basic Information suggestions already read `project.product_name` for `product_description` and LTR setup payload for `test_item`.
- Confirmed Basic Information records and a latest-confirmed repository method already exist; no schema change is required for latest confirmed identity reads.
- `project_identity.py` currently resolves `sample_description` from `project.product_name` or LTR setup payload and `test_item` from LTR setup payload, without consulting confirmed Basic Information.
- `ProjectRegistrySummaryService` is the shared source for `/api/projects/registry`, `/api/projects`, and `/api/projects/{project_id}` identity fields.
- Frontend title consumers already use `buildProjectIdentityLine(...)` or project API fields, so backend read-model priority can update most surfaces without page-specific title code.

## Inferred By Planner

- The implementation should be a backend read-model priority change plus small frontend refresh/test adjustments.
- Add a small identity override concept rather than duplicating Basic Information parsing in every API route.
- `ProjectRegistrySummaryService` should receive a Basic Information reader/repository dependency and pass the latest confirmed override into `resolve_project_identity(...)`.
- Basic Information Confirm should refresh `getProject(...)` or the Workbench route model after confirm so the identity line changes immediately.
- `Project.product_name` may remain stored as the initial identity; this lane changes display/read-model priority only.

## Not Yet Confirmed

- Whether confirmed `description_pn` should fill display identity if confirmed `product_description` is blank. Planner keeps this out of scope for V1 and preserves existing fallback.
- Whether temporary/no-LTR projects should display confirmed Basic Information product/test identity. Planner includes this where confirmed Basic Information exists, while keeping the temporary ID as the reference.

These do not block approved lane activation because they are documented as bounded assumptions/non-goals.

## Planning Risk

- Updating only one page would leave Project API, Project list, Matrix Editor, and Fee Evaluation inconsistent.
- Writing confirmed values back into source records would corrupt authority boundaries.
- Mixing this lane with existing TASK_352/release/Settings residuals would create packaging risk.
- Adding schema or broad Basic Information refactors would expand a read-model fix into a larger authority migration.

## Implementation Design Draft

Backend:

1. Add a confirmed Basic Information display identity adapter, likely in `project_identity.py` or a small adjacent dataclass.
2. Use latest confirmed `product_description` as `sample_description` / display product label when present.
3. Use latest confirmed `test_item` as `test_item` when present.
4. Preserve existing fallback to `project.product_name` and LTR setup payload when no confirmed Basic Information identity exists.
5. Wire `ProjectRegistrySummaryService` through `backend/api/dependencies.py` to the Basic Information repository/reader.
6. Keep `routes_project.py` response DTOs unchanged if existing `sample_description` / `test_item` fields are sufficient.

Frontend:

1. Keep `buildProjectIdentityLine(...)` as the shared display helper.
2. After Basic Information Confirm, ensure the current route/workbench model refreshes Project API data, not just Basic Information data.
3. Add focused tests for updated identity display in the affected surfaces.

## May Touch

- `backend/application/project_identity.py`
- `backend/application/project_registry_summary_service.py`
- `backend/application/project_basic_information_service.py` only for focused initial-suggestion clarification if needed.
- `backend/api/dependencies.py`
- `backend/api/routes_project.py` only for response-mapping alignment if needed.
- `tests/unit/test_project_registry_summary_service.py`
- `tests/integration/test_project_registry_summary_api.py`
- `tests/unit/test_project_basic_information_service.py`
- `tests/integration/test_project_basic_information_api.py`
- `frontend/src/features/projectIdentity.ts`
- `frontend/src/features/project-basic-information/useProjectBasicInformationModel.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx`
- Focused identity display tests for Matrix Editor, Fee Evaluation, and Project list as needed.
- TASK_353A docs/evidence/board.

## Must Not Touch / Locked Paths

- LTR Excel / public-drive workbook write authority.
- Intake raw parsing rules and original application form data.
- Database schema/migrations.
- Matrix parser, Fee calculation/default-fill rules, Folder Actions workflows, Report, StepInstance, AI, permissions, LAN/server, multi-user.
- Real public-drive/workbook/folder data.
- Unrelated dirty files, release/packaging residuals, Settings/LTR residuals, TASK_352 residuals.
- `.agents/**`
- `docs/project_management/**`

Locked paths:

- `backend/infrastructure/office/**`
- `backend/modules/fee_evaluation/**`
- `backend/application/public_folder_*`
- `backend/infrastructure/files/public_folder_*`
- `D:\Test Project/**`
- `D:\PublicProject/**`
- real public-drive roots and real LTR workbook files.

## Acceptance Criteria

1. With latest confirmed Basic Information, Project API and Project registry rows expose confirmed `product_description` as `sample_description` and confirmed `test_item` as `test_item`.
2. Without latest confirmed Basic Information, existing Intake/LTR setup fallback remains unchanged.
3. Basic Information initial draft still prefers project initial identity from Intake/LTR setup where currently available.
4. Basic Information Confirm does not mutate original intake/application-form data, LTR notes, LTR workbook, or public-drive authority.
5. After Confirm, Workbench / Matrix Editor / Fee Evaluation / Project list identity displays update through shared Project API/read-model data.
6. Frontend continues using `buildProjectIdentityLine(...)` rather than duplicating title concatenation.

## Validation Gate Draft

- `py -m pytest tests/unit/test_project_registry_summary_service.py tests/integration/test_project_registry_summary_api.py -q`
- `py -m pytest tests/unit/test_project_basic_information_service.py tests/integration/test_project_basic_information_api.py -q`
- focused frontend tests for Basic Information confirm refresh and identity display consumers.
- `npm run build`
- `git diff --check`
- trailing whitespace scan.
- forbidden-scope scan for LTR workbook/public-drive/schema/Matrix parser/Fee/Folder Actions/future-scope changes.

## Merge Gate Draft

- Developer evidence `ready_for_review`.
- Reviewer implementation gate pass.
- QA/browser smoke required for the visible confirm-to-title-update workflow.
- Integrator packaging/readiness must confirm only approved TASK_353A files are included and external residuals are excluded.
- Remote push is not authorized.

## Definition Of Ready

Ready for approved lane activation: yes.

Rationale:

- User goal and workflow are explicit.
- Current board state and predecessor completion are verified.
- Existing identity path, Basic Information authority records, API surfaces, and frontend consumers were checked from repository files.
- May Touch, Must Not Touch, Locked Paths, evidence, validation gate, and merge gate are concrete.
- The first acceptance path is testable through backend read-model/API tests and frontend identity refresh tests.
- Authority non-goals are explicit.

## Closeout

`TASK_353A_BASIC_INFORMATION_CONFIRMED_IDENTITY_AUTHORITY` is complete/accepted locally. The accepted package is limited to the approved backend display identity/read-model files, focused registry tests, TASK_353A task/plan/evidence, and board closeout. External TASK_352, Settings/LTR, release/desktop/packaging, New Project test, temp stash, `.agents/**`, and `docs/project_management/**` residuals remain excluded. Remote push is not authorized.
