# Separately approved renamed-copy cleanup

This local one-time entry handles only
`D:\ConnLabProjectsDev\DL-2026-11-013 [56cdd25d]`. It reuses the reviewed backup,
transaction, lock, recovery and Windows Recycle Bin implementation from
`legacy_import_cleanup.py`; it does not expand the completed nine-copy authorization.
No UI, API, dependency, schema migration or application startup path is added.

## Exact scope

The fixed member is `33043ab04dfb4bb484e2d9f30a0422ca`, the derived folder cache is
`9b8d61be32ba41ef8186b172edb4256f`, and completed intake batch
`3cf6adc1df33432686200577226889b6` remains unchanged. Only one member, one cache and
26 file indexes may be removed: **28 rows**, no Project/workspace/lifecycle records.
The target contains 27 files: 26 business files and `.connlab/library.json`.

Preserve the original
`D:\Project Model\DL-2026-11-013\DL-2026-11-013 T3BIGM FBB to GPU(Power) Qualification test`,
the entire unsuffixed `D:\ConnLabProjectsDev\DL-2026-11-013`, all other children,
the root and its identity, configuration, old completed batches and recovery logs.
Do not select by number or remove another directory sharing the DL number.

The read-only comparison established that all 26 business contents exist in the
original; 15 photos have different names there. The unsuffixed retained directory
also contains all 26 old names and relative paths with identical contents. Preserve
the comparison/name mapping as evidence. Revalidate the frozen files and associations
at execution rather than relying on this historical statement alone.

## New backup and execution

Use `C:\PythonEnvs\connlab\.venv\Scripts\python.exe` with `PYTHONUTF8=1` from the clean,
reviewed checkout. The CLI requires the exact production database and root. The Python
seam uses the same fixed member/cache/batch scope with isolated paths only for tests.

```powershell
$env:PYTHONUTF8 = '1'
python scripts/renamed_import_cleanup.py prepare --preview D:/PythonProject/connlab/tmp/renamed-import-cleanup-20261117/execution-preview.json --run D:/ConnLabCleanupBackups/<new-unique-run>
python scripts/renamed_import_cleanup.py apply --run D:/ConnLabCleanupBackups/<new-unique-run>
python scripts/renamed_import_cleanup.py verify --run D:/ConnLabCleanupBackups/<new-unique-run>
```

Replace the placeholder with a new persistent run path. Do not reuse the earlier
nine-directory run: that backup does not contain this directory. This entry rejects
legacy/default-authorization runs, mixed identities, other directory/cache/batch IDs,
Project bindings and counts outside the approved single item.

Preparation takes a new SQLite online backup and checks integrity, exports exact rows,
copies the complete tree including the control file and empty directories, and verifies
all content hashes. The actual single-copy authorization is written to `authorization.txt`
and included inside the checksummed manifest; it must not describe the old nine-copy scope.
Store the User request, comparison report, protected-directory/configuration baseline,
review/QA reports, implementation commit/patch and final verification in this run.
Partial preparation grants no apply authority; preserve it as evidence and resolve its cause.

Independent review and isolated QA must pass before live apply. The executor holds the
existing materials-archive/library locks, revalidates the exact graph and source/target,
and commits the exported PK deletes in one transaction. Completed batch audit stays live.
It then revalidates and recycles the one tree through Windows IFileOperation. A genuine
returned Recycle Bin destination plus matching full contents is required; source absence
alone is not success. There is no permanent-delete fallback or automatic confirmation
of a permanent-delete warning.

## Recovery and retention

Resume ordinary interruption with `apply --run <the-same-run>`; durable receipts prevent
a second recycle. Missing items without a durable receipt stop automatic replay. A process
can die between the OS move and receipt persistence: inspect the exact system-bin item
against the backup, or restore the verified tree to an absent original path before
selectively restoring its associations. Do not guess success or create a replacement run.

`restore-associations --run <same-run>` is an explicit recovery action. It inserts only
exported rows when all selected PKs are absent; conflicts roll back. Restore files separately
with no-overwrite semantics. A restored run cannot be applied again. Never overwrite the live
database with the full backup: unrelated projects may have changed concurrently.

After execution, independently verify backup/live integrity, exactly the 28 deleted rows
and no other data/schema changes, full backup and actual recycle contents, original and
all excluded-directory inventories/identities, root/configuration, completed batch/journal
state and catalog keys. If the local HTTP service is offline, use the production search
service/repository with SQLite `mode=ro`, query-only and a write-denying authorizer; do not
start the application or claim HTTP verification.

Keep the new backup, audit evidence, old run and Recycle Bin contents. Do not push, publish,
package, empty the bin or remove backups/worktrees. Completion waits for an explicit task Close.
