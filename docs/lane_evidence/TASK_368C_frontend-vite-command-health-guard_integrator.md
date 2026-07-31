# TASK_368C Integrator Evidence

Date: 2026-07-31
Task: `TASK_368C_FRONTEND_VITE_COMMAND_HEALTH_GUARD_QUICK_FIX`
Lane: `task-368c-frontend-vite-command-health-guard-quick-fix`
Role: ConnLab｜集成负责人 Integrator
Status: `integrator_accepted`
Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Authorized Gate

The permanent Orchestrator dispatched a controlled local merge gate after permanent Reviewer
status `reviewer_pass`, with no blocking or non-blocking finding. The frozen task makes QA
conditional, and Reviewer identified no environment-specific gap beyond the bounded Windows
PowerShell smoke; therefore no separate QA gate was required.

Remote push, publication, service restart, real dependency installation, repository frontend
execution, Vite startup, product-scope expansion, destructive cleanup, and worktree retirement
remained forbidden.

## Fresh Pre-Merge Facts

- Primary worktree: `D:\PythonProject\connlab`
- Primary branch: `master`
- Primary pre-merge HEAD:
  `c776699774ea4eeceb8e8de851ef233b0af4a4e2`
- Primary worktree/index: clean; no merge in progress
- Lane worktree:
  `D:\PythonProject\connlab-worktrees\task-368c-frontend-vite-command-health-guard-quick-fix`
- Lane branch:
  `lane/task-368c-frontend-vite-command-health-guard-quick-fix`
- Original base and exact merge-base:
  `e098c3c98b3333ada996e60bde1cc1bf494f970d`
- Quick Fixer ready HEAD:
  `3fa8bf362ddc2110d18083b8dcd57ab0b2166bdf`
- Reviewer pass / lane HEAD:
  `e7e5ac635aa06eda0c11e18436ffa60c2d83c062`
- Lane worktree/index: clean
- Remote branches containing lane HEAD: none

Ancestry checks proved the base is an ancestor of primary and lane, and the Quick Fixer ready HEAD
is an ancestor of the Reviewer/lane HEAD. The latest primary dispatch commit changed exactly the
TASK_368C task, plan, and board.

## Integrated Package

The complete `base..lane HEAD` package contains exactly four authorized paths:

1. `scripts/run_frontend.ps1`
2. `tests/unit/test_task_368c_run_frontend_vite_health_guard.py`
3. `docs/lane_evidence/TASK_368C_frontend-vite-command-health-guard_quick-fixer.md`
4. `docs/lane_evidence/TASK_368C_frontend-vite-command-health-guard_reviewer.md`

No `frontend/**`, package manifest, lockfile, dependency version/configuration, `node_modules`,
other launcher, backend, API, persistence, authority, release, task/plan/board, retained lane, or
frozen V2 path entered the lane package.

## Local Merge

Integrator performed a conflict-free local non-fast-forward merge.

- Merge commit:
  `f7923ad9d3ce73cb47f53b39688a98425b6b4c41`
- First parent:
  `c776699774ea4eeceb8e8de851ef233b0af4a4e2`
- Second parent:
  `e7e5ac635aa06eda0c11e18436ffa60c2d83c062`
- First-parent delta: exactly the four authorized paths
- Missing paths: zero
- Unexpected paths: zero
- Primary dispatch task/plan/board blobs: unchanged by the merge
- Merge `diff --check`: passed

No cherry-pick, partial integration, conflict resolution, push, publication, service restart, or
real frontend execution occurred.

## Merged-Tree Validation

Integrator ran on merged primary:

```text
py -m pytest tests\unit\test_task_368c_run_frontend_vite_health_guard.py -q
```

Result: `3 passed`.

```text
py -m pytest tests\unit\test_task_368c_run_frontend_vite_health_guard.py tests\unit\test_packaging_notes.py -q
```

Result: `8 passed`.

```text
powershell.exe -NoProfile -Command '$null = [ScriptBlock]::Create((Get-Content ''scripts\run_frontend.ps1'' -Raw -Encoding UTF8))'
```

Result: exit code `0`.

Additional checks:

- exact four-path first-parent allowlist: passed;
- forbidden-path count: zero;
- merge `git show --check`: passed;
- base-to-merge `git diff --check`: passed;
- lane and Quick Fixer ready commits are primary ancestors;
- primary and lane worktrees/indexes remained clean after validation.

## Frozen Behavior Boundary

The zero-context launcher diff changes only the dependency-health guard:

- `$viteCommand` resolves repository-relative
  `frontend\node_modules\.bin\vite.cmd`;
- two checks use `Test-Path -LiteralPath $viteCommand -PathType Leaf` against that exact leaf;
- a missing shim invokes the existing `npm install` recovery path;
- a post-install missing shim throws an actionable error before `npm run dev`;
- a healthy shim skips installation and preserves the original startup output and
  `npm run dev` invocation.

The bounded tests prove exact fake-npm invocation sequences:

- missing shim with successful repair: `install`, then `run dev`;
- healthy shim: `run dev` only;
- install that leaves the shim missing: `install` only, nonzero exit, no dev invocation.

No package, lockfile, dependency version/configuration, frontend source, `node_modules`, or other
launcher changed.

## No-Real-Npm And Runtime Provenance

Integrator did not run `scripts/run_frontend.ps1`, `npm install`, `npm run dev`, or any other real
npm/network/Vite command. The pytest module copies the launcher to a temporary fake repository
and puts a recording fake `npm.cmd` first on the child process `PATH`; it neither accesses the
repository frontend nor starts a server.

The local script fix is integrated. A final read-only filesystem check observed:

- `frontend\node_modules`: present;
- `frontend\node_modules\.bin\vite.cmd`: present;
- `frontend\node_modules\vite\package.json`: present.

This differs from the initial missing-shim reproduction, but this gate did not run any command
that could install or repair the real frontend dependencies. Shim health remains an environment
condition evaluated on each launcher run: if the shim is still present, the launcher skips
installation; if it is absent, the guarded path performs `npm install` and verifies it again.
This merge gate itself did not mutate `node_modules` or refresh any running localhost process.

## Remote And Runtime State

- Remote push: not performed.
- No locally known remote branch contains the integrated lane HEAD.
- Publication/deployment: not performed.
- Localhost/Vite start, stop, or restart: not performed.
- Current running services, if any, are unchanged.

## Residual Ledger

| Class | Item | Owner | Disposition |
|---|---|---|---|
| `integrated` | Complete four-path TASK_368C launcher/test/evidence package | none | Integrated by local merge `f7923ad9d3ce73cb47f53b39688a98425b6b4c41`; no package residual remains |
| `retain` | Clean integrated TASK_368C lane branch/worktree at `e7e5ac635aa06eda0c11e18436ffa60c2d83c062` | permanent Orchestrator governance | Retain until future separately authorized safe maintenance retirement; no removal attempted in this gate |
| `retain` (independent existing item) | TASK_368A merged branch plus unregistered non-worktree residual directory | permanent Orchestrator governance / User decision | Unchanged and not touched by TASK_368C |
| `retain` (independent existing item) | Clean integrated TASK_368B lane branch/worktree at `5cac86b60c728bcbb6a1b72a9e3d340fc976d21b` | permanent Orchestrator governance | Unchanged and not touched by TASK_368C |
| `retain` (independent existing item) | Cancelled browser-release checkpoint `0bf56ea09ba1a1baedd5ce982d0b47d73d1889df` | permanent Orchestrator governance / User decision | Unchanged, unintegrated, and not touched by TASK_368C |
| `retain` (independent frozen state) | Controlled Lane V2 worktrees/runtime snapshots | existing frozen governance owners | Unchanged; no V2 action was run |

There are no `duplicate`, `stale`, `format-only`, `conflict`, or unknown discard candidates.

## Stop Point

Status: `integrator_accepted`.

TASK_368C is complete/accepted and locally integrated. It was not pushed, published, deployed,
runtime-run, or used to mutate current `node_modules`. Next: Archive/Standby. No replacement or
follow-up task is created.
