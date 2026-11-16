# Historical materials collection and lookup

The library is an auxiliary archive. Project, LTR, Matrix, generated records and report authority
remain in their existing workspaces. Archive problems must not block those workflows.

## Ordinary receipt

Receive materials opens one native folder picker. Cancelling has no receipt side effect. The only
normal confirmation shows source, destination and Receive/Cancel. No business fields or state are
required. Equal project numbers do not identify equal folders. Existing names produce only Skip or
Keep independent copy, retaining the full original name with a suffix; no target content comparison
or replacement is authorized. Internal control files are preserved byte-for-byte without parsing.
The old Import UI is retired; old receiving/copy APIs and journals remain for their existing callers.

## Persistence and recovery

The additive `material_archive_folders` table represents directory indexing independently of copy
operations. A manually discovered folder does not acquire a fictional receipt batch. Filename-only
rows in `material_archive_files` cache the existing catalog sources; queries do not recursively scan
or stat each archive directory. Refresh updates those caches explicitly. Missing roots retain their
records and settings; a failed/cancelled directory scan does not replace its completed file cache.

Confirmed archive copies use the existing batch store with operation `material_archive`. One saved
plan retains one operation/final-directory identity across retries. Work first uses a private
same-volume staging payload under the library's excluded `.connlab/receiving` namespace. No file is
copied before staging identity is durable. An uncertain empty stage is retained and replaced by a
new stage instance within the same operation. Publication uses no-replace directory rename after
identity is persisted; restart can recognize an already-published folder by that identity. Index
failure remains incomplete/index_pending, and retry repairs registration without requiring the
original source or copying the files again. Edited received files are not overwritten.

## Lightweight independent work

A two-worker, bounded materials pool receives fresh SQLAlchemy sessions from the request's injected
engine. Neither request ORM objects nor sessions cross worker threads. Long scan/copy work uses a
materials-specific lock. The existing library lock is held only for the short final publication and
configuration revalidation boundary. Polling is read-only; cancel sets an Event checked at directory,
hash and copy chunks. While an OS operation is blocking, status remains cancellation_requested;
completion/cancellation is reported only after the worker actually exits that operation. The receipt
dialog can return to the library while cancellation remains pending, leaving its original operation
recoverable without holding navigation behind a modal.

Refresh discovers direct child folders only, then updates the lightweight catalog file cache.
Root/deep/recursive selections and redirected filesystem paths are rejected. Discovery excludes
control/staging directories. Ordinary file browse/search excludes .connlab and database files.
Formal project roots retain their own stable catalog identities; an archive is a copy source, never
an implicit formal-project destination. Existing explicit Workbench-bound selected-file copy remains.

## Acceptance and risks

Tests use isolated SQLite and directory trees. They cover manual discovery and stable identity,
same-name independent copies, four subprocess interruption windows, SQL registration failure after
publication with disconnected source, partial files, cancellation, root offline, filename-only
queries with disk scan/stat forbidden, real Windows junction rejection, long Chinese names, additive
schema preservation and a fresh-session HTTP worker. Symlink fixtures may be skipped by host privilege.
No business files, source databases or real Documents settings are used for experiments. Source
metadata and identities can be revalidated, but external storage may block inside OS calls; cancellation
is cooperative at the next checked boundary. No watcher, content deduplication, full-text/OCR/vector
index, batch splitting, metadata editor or archive management page is introduced.
