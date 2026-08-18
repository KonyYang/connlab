# TASK_342 Lifecycle Integration QA And Board Closeout Plan

Last Updated: 2026-06-27
Status: complete - Integrator accepted
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Current Lane: lifecycle-integration-qa-and-board-closeout
Role: Developer / Closeout Coordinator planning-first

## 1. Discovery Gate

Current active task/lane: no active implementation lane. `docs/task_board.md` marks TASK_341 complete/accepted after Reviewer, QA, and Integrator gates.

Why Planner is allowed: the user explicitly asked Planner to create or activate the missing formal planning-first lane `TASK_342_LIFECYCLE_INTEGRATION_QA_AND_BOARD_CLOSEOUT`. The board says the next step is Planner creation or activation before any implementation continues.

User goal restatement:

- Create the final lifecycle/workbench series closeout lane.
- Keep the task as integration QA and board closeout, not product feature implementation.
- Verify TASK_339A, TASK_339B, TASK_340, and TASK_341 evidence and board consistency.
- Define role sequence, evidence, validation, merge gates, and residual-risk handling.
- Do not start backend guard changes, Workbench rewrite, registry redesign, Report generation, StepInstance, AI, permissions, LAN/server, multi-user, or remote push.

Confirmed by user:

- TASK_339A is complete/accepted.
- TASK_339B is complete/accepted.
- TASK_340 is complete/accepted as planning output only.
- TASK_341 is complete/accepted after Reviewer, QA, and Integrator gates.
- Latest local commit is `d87345e feat(frontend): complete TASK_341 workbench shell`.
- TASK_342 formal files are missing.
- External governance/orchestration dirty residuals must not be mixed into product implementation packaging unless TASK_342 explicitly defines auditable governance closeout scope.

Confirmed by repository evidence:

- `docs/task_board.md` reports no active implementation lane and TASK_341 complete/accepted.
- `git log -1 --oneline` reports `d87345e feat(frontend): complete TASK_341 workbench shell`.
- TASK_342 formal task, plan, and evidence files did not exist before this Planner turn.
- `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md` lists TASK_342 as the final integration/QA lane.
- `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md` defines TASK_342 scope as integration validation, manual smoke, review/QA evidence, and final board update by Integrator.
- `docs/lane_evidence/TASK_339A_frontend-readonly-model_developer.md` records `Integrator gate: accepted`.
- `docs/lane_evidence/TASK_339B_projects-registry-lifecycle-views_developer.md` records `Integrator gate: accepted`.
- `docs/lane_evidence/TASK_340_unified-shell-plan_planner.md` records `Status: complete`.
- `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md` records Reviewer pass, QA pass, Integrator acceptance, and accepted package files.
- `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_qa.md` records `QA gate: pass` with residual non-blocking risk: real browser narrow-viewport overlap and tab focus order were not screenshot/tab-order verified because browser tooling was unavailable.
- Current worktree has external governance/orchestration dirty residuals under `AGENTS.md`, `.agents/skills/*`, and `docs/project_management/*`.

Inferred by Planner:

- TASK_342 should be docs/QA/integration closeout only.
- A Closeout Coordinator planning-first pass is useful to confirm exact final smoke and residual-risk disposition before QA/Integrator closeout.
- QA should attempt to close TASK_341 residual browser/tab-order risk if tooling is available; otherwise it must record a clear non-blocking or blocking disposition.

Not yet confirmed:

- Whether browser automation will be available to the QA thread during TASK_342.

Planning risk:

- Without a formal lane, final closeout could blur product implementation, QA, and Integrator responsibilities.
- Without residual-risk disposition, the TASK_341 browser/tab-order gap could be forgotten.
- Without strict May Touch/Must Not Touch, unrelated governance residuals could be mixed into product closeout packaging.

Recommendation:

Continue with explicit assumptions and activate TASK_342 as `approved` for Closeout Coordinator planning first only. Product code remains locked.

## 2. Definition Of Ready

Definition of Ready is satisfied for a planning-first closeout lane:

- user goal and closeout scenario are clear
- board state and dependencies are verified from files
- existing behavior and residual risk are checked from TASK_341 QA and Integrator evidence
- formal task, plan, evidence, and board lane are created by this Planner action
- dependencies and serialization constraints are explicit
- May Touch, Must Not Touch, Locked Paths, evidence, validation, and merge gates are concrete
- acceptance path is testable or reviewable through evidence audit, optional final smoke, Reviewer, QA, and Integrator gates
- non-goals prevent product feature scope creep
- unresolved browser tooling availability is documented as a QA-time residual-risk decision, not a blocker to planning-first activation

Planner gate: ready.

## 3. Closeout Objective

TASK_342 should answer:

```text
Is the lifecycle/workbench series complete, consistent, validated at the declared level, and ready to close on the board?
```

The closeout should cover:

- TASK_339A readonly model acceptance
- TASK_339B registry lifecycle views acceptance
- TASK_340 shell plan acceptance
- TASK_341 Workbench shell implementation acceptance
- TASK_341 residual QA risk disposition
- final board consistency
- explicit next-scope boundary after lifecycle/workbench series closeout

## 4. Required Closeout Planning Pass

Closeout Coordinator must update this plan and evidence before QA/Integrator work.

Required planning output:

- exact checklist of task/plan/evidence files to verify
- exact `docs/task_board.md` status checks
- final smoke commands and expected results
- browser/manual smoke availability decision
- residual-risk disposition plan
- Reviewer, QA, and Integrator stopping gates

## 5. Recommended Final Smoke Plan

Closeout Coordinator may refine this list before user approval.

Frontend lifecycle/workbench smoke:

```powershell
cd frontend
npm test -- --run src/features/project-lifecycle/projectLifecycleReadonlyModel.test.ts src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts src/features/projects-registry/projectRegistryLifecycleViews.test.ts src/pages/ProjectListPage.test.tsx src/features/project-workbench/projectWorkbenchShellModel.test.ts src/features/project-workbench/ProjectWorkbenchLayout.test.tsx
npm run build
```

Backend lifecycle/write-guard smoke, if closeout owner judges rerun useful:

```powershell
py -m pytest tests\unit\test_project_lifecycle_state_service.py tests\integration\test_project_lifecycle_api.py tests\unit\test_project_lifecycle_management_service.py tests\integration\test_project_registry_summary_api.py -q
```

Browser/manual smoke:

- If browser tooling is available, inspect a narrow viewport for Project Workbench shell overlap and walk real tab order through Back to projects, Project State, lifecycle banner, Matrix/primary workspace, Outputs, and History where present.
- If browser tooling is unavailable, QA must explicitly decide whether TASK_341 static/component coverage is sufficient for non-blocking closeout or whether the series remains blocked pending browser smoke.

## 6. May Touch

Planner may touch:

- `tasks/TASK_342_LIFECYCLE_INTEGRATION_QA_AND_BOARD_CLOSEOUT.md`
- `docs/task_342_lifecycle_integration_qa_and_board_closeout_plan.md`
- `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_developer.md`
- `docs/task_board.md`

Closeout Coordinator planning may touch:

- `docs/task_342_lifecycle_integration_qa_and_board_closeout_plan.md`
- `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_developer.md`

Reviewer may touch:

- `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_developer.md`

QA may touch:

- `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_qa.md`
- `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_developer.md` only to add a QA handoff pointer if the approved plan requires it

Integrator may touch:

- `docs/task_board.md`
- `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_developer.md`
- `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_qa.md` only for integration decision notes

## 7. Must Not Touch

- frontend product source
- backend product source
- root `tests/` or frontend test source files
- database migrations or schema files
- Office gateway internals
- public-drive/LTR authority paths
- Matrix/Fee business rules
- Project Folder backend behavior
- Projects registry implementation
- Workbench shell implementation
- TASK_339A/TASK_339B/TASK_340/TASK_341 product package files except read-only verification
- StepInstance, Report generation, AI, permissions, LAN/server, or multi-user scope
- unrelated governance/orchestration residual files unless a separate governance lane explicitly owns them

## 8. Locked Paths

- `tasks/TASK_342_LIFECYCLE_INTEGRATION_QA_AND_BOARD_CLOSEOUT.md`
- `docs/task_342_lifecycle_integration_qa_and_board_closeout_plan.md`
- `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_developer.md`
- `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_qa.md` once QA creates it

## 9. Validation Gate

Before review:

- Closeout planning pass confirms all required TASK_339A/339B/340/341 task, plan, and evidence files exist.
- Closeout planning pass confirms board status matches evidence status for TASK_339A, TASK_339B, TASK_340, and TASK_341.
- Closeout planning pass defines final smoke scope and browser/manual smoke availability decision.
- No product source files are changed.
- No TASK_342 QA or Integrator closeout is performed before the planning pass is reviewed and approved.

Before Integrator closeout:

- Reviewer gate passes for closeout plan/evidence consistency.
- QA gate passes or records a clear non-blocking residual-risk disposition.
- Any final smoke commands declared in the approved plan are run or explicitly waived with reason.
- External governance/orchestration dirty residuals are excluded from the TASK_342 product closeout package unless separately approved as governance scope.

## 10. Merge Gate

Reviewer, QA, and Integrator gates are required before TASK_342 can be accepted.

Merge remains blocked if:

- product code is modified from TASK_342
- board and evidence disagree on accepted status for TASK_339A/339B/340/341
- TASK_341 residual QA risk is ignored rather than dispositioned
- final smoke failures are unresolved
- backend guard changes, Workbench rewrite, registry redesign, Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope appear
- remote push is attempted

## 11. Role Sequence And Stop Gates

1. Closeout Coordinator planning pass:
   - update TASK_342 plan/evidence only
   - confirm evidence checklist and final smoke plan
   - stop for user approval

2. Reviewer gate:
   - review TASK_342 plan/evidence/diff for scope and consistency
   - write pass/blocking findings into TASK_342 evidence
   - stop

3. QA gate:
   - run approved final smoke/checks
   - create or update QA evidence
   - explicitly disposition residual risk
   - stop

4. Integrator gate:
   - confirm Reviewer/QA gates are passed
   - update `docs/task_board.md` to close the lifecycle/workbench series
   - record final integration decision
   - do not push remote

## 12. Closeout Coordinator Planning-First Resolution

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current task/lane: `TASK_342_LIFECYCLE_INTEGRATION_QA_AND_BOARD_CLOSEOUT` / `lifecycle-integration-qa-and-board-closeout`.

Allowed reason: `docs/task_board.md` marks TASK_342 approved for Developer/Closeout Coordinator planning first, TASK_339A/TASK_339B/TASK_340/TASK_341 are complete/accepted, and the user explicitly requested this planning-first closeout pass.

This pass is documentation and coordination only. It does not run final QA, does not perform final board closeout, does not modify product code or test source, and does not merge, commit, or push.

### Read-Only Audit Summary

Required files exist:

- TASK_339A task, plan, and developer evidence exist.
- TASK_339B task, plan, and developer evidence exist.
- TASK_340 task, plan, and planner evidence exist.
- TASK_341 task, plan, developer evidence, and QA evidence exist.
- TASK_342 task, plan, and developer/closeout evidence exist.

Board/evidence consistency:

- TASK_339A board row says complete. Developer evidence records `Reviewer gate: pass`, Integrator validation rerun, and `Integrator gate: accepted`.
- TASK_339B board row says complete. Developer evidence records `Reviewer implementation gate: pass`, QA not required, Integrator validation rerun, and `Integrator gate: accepted`.
- TASK_340 board row says complete/accepted as planning output only. Planner evidence records `Status: complete`; plan records accepted/complete follow-up and no product code changes.
- TASK_341 board row says complete/accepted after Reviewer, QA, and Integrator gates. Developer evidence records Reviewer pass, QA pass, Integrator validation rerun, and `Integrator gate: accepted`; QA evidence records `Status: qa_pass`.

Evidence nuance:

- Some prior developer evidence files keep their top-level execution-stage status, but the later Integrator sections are the acceptance authority. Reviewer/QA/Integrator should verify final gate sections, not only the first `Status:` line.
- `docs/task_board.md` is currently modified by Planner/Integrator activation work. This planning-first pass must not edit it.
- No current `frontend/`, `backend/`, or root `tests/` diff is part of TASK_342 planning-first.

## 13. Final Closeout Checklist

Reviewer should check before QA:

- TASK_342 plan/evidence were the only files modified by the Closeout Coordinator planning-first pass.
- TASK_342 scope remains docs/QA/integration closeout only.
- No product code, frontend test source, backend code, root tests, database/schema, Office gateway, public-drive/LTR authority, Matrix/Fee business rules, Project Folder backend, registry implementation, or Workbench shell implementation was changed.
- TASK_339A, TASK_339B, TASK_340, and TASK_341 have formal task, plan, and evidence files.
- Board rows for TASK_339A/339B/340/341 say complete/accepted and match final evidence gate sections.
- TASK_341 QA residual risk is explicitly carried into TASK_342 QA planning.
- TASK_342 does not introduce Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, multi-user, registry redesign, backend guard change, Workbench rewrite, remote push, or unrelated governance residual packaging.

QA should run or explicitly waive with reason:

```powershell
cd frontend
npm test -- --run src/features/project-lifecycle/projectLifecycleReadonlyModel.test.ts src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts src/features/projects-registry/projectRegistryLifecycleViews.test.ts src/pages/ProjectListPage.test.tsx src/features/project-workbench/projectWorkbenchShellModel.test.ts src/features/project-workbench/ProjectWorkbenchLayout.test.tsx
npm run build
```

Optional backend smoke may be run if QA wants to re-cover lifecycle/write-guard integration at closeout:

```powershell
py -m pytest tests\unit\test_project_lifecycle_state_service.py tests\integration\test_project_lifecycle_api.py tests\unit\test_project_lifecycle_management_service.py tests\integration\test_project_registry_summary_api.py -q
```

Static source search should be run or recorded as already covered by TASK_341 QA:

```powershell
rg -n "View activity history|Report generation|StepInstance|AI review|permissions|LAN/server|multi-user|closed_completed|closed_administrative" frontend\src\features\project-workbench frontend\src\workbench.css
```

Expected QA outcome:

- Frontend lifecycle/workbench/registry focused tests pass.
- Frontend build passes, allowing the existing Vite chunk-size warning if no new build error appears.
- Static search has no user-facing runtime future-scope controls or raw closed enum copy.
- Any backend smoke, if run, passes.
- Browser/manual smoke is passed, waived as non-blocking with evidence, or elevated to blocking with concrete failure details.

## 14. TASK_341 Residual QA Risk Disposition Plan

Residual from TASK_341 QA:

- Real browser narrow-viewport overlap and tab focus order were not screenshot/tab-order verified because the TASK_341 QA thread lacked browser tooling and frontend dependencies did not include Playwright.

TASK_342 QA must handle it in this order:

1. If a browser control tool is available, run a narrow viewport smoke on the Project Workbench shell and record screenshots or written observations for:
   - Project State lifecycle label and readonly reason visible without overlap
   - Matrix/primary workspace visible before Outputs
   - Outputs rail responsive wrapping
   - closed completed and closed administrative labels visible
   - no Resume/Stop/Close/Delete lifecycle write action in closed states
   - keyboard/tab order starts at Back to projects and proceeds through meaningful controls/regions in logical order
2. If no browser control tool is available, QA may record the residual as non-blocking only if:
   - focused component tests and source/static checks still pass
   - CSS responsive constraints remain present
   - there is no evidence of overlap, missing readonly reason, or hidden primary action from available static checks
   - QA explicitly states that real browser visual/tab-order verification remains a residual manual follow-up
3. QA must mark the residual as blocking if:
   - browser smoke is available and finds overlap or incoherent tab order
   - focused tests/build/source checks fail
   - a closed/stopped state exposes lifecycle write actions
   - Matrix is no longer before Outputs in DOM or visible hierarchy
   - QA cannot inspect enough evidence to decide non-blocking disposition

## 15. Gate Order And Role Touch Boundaries

1. Reviewer gate after this planning pass:
   - May touch only `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_developer.md`.
   - Reviews plan/evidence/diff, required inputs, board/evidence consistency, scope, validation plan, and residual-risk disposition plan.
   - Stops with pass or blocking findings.

2. QA gate after Reviewer pass and user/orchestrator routing:
   - May create/update `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_qa.md`.
   - May update TASK_342 developer evidence only to add a QA evidence pointer if the approved plan requires it.
   - May run tests/build/browser/manual smoke, but must not modify product code or test source.
   - Stops with QA pass/fail/blocked and residual-risk disposition.

3. Integrator gate after Reviewer and QA pass:
   - May update `docs/task_board.md` and TASK_342 evidence files for final integration decision.
   - Must confirm product source/test source remain unchanged by TASK_342.
   - Must close the lifecycle/workbench series on the board only if Reviewer/QA gates pass and no blocking residual risk remains.
   - Must not push remote unless a later explicit user instruction authorizes remote push.

Closeout planning gate: ready.

Implementation/final closeout remains blocked until the user explicitly approves the next gate.

## 16. Planner Validation Commands

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Test-Path tasks\TASK_342_LIFECYCLE_INTEGRATION_QA_AND_BOARD_CLOSEOUT.md
Test-Path docs\task_342_lifecycle_integration_qa_and_board_closeout_plan.md
Test-Path docs\lane_evidence\TASK_342_lifecycle-integration-qa-and-board-closeout_developer.md
Select-String -Path docs\task_board.md -Pattern 'lifecycle-integration-qa-and-board-closeout' -Encoding UTF8
Select-String -Path docs\task_342_lifecycle_integration_qa_and_board_closeout_plan.md -Pattern 'Planner gate: ready' -Encoding UTF8
Select-String -Path docs\task_342_lifecycle_integration_qa_and_board_closeout_plan.md -Pattern 'residual-risk' -Encoding UTF8
rg -n "[ \t]$" tasks\TASK_342_LIFECYCLE_INTEGRATION_QA_AND_BOARD_CLOSEOUT.md docs\task_342_lifecycle_integration_qa_and_board_closeout_plan.md docs\lane_evidence\TASK_342_lifecycle-integration-qa-and-board-closeout_developer.md docs\task_board.md
git diff --check -- tasks/TASK_342_LIFECYCLE_INTEGRATION_QA_AND_BOARD_CLOSEOUT.md docs/task_342_lifecycle_integration_qa_and_board_closeout_plan.md docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_developer.md docs/task_board.md
```

## 17. Stop Point

Closeout Coordinator planning-first gate is ready.

TASK_342 closeout is complete and accepted after Reviewer closeout planning gate, QA closeout gate, and Integrator final packaging/readiness gate.

The TASK_339A-TASK_342 lifecycle/workbench series is locally closed. Do not push remote or start a new feature scope from this lane.
