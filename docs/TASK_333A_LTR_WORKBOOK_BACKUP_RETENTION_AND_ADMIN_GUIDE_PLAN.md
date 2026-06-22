# TASK_333A LTR Workbook Backup Retention And Admin Guide Plan

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Current Active Task

`TASK_333_WORKBENCH_UPDATE_LTR_BASIC_INFORMATION_SYNC` is complete. `docs/task_board.md` currently requires stopping and waiting for a separate explicitly approved next task.

This `TASK_333A_LTR_WORKBOOK_BACKUP_RETENTION_AND_ADMIN_GUIDE` plan is a narrow follow-up requested by the user after TASK_333 smoke testing. The user approved implementation on 2026-06-22.

## Difficulty Assessment

This is not a one-line UI fix.

The change touches:

- backend LTR workbook transaction infrastructure;
- runtime configuration defaults and overrides;
- frontend success copy for the Workbench `Update LTR` flow;
- administrator documentation for recovery and cleanup.

The implementation is still small and well-bounded because the right backend insertion point already exists: `backend/infrastructure/office/ltr_workbook_transaction_gateway.py`.

## Goal

Keep LTR workbook backups useful for manual recovery and administrator tracing, while preventing `D:\ConnLabOps\ltr_backups` or any configured backup directory from growing indefinitely.

## Existing Behavior

### Backup Creation

`backend/infrastructure/office/ltr_workbook_transaction_gateway.py` creates a pre-write backup in `_backup_workbook()`:

```text
{backup_dir}\{workbook_stem}_{YYYYMMDD_HHMMSS_microseconds}{workbook_suffix}
```

Example:

```text
D:\ConnLabOps\ltr_backups\LTR_updated_20260621_182640_619309.xlsx
```

The backup is created before COM opens the workbook for writing. The transaction context exposes `backup_path`, and both initial LTR workbook commits and Workbench Basic Information sync commits can return it.

### Current Gaps

- No automatic cleanup exists.
- Backups accumulate permanently.
- Workbench `Update LTR` currently displays the local backup path in normal operator UI.
- There is no administrator guide explaining backup purpose, location, naming, recovery, or cleanup.
- The current backup is for manual recovery/diagnostics, not automatic rollback.

## Product Decision

Use a three-layer model:

1. **Operator UI** hides local filesystem backup paths and shows business success text.
2. **Backend/API result objects** keep the exact `backup_path` for administrator diagnostics.
3. **Administrator documentation** explains where backups live, how to recover manually, and how retention prunes old files.

This keeps the daily UI quiet for non-programmer operators while preserving traceability for support and recovery.

## Proposed Retention Rules

Add retention settings to `LtrWorkbookSettings` and `LtrWorkbookTransactionConfig`:

```python
backup_retention_count: int = 30
backup_retention_days: int = 30
backup_retention_max_mb: int = 500
```

Default policy:

- Keep at least the newest `backup_retention_count` ConnLab-owned backups for the same workbook.
- Delete eligible backups older than `backup_retention_days` when they are beyond the kept newest set.
- If the matching backup set still exceeds `backup_retention_max_mb`, delete oldest eligible backups until it is under the cap, while preserving the newest kept set.

Safety policy:

- Only inspect files in the configured `backup_dir`.
- Only delete files matching the same workbook stem and suffix pattern:
  - `{workbook_path.stem}_YYYYMMDD_HHMMSS_microseconds{workbook_path.suffix}`
- Never delete the backup created by the current transaction.
- Never delete files with non-matching names, different suffixes, directories, lock files, logs, or manually named recovery files.
- If cleanup fails for one old file, do not fail the workbook write after the backup has already succeeded. Record/log the cleanup failure if logging is available, and keep the write result successful. This avoids turning cleanup into a new write blocker.

## Configuration Design

Modify `backend/shared/config.py`.

Extend `LtrWorkbookSettings`:

```python
backup_retention_count: int = 30
backup_retention_days: int = 30
backup_retention_max_mb: int = 500
```

Load from local config and environment:

```text
[ltr_workbook]
backup_retention_count = 30
backup_retention_days = 30
backup_retention_max_mb = 500
```

```text
CONNLAB_LTR_WORKBOOK_BACKUP_RETENTION_COUNT
CONNLAB_LTR_WORKBOOK_BACKUP_RETENTION_DAYS
CONNLAB_LTR_WORKBOOK_BACKUP_RETENTION_MAX_MB
```

Use existing positive integer parsing style. Retention values must be positive. If the repository has existing config validation tests, extend those tests rather than adding a separate parser path.

Pass settings through `backend/api/dependencies.py` when constructing `LtrWorkbookTransactionConfig` for:

- `get_ltr_workbook_write_commit_service`
- `get_ltr_workbook_basic_information_sync_service`

## Backend Infrastructure Design

Modify `backend/infrastructure/office/ltr_workbook_transaction_gateway.py`.

Extend `LtrWorkbookTransactionConfig`:

```python
backup_retention_count: int = 30
backup_retention_days: int = 30
backup_retention_max_mb: int = 500
```

After `transaction.session.save()` succeeds, run:

```python
_prune_workbook_backups(
    workbook_path=workbook_path,
    config=config,
    current_backup_path=backup_path,
)
```

Suggested helper responsibilities:

- `_list_owned_workbook_backups(...) -> list[BackupCandidate]`
- `_parse_backup_timestamp(...) -> datetime | None`
- `_prune_workbook_backups(...) -> None`

`BackupCandidate` can be a small frozen dataclass with path, created_at, and size.

The helper should use structured filename parsing, not broad glob deletion. A regex is acceptable because this is a filename pattern with fixed timestamp format:

```text
^{re.escape(stem)}_(\d{8}_\d{6}_\d{6}){re.escape(suffix)}$
```

## UI Design

Modify `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx`.

Current success copy:

```tsx
LTR workbook updated: {result.sheet_name} row {result.row_number}.
Backup: {result.backup_path}
```

Proposed normal operator copy:

```text
LTR workbook updated: {sheet} row {row}. Backup retained automatically.
```

Do not show the full local backup path in the card. The exact path remains in API data for administrator use.

This follows ConnLab product guidance: user-facing UI should be operational and business-readable, and should not require normal operators to understand local infrastructure paths.

## Administrator Documentation

Add:

```text
docs/admin/ltr_workbook_backup_and_recovery.md
```

Contents:

- What LTR workbook backups are.
- Default/configured backup directory, including the common local example `D:\ConnLabOps\ltr_backups`.
- Backup naming format.
- Trigger timing: before each write transaction to the configured LTR workbook.
- Scope: manual recovery/diagnostics only, not automatic rollback.
- How to find the backup path:
  - backend/API result payload during troubleshooting;
  - logs or operation records if available;
  - backup directory sorted by timestamp.
- Manual recovery procedure:
  1. Close Excel and ConnLab operations using the workbook.
  2. Confirm the target workbook path.
  3. Copy the current target workbook to a separate emergency backup.
  4. Copy the selected ConnLab backup over the target workbook.
  5. Reopen ConnLab and verify LTR workbook compatibility/row state.
- Retention policy and why old backups are cleaned automatically.
- Warning that operators should not manually delete active public-drive workbook files.

## Tests

### Backend Unit Tests

Update `tests/unit/test_ltr_workbook_transaction_gateway.py`:

- backup creation still works;
- retention keeps the newest configured count;
- retention deletes only matching same-workbook backup files;
- retention does not delete current backup;
- retention ignores unrelated files and other workbook stems/suffixes;
- read-only preview still creates no lock, no backup, and no cleanup side effect.

Update `tests/unit/test_config.py`:

- defaults are loaded;
- local config overrides retention values;
- env vars override retention values;
- invalid non-positive retention values are rejected.

### Frontend Tests

Update `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.test.tsx`:

- success state shows `Backup retained automatically`;
- success state does not render the absolute `backup_path`.

## Risks

- If retention is too aggressive, manual recovery history may be shorter than expected. Use conservative defaults.
- If cleanup is implemented with broad globbing, it could delete unrelated files. Avoid broad glob deletion and match only the exact generated backup filename pattern.
- If cleanup errors fail the write transaction after the write succeeds, the operator may see confusing failures. Cleanup failures should not block the workbook write after backup creation succeeds.
- If UI removes the path without documentation, administrators lose discoverability. Add the admin guide in the same task.

## Scope Boundaries

This task does not implement:

- automatic rollback;
- backup restore UI;
- backup browser UI;
- backup compression;
- public-drive workbook versioning integration;
- LTR row mapping changes;
- Basic Information schema/API/persistence changes;
- report generation;
- StepInstance or execution persistence.

## Validation

Completed on 2026-06-22:

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

Reviewed after implementation on 2026-06-22. `TASK_333A_LTR_WORKBOOK_BACKUP_RETENTION_AND_ADMIN_GUIDE` is complete and accepted with no P1/P2 blocking findings. The implementation keeps backend/API backup traceability, hides local backup paths from normal operator UI, prunes ConnLab-owned backups using documented retention settings, and provides the administrator recovery guide.

## Stop Point

Implementation and validation are complete. Stop here and wait for separate explicit approval before starting another task.
