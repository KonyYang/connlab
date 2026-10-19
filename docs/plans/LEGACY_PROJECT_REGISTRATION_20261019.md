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

## Independent review and final acceptance

Executable subject: `3aa51f62a439647851a182c217a02388a5256164`.
Independent Planner, Developer, Reviewer, QA and Integrator contexts were used; browser operation
was performed by `/root` and its screenshots, DOM, isolated records and fake-opener log were
independently checked by QA. Review found one P2: public open/closed/target locations were missing
from ownership checks. The focused fix added all three paths; parameterized RED was 9 failures /
3 passes, then the affected Developer Python gate passed 38 tests. Final independent Standards and
Spec review has no unresolved findings.

- Final selected Python: 86 passed in the combined isolated run, plus the default-Settings test
  passed separately after removing conflicting QA path environment overrides: 87 selected behaviors.
- All 43 task-related frontend cases passed within both complete default-worker executions. Complete
  results were **1006 passed / 1 failed / 1 skipped** and **1005 passed / 2 failed / 1 skipped**.
  The existing temperature-navigation first test exceeded its 5-second timeout; the second run also
  had a following spy-count failure after that timeout. Its unchanged file passed all 8 tests alone.
  The activation `54b7f21d` frontend reproduced the same first-test timeout. That exported baseline
  additionally lacked a fee fixture; the retained fixture was added only to the Temp copy and its
  10 related tests passed separately. These findings do not make the complete frontend gate green.
- Corrected TypeScript project check passed (`qa-types-corrected.log`). The initial attempt combined
  incompatible build/tsBuildInfoFile flags and failed; it is retained, not cited as passing evidence.
  Vite production build passed with 195 modules, with its final distribution under Temp.
- Real samples: 36 projects; registration check classified 29 ready / 7 review. The 29 ready records
  registered, retries returned 29 Already Added, the 7 review records wrote nothing without Keep
  Separate, then registered independently after explicit confirmation. Search and all 36 details,
  fake opening, disconnected-folder browsing, reconnection and revision/ownership rejection passed.
  All 67 non-legacy tables in the isolated acceptance database retained their complete row hashes.
- UI at isolated `127.0.0.1:18769`: 3 disposable projects, 2 explicit Keep Separate choices, cancel
  then confirm, 3 Added, repeat check 3 Already Added / import disabled, Active empty and Legacy 3,
  search, details, fake Open Folder, same-ID Change Location and retained return search passed.
  At 1440x1000 and 514x900 there was no document horizontal overflow; table scrolling is local.
  Console warnings/errors were empty. The temporary browser and owned server were stopped.
- All 3,442 source inventory entries and 28 small metadata hashes match the pre-task baseline.
  Five other protected business/configuration files match their hashes, sizes and modification times.

### Ambient real-database exception

The real `data/connlab.sqlite3` hash and schema changed during development, before final QA.
Its `legacy_project_records` table exists with **zero rows**. Its modification time was 07:57:59 CST;
the preexisting port-8000 auto-reload worker restarted at 07:57:33, before QA began at 07:59:25.
This is consistent with reload followed by an existing request initializing the additive schema,
but timing is not an audit proof of the exact request. No test connection to the real service was
found; all registration test writes were isolated. There is no real-table row-hash baseline from
which to prove that all preexisting business rows are unchanged. **Do not claim that the real database
was untouched.** No real schema rollback or user-service shutdown was attempted. This exception and
the complete-frontend failures were disclosed to the User; functional acceptance has these limits.

Machine evidence and screenshots are in
`C:/Users/White/AppData/Local/Temp/connlab-legacy-registration-20261019`, especially
`qa-final-result.json`, `qa-api-acceptance-result.json`, `ui-root-result.json`,
`ui-legacy-list-desktop.png`, and the original/repeated/baseline test logs.
No push or publication occurred.
