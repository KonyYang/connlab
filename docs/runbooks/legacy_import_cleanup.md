# Approved legacy-import copy cleanup

This is a local, one-time operator tool for the User-approved nine duplicate folders and
one missing-folder registration under `D:\ConnLabProjectsDev`. It adds no UI, API, database
migration or application startup path. The command-line prepare entry checks the exact live
root/database and the fixed full member/project identifiers. The Python seam accepts a bounded
fixture authorization only for isolated verification.

## Exact boundary

Recycle only `DL-2026-04-003`, `009`, `011`, `012`, `013`, `018`, `031`, `033` and
`DL-2026-05-001`, after verified backups and association removal. The additional registration
`DL-2026-05-001 Coolpower HD3.5MM CTC qulificaition test` has no physical directory.

Do not change originals, `DL-2024-12-050`, `DL-2025-02-054`, `DL-2026-01-072`,
`DL-2026-11-003`, `DL-2026-11-013`, `DL-2026-11-013 [56cdd25d]`, the root itself,
root configuration or Materials library settings. Never select by project number alone.

## Prepare, review and execute

Run with `C:\PythonEnvs\connlab\.venv\Scripts\python.exe`, UTF-8 enabled, from the
reviewed checkout. Use a unique persistent run directory under `D:\ConnLabCleanupBackups`,
not `tmp`, a source tree or the material/project root.

```powershell
$env:PYTHONUTF8 = '1'
python scripts/legacy_import_cleanup.py prepare --preview D:/PythonProject/connlab/tmp/cleanup-preview-20261116/preview-facts.json --run D:/ConnLabCleanupBackups/<unique-run>
python scripts/legacy_import_cleanup.py apply --run D:/ConnLabCleanupBackups/<unique-run>
python scripts/legacy_import_cleanup.py verify --run D:/ConnLabCleanupBackups/<unique-run>
```

Do not copy the placeholder literally. Keep independent review/QA before applying to the live
store. Preparation creates a SQLite online backup, verifies `integrity_check`, retains the
approved preview and authorization summary, exports exact complete rows and completed journal
states into the checksummed manifest, copies all nine directory trees (including control and
empty directories), and verifies every file with SHA-256. A partial preparation has no valid
manifest/progress and grants no apply authority; retain it as failure evidence and prepare a
new run after resolving the cause. Copy the exact User authorization, independent review/QA
records and protected-file/catalog baseline into this durable run as additional evidence.

The tool holds the existing `materials-archive` then `library` locks and ordered project locks.
It rejects unfinished library/project operations, changed targets/sources/versions, new business
relations, incoming foreign-key children or unapproved path references. The database transaction
uses `BEGIN IMMEDIATE`; all SQL deletes use exported exact primary keys. Six empty Project roots,
10 members, six workspaces, nine derived folder caches, 109 file indexes and the six already
previewed `04-012` lifecycle events are the expected live removal. The exact current graph must
match the approved preview; new audit/business records stop cleanup. The six audit events remain
complete in both the database backup and manifest; existing completed batches and shared
recovery logs remain untouched in the live store.

After the SQL commit, each remaining directory is revalidated and sent individually through
Windows `IFileOperation`. There is no permanent-delete API/fallback and no automatic response to
a permanent-delete warning. `PreDeleteItem` must describe a recycle action; `PostDeleteItem` must
return the newly created Recycle Bin Shell item. Its actual `$Recycle.Bin/.../$R...` path is saved
before the Shell call returns, and the entire recycled tree is hash-verified. A vanished source
alone never counts as success. The isolated Windows probe verifies this transport on the same
local volume before real execution. See Microsoft
[SetOperationFlags](https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nf-shobjidl_core-ifileoperation-setoperationflags)
and [PostDeleteItem](https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nf-shobjidl_core-ifileoperationprogresssink-postdeleteitem).

## Failure and recovery

- Run `apply` again on the **same run** after an ordinary interruption. Full matching pre-state
  executes the single SQL transaction; fully absent selected keys recognize the committed state.
  Mixed or changed records stop. Existing recycle receipts suppress repeated operations.
- A recycle failure retains verified backups and any not-yet-recycled directory. Successfully
  recycled items and the database commit remain accurately recorded; fix the reported cause and
  resume, rather than create another cleanup run.
- A process can die between the OS moving an item and its callback persisting the receipt. If a
  target is missing without a receipt, automatic replay stops. Inspect the system Recycle Bin
  against the exact original path and verified backup; retain that evidence. Do not guess a new
  target or infer success from absence. Recovery can instead restore verified directory copies
  to **absent** original paths and use the selective association restore below.
- `restore-associations --run <same-run>` is an explicit operator recovery action, never invoked
  by apply. It only inserts the exact exported rows in parent-first order after requiring all
  selected primary keys to be absent. Existing PK/unique-key conflicts cause a transaction rollback.
  Restore directory copies separately to absent original paths first, using the saved inventories
  and no-overwrite copy semantics. Do not copy over an existing folder. Once restored, the run
  cannot be reapplied; a new cleanup requires a fresh reviewed snapshot.
- **Never replace the live database with the full backup** during normal recovery: other projects
  can have changed concurrently. The complete SQLite backup is retained for forensic recovery;
  scoped row restoration preserves unrelated writes.

Keep the run directory and Recycle Bin entries until the User separately decides their retention.
Neither task completion nor Close empties the bin, removes backups, pushes, publishes or packages.

## Verification

Isolated integration tests cover backup-before-unlink, no-overwrite originals, SQL rollback,
backup corruption/failure, changed files/new associations/audits, external cascade protection,
shared locks, ghost-only removal, unrelated concurrent writes, complete current SQLite schema,
audit restoration and process termination after a durable recycle receipt. A Windows-only test
recycles only a newly created test directory and verifies the actual Shell result and contents.
Final live evidence must separately compare all excluded directory inventories, original hashes,
root/configuration, exact catalog keys, removed relations, backups and nine recycle receipts.
