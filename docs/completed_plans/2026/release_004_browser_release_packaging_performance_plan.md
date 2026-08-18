# RELEASE_004 Browser Release Packaging Performance Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use
> `superpowers:test-driven-development` during the later authorized implementation pass.
> This plan is authorized for bounded static implementation only. It does not
> authorize release generation, staging, or commit.

**Goal:** Reduce desktop-only dependency collection in the Windows browser package and
print reliable elapsed time for each existing release-build step without changing
product or release-folder behavior.

**Architecture:** Keep the browser PyInstaller spec as the dependency boundary and use
PyInstaller's native recursive submodule filter plus explicit Analysis excludes. Keep
the PowerShell build script as the release orchestrator, adding only a primary-error-safe
timer around its five existing actions. Protect both contracts with static source tests;
actual package generation remains a separately approved future validation gate.

**Tech stack:** PyInstaller 6.x spec, Windows PowerShell, Python 3.11+, pytest static
contract tests.

## Current Phase And Permission

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled
  foundation.
- Current active board task: none.
- Accepted upstream: `TASK_366A_EXTERNAL_EXCEL_XLS_READ_COMPATIBILITY` at
  `2e8d7ddd2b7d08bff49987763cbdce66c0ebc4c6`.
- Repository HEAD audited by Developer planning-first:
  `add69823668d7ac4bf18645c688ce367a8fe0d42`.
- Reviewer B1 plan re-gate is passed and the user approved Developer planning-first.
- Developer docs-only planning-first is complete.
- Planner B2 source-of-truth reconciliation froze the native filter and timing
  contracts.
- Reviewer implementation-readiness re-gate passed.
- User explicitly approved product/package implementation.
- Developer implementation, Reviewer, QA, and Integrator static package gates passed.
  This lane is complete/accepted; generated-artifact/runtime validation remains a
  separately gated future option.

## Repository Facts

- Accepted HEAD uses
  `collect_submodules("backend") + ["backend.desktop.packaged_server"]` and no
  PyInstaller exclusions in the browser spec.
- The working-tree residual changes exactly three tracked candidates:
  - spec: 24 additions / 2 deletions
  - build script: 76 additions / 51 deletions
  - static test: 11 additions / 1 deletion
- The release plan is the fourth, untracked candidate. No candidate is staged.
- `backend.desktop.packaged_server` imports packaged static/runtime paths and the API;
  it does not import the desktop launcher, path picker, shell, or `webview`.
- Desktop-only paths are proven by source:
  - `backend.desktop.packaged_launcher` imports path picker and shell and imports
    `webview` at runtime.
  - `backend.desktop.path_picker_api` and `backend.desktop.shell` also load `webview`.
- Installed PyInstaller is 6.21.0. Its local signature is
  `collect_submodules(package, filter=..., on_error=...)`; the filter is applied before
  descending into a discovered subpackage. A post-collection list filter does not avoid
  that recursive discovery and is therefore not the final performance contract.
- The browser entry still supports the existing Fee export child flag. This lane must
  not exclude Office/Fee modules or alter that branch.

## Exact May Touch

Authorized static implementation may modify only:

1. `packaging/connlab_browser_server.spec`
2. `scripts/build_windows_browser_release.ps1`
3. `tests/unit/test_desktop_release_scripts.py`
4. `docs/release_004_browser_release_packaging_performance_plan.md`
5. This lane's Developer/Planner/Reviewer/reconciliation evidence and one board status
   hunk when the responsible governance role updates source of truth.

The three code/test files already contain mixed working-tree residuals owned by this
lane. A later pass must edit them hunk-by-hunk against accepted HEAD and must not rewrite
or stage unrelated files.

## Locked Paths And Behavior

- No backend/frontend product, API, schema, database, Office business gateway, Fee,
  parser, Contact Measurement Summary UI, Matrix, LTR, Settings, or project lifecycle
  change.
- No desktop release spec change.
- No dependency or `pyproject.toml` change.
- No real database, public-drive file, attachment, or source workbook access.
- No real release build, release-folder smoke, generated-output dependency probe, or
  HTTP smoke from generated output in planning, implementation-readiness, or the
  authorized static implementation gate.
- Do not create, inspect for dependency claims, modify, delete, stage, commit, or package
  any `dist_release/**` artifact in this lane.
- No stage, commit, push, residual cleanup, or absorption of TASK_364A/TASK_363D/Fee/
  parser/frontend residuals.

## Frozen Call And Data Flow

### Browser package dependency flow

1. PyInstaller loads `connlab_browser_server.spec` with `SPECPATH` at repository root.
2. Existing frontend-dist/icon guards run unchanged.
3. Existing datas include the built frontend and Fee seed JSON files unchanged.
4. `collect_submodules("backend", filter=is_browser_backend_submodule)` discovers
   backend modules while pruning the three desktop-only names/subtrees.
5. The predicate must reject only exact modules and subtrees using `name == prefix` or
   `name.startswith(f"{prefix}.")`. Naked `startswith(prefix)` or
   `startswith(tuple)` behavior is forbidden because it can reject unrelated sibling
   modules that merely share the same textual prefix.
6. `backend.desktop.packaged_server` remains an explicit hidden import if discovery did
   not already return it.
7. `Analysis.excludes` contains exactly the desktop runtime dependency roots
   `webview`, `PyQt5`, `pythonnet`, and `clr_loader`.
8. Existing EXE/COLLECT names, icon, console mode, data layout, UPX, and browser server
   entrypoint remain unchanged.

### Windows build flow

The existing five actions and ordering remain unchanged:

1. focused release tests unless `-SkipTests`
2. frontend build unless `-SkipFrontendBuild`
3. PyInstaller availability check
4. PyInstaller package construction
5. release-folder preparation

`Invoke-TimedStep` owns only elapsed-time reporting. It starts one Stopwatch, invokes
the supplied action once, and writes one `[time] <label>: <seconds>s` line from cleanup.
Therefore successful and failed steps both report elapsed time. The implementation must
preserve the original terminating error or explicit `$LASTEXITCODE` failure as the
primary error even if the timing/reporting cleanup itself fails.
Skipped steps preserve their existing skip message and do not emit a fabricated time.

The tests step retains `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and restores the caller's exact
prior environment value in `finally`. The frontend step retains `Push-Location` /
`Pop-Location`. Timing must not change release names, paths, cleanup, copy/move order,
frontend guards, command arguments, or success messages.

## Exact Future Implementation

### 1. Start with static red tests

Modify only the two existing browser-release nodes in
`tests/unit/test_desktop_release_scripts.py`:

- `test_browser_release_script_builds_web_folder_without_business_changes`
  - require `Invoke-TimedStep`, Stopwatch start/stop, cleanup/finally behavior, and
    `[time]`;
  - require static evidence that success and failure paths report elapsed time while
    the action/exit-code failure remains primary;
  - require all five labels to be wrapped;
  - retain all existing product/path/data-safety assertions.
- `test_browser_release_spec_uses_packaged_server_and_frontend_dist`
  - require native `filter=is_browser_backend_submodule` use;
  - reject direct broad concatenation and post-collection-only filtering;
  - require exact module/subtree comparison and a prefix-collision negative case;
  - require all three desktop module exclusions and all four Analysis exclusions;
  - retain packaged server, frontend, seed, icon, console, and release-name assertions.

Run only the static module and record the expected red assertions. Do not execute the
PowerShell build script or PyInstaller spec.

### 2. Implement the native spec filter

Use this exact responsibility split in `connlab_browser_server.spec`:

```python
BROWSER_EXCLUDED_BACKEND_PREFIXES = (
    "backend.desktop.packaged_launcher",
    "backend.desktop.path_picker_api",
    "backend.desktop.shell",
)


def is_browser_backend_submodule(name):
    return not any(
        name == prefix or name.startswith(f"{prefix}.")
        for prefix in BROWSER_EXCLUDED_BACKEND_PREFIXES
    )


hiddenimports = collect_submodules(
    "backend",
    filter=is_browser_backend_submodule,
)
if "backend.desktop.packaged_server" not in hiddenimports:
    hiddenimports.append("backend.desktop.packaged_server")
```

Keep the four `Analysis.excludes` entries from the candidate residual. Do not manually
enumerate the rest of backend, change `on_error`, or exclude general Office/Fee modules.
Do not use naked `name.startswith(prefix)` or `name.startswith(tuple)` for exclusion.

### 3. Implement primary-error-safe timing

Use one helper in `build_windows_browser_release.ps1`:

```powershell
function Invoke-TimedStep {
    param(
        [string]$Label,
        [scriptblock]$Action
    )
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $actionError = $null
    try {
        & $Action
    }
    catch {
        $actionError = $_
    }
    finally {
        try {
            $stopwatch.Stop()
            Write-Host ("[time] {0}: {1:n1}s" -f $Label, $stopwatch.Elapsed.TotalSeconds)
        }
        catch {
            if ($null -eq $actionError) {
                throw
            }
        }
    }
    if ($null -ne $actionError) {
        throw $actionError
    }
}
```

Wrap the same five candidate action blocks. Keep the candidate's tests-step environment
restoration. Do not add fast mode, parallel build, caching, output cleanup, or package
shape assertions to the script.

### 4. Green static validation

The authorized implementation gate may run only read/static checks:

```powershell
py -m pytest tests\unit\test_desktop_release_scripts.py -q
py -m py_compile packaging\connlab_browser_server.spec tests\unit\test_desktop_release_scripts.py
```

Parse the PowerShell source without invoking it:

```powershell
$tokens = $null
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile(
    (Resolve-Path "scripts\build_windows_browser_release.ps1"),
    [ref]$tokens,
    [ref]$errors
) | Out-Null
if ($errors.Count -ne 0) { throw ($errors | Out-String) }
```

Then run exact-path `git diff --check`, UTF-8 trailing-whitespace and physical-line
counts, candidate whitelist/forbidden-scope scan, and staging-empty check. Validation
must not execute either candidate packaging file.

## Line Budgets

Current UTF-8 physical counts including blank lines:

- `packaging/connlab_browser_server.spec`: 93
- `scripts/build_windows_browser_release.ps1`: 169
- `tests/unit/test_desktop_release_scripts.py`: 129
- this plan before Developer refinement: 177

Future limits:

- spec <= 120 lines
- build script <= 210 lines
- static test module <= 180 lines
- plan/evidence each <= 500 lines

No blank-line suppression or compressed formatting may be used to satisfy a limit.
If the static test node needs more room for prefix-collision and timing-failure cases,
split helper assertions inside the same test file rather than adding a new product path.

## Rollback And Failure Policy

- Static test, parse, compile, or scope failure blocks Reviewer routing. No generated
  package exists to clean up.
- Source rollback is the exact three-file residual hunk plus lane governance; do not
  revert any unrelated dirty file.
- If the native filter or Stopwatch contracts cannot be implemented within the exact
  candidate paths and line budgets, stop and route back to Planner/Reviewer rather than
  weakening the contract to post-collection filtering or success-only timing.
- A PyInstaller collection/exclusion regression cannot be declared absent from static
  evidence alone. Actual package viability and dependency removal remain residual risk
  until a separately authorized generated-artifact gate.
- If a future explicitly approved build fails, do not promote or describe the output as
  a release. Preserve the last accepted release and route the failure back to Developer;
  do not perform ad hoc `dist_release/**` cleanup.

## Separately Gated Future Package Validation

Only a later explicit user approval may authorize a real build, release-folder smoke,
generated dependency probe, or generated-output HTTP smoke. That gate must name a fresh
release identity, exact output root, cleanup/retention policy, expected package-shape
checks, HTTP port, and rollback owner before any command runs.

Until that gate occurs, do not claim measured build-speed improvement, reduced package
size, absent dependency folders, or runtime success. This lane can prove only the static
collection/exclusion/timing contracts.

## Package Isolation And Stop Point

- Exact product/test whitelist: the three candidate files above.
- Governance whitelist: this plan and this lane's evidence/status hunk only.
- External dirty files stay unstaged and unmodified.
- `dist_release/**` stays untouched and is not an input to validation claims.
- Stop after the authorized static Developer implementation pass and route Reviewer
  implementation gate. QA and Integrator routing remain unauthorized until that gate
  is reached.

## Developer Implementation Result

The authorized static-only pass adopted the native PyInstaller filter, exact
module/subtree predicate, explicit packaged-server retention, four Analysis excludes,
and primary-error-safe Stopwatch helper described above. Static tests execute only the
extracted filter and timer helpers; they do not execute the spec or build-script main
flow.

Validation recorded `8 passed`, clean Python compilation, clean PowerShell parser
output, and physical counts of spec 95, script 187, and test 179. No real release build
or generated-artifact validation was run. The next legal role is Reviewer implementation
gate; QA/Integrator and generated-output work remain locked.

## Integrator Static Closeout

Reviewer and QA passed the static-only gate. Integrator reran the focused static suite,
Python compilation, and PowerShell parser validation, then accepted the isolated local
package. No release script execution, PyInstaller invocation, generated-output probe,
HTTP smoke, or `dist_release/**` access occurred. Remote push was intentionally not
performed. A future generated-artifact/runtime gate still requires separate explicit
user approval and does not start from this closeout.
