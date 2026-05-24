# TASK_042_LTR_READINESS_SERVICE_AND_API

## Status

done

## Goal

Implement LTR readiness evaluation before LTR preview or registration can proceed.

## Scope

- Use `backend/modules/ltr/ltr_field_catalog.py` as the authoritative field catalog.
- Evaluate confirmed project, application form, sample info, and supporting evidence fields.
- Return readiness fields with value/source/severity/state/operator action.
- Distinguish blocker, review-required, and placeholder-allowed fields.
- Add an application service and thin API route if needed by this task.
- Add tests for blockers, review-required fields, placeholder-allowed fields, and API smoke if an endpoint is added.

## Out Of Scope

- LTR number generation beyond using existing pure rules.
- LTR workbook write.
- LTR registration preview or commit.
- Folder evidence placement.
- Lifecycle guards beyond readiness evaluation.
- Frontend changes unless explicitly required.
- Matrix, Report, AI review, LAN deployment, permissions, or Outlook inbox auto-scan.

## Inputs

- `backend/modules/ltr/ltr_field_catalog.py`
- `backend/modules/ltr/ltr_number_rules.py`
- `backend/infrastructure/office/excel_workbook_gateway.py`
- Existing project/application form/sample/file asset repositories

## Outputs

- LTR readiness service/result DTOs.
- Thin API route only if required by task implementation.
- Tests for readiness blockers, review-required fields, placeholder policy, and route smoke if applicable.
- Task board update after completion.

## Acceptance Criteria

- Missing `BLOCKER` fields block preview/registration readiness.
- `REVIEW_REQUIRED` fields require manual confirmation or explicit policy.
- `PLACEHOLDER_ALLOWED` fields use explicit placeholder policy.
- Each field reports source, value/state, severity, and operator action.
- Route layer stays thin if an API is added.
- No workbook write, registration preview, local commit, or UI implementation is added.

## Validation

- Run focused readiness tests.
- Run related LTR/API tests if route or shared LTR modules are touched.
