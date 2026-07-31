# TASK_368C_FRONTEND_VITE_COMMAND_HEALTH_GUARD_QUICK_FIX

Status: approved; isolated Quick Fixer worktree preparation pending
Lane: `task-368c-frontend-vite-command-health-guard-quick-fix`
Owner role: permanent Quick Fixer
Date: 2026-07-31

## Current Phase / Why Allowed

- Current phase:
  `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- The user explicitly requested a direct repair after `scripts/run_frontend.ps1` failed with
  `'vite' is not recognized`.
- Read-only reproduction is stable:
  - `frontend\node_modules` exists;
  - `frontend\node_modules\.bin\vite.cmd` is missing;
  - `frontend\node_modules\vite\package.json` exists;
  - `npm ls vite --prefix frontend --depth=0` reports `vite@7.3.2`;
  - the current script checks only `node_modules`, skips `npm install`, then calls
    `npm run dev`.
- The board has no other active product task. The retained cancelled browser-release package does
  not contain `scripts/run_frontend.ps1`, and no active lane owns this path.
- This is one deterministic Windows launcher guard with a bounded test and no product/frontend
  source, dependency-version, authority, API, persistence, or schema change. It satisfies
  `AGENTS.md` section 19.1.

## Goal

Treat the Windows Vite command shim, rather than the `node_modules` directory alone, as the
frontend dependency-health signal before starting the development server.

## Confirmed Input

- A Windows ConnLab checkout with `frontend\node_modules` present.
- The Vite package directory may exist while `frontend\node_modules\.bin\vite.cmd` is missing.
- `scripts/run_frontend.ps1` is invoked from any current working directory.

## Expected Output

- When `node_modules\.bin\vite.cmd` exists, the script skips `npm install` and calls
  `npm run dev`.
- When the shim is absent, the script runs `npm install` even if `node_modules` exists.
- After installation, the script verifies the shim again and stops with an actionable error if
  the dependency command is still unavailable; it must not continue to `npm run dev`.
- The script keeps using repository-relative paths and does not change dependencies or product
  code.

## Acceptance Criteria

1. A bounded Windows PowerShell smoke with a temporary fake repository proves that an existing
   `node_modules` directory without `vite.cmd` triggers `npm install` before `npm run dev`.
2. The same smoke proves that a present `vite.cmd` skips installation.
3. A successful-looking install that still does not create `vite.cmd` fails closed and does not
   call `npm run dev`.
4. The script remains parseable by Windows PowerShell.
5. No real Vite server, dependency download, browser, backend, or localhost process is started by
   automated tests.
6. No frontend product file, `package.json`, lockfile, dependency version, `node_modules`, or
   unrelated launcher is modified.

## May Touch

- `scripts/run_frontend.ps1`
- `tests/unit/test_task_368c_run_frontend_vite_health_guard.py`
- `docs/lane_evidence/TASK_368C_frontend-vite-command-health-guard_quick-fixer.md`

Governance before dispatch and Integrator closeout may additionally update:

- this task file;
- `docs/task_368c_frontend_vite_command_health_guard_quick_fix_plan.md`;
- `docs/task_board.md`;
- role-specific Reviewer/Integrator evidence.

## Must Not Touch

- `frontend/**`, including `package.json`, lockfiles, `node_modules`, source, tests, and Vite config
- any dependency version or package-manager configuration
- `scripts/run_mvp_dev.ps1`, `scripts/run_frontend_build.ps1`, or any other launcher
- backend, API, domain, infrastructure, persistence, schema, Matrix, Fee, LTR, or Office paths
- release/packaging product paths
- cancelled browser-release retained branch/worktree/checkpoint
- TASK_368A/TASK_368B retained residuals
- frozen Controlled Lane V2 state
- remote push, publication, service restart, destructive cleanup, or unknown residual discard

## Validation Gate

Required:

```powershell
py -m pytest tests\unit\test_task_368c_run_frontend_vite_health_guard.py -q
py -m pytest tests\unit\test_task_368c_run_frontend_vite_health_guard.py tests\unit\test_packaging_notes.py -q
powershell -NoProfile -Command "$null = [ScriptBlock]::Create((Get-Content 'scripts\run_frontend.ps1' -Raw -Encoding UTF8))"
```

The bounded test must use a temporary copied script and fake `npm.cmd`. It must not run the
repository script against the real `frontend` directory or start a server.

## Merge Gate

- clean exact-path Quick Fixer checkpoint;
- bounded fake-npm smoke and existing packaging-note regression;
- mandatory permanent Reviewer pass because the script starts a developer process;
- permanent Integrator package/merged-tree validation and residual closeout;
- QA only if Reviewer identifies an environment-specific gap that cannot be covered by the
  bounded PowerShell smoke;
- no push, publication, dependency install in the real checkout, or service restart.

## Stop Conditions

Quick Fixer must stop and return to Orchestrator if:

- a second existing production script is required;
- the repair needs `package.json`, lockfile, dependency-version, frontend source, or Vite config
  changes;
- the test cannot avoid a real dependency install or server start;
- PowerShell behavior differs in a way that makes the expected health signal ambiguous;
- tests fail outside the declared script boundary without a clear cause;
- any destructive action, remote push, shared-path conflict, or retained-lane mutation is
  required.
