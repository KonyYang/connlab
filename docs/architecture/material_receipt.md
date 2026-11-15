# Reference Library materials receipt

## Authority and boundaries

Ordinary Reference Library receipt is explicit file receipt. It does not register a business Project,
claim an LTR, parse a snapshot/database, restore Matrix or lifecycle state, bind a workspace, or create
portable data. Legacy import/recovery routes remain compatibility code; ordinary library navigation
must not call their member or portable APIs.

The receive save root lives in `material_receipt_settings`, independently of the native project output
root. Settings > Default locations > Materials library folder is its only ordinary editing surface.
Existing saved values and revisions remain in use without migration, even when temporarily offline.
With no saved path, the first runtime/settings read or receipt preview initializes
`<Windows Documents>/ConnLab/Materials` and persists that setting under the existing library lock.
Windows Documents is resolved through the OS known-folder API, including redirected Documents
locations; it is not a hard-coded user-profile path. Only the missing app-owned directories are
created. Existing contents are retained without scanning/adopting or moving them. Ownership and
internal-data boundaries are checked before creation; failures leave the setting unconfigured.
Receive reads that setting directly and shows the destination without configuration controls. An
unavailable root or failed default initialization blocks new receipt with actionable Settings guidance.
Changing the default does not move existing files, rewrite received-entry roots or change native project roots.
New received-only identities live in `material_receipt_entries`; durable progress lives in
`material_receipt_batches`. These additive tables are registered by the existing database bootstrap.
Metadata is central; the received source's `.connlab` files are never rewritten by receipt management.
Search distinguishes `unassociated` (no registered folder), `unavailable` (registered location cannot be
read) and `available`. The backend catalog retains these distinctions; explicit backend number/name
queries or project selections can resolve unassociated entries without a missing-location warning.
The ordinary library UI displays only available material directories, including when searching.
The same distinction appears in same-number receipt candidates, which cannot supplement an unlinked root.

`MaterialReceiptService` owns preview/confirmation/retry/metadata decisions. `MaterialReceiptFiles`
owns paths, hashing, locks and exclusive publication; `MaterialReceiptRepository` owns persistence.
The HTTP boundary is `/api/material-receipts`. The existing unified search catalog includes `receipt:`
entries without opening any Office file or invoking the old import service.

## Receive contract

1. Choose one folder and review its number, product description, test keywords and materials state.
   Historical numbering is preserved as entered (outer whitespace trimmed); case-insensitive equality
   only supplies same-number candidates. Folder names and relative paths are retained.
2. A same-number candidate never implies automatic ownership. Choose a managed native/received target
   to supplement, or an independent entry with a distinguishing description. Linked originals are
   visible candidates but cannot be write targets. Missing locations remain visible and unavailable.
3. Preview hashes source and target contents and binds the configured root revision/physical identity,
   target identity and current catalog metadata. Changes require a new preview before confirmation.
4. Only explicit confirmation starts receipt. Every original file, including old databases/snapshots,
   is copied byte-for-byte; empty directories are included. Ordinary materials default to Completed;
   a folder containing `.connlab` requires an explicit materials-state choice, without reading its
   internal state. This label is independent of all native Project lifecycle state.
5. Corresponding files with equal hashes are skipped. Different content is retained beneath
   `补充资料/<date-time>-<source>-<batch>/original-relative-path`; existing files never change.
   Incoming `.connlab` control data supplementing a native project always goes to that archive,
   even when its live counterpart is absent. Prior receipt records recognize already-preserved
   incoming content only for the same target and original relative path, and verify actual bytes.

## Concurrency, interruption and retry

Receipt uses the existing library lock and, for native targets, the existing project-generation lock
and pending-generation guard. Each file is staged next to its final target and hash checked before
atomic, no-replace publication (Windows rename; hard-link publication elsewhere). A racing target
file causes a per-file failure, never replacement. Temporary files are operation-owned and removed.

A durable batch is saved before destination creation and after each item. Successful independent items
continue when another item fails. Results distinguish copied, skipped, supplemented, failed and
retained-changed items, with separate file/directory counts. Lost-response confirmation returns the same
completed result. Incomplete batches resume by their own receipt identity; legacy batch endpoints cannot
read or run them. Source changes require a fresh preview. Previously copied items edited or deleted
before retry are retained as-is and reported as changed; retry does not recreate or overwrite them.

If a process stops between creating a new empty target root and recording its physical identity, retry
fails closed instead of claiming an unverified occupied directory. The original source and existing
files remain intact; inspect the incomplete result and preview a distinct location. Multi-instance
writers must share the same central data directory for the library/project lock scope.

## Metadata and reconnect

Received-only product descriptions, keywords and materials state are revision-checked metadata edits;
files and folder names are not changed. Native metadata remains in its Project business authority.
Unavailable entries remain in the backend catalog, with their existing identities and records.
The ordinary library lists only currently available directories, without a lost-location list or
Locate actions; refresh can reveal an entry again when its registered directory is available.
Scan limits/access errors and failed requests still surface actionable warnings. Daily details show
current materials metadata and location, without receipt history or source paths, and do not fetch
catalog history or run retries. Current receipt/copy dialogs retain their operation-bound result
checks and retries. Backend history and relocation endpoints remain available for compatibility.
Explicit location preview and confirmation reconnect a moved managed copy without copying files, parsing markers or changing a native
workspace. Original sources and all known native/member/linked/other-receipt roots (including retained
ones) are protected against aliasing. Unknown moved copies require the user's explicit folder choice.

## Verification and residual risks

Use isolated SQLite and folders. Required regression seams cover explicit preview/confirm, byte
preservation, no Project creation, native supplementation, repeated conflict skipping, historical
numbers, old-ConnLab materials-state confirmation, source/target/root changes, concurrent confirmation,
partial failures and fresh-session retry, edited/deleted copied files, directory failures, exclusive
publication races, missing-root search, metadata edit, reconnect ownership, separate batch namespaces
and cold additive-schema registration. UI acceptance must verify that folder selection never receives
files automatically and ordinary library details make no portable/recovery calls.

Very large sources are bounded by the existing inventory limits. Hashing reads all bytes and may be
slow on unavailable/network/removable storage; errors block or mark incomplete rather than declaring
success. No automatic synchronization, backup, Office parsing, restoration or cleanup of user files is
part of this feature. Layout and old compatibility behavior require separate review/QA on the final
integrated state.


Receipt ownership and relocation guards: the receive container may contain separate registered
entries, but cannot be an existing entry or lie inside one. Every new receipt destination must
be disjoint from registered native, linked, member, and received roots and their known original
sources; preview and confirmation recheck current ownership. Incomplete batches bind their
new received entry registration as well as physical destination identity, so relocation or
metadata revision requires a fresh preview instead of resuming writes to an old location.
Journal history and prior-conflict matching use the stable target key; after a managed folder
move, duplicate skipping still verifies the archived bytes at the current registered location.


Ordinary directory browsing uses `GET /api/project-library/browse` with a stable catalog key
and `relative_directory`. It lists only immediate children with type, extension, modified time,
and root-relative paths; refresh reads current disk state. Missing roots retain their catalog
identity, while unassociated native projects have no directory to browse. Redirected paths,
traversal, drives and alternate data streams are rejected. Filename search results include the
matching project's catalog metadata for the two-pane navigation surface.

Selected-file copying is a separate application service and file-plan adapter. The public
`/api/material-receipts/copy-preview` input is `source_key`, `relative_path`, `target_key`, and
`target_relative_directory` (default `Reference materials`); `/copy-confirm` accepts the saved
plan ID and fingerprint. Roots and target project identity are server-derived. Only an existing
business project can be the destination, including project-bound imported material entries.
The copy service uses the same project/library locks, exclusive publication and receipt journal,
but does not create a received identity, business Project, Matrix, snapshot or restoration state.
A preview authorizes one file only. Source hash/root identity, target registration/root identity
and target contents are rechecked at confirmation. Equal content is skipped; conflicts and
ConnLab control data are archived under a batch supplementary directory without replacing the
selected destination. Repeated archived files are skipped only after current-byte verification.
A failed copy retains an explicit result and uses the normal batch retry endpoint; a later manual
collision is never overwritten. Completed batch replay returns its historical result without
re-copying files. Selected-file confirmation currently inventories the destination root for stale
preview and conflict checks, so very large roots incur bounded receipt inventory costs.

Acceptance coverage includes browsing refresh and containment, filename-to-project navigation,
exact selected-file publication, explicit confirmation, native-only target eligibility, changed
source/target registrations and physical roots, conflict archives/repeat skipping, control-data
isolation, concurrent confirmation, failed-copy retry with manual collision, and HTTP contracts.
All checks use temporary files/databases; OS symlink cases are skipped where host privileges
prevent fixture creation. Ordinary copied files remain ordinary files, without automatic sync.


`GET /api/material-receipts/catalog-history?key=...` exposes durable copy and receipt batch
summaries for an existing canonical catalog identity, newest first, even when its directory is
unavailable. A bound member alias resolves to its canonical project when deduplicated. Full batch
results and explicit retry remain separate endpoints. This read-only history does not invoke
portable state or write native metadata. Across selected-copy and whole-folder operations,
archive reuse additionally requires the same intended destination relative path; a copy under
`Reference materials` cannot satisfy a later receipt intended for the project's root.


## Settings and daily browsing acceptance (2026-11-15)

- Existing receipt destination loads in Settings and is persisted through the existing receipt API;
  native project default and each registered project folder remain separate.
- Ordinary Receive has no location editor; it displays Materials library folder and uses the saved
  default directly. No valid root means no receipt confirmation can start.
- Many unavailable catalog entries produce no repair list; restoring a registered folder and refreshing
  makes it visible again without recreating its record. No deletion, relocation or filesystem scan
  of unrelated directories is introduced.
- Daily details omit history/source/Locate controls, while receipt metadata edits, formal Workbench
  navigation and current-operation confirmation/retry remain intact.
- Validate with synthetic API/browser responses plus isolated SQLite/folder tests. Root settings do
  not migrate old material folders, and hidden entries remain backend records rather than a cleanup
  queue. Real business files are outside validation scope.
