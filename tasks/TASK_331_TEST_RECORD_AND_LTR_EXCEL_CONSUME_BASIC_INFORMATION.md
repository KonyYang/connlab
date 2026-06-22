# TASK_331_TEST_RECORD_AND_LTR_EXCEL_CONSUME_BASIC_INFORMATION

## Status

Complete.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed

TASK_330A established Project Basic Information authority data/API. TASK_330B added the Workbench Basic Information workflow. TASK_330C made Project Folder formal outputs consume the latest confirmed Basic Information snapshot. TASK_330D/E/F completed follow-up fixes and Basic Information usability improvements.

The user confirmed that the TASK_330 series is complete and requested the next controlled task so remaining file generation/synchronization paths consume the same confirmed Basic Information authority.

The user approved implementation after review revisions were applied.

Implementation completed on 2026-06-21.

## Plan

Detailed implementation plan:

- `docs/task_331_test_record_and_ltr_excel_consume_basic_information_plan.md`

## Goal

Make Test Record Word draft generation and post-registration LTR Excel metadata synchronization read the latest confirmed Project Basic Information snapshot.

## Core Behavior

1. Test Record Word draft generation reads latest confirmed Basic Information before writing.
2. Test Record generation blocks before document mutation when confirmed Basic Information is missing.
3. Test Record header metadata uses confirmed Basic Information values for DL/LTR number, product description, test item-related project identity, and applicable specifications where available.
4. Test Record download keeps returning `.docx` as `FileResponse`; Basic Information version/source-signature hash are returned through response headers.
5. LTR Excel metadata synchronization is a post-registration operation for an existing registered LTR row.
6. LTR sync preview reads latest registered local LTR and latest confirmed Basic Information.
7. LTR sync commit updates only the existing workbook row for that LTR number.
8. LTR sync commit validates Basic Information version/hash from preview before writing.
9. Initial LTR application/registration remains unchanged and does not require confirmed Basic Information.
10. Basic Information modeled fields are not silently filled from Project/ApplicationForm/LTR fallback values after confirmation.

## In Scope

- Add Basic Information reader dependency to ConfirmedMatrix Test Record Word generation service.
- Update Test Record header metadata construction to use confirmed Basic Information for modeled fields.
- Add Basic Information context fields to Test Record generation result and API response.
- Add post-registration LTR workbook Basic Information sync application service.
- Add typed LTR sync preview/commit API routes.
- Wire Basic Information snapshot reader into Test Record and LTR sync dependencies.
- Add unit and integration tests for Test Record and LTR sync behavior.
- Add regression coverage proving initial LTR workbook write remains independent of Basic Information confirmation.

## Out Of Scope

- No Report generation or Report header fill.
- No Basic Information UI changes.
- No Basic Information schema/API/persistence changes.
- No Basic Information source-provider additions from Matrix or Fee.
- No Project Folder Required forms behavior change.
- No initial LTR application flow rewrite.
- No LTR sync frontend preview/commit workflow, confirmation dialog, success feedback, or one-click orchestration.
- Workbench `Project Basic Information` may show a reserved `Update LTR` entry point gated by confirmed Basic Information; the actual click-to-preview/commit workflow belongs to a later TASK_332-style UI/orchestration task.
- No attachment of LTR sync to `Update project folder`; backend preview/commit only.
- No public-drive upload redesign.
- No StepInstance, test execution persistence, evidence/image management, AI review, permissions, LAN/server, or multi-user behavior.

## Acceptance Criteria

- Test Record generation blocks with `Confirm Basic Information before generating Test Record.` when no confirmed snapshot exists.
- Test Record header uses confirmed Basic Information values when a snapshot exists.
- Test Record generation API still returns the Word file and exposes confirmed Basic Information context through `X-ConnLab-Basic-Information-Version` and `X-ConnLab-Basic-Information-Source-Hash` headers.
- Test Record generation does not silently overwrite an existing target document unless a safe managed-output/fingerprint rule proves it is safe; otherwise it blocks or generates a unique draft file name.
- Existing ConfirmedMatrix authority gating remains unchanged.
- LTR Basic Information sync preview blocks without a registered local LTR.
- LTR Basic Information sync preview blocks without confirmed Basic Information.
- LTR Basic Information sync preview builds row data from confirmed Basic Information values without Project/ApplicationForm fallback for fields already modeled in Basic Information.
- LTR Basic Information sync preview locates the target row through workbook `find_ltr_number()` and does not use append-row estimation.
- LTR Basic Information sync commit rejects stale Basic Information context.
- LTR Basic Information sync commit updates an existing workbook row only.
- LTR Basic Information sync commit blocks when the existing workbook row is missing.
- Initial LTR workbook write/registration tests continue to pass without requiring confirmed Basic Information.

## Completion Notes

- Test Record Word generation now requires a latest confirmed Project Basic Information snapshot before document mutation.
- Test Record header metadata uses confirmed Basic Information for modeled fields, and the download endpoint remains a `.docx` `FileResponse` with `X-ConnLab-Basic-Information-Version` and `X-ConnLab-Basic-Information-Source-Hash` headers.
- Deterministic Test Record output no longer silently overwrites an existing target document; a unique draft filename is generated when the target path already exists.
- Added backend-only LTR workbook Basic Information sync preview/commit APIs.
- LTR sync preview/commit locate the existing workbook row through `find_ltr_number()` and never use append-row estimation for this workflow.
- Product-boundary follow-up records that the reserved `Update LTR` entry belongs in the Workbench `Project Basic Information` card, gated by confirmed Basic Information; TASK_331 still does not implement the frontend preview/commit workflow.
- Review follow-up changed LTR sync preview business blockers to typed `status="blocked"` preview responses with blockers, while missing registered LTR remains a not-found API error.
- Review follow-up added a read-only LTR workbook preview transaction that opens the workbook without creating lock files, backups, or saves.
- LTR sync commit validates Basic Information version/source-signature hash from preview before writing.
- Missing registered LTR is exposed as a not-found API response for the sync workflow; stale Basic Information context is a conflict.
- Initial LTR workbook registration/write paths remain independent of Basic Information confirmation.

## Validation

- `py -m pytest tests/unit/test_confirmed_matrix_test_record_document_generation_service.py tests/unit/test_test_record_document_gateway.py tests/integration/test_confirmed_matrix_test_record_generation_api.py -q` (`23 passed`)
- `py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py tests/unit/test_ltr_workbook_transaction_gateway.py -q` (`17 passed`)
- `py -m pytest tests/integration/test_ltr_workbook_write_commit_api.py tests/unit/test_ltr_workbook_write_commit_service.py -q` (covered during TASK_331 completion)
- `py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py tests/integration/test_api_default_dependencies.py -q` (`37 passed`)
- `py -m pytest tests/integration/test_api_default_dependencies.py -q` (`3 passed`)
- `cd frontend; npm test -- --run ProjectBasicInformation ProjectWorkbenchLayout --watch=false` (`44 passed`)
- `cd frontend; npm run build` passed
- `git diff --check` reported no whitespace errors, only CRLF conversion warnings

## Validation

Run:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_test_record_document_generation_service.py tests/unit/test_test_record_document_gateway.py tests/integration/test_confirmed_matrix_test_record_generation_api.py -q
py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py -q
py -m pytest tests/integration/test_ltr_workbook_write_commit_api.py tests/unit/test_ltr_workbook_write_commit_service.py -q
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
cd frontend; npm test -- --run ProjectBasicInformation ProjectWorkbenchLayout --watch=false
cd frontend; npm run build
git diff --check
```

## Stop Point

After implementing and validating TASK_331, update `docs/task_board.md` and stop. Do not proceed to Report generation, frontend LTR sync preview/commit workflow, Project Folder orchestration, StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope without a separately approved task.
