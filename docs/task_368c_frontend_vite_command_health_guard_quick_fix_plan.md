# TASK_368C Frontend Vite Command Health Guard Quick Fix Plan

Date: 2026-07-31
Status: approved; isolated worktree created and Quick Fixer dispatch ready
Task: `TASK_368C_FRONTEND_VITE_COMMAND_HEALTH_GUARD_QUICK_FIX`
Lane: `task-368c-frontend-vite-command-health-guard-quick-fix`

## 1. Discovery Gate

Current phase:

- `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active task/lane:

- TASK_368C is the current active task on its isolated Quick Fixer lane.
- TASK_368A and TASK_368B are complete/accepted and locally integrated.
- The cancelled browser-release lane and frozen V2 worktrees are retained but inactive.

Dispatch facts:

- branch: `lane/task-368c-frontend-vite-command-health-guard-quick-fix`;
- worktree:
  `D:\PythonProject\connlab-worktrees\task-368c-frontend-vite-command-health-guard-quick-fix`;
- governance/base:
  `e098c3c98b3333ada996e60bde1cc1bf494f970d`;
- worktree and index were verified clean at the exact base before dispatch.

Why planning is allowed:

- The user explicitly requested a direct fix and supplied the failing command, error, environment,
  and preferred bounded Quick Fixer scope.
- The script behavior and dependency state are reproducible from the repository checkout.

Confirmed by user:

- Running `D:\PythonProject\connlab\scripts\run_frontend.ps1` fails because the Vite command shim
  is missing while `node_modules` exists.
- The repair must not change frontend product code, dependency versions, or lockfiles.

Confirmed by repository evidence:

- Primary `master` is clean at discovery HEAD
  `012d523eb87ccd7c7141b1242fd10d8df5957339`.
- `scripts/run_frontend.ps1` tests only the existence of `node_modules`.
- The real checkout has:
  - Node `v24.14.1`;
  - npm `11.11.0`;
  - `vite@7.3.2` reported by npm;
  - a Vite package directory;
  - no `frontend\node_modules\.bin\vite.cmd`.
- The existing packaging-note test only checks that the launcher contains `npm install` and
  `npm run dev`; it does not exercise the health branch.
- No active task owns `scripts/run_frontend.ps1`.
- The retained cancelled browser-release checkpoint contains eleven other paths and no
  `scripts/run_frontend.ps1` change.

Inferred by Planner:

- On this Windows-only launcher, `node_modules\.bin\vite.cmd` is the smallest executable health
  signal for the declared `npm run dev` command.
- Re-running `npm install` when that shim is absent is the intended recovery action.
- A post-install shim check should fail closed so the original opaque `'vite' is not recognized`
  failure is not repeated.

Not yet confirmed:

- None that changes scope, ownership, expected behavior, or validation. The fake-npm smoke avoids
  dependence on the current machine's network and dependency cache.

Planning risk:

- Checking only the Vite package directory would reproduce the existing false healthy state.
- Running the real launcher during tests would start a long-lived server or mutate dependencies.
- Broadening the repair to package versions or other launchers would exceed the user-approved
  defect.

Decision:

- Continue. Definition of Ready is satisfied and the user's direct-fix instruction is explicit
  implementation approval for this exact scope.

## 2. Design

### 2.1 Command-health guard

In `scripts/run_frontend.ps1`:

1. resolve the existing repository-relative frontend root;
2. resolve the expected Windows Vite shim under `node_modules\.bin\vite.cmd`;
3. when the shim is absent, run the existing `npm install` recovery;
4. verify the shim again;
5. throw an actionable error if it is still absent;
6. otherwise continue through the existing startup output and `npm run dev`.

No package manifest, version, Vite config, frontend source, or other launcher changes.

### 2.2 Bounded fake-npm test

Add one task-specific pytest module that:

- copies the launcher into a temporary `<repo>\scripts` directory;
- creates a temporary `<repo>\frontend` directory;
- places a fake `npm.cmd` first on `PATH`;
- records exact npm calls without network access;
- optionally creates `node_modules\.bin\vite.cmd` when fake install runs;
- proves the missing, healthy, and failed-repair paths;
- never invokes the real repository frontend or a real Vite server.

## 3. File-Level Changes

| Path | Planned change |
|---|---|
| `scripts/run_frontend.ps1` | Use the Vite Windows command shim as the dependency-health guard and fail closed after unsuccessful repair |
| `tests/unit/test_task_368c_run_frontend_vite_health_guard.py` | New bounded temporary-repository/fake-npm PowerShell smoke |
| `docs/lane_evidence/TASK_368C_frontend-vite-command-health-guard_quick-fixer.md` | Record RED/GREEN, validation, checkpoint, and handoff |

## 4. Risks And Controls

| Risk | Control |
|---|---|
| Test mutates the real `frontend` directory | Copy the script to a temporary fake repository |
| Test starts Vite | Fake `npm.cmd` records calls and returns immediately |
| Missing shim remains hidden after install | Explicit post-install `Test-Path -PathType Leaf` check |
| Scope expands into dependency management | Lock all frontend manifests, lockfiles, versions, and config |
| Retained release work is absorbed | Verify its exact checkpoint path list; keep branch/worktree locked |

## 5. Validation

RED:

- fake repository has `node_modules` but no `vite.cmd`;
- current script skips install and reaches fake `npm run dev`.

GREEN:

- bounded TASK_368C pytest module;
- bounded module plus existing packaging-note regression;
- Windows PowerShell parser check;
- exact allowlist, cached diff, `git diff --check`, and final clean lane status.

## 6. Review And Integration

- Quick Fixer creates an exact-path clean checkpoint and updates its evidence.
- Reviewer independently inspects base..lane HEAD and reruns the bounded PowerShell smoke.
- QA is optional unless Reviewer identifies an uncovered Windows environment risk.
- Integrator merges only the exact reviewed package, reruns validation on primary, updates
  task/board/evidence, records residuals, and retains or safely retires the clean worktree without
  force.

No remote push, real dependency install, frontend server start, publication, or service restart is
authorized.

## 7. Stop Conditions

Stop if:

- another production script or any frontend/dependency file must change;
- the recovery requires network-dependent assertions;
- the fake-npm test cannot isolate the real checkout;
- an unrelated failure or path conflict appears;
- destructive cleanup or remote mutation is required.
