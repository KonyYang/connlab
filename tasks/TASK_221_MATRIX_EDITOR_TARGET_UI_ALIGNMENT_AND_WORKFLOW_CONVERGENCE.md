# TASK_221_MATRIX_EDITOR_TARGET_UI_ALIGNMENT_AND_WORKFLOW_CONVERGENCE

## Status

Complete. Implemented and validated on 2026-05-17.

This is a UI alignment / workflow convergence task, not a UI redesign task.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

None. `TASK_220` Project Workbench target UI alignment is complete and the task board is waiting for user approval for the next controlled task.

## Why This Task Is Allowed Now

The current Matrix Editor page exists as a placeholder Definition Studio, but it no longer matches the approved target reference `Matrix Edit Page.png`.

The current implementation has started to drift toward a dashboard-like page:

- too many status/runtime cards
- Matrix Grid visual priority is reduced
- right-side support/status information competes with editing workflow
- target page workflow order is not preserved
- supporting libraries and templates are missing or underrepresented

This task is allowed because it is a bounded frontend alignment task:

- no backend changes
- no API contract changes
- no domain model changes
- no persistence changes
- no new complex interaction behavior
- no redesign beyond matching the supplied target image

## Model Fit Assessment

`GPT-5.3-codex` is suitable for execution.

Reason:

- The task is a scoped React/TypeScript/CSS alignment pass.
- The target is explicit: converge current Matrix Editor to `Matrix Edit Page.png`.
- Existing placeholder data can be reused or expanded statically without backend changes.
- The main risk is over-building. The task explicitly forbids new complex interactions, backend workflow, and dashboard expansion.

## Objective

Align the current Matrix Editor page to the target reference image `Matrix Edit Page.png`.

The target image is the visual and workflow contract. The result should read as:

```text
Matrix Editor = Definition Studio
```

It must not read as:

```text
Matrix Editor = Runtime Dashboard
```

## Target Page Principles

The implementation must preserve these target characteristics:

- Matrix Grid is the main core.
- Left Test Library is an auxiliary input surface.
- Right Group / Step Workspace is contextual.
- Bottom Templates and Reference Library are supporting references.
- Top action bar expresses authoring workflow.
- Header shows project identity and matrix editing metrics.
- Runtime projection appears only as supporting context, not the main page structure.

## Non-Goals

Do not:

- redesign the page
- invent a new layout
- add complex interactions
- implement real inline editing
- implement drag/drop composition
- implement backend persistence
- change Matrix authority semantics
- change API contracts
- change domain models
- add new dependencies
- turn Matrix Editor into a runtime/status dashboard
- move Matrix definition editing back into Project Workbench

## Current vs Target Delta

### Header Information Structure

Current:

- Header shows `Matrix Editor` and placeholder mode.
- Project identity is weak.
- Metrics are summary cards below the title.
- Actions are generic and disconnected from target workflow density.

Target:

- Left back navigation to Workbench.
- Strong page title: `Matrix Editor`.
- Project identity line: product name, LTR, BU, requester, LTR status.
- Header metrics: groups, steps, items.
- Right actions: save, publish/approval, more.

Required:

- Align header hierarchy and density to target.
- Keep English labels.
- Use existing model data where available.
- Use static placeholder values where backend data is not available.

### Top Operation Bar

Current:

- Actions are limited to `Workbench`, `Import Template`, `Save Draft`, `Validate`, `Confirm Authority`.
- Action grouping does not match target workflow.

Target:

- Dense authoring toolbar below header.
- Actions include add test item, add group, add step, duplicate row, import from template/spec, rule completion, follow-up matching, export Matrix.
- Right side includes display options, filter, and search.

Required:

- Render target-equivalent toolbar actions as disabled or placeholder buttons unless existing behavior supports them.
- Do not implement new business operations.
- Keep action density and grouping close to target.

### Left Test Library

Current:

- No left Test Library panel.

Target:

- Left supporting library with search.
- Common templates.
- Recently used items.
- Favorites.
- All test items grouped by category.
- Quick actions.

Required:

- Add left Test Library surface with static placeholder content.
- Keep it auxiliary; it must not dominate the Matrix Grid.
- Do not add backend calls or persistence.

### Matrix Grid

Current:

- Matrix table exists but is small and framed like a simple placeholder.
- Grid loses dominance because right-side cards consume visual attention.
- Row count and column density do not match target.

Target:

- Matrix Grid is the dominant central surface.
- Dense table with definition columns and group/step cells.
- Group/step cells use compact status tokens.
- Main table has horizontal density and scroll behavior.

Required:

- Expand placeholder rows to target-like density.
- Keep Matrix Grid as the largest visual area.
- Align column order and headers:
  - `#`
  - Test Item
  - Section
  - Test Method / Standard
  - Condition
  - Requirement
  - Steps / Groups columns
- Keep all behavior placeholder-safe.

### Right Group / Step Workspace

Current:

- Right panel contains runtime/status cards:
  - Authority Status
  - Step Identity Preview
  - Authority Sync
  - Selected Definition
  - Runtime Mapping Notes

Target:

- Right contextual workspace.
- Shows selected group and step preview.
- Tabs: step order, group info, fee/time plan, history.
- Step list table.
- Suggestion/validation notice.
- Basic sample count, expected completion, estimated fee.
- Note field and apply action.

Required:

- Replace status-card stack with target-like contextual workspace.
- Keep runtime projection notes out of primary visual hierarchy.
- Do not implement real editing or save behavior.

### Runtime Projection Area

Current:

- Runtime and authority sync information occupies too much space.

Target:

- Runtime/projection context is secondary and should not compete with authoring workflow.

Required:

- Keep projection reference only as small metadata or contextual note if needed.
- Do not create runtime support panels in Matrix Editor.
- Do not expose Workbench runtime-console concerns here.

### Bottom Template Area

Current:

- No bottom template card area matching target.

Target:

- Bottom left Templates area.
- Cards for reusable matrix templates.
- Search and preview/use actions.

Required:

- Add static template area.
- Keep as supporting reference.
- Do not implement template import behavior beyond existing route-safe placeholder buttons.

### Bottom Reference Library

Current:

- No bottom Reference Library panel matching target.

Target:

- Bottom right Reference Library.
- Tabs for method standards, conditions, requirements, spec clauses.
- Dense reference table with view/use actions.

Required:

- Add static Reference Library panel.
- Keep it supporting, not primary.
- Do not add backend/reference data model.

## Scope

Allowed:

- frontend-only React/TypeScript updates
- CSS layout and density adjustments in existing stylesheet
- static placeholder data inside Matrix Editor page or local constants
- static frontend tests for TASK_221 structure
- task board update after completion
- implementation plan document before coding

Forbidden:

- backend changes
- API client contract changes
- database changes
- domain model changes
- new routes
- new dependencies
- real Matrix editing implementation
- inline cell editing behavior
- drag/drop test item insertion
- template import execution
- authority confirmation behavior changes
- runtime dashboard/status expansion

## Required First Deliverable

Before implementation, create:

```text
docs/task_221_matrix_editor_target_ui_alignment_plan.md
```

The plan must include:

- target UI interpretation
- current vs target delta table
- exact file-level changes
- component reuse strategy
- static placeholder data strategy
- CSS alignment strategy
- tests to add/update
- validation commands
- manual smoke checklist

Stop after writing the plan and wait for explicit user approval.

## Expected File Touches

Likely files:

- `frontend/src/pages/ProjectMatrixEditorPage.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- `docs/task_board.md`
- `tasks/TASK_221_MATRIX_EDITOR_TARGET_UI_ALIGNMENT_AND_WORKFLOW_CONVERGENCE.md`

Avoid touching unless explicitly justified:

- `backend/**`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- Matrix authority service/backend files
- database or migration files

## Acceptance Criteria

- Matrix Editor visually follows `Matrix Edit Page.png`.
- Page reads as Definition Studio, not Runtime Dashboard.
- Matrix Grid is the dominant central workspace.
- Left Test Library is present and auxiliary.
- Right Group / Step Workspace is present and contextual.
- Bottom Templates area is present.
- Bottom Reference Library is present.
- Top operation bar follows target workflow order and density.
- Header follows target information structure.
- Runtime/projection information is contextual and secondary.
- English UI copy is used.
- No backend/API/domain changes are made.
- No new complex interaction behavior is introduced.
- `npm run build` passes.
- TASK_221 static frontend assertions pass.

## Explicit Non-Acceptance

The task is not acceptable if:

- The result is a newly invented Matrix Editor layout.
- Matrix Grid remains visually secondary.
- Runtime/status cards remain the dominant right-side content.
- Test Library, Templates, or Reference Library are omitted.
- New backend behavior is required to render the page.
- Workbench runtime-console concepts are mixed into Matrix Editor primary workflow.

## Validation

Required:

```powershell
cd frontend
npm run build
```

Required targeted tests:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task221 or task220 or task219"
```

Recommended governance tests after task board update:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

## Manual Smoke Path

1. Open a Project Workbench route.
2. Navigate to Matrix Editor.
3. Compare the page against `Matrix Edit Page.png`.
4. Confirm header identity and metrics match target hierarchy.
5. Confirm top operation toolbar matches target order and density.
6. Confirm left Test Library appears and remains auxiliary.
7. Confirm Matrix Grid is the dominant central area.
8. Confirm right Group / Step Workspace replaces dashboard-like runtime cards.
9. Confirm bottom Templates and Reference Library appear.
10. Confirm Workbench navigation still works.
11. Confirm no backend-dependent editing behavior is implied as implemented.
