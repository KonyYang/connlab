# TASK_353A Basic Information Confirmed Identity Authority - Planner Evidence

Task ID: `TASK_353A_BASIC_INFORMATION_CONFIRMED_IDENTITY_AUTHORITY`
Lane: `basic-information-confirmed-identity-authority`
Role: Planner
Date: 2026-07-07
Status: approved - ready for Developer implementation pass

## Discovery Gate Result

Definition of Ready is satisfied. The lane is approved because the user explicitly authorized approved lane activation if DoR was met, and repository evidence proves the current identity read model, Basic Information confirmed snapshot capability, API response path, and frontend display consumers.

## Current Phase / Active Task / Why Allowed

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active board state: `TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW` complete/accepted.
- Current role: Planner.
- Why allowed: user requested TASK_353A creation/activation and full-auto orchestration, with this heartbeat limited to one Planner Discovery/lane-creation action.

## Confirmed By User

- Display identity should be DL number + Product Description + Test Item.
- Intake setup Sample Description / Test Item are editable creation-time draft values.
- Apply LTR Number / project creation uses those setup values as initial identity.
- Confirmed Basic Information Product Description / Test Item become the current local display identity authority.
- No confirmed Basic Information means existing fallback remains.
- Do not write confirmed Basic Information back to Intake raw data, original application form, LTR notes, LTR Excel, or public-drive authority.

## Confirmed By Repository Evidence

- `IntakeInboxPage.tsx` autosaves `project_setup`.
- `new_project_completion_service.py` stores setup values in `new_project_setup_confirmation` operator notes.
- `project_basic_information_service.py` already assembles Basic Information suggestions and persists confirmed records.
- `project_basic_information_output.py` / `ProjectBasicInformationRepository` already provide latest confirmed snapshot reads.
- `project_identity.py` and `ProjectRegistrySummaryService` currently do not consult confirmed Basic Information for display identity.
- `routes_project.py` maps registry row identity into Project API responses.
- `projectIdentity.ts`, Workbench, Matrix Editor, Fee Evaluation, and Project list already use Project API identity fields/shared helper.

## Inferred By Planner

- No schema change is needed.
- This is a read-model priority/update and frontend refresh/regression lane.
- Backend should centralize the Basic Information override in the shared identity resolver / registry summary path.
- Frontend should refresh Project API data after Basic Information Confirm instead of building page-specific titles.

## Not Yet Confirmed

- `description_pn` display fallback is not confirmed; excluded from V1 override unless existing fallback already reaches it.
- Temporary/no-LTR display behavior with confirmed Basic Information is inferred to follow the same product/test identity priority while keeping temporary ID as the reference.

These assumptions are bounded and do not block lane approval.

## May Touch / Must Not Touch / Locked Paths

See:

- `tasks/TASK_353A_BASIC_INFORMATION_CONFIRMED_IDENTITY_AUTHORITY.md`
- `docs/task_353a_basic_information_confirmed_identity_authority_plan.md`

## Validation Gate

Developer must provide backend read-model/API tests, frontend identity refresh/display tests, `npm run build`, `git diff --check`, trailing whitespace scan, and forbidden-scope/status scan.

## Merge Gate

Reviewer, QA, and Integrator gates are required. QA/browser smoke should verify Basic Information Confirm updates Workbench / Matrix Editor / Project list identity display. Remote push is not authorized.

## External Residuals Excluded

Current worktree contains unrelated residuals, including TASK_352 PDF import modified files, release/packaging artifacts, Settings/LTR helper files, desktop packaging files/tests, `dist_release/**`, `packaging/**`, and `temp_agents_stash.md`. They are not TASK_353A inputs and must not be packaged with this lane unless separately approved.

## Stop Point

Planner lane activation complete. Recommended next role: Developer implementation pass through Orchestrator. This Planner thread must not write product code or start Developer directly.

## Validation Checkpoint

Planner docs-only validation completed:

- `git diff --check -- docs/task_board.md tasks/TASK_353A_BASIC_INFORMATION_CONFIRMED_IDENTITY_AUTHORITY.md docs/task_353a_basic_information_confirmed_identity_authority_plan.md docs/lane_evidence/TASK_353A_basic-information-confirmed-identity-authority_planner.md` passed with only the existing LF/CRLF warning on `docs/task_board.md`.
- Trailing whitespace scan on the TASK_353A touched docs returned no matches.
- Targeted status confirmed this Planner pass touched only TASK_353A source-of-truth docs/board/evidence; visible backend/frontend/test changes are external residuals and remain excluded from TASK_353A.
