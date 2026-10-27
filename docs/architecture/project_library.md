# Unified project library and portable project data

Status: implementation and isolated acceptance in progress for
`TASK_UNIFIED_PROJECT_LIBRARY_20261027`. The task plan and current test evidence,
not this architecture note, determine completion. Production data migration is a
separate, explicitly authorized operation.

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

## Acceptance boundaries

The task requires at least 300 isolated projects, interruption and retry tests,
mutable-title and everyday-file-edit tests, and an A/B restore with the source
paths unavailable. Each declared data family needs nonempty evidence. Restored
Matrix editing, LLCR values/units and report preparation must be checked through
their existing public interfaces; a successful response or file count is not
proof of full recovery.

Same-machine isolated A/B testing is not a claim of physical dual-computer testing.
The final migration package must identify supported versions, source-data defects,
conflict decisions, backup and rollback steps, and actual unverified items.
