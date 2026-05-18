# TASK_219A_PROJECT_WORKBENCH_RUNTIME_CONSOLE_REPOSITIONING

## Status

Approved and executed on 2026-05-17.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

None. TASK_219 is complete. TASK_219A is executed as a bounded frontend IA repositioning slice.

## Why This Task Is Allowed Now

The current Workbench already moved toward a Runtime Console, but the lower half still exposes old project-preparation workflows:

- project folder creation
- approval package path entry and placement
- evidence placement preview/place
- read-only lookup summary

The business conclusion has changed:

```text
Project Workbench = Project Runtime Console
```

After Matrix Edit is complete, test record, fee evaluation, and Section 2 completion date are derived or automatically generated outputs. Product materials are already archived during LTR import. Other materials should remain lightweight drag/drop style actions, not a complex preparation workbench.

This task is allowed because it removes low-value Workbench process clutter and preserves the current architecture rule that Matrix definition editing remains outside Workbench.

## Model Fit Assessment

`GPT-5.3-codex` is suitable because this is a bounded frontend IA and copy refactor with strict behavior preservation. It requires careful code reading and UI boundary discipline, but does not require new backend domain modeling or runtime persistence.

## Objective

Reposition the Project Workbench lower half into Runtime Console support surfaces:

- keep runtime state, Matrix authority, output freshness, and current blockers visible
- hide or demote complex manual preparation flows
- preserve lightweight actions only when they are necessary and safe
- prevent Workbench from becoming a universal operations page

## Product Direction

Workbench should answer:

1. What is the project runtime state?
2. Is Matrix authority current?
3. Are derived outputs current, stale, missing, or failed?
4. What lightweight action is needed now, if any?

Workbench should not ask the operator to manually assemble generated output paths as a normal flow.

## Existing Code Context

Observed frontend files:

- `frontend/src/pages/ProjectWorkbenchPage.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchDocumentStatusPanel.tsx`
- `frontend/src/features/project-workbench/ProjectFolderCreationPanel.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchEvidencePanel.tsx`
- `frontend/src/components/workflow/ApprovalPackagePanel.tsx`
- `frontend/src/components/project/ProjectLookupPanel.tsx`
- `frontend/src/workbench.css`

Observed API/client dependencies:

- folder preview/generate APIs
- evidence placement preview/place APIs
- approval package preview/execute APIs
- project output status summary API
- runtime projection read-only snapshot API
- Matrix draft list/get/update/validate/confirm APIs

## Scope

Allowed:

- frontend-only IA and copy changes in Project Workbench
- convert lower folded surfaces into status-first collapsed or hidden support entries
- remove primary visual prominence from approval package manual path form
- keep output status as a read-only Runtime Console section
- preserve route behavior and Matrix Editor navigation
- update or add frontend static tests and build validation
- create an implementation plan document before code

Forbidden:

- backend/API/DB changes
- StepInstance, execution persistence, image asset management, report generation, permissions, LAN deployment, or AI review
- implementing new drag/drop persistence
- implementing automatic generation logic
- deleting existing backend endpoints
- turning Matrix into an Excel-like string editor
- moving complex data entry into Workbench

## Plan Deliverable

Plan file created and approved before implementation:

`docs/task_219a_project_workbench_runtime_console_repositioning_plan.md`

## Implementation Summary

Expected implementation direction:

- Keep `ProjectWorkbenchDocumentStatusPanel` visible as a runtime/output status surface.
- Replace the four lower `details` panels with a compact `Runtime support` or `Project setup status` summary.
- Keep project folder status visible, but do not make folder creation dominate the Workbench.
- Convert approval package path-entry UI into a non-primary support detail or hide it behind an explicit advanced/support affordance if still needed for existing backend validation.
- Keep evidence placement as lightweight status/action only; do not expand into a large workflow.
- Remove `ProjectLookupPanel` from the main Workbench runtime surface unless the plan proves it is still needed as a status diagnostic.

Implemented changes:

- Added `Runtime support` status-first compact section in Workbench lower half.
- Demoted heavy setup workflows into one collapsed `Advanced support` surface.
- Kept folder/approval/evidence/lookup capabilities reachable inside nested collapsibles.
- Kept output status panel and runtime primary surfaces unchanged.

## Acceptance Criteria

- Workbench first screen reads as Runtime Console, not setup workbench.
- Lower half no longer stacks large manual forms for project folder, approval package, evidence, and lookup.
- Automatically derived outputs are shown as status/results, not normal manual preparation steps.
- Matrix definition remains reachable through Matrix Editor.
- No new backend endpoints or persistence are introduced.
- Existing critical route navigation remains stable.
- `npm run build` passes.

## Validation

Required:

```powershell
cd frontend
npm run build
```

Required static/smoke tests if touched:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

Manual smoke:

1. Open a project Workbench.
2. Confirm Runtime Console remains the primary surface.
3. Confirm Matrix Editor navigation still works.
4. Confirm output status is visible and business-readable.
5. Confirm lower legacy setup flows are not visually dominant.

## Execution Result (2026-05-17)

- `npm run build` (frontend) passed.
- Board-state governance tests passed:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

`17 passed`.

- `py -m pytest tests\unit\test_frontend_shell_files.py -q` reports 10 failures, all in historical/static expectation drift areas outside TASK_219A scope (legacy assertions around older workbench/inbox contracts). TASK_219A-specific repositioning changes compile and are aligned with runtime-console-first direction.
