# TASK_353C LTR Update Preview Minimal Registered LTR Enablement - Planner Evidence

Task ID: `TASK_353C_LTR_UPDATE_PREVIEW_MINIMAL_REGISTERED_LTR_ENABLEMENT`
Lane: `ltr-update-preview-minimal-registered-ltr-enablement`
Role: Planner
Date: 2026-07-07
Status: planned - ready for Reviewer plan gate

## Current Phase / Active Task / Why Allowed

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current board state: `TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW` is complete/accepted in local commit `66169664`.
- Current role: Planner.
- Why allowed: user/orchestrator explicitly corrected the accepted TASK_353B product direction and requested a Planner Discovery Gate / corrective lane creation only. This pass does not implement product code or route Developer.

## User Correction

The user rejected the over-expanded TASK_353B result. The desired product behavior is:

- keep the original `LTR update preview` entry;
- allow it for projects that already have registered LTR/DL;
- do not require confirmed Basic Information just to open preview;
- use/import initial Basic Information/project setup values in the preview;
- keep the rest of the original flow;
- remove the separately added button/card/API/service workflow.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `$impeccable` product context
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `tasks/TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW.md`
- `docs/task_353b_registered_ltr_workbook_row_preview_plan.md`
- TASK_353B planner/developer/reviewer/QA evidence
- commit `66169664` file list
- current Basic Information side-card, API client, Workbench wiring, and LTR Basic Information sync service code

## Confirmed By User

- TASK_353B over-modified the product.
- The independent `LTR workbook row preview` button/card/workflow is not wanted.
- The existing `LTR update preview` entry should be the entry point.
- Registered LTR is the enablement condition for opening preview.
- Basic Information confirmation should not be required just to preview.
- Initial Basic Information/project setup should be usable in preview.
- Existing update/commit semantics should otherwise stay.

## Confirmed By Repository Evidence

- Board and commit history show TASK_353B accepted in commit `66169664`.
- That commit added independent registered-row preview backend route/service, frontend DTO/helper, Basic Information summary-card second action/panel, Workbench prop wiring, and focused tests.
- Current `ProjectBasicInformationSummaryCard` renders both `LTR workbook row preview` and `Update LTR from Basic Information`.
- Current `LtrWorkbookBasicInformationSyncService.preview(...)` requires confirmed Basic Information, while commit still guards write/commit through preview acknowledgement, operator confirmation, expected version/hash, lifecycle write guard, and write transaction.

## Inferred By Planner

- This is a formal post-acceptance corrective lane, not a continuation of TASK_353B acceptance.
- Reviewer plan gate is appropriate before Developer because scope reverses accepted UI/API behavior and must protect commit safety.
- Developer should not use a raw revert blindly because current workspace has unrelated residuals and subsequent accepted state may include board/evidence changes.

## Not Yet Confirmed

- Exact internal source for initial Basic Information fallback. Safe implementation default: reuse existing project setup / project identity / Basic Information fallback read model without creating new schema or authority paths.
- Exact label. Safe default: keep `LTR update preview`.

These are not blockers because the lane locks broad changes and requires validation around fallback source and copy.

## Planned Files

- `tasks/TASK_353C_LTR_UPDATE_PREVIEW_MINIMAL_REGISTERED_LTR_ENABLEMENT.md`
- `docs/task_353c_ltr_update_preview_minimal_registered_ltr_enablement_plan.md`
- `docs/lane_evidence/TASK_353C_ltr-update-preview-minimal-registered-ltr-enablement_planner.md`
- `docs/task_board.md`

## Decision

Create a planned corrective lane and stop at Reviewer plan gate. Do not route Developer implementation from this Planner pass.

## Validation

Completed validation:

- `git diff --check -- docs/task_board.md tasks/TASK_353C_LTR_UPDATE_PREVIEW_MINIMAL_REGISTERED_LTR_ENABLEMENT.md docs/task_353c_ltr_update_preview_minimal_registered_ltr_enablement_plan.md docs/lane_evidence/TASK_353C_ltr-update-preview-minimal-registered-ltr-enablement_planner.md` passed with only the existing `docs/task_board.md` LF/CRLF warning.
- trailing whitespace scan on the touched TASK_353C docs/board/evidence returned no matches.
- targeted status shows this Planner pass created/updated only TASK_353C source-of-truth docs/evidence plus `docs/task_board.md`.
- Current workspace also contains product-code residuals, including TASK_353B-related registered-row preview removals/modifications and unrelated release/settings/Fee/PDF residuals. They were not edited by this Planner pass and must not be packaged or reviewed as Planner output.

## Next Role

Reviewer plan gate.
