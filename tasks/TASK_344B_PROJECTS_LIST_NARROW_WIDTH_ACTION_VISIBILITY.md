# TASK_344B Projects List Narrow Width Action Visibility

Status: complete - Integrator accepted
Lane: projects-list-narrow-width-action-visibility
Owner Role: Planner/Frontend Developer/Reviewer/QA/Integrator
Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Last Updated: 2026-06-28

## 1. Goal

Create a formal planning-first frontend UX fix lane for the post-acceptance smoke finding that `/projects` horizontally overflows around a 514px in-app browser width, leaving `Status`, `Next Step`, and `Action` outside the first visible area.

The fix should make TASK_343C's core `Open Workbench` / `Open archive` action copy discoverable at narrow in-app widths without reopening TASK_343C and without introducing lifecycle mutation controls in the Projects list.

## 2. Scope

In scope:

- Responsive `/projects` registry row layout at narrow in-app browser widths.
- Visibility/discoverability of row status, next-step copy, and row action.
- Preservation of TASK_339B views: `On-going`, `Planning`, `Closed`, and `All`.
- Preservation of TASK_343C routing-only behavior: no direct Stop/Resume/Close/Delete actions.
- Focused component/source tests and browser/manual smoke at about 514px width if available.

Out of scope:

- Backend/API/schema changes.
- Frontend API client changes.
- Workbench lifecycle behavior changes.
- TASK_343A/B/C accepted implementation changes outside the approved narrow `/projects` files.
- Projects registry redesign beyond narrow-width action visibility.
- Closed smoke-data setup, which belongs to TASK_344A.
- Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.

## 3. May Touch

Planner activation may touch:

- `tasks/TASK_344B_PROJECTS_LIST_NARROW_WIDTH_ACTION_VISIBILITY.md`
- `docs/task_344b_projects_list_narrow_width_action_visibility_plan.md`
- `docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_planner.md`
- `docs/task_board.md`

Future Developer planning-first may touch:

- `docs/task_344b_projects_list_narrow_width_action_visibility_plan.md`
- `docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md`

Future implementation may touch only after explicit approval:

- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/pages/ProjectListPage.test.tsx`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts` only if label/helper shape is needed for accessibility copy
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts`
- `frontend/src/project-dashboard.css`
- `docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md`

## 4. Must Not Touch

- `backend/`
- root `tests/`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/`
- `frontend/src/features/project-lifecycle/`
- `frontend/src/workbench.css`
- TASK_343A/B/C task/plan/evidence except read-only reference
- TASK_344A smoke-data lane files except read-only reference
- database schema or migrations
- public-drive, Office, LTR, Matrix, Fee, Report, or output authority workflows
- `AGENTS.md`
- `.agents/skills/`
- `docs/project_management/`
- unrelated governance/orchestration residuals

## 5. Locked Paths

- `tasks/TASK_344B_PROJECTS_LIST_NARROW_WIDTH_ACTION_VISIBILITY.md`
- `docs/task_344b_projects_list_narrow_width_action_visibility_plan.md`
- `docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_planner.md`
- future `docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md`
- future approved `/projects` registry files listed in May Touch

## 6. UX Contract

At around 514px in-app browser width:

- Project identity remains visible.
- Status is discoverable without relying on horizontal scroll.
- Next Step is discoverable without relying on horizontal scroll.
- Row action copy `Open Workbench` or `Open archive` is discoverable without relying on horizontal scroll.
- The layout must not add direct lifecycle mutation controls.
- The layout should remain calm, dense, and operational. Avoid decorative cards, side stripes, and future-feature copy.

Developer may choose the responsive pattern during planning, but the preferred direction is a compact responsive row treatment that keeps status, next step, and action near the project identity rather than requiring a wide table scroll.

## 7. Validation Gate

Planner gate requires:

- task, plan, Planner evidence, and board row exist.
- scope excludes lifecycle mutation controls and backend/API/schema changes.
- May Touch, Must Not Touch, Locked Paths, Evidence, Validation Gate, and Merge Gate are explicit.

Future implementation validation requires:

- focused tests for narrow `/projects` row action visibility or stable responsive class/markup behavior.
- focused tests still prove no Stop/Resume/Close/Delete registry controls.
- TASK_339B view filters still render.
- TASK_343C row action copy still routes through `onOpenProject(project_id)`.
- frontend build passes.
- source scans show no lifecycle mutation helper calls in Projects registry code.
- browser/manual smoke at about 514px verifies Status, Next Step, and Action are discoverable without horizontal scroll, or a documented blocker explains why browser verification is unavailable.

## 8. Reviewer / QA / Merge Gates

Reviewer plan gate is required before Developer planning-first or implementation routing.

Future implementation must require:

- Developer planning-first checkpoint before product code.
- Reviewer implementation gate.
- QA/browser smoke gate because the issue was found in real narrow-width smoke.
- Integrator packaging/readiness gate.

Merge remains blocked if:

- `/projects` still hides status/next-step/action behind horizontal scroll at the target width without an accepted reason.
- direct lifecycle mutation controls are introduced in the Projects list.
- backend/API/schema/frontend API client or Workbench lifecycle files are changed.
- TASK_344A smoke-data work or unrelated governance residuals are mixed in.

## 9. Stop Point

Stop after Integrator packaging/readiness, local controlled commit, and completion callback.

Recommended next role: User/Orchestrator decision. Separate TASK_344A closed lifecycle smoke-data fixture residual remains outside this package and must use its own legal gate if pursued.

Do not start TASK_344A, backend changes, Workbench changes, remote push, reset, delete, or unrelated cleanup from this TASK_344B closeout.
