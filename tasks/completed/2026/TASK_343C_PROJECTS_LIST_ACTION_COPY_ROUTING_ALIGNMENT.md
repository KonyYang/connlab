# TASK_343C Projects List Action Copy Routing Alignment

Status: complete/accepted by Integrator
Lane: projects-list-action-copy-routing-alignment
Owner Role: Planner/Designer
Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Last Updated: 2026-06-27

## 1. Goal

Create the formal planning-first lane for Projects list action copy and routing alignment after `TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX` and `TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW` were accepted.

TASK_343C keeps lifecycle authority in the Project Workbench. The Projects list should remain a registry and routing surface: it helps operators find the right project state, understand the next step, and open the correct Workbench context. It must not duplicate Stop, Resume, Close as completed, or Close administratively mutation flows in the registry.

This lane completed the approved planning, Projects registry/list frontend implementation, Reviewer implementation gate, QA gate, and Integrator packaging/readiness flow.

## 2. Allowed Reason

- Parent `TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX` is complete/accepted and split the remaining lifecycle UX work into TASK_343A, TASK_343B, and TASK_343C.
- `TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX` is complete/accepted and implemented Workbench Stop/Resume UX.
- `TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW` is complete/accepted and implemented Workbench close completed/admin UX.
- `TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS` is complete/accepted and implemented Projects registry lifecycle views with read/navigation-oriented row actions only.
- `docs/task_board.md` currently has no active implementation lane and names TASK_343C as the next formal Discovery Gate candidate.
- The user explicitly requested TASK_343C formal planning-first lane creation/activation.

## 3. Scope

TASK_343C owns only Projects list action copy and routing alignment.

In scope:

- Projects list row action label and accessible label alignment.
- Projects list next-step copy alignment with accepted Workbench lifecycle states.
- Projects list routing intent into Workbench contexts.
- State-specific copy for active, stopped, closed completed, closed administrative, temporary/no-LTR planning, matrix-needed, and folder-created rows.
- Preservation of TASK_339B view categories: `On-going`, `Planning`, `Closed`, and `All`.
- Focused frontend selector/component tests after a separate implementation approval.

Out of scope:

- Stop, Resume, Close as completed, or Close administratively mutation controls in the Projects list.
- Backend/API/schema/write-guard changes.
- Workbench Stop/Resume/Close behavior changes from TASK_343A/TASK_343B.
- Projects registry redesign beyond copy/routing alignment.
- Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.

## 4. State Copy And Routing Contract

| Project state | Projects list status copy | Next-step copy intent | Row action intent |
|---|---|---|---|
| Active formal/registered with Matrix work | Business status such as `Matrix Needed` or existing active queue label | Continue Matrix or setup work in Workbench | Open Workbench |
| Active formal/registered with folder-created setup | `Folder Created` unless lifecycle overlay says otherwise | Continue from Workbench project setup and Matrix authority | Open Workbench |
| Active temporary/no-LTR planning | `Planning` or `Temporary Planning` where already used | Continue setup in Workbench | Open Workbench |
| Stopped formal/registered | `Stopped` | Resume or archive from Workbench | Open Workbench |
| Stopped temporary/no-LTR | `Stopped` plus temporary planning context where row identity already exposes it | Resume or administratively archive from Workbench | Open Workbench |
| Closed completed | `Closed: Completed` | View readonly completed archive | Open archive |
| Closed administrative | `Closed: Administrative` | View readonly administrative archive | Open archive |
| Closed unknown legacy fallback | `Closed` | View readonly archive | Open archive |

The Projects list must not present direct mutation affordances such as `Stop project`, `Resume project`, `Close project`, `Close as completed`, or `Close administratively`. Those remain Workbench-owned flows.

## 5. May Touch

Planner activation may touch:

- `tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md`
- `docs/task_343c_projects_list_action_copy_routing_alignment_plan.md`
- `docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_planner.md`
- `docs/task_board.md`

Reviewer plan gate may touch only its review evidence/checkpoint if the role creates one, or may report findings in thread.

Future Developer planning-first may touch only after Reviewer plan gate pass and routing:

- `docs/task_343c_projects_list_action_copy_routing_alignment_plan.md`
- `docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_developer.md`

Future implementation may touch only after explicit approval of the Developer planning pass. Likely candidates:

- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/pages/ProjectListPage.test.tsx`
- `frontend/src/project-dashboard.css` only if copy/action wrapping needs small registry style support
- `docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_developer.md`

## 6. Must Not Touch

- `backend/`
- root `tests/`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/`
- `frontend/src/features/project-lifecycle/` except read-only reference during planning/review
- `frontend/src/workbench.css`
- TASK_343A and TASK_343B implementation files except read-only reference
- TASK_336 through TASK_342 source files except read-only reference
- `AGENTS.md`
- `.agents/skills/`
- `docs/project_management/`
- database schema, migrations, API routes, write guards, Office gateways, public-drive workflows
- unrelated governance/orchestration residuals

## 7. Locked Paths

While TASK_343C is active, these paths are locked to this lane or read-only reference as stated:

- `tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md`
- `docs/task_343c_projects_list_action_copy_routing_alignment_plan.md`
- `docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_planner.md`
- `docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_developer.md`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/pages/ProjectListPage.test.tsx`
- `frontend/src/project-dashboard.css`

## 8. Validation Gate

Planner gate requires:

- task, plan, Planner evidence, and board row exist.
- Discovery Gate separates user facts, repository evidence, Planner assumptions, and open questions.
- May Touch, Must Not Touch, Locked Paths, Evidence, Validation Gate, Reviewer Gate, QA Gate, and Merge Gate are explicit.
- plan states Projects list lifecycle actions remain routing-only and no mutation controls are added.
- no product code is changed.

Future implementation validation must include:

- active, stopped, closed completed, closed administrative, temporary/no-LTR, matrix-needed, and folder-created state copy coverage.
- `Open` or equivalent row action copy routes into Workbench/archive intent without direct lifecycle writes.
- TASK_339B view categories remain intact.
- no direct imports or calls to lifecycle mutation helpers from Projects registry code.
- focused Projects registry tests pass.
- frontend build passes.
- package diff check passes.

## 9. Reviewer / QA / Merge Gates

Reviewer plan gate is required before Developer planning-first or implementation routing.

Future implementation must require:

- Developer planning-first checkpoint before product code.
- Reviewer implementation gate.
- QA gate if Reviewer or plan determines manual/browser smoke is needed for routing or accessibility confidence.
- Integrator packaging/readiness gate.

Merge remains blocked until:

- Developer evidence records implementation and validation.
- Reviewer has no blocking findings.
- QA passes or records an accepted non-blocking residual if QA is required.
- package contains only approved TASK_343C files plus board/evidence updates.
- backend/API/schema/frontend API client changes are absent.
- Workbench Stop/Resume/Close behavior, TASK_343A/TASK_343B implementation, future scope, and unrelated governance residuals are not mixed in.

## 10. Stop Point

Stop after Integrator packaging/readiness acceptance and completion callback.

Recommended next role: User if the TASK_343 series is complete, or Planner only if another TASK_343 sublane is explicitly required.

Do not start TASK_344 or later tasks, backend changes, Workbench behavior changes, Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, multi-user scope, push, reset, delete, or unrelated cleanup from this lane.
