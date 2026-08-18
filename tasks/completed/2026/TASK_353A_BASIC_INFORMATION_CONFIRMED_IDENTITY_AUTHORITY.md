# TASK_353A_BASIC_INFORMATION_CONFIRMED_IDENTITY_AUTHORITY

Status: complete/accepted - Integrator packaging/readiness accepted
Lane: basic-information-confirmed-identity-authority
Owner: Planner / Developer / Reviewer / QA / Integrator
Created: 2026-07-07

## Goal

Make the project display identity consistent across ConnLab by resolving the top identity line as:

```text
DL number + Product Description + Test Item
```

When latest confirmed Basic Information exists, it is the local project display identity authority for `Product Description` and `Test Item`. When no confirmed Basic Information exists, existing Intake/LTR setup identity fallback remains unchanged.

## Current Phase And Authorization

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current board context: TASK_352 PDF Matrix import deterministic preview is complete/accepted; TASK_353A is complete/accepted after Reviewer, QA, and Integrator gates.
- User explicitly authorized Planner Discovery Gate and allowed approved lane creation if Definition of Ready is satisfied.
- Definition of Ready is satisfied from repository evidence and user-confirmed business rules.
- This lane is accepted locally after controlled packaging/readiness; remote push is not authorized.

## Confirmed By User

- Intake `Project setup confirmation` Sample Description / Test Item values are pre-project draft values extracted from the application form and manually correctable.
- These draft values are autosaved and should become the project initial identity source when Apply LTR Number / project creation runs.
- Basic Information `Product Description *` and `Test Item *` should initially prefer the project initial identity.
- After Basic Information Confirm, confirmed `Product Description *` and `Test Item *` become the current local project display identity authority.
- Workbench, Matrix Editor, Fee Evaluation, Project list, and Basic Information top identity display should update to DL number + confirmed Product Description + confirmed Test Item.
- If no confirmed Basic Information exists, fallback remains Intake/LTR initial identity.
- Basic Information Confirm must not write back to the original application form, Intake parsed data, LTR notes, LTR Excel, or public-drive authority.

## Confirmed By Repository Evidence

- `frontend/src/pages/IntakeInboxPage.tsx` autosaves `project_setup` and maps setup values to `test_item` / `sample_description`.
- `backend/application/new_project_completion_service.py` stores setup values in `new_project_setup_confirmation` operator notes during Apply LTR completion.
- `backend/application/project_basic_information_service.py` assembles Basic Information suggestions from project identity and setup payload, and persists confirmed Basic Information records without schema changes.
- `backend/application/project_basic_information_output.py` and `backend/infrastructure/storage/repositories/project_basic_information.py` already expose latest confirmed Basic Information snapshots.
- `backend/application/project_identity.py` is the shared resolver for project display identity but currently uses `project.product_name` and LTR setup payload only.
- `backend/application/project_registry_summary_service.py` builds `/api/projects/registry` rows from `resolve_project_identity(...)`, and `backend/api/routes_project.py` maps registry row `sample_description` / `test_item` into `GET /api/projects` and `GET /api/projects/{project_id}`.
- `frontend/src/features/projectIdentity.ts` centralizes the frontend identity line builder, and Workbench, Matrix Editor, Fee Evaluation, Basic Information, and Project list consumers already rely on Project API identity fields or the shared builder.

## Inferred By Planner

- This can be implemented as a read-model/resolver update with focused tests; no database schema change is required because confirmed Basic Information records already exist.
- The cleanest backend boundary is to make `project_identity.py` accept/read a latest confirmed Basic Information snapshot or an explicit `ProjectDisplayIdentityOverride`.
- `ProjectRegistrySummaryService` should receive a Basic Information reader/repository dependency so registry rows, project list rows, and project detail rows share the same priority.
- Basic Information Confirm should ensure the frontend refreshes `getProject(...)` or route-level project context after the confirm response, so the top identity updates immediately instead of waiting for a page reload.
- Frontend pages should continue using `buildProjectIdentityLine(...)`; avoid per-page title concatenation logic.

## Not Yet Confirmed

- Whether `description_pn` should be used as a fallback when confirmed `product_description` is empty. Lane assumption: use confirmed `product_description` only for display override, and keep existing fallback otherwise. This does not block implementation because the user named Product Description as the display source.
- Whether temporary projects without LTR should also use confirmed Basic Information for product/test identity after confirmation. Lane assumption: yes for local display identity where Basic Information exists, while the temporary project ID remains the reference until LTR registration.

## May Touch

- `backend/application/project_identity.py`
- `backend/application/project_registry_summary_service.py`
- `backend/application/project_basic_information_service.py` only if needed to clarify initial Basic Information suggestions from project setup.
- `backend/api/dependencies.py`
- `backend/api/routes_project.py` only if response mapping needs minor alignment.
- `tests/unit/test_project_registry_summary_service.py`
- `tests/integration/test_project_registry_summary_api.py`
- `tests/unit/test_project_basic_information_service.py` or `tests/integration/test_project_basic_information_api.py` only for focused initial identity / confirm behavior coverage.
- `frontend/src/features/projectIdentity.ts` only if shared identity fallback behavior needs a focused helper adjustment.
- `frontend/src/features/project-basic-information/useProjectBasicInformationModel.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts` and focused tests only if immediate post-confirm refresh requires Workbench model alignment.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`, `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`, and `frontend/src/pages/ProjectListPage.test.tsx` only for identity display regressions.
- TASK_353A docs/evidence/board.

## Must Not Touch

- LTR Excel / public-drive workbook write authority rules.
- Intake raw parsing rules, unless implementation proves a minimal read-only source bug and returns to Planner/Reviewer.
- Database schema/migrations.
- Matrix parser, Fee calculation/default-fill rules, Folder Actions workflows, Report generation, StepInstance/execution persistence, AI, permissions, LAN/server, or multi-user scope.
- Real public-drive/workbook/folder data.
- Unrelated dirty files, release/packaging residuals, Settings/LTR residuals, TASK_352 residuals.
- `.agents/**`
- `docs/project_management/**`

## Locked Paths

- `backend/infrastructure/office/**`
- `backend/modules/fee_evaluation/**`
- `backend/application/public_folder_*`
- `backend/infrastructure/files/public_folder_*`
- `frontend/src/features/matrix-editor/**` except focused identity display tests if needed.
- `frontend/src/features/fee-evaluation/**` except focused identity display tests if needed.
- `frontend/src/pages/ProjectListPage.tsx` unless Planner/Reviewer later approves a copy-only display defect.
- `D:\Test Project/**`
- `D:\PublicProject/**`
- real public-drive roots and real LTR workbook files.
- `.agents/**`
- `docs/project_management/**`

## Validation Gate

Developer must provide evidence for:

- Backend unit tests proving latest confirmed Basic Information `product_description` / `test_item` override Project API and registry identity fields.
- Backend unit/API tests proving no confirmed Basic Information keeps existing Intake/LTR setup fallback.
- Basic Information initial draft still receives project setup identity from Intake/LTR setup payload.
- Frontend focused tests proving Basic Information Confirm can refresh the project read model or relevant route state so Workbench/title consumers show updated identity.
- Focused identity display regressions for Workbench, Matrix Editor, Fee Evaluation, and Project list where practical.
- `npm run build`.
- `git diff --check`.
- Forbidden-scope/status scan proving no LTR workbook/public-drive/schema/Matrix parser/Fee/Folder Actions/future-scope changes were included.

## Merge Gate

- Developer evidence must be `ready_for_review`.
- Reviewer implementation gate must pass with no blocking findings.
- QA/browser smoke is required because this is a user-visible identity display flow.
- Integrator must verify package isolation from existing TASK_352, release/packaging, Settings/LTR, and unrelated dirty residuals before updating global completion status.
- Remote push is not authorized.

## Stop Point

TASK_353A is complete/accepted locally after Developer implementation, Reviewer implementation gate, QA gate, and Integrator packaging/readiness. Recommended next role: Orchestrator/User routing decision for the next approved lane. Remote push is not authorized.
