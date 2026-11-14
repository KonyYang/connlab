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
