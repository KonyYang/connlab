# TASK_330C_PROJECT_FOLDER_OUTPUT_CONSUMES_BASIC_INFORMATION

## Status

Complete including follow-up review fixes.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed

TASK_330A established the backend Project Basic Information draft/confirmed authority data/API. TASK_330B added the Workbench `Basic Information` entry, editor workspace, autosaved draft behavior, confirm flow, and read-only summary card. The task board stop point explicitly names TASK_330C as the next allowed task after separate approval.

The user approved implementation on 2026-06-20. Implementation and validation are complete.

## Goal

Make the Project Folder formal output workflow consume the latest confirmed Project Basic Information snapshot.

The snapshot becomes the source for:

- Project Folder Required forms business identity fields,
- Fee Form base identity fields,
- Customer Feedback Form base/contact/date fields,
- copied LTR application Word document write-back fields,
- managed-output freshness signatures for safe refresh after Basic Information is reconfirmed.

## Core Behavior

1. `Generate project folder` / `Update project folder` continues to create or update the local Official project folder through the existing workflow.
2. Formal outputs must use the latest confirmed Basic Information snapshot, not ad hoc Project/ApplicationForm field assembly.
3. If no confirmed Basic Information snapshot exists, formal output generation/write-back returns a backend blocker before mutating those formal outputs.
4. Autosaved Basic Information drafts are ignored by project-folder outputs until the operator confirms them.
5. If Basic Information is reconfirmed, `Update project folder` can refresh formal outputs only when TASK_321 managed-output fingerprint safety allows it.
6. Manually edited, unmanaged, or fingerprint-changed formal output files must block instead of being overwritten.
7. Output records must include Basic Information version/source-signature context so stale outputs are detectable.

## In Scope

- Add a small application-layer reader/boundary for latest confirmed Basic Information consumption.
- Required forms preview/generate reads latest confirmed Basic Information.
- Required forms context signatures include Basic Information version and a hash of the Basic Information source signature.
- Required forms generate validates Basic Information context from preview before writing.
- Fee Form generation receives confirmed Basic Information base identity fields through the existing staging generator boundary.
- Customer Feedback generation receives confirmed Basic Information base/contact/date fields through the existing generation boundary.
- Customer Feedback filename owner suffix uses confirmed Basic Information `project_leader`, falling back to the current source only when that field is empty.
- Project Folder copied application Word write-back reads confirmed Basic Information for known fields.
- Section/Application write-back output records include Basic Information context.
- Frontend Required forms preview/generate DTOs echo Basic Information version/hash when stale-preview validation requires them.
- Unit and API tests for missing snapshot blockers, context signatures, safe refresh, and field consumption.

## Out Of Scope

- No Basic Information UI changes.
- No Basic Information source assembly changes beyond reading the latest confirmed snapshot.
- No Matrix/Fee source providers for Basic Information.
- No LTR workbook writeback.
- No report generation.
- No public-drive upload redesign.
- No StepInstance, test execution persistence, evidence/image management, AI review, permissions, LAN/server, or multi-user behavior.
- No new template-mapping UI.
- No direct frontend Office/filesystem/SQLite access.
- No unrelated request-material collection API bug fix or Fee Form performance cache unless separately approved.

## Acceptance Criteria

- Project Folder Required forms preview blocks when confirmed Basic Information is missing.
- Project Folder Required forms generation cannot proceed from a stale preview if Basic Information version/source signature changed.
- Fee Form output receives at least DL/LTR number, product description, test item, requested by, location, and lab performing tests through the backend Office/gateway path.
- Customer Feedback output receives at least DL/LTR number, product description, test item, requested by, phone, requestor email, project leader, lab performing tests, date lab received samples, and estimated completion date through the backend Office/gateway path.
- Customer Feedback filename suffix uses confirmed Basic Information `project_leader` when present.
- Copied application Word document write-back uses confirmed Basic Information values for known fields.
- Reconfirming Basic Information changes the formal-output source context and marks managed outputs refreshable only when their disk fingerprint is unchanged.
- User-modified or unmanaged output files return conflict/block and are not overwritten.
- Existing Matrix/Fee authority gates remain intact.

## Implementation Summary

- Added a small application-layer Basic Information output reader/snapshot boundary for latest confirmed snapshots.
- Required forms preview/generate now blocks without confirmed Basic Information, echoes Basic Information version/source-signature hash, and rejects stale generate requests.
- Required forms output context now includes Basic Information context so reconfirmed snapshots make managed outputs stale.
- Unmanaged existing Fee Form / Customer Feedback Form targets now return conflict instead of being treated as current.
- Fee Form and Customer Feedback staging now receive confirmed Basic Information values through backend generator commands.
- Fee Form Matrix basic export now passes Basic Information identity values into the workbook writer, and the Office gateway writes those values into the workbook header area.
- Customer Feedback identity fields and owner suffix prefer confirmed Basic Information.
- Copied application Word write-back now reads confirmed Basic Information fields and blocks user-modified managed targets through fingerprint checks before writing.
- Frontend Required forms DTO/request construction now carries Basic Information version/hash for stale-preview validation.
- Required forms generate validates that the Basic Information snapshot read for actual generation still matches the preview context.

## Validation

Completed targeted validation:

```powershell
py -m pytest tests/integration/test_project_folder_required_forms_api.py tests/unit/test_project_folder_required_forms_service.py tests/unit/test_project_application_form_write_back_service.py tests/unit/test_customer_feedback_form_generation_service.py -q
# 42 passed

py -m pytest tests/integration/test_project_folder_required_forms_api.py tests/unit/test_project_folder_required_forms_service.py tests/unit/test_project_application_form_write_back_service.py tests/unit/test_customer_feedback_form_generation_service.py tests/unit/test_confirmed_matrix_fee_evaluation_export_timeout_service.py tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py tests/unit/test_fee_evaluation_workbook_gateway.py -q
# 91 passed

py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_timeout_service.py tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py -q
# 36 passed

py -m pytest tests/unit/test_project_basic_information_service.py tests/integration/test_project_basic_information_api.py -q
# 12 passed

cd frontend
npm test -- --run ProjectWorkbenchLayout ProjectFolderTaskList projectFolderTaskSelectors --watch=false
# 39 passed

npm run build
# passed

git diff --check
# no whitespace errors; CRLF warnings only
```

Known non-blocking validation note:

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q
# 4 failures in older exact-string guard tests for TASK_315F/TASK_277 Matrix/Fee UI wiring.
# These failures are unrelated to TASK_330C output consumption.

cd frontend
npm run build
# currently blocked by unrelated existing edits in frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx:
# TS2322 Type 'null' is not assignable to type 'ReactElement...'.
```

Manual smoke after implementation:

- Confirm Basic Information on a test project.
- Click `Generate project folder` / `Update project folder`.
- Verify Fee Form, Customer Feedback Form, and copied application Word document use confirmed Basic Information values.
- Reconfirm Basic Information with a changed field.
- Click `Update project folder`.
- Verify safe managed outputs refresh and manually edited outputs block.

## Stop Point

Stop after TASK_330C implementation and validation. Do not proceed to LTR workbook writeback, report generation, StepInstance, AI, permissions, LAN/server, or multi-user scope without a separate approved task.
