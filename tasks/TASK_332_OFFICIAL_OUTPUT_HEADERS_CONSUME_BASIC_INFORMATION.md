# TASK_332_OFFICIAL_OUTPUT_HEADERS_CONSUME_BASIC_INFORMATION

Status: complete, including review follow-up

Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

Plan: `docs/task_332_official_output_headers_consume_basic_information_plan.md`

## Summary

Make formal Project Folder outputs consistently consume the latest confirmed Project Basic Information snapshot for header/identity fields, while avoiding duplicate Office open/save cycles for the same file.

This task focuses on the outputs created or refreshed by Project Folder workflows:

- Fee Evaluation workbook header fields.
- Customer Feedback workbook header fields.
- Copied LTR Application Form Word write-back.
- Test Record Word header regression hardening.

TASK_330C already connected several paths to Basic Information, and TASK_331 connected Test Record to Basic Information. TASK_332 is the consolidation and hardening task: centralize the output identity payload, remove remaining silent fallback behavior for modeled Basic Information fields, fill the currently unsupported Customer Feedback identity fields, ensure Application Form write-back reads Basic Information first for modeled fields, and add tests proving each Office output writes header data in the same existing file session.

## Allowed Scope

- Backend application/infrastructure code for formal output identity/header mapping.
- Required Forms staging and Project Folder output generation paths.
- Fee Evaluation workbook generation tests and, if needed, minimal gateway mapping hardening.
- Customer Feedback workbook generation tests and gateway field mapping expansion.
- Project Application Form Word write-back mapping tests and, if needed, mapping hardening.
- Test Record generation tests proving Basic Information header consumption remains intact and no second write-back pass is introduced.
- Task board update after implementation.

## Out Of Scope

- Workbench UI changes.
- New frontend buttons or LTR sync workflow activation.
- Basic Information schema/API/persistence changes.
- Matrix/Fee Basic Information source provider changes.
- Report generation.
- StepInstance, execution persistence, evidence/image workflows, AI, permissions, LAN/server, or multi-user scope.
- Replacing all Office gateways with a new framework.
- Changing public-drive authority rules.

## Product Rules

- Formal outputs consume latest confirmed Project Basic Information for fields already modeled by Basic Information.
- For modeled fields, do not silently fall back to Project/ApplicationForm/LTR values after a confirmed Basic Information snapshot is required.
- Missing required output header fields should produce a clear blocker or warning according to output criticality, not mixed-source data.
- One output file should be opened once for its generation/update operation whenever practical:
  - Do not generate the body, close the Office file, reopen it, then write headers.
  - Write header/identity fields inside the same Excel/Word session used for the rest of that output.
- Managed-output fingerprint safety continues to apply. User-modified managed outputs must not be silently overwritten.

## Implementation Notes

- Reuse `backend/application/project_basic_information_output.py` as the formal-output snapshot boundary.
- Add a focused output identity mapper instead of duplicating field dictionaries across Fee, Customer Feedback, Application Form, and Test Record services.
- The mapper should return typed or named payloads for each output, not a generic unstructured grab bag.
- Existing output services should receive the mapped identity before they open Office files.
- Infrastructure gateways should write headers during their current open/save session.
- Use the user-provided reference files as manual reference only. Automated tests must not depend on files under `C:/Users/White/Desktop/...`.
  - During implementation, convert the observed layouts into minimal generated fixtures under `tests/fixtures/` or generate equivalent workbooks/documents inside tests.
  - The user-provided paths remain useful for manual smoke and mapping review, not CI/unit-test input.
  - Fee sample: `C:/Users/White/Desktop/AI information/Projects/DL-2025-11-073/DL-2025-11-073 Coolpower 3.40mm Pin Busbar To Socket Busbar Qualification Test/DL-2025-11-073 Form for Testing Fee Evaluation.xls`
  - Customer Feedback sample: `C:/Users/White/Desktop/AI information/Projects/DL-2025-11-073/DL-2025-11-073 Coolpower 3.40mm Pin Busbar To Socket Busbar Qualification Test/DL-2025-11-073 Customer Feedback Form.xlsx`
  - Application Form sample: `C:/Users/White/Desktop/AI information/Projects/DL-2025-11-073/DL-2025-11-073 Coolpower 3.40mm Pin Busbar To Socket Busbar Qualification Test/Submitted Material/Coolpower 3.40mm Busbar To Busbar qualification test  Request-20251111.docx`

## Acceptance Criteria

1. Fee Evaluation workbook generation writes DL/LTR number, product description, test item, requested by, location/Mfg. Site, and lab performing the tests from confirmed Basic Information in the same Excel COM session that writes Matrix/Fee rows.
2. Customer Feedback workbook generation writes all currently supported Basic Information identity fields, and the gateway no longer drops known fields such as phone, email, project leader, lab, received date, and estimated completion date when matching labels exist.
3. Copied Application Form Word write-back maps modeled fields from confirmed Basic Information first and does not silently overwrite them with ApplicationForm/Project values.
4. Test Record generation remains one-pass and continues to block without confirmed Basic Information when a reader is configured.
5. Required Forms generation reads one confirmed Basic Information snapshot context for preview/generate and continues stale-context validation.
6. Existing managed-output conflict/fingerprint behavior is preserved.
7. Tests cover Fee, Customer Feedback, Application Form, Test Record, and Required Forms orchestration behavior.
8. Tests use generated/minimal fixtures instead of user desktop sample files.

## Required Validation

Run at minimum:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_fee_evaluation_workbook_gateway.py -q
py -m pytest tests/unit/test_customer_feedback_form_generation_service.py tests/unit/test_customer_feedback_workbook_gateway.py -q
py -m pytest tests/unit/test_project_application_form_write_back_service.py -q
py -m pytest tests/unit/test_confirmed_matrix_test_record_document_generation_service.py tests/integration/test_confirmed_matrix_test_record_generation_api.py -q
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
```

If frontend files are not changed, frontend build/test is not required for TASK_332.

## Completion Notes

- Added a focused Project Basic Information output identity mapper for Fee Form, Customer Feedback, Application Form write-back, and Test Record header payloads.
- Required Forms staging now passes Fee/Customer Feedback identity payloads derived from the same confirmed Basic Information snapshot used by the output context.
- Customer Feedback workbook header filling now supports sample-compatible label/offset rules, including merged/annotated label text such as `Project Details`, `Work Request No.`, `From Date`, `Site`, and `GES Team`.
- Application Form Word write-back now uses modeled confirmed Basic Information fields without silently falling back to Project/ApplicationForm values for those modeled fields.
- Fee Form workbook regression coverage now verifies the Basic Information identity is written during the existing Excel session instead of a second open/save pass.
- Test Record Basic Information header behavior remains covered through the existing confirmed-matrix document generation and API regression tests.
- Review follow-up fixed the Customer Feedback Required Forms chain so staging passes raw confirmed Basic Information values into the Customer Feedback service, preventing double-mapping and lost workbook headers.
- Review follow-up added `location` to Customer Feedback identity so the sample-compatible `Site` header can be filled from confirmed Basic Information.
- Smoke follow-up fixed Fee Form header placement: the gateway now finds existing template labels (`LTR Number`, `Requestor`, `Test Description`, `Site`) and writes only the value into the cell to the right, instead of writing combined `Label: value` text into fixed cells.

Validation:

```powershell
py -m pytest tests/unit/test_project_basic_information_output_identity.py tests/unit/test_required_forms_staging_generator.py tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_fee_evaluation_workbook_gateway.py tests/unit/test_customer_feedback_form_generation_service.py tests/unit/test_customer_feedback_workbook_gateway.py tests/unit/test_project_application_form_write_back_service.py tests/unit/test_confirmed_matrix_test_record_document_generation_service.py tests/integration/test_confirmed_matrix_test_record_generation_api.py tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
```

Result: `100 passed`.

Additional Fee Form smoke hotfix validation:

```powershell
py -m pytest tests/unit/test_fee_evaluation_workbook_gateway.py -q
```

Result: `11 passed`.

## Stop Point

After this task is implemented and verified, update `docs/task_board.md` and stop. Do not begin Report generation, LTR sync UI, or Project Folder one-click orchestration follow-up without separate explicit approval.
