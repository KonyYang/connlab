# TASK_353C LTR Update Preview Minimal Registered LTR Enablement Plan

> Status: complete/accepted by Integrator
> Task: `TASK_353C_LTR_UPDATE_PREVIEW_MINIMAL_REGISTERED_LTR_ENABLEMENT`
> Lane: `ltr-update-preview-minimal-registered-ltr-enablement`
> Created: 2026-07-07

## 1. Discovery Gate

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active task/lane: `TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW` is complete/accepted in board and local commit `66169664`, but the user has explicitly rejected that accepted product direction.

Current role: Planner source-of-truth reconciliation.

Why allowed: QA reported the corrective implementation has passed Reviewer re-gate and QA but board/source-of-truth still says TASK_353C is planned. This pass reconciles documentation only and does not modify product code, package files, commit, or push.

## 1.1 Source-Of-Truth Reconciliation

The corrective implementation evidence lives mainly in TASK_353B role evidence because it corrected the already accepted TASK_353B package. This plan now records the durable TASK_353C state:

- User corrected the TASK_353B accepted direction and requested minimal `LTR update preview` enablement.
- Planner created TASK_353C as the corrective lane.
- Reviewer plan gate passed in `docs/lane_evidence/TASK_353C_ltr-update-preview-minimal-registered-ltr-enablement_reviewer.md`.
- Developer correction fix pass completed in `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_developer.md`.
- Reviewer correction re-gate passed in `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_reviewer.md`.
- QA correction pass is recorded in `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_qa.md`.
- TASK_353C is ready for Integrator packaging/readiness. It is not complete/accepted yet.

## 2. User Correction Restatement

The user does not want a new independent registered-LTR workbook row preview workflow. They only want the existing `LTR update preview` button/entry to be clickable for projects that already have a registered LTR number, even when Basic Information is not yet confirmed. That preview should be able to use the initial Basic Information/project setup values on the left/pending side. Everything else should remain as close to the original behavior as possible, especially the existing workbook update/commit safety model.

## 3. Evidence Read

Governance:

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`

UI/product context:

- `$impeccable` product context
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`

TASK_353B context:

- `tasks/TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW.md`
- `docs/task_353b_registered_ltr_workbook_row_preview_plan.md`
- `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_planner.md`
- `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_developer.md`
- `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_reviewer.md`
- `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_qa.md`
- commit `66169664`

Code facts:

- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `backend/application/ltr_workbook_basic_information_sync_service.py`
- `backend/application/registered_ltr_workbook_row_preview_service.py`
- `backend/api/routes_ltr_workbook_registered_row_preview.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`

## 4. Confirmed By User

- TASK_353B was overbuilt.
- The independent two-button/card direction is not the desired product behavior.
- The desired change is to keep the original `LTR update preview` entry.
- Registered-LTR projects should be able to click `LTR update preview`.
- Basic Information unconfirmed state should not block opening the preview.
- Preview should use/import the initial Basic Information/project setup values.
- Other behavior should remain as originally designed.
- Related added functionality should be withdrawn.

## 5. Confirmed By Repository Evidence

- Board marks TASK_353B complete/accepted and commit `66169664` exists locally.
- Commit `66169664` added independent registered-row preview files and UI/client wiring.
- `ProjectBasicInformationSummaryCard` currently imports `previewRegisteredLtrWorkbookRow`, holds `registeredRowPreview` state, and renders `LTR workbook row preview` separately from `Update LTR from Basic Information`.
- `frontend/src/api/client.ts` currently has `RegisteredLtrWorkbookRowPreview` DTOs and `previewRegisteredLtrWorkbookRow(...)`.
- `LtrWorkbookBasicInformationSyncService.preview(...)` currently calls `_require_basic_information(...)`, which requires latest confirmed Basic Information before preview construction.
- The commit/update path still has explicit preview acknowledgement, operator confirmation, expected version/hash, lifecycle write guard, and workbook write transaction checks.

## 6. Inferred By Planner

- This should be a formal post-acceptance corrective lane rather than a quick fix because it reverses accepted scope, removes API/service/UI artifacts, and changes preview/commit contract wording.
- The safer path is not a raw git revert of commit `66169664` because some wiring or tests may have evolved after acceptance and there are unrelated residuals in the workspace.
- Developer should surgically remove the independent registered-row preview surface while preserving any generally useful registered-LTR prop or helper only if required by the original `LTR update preview` enablement.
- Commit/update should remain stricter than preview. If preview uses fallback/initial data, commit should remain disabled/blocked until confirmed Basic Information exists unless a later Reviewer-approved contract explicitly allows writing fallback values.

## 7. Not Yet Confirmed

- Exact source object for "initial Basic Information": likely project setup payload / Intake setup / TASK_353A fallback read model, but Developer should confirm the smallest existing source instead of creating a new data channel.
- Exact copy: whether the visible label remains `LTR update preview` or is minimally clarified. Safe default: keep `LTR update preview` unless Reviewer requires clearer copy.

These do not block planning because they can be bounded as implementation discovery inside the approved May Touch and validation gates.

## 8. What To Revert Or Remove

- Independent `LTR workbook row preview` button/action.
- Independent registered-row preview panel/card/table.
- `previewRegisteredLtrWorkbookRow(...)` frontend helper and related DTOs if no longer used.
- `GET /api/projects/{project_id}/ltr-workbook/registered-row-preview` route.
- `RegisteredLtrWorkbookRowPreviewService`.
- Registered-row preview focused tests if they only test the removed workflow.
- Workbench/summary-card props that exist only to drive the removed independent action.

## 9. What To Keep

- Existing Basic Information LTR workbook sync/update route family.
- Existing `Confirm update` commit flow and safety checks.
- Exact registered DL row lookup behavior.
- Workbook read-only preview behavior used by the original update preview.
- Existing Basic Information side-card layout, with one LTR update entry.
- TASK_349A Intake specified-LTR preview semantics.
- TASK_353A confirmed identity behavior.

## 10. Preview Versus Commit Contract

Preview can open when:

- Project has a registered DL/LTR.
- Workbook row can be located or returns a readable blocker/not-found state.
- Basic Information may be unconfirmed; preview uses initial Basic Information/project setup fallback in that case.

Commit/update can proceed only when:

- The original commit safety contract is satisfied.
- Operator explicitly confirms.
- Preview is acknowledged.
- Required expected version/hash or equivalent safe source validation exists.
- Lifecycle write guard and workbook transaction checks pass.
- The implementation does not silently write fallback values from unconfirmed Basic Information unless a separate approved contract allows it.

## 11. May Touch

See `tasks/TASK_353C_LTR_UPDATE_PREVIEW_MINIMAL_REGISTERED_LTR_ENABLEMENT.md`.

Key planned scope:

- Remove TASK_353B independent registered-row preview API/service/client/UI/tests.
- Modify existing Basic Information LTR update preview enablement and fallback source.
- Preserve commit/update gate.
- Focused backend/frontend tests.

## 12. Must Not Touch / Locked Paths

See `tasks/TASK_353C_LTR_UPDATE_PREVIEW_MINIMAL_REGISTERED_LTR_ENABLEMENT.md`.

Key locks:

- No LTR workbook authority write-rule changes.
- No schema/migration.
- No Intake specified-LTR/local duplicate changes.
- No Matrix/Fee/Folder Actions/Report/StepInstance/AI/permissions/LAN/server/multi-user.
- No real workbook/folder mutation.
- No unrelated residual cleanup.

## 13. Validation Gate Draft

- Focused backend tests prove preview can be built with registered LTR and fallback initial Basic Information when confirmed Basic Information is absent.
- Backend tests prove no registered LTR blocks preview.
- Backend tests prove commit remains blocked without confirmed/safe source requirements.
- Frontend tests prove only the original LTR update preview action is visible.
- Frontend tests prove the action is enabled with registered LTR despite unconfirmed Basic Information.
- Frontend tests prove independent `LTR workbook row preview` button/card no longer appears.
- Existing Basic Information sync commit regression tests pass.
- TASK_349A specified-LTR authority preview regressions pass if shared code is touched.
- `npm run build`, focused pytest, focused npm tests, `git diff --check`, trailing whitespace scan, forbidden-scope/status scan.

## 14. Planning Risk

- A broad revert could accidentally remove useful later changes or collide with unrelated residuals.
- Enabling preview before Basic Information confirmation can accidentally weaken commit if preview and commit share the same DTO without a clear source-state contract.
- The user explicitly asked to avoid extra UI complexity, so the Reviewer should block any reintroduced second LTR preview entry.

## 15. Questions

None blocking for a planned lane. The user's correction is specific enough to plan a corrective lane. Implementation must keep ambiguous copy/source details within the conservative defaults above.

## 16. Definition Of Ready

Definition of Ready for a planned lane is satisfied:

- User correction is clear.
- Accepted TASK_353B conflict is documented.
- Existing code boundaries and commit impact are known.
- Preview versus commit behavior is separated.
- May Touch / Must Not Touch / Locked Paths are concrete.
- Validation and merge gates are testable.

Reviewer plan gate passed. Developer correction fix pass completed. Reviewer correction re-gate passed. QA correction pass completed.

TASK_353C is complete/accepted after Integrator packaging/readiness with strict hunk/file package isolation.
