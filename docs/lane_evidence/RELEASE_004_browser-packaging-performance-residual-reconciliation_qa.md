# RELEASE_004 QA Static Gate

Date: 2026-07-22

## Result

`qa_pass` for the authorized static-only gate.

This QA run did not invoke the release script, PyInstaller, frontend build, generated-output probe, or HTTP smoke. It did not access `dist_release/**`, real databases, public-drive paths, or user attachments.

## Scope and Package Boundary

Candidate product/test paths inspected:

- `packaging/connlab_browser_server.spec`
- `scripts/build_windows_browser_release.ps1`
- `tests/unit/test_desktop_release_scripts.py`
- `docs/release_004_browser_release_packaging_performance_plan.md`

`git diff --cached --name-only` for the candidate set was empty. The three tracked product/test paths are modified and the plan is untracked; no staging action was performed. Known external worktree residuals were not inspected, changed, or included.

The board currently reports no globally active task, while its active-execution model and the Reviewer callback explicitly authorize this Release 004 static QA gate. This governance mismatch was recorded only; `docs/task_board.md` was not changed by QA.

## Commands and Results

```powershell
py -m pytest tests\unit\test_desktop_release_scripts.py -q
py -m py_compile packaging\connlab_browser_server.spec tests\unit\test_desktop_release_scripts.py
[System.Management.Automation.Language.Parser]::ParseFile(...build_windows_browser_release.ps1...)
```

- Static release-script suite: `8 passed in 0.34s`.
- Python compile: passed with no output.
- PowerShell `Parser.ParseFile`: passed (`POWERSHELL_PARSE_OK`).

No release build command, release script execution, or generated-artifact verification was run.

## Static Assertions

- Native backend collection uses `collect_submodules("backend", filter=is_browser_backend_submodule)`.
- The filter uses the exact boundary `name == prefix or name.startswith(prefix + ".")`; the `backend.desktop.shellfish` prefix-collision negative is covered, and `backend.desktop.packaged_server` remains explicitly packaged.
- The four `Analysis` exclusions are present: `webview`, `PyQt5`, `pythonnet`, and `clr_loader`.
- `Invoke-TimedStep` has one `Stopwatch.StartNew()` invocation, invokes the action under `try`, stores the primary action exception, and stops/reports timing from `finally` without replacing the primary exception.
- Static count: five `Invoke-TimedStep` release actions, four `$LASTEXITCODE` guards, one Stopwatch creation, and no `Measure-Command` use.
- The release script retains static cleanup code as part of its approved release workflow. QA did not execute it.

## Hygiene and Limits

- `git diff --check` for the three tracked candidate paths: passed; only existing LF/CRLF normalization notices.
- Trailing-whitespace scan for all four candidate paths: no matches.
- Physical line counts: spec `81`, script `170`, test `149`, plan `261`; all within the approved budgets.
- No product/test/evidence content was staged. No real-data or generated-output path was accessed.

## Residual Risk

This static gate cannot establish release artifact completeness, startup behavior, bundle size, or measured performance. Those checks remain intentionally unperformed and require a separately authorized artifact/runtime gate.

## Handoff

Recommended next role: **Integrator packaging/readiness**. Integrator must preserve the candidate whitelist and keep external residuals isolated.
