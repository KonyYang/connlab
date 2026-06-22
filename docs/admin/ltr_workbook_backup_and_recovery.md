# LTR Workbook Backup And Manual Recovery

## Purpose

ConnLab creates a pre-write backup before each write transaction to the configured
LTR registration workbook. The backup is for administrator diagnostics and manual
recovery. It is not an automatic rollback mechanism, and ConnLab does not restore
from these files by itself.

## Where Backups Are Stored

The backup directory is configured by the LTR workbook settings:

- Local config key: `[ltr_workbook].backup_dir`
- Environment variable: `CONNLAB_LTR_WORKBOOK_BACKUP_DIR`

A common workstation path is:

```text
D:\ConnLabOps\ltr_backups
```

Normal operator UI does not display this local path after a successful Workbench
`Update LTR` action. The API result still contains the exact `backup_path` for
support investigation, and administrators can also inspect the configured backup
directory directly.

## Naming Format

LTR workbook backups use the source workbook stem, a timestamp, and the original
suffix:

```text
{workbook_stem}_{YYYYMMDD_HHMMSS_microseconds}{workbook_suffix}
```

Example:

```text
LTR_updated_20260621_182640_619309.xlsx
```

Only files matching this ConnLab-owned pattern for the same workbook are eligible
for automatic retention cleanup.

## Retention Policy

ConnLab prunes old LTR workbook backups after a successful workbook save. Cleanup
does not run after failed writes.

Default settings:

```toml
[ltr_workbook]
backup_retention_count = 30
backup_retention_days = 30
backup_retention_max_mb = 500
```

Environment overrides:

```text
CONNLAB_LTR_WORKBOOK_BACKUP_RETENTION_COUNT
CONNLAB_LTR_WORKBOOK_BACKUP_RETENTION_DAYS
CONNLAB_LTR_WORKBOOK_BACKUP_RETENTION_MAX_MB
```

Retention behavior:

- Keeps the newest configured number of matching backups.
- Deletes older matching backups beyond that kept set.
- Applies the size cap to matching backups by deleting oldest eligible files.
- Never deletes the backup created by the current successful transaction.
- Never deletes unrelated files, different workbook names, different suffixes,
  directories, lock files, logs, or manually named recovery files.

## Manual Recovery Procedure

Use this only when an administrator has verified that the public-drive LTR workbook
must be restored from a pre-write backup.

1. Close Excel and pause ConnLab operations that may write to the LTR workbook.
2. Confirm the configured target workbook path in setup/configuration.
3. Copy the current target workbook to a separate emergency backup location.
4. Choose the ConnLab backup by timestamp from the configured backup directory.
5. Copy the chosen backup over the target workbook path.
6. Reopen ConnLab and verify the LTR row state before resuming operations.

Do not manually delete or replace the active public-drive workbook unless the
recovery action is intentional and coordinated.

