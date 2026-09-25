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
- Preview separates missing or unreadable generation inputs (`start_blockers`) from existing-file
  conflicts (`review_conflicts`). Both prohibit an ordinary Start. A conflict can be reviewed for a
  fresh Backup and Rebuild. For new reviewed archive/rebuilds, the preview binds the one active old
  business folder by directory identity and manifest, not by hashing its files. It shows that folder
  as the archive source and the latest confirmed Basic Information name as the fresh target inside
  the already indexed LTR workspace, even when the configured save root now differs.
  Missing inputs do not hide Link existing folder when the workspace identity itself is adoptable.
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
- A newly approved archive/rebuild moves the entire old business folder to
  `LTR/History/Folders/<old name + last-modified timestamp>` without inspecting its descendant
  names or bytes. The fresh business folder contains only the template and outputs regenerated from
  current confirmed authority; no old file is copied back. Root-level LTR files and Source Book stay
  in place. The source folder, workspace, archive parents, manifest and staged new folder retain
  identity/path checks. A registered FileAsset or separately selected source inside the folder to
  be archived is still a Start blocker: it must first be provided from an independent location for
  regeneration. A manifest with an official-folder filesystem identity must match the old folder;
  an older manifest without that field remains eligible only with the same-project/DL manifest,
  indexed path, and sole active DL-prefixed folder checks. A new active sibling after archival
  blocks recovery without deleting the archived old folder or operation-owned stage.
- A pending folder-name relocation can be retired by a new confirmed archive/rebuild only if no
  move or manifest update was recorded and the indexed sole active folder and manifest still match.
  A partly moved relocation must resume its own recovery. After an archive move, generation Resume
  uses the saved publication effect rather than requiring the pre-move preview to remain true.
  Historical content-bound generation journals continue their original recovery policy and keep the
  folder name approved when that journal started; a later confirmed Basic name cannot retarget them.
  A linked legacy LTR workspace whose directory name differs from the DL number still archives its
  verified DL-prefixed business child under that workspace's History/Folders.
- A hard exit during staging, before intent exists, abandons that unique staging attempt. A subsequent
  attempt uses a new path. Unjournaled files are retained, not guessed to be safe to delete. Workspace
  stages live in the configured output root's `.connlab/generation` area, outside final project content.
- A blocked historical initial rebuild can release its unpublished checkpoint when the original directory still
  has its recorded identity, no backup or other publication effect exists, and its unchanged staged
  directories are proven to belong to this operation. This also handles an older persisted checkpoint
  when an operator saved files after a locked-folder error. Only these internal stages are discarded;
  the edited original remains untouched. A changed historical folder requires a fresh preview and explicit new
  generation; legacy Continue existing folder preserves its contents. Missing ownership evidence, changed
  stages, backups, links/junctions, or incomplete cleanup retain the checkpoint for review.
- A file published before its record commits is reconciled into exactly one matching lineage record.
  A record committed before the progress checkpoint is recognized without generating or publishing again.
- A legacy workspace moved under the current configured save location can be linked explicitly when
  exactly one direct child has a non-redirected manifest matching both internal project ID and DL,
  with Source Book and its manifest-named official folder present. Multiple candidates, a foreign
  manifest, or a symlink/junction never supplies an automatic workspace identity. Link updates the
  manifest and workspace index; subsequent Open uses that indexed folder.
- If the indexed workspace still exists but its recorded inner official folder is missing, direct
  DL-named folders are listed by full path for manual review. Even a single candidate is not proof
  that it is the renamed folder: Link and generation remain blocked, and neither the manifest nor
  business content is rewritten. A foreign manifest also blocks repair. If there is no manifest or
  candidate, regeneration is offered only with a reachable template; Link is not offered for a
  missing folder.
- A legacy output record pointing to an unavailable old path can be relinked to the current target
  only when exactly one current system-generated record of the same kind has the target's SHA-256.
  Different bytes, multiple matching records, or an old path that still exists remain conflicts.
  Relink registers the current path without rewriting the target file. A redirected target or changed
  bytes at registration fails closed instead of registering an unverified new fingerprint.

## Fail-safe limits

Changed inputs, a stopped/closed project, changed targets, missing/unproven staged content, or a damaged
journal stop the operation. Resume cannot approve different inputs or overwrite foreign files; these
cases require operator/support review. Recovery backups and abandoned internal stages are retained for
that review. Safely checkpointed blocked operations may be explicitly replaced as described above;
uncheckpointed publication requires recovery or support review first. An unfinished operation is never
automatically replaced; the proven pre-publication staging cleanup described above does not remove
project files or recovery backups.

The existing Fee Form `.xls` template identity policy is retained: controlled revision/path plus size
allow legacy Excel OLE metadata churn. Other input/template bytes are hashed. Configured Test Record
templates outside the resource folder are also bound to the operation.

The retained direct `/official-workspace/create` backup route keeps its legacy manifest guard and
does not rename an old folder to a newly confirmed description. The Workbench Create folder path
uses the recoverable generation operation for that behavior.

### Windows overwrite cleanup

After all eight output steps finish, delete-and-rebuild removes only its journal-owned
`overwrite-old` recovery copy. Windows ReadOnly attributes on old files or directories can prevent
this final cleanup even though the new project outputs have already been generated. This is not
evidence that the configured project root is missing or that document generation failed.

The cleanup handles ReadOnly only on an entry whose approved location, filesystem identity,
non-redirected ancestry and retained content inventory have been verified. It does not change ACLs,
grant permissions, alter the new workspace or templates, or remove retained history. A locked entry,
real permission denial, changed content or changed identity still stops cleanup. The original
operation stays pending; it is not marked complete and cannot be replaced by a fresh rebuild.
ReadOnly files with multiple hard links also remain pending: changing their attributes could affect
an alias outside the approved recovery copy. Normal unlinking without attribute changes is unchanged.

Recovery uses the existing Create project folder review/Resume flow. It checks the original inputs
again and retries final cleanup without regenerating completed documents. The production runner passes
its live input check into the cleanup publisher, including checks before and after ReadOnly repair.
If inputs change after the attribute repair, deletion stops; it does not blindly restore attributes
on potentially changed content. Do not delete the journal
or manually reset its step counter to clear a cleanup error. Tests reproduce ReadOnly behavior in
temporary Windows directories; deployment does not automatically clean real project backups.

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
