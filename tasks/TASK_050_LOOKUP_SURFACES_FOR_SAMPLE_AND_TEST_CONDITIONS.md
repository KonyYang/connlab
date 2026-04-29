# TASK_050_LOOKUP_SURFACES_FOR_SAMPLE_AND_TEST_CONDITIONS

## Status

done

## Goal

Provide quick lookup surfaces for sample information and testing condition/method text.

## Scope

- Add backend lookup behavior for project, sample, and testing summary data.
- Make sample information searchable by project, DL, part number, product name, or requestor where structured records exist.
- Expose testing condition/method summary from structured application form data.
- Keep lookup read-only.

## Out Of Scope

- Matrix, Test Record, Report, AI review, LAN deployment, permissions, or Outlook inbox auto-scan.
- Test execution or result ingestion.
- Report generation.
- Frontend changes unless explicitly required.

## Inputs

- Confirmed `Project`, `ApplicationForm`, `SampleInfo`, `LtrRecord`, and `FileAsset` records.
- Existing readiness and evidence data where useful.

## Outputs

- Lookup application service/API.
- Tests for sample lookup and testing summary behavior.
- Task board update after completion.

## Acceptance Criteria

- Sample info is searchable by project, DL, part number, product name, and requestor.
- Testing condition/method text is visible without opening Word.
- Lookup uses structured records, not raw Word/Excel as source of truth.
- No Matrix/test execution/report generation is implemented.

## Validation

- Run focused lookup tests.
- Run related project/intake/LTR tests.
