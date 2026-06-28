# TASK_345A Project Lifecycle Business Model Contract - Planner Evidence

Date: 2026-06-28
Role: Planner
Task: `TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT`
Lane: `project-lifecycle-business-model-contract`
Status: ready_for_review
Implementation approved: no
Product code changed: no

## Summary

Created the formal planning-first contract draft for the Project lifecycle business model rework after the user answered the Discovery blockers.

This lane is planned and ready for Reviewer plan gate only. It does not approve backend, frontend, test, schema, public-drive LTR workbook authority, or product runtime implementation.

## User Answers Recorded

- Primary action policy uses Activate direction for stopped/closed, including Completed-closed projects. Permanent readonly and Reopen-only semantics are not the target.
- `Completed` is not a special close path. All close reasons use one unified close form.
- Temporary `Apply/Register LTR` is currently only a workflow entrypoint. Public-drive LTR workbook authority writes belong to a later authority lane.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `$impeccable` product context
- `docs/lane_evidence/DISCOVERY_project-lifecycle-business-model-rework_planner.md`

## Files Changed

- Added `tasks/TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT.md`
- Added `docs/task_345a_project_lifecycle_business_model_contract_plan.md`
- Added `docs/lane_evidence/TASK_345A_project-lifecycle-business-model-contract_planner.md`
- Updated `docs/task_board.md` with planned lane row and next-step text

## Lane State

- Status: `planned`
- Next role: Reviewer plan gate
- Developer routing: forbidden until Reviewer/user approval creates a downstream approved implementation lane

## May Touch Confirmed

- `tasks/TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT.md`
- `docs/task_345a_project_lifecycle_business_model_contract_plan.md`
- `docs/lane_evidence/TASK_345A_project-lifecycle-business-model-contract_planner.md`
- `docs/task_board.md` planned/proposed row and next-step text only

## Must Not Touch Confirmed

- `backend/`
- `frontend/`
- `tests/`
- `frontend/src/api/client.ts`
- public-drive, Office, LTR workbook authority files or gateways
- Matrix, Fee, Folder, Basic Information, Required Forms, Approval Package, Public Drive implementation files
- completed TASK_336 to TASK_344 task/plan/evidence files except read-only reference
- `AGENTS.md`
- `.agents/`
- `docs/project_management/`
- unrelated governance/orchestration residuals

## Locked Paths

All product implementation paths are locked for this Planner contract lane. Future lanes must declare their own locked paths after TASK_345A is accepted.

## Validation

Completed local validation after file writes:

- `git diff --check -- tasks/TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT.md docs/task_345a_project_lifecycle_business_model_contract_plan.md docs/lane_evidence/TASK_345A_project-lifecycle-business-model-contract_planner.md docs/task_board.md` passed with the existing CRLF warning for `docs/task_board.md` only.
- `git status --short -- backend frontend tests` showed existing dirty frontend paths outside this Planner lane: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx` and `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`. They were not modified, routed, or packaged by TASK_345A.
- `Select-String` checks found planned status, no implementation approval, Reviewer plan gate, Activate project, unified close form, public-drive LTR workbook authority deferral, Must Not Touch, and Locked Paths markers.

## Next Role

Reviewer plan gate for:

- Task: `TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT`
- Lane: `project-lifecycle-business-model-contract`

## Stop Point

Stop after validation and completion callback. Do not route Developer implementation.
