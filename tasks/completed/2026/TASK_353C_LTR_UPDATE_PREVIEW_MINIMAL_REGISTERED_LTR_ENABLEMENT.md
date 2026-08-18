# TASK_353C LTR Update Preview Minimal Registered LTR Enablement

Status: complete/accepted by Integrator
Lane: `ltr-update-preview-minimal-registered-ltr-enablement`
Owner role: Integrator packaging/readiness
Created: 2026-07-07

## Goal

Correct the post-acceptance TASK_353B direction. The accepted TASK_353B package added an independent `LTR workbook row preview` button/card/API/service workflow, but the user clarified that this was overbuilt.

The intended behavior is smaller: keep the original `LTR update preview` entry and allow a registered LTR project to click it even before Basic Information is confirmed. The preview should use the project's initial Basic Information/project setup fallback as the left-side pending source when no confirmed Basic Information exists. Existing workbook update/commit safety must remain intact.

## Source-Of-Truth Reconciliation

The corrective scope has passed implementation review and QA, but the implementation evidence was appended under TASK_353B because it corrected the accepted TASK_353B package. Repository source-of-truth is reconciled here:

- User corrected TASK_353B after acceptance and requested the minimal `LTR update preview` behavior.
- Planner created TASK_353C as the post-acceptance corrective lane.
- Reviewer plan gate passed in `docs/lane_evidence/TASK_353C_ltr-update-preview-minimal-registered-ltr-enablement_reviewer.md`.
- Developer correction fix pass completed in `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_developer.md`.
- Reviewer correction re-gate passed in `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_reviewer.md`.
- QA correction pass is recorded in `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_qa.md`.
- Planner reconciliation records that TASK_353C is ready for Integrator packaging/readiness, not complete.

## User-Corrected Rules

- Do not treat commit `66169664` as the final product direction despite Integrator acceptance.
- Remove the independent `LTR workbook row preview` button, card, read-only workflow, API/service/client wiring, and focused tests if they are no longer needed.
- Keep the original `LTR update preview` entry, layout, and interaction model with only minimal copy clarification if needed.
- Enable the original preview when the project has a registered DL/LTR number.
- Basic Information not being confirmed must not block opening the preview.
- The preview's left side may use initial Basic Information/project setup fallback data.
- Keep existing `Confirm update` / commit safety semantics. Preview availability must not automatically authorize workbook writes.
- Do not add a second LTR workbook preview user entry.

## Confirmed Repository Context

- `docs/task_board.md` marks `TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW` complete/accepted.
- Commit `66169664` added:
  - `backend/application/registered_ltr_workbook_row_preview_service.py`
  - `backend/api/routes_ltr_workbook_registered_row_preview.py`
  - typed client helper and DTOs in `frontend/src/api/client.ts`
  - a separate `LTR workbook row preview` action/panel in `ProjectBasicInformationSummaryCard`
  - Workbench registered-LTR prop wiring
  - focused registered-row preview backend/API/frontend tests
- Current `ProjectBasicInformationSummaryCard` renders both `LTR workbook row preview` and `Update LTR from Basic Information`.
- Current `LtrWorkbookBasicInformationSyncService.preview(...)` requires latest confirmed Basic Information before it can build the update preview.
- Current commit/update path already requires preview acknowledgement, operator confirmation, expected confirmed Basic Information version/hash, lifecycle write permission, and workbook write transaction.

## Preview Versus Commit Contract

Preview:

- May be opened when the project has a registered DL/LTR.
- May use initial Basic Information/project setup fallback if no confirmed Basic Information exists.
- Must read the current workbook row and show pending values for review.
- Must not write to the workbook.
- Must not create a second user-facing preview action.

Commit/update:

- Must remain protected by existing explicit operator confirmation and workbook write safeguards.
- If the implementation cannot safely commit from initial fallback data, commit must stay disabled or blocked until confirmed Basic Information exists.
- Must not silently write fallback values to the workbook.
- Must not weaken lifecycle write guard, preview acknowledgement, version/hash, workbook transaction, or exact registered-LTR row checks.

## May Touch

Future Developer implementation may touch only the following, unless Reviewer plan gate narrows or explicitly expands scope:

- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx`
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx` and `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx` only to remove now-unneeded registered-row-only props or preserve required registered-LTR enablement.
- `frontend/src/api/client.ts` only to remove TASK_353B registered-row preview DTO/helper or adjust existing Basic Information sync DTOs if required.
- `backend/application/ltr_workbook_basic_information_sync_service.py` only to allow preview construction from initial Basic Information/project setup fallback while preserving commit safety.
- `backend/api/routes_ltr_workbook_basic_information_sync.py` only if response mapping for preview blockers/fallback metadata needs adjustment.
- `backend/api/dependencies.py` and `backend/api/main.py` only to unregister/remove TASK_353B registered-row preview route/service.
- `backend/application/registered_ltr_workbook_row_preview_service.py` and `backend/api/routes_ltr_workbook_registered_row_preview.py` for removal.
- `tests/unit/test_registered_ltr_workbook_row_preview_service.py` and `tests/integration/test_registered_ltr_workbook_row_preview_api.py` for removal if the independent workflow is removed.
- Existing Basic Information sync backend/API tests and focused frontend tests.
- `docs/lane_evidence/TASK_353C_ltr-update-preview-minimal-registered-ltr-enablement_developer.md`.
- TASK_353C task/plan/evidence/board through normal lane flow.

## Must Not Touch

- LTR Excel/public-drive workbook authority write rules.
- Existing Basic Information sync commit safety gate, except to keep it at least as strict as before.
- Intake original parsing, specified-LTR authority preview, or local duplicate semantics.
- Database schema or migrations.
- Matrix parser/import, Fee calculation/export, Folder Actions/public folder workflow, Report, StepInstance, AI, permissions, LAN/server, multi-user.
- Real LTR workbooks, real public-drive folders, or real user folders.
- Release/settings/template residual cleanup or unrelated dirty files.
- `.agents/**`, `docs/project_management/**`, or remote push.

## Locked Paths

- Real LTR workbook files and public-drive roots.
- Database schema/migration files.
- Matrix/Fee/Folder Actions runtime modules outside focused tests.
- Release/packaging paths and current external residual files.
- `.agents/**` and `docs/project_management/**`.

## Validation Gate Draft

Backend:

- Original Basic Information LTR update preview can produce a preview for a registered LTR project without confirmed Basic Information by using initial Basic Information/project setup fallback.
- Project without registered LTR remains blocked or disabled.
- Confirm update / commit still requires existing safety checks and must not write from unconfirmed fallback data unless explicitly proven safe and Reviewer-approved.
- TASK_353B independent registered-row preview service/route tests are removed or no longer referenced if the workflow is removed.
- Existing Basic Information sync preview/commit regression tests still pass.

Frontend:

- Only one user-facing LTR workbook action remains in the Basic Information side card: the original `LTR update preview` entry or minimally clarified equivalent.
- No independent `LTR workbook row preview` button/card/table remains visible.
- `LTR update preview` is enabled when registered LTR exists even if Basic Information is not confirmed.
- Preview displays initial Basic Information/project setup fallback on the pending side when no confirmed Basic Information exists.
- No registered LTR still disables or blocks the action.
- Commit/update controls remain disabled or blocked until the original commit safety contract is satisfied.

Commands:

- Focused pytest for Basic Information LTR sync service/API and any fallback-source tests.
- `npm test -- ProjectBasicInformationSummaryCard --run`
- Workbench focused tests if prop wiring changes.
- `npm run build`
- `git diff --check`
- trailing whitespace scan
- forbidden-scope/status scan confirming independent registered-row preview route/service/client/UI is removed and no unrelated residuals are packaged.

## Merge Gate Draft

- Reviewer plan gate must pass before Developer planning or implementation.
- User/source-of-truth authorization is required before Developer implementation.
- Developer evidence must list removed TASK_353B independent workflow files and changed fallback/enablement files.
- Reviewer implementation gate must confirm preview is opened through the original entry and commit safety is not weakened.
- QA smoke should verify the registered-LTR unconfirmed-Basic-Information case, no-LTR blocker, no second button/card, and commit gate preservation.
- Integrator packaging must isolate TASK_353C and exclude unrelated residuals.
- Remote push is not authorized.

## Definition Of Ready

Reviewer plan gate: passed.

Developer correction fix pass: complete.

Reviewer correction re-gate: passed.

QA correction pass: passed.

TASK_353C is complete/accepted after Integrator isolated the corrective package, validated merge/readiness, and updated board closeout.
