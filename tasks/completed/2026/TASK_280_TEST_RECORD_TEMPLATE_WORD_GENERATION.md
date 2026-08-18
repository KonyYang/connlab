# TASK_280_TEST_RECORD_TEMPLATE_WORD_GENERATION

## Status

Status: closed (archived 2026-08-18; superseded by Sol-native manual task publishing; implementation not approved)

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Allowed Reason

TASK_279 is complete and the task board currently has no active implementation task. The user requested the next controlled task: Project Workbench `Test record` should generate a Word Test Record by filling the approved Word template from active Matrix authority, replacing the current manual operation.

## Objective

Enable the Project Workbench `Test record` action to generate a real Word Test Record document from the active ConfirmedMatrix using the approved template:

```text
D:\Source\Office Auto\TestDocument\Template\FDQF-E-036 Test Record Template-Even.docx
```

The generated document should follow the manual example shape:

```text
Group Number / Sample Quantity paragraph
Step table populated from Matrix group steps
Equipment table left blank for manual completion
repeat per selected Matrix group
```

This task replaces the manual step of copying the template and filling group/step rows from a Matrix workbook.

## User Reference Files

Template:

```text
D:\Source\Office Auto\TestDocument\Template\FDQF-E-036 Test Record Template-Even.docx
```

Matrix example:

```text
C:\Users\White\Desktop\AI information\Projects\DL-2025-11-073\matrix.xlsx
```

Historical generated output example:

```text
C:\Users\White\Desktop\AI information\Projects\DL-2025-11-073\DL-2025-11-073 Coolpower 3.40mm Pin Busbar To Socket Busbar Qualification Test\Submitted Material\DL-2025-11-073 Test Record.docx
```

## Observed Template Shape

The approved template currently contains:

- table 0: a 9-column step table with headers:
  - `Step`
  - `Test items`
  - `Test Method`
  - `Test conditions`
  - `Start Date/Time`
  - `Complete Date/Time`
  - `Equipment ID No.`
  - `Tested By`
  - `Remarks`
- table 1: a 7-column equipment table.

The historical output repeats the first two template tables for each selected group.

## Scope

### In Scope

1. Generate a Word `.docx` from active ConfirmedMatrix only.
2. Use the approved Word template as the source document layout.
3. Fill one group section per selected ConfirmedMatrix group.
4. Fill group paragraph:
   - group number
   - sample quantity expression
   - sample number placeholder derived from group label and sample quantity where possible.
5. Fill step table columns:
   - step sequence
   - test item
   - test method
   - test condition
   - remarks from requirement
6. Leave manual execution columns blank:
   - start date/time
   - complete date/time
   - equipment ID
   - tested by
7. Preserve the template's formatting as much as practical by cloning template paragraphs/tables instead of building a generic document from scratch.
8. Wire Project Workbench `Test record` button to generate and download the document.
9. Prefer saving generated output under the latest project folder `Submitted Material` when a project folder record exists.
10. Fall back to the controlled generated-output directory when no project folder record exists.
11. Add backend unit/integration tests and frontend button tests.

### Out Of Scope

Do not implement in TASK_280:

- page header/footer filling
- formal persisted `TestRecord` aggregate
- StepInstance or execution persistence
- image/evidence/test-data insertion
- report generation
- fee calculation
- equipment auto-fill
- template picker UI
- historical Test Record import as a template
- editing generated Word content inside ConnLab
- generating from Excel directly
- generating from frontend temporary Matrix editor state
- generating from unconfirmed ProjectMatrixDraft
- permissions, approval workflow, AI, or multi-user locking

## Architecture Decision

Generation source remains:

```text
Active ConfirmedMatrix -> ConfirmedMatrixTestRecordPreview -> Word template writer
```

The Excel file is reference material only. Runtime generation must not parse `matrix.xlsx`; it must consume the active ConfirmedMatrix already approved in ConnLab.

The Word writer belongs in infrastructure:

```text
api route -> application service -> infrastructure Office gateway
```

Frontend must call the API only. It must not manipulate Word, SQLite, or project folders directly.

## Expected Files

Backend:

- `backend/shared/config.py`
- `backend/application/confirmed_matrix_test_record_document_generation_service.py`
- `backend/infrastructure/office/test_record_document_gateway.py`
- `backend/api/routes_confirmed_matrix_test_record_generation.py`
- `backend/api/dependencies.py` if a folder repository dependency is needed

Frontend:

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/workbench.css` only if button state styling needs adjustment

Tests:

- `tests/unit/test_test_record_document_gateway.py`
- `tests/unit/test_confirmed_matrix_test_record_document_generation_service.py`
- `tests/integration/test_confirmed_matrix_test_record_generation_api.py`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`
- `tests/unit/test_frontend_shell_files.py`

Task tracking:

- `tasks/TASK_280_TEST_RECORD_TEMPLATE_WORD_GENERATION.md`
- `docs/task_280_test_record_template_word_generation_plan.md`
- `docs/task_board.md`
- `docs/task_plan_index.md`

## Acceptance Criteria

1. Project Workbench Matrix area shows an enabled `Test record` action when active ConfirmedMatrix preview is ready.
2. Clicking `Test record` calls the existing ConfirmedMatrix Test Record generation API and downloads a `.docx`.
3. The generated file is based on `FDQF-E-036 Test Record Template-Even.docx`.
4. The output contains one group section for every selected active ConfirmedMatrix group.
5. Each group section contains a group/sample paragraph.
6. Each group section contains a populated step table.
7. Step rows preserve Matrix step sequence order.
8. Step table fills test item, method, condition, and remarks from ConfirmedMatrix preview data.
9. Start date/time, complete date/time, equipment ID, and tested-by cells remain blank.
10. Equipment tables remain present and blank.
11. If a latest project folder exists, the generated file path targets `Submitted Material\<project_no> Test Record.docx`.
12. If no latest project folder exists, generation still returns a downloadable `.docx` from controlled generated output.
13. Output file strategy is fixed and deterministic in this task: if target file already exists, overwrite it.
14. No page header/footer field population is introduced.
15. No TestRecord aggregate, execution persistence, report, fee, image, evidence, permissions, AI, or multi-user scope is introduced.
16. Backend writer validation includes a real-template-structure test path and must not rely only on a minimal fallback template.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for execution.

Reason:

- The task is a bounded backend/frontend integration with existing ConfirmedMatrix preview data, API route, and Word gateway patterns.
- The main risk is OOXML/table cloning fidelity, which is manageable with focused unit tests against the provided template.
- The task should be implemented with `superpowers:executing-plans` rather than broad parallel development because Word document layout changes need careful serial verification.

## Validation Plan

Backend:

```powershell
py -m pytest tests\unit\test_test_record_document_gateway.py -q
py -m pytest tests\unit\test_confirmed_matrix_test_record_document_generation_service.py -q
py -m pytest tests\integration\test_confirmed_matrix_test_record_generation_api.py -q
```

Frontend:

```powershell
cd frontend
npm test -- --run ProjectWorkbenchMatrixProjectionPanel --watch=false
npm run build
```

Static guards:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task280 or task279 or project_workbench"
```

Smoke:

```text
Open Project Workbench -> confirm active Matrix exists -> click Test record -> downloaded .docx opens in Word -> document contains selected group sections and populated step rows.
```
