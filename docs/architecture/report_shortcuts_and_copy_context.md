# Report shortcuts and current Workbench copy context

Report shortcuts are ordinary material-library metadata, independent of generated report,
Matrix, approval and lifecycle authority. `library_report_shortcuts` stores only a stable
catalog key, role (`internal` / `customer`) and root-relative file path. It is explicitly
excluded from the legacy project portable aggregate, with no new export or restore capability.

Exact catalog entries retain their identities even when a member and native project share
`project_id` but own different roots. A missing member navigation key resolves to the catalog's
represented project alias. Display numbers and filenames never merge identities. Setting a
shortcut resolves and stats the selected file only; there is no hashing, inventory, document
parsing, version tracking or file mutation. Replacement compares the expected current pointer
and requires explicit confirmation. First set and removal are direct metadata operations.
The same file can serve both roles. Root relocation and same-path edits/replacement retain
the association and refresh modified time. Missing files/roots retain a removable pointer;
no substitute or latest report is selected. Incoming receipts and file copies never inherit
shortcut metadata.

The compact Common reports group exists only when at least one pointer exists. Links reuse
the ordinary safe open API. Each pointer remains removable when unavailable; missing-file
reselection reviews old/new paths, and missing-root location uses the existing material detail
flow. Selected-file More actions set, replace or remove these ordinary shortcuts.

Copy destinations come only from the actual Workbench route context. Sidebar last-project
memory remains separate. Workbench to Library carries RAM context; Projects list, Settings,
other areas and direct Library boot clear it. Source selection in Library cannot choose or
change the destination. The dialog shows the target number, name and registered directory
before its explicit destination preview and copy confirmation; it has no target selector.

The server issues an opaque per-browser session and token. Context activation/clear carries
a strictly increasing client intent. Clear (including failed activation) invalidates old tokens
before resolving a new target; out-of-order requests cannot revive them. The in-process registry
is bounded to 512 sessions and expires inactive contexts after 12 hours. Reload/server restart
requires returning through a Workbench. Registry summaries supply the existing active/non-temporary
Workbench eligibility rule; reviewed imported identity remains eligible without inventing an LTR.
Activation, preview and confirmation recheck eligibility and the registered root's physical identity.

Copy preview and confirmation require explicit context proof; the old target-key-only write DTO
is intentionally rejected. Every copy batch retry, including generic receipt history retry,
rechecks the same live context and saved plan. Completed historical results remain readable by
GET without mutation. History shows copy retry only for its original still-live context.
Context switching is serialized against publication under a context lock, then library/project
locks: an already-authorized in-flight write completes before the server acknowledges the clear,
and subsequent preview/confirm/retry cannot use the old token. The destination never changes
mid-operation. Browser responses from an obsolete context are discarded.

Validation uses isolated files and databases. Developer coverage includes shortcut aliases and
distinct roots, metadata-only set/replace/remove, missing paths, same-path changes, no hash or
inventory calls, safe open/reselect, no inheritance, portable exclusion, cold schema registration,
mandatory copy proof, monotonic clear, cross-session isolation, ordered clear/publication, actual
registry temporary rejection/imported acceptance, stale previews, generic retry guarding, and
route/UI response races. Independent QA owns the complete matrix and real connected browser path.


## Compact operation guidance

The browsing header and managed location describe the source, never the copy destination.
A separate compact line shows either the live Workbench number/name/registered path or how
to establish that context. Selecting a folder navigates it; only selecting a file enables file
operations. The selected-file line shows its root-relative path. Without a Workbench target,
Open file and Open containing folder remain available while Copy is disabled with guidance.
Changing/clearing context invalidates prior destination checks, confirmations and retry controls;
no new approval dialog is added. Server checks remain authoritative at execution.

The library summarizes missing registered locations separately from unassociated projects.
The location view retains the registered path and offers Refresh after access is restored;
it does not offer automatic relocation or reconstruction. Existing legacy relocation APIs are
not advertised as current-page controls. Search rules and ordinary receipt/copy protection stay
unchanged. This round does not integrate Tools, restoration, synchronization or backup.


## Validation and remaining OS coverage — 2026-11-18

UI guidance changes were checked in an isolated worktree through public component operations,
then through real Vite (5228) -> Uvicorn (8848) -> a dedicated SQLite and A/B file directories.
No product backend, search rules or context protocol changed. Validation evidence is retained
under `tmp/library-status-hints-20261118` in the primary repository:

- Frontend: six affected files, 40 tests passed. The final all-unavailable empty-state correction
  reran the affected 12 page tests; 41 unique tests passed across those runs. Final TypeScript/Vite
  production build passed. React act warnings remain in the logs.
- Backend safety regression: 73 passed, four skipped. Real connected API checks made 22 requests,
  observing supplementary publication, repeat skip, retained manual A contents, changed B source
  rejection, target-only request rejection and stale confirm/retry rejection after switch/clear.
- Browser: entering A Workbench then browsing B kept A's number/name/registered directory;
  confirmed a real supplementary copy; returning through **Back to projects** cleared the target;
  selecting a file still allowed ordinary open but disabled Copy. The sidebar Projects action may
  resume the last Workbench; it is not itself proof of reaching the project list.
- The unavailable-location summary and explicit unassociated-project search were checked separately.
  1280-wide and 595-wide views retained wrapping/readable paths and actions, with no measured
  horizontal overflow in the new status/path lines. Screenshots and `browser-results.json` remain.

The four skipped nodes are:

| Isolated test | OS behavior still unverified on this host |
| --- | --- |
| `test_overlap_and_redirected_sources_cannot_be_received` | Whole-folder receipt rejects a redirected source descendant. |
| `test_selected_copy_rejects_reparse_source_and_destination` | Selected copy rejects a file symlink and redirected destination directory. |
| `test_redirected_report_path_is_rejected` | A redirected report cannot become a shortcut. |
| `test_redirected_files_are_not_scanned_or_opened` | Search/browse exclude redirected children and open rejects traversal through them. |

`symlink-gap-audit.json` records the exact pytest nodes and independent creation probes. Both
file and directory probes failed before the behavior assertions with **WinError 1314: required
privilege not held**. This reproduces the earlier four library skips; it is distinct from the
three skipped workspace-folder tests in the previous directory-rule task. No security setting
or privilege was changed. Ordinary path/context/file protections passed, but these actual
OS symlink branches must not be reported as passed or inferred from ordinary-file tests.

The first environment check exposed an unset receipt-root default and was stopped. Its diagnostic
SQLite is retained separately. All final validation used the fresh `library-safe/Data/ui-safe.sqlite3`
with an explicitly seeded `library-safe/Received` root; Projects, templates, configuration, logs and
all A/B file operations were isolated. A first connected script assertion compared Windows newline
bytes incorrectly after the safety checks; the test-only expectation was corrected and the connected
checks rerun successfully. These setup/test issues did not change product code or authorize any
business-file mutation. Retained import/portable code was neither cleaned up nor extended.
