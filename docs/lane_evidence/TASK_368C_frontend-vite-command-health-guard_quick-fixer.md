# TASK_368C Quick Fixer Evidence

Date: 2026-07-31
Task: `TASK_368C_FRONTEND_VITE_COMMAND_HEALTH_GUARD_QUICK_FIX`
Lane: `task-368c-frontend-vite-command-health-guard-quick-fix`
Role: permanent Quick Fixer
Status: `ready_for_review`

## Authorization And Scope

- Current phase:
  `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- The user explicitly requested a direct repair after `scripts/run_frontend.ps1` failed with
  `'vite' is not recognized`.
- The Orchestrator formally dispatched the bounded Quick Fixer lane after confirming stable
  reproduction, no path conflict, and `AGENTS.md` section 19.1 eligibility.
- Primary dispatch HEAD:
  `c776699774ea4eeceb8e8de851ef233b0af4a4e2`.

May Touch:

- `scripts/run_frontend.ps1`
- `tests/unit/test_task_368c_run_frontend_vite_health_guard.py`
- this evidence file

No frontend file, dependency manifest, lockfile, `node_modules`, other launcher, product path, or
retained lane was changed.

## Worktree

- Branch: `lane/task-368c-frontend-vite-command-health-guard-quick-fix`
- Worktree:
  `D:\PythonProject\connlab-worktrees\task-368c-frontend-vite-command-health-guard-quick-fix`
- Governance/base:
  `e098c3c98b3333ada996e60bde1cc1bf494f970d`.
- Exact branch and HEAD matched the dispatch; worktree and index were clean before implementation.
- Implementation checkpoint:
  `a6e9fa193a84745afb742fd419fae9779d48c981`.

## Reproduction

- `frontend\node_modules`: present.
- `frontend\node_modules\.bin\vite.cmd`: absent.
- `frontend\node_modules\vite\package.json`: present.
- Node: `v24.14.1`; npm: `11.11.0`; installed package: `vite@7.3.2`.
- The original launcher checked only `node_modules`, skipped installation, and later could not
  resolve the Vite command.

## TDD

The bounded test copies the real repository launcher into a temporary fake repository and puts a
recording `npm.cmd` first on `PATH`. It never invokes real npm, the real frontend directory,
network access, or a Vite server.

RED:

- Missing shim with an existing `node_modules` directory recorded only `run dev`, not
  `install` then `run dev`.
- A successful-looking fake install that did not create the shim returned zero and still called
  `run dev`.
- Healthy-shim compatibility already passed.
- Result: `2 failed, 1 passed`, with both failures matching the missing health guard.

Minimal GREEN:

- The launcher now uses the Windows leaf file
  `node_modules\.bin\vite.cmd` as its dependency-health signal.
- When absent, it performs the existing `npm install`.
- It checks the shim again and throws an actionable error when installation leaves it missing,
  so `npm run dev` is not called.
- When the shim exists, installation remains skipped and the original startup output and
  `npm run dev` behavior are preserved.
- Result: `3 passed`.

## Validation

- `py -m pytest tests\unit\test_task_368c_run_frontend_vite_health_guard.py -q`:
  `3 passed`.
- `py -m pytest tests\unit\test_task_368c_run_frontend_vite_health_guard.py tests\unit\test_packaging_notes.py -q`:
  `8 passed`.
- Windows PowerShell `ScriptBlock.Create(...)` parse check: passed. The first wrapper invocation
  expanded `$null` in the caller shell; the protected equivalent was rerun and exited zero.
- `git diff --check`: passed.
- Exact changed-path and cached-path checks remained within the three-path allowlist.

## Self-Check And Handoff

- No cross-layer behavior, API, persistence, frontend product code, dependency version, hardcoded
  absolute repository path, or unrelated feature was added.
- No TODO, swallowed exception, real dependency install, server start, restart, publication,
  remote push, destructive cleanup, or unknown residual discard occurred.
- Remote state: not pushed.
- Final evidence-only checkpoint and clean worktree/index proof are recorded in the Orchestrator
  callback.
- Next role: mandatory Reviewer.
