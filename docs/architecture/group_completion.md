# Manual group completion and descriptions

Matrix projection's Status row owns a manual completion checkbox and a free-text description for
each confirmed group. This is an operator note, separate from Matrix step descriptions and test
execution results. It does not change Matrix authority, registry ownership or project lifecycle.

## Write contract

`PUT /api/projects/{project_id}/group-completion/{group_key}` requires the active
`confirmed_matrix_id` and at least one of `completed` or `description`.

- Existing boolean-only callers remain valid. Omitting `description` preserves the last text;
  an empty string clears it. A nullable description supports migrated records. The limit is 2000
  characters. Missing changes, explicit null completion and longer descriptions are rejected.
- A checkbox change can save the group's dirty description atomically. It attests the current
  group's Matrix content and follows the existing completion timestamp behavior.
- A description-only save appends an event carrying the original applicable event's completion,
  completion timestamp, lineage, revision and content signature. If only a same-key uncertain event
  exists, that event's evidence is retained. Without prior evidence, it records an incomplete group
  against the current Matrix. Only the text and event recording identity/time change.
- Text edits cannot re-attest changed content, remove Needs review, or shorten the history window
  that detects a content change followed by a reversion. Date-only Matrix revisions retain their
  existing behavior. The current Matrix identity and lifecycle/registry write guard remain mandatory.

The UI uses a 16px checkbox and a two-row description field. Save appears only while the description
differs from its saved value; blur never saves. Requests disable editing until they settle. Errors
retain the draft for retry, read-only/hidden projects disable writes, and late responses from a
previous project or another Matrix cannot replace the displayed state.

## Persistence and old data

Descriptions use a nullable `TEXT` column on `group_completion_events`. The startup SQLite migration
adds only this column when absent and is idempotent; it never rebuilds the table or rewrites existing
completion evidence. New databases create the same nullable column directly.

Portable snapshots keep the existing event family and format version. Checksum and source signature
are validated against the original payload before missing description fields default to null in an
in-memory view. The exact event IDs missing that field are retained for legacy fingerprint matching:
only null descriptions on those events may be omitted when comparing with the old signature.
Non-null text, other current descriptions and newly appended events still make the snapshot stale.
Normalized rows flow into restore comparisons/insertion, allowing repeated restore of old snapshots.
Snapshots lacking the entire event family remain compatible only while the current event set is
empty. Source envelopes, signatures and files are never rewritten during inspection or restore.

## Verification and risks

Regression seams are the completion API/service, database startup, portable restore/status APIs and
the Matrix projection component. Acceptance includes independent description saves and clearing,
unchanged completion timestamps, changed/reverted/uncertain Matrix review protection, additive repeat
migration, old/current portable round trips, explicit UI Save, failed-save retry and stale responses.
Browser QA must measure the checkbox at 16px and check the dense table at narrow workstation widths.

This task authorizes no real business database migration or source-file changes. A production startup
will add the nullable column when explicitly run later. Existing append-only completion history keeps
its current last-write behavior; this change introduces no multi-user conflict protocol.
