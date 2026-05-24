# TASK_219F Runtime Console Responsibility Refinement Plan

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_219F_PROJECT_WORKBENCH_LEGACY_SUPPORT_REMOVAL_AND_RUNTIME_CONSOLE_RESPONSIBILITY_REFINEMENT`

## Why This Task Is Allowed Now

- `TASK_219F` first pass removed the old advanced-support stack.
- User review confirms remaining lower areas still reflect workflow residue rather than runtime-critical console information.
- Task board active task is none, and user explicitly approved continuing with TASK_219F.

## 1) Current Lower UI Responsibility Inventory

Current lower regions in Workbench:

1. `runtime-console-output-secondary`
- Renders `ProjectWorkbenchDocumentStatusPanel` (`Derived outputs`).
- Shows Section 2/Test record/Fee evaluation/Approval package in missing/current/stale style.

2. `runtime-support-shell`
- Shows `Runtime Support / Project setup status` card grid.
- Cards include `Project Folder`, `Approval Package`, `Other Materials`, `Lookup Diagnostics`.

3. `ProjectWorkbenchMaterialDropPanel`
- Shows `Other materials` intake and fallback source-path textarea.
- Shows `Preview placement`/`Confirm placement` actions.
- Shows bottom counters: `Input paths`, `Preview items`, `Placed files`, `Status`.

Assessment:

- These regions are largely setup-process and system-process visibility, not runtime-critical execution visibility.

## 2) Responsibility Classification

### Runtime-critical (keep visible)

- Matrix authority sync status.
- Projection alignment/mismatch.
- Runtime projection map and selected step context.
- Runtime blockers/attention and projection errors.
- Matrix Editor navigation action.

### Contextual only (show when actionable exception)

- Derived output stale/failure/manual-unverified warnings.
- Missing output only at a lifecycle gate where action is required.
- Missing folder only when it blocks an immediate required action.

### Remove from Workbench main body

- Always-visible `Derived outputs` board.
- Always-visible `Runtime Support / Project setup status` card grid.
- Always-visible `Other materials` action panel.
- Material process counters (`Input paths`, `Preview items`, `Placed files`, `Status`).

### Collapse

- None for this task. Collapsing still preserves the old mental model and visual weight.

## 3) Exact JSX/Import/Prop Removal List

### File: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`

Remove imports:

- `ProjectWorkbenchDocumentStatusPanel`
- `ProjectWorkbenchMaterialDropPanel`
- `ProjectWorkbenchSupportModel`

Remove prop and signature members:

- `supportModel: ProjectWorkbenchSupportModel`
- `supportModel` function parameter

Remove support-model destructuring block:

- `approvalResult`
- `evidencePlan`
- `evidenceResult`
- `folderReady`
- `placingEvidence`
- `previewingEvidence`
- `onPlaceEvidence`
- `onPreviewEvidence`

Remove rendered sections:

- `<section className="runtime-console-output-secondary">...</section>`
- `<section className="runtime-support-shell" ...>...</section>`
- `<ProjectWorkbenchMaterialDropPanel ... />`

Remove helper component if unused after section removal:

- `RuntimeSupportCard`

Keep runtime model fields and runtime-console primary sections unchanged.

### File: `frontend/src/pages/ProjectWorkbenchPage.tsx`

Remove import:

- `selectProjectWorkbenchSupportModel`

Remove local variable:

- `const supportModel = selectProjectWorkbenchSupportModel(model);`

Remove layout prop:

- `supportModel={supportModel}`

### File: `frontend/src/features/project-workbench/useProjectWorkbenchSupportModel.ts`

Decision for this task:

- Keep file unchanged unless TypeScript/build fails due to strict unused export policy.
- This task is UI visibility refinement, not support-hook deletion.

## 4) Simplification Strategy

Use the simplest viable Workbench rule:

```text
If it is not needed to decide the next runtime action, do not render it.
```

This task should delete visible lower regions instead of replacing them with a new notification, drawer, collapsed panel, or renamed status board.

Rationale:

- The current runtime attention surface is the right long-term home for execution blockers.
- Adding a new exception notification now would preserve the habit of explaining internal system state.
- Backend output records and support model data can stay available for future audit/log surfaces without being rendered in Workbench.

## 5) Derived Outputs Visibility Decision

- Remove the always-visible `Derived outputs` board from Workbench.
- Do not add a replacement exception banner in this task.
- Continue keeping output status data in the model if it is already used for runtime projection state or stale calculations.
- Future exception rendering should be handled in a dedicated runtime-attention task if a real blocker case is defined.

## 6) Runtime Support Visibility Decision

- Remove always-visible runtime-support status cards.
- Do not replace with another status board.
- Do not keep `Project Folder`, `Approval Package`, `Other Materials`, or `Lookup Diagnostics` as routine cards.
- If future support action is required, it should be contextual to a concrete blocker in a separate task.

## 7) Material Intake/Counters Visibility Decision

- Remove `Other materials` panel from Workbench main body in TASK_219F.
- Remove visible process counters from runtime console.
- Do not add a new modal, drawer, audit page, or hidden debug panel in this task.

## 8) CSS Cleanup List

File: `frontend/src/workbench.css`

Remove styles only if orphaned after JSX removals:

- `.runtime-console-output-secondary`
- `.runtime-support-shell`
- `.runtime-support-heading`
- `.runtime-support-grid`
- `.runtime-support-card*`
- `.material-drop-*`

Keep unrelated runtime-console primary styles.

Keep other component styles unless confirmed truly orphaned and not referenced elsewhere.

## 9) Static Test Assertions

File: `tests/unit/test_frontend_shell_files.py`

Update existing TASK_219 assertions that still expect lower panels.

Add/adjust `TASK_219F` test with negative assertions on `ProjectWorkbenchLayout.tsx`:

Must not contain:

- `Derived outputs`
- `Runtime Support`
- `Project setup status`
- `Other materials`
- `Drop files here (desktop workspace)`
- `Preview placement`
- `Confirm placement`
- `Input paths`
- `Preview items`
- `Placed files`

Must keep runtime console essentials:

- `Project runtime console`
- `Matrix Overview`
- `Runtime execution map`
- `Step Workspace`
- `Edit Matrix Definition`

For `ProjectWorkbenchPage.tsx`, assert removal of support-model wiring:

- no `selectProjectWorkbenchSupportModel`
- no `supportModel=`

## 10) Risk List

1. Existing tests may still assume `Derived outputs` or `Other materials` presence.
- Mitigation: update those tests in same task with new boundary assertions.

2. Removing lower boards removes output freshness visibility from the normal Workbench screen.
- Mitigation: treat this as intended behavior. Output lineage belongs to audit/log or a future exception-specific surface, not a permanent runtime console board.

3. Over-cleaning CSS may impact reusable components.
- Mitigation: only remove clearly orphaned selectors tied to removed JSX.

4. Hook files may retain unused exports.
- Mitigation: leave hook file intact unless build/lint requires cleanup.

## 11) Validation Commands

Required:

```powershell
cd frontend
npm run build
```

Required:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

Recommended after board update:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

## 12) Manual Smoke Path

1. Open a project Workbench.
2. Confirm runtime console main body still renders normally.
3. Confirm Matrix overview and step workspace remain visible.
4. Confirm `Derived outputs` board is absent in normal state.
5. Confirm `Runtime Support / Project setup status` board is absent.
6. Confirm `Other materials` intake panel is absent.
7. Confirm bottom counters are absent.
8. Confirm `Edit Matrix Definition` navigation still works.

## 13) Stop Rule

After this plan document is submitted, stop and wait for explicit user approval before implementation code edits.
