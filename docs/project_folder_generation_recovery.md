# Project Folder generation and interruption recovery

The Workbench starts one backend operation; its browser does not issue the individual document writes.
The fixed sequence is workspace, request materials, folder check, Customer Feedback, Fee Form, Test
Record, Test Status, and copied Application Form write-back. Existing per-step endpoints remain available.
Project/Matrix/confirmed Fee/Basic Information and configured source/template authority remain unchanged.

## Ownership and approval

- `GET .../project-folder/generation/preview` returns the displayed workspace preview and its context
  token together. Start sends that same token and a request ID; conflict confirmation retains the token
  from the displayed dialog. Changed source/configuration/targets require a fresh review, never implicit
  reauthorization. Repeating a request ID returns the existing operation.
- The backend owns worker and session lifetime. Each step opens and commits its own session; only then
  does the journal advance. Closing a page does not cancel generation. Reconnection reads the current
  operation; Resume uses its operation ID and verifies the original context before any additional write.
- Corrected inputs may start a new operation only after a fresh displayed preview and explicit action.
  The previous journal is archived unchanged; conflict choices are collected again, never inherited.
  Replacement is refused while any durable publication effect lacks its completed-step checkpoint.
  This permits fixing missing inputs without rebinding a partly generated operation to new authority.
- A project-scoped OS file lock serializes generation. The retained per-step mutation routes share the
  lock/unfinished-operation guard so another tab cannot bypass the active operation.

## Durable publication

The checksum-protected journal is under `Settings.data_dir/project_folder_generation/<project-hash>`.
Each operation records staged identity, complete content hash, target preimage, intended output
registration, and stable workspace record before publication. SQLite remains an index/lineage store,
not a replacement for configured external business authority.

- New files are published from complete same-volume staging with no-overwrite hard links. Matching
  content alone is insufficient for recovery: the final file must retain the recorded filesystem
  identity. Only the exact proven staged link is removed; there is no broad directory cleanup.
- Managed updates recheck the expected target content and identity before replacement. Application
  Form Office edits operate on a journal-owned temporary copy, never the final or original source file.
- Workspace contents (including Source Book for new workspaces) are staged before directory rename.
  Every later step verifies recorded workspace, official-folder and Source Book directory identities
  before recovery or writes; generated contents may evolve, but replacement directories are refused.
  Manifest intent and the stable workspace record recover move/manifest/DB gaps. Existing conflicts
  move to the operation's recovery backup once; restart never repeats that destructive choice.
- A hard exit during staging, before intent exists, abandons that unique staging attempt. A subsequent
  attempt uses a new path. Unjournaled files are retained, not guessed to be safe to delete. Workspace
  stages live in the configured output root's `.connlab/generation` area, outside final project content.
- A file published before its record commits is reconciled into exactly one matching lineage record.
  A record committed before the progress checkpoint is recognized without generating or publishing again.

## Fail-safe limits

Changed inputs, a stopped/closed project, changed targets, missing/unproven staged content, or a damaged
journal stop the operation. Resume cannot approve different inputs or overwrite foreign files; these
cases require operator/support review. Recovery backups and abandoned internal stages are retained for
that review. Safely checkpointed blocked operations may be explicitly replaced as described above;
uncheckpointed publication requires recovery or support review first. Nothing automatically discards
an unfinished operation or deletes data.

The existing Fee Form `.xls` template identity policy is retained: controlled revision/path plus size
allow legacy Excel OLE metadata churn. Other input/template bytes are hashed. Configured Test Record
templates outside the resource folder are also bound to the operation.

Publication requires stable nonzero filesystem file IDs and same-volume hard-link/rename support
(the Windows/NTFS workbench environment). Unsupported filesystems fail safely. This is not an atomic
compare-and-swap against a non-cooperating external editor between the final check and OS replace;
operators must not concurrently edit output files during generation. ConnLab's participating HTTP
mutations are serialized. There are no new dependencies, database schema migrations, public-drive uploads,
or implicit business-authority changes.

## Regression coverage

Developer fixtures use temporary directories/SQLite and fake Office only. Coverage includes backend
start/read/resume, source/template drift, closed projects, damaged journals, shared locks, foreign matching
bytes, frontend project-switch/stale responses, and reconnect without browser-owned writes. Subprocesses
are forcibly exited during workspace copy/move/backup/manifest/index windows, file-before-DB and
DB-before-checkpoint windows, and fake Office editing/publication windows. Recovery asserts unchanged
foreign/source bytes, no duplicate registration, stable output timestamps and no repeat Office generation.
Independent Reviewer/QA/Integrator checks are required before completion of this high-risk change.
