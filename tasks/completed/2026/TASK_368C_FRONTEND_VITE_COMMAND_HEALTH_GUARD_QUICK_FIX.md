# TASK_368C_FRONTEND_VITE_COMMAND_HEALTH_GUARD_QUICK_FIX

Status: `complete` / `accepted` / `locally_integrated`
Lane: `task-368c-frontend-vite-command-health-guard-quick-fix`
Owner role: Integrator closeout complete; no active implementation owner
Date: 2026-07-31

## Dispatch Worktree

- Branch: `lane/task-368c-frontend-vite-command-health-guard-quick-fix`
- Worktree:
  `D:\PythonProject\connlab-worktrees\task-368c-frontend-vite-command-health-guard-quick-fix`
- Governance/base commit:
  `e098c3c98b3333ada996e60bde1cc1bf494f970d`
- Creation verification: branch, worktree HEAD, status, and index match the exact recorded base
  and are clean.
- Global dispatch metadata is committed only on primary. The lane Quick Fixer owns its evidence
  file and must not edit task, plan, or board during implementation.

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

## Local Integration Acceptance

- Quick Fixer ready HEAD:
  `3fa8bf362ddc2110d18083b8dcd57ab0b2166bdf`.
- Reviewer/lane HEAD:
  `e7e5ac635aa06eda0c11e18436ffa60c2d83c062`.
- Primary pre-merge HEAD:
  `c776699774ea4eeceb8e8de851ef233b0af4a4e2`.
- Local non-fast-forward merge commit:
  `f7923ad9d3ce73cb47f53b39688a98425b6b4c41`.
- The merge was conflict-free. Its first-parent delta is exactly the four authorized launcher,
  bounded-test, Quick Fixer evidence, and Reviewer evidence paths; primary dispatch task, plan,
  and board were preserved.
- Merged-tree validation passed: bounded TASK_368C `3 passed`, combined packaging regression
  `8 passed`, Windows PowerShell parse, exact package/forbidden-path checks, `diff --check`,
  `git show --check`, and ancestry checks.
- The final launcher checks the exact `node_modules\.bin\vite.cmd` leaf, runs the existing install
  path when it is absent, checks again and throws before dev when repair leaves it absent, and
  preserves the healthy startup output plus `npm run dev` path.
- No real npm, network, repository frontend, Vite server, publication, push, or service restart
  was run. A final read-only check found that the current checkout's `vite.cmd` shim now exists,
  although this gate did not create or repair it. Shim health remains an environment condition
  evaluated on every launcher run: a still-present shim skips install, while a future missing shim
  invokes the guarded `npm install` path. This integration did not refresh any running process.
- The clean integrated TASK_368C lane branch/worktree is retained under permanent Orchestrator
  governance for future separately authorized safe maintenance retirement. No removal was
  attempted in this gate.
- TASK_368A, TASK_368B, browser-release, and frozen V2 retained state remain separate and were
  not touched.

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
