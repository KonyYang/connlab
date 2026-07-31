# TASK_368C Reviewer Evidence

Date: 2026-07-31
Task: `TASK_368C_FRONTEND_VITE_COMMAND_HEALTH_GUARD_QUICK_FIX`
Lane: `task-368c-frontend-vite-command-health-guard-quick-fix`
Role: permanent Reviewer
Status: `reviewer_pass`

## Authorization And Governance

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Primary `docs/task_board.md` records TASK_368C as the current active task and authorizes the
  Quick Fixer -> Reviewer -> Integrator gate sequence.
- The authoritative primary task and plan were read at dispatch HEAD
  `c776699774ea4eeceb8e8de851ef233b0af4a4e2` and treated as read-only governance.
- Reviewer changed no launcher, test, frontend, dependency, Quick Fixer evidence, or product file.
  No real npm, network, Vite server, restart, merge, push, cherry-pick, or destructive action ran.

## Inspected Commits And Worktree

- Governance base: `e098c3c98b3333ada996e60bde1cc1bf494f970d`
- Implementation checkpoint: `a6e9fa193a84745afb742fd419fae9779d48c981`
- Required review HEAD: `3fa8bf362ddc2110d18083b8dcd57ab0b2166bdf`
- Branch: `lane/task-368c-frontend-vite-command-health-guard-quick-fix`
- Worktree:
  `D:\PythonProject\connlab-worktrees\task-368c-frontend-vite-command-health-guard-quick-fix`

The exact branch and HEAD matched the dispatch, the base is an ancestor of the required review
HEAD, and the worktree/index were clean before review.

## Scope Review

The committed range
`e098c3c98b3333ada996e60bde1cc1bf494f970d..3fa8bf362ddc2110d18083b8dcd57ab0b2166bdf`
contains exactly:

- `scripts/run_frontend.ps1`
- `tests/unit/test_task_368c_run_frontend_vite_health_guard.py`
- `docs/lane_evidence/TASK_368C_frontend-vite-command-health-guard_quick-fixer.md`

No frontend source, `package.json`, lockfile, dependency version/configuration, `node_modules`,
other launcher, backend, API, persistence, authority, release, or governance file changed. The
implementation-checkpoint-to-review-HEAD range is evidence-only.

## Findings

### Blocking

- None.

### Non-Blocking

- None.

## Detailed Review

### Launcher Guard And Compatibility

- The launcher builds the repository-relative expected path
  `frontend\node_modules\.bin\vite.cmd` and tests it with `-LiteralPath` plus `-PathType Leaf`.
- A missing shim runs the existing `npm install` path regardless of whether `node_modules`
  already exists.
- The same exact leaf is checked after installation. If it remains absent, the script throws an
  actionable error containing the expected path and does not call `npm run dev`.
- A healthy shim skips installation. Existing startup text, repository-relative location
  resolution, and `npm run dev` behavior are unchanged.
- Quoting and path handling are valid for Windows PowerShell, including worktree paths with
  spaces because paths are passed as values rather than interpolated command fragments.

Reviewer explicitly assessed the absence of a separate `$LASTEXITCODE` check after `npm install`.
This is not blocking under the approved contract: the exact Vite shim is the declared health
signal, and every failed repair that leaves it absent is converted to a nonzero terminating error
before startup. A partial install that creates the declared shim can continue to the unchanged
`npm run dev` command, whose own exit behavior remains visible; broad dependency-health policy was
not part of this bounded task.

### Regression Isolation And Assertions

- The test copies the production launcher into a temporary fake repository and derives the fake
  frontend path from that copied script.
- A temporary `npm.cmd` is placed first on the child process `PATH`; it records calls and returns
  immediately, so no repository frontend, real npm, network, or server is touched.
- The missing-shim recovery asserts exact ordering: `install`, then `run dev`.
- The healthy-shim path asserts install is skipped and only `run dev` is called.
- The successful-looking install-without-shim path asserts a nonzero result, only `install`, no
  dev call, and the actionable blocker text on stderr.
- The tests exercise the copied production script rather than reproducing its predicate in
  Python, so they are neither tautological nor coupled to an implementation-only helper.

## Independent Validation

Reviewer ran:

```powershell
py -m pytest tests\unit\test_task_368c_run_frontend_vite_health_guard.py -q
```

Result: `3 passed in 1.24s`.

```powershell
py -m pytest tests\unit\test_task_368c_run_frontend_vite_health_guard.py tests\unit\test_packaging_notes.py -q
```

Result: `8 passed in 1.25s`.

```powershell
powershell.exe -NoProfile -Command '$null = [ScriptBlock]::Create((Get-Content ''scripts\run_frontend.ps1'' -Raw -Encoding UTF8))'
```

Result: exit code `0`.

Additional checks:

- `git diff --check` for base through required review HEAD: passed.
- `git show --check` for both implementation and evidence commits: passed.
- exact changed-path allowlist: passed; exactly three authorized paths.
- base ancestry, exact branch, exact required review HEAD: passed.
- pre-evidence working tree and index, including untracked files: clean.

## Conclusion And Handoff

- Conclusion: `reviewer_pass`
- Blocking findings: none
- Non-blocking findings: none
- Next role: permanent Integrator
- QA is not required: the bounded Windows PowerShell smoke independently covers all three
  authorized environment behaviors and no additional environment-specific gap was identified.
