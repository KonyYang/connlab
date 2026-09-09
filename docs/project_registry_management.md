# Project closure and recoverable removal

## Scope and authority

This change runs locally in ConnLab. It provides a compact project-close flow,
recoverable removal, conflict-aware restore, retained history, and exclusion from
normal project lists, counts, selectors, and work queues. It does not implement
permanent deletion, duplicate-create prompts, or migration of LTR ownership.

The immutable internal `project_id` identifies a record. A displayed DL number is
a business identity and may be shared by distinct historical or mistaken records.
Removal and restore must never use the displayed number as a database record key.

Business lifecycle and registry location are independent. Registry locations are
normal (`active`), recycle bin (`trash`), and retained history (`history`). Moving a
record does not change its lifecycle, Matrix, schedule, fee versions, outputs,
LTR records or ownership, source materials, external paths, or external files.

## Closing and reopening

- The operator explicitly selects Completed, Cancelled, Cannot continue testing,
  or Other. Other requires a nonblank note; the other categories allow no note.
- Existing Failed and Duplicate closure reasons remain readable. A test failing
  its acceptance requirement is not itself an incomplete project.
- Missing/stale/failed output records appear as a collapsible reminder, not a new
  completion gate. No automatic claim of successful testing is made.
- Failed submissions keep the entered reason and note. Repeated submissions are
  prevented. Dialog focus, Escape, keyboard navigation and narrow screens work.
- Reopening a closed project is distinct from restoring a removed project.
  Restoring a closed record preserves its closed business state.

## Recycle bin and retained history

The project list exposes a row management action and separate Recycle bin and
Retained history locations. The ordinary All view excludes both hidden locations.
Removal previews the exact record, related-data summary and retention boundary.
Removal records the actor, time and reason without deleting project data.

Restore previews all normally visible records with the same resolved business
identity. The operator may restore to the normal area if there are no conflicts,
restore only to history, or explicitly retain the conflicting current records in
history and restore the selected record. Cancel changes nothing. History records
may use the same conflict-aware restore flow to return to the normal area.

Every submit revalidates its preview identity and affected records. Changes since
preview cause a conflict response. All affected state transitions and their audit
events succeed atomically or leave all records unchanged. No record content is
overwritten and no LTR ownership is implicitly transferred.

## Access, concurrency and scope of removal

Normal lists and selectors exclude hidden records. Read-only inspection and audit
retain access to their real identities and references. Cleanup audit must inspect
all locations so that retained LTR links are not misreported as orphans.

Hidden records cannot accept normal business writes, including requests from old
tabs or indirect draft/case/revision identifiers. Management restore is an explicit
exception. Pending/running file generation blocks removal; its existing locking
and execution checks must prevent a check-then-write race with removal or restore.

External public-drive directories, source files, Word/Excel templates, and LTR
workbooks are outside the remove/restore scope. Their existence is described in
the confirmation instead of treated as authorization to delete or update them.

## Acceptance and validation

Use synthetic projects and an isolated SQLite database, never real projects, for
mutation tests. The required acceptance scenarios are:

1. Common close reasons permit no note; Other rejects blank notes without changing
   state. Missing reason cannot be submitted. Legacy reasons remain readable.
2. Remove A, then create B with the same displayed DL number. Cancelled restore
   changes neither. Explicit replacement restores A and retains B in history.
   Restoring only to history leaves B current. Both internal IDs and contents stay
   intact, and B can subsequently request restore.
3. Multiple conflicts are displayed and revalidated; stale previews and races never
   produce partial transitions or silently replace an unacknowledged record.
4. Hidden records leave normal lists/counts/selectors/queues and reject ordinary
   writes. Restored records return according to their original lifecycle.
5. LTR ownership, Matrix/fee authority, source files, generated files and external
   paths remain unchanged. Cleanup audit preserves correct reference attribution.
6. Background generation and removal are mutually exclusive. Errors keep recoverable
   project state and the operator's dialog input.
7. The shared close and registry dialogs work with keyboard and a narrow viewport.

Developer feedback uses affected public-seam tests. An independent review precedes
the final Python/frontend/build gate and isolated browser verification. Integration
checks the exact reviewed tree and evidence; no GitHub push is part of delivery.
