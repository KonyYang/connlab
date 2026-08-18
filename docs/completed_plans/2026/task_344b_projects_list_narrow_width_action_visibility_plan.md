# TASK_344B Projects List Narrow Width Action Visibility Plan

Status: complete - Integrator accepted
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Current Lane: projects-list-narrow-width-action-visibility
Role: Developer
Last Updated: 2026-06-28

## 1. Discovery Gate

Current active task/lane: no active implementation lane. `docs/task_board.md` marks TASK_343C complete/accepted.

Why Planner is allowed: user-reported post-acceptance smoke found a new visible blocker at around 514px in-app browser width. The user explicitly asked Planner to triage and create or plan a new fix lane instead of modifying accepted TASK_343C directly.

This pass is planning only. It does not edit frontend product code, backend code, tests, runtime behavior, or accepted TASK_343C files beyond new planning docs and board state.

### Confirmed By User

- TASK_343C is accepted.
- At about 514px browser width, `/projects` table horizontally overflows.
- `Status`, `Next Step`, and `Action` are not visible in the first viewport.
- TASK_343C's core `Open Workbench` / `Open archive` copy requires horizontal scrolling to see.
- Developer did not modify files during triage.

### Confirmed By Repository Evidence

- Current CSS sets `.project-table { min-width: 1060px; }` and `.project-table-wrap { overflow-x: auto; }`.
- `ProjectListPage` renders Status, Next Step, and Action as right-side table columns.
- TASK_343C evidence accepted real browser `/projects` smoke as a residual.
- TASK_343C remains routing-only and prohibits direct lifecycle mutation controls.

### Inferred By Planner

- The narrow-width issue is a frontend UX/layout defect, not a backend/API issue.
- A responsive row treatment is safer than reducing columns until labels become unreadable.
- Because the finding came from browser smoke, future implementation should require QA/browser smoke or an explicit browser-tooling blocker.

### Not Yet Confirmed

- Exact responsive pattern: stacked row, priority columns, sticky action, or another compact layout.
- Whether browser automation will be available for QA.

These do not block lane creation because the UX contract and file boundaries are clear.

Planner gate: passed by Reviewer.
Developer planning-first gate: ready.

## 2. UX Requirements

At approximately 514px in-app browser width:

- Users should see project identity, status, next step, and the row action without horizontal scrolling.
- `Open Workbench` and `Open archive` remain the only row action labels.
- Existing filters remain visible and usable.
- The table may become a stacked or compact row layout, but it must preserve scanability and semantic labels.
- The layout must not show Stop, Resume, Close, Delete, Report, StepInstance, AI, permissions, LAN/server, or multi-user controls.

## 3. Developer Planning-First Result

Read-only inspection confirmed the original browser finding:

- `frontend/src/project-dashboard.css` sets `.project-table { min-width: 1060px; }`.
- `.project-table-wrap` uses horizontal scrolling.
- `ProjectListPage` renders `Status`, `Next Step`, and `Action` as the rightmost columns.
- At a narrow in-app width, the core TASK_343C route action can be off-screen even though the row itself is present.

Approved first implementation strategy:

- Preserve the desktop table behavior for normal workstation widths.
- At narrow widths, change only the `/projects` table presentation into a compact stacked row treatment.
- Add stable `data-label` attributes and cell class names in `ProjectListPage` so CSS can show row labels without duplicating route actions.
- In the narrow media query, remove the table `min-width`, avoid horizontal overflow as the required path, visually hide the table header, and display each row as a dense operational stack.
- Order narrow row cells as Project ID, Status, Next Step, Action, then lower-priority sample/test item details.
- Keep the single row action button as the existing `onOpenProject(row.project_id)` route action.
- Keep action copy from TASK_343C helpers: active/stopped/planning rows use `Open Workbench`; closed rows use `Open archive`.
- Do not add direct Stop, Resume, Close, Delete, Report, StepInstance, AI, permissions, LAN/server, or multi-user controls.
- Do not add decorative card grids, side stripes, gradient text, or future-feature copy.

Exact later implementation file list:

- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/pages/ProjectListPage.test.tsx`
- `frontend/src/project-dashboard.css`
- `docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md`

Not planned for the first implementation pass:

- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts`

Those helper files remain optional only if implementation discovers that accessible route labels cannot be kept stable from `ProjectListPage` alone. Any such use must stay within TASK_343C routing-only semantics and be recorded in Developer evidence before review.

## 4. Implementation Planning Notes

Developer planning-first should inspect:

- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/pages/ProjectListPage.test.tsx`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts`
- `frontend/src/project-dashboard.css`

Planning-first inspection result:

- `ProjectListPage` already centralizes row rendering and action routing, so no new feature hook or API client work is needed.
- `projectRegistryLifecycleViews.ts` already owns business-readable status, next-step, and action copy, so no backend enum tokens are needed.
- `project-dashboard.css` is the correct style boundary for the Projects registry table and existing responsive toolbar rules.
- Component tests can verify stable narrow markup/class/data-label behavior, no mutation controls, and unchanged view filtering; real width behavior still needs QA/browser smoke.

## 5. Focused Test Plan

Later implementation should add focused tests for:

- narrow row markup exposes `data-label="Status"`, `data-label="Next Step"`, and `data-label="Action"` for each rendered row.
- the action cell still contains exactly the routing button and calls `onOpenProject(project_id)`.
- active registered and folder-created rows still show `Open Workbench`.
- stopped formal and stopped temporary rows still show `Open Workbench` and no list-level Resume/Close controls.
- closed completed/admin/legacy rows still show `Open archive` where test fixtures provide closed lifecycle overlays.
- `On-going`, `Planning`, `Closed`, and `All` filters continue to work.
- no Projects list direct Stop/Resume/Close/Delete mutation controls are rendered.
- no raw backend enum tokens become user-facing copy.

Because JSDOM does not prove CSS layout at 514px, component tests should be treated as structural regression coverage. QA/browser smoke remains required for the actual narrow-width acceptance.

## 6. Validation Plan

Future Developer validation should include:

```powershell
cd frontend
npm test -- --run src/features/projects-registry/projectRegistryLifecycleViews.test.ts src/pages/ProjectListPage.test.tsx
npm run build
```

```powershell
git diff --check -- frontend/src/pages/ProjectListPage.tsx frontend/src/pages/ProjectListPage.test.tsx frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts frontend/src/project-dashboard.css docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md
rg -n "[ \t]$" frontend/src/pages/ProjectListPage.tsx frontend/src/pages/ProjectListPage.test.tsx frontend/src/project-dashboard.css docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md
rg -n --glob '!*.test.ts' --glob '!*.test.tsx' "stopProjectLifecycle|resumeProjectLifecycle|closeProjectCompletedLifecycle|closeProjectAdministrativeLifecycle|deleteProject|removeProject|onStop|onResume|onClose|onDelete" frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx
rg -n --glob '!*.test.ts' --glob '!*.test.tsx' "Stop project|Resume project|Close project|Close as completed|Close administratively|Delete project|StepInstance|Report generation|AI review|permissions|LAN/server|multi-user" frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx frontend/src/project-dashboard.css
rg -n "border-left:\s*[2-9]px|border-right:\s*[2-9]px|background-clip:\s*text|linear-gradient" frontend/src/project-dashboard.css
git status --short -- backend tests frontend/src/api/client.ts frontend/src/features/project-workbench frontend/src/features/project-lifecycle frontend/src/workbench.css
```

QA/browser smoke should verify:

- viewport around 514px.
- `/projects` Status, Next Step, and Action discoverable without horizontal scroll.
- at least one active/stopped row shows `Open Workbench` access.
- at least one closed row, if available or supplied by TASK_344A, shows `Open archive` access.
- keyboard focus reaches visible row action.
- no horizontal scroll is needed to discover Status, Next Step, or the row action at the target width.

If browser control is unavailable, QA should record the exact blocker, then Reviewer/Integrator should decide whether structural tests plus source/CSS inspection are enough or whether TASK_344B remains blocked for real smoke.

## 7. Gates

Reviewer should block if the plan or implementation:

- adds lifecycle mutation controls to Projects list.
- hides the action behind horizontal scroll at the target width.
- changes backend/API/schema/frontend API client or Workbench lifecycle behavior.
- mixes closed smoke-data setup into this UX fix.
- removes TASK_339B filters/categories.

QA is required for implementation because the defect is a real narrow-width smoke finding.

Integrator may accept only after Reviewer and QA gates pass.

## 8. Non-Blocking Suggestions

Developer triage also mentioned:

- Close confirmation submit readiness clarity.
- disabled Delete temporary project visibility.
- stopped reason timestamp formatting.

These are not part of TASK_344B. They require separate Planner triage or explicit user approval if they become product work.

## 9. Developer Planning-First Validation

Developer planning-first updates are docs-only:

- `docs/task_344b_projects_list_narrow_width_action_visibility_plan.md`
- `docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md`

Developer planning-first must validate:

```powershell
Test-Path docs/task_344b_projects_list_narrow_width_action_visibility_plan.md
Test-Path docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md
git diff --check -- docs/task_344b_projects_list_narrow_width_action_visibility_plan.md docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md
rg -n "[ \t]$" docs/task_344b_projects_list_narrow_width_action_visibility_plan.md docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md
git status --short -- frontend backend tests docs/task_board.md
```

Product-code changes are forbidden in this planning-first pass. Any pre-existing product, board, or governance residuals must be recorded as external packaging context, not included as TASK_344B Developer planning edits.

## 10. Integrator Closeout

Integrator packaging/readiness accepted TASK_344B after Reviewer implementation gate and QA gate passed.

Accepted package boundary:

- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/pages/ProjectListPage.test.tsx`
- `frontend/src/project-dashboard.css`
- `tasks/TASK_344B_PROJECTS_LIST_NARROW_WIDTH_ACTION_VISIBILITY.md`
- `docs/task_344b_projects_list_narrow_width_action_visibility_plan.md`
- `docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_planner.md`
- `docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md`
- `docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_qa.md`
- `docs/lane_evidence/artifacts/TASK_344B_qa/`
- `docs/task_board.md`

Excluded from this package: TASK_344A smoke-data fixture/planning files, `AGENTS.md`, `.agents/skills/*`, `docs/project_management/*`, backend/API/schema/frontend API client, Workbench lifecycle implementation, TASK_343A/B/C implementation, and future-scope product work.

Stop after Integrator callback. Recommended next role: User/Orchestrator decision; route TASK_344A separately if the closed-row smoke data gap still needs closure.
