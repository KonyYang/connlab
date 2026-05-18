# TASK_219F_PROJECT_WORKBENCH_LEGACY_SUPPORT_REMOVAL_AND_RUNTIME_CONSOLE_RESPONSIBILITY_REFINEMENT

## Status

Complete. First removal pass and R2 responsibility refinement are implemented.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

None. `TASK_219F` first removal pass and R2 responsibility refinement are complete.

## Why This Task Is Allowed Now

The first pass removed the explicit legacy advanced support block, but the current Workbench still renders lower regions that preserve a setup-workflow mental model:

- `Derived outputs`
- `Runtime Support / Project setup status`
- `Other materials`
- material input/preview/placed/status counters

The confirmed product direction is stricter:

```text
Project Workbench = Project Runtime Console
```

The issue is no longer only visible legacy panels. The remaining lower UI still presents system outputs and internal support process counters as if they were runtime-critical operator information.

This R2 refinement is allowed because it is a bounded frontend IA responsibility correction after `TASK_219A` through `TASK_219F` first pass.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for execution.

Why suitable:

- The task is a bounded frontend responsibility/IA correction.
- The expected implementation is React/CSS/static-test cleanup, not new backend domain design.
- The model can safely remove rendered UI regions, update static guards, and preserve route/API boundaries.
- The task has clear negative assertions: do not show derived-output process boards, setup-status boards, material placement counters, or legacy support actions in the Runtime Console.

Execution caveats:

- Do not implement output generation, Step execution persistence, file upload, image asset management, report binding, permissions, or LAN behavior.
- Treat backend output records as audit/status data, not as always-visible Workbench UI.
- Do not delete backend endpoints or reusable components unless a separate task approves that cleanup.

## Objective

R2 objective: refine Project Workbench by removing lower UI regions that are not runtime-critical.

After this task, the Workbench should show:

- Runtime Console primary surface
- Matrix authority/runtime projection state
- current execution attention and blockers
- selected Matrix/Step runtime context
- only operator actions that are needed now

The Workbench must not show:

- always-visible derived-output board when all items are missing/current without action
- always-visible Runtime Support / Project setup status board
- approval package, folder, lookup, or other-materials status cards as routine console content
- material input path area
- material preview/placed/status counters
- support process metrics that exist mainly to explain internal system behavior

## Runtime Console Responsibility Analysis

### Runtime-critical information

Runtime-critical information is information the engineer needs to decide what to do now during Matrix-driven execution.

Keep visible long-term:

- Matrix authority version and projection alignment.
- Candidate vs authority mismatch.
- Runtime projection loading/error state.
- Execution attention: blockers, stale execution map, missing authority, invalid Matrix, stale projection, selected token no longer valid.
- Matrix overview and selected Step runtime context.
- Current Step status if backed by real runtime data or clearly marked as placeholder before persistence exists.
- Navigation to Matrix Editor when authority definition needs correction.

### Historical workflow residue

These should not be always visible in Runtime Console:

- Section 2 completion.
- Test record.
- Fee evaluation.
- Approval package.
- Project folder setup status.
- Lookup diagnostics.
- Material placement preview counts.
- Input path count, preview item count, placed file count, generic status counters.

Reason: these mostly describe system-produced artifacts or old setup workflow checkpoints. They do not usually drive the engineer's next runtime execution decision.

### Derived outputs decision

Derived outputs should not remain as an always-visible board.

R2 target:

- Hide when outputs are missing because generation has not yet been triggered or is not runtime-critical.
- Do not add a replacement exception banner in this task.
- Keep output records available in model/API for future audit or exception-specific surfaces.
- Future exception rendering should be handled by a dedicated runtime-attention task once concrete blocker cases are defined.
- Route full output lineage to audit/log or a future output history surface, not the primary Workbench runtime body.

### Runtime Support decision

Runtime Support should become lightweight contextual support, not a status board.

R2 target:

- Remove the always-visible `Runtime Support / Project setup status` card grid.
- Do not show `Folder`, `Approval Package`, `Other Materials`, or `Lookup Diagnostics` as routine status cards.
- If a support action is necessary, show it contextually near the blocker it resolves.
- If there is no actionable support need, show nothing.

### Bottom material counters decision

The bottom material counters are system-internal execution indicators:

- `Input paths`
- `Preview items`
- `Placed files`
- `Status`

R2 target:

- Remove from Runtime Console.
- They may belong inside an audit/debug panel or future dedicated material intake flow, not the daily Runtime Console.

### Internal-process exposure problem

Current lower UI still has a product smell:

```text
The page explains how the system works instead of showing what the operator must act on.
```

R2 should remove that smell by making non-critical system processes contextual, exceptional, or auditable.

## Current UI Problem

First-pass UI now communicates this hierarchy:

```text
Derived outputs
Runtime support
Other materials
  Drop files here
  Source paths
  Preview placement / Confirm placement
  Input paths / Preview items / Placed files / Status
```

Target hierarchy:

```text
Runtime Console
  Matrix authority and projection sync
  Runtime execution map
  Selected step runtime context
  Runtime attention / blockers
  Contextual exception notifications only
```

## Existing Code Context

Likely frontend files to inspect and edit:

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchSupportModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchDocumentStatusPanel.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchMaterialDropPanel.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`

Rendered labels to remove or make exception-only in visible Workbench:

- `Derived outputs`
- `Output sync visibility against current Matrix authority`
- `Section 2 completion`
- `Test record`
- `Fee evaluation`
- `Approval package`
- `Runtime Support`
- `Project setup status`
- `Status-first, advanced actions collapsed`
- `Project Folder`
- `Other Materials`
- `Lookup Diagnostics`
- `Other materials`
- `Drop files here (desktop workspace)`
- `Source paths (fallback)`
- `Preview placement`
- `Confirm placement`
- `Input paths`
- `Preview items`
- `Placed files`

## Scope

Allowed:

- frontend-only Runtime Console responsibility refinement
- remove always-visible derived output board
- remove always-visible Runtime Support / Project setup status card grid
- remove visible material intake/action panel and internal counters
- remove derived output visibility from the normal Workbench body without adding a replacement panel
- keep output/audit data in client/model if still needed by selectors or future surfaces
- remove imports, props, and CSS that only serve removed visible sections
- keep Matrix Editor navigation
- keep runtime projection loading and token selection behavior
- add static tests that fail if removed process-board labels return to Workbench layout
- update `docs/task_board.md` after implementation completion
- create a concrete implementation plan before coding

Forbidden:

- backend/API/DB changes
- deleting backend folder/evidence/approval/lookup endpoints
- deleting reusable components if other routes or future tasks may still need them
- changing Matrix draft update/validate/confirm behavior
- implementing automatic output generation
- implementing StepInstance, execution persistence, image asset management, report generation, AI review, permissions, or LAN deployment
- adding new dependencies
- moving complex data entry into Workbench under a different name
- adding an output history/audit page in this task
- adding a new support drawer, modal, or hidden debug panel unless explicitly approved

## Required First Deliverable

Before writing implementation code, create:

```text
docs/task_219f_runtime_console_responsibility_refinement_plan.md
```

The plan must include:

- current lower UI responsibility inventory
- classification of each region as runtime-critical, contextual, collapsed, removed, or exception-only
- exact JSX/import/prop removal list
- decision on derived outputs visibility
- decision on runtime support visibility
- decision on material intake/counters visibility
- CSS cleanup list
- static test assertions
- risk list
- validation commands
- manual smoke path

Stop after writing the plan and wait for explicit user approval.

## First Pass Execution Result

The first pass removed visible legacy support surfaces from Project Workbench runtime console:

- Removed advanced support container and nested legacy sections from `ProjectWorkbenchLayout`.
- Removed rendering/import references for:
  - `ProjectFolderCreationPanel`
  - `ApprovalPackagePanel`
  - `ProjectWorkbenchEvidencePanel`
  - `ProjectLookupPanel`
- Kept `ProjectWorkbenchMaterialDropPanel` as lightweight runtime support surface.
- Kept runtime console primary areas, derived output status section, and runtime support status cards.
- Added/updated static frontend guards to ensure removed legacy labels/surfaces do not regress.

R2 follow-up required by user review:

- Remove or contextualize `Derived outputs`.
- Remove always-visible `Runtime Support / Project setup status`.
- Remove visible `Other materials` intake panel.
- Remove bottom material process counters.
- Keep only runtime-critical information and exception-driven notifications in the console.

## R2 Execution Result

Implemented the stricter Workbench Runtime Console simplification:

- Removed always-visible `Derived outputs` rendering from `ProjectWorkbenchLayout`.
- Removed always-visible `Runtime Support / Project setup status` rendering from `ProjectWorkbenchLayout`.
- Removed visible `Other materials` intake/action panel from Workbench.
- Removed support-model prop wiring from `ProjectWorkbenchPage` to `ProjectWorkbenchLayout`.
- Removed readiness entries for routine `Approval Package`, `Fee Evaluation`, and `Open Setup Manager`.
- Removed orphaned runtime-support/supporting CSS selectors from `frontend/src/workbench.css`.
- Updated frontend static guards so removed process-board labels and components cannot return to visible Workbench layout.

## Implementation Guidance After Approval

Expected R2 implementation direction:

1. Remove always-visible `runtime-console-output-secondary` if it renders the `Derived outputs` board.
2. Do not add a replacement derived-output notification, banner, drawer, or collapsed section in this task.
3. Remove always-visible `runtime-support-shell`.
4. Remove visible `ProjectWorkbenchMaterialDropPanel` from Workbench.
5. Remove support/action props from `ProjectWorkbenchLayout` if no longer used.
6. Keep backend-facing support hooks only if still used elsewhere; defer deeper hook cleanup to a separate task.
7. Remove CSS rules only when clearly orphaned by this visibility change.
8. Update static tests so removed process-board labels cannot reappear.

## Acceptance Criteria

- Workbench UI no longer displays an always-visible `Derived outputs` board.
- Workbench UI no longer displays an always-visible `Runtime Support / Project setup status` board.
- Workbench UI no longer displays `Other materials` intake/action panel.
- Workbench UI no longer displays material process counters: `Input paths`, `Preview items`, `Placed files`, `Status`.
- No normal `all missing` generated-output board is shown just to explain internal system state.
- No replacement exception UI is added in this task.
- Matrix Editor navigation remains available.
- Runtime Console primary surface remains visible.
- No backend/API behavior is changed.
- `npm run build` passes.
- Static tests guard against lower process-board labels returning to `ProjectWorkbenchLayout`.

## Visibility Policy

### Permanently keep

- Matrix authority and projection sync.
- Runtime execution map.
- Runtime attention/blocker surface.
- Selected step runtime context.
- Matrix Editor navigation.

### Contextualize In Future Tasks

- Derived output issues.
- Output freshness or generation failure.
- Support actions that directly resolve a current blocker.

### Collapse

- None by default in R2. Collapsing is not enough when the information is system-internal or old workflow residue.

### Remove from Workbench

- Derived outputs board as routine content.
- Runtime Support / Project setup status board.
- Other materials intake panel.
- Material placement counters.
- Lookup diagnostics card.

### Show Only On Exception In Future Tasks

- Stale derived output after Matrix authority changes.
- Failed output generation/placement.
- Manual output that cannot be verified.
- Missing output only when a lifecycle gate requires it.
- Missing project folder only when it blocks a current required action.

## Validation

Required:

```powershell
cd frontend
npm run build
```

Result: passed.

Required:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

Result: `64 passed`, `4 failed`. The remaining failures are historical Intake/Precheck static assertion drift outside TASK_219F scope:

- `test_task087_intake_information_density_cleanup`
- `test_task082_precheck_sample_rows_are_editable_with_icon_actions`
- `test_task091_intake_precheck_typography_uses_shared_ui_vocabulary`
- `test_task096_creation_draft_lifecycle_frontend_actions`

TASK_219F targeted Workbench static checks passed:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task219 or task188 or task190 or task187 or project_lookup or task100 or task150"
```

Result: `9 passed`, `59 deselected`.

Recommended board/governance check if task board is updated:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

## Manual Smoke Path

1. Open a project Workbench.
2. Confirm Runtime Console primary surface remains visible.
3. Confirm Matrix authority/projection sync remains visible.
4. Confirm runtime execution map remains visible.
5. Confirm selected Step runtime context remains visible.
6. Confirm `Derived outputs` board is absent during normal missing/current states.
7. Confirm `Runtime Support / Project setup status` board is absent.
8. Confirm `Other materials` intake panel is absent.
9. Confirm material counters are absent.
10. Click Matrix Editor navigation and confirm routing still works.
