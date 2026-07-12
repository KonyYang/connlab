# TASK_361G Contact Measurement Schema CHECK Compatibility Bootstrap Corrective Plan

## Status

Complete / Integrator accepted on 2026-07-13. Developer implementation/fix passes,
Reviewer implementation re-gates, QA disposable legacy SQLite startup/API smoke,
and controlled Integrator package isolation passed. Remote push was intentionally
not performed. TASK_361E remains paused_by_user.

## Discovery Gate

### Current Phase / Active Task / Role / Why Allowed

- Phase: Phase 11 controlled Matrix foundation.
- Active task: TASK_361G complete/accepted.
- Role: Integrator packaging/readiness closeout.
- TASK_361F is accepted at `983633b7`; its four-index correction is complete.
- TASK_361E remains paused by explicit user instruction.
- Controlled operational evidence proves a distinct pre-index CHECK compatibility
  blocker without any database content/metadata change.
- Reviewer implementation blockers are closed, QA passed, and the package is limited
  to the TASK_361G migration CHECK compatibility bootstrap corrective.

### Confirmed By User

- The real existing DB lacks three target-snapshot and two impact CHECK constraints.
- Startup fails before index bootstrap; Matrix session and read-only Test Record
  preview return `500`.
- The controlled smoke preserved DB hash/size/mtime and six authority row counts, and
  skipped Cancel/Delete and generation POST operations.
- The next lane must be independent, planned-only, non-destructive, idempotent, and
  must not touch the real DB or TASK_361D/E/frontend/consumers.

### Confirmed By Repository Evidence

- The accepted TASK_361F migration currently rejects missing named CHECKs before
  foreign-key/expression/index compatibility work.
- It later compares canonical CHECK expressions exactly and then performs TASK_361F
  semantic-index bootstrap.
- Fresh authority ORM tables define the five required expressions, but SQLite has no
  supported `ALTER TABLE ADD CHECK` path for an existing table.
- The operational QA evidence records empty authority tables, absent CHECK names,
  unchanged DB fingerprint/metadata/counts, and blocked read-only endpoints.

### Inferred By Planner

- Table rebuild would physically add CHECKs but violates the user's safety boundary.
- Exact table-CHECK semantic recognition plus canonical guard triggers is the minimum
  non-destructive equivalent enforcement for old tables.
- Arbitrary logical-equivalence inference is unsafe; only canonical exact predicates
  are accepted. Unknown shapes remain fail-closed.
- CHECK and TASK_361F index bootstrap should be planned as one atomic schema
  transaction after all row/schema preflights, preserving no-partial-success.

### Not Yet Confirmed

None that blocks Reviewer plan review. Exact trigger names/SQL and transaction helper
layout are frozen by the task and remain Reviewer technical scrutiny, not user-facing
product decisions.

## Compatibility Design

Classify each required semantic as:

- exact table CHECK (compatible regardless name);
- exact canonical guard triggers (compatible fallback for old tables);
- absent (eligible for guard bootstrap only after row preflight);
- incompatible/ambiguous (fail-closed).

For target snapshots, use `trg_cmp_target_checks_insert_v1` and
`trg_cmp_target_checks_update_v1`; the update trigger is limited to the four anchor
columns plus `stable_target_key`. For impacts, use
`trg_cmp_impact_checks_insert_v1` and `trg_cmp_impact_checks_update_v1`; the update
trigger is limited to `impact_subject_key` and `impact_identity_key`. Each pair
combines its table's required predicates and uses a stable
`RAISE(ABORT, 'authority_corrupt: ... CHECK compatibility guard rejected row')`
message. Before DDL, evaluate exact predicates against all existing rows and validate
non-index table/column/FK/non-null shape. Reinspect exact trigger SQL after creation.
Do not rewrite table DDL or data.

The current TASK_361F index classification/preflight remains behaviorally frozen.
Implementation planning must ensure all CHECK and index preflights occur before any
DDL and all missing guard/index objects are created in one contained transaction.

## API And Runtime Boundary

No route, DTO, dependency, or frontend change is planned. Existing `init_db()` invokes
the repaired migration. Temporary integration tests use Matrix session GET and
read-only confirmed Test Record preview GET only as startup probes. Cancel/Delete and
generation POST semantics are outside this lane.

## May Touch / Must Not Touch / Locked Paths

The task file is authoritative. Future work is limited to the existing authority
migration, focused temporary schema/startup tests, and governance. Real databases,
table rebuild/data repair, models/repositories/lifecycle/API/client/frontend,
TASK_361D/E, Fee/formal workbook/generic Test Record/Report semantics, parser/import,
LTR/public drive, release/settings, and external residuals remain locked.

## Validation Gate

1. Disposable old-schema fixtures with missing/mixed/alternate CHECK shapes.
2. Populated valid/invalid row preflight and exact before/after preservation.
3. Canonical INSERT/UPDATE guard enforcement and idempotent repeat startup.
4. Atomic rollback/lock behavior with TASK_361F indexes still absent on failure.
5. Fresh DB and TASK_361B/F lifecycle/schema/startup regressions.
6. Temporary Matrix session/read-only Test Record startup probes.
7. Compile, diff/trailing, line-count, whitelist/forbidden, no-real-path, and package
   isolation scans.

## Dependencies And Ordering

1. TASK_361B-D and TASK_361F remain accepted baselines.
2. TASK_361G is the current planned corrective and must be accepted before another
   operational smoke or any TASK_361E resume decision.
3. TASK_361E remains paused and cannot inherit TASK_361G authorization or package
   changes.

## Definition Of Ready

Satisfied and closed for TASK_361G. No blockers remain for this corrective lane.
TASK_361E remains paused and cannot inherit this authorization.

---

## Developer Planning-First Refinement

### Current Phase / Authorization Boundary

- Phase: Phase 11 controlled Matrix foundation.
- Active task: `TASK_361G_CONTACT_MEASUREMENT_SCHEMA_CHECK_COMPATIBILITY_BOOTSTRAP_CORRECTIVE`.
- This pass is docs-only. It does not authorize migration, tests, API, routes,
  real-database access, or an operational smoke.
- `TASK_361F` remains the accepted index-bootstrap baseline. `TASK_361E` remains
  `paused_by_user` and cannot absorb this repair.

### Exact Semantic Registry

Implementation must represent each physical/compatibility semantic independently,
even though the canonical triggers enforce them in target and impact pairs.

| Key | Table | Required canonical table-CHECK expression | Canonical guard pair |
|---|---|---|---|
| `target_group_anchor_xor` | `measurement_plan_target_snapshots` | `(source_group_snapshot_id IS NOT NULL AND length(trim(source_group_snapshot_id)) > 0 AND manual_group_anchor_id IS NULL) OR (source_group_snapshot_id IS NULL AND manual_group_anchor_id IS NOT NULL AND length(trim(manual_group_anchor_id)) > 0)` | target INSERT/UPDATE |
| `target_row_anchor_xor` | `measurement_plan_target_snapshots` | `(source_row_snapshot_id IS NOT NULL AND length(trim(source_row_snapshot_id)) > 0 AND manual_row_anchor_id IS NULL) OR (source_row_snapshot_id IS NULL AND manual_row_anchor_id IS NOT NULL AND length(trim(manual_row_anchor_id)) > 0)` | target INSERT/UPDATE |
| `target_key_prefix` | `measurement_plan_target_snapshots` | `stable_target_key LIKE 'cmp-target:v1|%'` | target INSERT/UPDATE |
| `impact_subject_prefix` | `measurement_plan_impacts` | `impact_subject_key LIKE 'cmp-target:v1|%' OR impact_subject_key LIKE 'cmp-candidate:v1|%'` | impact INSERT/UPDATE |
| `impact_identity_prefix` | `measurement_plan_impacts` | `impact_identity_key LIKE 'cmp-impact:v1|%'` | impact INSERT/UPDATE |

`_canonical_sql` may normalize keyword case, identifier quoting, whitespace, and one
or more outer parentheses. It must retain quoted literals, operators, nested
parentheses, and `AND`/`OR` grouping. A table CHECK is compatible only when its
canonical expression equals one individual registry expression. A combined,
weaker, stronger, reordered-grouping, unknown, or same-name-wrong expression is
`authority_corrupt`; implementation must not infer logical equivalence.

### Frozen Canonical Trigger SQL Contract

The future migration owns exactly four trigger names. It must build SQL from the
following canonical bodies, normalize the stored `sqlite_master.sql`, and require
exact equality after creation. `IS NOT 1` intentionally rejects `FALSE` and `NULL`
so legacy indeterminate values cannot pass by SQL three-valued logic.

```sql
CREATE TRIGGER trg_cmp_target_checks_insert_v1
BEFORE INSERT ON measurement_plan_target_snapshots
FOR EACH ROW WHEN (
  ((NEW.source_group_snapshot_id IS NOT NULL AND length(trim(NEW.source_group_snapshot_id)) > 0 AND NEW.manual_group_anchor_id IS NULL)
   OR (NEW.source_group_snapshot_id IS NULL AND NEW.manual_group_anchor_id IS NOT NULL AND length(trim(NEW.manual_group_anchor_id)) > 0))
  AND ((NEW.source_row_snapshot_id IS NOT NULL AND length(trim(NEW.source_row_snapshot_id)) > 0 AND NEW.manual_row_anchor_id IS NULL)
       OR (NEW.source_row_snapshot_id IS NULL AND NEW.manual_row_anchor_id IS NOT NULL AND length(trim(NEW.manual_row_anchor_id)) > 0))
  AND NEW.stable_target_key LIKE 'cmp-target:v1|%'
) IS NOT 1
BEGIN
  SELECT RAISE(ABORT, 'authority_corrupt: target CHECK compatibility guard rejected row');
END;

CREATE TRIGGER trg_cmp_target_checks_update_v1
BEFORE UPDATE OF source_group_snapshot_id, manual_group_anchor_id,
  source_row_snapshot_id, manual_row_anchor_id, stable_target_key
ON measurement_plan_target_snapshots
FOR EACH ROW WHEN (
  ((NEW.source_group_snapshot_id IS NOT NULL AND length(trim(NEW.source_group_snapshot_id)) > 0 AND NEW.manual_group_anchor_id IS NULL)
   OR (NEW.source_group_snapshot_id IS NULL AND NEW.manual_group_anchor_id IS NOT NULL AND length(trim(NEW.manual_group_anchor_id)) > 0))
  AND ((NEW.source_row_snapshot_id IS NOT NULL AND length(trim(NEW.source_row_snapshot_id)) > 0 AND NEW.manual_row_anchor_id IS NULL)
       OR (NEW.source_row_snapshot_id IS NULL AND NEW.manual_row_anchor_id IS NOT NULL AND length(trim(NEW.manual_row_anchor_id)) > 0))
  AND NEW.stable_target_key LIKE 'cmp-target:v1|%'
) IS NOT 1
BEGIN
  SELECT RAISE(ABORT, 'authority_corrupt: target CHECK compatibility guard rejected row');
END;

CREATE TRIGGER trg_cmp_impact_checks_insert_v1
BEFORE INSERT ON measurement_plan_impacts
FOR EACH ROW WHEN (
  (NEW.impact_subject_key LIKE 'cmp-target:v1|%' OR NEW.impact_subject_key LIKE 'cmp-candidate:v1|%')
  AND NEW.impact_identity_key LIKE 'cmp-impact:v1|%'
) IS NOT 1
BEGIN
  SELECT RAISE(ABORT, 'authority_corrupt: impact CHECK compatibility guard rejected row');
END;

CREATE TRIGGER trg_cmp_impact_checks_update_v1
BEFORE UPDATE OF impact_subject_key, impact_identity_key
ON measurement_plan_impacts
FOR EACH ROW WHEN (
  (NEW.impact_subject_key LIKE 'cmp-target:v1|%' OR NEW.impact_subject_key LIKE 'cmp-candidate:v1|%')
  AND NEW.impact_identity_key LIKE 'cmp-impact:v1|%'
) IS NOT 1
BEGIN
  SELECT RAISE(ABORT, 'authority_corrupt: impact CHECK compatibility guard rejected row');
END;
```

An exact physical CHECK satisfies its individual semantic. If every semantic for a
table is physical-CHECK compatible, its trigger pair is not required. If one or more
semantics are absent, an exact canonical trigger pair may satisfy the remaining
compatibility enforcement, including already-physical predicates. A same-name wrong
trigger is `authority_corrupt`; an unknown alternate trigger is neither removed nor
accepted as authority proof.

### Future Migration Sequence

1. Retain TASK_361F's table/column/non-null/FK validation and exact index semantic
   classification as read-only baseline behavior.
2. Inspect `get_check_constraints()` and `sqlite_master` for all five individual
   expressions. Classify every semantic as physical, missing, or corrupt. Inspect
   the four frozen trigger names and classify canonical, absent, or corrupt.
3. Before every DDL statement, preflight all rows for missing CHECK semantics using
   `WHERE (<exact table predicate>) IS NOT 1`. The target query evaluates the three
   target predicates independently and the impact query evaluates the two impact
   predicates independently. A false or NULL result is `authority_corrupt` and
   leaves triggers and TASK_361F indexes untouched.
4. In the same pre-DDL phase, run the unchanged TASK_361F missing-index duplicate
   and NULL preflights. If either CHECK or index preflight fails, no DDL occurs.
5. Open one explicit SQLite `BEGIN IMMEDIATE` transaction only after all schema,
   CHECK, trigger, row, and index preflights pass. Re-read classifications inside the
   transaction to account for another writer's completed bootstrap.
6. Create only absent canonical trigger pairs and only still-missing TASK_361F
   indexes. Reinspect exact trigger SQL, CHECK/trigger compatibility, and all four
   index semantics before commit.
7. Any DDL/read-verify exception rolls back all new triggers and indexes. A lock or
   busy `BEGIN IMMEDIATE` returns one concise startup error with no fallback. A
   repeated startup sees the exact guards/indexes and performs no DDL.

The implementation must preserve the current migration under the Python hard limit
of 500 lines. It may reorganize focused functions inside the same authorized module,
but may not create an unreviewed helper module or alter `database.py` call order.

### Exact Future Package

| Path | Future responsibility |
|---|---|
| `backend/infrastructure/storage/contact_measurement_plan_authority_schema_migration.py` | CHECK/trigger semantic registry, row preflight, shared atomic bootstrap, exact revalidation. |
| `tests/unit/test_contact_measurement_plan_schema.py` | Fresh-schema and wrong-shape regression extensions. |
| `tests/integration/test_contact_measurement_plan_schema_check_compatibility_startup.py` | Disposable old-schema fixtures, trigger enforcement, atomicity/idempotency/lock and startup probes. |
| `tests/integration/test_matrix_editor_session_api.py` | Only a narrow temporary old-schema Matrix session GET assertion if not clear in the focused module. |
| `tests/integration/test_matrix_editor_test_record_generation_api.py` | Only a narrow temporary old-schema read-only confirmed Test Record preview GET assertion if not clear in the focused module. |
| TASK_361G plan/evidence/board | Lane governance only. |

No new dependency, schema/model/repository/lifecycle/API/client/frontend file is
planned. `database.py`, all real databases and files, TASK_361D, paused TASK_361E,
Fee, generic Test Record/Report semantics, parser, LTR/public-drive, Settings,
release, `.agents/**`, `docs/project_management/**`, and external residuals remain
locked.

### Test And Validation Contract

- Unit/temp SQLite: exact alternate-name CHECKs; all-five missing; each missing;
  mixed physical-CHECK/canonical-trigger states; same-name wrong trigger; combined
  or grouping-changed CHECK; invalid/NULL existing target or impact rows; zero-DLL
  preflight failure; DDL rollback; repeated startup and locked writer.
- Trigger regression: invalid INSERT and the exact covered UPDATE columns abort with
  the frozen message; valid target/impact writes expected by TASK_361B lifecycle
  tests still succeed; unrelated-column updates are not intercepted by these guards.
- Preservation: compare six authority row counts and values plus every non-approved
  `sqlite_master` object before/after. Only the four listed triggers and accepted
  TASK_361F indexes may be added.
- Startup probes: disposable old-schema fixture only, `GET /matrix-editor/session`
  and read-only confirmed Test Record preview GET. Do not call Cancel/Delete,
  generate/download, or any real document route.
- Final gate: focused pytest suites, `py_compile`, migration/test line counts,
  `git diff --check`, UTF-8 trailing-whitespace, whitelist/forbidden/no-real-path
  scans, and exact dirty-worktree isolation. Browser or real-db smoke is out of
  scope; QA may later perform a separately authorized disposable smoke.

### Planning-First Risks

- SQL canonicalization that removes nested grouping would accept a semantically
  distinct CHECK or trigger. Exact token structure is the safety boundary.
- A trigger pair that omits `IS NOT 1` can allow NULL/unknown legacy values. The
  frozen SQL must retain it in every trigger and row preflight.
- Creating guards before all TASK_361F index preflights can leave partial schema
  success. The shared transaction ordering is non-negotiable.
- The operational incident is evidence only. No planning or later Developer test may
  reconnect to `data/connlab.sqlite3` or an operator path.
