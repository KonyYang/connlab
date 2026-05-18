# TASK_220_PROJECT_WORKBENCH_TARGET_UI_ALIGNMENT

## Status

Complete. Implemented and validated on 2026-05-17.

This task is a UI alignment task, not a redesign task.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

None. `TASK_219F` Workbench runtime console responsibility refinement is complete and the task board is waiting for user approval for the next controlled task.

## Why This Task Is Allowed Now

The Workbench has been simplified into a Runtime Console, but the current screen still does not visually align with the approved target reference image `Project workbench UI.png`.

This task is allowed because it is a bounded frontend UI alignment task:

- no backend changes
- no API contract changes
- no domain model changes
- no new runtime behavior
- no redesign beyond matching the provided target image

## Model Fit Assessment

`GPT-5.3-codex` is suitable for execution.

Reason:

- The task is a scoped React/CSS UI alignment task.
- The implementation can reuse the current Workbench components and static placeholder/runtime projection data.
- The acceptance criteria are visual and structural, not algorithmic or backend-heavy.
- The main risk is over-designing; the task explicitly forbids redesign and new feature expansion.

## Objective

Align the current Project Workbench page to the target reference image `Project workbench UI.png`.

The target image is the only visual reference. The current page must converge to that target first, before any later product optimization or deeper interaction work.

The implementation should match:

- page structure
- section hierarchy
- density
- card organization
- header information structure
- project readiness strip
- filter toolbar
- Matrix Overview structure
- Step Workspace layout
- Runtime Attention area
- Recent Activity area
- Fee Estimate area

All visible UI copy must be English.

## Target Image Lock

The executor must treat `Project workbench UI.png` as the visual contract.

Required behavior:

- Compare the current Workbench screen against the target screen before editing.
- Preserve the target screen information hierarchy.
- Preserve the target screen section order.
- Preserve the target screen runtime-console positioning.
- Translate target labels into concise English instead of keeping Chinese labels.
- Use existing Workbench runtime data, static placeholders, or existing UI affordances where backend data is not available.

Forbidden behavior:

- Do not reinterpret the target into a new layout.
- Do not introduce a new visual language.
- Do not add new product concepts.
- Do not make the page more complex than the target.
- Do not restore the removed lower legacy workflow boards from TASK_219F.
- Do not create backend work just to make a visual field dynamic.

## Non-Goal

This is not a redesign task.

Do not:

- invent a different layout
- optimize beyond the target image
- add new workflows
- introduce a new design system
- rework business structure
- implement Step persistence
- implement output generation
- implement file upload or material placement
- change backend logic
- change domain models
- change API contracts

## Current vs Target Delta

### Header

Current:

- Topbar is too compressed and visually uneven.
- Product name is not prominent enough compared with target.
- Current topbar action buttons are cramped.
- Progress, metrics, last update, and refresh are present but not structured like target.
- The right side can wrap or crowd controls in a way that breaks the target header rhythm.

Target:

- Left menu and `Project Workbench` title.
- Clear product identity block with LTR badge.
- Metadata row: LTR, BU, Requester.
- Project progress block.
- Status metrics in one horizontal band.
- Last updated timestamp with refresh icon/control.

Required:

- Align header arrangement to match target proportions and hierarchy.
- Keep existing data sources and fallback values.
- English labels only.

### Project Readiness Strip

Current:

- Runtime readiness cards are sparse and not aligned to target.
- Recent TASK_219F removed routine lower support boards, but the target still has a compact top readiness strip.

Target:

- Compact horizontal readiness strip below header.
- Title: `Project readiness`.
- Items: Project Created, LTR Registered, Folder Created, Source Materials, Matrix Authority, Approval Package, Fee Evaluation.
- `Open Setup Manager` button on the right.

Required:

- Add compact readiness strip as shown in target.
- Treat this as top-level readiness context, not as a lower workflow board.
- Do not reintroduce approval/folder/evidence forms.
- The right-side `Open Setup Manager` affordance is allowed only as a lightweight navigation/action placeholder if already compatible with existing frontend boundaries.

### Filter Toolbar

Current:

- Filter bar exists but spacing and hierarchy do not match target.

Target:

- One compact toolbar row.
- Category select on the left.
- Checkbox group after it.
- Status radio group to the right.
- Small navigation controls on far right if practical.

Required:

- Match target density and ordering.
- Keep existing filter behavior placeholder/static if no behavior exists.
- Avoid inventing new filtering semantics.

### Matrix Overview

Current:

- Matrix area is close but still visually different from target.
- Header copy and table framing differ.
- Table density and right-side scrolling differ.

Target:

- Large left matrix panel.
- Title block: `Matrix Overview`.
- Bilingual-style target labels should be rendered in English only.
- Column grouping and matrix table should keep dense operational layout.
- Matrix table should occupy most of the left workspace.

Required:

- Align table panel header, borders, density, scroll behavior, and column widths to target.
- Do not change Matrix data semantics or API projection shape.
- Keep the Matrix as a read-only runtime execution map in Workbench.

### Step Workspace

Current:

- Right panel exists but layout is not aligned with target.
- Tools and tabs are too cramped and inconsistent.
- Data cards need target-style density.

Target:

- Right-side fixed-width Step Workspace.
- Breadcrumb-like group/step line.
- Header title `Step 2 - LLCR`.
- Three compact action buttons: Matrix, Image, Record.
- Status row.
- Tabs row.
- Fact grid.
- Test data summary.
- Step lifecycle flow.
- Action buttons.
- Notes and Save.

Required:

- Match target structure and order.
- English labels only.
- Do not make buttons functional unless existing behavior already supports it.
- Keep Step Workspace as the focused runtime context panel, not a full data-entry replacement.

### Runtime Attention

Current:

- Runtime attention is present but too low-emphasis and does not match target card group.

Target:

- Bottom left wide attention section.
- Title: `Project issues / reminders`.
- Four compact issue cards: Failed items, Missing evidence, Unsynced report, In progress.
- Cards include small status count and `View details` affordance.

Required:

- Align bottom left attention area to target.
- Use existing projection counts or mock/static values as current implementation already does.
- Do not add new backend data.
- This area should show operator-facing issues/reminders, not internal execution counters.

### Recent Activity

Current:

- Recent activity exists but should visually align to target.

Target:

- Middle bottom panel.
- Title: `Recent activity`.
- Compact list with timestamps.
- `View all activity` action.

Required:

- Keep current static activity content if needed.
- Align panel proportions and spacing to target.

### Fee Estimate

Current:

- Fee estimate exists but should align to target.

Target:

- Bottom right panel.
- Title: `Fee estimate`.
- Three compact amount cards: Estimated, Spent, Remaining.
- `View fee details` action.

Required:

- Keep static/mock content if existing implementation is static.
- Align density and button placement to target.

## Scope

Allowed:

- frontend-only React/CSS updates
- Workbench layout and copy alignment
- Workbench CSS density, grid, spacing, border, and table adjustments
- static frontend tests for target structure
- task board update after completion
- implementation plan document before coding
- alignment of current component JSX where needed
- replacement of placeholder copy with English target-equivalent copy

Forbidden:

- backend changes
- API contract changes
- database changes
- domain model changes
- new dependencies
- new routes
- StepInstance or Step persistence
- report generation
- file/material upload
- output generation
- approval package workflow restoration
- old lower workflow boards
- changing Matrix Editor behavior
- any backend endpoint/schema changes
- any API client contract changes
- any persistent state change
- broad frontend architecture refactor

## Required First Deliverable

Before implementation, create:

```text
docs/task_220_project_workbench_target_ui_alignment_plan.md
```

The plan must include:

- target UI interpretation
- current vs target delta list
- missing areas
- excess areas
- layout differences
- information hierarchy differences
- exact file-level changes
- component reuse strategy
- CSS alignment strategy
- static test assertions
- validation commands
- manual smoke path

Stop after writing the plan and wait for explicit user approval.

## Expected File Touches

Likely files:

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixOverview.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- `docs/task_board.md`
- `tasks/TASK_220_PROJECT_WORKBENCH_TARGET_UI_ALIGNMENT.md`

Avoid touching unless necessary:

- `backend/**`
- `frontend/src/api/client.ts`
- `frontend/src/pages/ProjectMatrixEditorPage.tsx`
- Matrix edit service files

## Acceptance Criteria

- Header visually follows target image hierarchy.
- Project readiness strip follows target image structure.
- Filter toolbar follows target image structure.
- Matrix Overview panel follows target image density and layout.
- Step Workspace follows target image section order and proportions.
- Runtime Attention bottom section follows target image structure.
- Recent Activity panel follows target image structure.
- Fee Estimate panel follows target image structure.
- The page reads as one Runtime Console, not as separate historical setup workflows.
- English UI copy is used.
- No lower legacy workflow board is reintroduced.
- No backend/API/domain changes are made.
- `npm run build` passes.
- TASK_220 static frontend assertions pass.

## Explicit Non-Acceptance

The task is not acceptable if:

- The result is a newly designed Workbench that only loosely resembles the target.
- The lower `Derived outputs`, `Runtime Support`, `Other materials`, or legacy evidence/setup detail panels reappear.
- The implementation adds live behavior that depends on unapproved backend changes.
- The Step Workspace becomes a complex data-entry workspace beyond the target image.
- The Matrix Overview loses its left-dominant operational table role.

## Validation

Required:

```powershell
cd frontend
npm run build
```

Required targeted tests:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task220 or task219 or task188 or task190"
```

Recommended governance tests after task board update:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

## Manual Smoke Path

1. Open a Project Workbench route.
2. Compare the page against `Project workbench UI.png`.
3. Confirm top header order and proportions match the target.
4. Confirm readiness strip is compact and top-level.
5. Confirm Matrix Overview and Step Workspace match target layout.
6. Confirm bottom Runtime Attention, Recent Activity, and Fee Estimate align to target.
7. Confirm no Derived Outputs board, Runtime Support board, or Other Materials panel appears.
8. Confirm Matrix Editor navigation still works.
