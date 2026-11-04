# Unified project library and portable project data

Status: current implementation contract. The shared task board and current test
evidence determine acceptance. Production data migration is a separate,
explicitly authorized operation.

## User contract

- The full registered LTR, including any suffix, remains the business reference.
  The internal Project identity is stable; titles and absolute directory paths
  are mutable. A matching LTR alone never authorizes replacement of a record.
- Engineers may add, edit, copy or delete ordinary files and directories using
  Windows. File freshness and missing evidence are separate from project identity.
  A missing file does not authorize recreating an empty form or replacing results.
- A project can remain available for browsing while required information is
  incomplete. Only actions that need that information are blocked.
- A complete project folder can carry a versioned data snapshot for another
  compatible ConnLab instance. The target must recover without reading the source
  computer's database or following its original absolute paths.

## Project library entry

### Simple receiving flow

Import Projects has one default path: choose one complete project folder. The
normal production route runs the existing scan and reviewed plan automatically.
When the result is safe, ConnLab receives the files (or restores a compatible
portable snapshot) and opens the verified Project identity without showing a
second review or confirmation page. An unchanged duplicate opens its existing
Project without creating another batch. The configured save location is owned by
Settings and is not repeated or editable on the import page.

The page stops only for a decision that cannot be inferred safely: a missing LTR,
an incomplete folder boundary, a carried ConnLab identity without a usable
snapshot, or an identity/content conflict. A trusted snapshot with the same stable
Project identity and different saved data offers only **Replace Existing Project**
or **Cancel Import**. Replacement first creates the backend-owned complete recovery
copy. A matching LTR with a different Project identity cannot replace the current
project from this flow. Manual path entry is a fallback only when the native folder
picker fails. Batch controls, linking tools, destination controls and implementation
details are not part of the default single-project path. The backend still
authorizes every choice.

Each ordinary review row carries a stable fingerprint of its reviewed source and
destination context. Files-only replanning retains selection/keep-copy decisions
only for unchanged rows; changed rows lose both selection and the old decision.
The source strip truncates long names, with full paths in folded options. The
final copy sentence uses the save-folder name rather than repeating a long path.

Running and interrupted batches expose an explicit Resume action; the existing
OS-owned library lock rejects a concurrent writer. Resume verifies copied material
and ownership before registration. Supplementary files require the batch's own
durable receipt, not just their parent project's marker. Cross-volume moves use
a verified destination-side staged copy and durable transfer receipt before
removing the original. Copy/promotion interruptions can retry; occupied or changed
destinations preserve both locations. No real project migration is implied.

Folded comparisons name changed/added/absent files (bounded lists) and recognized
project, Matrix, test-result and scheduling record families. They compare saved
content, not row order, and do not perform a field-level merge.

A successful single-project intake opens the verified Project identity directly.
Non-blocking source warnings remain recorded instead of preventing normal project
use. A retained history copy stays in its safe details view. Returning to Projects
always uses the complete catalog.

Source completeness is separate from file layout. A carried ConnLab identity
without a snapshot is never silently treated as a restored project. When that
identity already has local data, intake may reuse it through the existing guarded
linking review. Otherwise the user must export from the original computer or
explicitly choose Import Files Only. That choice creates a new project identity,
retains the source metadata inside the copied subtree, and does not claim restored
test data. Newer marker or snapshot versions require a ConnLab update and cannot
use this fallback. Malformed metadata also prevents silent normal intake.
The original software identity remains available for duplicate comparison, while
the files-only project receives its own identity. Choosing the unchanged source
again opens the received project; changed material still requires fresh review.

Supported version-1 snapshots are verified before restore. The known earlier
contract without group-completion events is normalized to an empty event
collection after validating its original signature; the source envelope is never
rewritten. Unknown contracts are not guessed or overwritten.

### Managed ordinary intake

Final ordinary intake confirmation establishes a stable Project binding as well as
library membership. Repeated batch submissions reuse that binding. Carried stable
project IDs are retained; an already-existing unclaimed Project ID is linked by
the same final confirmation after previewing the old and new working locations.
Writer exclusion and an unchanged registry/folder context are required before
copying, then checked again before rebinding only owned file paths. Existing
project data is retained. Recycle, a different registered LTR, another managed
entry, or an incomplete existing workspace require conflict review. Interrupted
binding can resume only for the batch's unchanged member and destination.
Explicit conflict copies retain
their separate review rules. No LTR workbook registration, Matrix confirmation or
test values are manufactured by intake.

A recognized `LTR Title` business folder is copied into `Projects/LTR/LTR Title`
with an empty root-level `Source Book`. A pure LTR root containing one matching
business folder is received without another outer layer; an absent `Source Book`
is created in the copy. Original files and internal material paths remain intact.
Supplementary assignments and portable restore keep their reviewed placement rules.
Existing source-named folders require conflict review before standard reception.
Material equality accounts for the copied envelope, so unchanged sources remain
duplicates while changed evidence still requires review. Other layouts retain their
existing handling until explicitly resolved; they are not silently rearranged.

Flat legacy folders with an LTR are received as a complete business subtree,
including any old Source Book inside that subtree. A new empty root-level Source
Book does not claim that those old workbooks were restored into execution data.
A bare LTR folder uses an `LTR Imported files` child when no business title is known.
Selecting only a standard materials subfolder without project identity, multiple
same-LTR business folders, or a file occupying the canonical Source Book location
requires boundary review. Keep Separate cannot override these boundary blockers.

Registry summaries expose a historical LTR only through explicit Project membership.
Its display kind is `imported`, with `has_registered_ltr=false` and no registered
LTR record. A real LTR registration always wins. Imported rows use the normal
project actions without a permanent imported-only badge; missing Matrix state is
shown rather than inventing completion.

Recognized standard imports also bind the received root, business folder and
Source Book in the normal workspace record and publish a matching manifest.
Existing mismatched workspace bindings require review. Ordinary successful import
navigation reads the actual member identity before opening the workbench; retained,
unavailable or unbound records keep their safe details entry.

Project details expose the explicit `library_member_id` association for catalog and
file-management views. The common Workbench does not add an imported-project setup
card or a special Browse Files action; imported and locally created projects use the
same normal Workbench actions. Recycle display and restore conflict checks use the
same historical identity rule as Projects; a real registered LTR continues to take
precedence. These reads do not register an LTR or mutate source materials.

Imported projects without real Matrix draft steps show an empty setup state rather
than sample test steps. Actual draft steps remain visible for review, and confirmed
Matrix projections retain the normal execution workspace. No confirmation or test
data is inferred from the presence of ordinary files.

New portable working copies use the validated full LTR as their destination root,
including suffixes, regardless of the transport folder's name. Existing working
copy and recovery decisions keep their reviewed paths and protections. Unnumbered
copies retain their transport-derived destination until their identity is resolved.

### Save location and guided import

Ordinary instances reuse the active Settings **Project default save location**.
They keep their existing database and data directories; import does not require
a new library root or a database move. Missing or unavailable destinations block
source selection and direct the operator to Settings. Data/database directories
and redirected paths remain rejected. The import page has no destination editor.
Changing the future import destination does not move or rewrite existing projects.

Selecting one source automatically scans and reviews it. Ordinary files and
portable snapshots use the same chooser and server-reviewed tokens. A safe plan
executes immediately; saved-data restore uses the existing plan ID, fingerprint
and conflict protections. Manual path entry appears only after native-picker
failure. In-place linking remains available only through its compatible direct
route and is not advertised as a normal import choice.

Intake and restore plans bind the destination path and directory identity. A
changed/replaced destination invalidates old confirmations and unfinished batch
resumes. Recovery packets for an ordinary instance live beneath its existing
`data_dir/project_library/recovery`; explicit managed libraries retain
`Backups/Project Recovery`. Neither mode moves the database or grants public-drive
write authority.

Mixed UI results retain the original backend batch identities. File-only batch
recovery remains unchanged; snapshot failures are checked again before another
confirmation and do not repeat successful file intake. Individual member links
open each imported result. Mixed results return to the shared Projects list
without inventing a synthetic backend batch filter.

### Shared catalog

The **Projects** homepage is the shared catalog for registered test projects,
received project folders, and folders linked in place. One search covers LTR,
title, sample, test item, requestor and folder path. The default **All Projects**
view also includes materials that are not ready for testing; **Files Only** is an
explicit filter. **Import Projects** is the sole visible receiving entry. **Recycle**
is the single retained-record entry, combining deleted (`trash`) and conflict-retained
(`history`) records. Rows show **Deleted** or **Retained after conflict**, the recorded
reason, and their original identity. Both offer read-only details and **Restore**.
The existing state values, preview tokens, blockers and replacement decisions remain
unchanged; no database records or files are migrated. Conflicting active records
retained during a restore appear in the same Recycle list. **Keep as retained record**
preserves the existing restore-to-history choice without exposing another list.
A partial source failure leaves available records visible with Retry. Duplicate
responses for the same internal ID use the latest revision; equal LTRs never combine
independent records.

A received member combines with a registered row only through its explicit
`project_id`. Its folder and mutable title remain searchable, but the registered
project row does not expose a separate **Project Files** disclosure. File access
uses the active project's normal folder action. Linked and unclaimed member IDs
stay namespaced. Matching names, paths or LTRs never merge records or authorize writes.
Read-only retained-registry checks prevent a trashed workspace from reappearing
through its folder entry. If those checks fail, uncertain workspace entries wait
for retry; independently available records remain visible with a warning.

Import results return to the full `/projects` catalog without applying a batch
filter. Explicit older batch links remain compatible. Searches/pages persist
across detail and import navigation. Old `/project-library` and `/projects?view=legacy` URLs render the
same homepage; existing member detail URLs remain compatible. This is a frontend
composition of existing read APIs, with no database/schema migration.

Import Projects receives one selected project into the configured project folder.
Changing the selected folder invalidates its reviewed plan; cancelling the native
picker preserves the current reviewed selection. A safe selection executes only
after the server has returned its bound plan and fingerprint. The old Legacy list
and direct linking URLs remain compatible, but no longer add choices to the common
import page. File opening, location changes and test continuation remain in their
corresponding project details.

All-project and individual receiving-batch views retain separate session search
and page state. New batches start unfiltered. Member links carry the batch in the
URL so a reload or Back to Library returns to that same view. Import opened from
the library also retains this return context through the optional linking flow.
An already-added result opens its existing member without claiming membership in
the new batch; View Added Projects refers only to newly received members. Empty
search results offer Clear Search without suggesting another import is needed.

Duplicate previews offer **Open Existing Project** only when the existing
identity/material checks return a verified member ID. This optional response
field is navigation metadata outside the saved intake plan; it does not change
fingerprints, selections or conflict rules. Conflicts and unregistered targets do
not expose that link. An all-duplicate preview explains that no copies are needed;
a mixed preview still receives only explicitly selected new projects.

## Existing and new boundaries

The existing `legacy_project_records` registry remains an in-place browsing
facility. A library member records managed-file membership and may later link to
an ordinary business Project. These records do not replace Project lifecycle,
LTR ownership, confirmed Matrix authority, or the existing Workbench.

Receiving a copy and selecting the active working copy are separate decisions.
`Keep Separate` must not silently redirect the existing Project's output paths.
Known projects retain their identity; unstructured material requires explicit
takeover and later confirmation through the existing business workflow.

The template has an outer workspace containing the business directory and its
sibling `Source Book`. Intake preserves that complete boundary and custom
subdirectories. Other historical layouts remain admissible and can be reviewed.

## Responsibilities

| Module | Responsibility |
|---|---|
| `backend/domain/project_library.py` | Library errors and stable public contracts |
| `backend/application/project_library/` | Review, intake, title/location and takeover orchestration |
| `backend/infrastructure/project_library/files.py` | Bounded filesystem inspection, owned staging, review plans and file operations |
| `backend/infrastructure/project_library/ownership.py` | Explicit project ownership, indirect/JSON references and typed row conversion |
| `backend/infrastructure/project_library/assets.py` | Referenced files outside the project, relative tokens and verified asset transfer |
| `backend/infrastructure/project_library/portability.py` | Versioned snapshot preparation, inspection and restoration |
| `backend/infrastructure/storage/models_project_library.py` and repository | Membership and durable batch state, independent of business lifecycle |
| `backend/api/routes_project_library.py` and schemas | Typed transport and dependency composition |
| `frontend/src/features/project-library/` | Import, list, member details and portable-restore user flows |

The UI uses the typed API module. It does not decide database ownership or copy
files itself. Restore uses declared table and field contracts; it does not accept
executable SQL or infer ownership solely from foreign-key traversal.

## Runtime and storage

`CONNLAB_LIBRARY_ROOT` selects an explicit library. Existing configuration and
environment overrides must be validated together so that a selected library does
not accidentally connect to a database outside it. Legacy default development and
packaged paths remain compatible when no library is selected.

Root selection is a startup binding, not a hot database switch during an API
request. Development, tests and migration rehearsals use separate roots. The
configured external-resource registry continues to identify public LTR workbooks,
templates and public-drive locations; portable project data does not grant the
target computer permission to write those resources.

A selected library has a version/database binding marker and an OS-owned writer
lease. An incompatible binding or another writer process must fail before the
database is opened for application work. Legacy configurations without a selected
library retain their existing startup paths; selecting a new root does not move
old data or change formal configuration automatically.

Library listing and search inspect identity, location and pending-action metadata;
they do not hash every project's material or export its complete data graph.
The list reports **Not Checked** rather than claiming a verified current snapshot.
Member details and **Prepare to Take** still perform full freshness checks.
A renamed, missing or ambiguous inner business directory must produce a location
review action before continuation; a valid outer marker alone is insufficient.

## Portable data contract

The snapshot is held under the project's `.connlab/portable` area, with a format
version, source signature, creation time, coverage and integrity evidence. A
directory identity manifest alone is insufficient to recover test data.

The project aggregate includes Project/Basic/Application/Sample data, intake
lineage, source/draft/confirmed Matrix histories and their cyclic references,
measurement plans and point profiles, schedule/fee revisions, existing LLCR
datasets, report preparation decisions and retained output lineage.

Identifiers remain stable when restoring into a new target. Storage-local
autoincrement identities require special treatment rather than overwriting
another project's row. All required relationships are validated, including
references encoded in JSON or string fields without SQL foreign keys.

Project-external report evidence, report working-draft files and other files
referenced by persistent records must be collected explicitly. Path tokens bind
them to project-relative or target-data-relative locations. Historical missing
references remain visible; original paths must not become live target bindings.

Acknowledged migration-source material gaps travel in the signed
`operation_history` as `migration_source_gaps` version 1. The record binds the
project, source key and reviewed fingerprint, with stable gap IDs and descriptions;
it is provenance only and explicitly non-replayable. Descriptions never become
file locations, repair commands or target write permission. Inspection, member
status and subsequent native snapshot preparation derive visible reminders from
this history, including retained recovery packets. Repeated preparation deduplicates
the same facts without adding timestamps or creating false freshness changes.
Malformed/unsupported records, conflicting gap identities and a damaged inherited
snapshot stop preparation/restoration rather than being silently discarded.
Ordinary project-file changes are still handled as freshness/missing-reference
observations; validating inherited snapshot structure does not require those
ordinary files to remain unchanged.

Local credentials, sessions, machine profiles and unrelated projects are excluded.
Process-local customer-report jobs and source process IDs are not restorable
execution state. Persistently referenced completed outputs are retained through
their owning records. Completed approval decisions may be retained only as
non-replayable provenance; source approvals do not authorize new target writes.

## Recovery and conflicts

Review tokens bind source evidence, intended target and target revisions. File
intake stages and verifies owned copies before registration, without overwriting
an existing destination. Batch identity must be available to the client before
the initial submission so a lost response can be recovered idempotently.

Snapshot preparation must not publish partially written metadata. Restoration
checks format, integrity, source-file changes, missing dependencies and existing
target identities before applying records and paths. Same-LTR/different-identity,
divergent revisions and unrelated primary-key collisions require explicit review.
Source-machine pending journals cannot be replayed against target-machine paths.

For an existing target, a conflict requires a new reviewed plan with an explicit
resolution. A same-identity replacement must retain a complete target recovery
point before switching the working copy. That recovery point includes the target
data graph and external assets as well as its ordinary files. A different identity
using the same LTR may be retained as history without acquiring current LTR
ownership through the separate retained-record workflow, but the common import flow
does not offer that as an alternative to replacement. It permits replacement only
for the verified same Project identity; otherwise the operator cancels the import.
History remains searchable and browsable, including location recovery; it does not
become an editable working project merely by being received.

The plan binds the source signature and target revision. Changing a resolution or
changing either side requires review again. Neither modification time nor a
matching LTR is permission to merge fields, discard history or overwrite a copy.
Interrupted operations must leave an explicit recoverable state rather than
reporting a partially applied copy as complete.

## Acceptance boundaries

The intended operator sequence is:

1. In Projects, choose **Import Projects**, then **Choose Project Folder**.
   The default UI checks exactly one complete project boundary, never recursively
   expands a parent into a batch, and replaces rather than appends a new selection.
   An LTR root and an LTR-prefixed business folder are valid inputs. Parent folders,
   individual files and known project subfolders receive contextual guidance.
   Identity metadata is read before asking for an LTR. Only an unidentified manual
   project can receive a user-supplied existing LTR; existing ConnLab identity cannot
   be overridden. The reviewed number, layout and conflicts are bound into the
   ordinary intake plan. A single **Confirm Import** performs the copy; preview
   alone does not copy or register the project. Destination remains the Settings
   **Project default save location**. Original files and folders are preserved.
2. In **Projects**, search by LTR or title, open the project details and use **Open Folder** for ordinary
   Windows file work. **Manage** provides file refresh, **Edit Title** and
   **Locate Folder** when a directory was moved or renamed.
3. Use **Continue Testing** to review takeover before entering the existing
   Project Workbench. Receiving documents alone does not confirm test authority.
4. Before changing computers, use **Prepare to Take** and **Confirm Snapshot**.
   Check that the saved data is current, then copy the complete project root.
5. On the other computer, choose the complete project root through the same import
   entry. Saved ConnLab data automatically takes the existing restoration path.
   If the stable Project identity already exists with different saved data, choose
   **Replace Existing Project** or **Cancel Import**. Replacement creates a complete
   recovery copy before switching; the LTR alone never enables it. Review missing
   dependencies. A missing snapshot is never silently treated as a successful data
   restoration; newer formats remain blocked. Files-only intake still requires an
   explicit choice where offered.

**More Options** retains **Link Folders Without Copying** for in-place registration.
Backend batch discovery/intake and recovered batch results remain compatible; the
default chooser does not expose batch selection, boundary-splitting or loose-file
assignment controls. Restoring saved data and receiving ordinary files preserve
their existing independent protections. A successful eligible single project opens
its verified workspace; a retained/ineligible project opens details. **Import More**
starts a clean selection; returning to Projects does not add an import-batch filter.
Errors and unfinished/review results
remain visible. Reopening with a successful saved batch keeps the fresh chooser
available and puts the previous result under **Last Import**.

An old manual folder without a snapshot remains a valid material-intake source.
Recovering structured test data from an old database requires the compatible
database-copy rehearsal path; it cannot be inferred from a directory name.

The task requires at least 300 isolated projects, interruption and retry tests,
mutable-title and everyday-file-edit tests, and an A/B restore with the source
paths unavailable. Each declared data family needs nonempty evidence. Restored
Matrix editing, LLCR values/units and report preparation must be checked through
their existing public interfaces; a successful response or file count is not
proof of full recovery.

Same-machine isolated A/B testing is not a claim of physical dual-computer testing.
The final migration package must identify supported versions, source-data defects,
conflict decisions, backup and rollback steps, and actual unverified items.
