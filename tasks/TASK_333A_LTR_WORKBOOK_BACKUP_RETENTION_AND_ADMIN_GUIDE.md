# TASK_333A_LTR_WORKBOOK_BACKUP_RETENTION_AND_ADMIN_GUIDE

## Status

Complete. Implemented and validated on 2026-06-22.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed For Planning

`TASK_333_WORKBENCH_UPDATE_LTR_BASIC_INFORMATION_SYNC` connected the Workbench `Update LTR` action to the existing public-drive LTR workbook sync workflow. Smoke testing confirmed the target workbook is updated, but also exposed an operational issue: every write transaction creates a permanent timestamped backup under the configured LTR workbook backup directory, such as `D:\ConnLabOps\ltr_backups`, and the directory can grow without a cleanup policy.

The user approved a three-layer direction:

1. Keep backups out of normal operator UI.
2. Keep exact backup paths available through API results and administrator recovery channels.
3. Document the backup location, naming, purpose, recovery process, and retention policy for developers or administrators.

This follow-up is a narrow operational hardening task for the backup lifecycle created by TASK_333 and the shared LTR workbook write transaction gateway.

## Plan

Detailed implementation plan:

- `docs/TASK_333A_LTR_WORKBOOK_BACKUP_RETENTION_AND_ADMIN_GUIDE_PLAN.md`

## Goal

Prevent the configured LTR workbook backup directory from growing indefinitely while preserving safe manual recovery and administrator traceability.

## Core Behavior

1. LTR workbook writes still create a pre-write backup before opening the workbook for modification.
2. Backup retention runs automatically after a successful workbook save.
3. Retention only deletes ConnLab-owned LTR workbook backup files that match the transaction gateway naming pattern for the same workbook.
4. Retention keeps a conservative recent history, with explicit defaults and configurable limits.
5. Normal Workbench UI no longer displays the local backup path after `Update LTR`; it displays business success copy instead.
6. API responses continue to carry the exact `backup_path` for administrator diagnostics.
7. A new administrator guide documents where backups are stored, why they exist, how to recover manually, and how retention works.

## In Scope

- LTR workbook transaction backup retention configuration.
- Retention logic in the shared LTR workbook transaction gateway.
- Unit tests covering retention count/age/ownership safety.
- Config loading tests for the new retention defaults and overrides.
- Workbench `Update LTR` success copy that hides the local absolute backup path from ordinary UI.
- Frontend test update for the success copy.
- Administrator documentation for LTR workbook backups and manual recovery.
- Task board update after implementation.

## Out Of Scope

- No removal of pre-write backups.
- No automatic rollback or automatic restore from backups.
- No UI for browsing, downloading, deleting, or restoring backups.
- No changes to public-drive workbook authority.
- No changes to initial LTR number allocation or LTR row mapping.
- No changes to Basic Information schema/API/persistence.
- No changes to Project Folder output generation.
- No Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.

## Acceptance Criteria

- A successful LTR workbook write still returns an exact `backup_path` through backend/API result objects.
- The Workbench `Update LTR` success message does not render the local absolute backup path.
- The LTR workbook backup directory is pruned automatically according to documented retention settings.
- Retention deletes only ConnLab-owned backups for the same workbook stem and suffix, never arbitrary files in the backup directory.
- Existing LTR workbook transaction, initial LTR commit, and Basic Information sync tests continue to pass.
- New tests prove retention keeps recent backups and removes older eligible backups.
- New administrator guide documents backup directory, naming, purpose, manual recovery, and cleanup policy.

## Validation

```powershell
py -m pytest tests/unit/test_ltr_workbook_transaction_gateway.py tests/unit/test_config.py -q
# 15 passed

py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py tests/unit/test_ltr_workbook_write_commit_service.py tests/integration/test_ltr_workbook_write_commit_api.py -q
# 29 passed

cd frontend; npm test -- --run ProjectBasicInformationSummaryCard --watch=false
# 8 passed

cd frontend; npm run build
# passed

git diff --check
# passed with CRLF conversion warnings only
```

## Review Result

Reviewed after implementation on 2026-06-22. No P1/P2 blocking issues were found. Residual risk is limited to best-effort backup pruning when old backup files are locked or unavailable; this does not block LTR workbook writes and is documented as an administrator/manual recovery concern.

## Stop Point

Stop after implementation, validation, and task board update. Do not proceed to another task without separate explicit approval.
