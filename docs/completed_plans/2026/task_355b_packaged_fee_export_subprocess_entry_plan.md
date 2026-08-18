# TASK_355B Packaged Fee Export Subprocess Entry Plan

> Status: complete after user approval on 2026-07-07.

## Anti-Skip Status

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task on board: `TASK_355A_FEE_EVALUATION_TEMPLATE_FOLDER_SETTINGS_ALIGNMENT`, complete/accepted
- Why this plan is allowed now: the user requested a manual smoke test on the packaged browser release Fee Evaluation page. The smoke reproduced a release-only Fee Form generation error that is adjacent to, but distinct from, TASK_355A.

## Smoke Evidence

Manual browser smoke target:

```text
http://127.0.0.1:8765/projects/f4507aed538b422988e1a8c1ed71f0a1/fee-evaluation
```

Action:

```text
Click Fee Form
```

Observed page error:

```text
Child process did not emit one valid JSON object to stdout.
```

Browser console:

```text
No relevant browser-side error captured.
```

Running packaged process:

```text
D:\PythonProject\connlab\dist_release\ConnLab_Web_202607071755_v0.1.0\ConnLab_Server.exe
```

## Root Cause Hypothesis

`FeeEvaluationExportSubprocessRunner` starts the child export process with:

```python
[
    sys.executable,
    "-m",
    "backend.infrastructure.office.fee_evaluation_export_child",
    "--command-json",
    str(command_json.resolve()),
]
```

This works in source/dev because `sys.executable` is Python.

In the packaged release, `sys.executable` is `ConnLab_Server.exe`. The EXE entry point is `backend.desktop.packaged_server`, whose argparse contract accepts only server options such as `--host` and `--port`. It is not a Python interpreter and does not support `-m backend.infrastructure.office.fee_evaluation_export_child`.

The child therefore does not emit the expected JSON payload to stdout, so the parent reports:

```text
Child process did not emit one valid JSON object to stdout.
```

## Goal

Make packaged browser releases able to run the Fee Evaluation export child entry point and emit exactly one JSON object to stdout, while preserving the current source/dev `python -m ...` behavior.

## Scope

In scope:

- Packaged browser EXE child-mode argument routing.
- Fee Evaluation export subprocess command construction.
- Unit tests proving source mode still uses `-m` and packaged mode uses the EXE child flag.
- Focused manual/API smoke guidance for the packaged release.

Out of scope:

- No Fee pricing/default-fill rule changes.
- No workbook template changes.
- No Settings UI changes.
- No Excel COM gateway rewrite.
- No broad subprocess framework replacement.
- No LAN/server/multi-user/permissions changes.

## Design

### 1. Add a packaged child mode to `packaged_server.py`

Modify:

```text
backend/desktop/packaged_server.py
```

Add a reserved CLI mode, for example:

```text
ConnLab_Server.exe --connlab-fee-export-child --command-json <path>
```

Behavior:

- If `--connlab-fee-export-child` is present, call `backend.infrastructure.office.fee_evaluation_export_child.main(...)`.
- Pass through `--command-json <path>` to the existing child main.
- Do not start Uvicorn in child mode.
- Preserve normal server mode for existing `Start_ConnLab.bat`.

### 2. Make the runner choose packaged child argv

Modify:

```text
backend/infrastructure/office/fee_evaluation_export_subprocess_runner.py
```

Proposed behavior:

- In normal source/dev mode, keep current:

```text
python -m backend.infrastructure.office.fee_evaluation_export_child --command-json ...
```

- In PyInstaller packaged mode, use:

```text
ConnLab_Server.exe --connlab-fee-export-child --command-json ...
```

Detection:

```python
getattr(sys, "frozen", False)
```

### 3. Preserve stdout contract

The existing child entry point already emits exactly one JSON object through:

```text
backend.infrastructure.office.fee_evaluation_export_child._emit(...)
```

Do not add logging or print statements to child stdout.

### 4. Tests

Update:

```text
tests/unit/test_fee_evaluation_export_subprocess_runner.py
```

Required assertions:

- Source/dev `_child_command(command_json)` still includes `-m backend.infrastructure.office.fee_evaluation_export_child`.
- Packaged mode `_child_command(command_json)` uses `--connlab-fee-export-child --command-json <abs-path>` and does not include `-m`.

Add/update:

```text
tests/unit/test_desktop_packaged_server.py
```

Required assertions:

- Child-mode argv calls Fee export child main and does not start the web server.
- Normal argv still starts server path through the existing flow.

## Validation Commands

Focused tests:

```powershell
py -m pytest tests\unit\test_fee_evaluation_export_subprocess_runner.py tests\unit\test_desktop_packaged_server.py -q
```

Release packaging tests:

```powershell
py -m pytest tests\unit\test_desktop_packaged_runtime_paths.py tests\unit\test_desktop_packaged_static.py tests\unit\test_desktop_release_scripts.py -q
```

Manual packaged smoke:

1. Rebuild browser release after the fix.
2. Start the rebuilt `Start_ConnLab.bat`.
3. In Settings, set `Template folder` to the official template folder containing exactly one `*FDQF-E-176*.xls`.
4. Open the same Fee Evaluation page.
5. Click `Fee Form`.
6. Expected: no `Child process did not emit...` error; `.xls` download/generation succeeds or a business-readable Excel/template error is returned.

## Risks

- PyInstaller child-mode routing must avoid starting a second server.
- Child stdout must stay JSON-only; any diagnostic prints must go to stderr or parent-side logs.
- The current running release folder will not change until a new release build is produced.

## Approval Gate

Implementation was approved by the user with:

```text
同意按 TASK_355B 方案实施
```

Completion summary:

- Added PyInstaller packaged-mode child argv for Fee Evaluation export subprocesses:
  - source/dev: `python -m backend.infrastructure.office.fee_evaluation_export_child --command-json ...`
  - packaged: `ConnLab_Server.exe --connlab-fee-export-child --command-json ...`
- Added a reserved child mode to `backend.desktop.packaged_server` so the packaged EXE routes Fee export child requests to `fee_evaluation_export_child.main(...)` and does not start Uvicorn in child mode.
- Preserved normal `--host` / `--port` local web server mode.
- Added unit coverage for packaged child argv and packaged server child-mode routing.

Validation:

```text
py -m pytest tests\unit\test_fee_evaluation_export_subprocess_runner.py tests\unit\test_desktop_packaged_server.py -q
```

Result: `8 passed in 1.49s`.

```text
py -m pytest tests\unit\test_desktop_packaged_runtime_paths.py tests\unit\test_desktop_packaged_static.py tests\unit\test_desktop_release_scripts.py -q
```

Result: `12 passed in 0.62s`.

```text
py -m pytest tests\unit\test_fee_evaluation_export_subprocess_runner.py tests\unit\test_confirmed_matrix_fee_evaluation_export_timeout_service.py tests\integration\test_confirmed_matrix_fee_file_download_api.py -q
```

Result: `26 passed in 2.26s`.

Manual packaged smoke status:

- Code fix is implemented and covered by tests.
- The currently running release EXE at `dist_release\ConnLab_Web_202607071755_v0.1.0\ConnLab_Server.exe` will not include this change until the browser release is rebuilt and restarted.
