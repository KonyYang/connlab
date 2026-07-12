# TASK_361B Contact Measurement Plan Authority Backend Developer Evidence

Status: developer_planning_first_complete
Task: `TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND`
Lane: `contact-measurement-plan-authority-backend`
Date: 2026-07-12
Role: Developer

## Gate

Developer planning-first only. No schema, migration, backend service, API route, config, test, frontend, API-client, workbook, or real-file implementation changed.

Current phase: Phase 11, Project Workbench / Matrix / Approval Package controlled foundation.
Current active task: `TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND`.
Why allowed: TASK_361A is complete/accepted, Reviewer B1/B2 plan re-gate evidence is `reviewer_pass`, and the user explicitly authorized this documentation-only Developer planning-first pass.

## Source-Of-Truth Note

`docs/task_board.md` still says the Reviewer B1/B2 re-gate is pending, while the current TASK_361B Reviewer evidence records the re-gate as passed. This is a governance wording residual. It does not authorize implementation; this pass remains docs-only under the user's explicit planning-first approval. Planner must reconcile the board before any implementation authorization.

## Implementation-Readiness Decisions

1. The six additive tables and their SQLite types, foreign keys, checks, unique indexes, partial indexes, and migration order are now exact in the plan.
2. `impact_subject_key` and `impact_identity_key` are non-null canonical fields. SQLite refresh uses unique `(editable_revision_id, impact_identity_key)` plus insert/read/verify, with literal `none` evidence sentinels and `authority_corrupt` rollback on same-key divergence.
3. Target Group and Row source-lineage/manual-anchor axes each require XOR. Every `cmp-target:v1` value is rebuilt and compared byte-for-byte on write and read; corruption blocks the independent authority and cannot trigger legacy fallback once a root exists.
4. Bootstrap is lazy, per Project, active-confirmed-only, provenance-idempotent, partial-run recoverable, transactional, and non-destructive. Root-exists authority corruption blocks rather than silently reverting to legacy JSON.
5. `draft` / `needs_review` / `confirmed` / `superseded` lifecycle, pure impact classifier, partial-compatible effective projection, stale fingerprints, and typed route/DTO shapes are bounded to backend foundation scope.
6. The only rollback flag is `Settings.contact_measurement_plan_authority_enabled`, loaded from the strict environment variable and injected by `backend/api/dependencies.py`. Disabled reads select the read-only legacy adapter; disabled writes are blocked before mutation.

## Future Package And Tests

The exact future modules, config/dependency registration, migration order, no-consumer boundary, file size split, test names, temporary SQLite migration/bootstrap/recovery coverage, API stale/disabled cases, and package-isolation checks are recorded in the plan. TASK_361C, TASK_361D, and TASK_361E remain downstream and are not authorized by this pass.

## Planning Validation

- Read AGENTS, board, task, TASK_361A accepted contract/evidence, TASK_361B Planner and Reviewer evidence, Matrix authority models/revision flow, existing contact-plan storage/migration, confirmed consumers, Settings, dependencies, and current worktree status.
- Updated only `docs/task_361b_contact_measurement_plan_authority_backend_plan.md` and this Developer evidence.
- Product code, schema/migration, API, tests, API client, and real files remain untouched.
- Per-file `git diff --no-index --check` passed with only existing LF/CRLF working-copy warnings; trailing-whitespace scan returned no matches.
- Targeted status confirms current backend parser/test changes, board documentation, and other TASK artifacts are external residuals, excluded from this planning pass.

## Stop Point

Recommended next role: Reviewer implementation-readiness gate.

Blocking summary: none for Developer planning-first. Product implementation remains unauthorized pending Reviewer readiness, Planner source-of-truth reconciliation, and explicit user implementation approval.

## Developer Implementation Checkpoint: 2026-07-12

Status: ready_for_review / implementation complete pending Reviewer implementation gate.

- Added backend-only authority identity, six-table registration, strict env flag,
  repository, lazy confirmed-Matrix bootstrap, revision lifecycle, pure impact
  classification, projection boundary, typed FastAPI routes, and dependency/main
  wiring. No frontend, API-client, Fee/workbook consumer, Matrix parser, LTR, or
  real-file path was changed.
- Temporary-SQLite integration coverage now proves legacy confirmed contact-plan
  bootstrap creates root/revision/target/family snapshots, same-provenance reruns
  are idempotent, partial rows recover only for the same payload, divergent payload
  and root-without-authority states block as `authority_corrupt`, and stale/confirm/
  supersede transactions preserve the active revision until a valid confirmation.
- The typed route suite covers summary/workspace/effective projection, opening a
  draft, save, impact refresh, compatible acceptance, explicit inclusion update,
  custom-family replacement with derived readings, confirmation, feature-disabled
  write blocking, and route registration.
- Validation: `py -m pytest` focused TASK_361B suite: `27 passed`; targeted
  `py_compile` passed; `git diff --check` passed with existing LF/CRLF warnings
  only; trailing-whitespace scan found no matches. External parser/test, board,
  and other residuals remain excluded.

Completion additions: the reviewed partial unique revision indexes now enforce one
confirmed and one editable revision per root; confirmation supersedes and flushes
the old authority before promoting the draft in the same savepoint. Existing SQLite
partial-table inspection blocks incompatible authority tables. A real confirmed
Matrix supersession regression proves impact persistence, unresolved-review confirm
blocking, and compatible-target projection without legacy fallback.

Recommended next role: Reviewer implementation gate.

Blocking summary: none known for the Developer implementation package. Existing
parser/test, board, Settings/LTR, release, and other external worktree residuals
remain excluded and were not cleaned, staged, committed, or pushed.

## Reviewer B3-B6 Fix Pass: 2026-07-12

- Added canonical `cmp-candidate:v1` subjects for new/unmatched Matrix candidates;
  persisted impacts retain `stable_target_key = null` for those candidates and
  dedupe through the non-null candidate subject plus impact identity. Rebind now
  accepts the candidate subject rather than overloading a target key.
- Existing-db migration inspection now validates required columns, named checks,
  unique/partial indexes, and rejects incompatible authority shape. ORM checks
  enforce target and impact canonical key prefixes.
- Recorded the two narrow revision helper modules in the exact TASK_361B module
  split above. They are backend-only lifecycle helpers, not TASK_361C-E scope.
- Disabled authority writes now return HTTP `503` with
  `contact_measurement_plan_authority_disabled`.

Fix-pass validation: focused identity/classifier/schema/bootstrap/lifecycle/API
suite `15 passed`; no frontend, Fee/workbook consumer, parser, LTR, or real-file
scope was changed. Reviewer implementation re-gate is recommended after the full
focused suite and static checks complete.

## Reviewer B3R/B4R Fix Pass: 2026-07-12

- Candidate rebind now resolves the exact editable-revision `cmp-candidate:v1`
  review impact to `rebound`; repeated equal rebind is read-verified/idempotent and
  no longer blocks confirmation. The audit remains linked to the revision and
  candidate subject.
- Existing SQLite validation now reads actual foreign-key targets, table SQL CHECK
  expressions, unique/index metadata, and partial-index predicates. Any shape
  mismatch blocks with `authority_corrupt`; no existing table is guessed or rebuilt.

Focused candidate-rebind/supersession and schema regressions passed; no locked scope
was changed. Recommended next role: Reviewer implementation re-gate.

## Reviewer B3R2/B4R2 Fix Pass: 2026-07-12

- Rebind now recalculates the editable revision fingerprint after target replacement
  and candidate-impact resolution in the same transaction. The prior token is stale;
  repeated equal rebind is read-verified and the reloaded token is required to confirm.
- Migration validation now compares the exact SQLite FK local/referred columns and
  NO ACTION/NONE semantics, exact full unique index column sets, and partial index
  predicates in addition to canonical table CHECK fragments.

## Reviewer B4R3 Fix Pass: 2026-07-12

- Revision partial-index validation now requires `unique=1`, `partial=1`, the exact
  single indexed column `measurement_plan_root_id`, and canonical WHERE equality.
- Named CHECK validation compares normalized complete expressions rather than loose
  SQL fragments. Rebind fingerprint regression proves an old token is stale before
  the new reloaded token can confirm.

## Reviewer B4R4 Fix Pass: 2026-07-12

- Partial-index predicates now compare exact token-normalized WHERE expressions.
- CHECK normalization preserves nested boolean grouping and strips only an optional
  outer expression wrapper, preventing AND/OR grouping changes from passing.

## Reviewer B4R5 Tests-Only Fix Pass: 2026-07-12

- Added existing temporary-SQLite corruption regressions for a same-name partial
  index with an extra restrictive predicate and a persisted named CHECK with the
  same tokens but changed AND/OR grouping. Both re-enter `init_db()` and block as
  `authority_corrupt` without authority writes.
- Full focused TASK_361B suite: `29 passed`; py_compile and diff checks passed.
