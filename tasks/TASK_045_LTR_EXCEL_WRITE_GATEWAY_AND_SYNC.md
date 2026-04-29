# TASK_045_LTR_EXCEL_WRITE_GATEWAY_AND_SYNC

## Status

done

## Goal

Optionally write an approved local LTR registration to the external LTR workbook through an infrastructure gateway, with explicit feature gating and password handling.

## Scope

- Keep workbook write disabled by default.
- Add settings for workbook path, mode, write enablement, backup location, and password.
- Open password-protected workbook through configurable settings or gateway input; do not hard-code the default password.
- Keep all Excel access behind `backend/infrastructure/office/`.
- Synchronize local record/workbook state only after a successful write path.
- Return actionable errors for missing path, disabled write mode, unsupported adapter, missing password, wrong password, lock/write failure, and stale preview/snapshot.
- Add tests that never write to the real workbook path.

## Out Of Scope

- Implementing Matrix, Report, AI review, LAN deployment, permissions, or Outlook inbox auto-scan.
- Frontend changes unless explicitly required.
- Folder evidence placement.
- LTR renumbering.
- Project folder rename.
- Writing to the real public workbook unless settings explicitly enable it and the active task implementation supports the adapter safely.

## Inputs

- `backend/application/ltr_local_commit_service.py`
- `backend/application/ltr_registration_preview_service.py`
- `backend/infrastructure/office/excel_workbook_gateway.py`
- `backend/shared/config.py`
- Existing project/LTR repositories

## Outputs

- Feature-gated workbook write/sync workflow.
- Infrastructure gateway behavior for supported workbook adapter(s), or explicit unsupported handling.
- Configurable password handling, with no hard-coded password in code/tests.
- Tests for disabled mode, password requirements, unsupported `.xls` handling, and no real workbook write.
- Task board update after completion.

## Acceptance Criteria

- Write path is disabled by default.
- No code or tests hard-code `DGLAB`; password comes from settings or explicit gateway input.
- Missing or wrong workbook password returns an actionable error and does not create misleading local state.
- Excel read/write remains behind infrastructure gateway classes only.
- Local LTR state is not marked as workbook-synced unless workbook write succeeds.
- Real workbook path is not hard-coded and is not written by tests.

## Validation

- Run focused workbook write/sync tests.
- Run related LTR local commit, preview, readiness, and API tests if shared paths are touched.
