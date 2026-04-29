# TASK_039_LTR_FIELD_CATALOG_AND_READINESS_SOURCE_MAP

## Status

done

## Goal

Define the authoritative Phase 7 LTR readiness field catalog before building readiness services, preview, or workbook integration.

## Scope

- Define the 19 LTR readiness fields from the Phase 7 source image/list.
- Map each field to confirmed ConnLab data sources where available.
- Define fallback/manual confirmation policy for each field.
- Define severity for each field:
  - `BLOCKER`
  - `REVIEW_REQUIRED`
  - `PLACEHOLDER_ALLOWED`
- Define placeholder policy for future-result or not-yet-knowable fields.
- Add focused tests for the field catalog.
- Add or update documentation for the field mapping.

## Out Of Scope

- LTR number generation rules.
- LTR workbook read/write.
- LTR readiness API/service implementation.
- LTR registration preview or commit.
- Folder evidence placement.
- Lifecycle guards.
- Frontend changes unless explicitly required by this task.
- Matrix, Report, AI review, LAN deployment, permissions, or Outlook inbox auto-scan.

## Inputs

- `docs/ConnLab_Phase7_Real_LTR_Folder_Lifecycle_Plan.md`
- `docs/phase7_real_sample_baseline.md`
- Confirmed `Project`, `ApplicationForm`, `SampleInfo`, `IntakeAsset`, and `FileAsset` fields.
- Existing `backend/modules/ltr/` package.

## Outputs

- LTR field catalog module.
- Field source, fallback, severity, placeholder policy, and operator action mapping.
- Documentation for the 19-field source map.
- Focused tests.
- Task board update after completion.

## Acceptance Criteria

- Each of the 19 fields has:
  - canonical field key
  - display label
  - source path
  - fallback/manual policy
  - severity
  - placeholder policy where applicable
- Future-result fields such as Test Result and Failed item use explicit placeholder policy instead of accidental blocking.
- The catalog is pure Python and does not import Excel, SQLite, FastAPI, Office, or settings.
- No downstream readiness service, number rule, workbook, or UI behavior is implemented.

## Validation

- Run focused LTR field catalog tests.
- Run related LTR tests if shared LTR modules are touched.
