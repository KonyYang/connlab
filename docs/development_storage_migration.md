# Development storage and the reviewed local relocation

The explicit development entry (`backend.api.development:create_app`) selects development;
the packaged server and desktop launchers select release. Ports, folder names and database
contents do not choose the environment. The Vite development entry expects development;
the built HTML expects release. A mismatched first connection does not mount business pages.

| Current purpose | Development default | Release default |
| --- | --- | --- |
| Project output | `D:\ConnLabDev\Projects` | `D:\ConnLab\Projects` |
| Materials library | `D:\ConnLabDev\Materials` | `D:\ConnLab\Materials` |
| Temporary materials | `D:\ConnLabDev\TemporaryMaterials` | `D:\ConnLab\TemporaryMaterials` |

`Settings.output_path(purpose)` supplies the common output-root rule. New actual output
purposes should reuse that rule when implemented; this change predefines no future classes
or Settings. Explicit operator output locations remain authoritative. First related use
creates an unconfigured default and records its binding. Startup and opening unrelated
pages do not create these three business directories. A saved offline location is not an
unconfigured location. Missing drives and access failures direct the operator to the existing
Settings location controls, without C-drive fallback or blocking unrelated functions.

Existing internal storage stays where it is: development uses its repository data/config/log
locations, release uses its existing per-user ConnLab locations or explicit managed library.
An entry replaces only inherited defaults that it previously owned, before reading its own
configuration. Explicit environment overrides remain overrides. Upload spooling and owned
child-process temporary files use the current data directory's `tmp`. Shared external-file
locks retain the existing physical-file lock domain; changing environment does not split it.

The runtime identity combines explicit environment, canonical database location and file
identity. Normal database writes and restarts retain the same namespace. An atomic database
replacement requires restarting a running backend. Unsupported in-place byte overwrites
that preserve a file's identity are not a supported restore procedure. Restore only while
writers are stopped, using a separate verified database file, then restart.

Before loading App or reading business browser state, the frontend binds `/api/runtime-environment`.
JSON, multipart, blob and generated-file downloads carry the expected data instance. The
backend checks it before invoking routes or consuming request bodies. A switched backend
unmounts the old business UI and requires reload; it cannot adopt old drafts automatically.
Business local/session storage and the Temperature IndexedDB are namespaced by environment
and database instance. Old unscoped values/databases remain untouched and are not restored
into a newly bound instance. Same-host login cookies are similarly namespaced. The Sidebar
collapsed preference is only a visual preference and remains shared.

Release startup does not manufacture optional administrator credentials or require writing
ProgramData for unrelated features. Missing/unreadable credentials disable workbook writes;
existing valid administrator configuration is preserved.

## This machine's finite relocation

`scripts/migrate_local_development_materials.py` is an operator coordinator for the reviewed
2026-11-17 development inventory only, not a user feature or general migration tool. Its CLI
accepts only the primary repository and evidence beneath `D:\ConnLabDev\MigrationBackups`.
It never stops processes, deletes old folders, clears database tables or replaces existing targets.

The fixed candidates are four project members from `D:\ConnLabProjectsDev` (DL-2024-12-050,
DL-2025-02-054, DL-2026-01-072, DL-2026-11-013), two archives from `D:\ConnLabMaterials`
(DL-2026-04-032, DL-2026-05-001), and the three reviewed directories from
`D:\ConnLabProjectsTemporary`. Each goes to the corresponding child under `D:\ConnLabDev`.
The old empty materials configuration is rebound to `D:\ConnLabDev\Materials`.

Keep `DL-2026-11-003` at its old location: its business folder is missing and it has no
library member with a supported complete-root rebind. Seven old development workspace
references into the release-owned `D:\ConnLabProjects` also remain unchanged for ownership
review. Real source locations, release data, `ConnLabCleanupBackups`, existing test evidence,
root directories and other backups are not relocation candidates. The old project parent
therefore remains partly active because of the held workspace.

1. Recheck the board, exact running processes, reviewed inventory and source ownership.
   Coordinate and stop only development writers; preserve the live release process.
2. Choose a unique run directory. Run the script without `--apply` to prepare a consistent
   SQLite backup, config copies, source file hashes/identities and exact before-reference records:
   `python scripts/migrate_local_development_materials.py --evidence-dir D:/ConnLabDev/MigrationBackups/<run>`.
3. Review the saved `relocation.json`. With development writers still stopped, run the same
   command with `--apply --writers-stopped`. The flag records the operator's coordinated
   prerequisite; the script does not attempt to kill or discover every possible writer.
4. The coordinator uses verified non-overwriting copies, supported member location plans and
   the explicit project ownership path contract. It rebinds exact archive/cache IDs while
   retaining relative indexes and completed copy-operation audit payloads. Only after all
   copies and reference updates succeed does it switch the three active roots. Source paths
   recording original receipt provenance are retained. No database-wide string replacement occurs.
5. Run the same command with `--verify`, restart the owned development services, and verify
   project opening, query, file access and a new isolated save. Record actual UI/API evidence
   alongside the manifest. The coordinator alone does not claim these user-flow checks.

The run journal retains original plans so interrupted publication resumes the existing
operation. An incomplete copy or changed source/target stops for inspection and retains
both locations; it never overwrites an existing partial file. Do not delete an uncertain
copy to obtain a green run. The original directories are recovery copies after successful
rebind and must no longer be used as normal write/index roots. The held directories remain
explicit exceptions. The consistent database backup and config copies are recovery evidence,
not automatic permission to overwrite a live database. If rollback is necessary, stop writers
again and review the saved exact before/after records and subsequent edits first.
