# Basic project folder creation, phase one

Scope: basic directory creation and source archive, directory identity/availability, and durable
public associations. No independent Generate files workflow, public automatic rename, release or
real public-drive test is included. Existing year resolution and append/skip public file protections
remain unchanged.

## User behavior and authority

Create folder requires a registered full LTR, legal generated folder name, an existing usable save
root and an editable Project. It does not read Matrix/Fee/Basic Information confirmation as a
prerequisite and never resolves an Office template. It creates the LTR workspace, Source Book,
identity metadata and existing structural E-mail/Submitted Material/Photos/Test results subfolders.
It archives available mail/application/attachments using the established material classification.
Each missing/unreadable source, different existing target or individual copy failure is reported
without blocking other materials. Ambiguous request-email sources are skipped for review.

A persisted same-project directory is reused even after product/test descriptions change. Missing
structural subfolders are repaired without changing existing content. A missing/replaced linked
business folder is not silently recreated. An unlinked same-name candidate requires explicit
ownership confirmation; a conflicting manifest, unsupported manifest schema, different project/LTR,
redirected path or changed directory identity refuses creation. No basic action moves, rebuilds,
renames or replaces an existing business file. A new request scans newly available materials;
replaying the same request ID returns the original operation.

The basic manifest and SQLite association commit **before** optional archive copies. Therefore a
completed operation with archive issues still exposes a usable local directory independently of
generated-output completeness. Closed projects remain openable through validated associations but
cannot create/rebind/sync. Existing Submit content checks remain strict.

## Interfaces and ownership

- `GET /api/projects/{id}/official-workspace/basic/preview`: status, directory availability,
  server-derived target, expected context, blockers and retained operation ID.
- `POST .../basic/create`: expected context, request ID, optional explicit existing-folder
  confirmation. No raw target path is accepted as authority.
- `POST .../basic/resume`: exact retained operation ID.
- `GET /api/projects/{id}/public-folder-workflow/binding/preview`: bound/review-required/blocked,
  full LTR/year, old/proposed paths, server candidate tokens and whether creation may be confirmed.
- `POST .../binding/confirm`: expected context and one server candidate token, or `create` only
  when no exact candidate exists. The request commits the association before any later file sync.

`BasicProjectWorkspaceService` coordinates basic identity/recovery; its infrastructure publisher
owns exclusive staged directory publication, manifest publication and owned material staging.
`PublicFolderBinding` owns explicit destination selection and saved identity validation. Public
workflow continues to own file-level previews, append/skip decisions, Submit/Pull and audit rows.

New work uses `data_dir/basic_project_workspace`; its journal uses the existing checksum/envelope
and the canonical `project_folder_generation` OS lock. Basic create/resume own that lock in service;
the automatic registry guard exempts only those exact routes from taking it twice. Registry-state
checks remain. Ordinary retained writers reject unfinished basic operations; basic operations reject
unfinished legacy generation/report delivery. Project-library moves/snapshots reject pending basic
operations. No legacy journal is converted or treated as permission for new behavior.

## Public identity and compatibility

The binding stores version, project ID, normalized **complete** LTR, configured root, resolved year,
Open/Closed location, actual path and stable directory/year identities. A valid saved binding wins
over a changed local description. There is no fuzzy match or automatic rename.

When a binding needs review, enumerate only immediate children of the resolved Open year and parse
the complete first LTR token. `DL-2026-09-002` never matches `DL-2026-09-002A`. Zero candidates allow
explicit project-child creation; one candidate still requires confirmation; multiple candidates
require an explicit choice. Failed/incomplete enumeration never means zero candidates. Config/root,
year or identity changes require review. Parent Open/Closed/year directories are never created.
Upload checks Open/year only; Submit checks Closed/year. A pending approved Submit is a recovery
case and keeps upload blocked until the retained move is resolved.

The old sync execute API remains compatible only with the **current** confirmed matching preview:
zero candidates additionally need directory-creation confirmation; one candidate additionally needs
existing-folder confirmation and must equal the exact proposed path. Its preview binds complete
enumeration/absence and identities. It then commits the binding and refreshes file preview before
copying. Persisted preferences/history never supply approval, and invalid saved bindings never use
this adapter. Description-different or multiple candidates use the new explicit binding endpoint.

Existing unmanaged files remain unmanaged. A confirmed rebind may rebase this project's managed-file
paths only when the old and selected directory identities prove the **same directory**. Selecting
a different directory never transfers file ownership. Extra public files are retained; differing
files remain skipped for review under the prior partial-sync policy.

## Migration and portable copies

SQLite adds `creation_kind` (old rows default `template`), makes template origin nullable for basic
records, and adds public-state `binding_json`. Existing rows, keys and indexes are retained. An
explicit SQLite transaction begins before DDL so an interruption rolls back the staging table and
the original schema/data remain retryable. Unsupported schema or a preexisting staging-name
collision fails closed; migration never deletes an arbitrary staging table.

Version-1 template manifests remain supported; basic manifests use version 2 with explicit basic
kind and null template origin. Unknown schema versions refuse writes. Portable export/restore
preserves null basic origin and exports completed basic journal history as provenance, never a
replayable operation. Imported public bindings require fresh confirmation even if copied absolute
paths happen to exist. They are hints, not granted upload permission.

Code rollback is **not** database downgrade. An old binary may require a non-null template origin
and cannot safely read a database containing basic rows. Keep the pre-upgrade database backup and
business-folder copies for operational rollback; do not fabricate a template path or delete rows
to make an old executable start. No downgrade is performed by this batch.

## Interruption behavior

Before publication, directory intents retain their staged filesystem identity. Resume validates the
current registered LTR, configured root, lifecycle and every completed directory identity before
new effects, manifest, association and material writes. Changed inputs/path ownership stop recovery
while preserving files. Manifest or association failure retains the operation; no substitute folder
is guessed. Ordinary material issues complete with an issues list; identity/journal/path failures
remain blocking. A source-copy failure removes only its just-created identity-proven partial stage;
cleanup failure stops recovery instead of exposing it as a syncable business file.

Public binding is committed even for an empty folder and before any partial copy. If directory
creation succeeds but its database commit fails, the physical directory remains and the next
review discovers it as an existing candidate; no second description-derived folder is created.

Submit commits an exact move intent before moving Open to Closed. If move succeeds but final
metadata commit fails, a fresh session can preview/confirm completion of metadata only when the
expected Closed directory has the exact retained identity, the Open source is absent, and the
reviewed Closed year identity still matches. A changed/missing/both-present pair stops recovery.
Pending Submit blocks uploads. Successful completion records the actual Closed association and
retains the existing sync lock and Pull behavior.

## Isolated acceptance and validation

All automated file/database effects use pytest temporary roots or this worktree's `tmp`; live app
configuration, project folders and real public shares are excluded. Focused tests exercise:

1. Creation without Matrix/Fee/Basic Information/templates; second-session association visibility
   before archive; independent missing/conflicting material handling; a new click archives later files.
2. Linked-directory reuse/manual-byte retention, existing-folder confirmation, racing directory
   refusal, manifest interruption/resume and root/full-LTR drift refusal.
3. Schema/index/data preservation, transactional migration fault/retry, null-origin portability
   and imported-binding review.
4. Exact base/suffix candidates, unique/multiple review, inaccessible enumeration, missing year,
   saved path stability and stale/raw client-path refusal.
5. Empty binding commit before files, partial copy with cross-session binding visibility,
   same-directory explicit rebind, and Submit move/DB interruption across fresh API sessions.
6. Canonical writer collision, unfinished basic versus old writer rejection, and real HTTP resume.

Developer evidence is retained under `tmp/phase1-*.log`. Independent review/QA and local integration
are parent-task stages and must report their actual pinned commit/results; this document does not
claim those stages have passed. Existing legacy generation/API/portability suites form the affected
compatibility matrix. Windows path-capacity tests must use a short pytest temporary root; a long
app-managed worktree prefix is not evidence of a product path-regression.

Developer execution on this batch: the short-root affected run produced 192 passing tests and one
old open-service fixture failure (it omitted the newly explicit validated-availability flag).
That fixture now declares availability, and a new test rejects an existing path whose availability
is explicitly false. The corrected open slice passed 5 tests; the retained generation/publisher
slice passed 28 tests. Final basic/API/open validation passed 18 tests, including the additional
draft-only-LTR refusal regression. These focused follow-ups cover the final changed behavior without
claiming another full matrix run. The single Starlette/httpx deprecation warning is preexisting.
