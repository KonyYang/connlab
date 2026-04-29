# TASK_043_LTR_REGISTRATION_PREVIEW

## Status

done

## Goal

Preview the next LTR number and target workbook/local registration data before any write or commit.

## Scope

- Use the readiness service from `TASK_042`.
- Use pure number rules from `backend/modules/ltr/ltr_number_rules.py`.
- Use workbook snapshot data where available, without writing to the workbook.
- Include existing local LTR records when calculating or checking proposed numbers.
- Return a preview object with proposed LTR number, source values, target context, readiness fields, conflicts, warnings, and snapshot fingerprint when available.
- Add a thin API route if needed by this task.
- Add tests for no-write preview behavior, duplicate/conflict detection, local-only mode, and stale/missing snapshot handling where applicable.

## Out Of Scope

- LTR local commit.
- Workbook write.
- Project folder rename or evidence placement.
- Lifecycle guards beyond preview prerequisites.
- Frontend changes unless explicitly required.
- Matrix, Report, AI review, LAN deployment, permissions, or Outlook inbox auto-scan.

## Inputs

- `backend/application/ltr_readiness_service.py`
- `backend/modules/ltr/ltr_number_rules.py`
- `backend/infrastructure/office/excel_workbook_gateway.py`
- Existing project/LTR repositories

## Outputs

- LTR registration preview service/result DTOs.
- Thin API route only if required by task implementation.
- Tests for preview number, conflicts, no-write behavior, and API smoke if an endpoint is added.
- Task board update after completion.

## Acceptance Criteria

- Preview performs no workbook write and no local registration commit.
- Preview can operate in `local_only` mode.
- Proposed DL number is deterministic from local/workbook snapshot sources available to the task.
- Duplicate local LTR and duplicate workbook DL are reported as conflicts.
- Readiness blockers prevent successful preview.
- Returned preview includes field mapping/readiness data needed for operator confirmation.
- API route stays thin if added.

## Validation

- Run focused preview tests.
- Run related LTR/readiness/API tests if route or shared LTR modules are touched.
