# TASK_361F Contact Measurement Schema Compatibility Bootstrap Corrective Plan

## Status

Complete / Integrator accepted on 2026-07-13. Developer implementation, Reviewer
implementation re-gates, QA disposable startup/API smoke, and controlled Integrator
package isolation passed. Remote push was intentionally not performed. TASK_361E
remains paused.

## Discovery Gate

### Current Phase / Active Task / Role / Why Allowed

- Phase: Phase 11 controlled Matrix foundation.
- Active task: TASK_361F complete/accepted.
- Role: Integrator packaging/readiness closeout.
- TASK_361B-D are accepted. TASK_361E is paused by explicit user instruction so a
  production startup defect cannot be mixed into formal consumer migration.
- Reviewer implementation blocking findings are closed, QA passed, and the package
  is limited to the TASK_361F migration compatibility bootstrap corrective.

### Confirmed By User

- Matrix Editor Test Record and Cancel fail with Internal Server Error, while Matrix
  session GET returns `500`.
- Traceback ownership is `init_db()` -> Contact Measurement Plan authority schema
  migration -> missing required indexes.
- The existing database lacks four expected authority unique-index names.
- The corrective must preserve all Measurement Plan data and constraints, be
  non-destructive and repeatable, use only disposable databases for validation, and
  stay separate from TASK_361D/E and frontend/consumer behavior.

### Confirmed By Repository Evidence

- `database.init_db()` imports the authority models, executes
  `Base.metadata.create_all()`, then calls the authority schema migration.
- The migration currently validates required index names before validating exact
  unique/partial shapes and raises when any required name is absent.
- The migration does not create missing indexes or recognize an equivalent index
  under another name.
- TASK_361B's accepted schema defines two revision partial unique indexes plus target
  and impact full unique constraints, and its tests cover fresh creation and
  wrong-shape rejection but not an otherwise compatible existing database missing
  these indexes.
- Dependency construction invokes `init_db()`, so one global migration exception can
  break Matrix Editor endpoints before their business services run.

### Inferred By Planner

- `create_all()` cannot evolve indexes on an already existing table; the safe repair
  belongs in the dedicated SQLite migration, not API routes or consumers.
- Exact semantic-index recognition avoids unnecessary duplicate DDL for compatible
  SQLite autoindexes/alternate names. Canonical creation is appropriate only where
  no equivalent enforcement exists and duplicate preflight succeeds.
- All conflict checks should complete before any index is created so an incompatible
  database cannot be left partially changed.

### Not Yet Confirmed

None that blocks plan review. The exact historical process that created the affected
database is not required for V1 because the compatibility fixture is defined by its
observable schema/data state and the repair is semantic and idempotent.

## Planned Design

Introduce a small semantic index specification inside the existing migration module.
For each required invariant, inspect SQLite `PRAGMA index_list`, `index_info`, and
`sqlite_master.sql`; canonicalize predicates using the existing SQL normalizer.

The migration sequence is:

1. reject non-index table/column/CHECK/FK incompatibility;
2. classify each required index as canonical, exact-equivalent, absent, or corrupt;
3. preflight duplicate keys for every absent semantic index;
4. if any conflict exists, fail before DDL;
5. transactionally create only absent canonical indexes;
6. re-run exact semantic validation;
7. return without touching authority rows.

Name-only presence is never enough, but exact semantics may be accepted under an
alternate SQLite-owned name. Wrong same-name shape remains corrupt and is not dropped
or replaced. No table rebuild or data repair belongs to this lane.

## API And Runtime Boundary

No API contract or route changes are needed. Existing dependency construction and
`init_db()` call the repaired migration. Disposable integration tests prove Matrix
session, draft cancel, and Test Record requests pass startup after compatibility
bootstrap; they do not change those endpoint semantics.

## May Touch / Must Not Touch / Locked Paths

The task file's exact path list is authoritative. V1 is limited to the authority
schema migration plus focused temporary-database tests and governance. `database.py`,
authority models/repositories/lifecycle, API/client/frontend, TASK_361D/E, Fee/Test
Record behavior, real databases/files, parser, LTR/public drive, release/settings,
and external residuals remain locked unless a later Planner/Reviewer scope re-gate
explicitly changes that boundary.

## Validation Gate

1. Build repo-controlled disposable SQLite fixtures representing valid existing
   authority data with missing/alternate indexes.
2. Assert semantic bootstrap/recognition, repeated no-op startup, exact indexes, and
   complete preservation of authority rows and non-index schema.
3. Assert duplicates and malformed shapes fail before any DDL/data change.
4. Re-run fresh TASK_361B schema tests and focused authority regressions.
5. Run Matrix Editor session/draft-cancel/Test Record startup API regressions against
   temporary databases only.
6. Run compile, diff/trailing, line-count, whitelist/forbidden, dependency, and
   no-real-path scans.

## Merge And Package Isolation

Complete. The accepted package contains only the approved migration/test/governance
files, QA used temporary databases, and Integrator package isolation excluded the
paused TASK_361E package, TASK_361D, frontend/API client, Fee/Test Record behavior,
authority model/repository/lifecycle changes, real data, parser/MCR, TASK_360Q/R/S,
superpowers plans, release/settings, and all unrelated residuals.

## Dependencies And Ordering

1. TASK_361B-D remain accepted prerequisites and regression baselines.
2. TASK_361F is the current corrective lane and must complete before TASK_361E may be
   reconsidered.
3. TASK_361E remains paused and requires an explicit later user resume decision; it
   cannot inherit TASK_361F authorization or package changes.

## Definition Of Ready

Satisfied and closed for TASK_361F. No blockers remain for this corrective lane.
TASK_361E remains paused and cannot inherit this authorization.

---

## Developer Planning-First Refinement

### Verified Runtime Boundary

`init_db()` imports registered models, calls `Base.metadata.create_all()`, then calls
`migrate_contact_measurement_plan_authority_schema(engine)`. The corrective must stay
inside that existing SQLite migration. `database.py` is read-only evidence: no call
order change is authorized. The migration runs after fresh-table registration but
must safely bootstrap indexes on an existing table because `create_all()` does not
evolve existing SQLite index objects.

### Four Exact Semantic Invariants

The implementation must represent these as structured specifications, not name-only
sets. Every candidate index is inspected through `PRAGMA index_list`, `index_info` or
`index_xinfo`, and `sqlite_master.sql`:

| Invariant | Table | Exact ordered columns | Unique/predicate/null semantics |
|---|---|---|---|
| confirmed revision per root | `measurement_plan_revisions` | `measurement_plan_root_id` | `UNIQUE`, partial `WHERE state = 'confirmed'`; rows outside predicate and NULL root values are not covered by SQLite partial uniqueness. Canonical model root id is non-null. |
| editable revision per root | `measurement_plan_revisions` | `measurement_plan_root_id` | `UNIQUE`, partial `WHERE state IN ('draft', 'needs_review')`; same partial/NULL coverage rule. |
| target identity | `measurement_plan_target_snapshots` | `measurement_plan_revision_id`, `stable_target_key` | full `UNIQUE`, no predicate. Both ORM columns are non-null, so SQLite NULL-distinctness must not be used as an equivalent substitute. |
| editable impact identity | `measurement_plan_impacts` | `editable_revision_id`, `impact_identity_key` | full `UNIQUE`, no predicate. Both ORM columns are non-null; NULL-permitting variants are incompatible. |

An alternate index name, including a SQLite-generated name, is acceptable only if its
unique flag, exact column order, partial/full kind, canonical predicate, and practical
NULL coverage are semantically identical. A same-name or alternate-name index with a
wrong unique flag, column set/order, predicate, or NULL-permitting replacement is
`authority_corrupt`, never a replace/delete candidate.

### Existing-Database Bootstrap Algorithm

1. Use the existing non-index table/column/CHECK/FK validation first. Any failure is
   `authority_corrupt`; do not create indexes or alter data.
2. Classify all four semantic specifications before DDL as `canonical`,
   `equivalent`, `absent`, or `incompatible`. No index name alone is decisive.
3. For every `absent` invariant, run duplicate preflight with exact columns and its
   predicate before opening DDL. A partial invariant checks only rows matching its
   canonical predicate. A full invariant checks all rows and treats prohibited NULL
   values as incompatibility rather than SQLite's distinct-NULL loophole.
4. If any duplicate, null-semantic conflict, or incompatible index exists, raise a
   readable `authority_corrupt` error before every DDL statement. Preserve rows and
   all schema objects.
5. In one `engine.begin()` transaction, create only the absent canonical unique
   indexes with stable canonical names. Use no table rebuild, no drop/replace, no
   column/constraint alteration, and no data repair.
6. Re-run full semantic recognition inside the transaction after DDL. Commit only if
   every invariant is canonical or equivalent. A DDL exception rolls back every newly
   created index; a second `init_db()` is then idempotent and creates none.

The migration must treat DDL failure after a subset of `CREATE UNIQUE INDEX` calls as
a transaction rollback event. It may not continue, retry with different semantics,
or leave a partial bootstrap accepted. SQLite serialization protects one writer; test
coverage must exercise repeated startup and two independently opened temporary-engine
calls to establish deterministic idempotency, while treating lock/busy errors as
readable startup failures with no semantic fallback.

### Compatibility and Regression Scope

- A temporary existing-database fixture starts from valid authority tables/data plus
  all-four-missing indexes. It must boot with exactly the four semantic invariants
  afterward, preserving all rows and non-index `sqlite_master` SQL.
- Additional fixtures cover each independently missing invariant, exact equivalent
  alternate names, preflight duplicates, same-name wrong shape, non-index malformed
  CHECK/FK/table schema, partial predicate extra conjunct/disjunction, wrong ordered
  columns, and prohibited nullable identity variants.
- Matrix Editor session GET, draft Cancel, and current Test Record API regressions run
  through `init_db()` only against disposable database paths. They prove startup no
  longer masks existing endpoint semantics; they do not change Matrix/Test Record
  behavior or response contracts.
- No test opens, copies, or points at `data/connlab.sqlite3`. No table rebuild,
  delete, repair, backfill, migration of real data, or TASK_361E resumption occurs.

### Exact Future Package

May Touch remains only the authority schema migration, the current focused schema
tests, one narrow temp-SQLite compatibility integration module if needed, the two
existing temporary Matrix-session/Test-Record API regression files, and TASK_361F
governance/evidence. Models, repositories, lifecycle, commands, API/client/frontend,
TASK_361D, paused TASK_361E, Fee, generic Test Record semantics, Report, parser,
LTR/public-drive, real databases/files, `.agents/**`, and
`docs/project_management/**` stay locked. New helper modules are not planned; retain
clear functions below AGENTS line limits in the existing migration module or stop for
scope reconciliation.
