# Generate files in an existing project workspace

`ProjectFileGenerationService` coordinates selected derived files independently of folder creation.
The entry requires an existing registered phase-one workspace whose configured boundary, project/DL
identity, manifest, and directory identities still match. It never creates a project workspace,
collects request materials, or changes public-drive naming, synchronization, submission, or reports.

The API is `/api/projects/{project_id}/project-folder/files`: GET previews eight items, POST `/start`
accepts an idempotent `request_id`, workspace token, and per-file token/action; GET
`/operations/{operation_id}` observes progress and POST its `/resume` resumes explicitly. Requests
cannot supply filesystem paths. Display target and backup paths are relative to the linked workspace.

| File | Required confirmed inputs |
| --- | --- |
| Customer Feedback Form | Basic Information, Matrix plan-date schedule, feedback template |
| Fee Form | Matrix, current Fee, Basic Information, fee template |
| Test Record | Matrix, Basic Information, configured DOCX template |
| Test Status | Matrix |
| Application Form | Proven selected archived Word source or current managed target, Basic Information, schedule |
| LLCR / CR Record | Relevant Matrix steps and explicit Matrix Point Profile |
| IR/DWV Record | Relevant Matrix steps, explicit electrical pairs, configured template; missing Basic produces warnings |

Readiness and tokens belong to each file. A missing prerequisite or ordinary generator failure does
not prevent independent selected files from completing. Explicitly skipped files stay skipped.
Existing targets default to skip; replacement requires `replace_with_backup`. A target collision
between selected kinds is rejected before dispatch. Tokens bind the selected authorities/templates,
target parent identity, and reviewed existing file hash/identity rather than unrelated outputs.

## Publication and recovery

The canonical project lock remains `data_dir/project_folder_generation`. A dedicated checksummed
`ProjectFileGenerationJournal` stores current and historical receipts under
`data_dir/project_file_generation`; it does not change the legacy v1 journal reader or schema.
The initial queued receipt contains its complete workspace and choices. Request replay searches both
current and historical receipts and rejects a different signature for the same request identity.

Before creating staging, the service saves the operation-owned directory intent. Staging lives under
the configured workspace root's `.connlab-file-staging/<operation_id>/<key>`, outside the LTR business
subtree and on the target volume. The publisher verifies file/directory identities, hashes, and
hard-link support before archival. Its frozen receipt precedes target mutation. Explicit replacement
atomically moves the reviewed file without replacement to
`LTR/History/Files/<operation_id>/<filename>`, verifies and flushes that backup, then publishes the
staged file using exclusive hard-link creation. It never deletes a final target to make room.
History parents and all publication parents are identity checked. A racing unapproved file moved
into History is retained and stops recovery; it is never removed or silently accepted.

Recovery resolves frozen publication and registration effects before rereading current sources.
Published outputs register from frozen lineage with existing `ProjectOutputRecord` rows and an
idempotent equality check; no database migration is needed. A crash after a database commit but before
receipt completion reuses that row. Completed items are never regenerated. A reappeared target,
changed/missing backup, changed parent, or staged bytes without durable file identity stops recovery
and retains all evidence. No automatic History or staging cleanup is introduced.

Queued/running/interrupted or damaged receipts fence registry, library/portability, Basic folder,
legacy generation, direct output and report writers under their existing project lock. Specific
file-lock errors can leave that item recoverable while other selected files finish; journal,
database or ownership uncertainty stops shared writes. Ordinary terminal failures yield completed
partial results and release the fence. Read-only status derives a dead or undispatched worker as
interrupted without mutating the receipt; the browser does not own continuation.
The non-mutating local/public folder-open actions retain registry visibility checks and remain
available during generation or recovery; they do not acquire a generation write slot.

## Verification and remaining risks

Focused tests exercise independent readiness, explicit skip, idempotency across history, target
collisions, real no-replace moves/hard links, same-byte inode replacement, parent replacement,
published registration retry, unknown staging and dead-worker projection. API tests reject client
paths and prove interrupted/damaged receipts block retained writers. Source tests use isolated
SQLite and real generated workbooks; Office boundaries use test writers where Office is unavailable.
Independent QA must also exercise fresh-process interruption and recovery with isolated SQLite and
files. Filesystems lacking stable identities, hard links, or atomic no-replace moves fail closed;
manual review is required for ownership that cannot be proved.
