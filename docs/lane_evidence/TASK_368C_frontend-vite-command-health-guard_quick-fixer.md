# TASK_368C Quick Fixer Evidence

Date: 2026-07-31
Task: `TASK_368C_FRONTEND_VITE_COMMAND_HEALTH_GUARD_QUICK_FIX`
Lane: `task-368c-frontend-vite-command-health-guard-quick-fix`
Role: permanent Quick Fixer
Status: `approved_pending_worktree`

## Authorization

- The user explicitly requested a direct fix for `scripts/run_frontend.ps1`.
- The supplied failure, read-only environment evidence, expected boundary, and non-goals are
  sufficient for the `AGENTS.md` section 19.1 fast path.

## Read-Only Reproduction

- `frontend\node_modules`: present.
- `frontend\node_modules\.bin\vite.cmd`: absent.
- `frontend\node_modules\vite\package.json`: present.
- Node: `v24.14.1`.
- npm: `11.11.0`.
- `npm ls vite --prefix frontend --depth=0`: `vite@7.3.2`.
- Current launcher checks only `node_modules`, so it skips `npm install` and later fails to
  resolve `vite`.

## Frozen Scope

May Touch:

- `scripts/run_frontend.ps1`
- `tests/unit/test_task_368c_run_frontend_vite_health_guard.py`
- this evidence file

All frontend files, dependency manifests/versions, other launchers, release packages, retained
lanes, and unrelated product paths are forbidden.

## Planned Worktree

- Branch: `lane/task-368c-frontend-vite-command-health-guard-quick-fix`
- Worktree:
  `D:\PythonProject\connlab-worktrees\task-368c-frontend-vite-command-health-guard-quick-fix`
- Base commit: pending governance checkpoint and worktree creation.

## Required Quick Fixer Record

Before callback, replace the pending status and record:

- exact branch/worktree/base verification;
- RED result from the fake-repository smoke;
- implementation and exact changed paths;
- GREEN pytest, packaging-note regression, PowerShell parse, and Git checks;
- confirmation that no real npm install/server start/frontend file mutation occurred;
- implementation/evidence commits;
- clean worktree/index proof;
- remote state and residuals;
- next role recommendation.

Stop status must be one of:

- `ready_for_review`;
- `blocked_scope_expansion`;
- `blocked_unexplained_test_failure`;
- `blocked_environment_behavior`.
