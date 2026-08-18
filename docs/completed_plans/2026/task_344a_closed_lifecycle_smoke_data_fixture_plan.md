# TASK_344A Closed Lifecycle Smoke Data Fixture Plan

Status: complete - Integrator accepted with documented data gap
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Current Lane: closed-lifecycle-smoke-data-fixture
Role: Planner
Last Updated: 2026-06-28

## 1. Discovery Gate

Current active task/lane: no active implementation lane. `docs/task_board.md` marks `TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT` complete and accepted after Reviewer, QA, and Integrator gates.

Why Planner is allowed: post-acceptance smoke found that closed completed/admin cases were not present in the current local registry/lifecycle overlay data, and the user explicitly asked Planner to route this as a new formal fix/fixture lane instead of reopening TASK_343C.

This pass is planning only. It does not create data, mutate databases, modify product code, or run QA.

### Confirmed By User

- TASK_343C is accepted and must not be directly modified.
- Current local `/api/projects/registry` or lifecycle overlays do not contain closed completed/admin projects for real smoke.
- QA/Closeout Coordinator may need safe closed smoke data, or Developer may create a fixed fixture only if approved.
- Production data must not be destructively mutated.

### Confirmed By Repository Evidence

- TASK_343C QA evidence accepted browser `/projects` smoke as a residual because browser tooling was unavailable.
- TASK_343C tests and source inspection cover closed copy in fixtures, but not current-environment closed data availability.
- TASK_343B implemented Workbench close completed/admin UX and closed archive suppression of Stop/Resume/Close controls.
- `docs/task_board.md` currently recommends a new formal lane before TASK_344 or later work.

### Inferred By Planner

- The closed data gap is a QA data/procedure problem, not a TASK_343C product-code defect by itself.
- The safest first route is a QA/Closeout smoke-data lane that records local data setup and smoke findings.
- If current data cannot be prepared safely through existing UI/API procedures, a later Developer planning-first pass may propose a local fixture script as a separate approved step.

### Not Yet Confirmed

- Whether QA can safely create closed completed/admin projects through existing local UI/API flows in the current environment.
- Whether a reusable fixture script is needed.

These questions affect QA execution details, but not this planning lane's file ownership or non-goals.

Planner gate: ready.

## 2. Smoke Procedure Contract

QA should prefer existing product flows against a local disposable workspace:

1. Prepare or identify one formal/registered project that can be closed completed.
2. Prepare or identify one project that can be closed administratively.
3. Record project IDs, route URLs, setup source, and whether the data is disposable.
4. Verify `/projects` shows closed completed/admin rows in the `Closed` view.
5. Verify row action copy is `Open archive`.
6. Open each Workbench and verify closed archive states are readonly and do not show Stop, Resume, Close again, or close type conversion controls.

If QA cannot prepare data safely, QA should stop with a blocker and recommend a Developer fixture-planning lane.

## 3. Safety Rules

- Use local disposable data only.
- Do not edit public-drive files, Office documents, LTR workbooks, or operator production data.
- Do not add hidden test-only behavior to production code.
- Do not change lifecycle API, schema, write guards, or frontend implementation.

## 4. Gates

Reviewer plan gate should check that the lane is non-destructive and does not authorize product-code edits.

QA gate should record:

- environment
- project IDs
- setup path
- screenshots or text observations if screenshots are unavailable
- pass/fail status for registry closed rows and Workbench closed archive actions
- cleanup/disposability status

Integrator may close after QA evidence is accepted.

## 5. Integrator Closeout

Integrator accepted TASK_344A after Reviewer plan gate and QA gate passed.

Accepted outcome:

- QA completed read-only registry/API and browser Closed-view smoke.
- Current local registry had `44` rows: `25` cancelled, `6` draft, and `13` ltr_registered.
- Lifecycle overlays swept `44` rows: `19` active, `25` stopped, and `0` closed.
- Browser Closed view at `514x720` showed `No projects in this view`, row count `0`, `Open archive` count `0`, `Open Workbench` count `0`, and Stop/Resume/Close count `0`.
- QA did not mutate local/project data and did not modify product code.

Accepted package boundary:

- `tasks/TASK_344A_CLOSED_LIFECYCLE_SMOKE_DATA_FIXTURE.md`
- `docs/task_344a_closed_lifecycle_smoke_data_fixture_plan.md`
- `docs/lane_evidence/TASK_344A_closed-lifecycle-smoke-data-fixture_planner.md`
- `docs/lane_evidence/TASK_344A_closed-lifecycle-smoke-data-fixture_qa.md`
- `docs/lane_evidence/artifacts/TASK_344A_qa/`
- `docs/task_board.md`

Excluded from this package: Workbench dirty product files, `AGENTS.md`, `.agents/skills/*`, `docs/project_management/*`, backend/API/schema/frontend API client, TASK_343A/B/C implementation files, TASK_344B accepted implementation files, production/user data, public-drive files, Office documents, and LTR authority files.

Stop after Integrator callback. Recommended next role: User/Planner decision; route a separate Developer fixture-planning lane only if repeatable closed completed/admin smoke data is still required.
