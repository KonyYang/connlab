# Legacy project registration

## Approved outcome and boundaries

Tools > Import Legacy Projects registers selected historical folders so operators can search and
browse them in Projects > Legacy. Original paths, files and directory structures remain unchanged.
No remote publication, real business database edits during development/validation, copying,
normalization of source names, source manifests, Office automation, LTR registration, Matrix recovery,
or business lifecycle creation is part of this task.

`legacy_project_records` is an additive, independent table. A legacy registration has a generated UUID,
the original folder name, old number/evidence, an internal legacy source-ID hint, original resolved
path and normalized unique key, identification notes, timestamps and revision. It is not a `projects`
row and cannot enter the Workbench or business project writes. Existing tables/rows retain their
authority and behavior.

## Operator flow

1. Choose up to 20 locations, Start Preview, review folder boundaries and select candidates.
2. Check Registration compares the complete preview batch with historical and business records,
   including Trash/History, LTR numbers and generated/workspace/public-workflow local locations.
3. Already Added folders cannot be selected. Conflicting number/evidence/source-ID hints default to
   unselected; explicit Keep Separate enables an independent historical record. Overlapping project
   boundaries require a new preview instead of Keep Separate. Missing numbers are allowed.
4. Import Selected shows one confirmation with the selected count. Confirm Import writes only
   local registration rows. Results show added/already added/needs review/failed items; recheck and
   retry remaining items safely. Registration supports up to 1,000 projects per batch.
5. View Imported Projects opens Projects > Legacy. Search old number evidence, folder name or path;
   Browse opens `/legacy-projects/{record_id}`. Search text survives the return to the Legacy list.
6. Open Folder uses the backend-stored, revalidated location and Windows Explorer. Change Location
   changes only the registration link with an expected revision. Offline folders keep searchable
   registration details and can be reconnected later.

## Implementation seams and risks

- Read-only preview/picker handlers still have no database/settings dependency. Separate plan/import
  handlers intentionally depend on the local database.
- Application service owns eligibility, fingerprints, selection/conflicts, search, browse and
  relocation rules. Repository owns persistence and SQLite `BEGIN IMMEDIATE` check/write transactions.
  Filesystem and Explorer work remain behind existing infrastructure gateways.
- Plan fingerprints cover current directory identity, all recognized number evidence, source-ID hint,
  notes, batch conflicts and current matching registration revisions. Import rereads under the write
  transaction. Stale checks return needs review; successful retries become Already Added.
- Unique normalized paths and serialized checks prevent double-click/two-connection duplication.
  Current physical identity is cached only within a check, never stored as permanent inode ownership.
- Source folders are untrusted inputs; redirected paths are rejected. No file content is executed.
  A single unreadable/missing project does not block valid projects in the same batch.
- A folder can disappear after registration; no availability requirement is imposed on record reads.
  Source files must be accessible on this workstation before import (cross-machine transfer is out of scope).

## Acceptance and developer evidence

Public service/API and accessible component seams cover 320 unstructured/no-number folders,
idempotent retry, concurrent registration, explicit Keep Separate, all number/source hints,
formal active/trash/history ownership, stale metadata/revision, mixed missing items, retained search,
fake Explorer opening, location changes and additive bootstrap with old row preservation. Original
read-only preview and picker cancellation protection are retained.

TDD RED: new registration service missing (pytest collection failed); preview test could not find
Check Registration while the two existing cancellation/fallback tests passed; new list/browser
components were absent. GREEN: affected backend tests passed after implementation (24 tests, 6.63s
before the final retained-workspace/relocation additions); affected frontend tests passed (27 tests).
Final developer backend check: 26 passed, one existing Starlette TestClient deprecation warning,
8.08s. TypeScript `tsc -b` passed. Final exact-state narrow checks are recorded in the handoff; independent
review, complete QA, isolated UI and real sample inventory verification follow the developer commit.

No real service on ports 5173/8000 or real business database was used during development. All writes
in developer tests use disposable SQLite stores and disposable directories; Explorer is replaced by
a fake launcher.
