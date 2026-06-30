# TASK_346D Workbench Folder Actions Functional Wiring - Scope Reconciliation Evidence

Status: scope_reconciled_b1
Date: 2026-06-30
Role: Planner
Task: `TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING`
Lane: `workbench-folder-actions-functional-wiring`

## 1. Purpose

Perform one Planner scope/source-of-truth reconciliation action after Reviewer implementation gate blocked TASK_346D with B1/B2/B3.

This pass does not modify product code and does not route Developer directly.

## 2. Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING.md`
- `docs/task_346d_workbench_folder_actions_functional_wiring_plan.md`
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_planner.md`
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_developer.md`
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_reconciliation_planner.md`
- TASK_346A/B/F/C accepted context from task, plan, board, and evidence references
- Current `git status --short`
- Current diff/status for the three proposed bridge files

## 3. Reviewer / Developer Blocking Context

Reviewer implementation gate blocked with:

- B1: `useProjectRuntimeConsoleModel.ts`, `ProjectWorkbenchActiveMatrixWorkspace.tsx`, and `ProjectWorkbenchLifecycleSections.tsx` were changed outside the approved TASK_346D Developer May Touch.
- B2: unrelated LTR workbook local settings helpers appeared in `frontend/src/api/client.ts`.
- B3: public-folder workflow DTO operation id fields were typed as `number` while the accepted TASK_346C backend DTO uses `str`.

Developer fix pass stopped before product edits and recorded that B1 is a real May Touch mismatch. Removing the bridge changes would keep the old May Touch boundary but would leave Sync/Submit/Pull/Auto sync wiring functionally incomplete.

## 4. Planner Decision

Planner accepts B1 as a scope reconciliation issue and adds the three bridge files to TASK_346D Developer May Touch:

- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`

This stays inside TASK_346D because the lane objective is frontend API-client / Workbench functional wiring from the accepted TASK_346C backend workflow to the accepted TASK_346F Folder Actions surface.

## 5. Rationale

- `useProjectRuntimeConsoleModel.ts` is the existing bridge that selects which `useProjectWorkbenchModel` fields and handlers reach the Workbench runtime console/layout.
- `ProjectWorkbenchActiveMatrixWorkspace.tsx` hosts the active Matrix right-rail Folder Actions surface.
- `ProjectWorkbenchLifecycleSections.tsx` hosts lifecycle/no-Matrix Folder Actions surfaces.
- Current diff shows these files only bridge public-folder workflow state/handlers into existing Folder Actions surfaces.
- Without these touches, public-folder workflow context, Auto sync state, Sync/Submit/Pull preview/execute handlers, and confirmation handlers can be created in the model but will not reach the visible Folder Actions UI.
- Splitting this bridge into a separate lane would create an artificial boundary and leave TASK_346D incomplete, while still requiring the same three frontend Workbench bridge files later.

## 6. Scope Locks Preserved

This reconciliation does not authorize:

- backend/API/schema/file-operation changes
- Projects list or Projects registry changes
- Matrix Editor business logic
- real `D:\Test Project/**`
- real `D:\PublicProject/**`
- real public-drive folder mutation
- real LTR workbook files
- public-drive LTR workbook authority writes
- `.agents/**`
- `docs/project_management/**`
- release-engineering residuals
- unrelated LTR workbook local settings helpers
- StepInstance, Report, AI, permissions, LAN/server, or multi-user scope

## 7. B2 / B3 Status

B2 and B3 remain unresolved and must return to Developer fix pass:

- B2: remove unrelated LTR workbook local settings helper diff from `frontend/src/api/client.ts`.
- B3: align public-folder workflow DTO operation id field types with backend `str`.

Developer fix pass should not treat this Planner reconciliation as resolving B2/B3.

## 8. Files Updated By This Planner Pass

- `docs/task_board.md`
- `tasks/TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING.md`
- `docs/task_346d_workbench_folder_actions_functional_wiring_plan.md`
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_scope_reconciliation_planner.md`

No product code was modified by this Planner pass.

## 9. Validation

Completed after source-of-truth updates:

- `git diff --check -- docs/task_board.md tasks/TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING.md docs/task_346d_workbench_folder_actions_functional_wiring_plan.md docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_scope_reconciliation_planner.md` passed with only the existing `docs/task_board.md` LF/CRLF warning.
- Trailing whitespace scan on touched reconciliation docs returned no matches.
- Targeted status showed current product-code dirty files from the existing Developer implementation and unrelated release/settings residuals; this Planner pass changed only source-of-truth docs/evidence listed in section 8.
- Source scan confirmed the three bridge files and B2/B3 unresolved status are recorded in `docs/task_board.md`, the TASK_346D task file, the TASK_346D plan, and this evidence.

## 10. Stop Point

Planner scope reconciliation gate: ready.

Recommended next role: Developer fix pass for unresolved Reviewer B2/B3, using the updated TASK_346D May Touch list.
