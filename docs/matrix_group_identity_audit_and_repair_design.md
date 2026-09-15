# Matrix Group Identity — Read-only Audit and Repair Design

Status: TASK_MATRIX_GROUP_IDENTITY_B audit baseline (2026-09-16)

## Decision

Keep Confirmed Matrix authority history. It is immutable audit evidence and is already consumed by
the authority-history read model. Do not delete or rewrite confirmed revisions to simplify the UI.

Treat the following as separate concerns:

1. **Current editable draft integrity** — must block save, confirm, and export when Group identities
   collide or child records reference groups/rows outside the draft aggregate.
2. **Confirmed authority history** — retain every immutable revision; show only the current authority
   in the normal workflow and place revision history behind a collapsed details action.
3. **Legacy orphaned lineage** — repair only through a previewed, fingerprinted, transactional
   maintenance operation. Never repair operator data during ordinary startup.

No database row was changed during this audit.

## Evidence

### User-visible failure

The captured Matrix Editor showed `Group ids and keys must be unique.` after adding or moving groups.
The diagnostic log records repeated `live-xlsx-export` HTTP 422 responses at 10:44 while draft
autosaves returned 200. After the Matrix state was rebuilt, export returned 200 at 10:45. This is the
signature of an invalid edit-session payload reaching export validation, not of a query becoming slow
because many historical revisions exist.

TASK_MATRIX_GROUP_IDENTITY_A closed the active defect by assigning stable unique identities on
add/insert/duplicate, preserving identity on move, rejecting duplicate identities at draft and
confirmation seams, and blocking export while the session is invalid.

### Read-only database audit

The audit was run through `scripts/audit_matrix_identity.py`. SQLite files were opened with
`mode=ro` and `PRAGMA query_only=ON`.

| Database | Draft roots | Editable drafts | Confirmed revisions | Active authorities | Retained revisions | Duplicate Group identities | Multiple editable/active roots |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Development | 158 | 8 | 151 | 24 | 127 | 0 | 0 |
| Packaged user data | 35 | 4 | 31 | 10 | 21 | 0 | 0 |

The highest development revision counts are 38, 31, and 22 for three projects. The packaged database
maximum is 10. These counts are small relative to the stored Matrix rows/cells and do not explain the
interactive identity failure.

SQLite `PRAGMA foreign_key_check` did find legacy orphaned lineage:

- Development: 19 Step Quantity rows reference missing Draft Groups; all belong to superseded drafts.
- Packaged user data: 2 Step Quantity rows reference a missing Draft Group; both belong to one
  superseded draft.
- Development: 4 rows in one superseded Confirmed Matrix revision reference Draft Rows that no longer
  exist. The confirmed rows themselves retain their complete immutable content; the missing reference
  is lineage damage, not loss of the active authority content.

Affected project identifiers are intentionally recorded for a future repair preview:

- Step Quantity lineage: `53dbd6488b7b4b47bbfb55ca18374418`,
  `638bb45740f64a0085b2fa203c9d014c`, and packaged project
  `49b2353f2f284cbb866919f2a5c828c6`.
- Historical Confirmed Row lineage: `2cd4b0e7ff6f4df99448c9ffdd78629f`, revision 4.

## Root cause boundary

The current SQLite engine does not enable foreign-key enforcement for every application connection.
Schema declarations therefore document lineage but do not reliably prevent an invalid write.

There is also a structural mismatch:

- a confirmed version is immutable and copies the full Group/Row/Cell content;
- confirmed child rows nevertheless have foreign keys to child rows of an editable draft aggregate;
- replacing an editable draft deletes and recreates its Group/Row children.

An immutable snapshot must not depend for validity on mutable children. The root draft reference is
valid provenance, but confirmed `draft_group_id` and `draft_row_id` values should be retained as
lineage identifiers, not enforced foreign keys to mutable child tables.

Draft-only children are different: Step Quantity, duration, text override, and cell records must refer
to Group/Row children in the same current draft aggregate. This invariant should be checked in the
domain/application save interface and then enforced by SQLite.

## Proposed repair module

Use one deep maintenance module with two interfaces:

### `preview(database_fingerprint) -> RepairPreview`

Read-only. It returns:

- database SHA-256 and schema version;
- each finding with project, draft/revision, active-or-superseded status, affected row count, and
  proposed action;
- a classification of `safe-derived-cleanup`, `lineage-reconstruction-review`, or `no-action`;
- expected post-repair `foreign_key_check` result.

### `execute(preview_id, expected_database_fingerprint, operator_reason) -> RepairReceipt`

High-risk and intentionally separate from this task. It must:

1. acquire the application database maintenance lock;
2. verify the database fingerprint still matches the preview;
3. create a recoverable database backup and verify its hash;
4. execute only the actions contained in the accepted preview, in one transaction;
5. run Matrix invariants and `PRAGMA foreign_key_check` before commit;
6. retain an audit receipt with before/after counts and backup location;
7. restore the backup automatically if validation or commit fails.

No generic “repair all” or startup auto-delete action should exist.

## Repair policy

### Superseded Draft Step Quantity orphan

Proposed action: delete only the orphaned derived Step Quantity row after proving that:

- its draft is superseded;
- its Group no longer exists in that draft;
- no current draft or active confirmed projection consumes it;
- an immutable Confirmed Step Quantity copy, when applicable, remains untouched.

This is a previewable cleanup, not reconstruction.

### Confirmed Row missing mutable Draft Row lineage

Default action: no automatic mutation. The immutable Confirmed Row still contains the authoritative
test item and is not missing business content. Removing or rewriting a confirmed revision would damage
audit evidence; recreating a mutable draft child can also collide with later row ordering.

The schema migration should convert confirmed child-to-draft-child foreign keys into informational
lineage fields while keeping the confirmed snapshot immutable. A repair preview may optionally propose
a lineage tombstone only if a future audit requirement demands one.

### New writes

Before enabling SQLite foreign keys globally:

1. validate all Group/Row identities and all child references at the draft save interface;
2. preserve Group/Row IDs during reorder operations;
3. ensure aggregate replacement deletes draft children in dependency order;
4. remove the invalid confirmed-child-to-mutable-draft-child constraints through a transactional,
   compatibility-tested schema migration;
5. repair safe legacy draft orphans;
6. enable `PRAGMA foreign_keys=ON` on every application connection and fail startup if it is not active.

Enabling foreign keys before these steps would turn existing historical defects into runtime failures.

## History and UI policy

- Normal Matrix Editor and Project Workbench show only the active authority and one editable draft.
- Authority Change History remains available as a collapsed “View authority history” panel. It should
  show revision, timestamp, operator, and compact change summary; it is not an alternate editing path.
- Superseded draft roots are implementation lineage and should not be shown as user-selectable Matrix
  versions.
- Do not add a purge button for confirmed history. The observed revision volume is not a performance
  problem and deletion would reduce traceability.
- A later retention task may compact redundant derived draft children only after confirmed snapshots,
  repair receipts, and rollback rules are proven sufficient.

## Implementation sequence

1. **Completed in this task:** reusable read-only audit module and CLI; audit development and packaged
   databases; document repair and retention policy.
2. **Next high-risk task:** preview/execute repair workflow, schema migration, and connection-level
   foreign-key enforcement with backup/rollback tests. No UI execution button until preview and
   receipt contracts pass integration tests.
3. **Later standard task:** collapse Authority Change History in the UI and add operator-facing
   explanations; do not change persistence or retention.

## Acceptance criteria for the high-risk repair task

- Preview is deterministic and makes zero database/file changes.
- Execute refuses a stale fingerprint and never changes active authority content.
- Every mutation has a verified backup and durable receipt.
- Superseded draft orphans are removed only when classified safe.
- Confirmed revision count and content hashes remain unchanged.
- `PRAGMA foreign_key_check` is clean for enforced relationships.
- Add, insert, duplicate, move, autosave, confirm, reload, and export remain green in both development
  and packaged runtime paths.
