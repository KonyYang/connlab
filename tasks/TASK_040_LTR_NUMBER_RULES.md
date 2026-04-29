# TASK_040_LTR_NUMBER_RULES

## Status

done

## Goal

Implement pure deterministic LTR number parsing, validation, formatting, and monthly sequence rules before any workbook snapshot or registration preview work.

## Scope

- Support standard DL format: `DL-{YYYY}-{MM}-{NNN}`, for example `DL-2026-04-001`.
- Support W-prefix format such as `W123`.
- Support suffix format such as `DL-2026-04-001ABC`.
- Parse LTR number components into structured pure Python values.
- Validate invalid values with actionable errors.
- Calculate the next monthly sequence from existing local/workbook number strings passed as plain input data.
- Add focused unit tests.

## Out Of Scope

- LTR workbook read/write.
- LTR readiness service or API.
- LTR registration preview or commit.
- Folder evidence placement.
- Lifecycle guards.
- Frontend changes.
- Matrix, Report, AI review, LAN deployment, permissions, or Outlook inbox auto-scan.

## Inputs

- `backend/application/ltr_service.py`
- `backend/modules/ltr/ltr_field_catalog.py`
- Existing LTR API/repository tests
- Required formats from Phase 7 plan

## Outputs

- Pure LTR number rules module under `backend/modules/ltr/`.
- Unit tests for standard, W-prefix, suffix, invalid formats, and sequence generation.
- Task board update after completion.

## Acceptance Criteria

- `DL-2026-04-001` is valid base format.
- `W123` is valid W-prefix input.
- `DL-2026-04-001ABC` is valid suffix format.
- Current month sequence increments from existing base DL values only.
- Invalid values return actionable errors.
- Pure rules do not import Excel, SQLite, FastAPI, Office, application services, or settings.

## Validation

- Run focused LTR number rule tests.
- Run related LTR tests if shared LTR modules are touched.
