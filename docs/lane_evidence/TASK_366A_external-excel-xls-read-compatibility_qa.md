# TASK_366A QA Evidence - External Excel `.xls` Read Compatibility

**Date:** 2026-07-20
**Role:** QA / Smoke Owner
**Lane:** `external-excel-xls-read-compatibility`
**Result:** `qa_pass`

## Scope and Safety Boundary

- Validated only the TASK_366A candidate: legacy `.xls` read-only gateway, Office facade/lifecycle dispatch, external-resource and desktop picker wiring, and their focused tests.
- All pytest runs used disposable roots under `tmp/` through `--basetemp`.
- No real public-drive, LTR, or user workbook was opened. One real Excel COM smoke used a newly created disposable file under `tmp/task366a_realcom_5lsgkh12/`; it was deleted after verification.
- No product/test source, board, staging area, commit, or push was modified by QA.

## Validation Commands and Results

1. Focused TASK_366A fake-COM/lifecycle/resource/read/API/picker suite:

   ```powershell
   py -m pytest -p no:cacheprovider --basetemp=tmp\task_366a_qa_pytest `
     tests/unit/test_excel_com_readonly_tabular_gateway.py `
     tests/unit/test_external_resource_service.py `
     tests/unit/test_external_excel_read_service.py `
     tests/unit/test_desktop_path_picker_api.py `
     tests/integration/test_external_excel_read_api.py `
     tests/unit/test_excel_structure_probe.py `
     tests/unit/test_office_lifecycle.py -q
   ```

   Result: **63 passed** in 8.81s.

2. Existing XLSX/Office/LTR regression expansion:

   ```powershell
   py -m pytest -p no:cacheprovider --basetemp=tmp\task_366a_qa_xlsx_ltr `
     tests/unit/test_excel_structure_probe.py `
     tests/unit/test_office_integration_boundary.py `
     tests/unit/test_ltr_workbook_compatibility_service.py -q
   ```

   Result: **15 passed** in 1.71s.

3. Reviewer nine-module composition tail:

   ```powershell
   py -m pytest -p no:cacheprovider --basetemp=tmp\task_366a_qa_nine_module_tail `
     tests/unit/test_office_integration_boundary.py `
     tests/unit/test_ltr_workbook_compatibility_service.py -q
   ```

   Result: **11 passed** in 1.64s. Together with item 1, this reproduces the declared nine-module total of **74 passed**.

4. Compilation:

   ```powershell
   py -m py_compile backend/infrastructure/office/excel_com_readonly_tabular_gateway.py backend/infrastructure/office/office_facade.py backend/infrastructure/office/office_lifecycle.py backend/application/external_resource_service.py backend/desktop/path_picker_api.py
   ```

   Result: passed (no output).

## Behavior Coverage

- Focused fake-COM and API suites passed for `.xls` structure/read dispatch, lifecycle cleanup, picker/resource wiring, and HTTP error behavior. Existing `.xlsx` structure and LTR compatibility regressions also passed.
- Source audit confirms inclusive pre-read guards: `65_536` rows, `256` columns, and `1_000_000` cells.
- Source audit confirms the fallback classifier is exact: only exception type module `pywintypes` with type name `com_error` may retry `UsedRange.Value2`; no direct `pywin32` import was added. Arbitrary non-COM Value failures do not take that fallback; primary read failures remain authoritative over cleanup failures. The focused gateway suite covers these paths and exactly-once cleanup.
- `.xls` remains a read/structure-preview path; no write/create behavior was introduced in candidate production code. API-focused tests passed, including the expected user-facing rejected-input/HTTP 400 paths.

## Real COM Read-Only Smoke

`pywin32` and local Excel COM were available. QA created a disposable legacy workbook only:

- Temporary file: `D:\PythonProject\connlab\tmp\task366a_realcom_5lsgkh12\qa_legacy.xls`
- Setup data: sheet `Data`, headers `Record`, `Date`, one row `QA-001`, `2026-07-20`.
- `OfficeFacade.probe_excel_structure()` returned `valid=true`, matched `Data`.
- `OfficeFacade.read_excel_tabular_rows()` returned the expected row; Excel serial date was normalized to `2026-07-20T00:00:00+00:00`.
- SHA-256, size (`25088` bytes), and mtime were identical before and after the facade probe/read, demonstrating the product read path did not mutate the temporary `.xls`.
- Cleanup verified: the isolated temp root and workbook were removed after smoke (`ARTIFACT_CLEANED=True`).

## Candidate / Static Checks

- Candidate status is exactly nine tracked modifications plus the expected two new untracked files:
  - `backend/application/external_resource_service.py`
  - `backend/desktop/path_picker_api.py`
  - `backend/infrastructure/office/office_facade.py`
  - `backend/infrastructure/office/office_lifecycle.py`
  - `backend/infrastructure/office/excel_com_readonly_tabular_gateway.py` (new)
  - focused TASK_366A unit/integration tests, including `test_excel_com_readonly_tabular_gateway.py` (new)
- `git diff --check` for tracked candidate paths: pass; only existing LF/CRLF normalization notices.
- Candidate trailing-whitespace scan: no matches.
- Candidate direct-pywin32-import scan: no matches.
- Candidate real absolute-path/public-drive/data-DB scan: no matches.
- Locked existing `backend/infrastructure/office/excel_workbook_gateway.py` diff count: `0`; `data/` status count: `0`; staged candidate count: `0`.
- Physical-line maximum: gateway test `427`; gateway `366`; both under the 500-line hard limit.
- The worktree contains unrelated backend/frontend/release/governance residuals; they were not included in this QA candidate assessment.

## Residual / Handoff

- Non-blocking governance note: current task/plan header wording still refers to an earlier Developer-pending state, while the explicit Reviewer implementation re-gate routed this active TASK_366A lane to QA. QA did not alter the board or task documents. Integrator should reconcile only the status/evidence transition while keeping unrelated residuals excluded.

**QA gate: pass.** Recommend **Integrator packaging/readiness** for the isolated TASK_366A candidate.
