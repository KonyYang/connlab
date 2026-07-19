# TASK_364C Reviewer Package-Boundary Gate

Date: 2026-07-19

Status: `reviewer_blocked`

## Blocking Findings

### B1: The baseline whitelist omits required `database.py` bootstrap ownership

`HEAD` `2dac189d9b45eb68382af216e8144c6140869a71` has no CR-coverage contract.
The worktree has one additional, unaccepted product hunk in
`backend/infrastructure/storage/database.py`: it adds
`contact_point_profile_cr_category_selections` to `profile_tables`.

That hunk is required by the seven-file candidate. Without it, the new SQLAlchemy
selection model remains in the generic `Base.metadata.create_all()` set and can be
created before `bootstrap_contact_point_profile_schema()` performs its dedicated
validation and `BEGIN IMMEDIATE` bootstrap. The proposed seven-product-file package
would therefore not preserve the stated fail-closed, transactional migration boundary.

Required Planner package-boundary fix:

- add this exact one-line `database.py` hunk to TASK_364C's May Touch/whitelist and
  ownership statistics; it must remain the sole allowed hunk in that mixed file;
- add an isolated-package `init_db()` assertion proving the selection table is excluded
  from generic `create_all()` and is created/read-verified only by the dedicated
  Point Profile bootstrap; and
- keep this a packaging correction only. Do not add R1 UI, SummaryCard, downstream
  consumer, or unrelated `database.py` changes.

### B2: The declared backend validation count is not reproducible from the exact test whitelist

The four named TASK_364C test files pass, but their actual command is:

```text
py -m pytest tests/unit/test_contact_point_profile_fingerprint.py \
  tests/unit/test_contact_point_profile_lifecycle.py \
  tests/unit/test_contact_point_profile_schema.py \
  tests/integration/test_contact_point_profile_api.py -q
```

Result: `31 passed`, not the planned `46 passed`. The source of the additional fifteen
tests is not enumerated by the package plan and cannot be inferred into this lane.
Also, no hunk-isolated frontend build/typecheck artifact exists yet; the current build
contains excluded R1 and SummaryCard worktree hunks.

Required Planner fix: replace the stale `46` expectation with the exact package command
and count, or explicitly enumerate any extra read-only compatibility modules. QA must
run the frontend build/typecheck from a hunk-isolated baseline package before any
Integrator action.

## Verified Candidate Facts

- The planned twelve candidate files match the visible authority/API/client/test hunks:
  seven listed product files, four focused tests, and exactly `11` additions in the
  five permitted `frontend/src/api/client.ts` type symbols/fields.
- The candidate core is internally coherent: the composite selection FK is bound to a
  category snapshot in the same revision; confirmation persists custom selections in
  the revision transaction; V3 fingerprinting includes mode and selected identities;
  the read projection returns effective ids for `follow_llcr`; and the route/client
  DTOs carry the same direct-confirm and response contract.
- Scoped `git diff --check` and UTF-8 trailing-whitespace checks passed with only the
  repository LF/CRLF notices. The index is empty. R1 selectors/model/editor/CSS,
  SummaryCard, TASK_363C/D, TASK_365A/B/C, Fee/workbook/generic outputs, parser/LTR,
  and real-data/file paths were not included in this review package.

## Initial Gate Route (Superseded)

The initial route was **Planner docs-only package-boundary fix**. That route completed
with the B1/B2 correction reviewed below. TASK_364B remained Integrator blocked during
that correction.

## B1/B2 Re-gate

Date: 2026-07-19

Status: `reviewer_pass / test-only authorization required`

The Planner's B1/B2 documentation correction closes the package-boundary findings.

- The exact candidate now contains eight product files. The only permitted
  `backend/infrastructure/storage/database.py` change is the one-line addition of
  `contact_point_profile_cr_category_selections` to `init_db().profile_tables`.
  Its current diff is precisely `1` addition. This keeps the new model out of generic
  `Base.metadata.create_all()` so the existing dedicated Point Profile bootstrap owns
  validation, transactional creation, and read-verify.
- The corrected candidate statistics reproduce: the eight product files plus four
  focused tests are `581 additions / 17 deletions`; the mixed client file has exactly
  `11` additions for the five approved CR-coverage type symbols/fields. The index is
  empty, and no whole-file client or database inclusion is authorized.
- The package command is now truthfully fixed at `31 passed` for the four named
  modules. The historical `46` belongs to the broader TASK_364B suite and is no longer
  represented as TASK_364C evidence.
- The proposed assertion is bounded to
  `tests/unit/test_contact_point_profile_schema.py`, currently below the Python hard
  limit. Its required proof is well-scoped: generic `Base.metadata.create_all()` must
  exclude the selection table, and real temporary `init_db()` must create/read-verify
  it through the dedicated bootstrap.

No hidden product dependency remains after the `database.py` hunk is included. The
isolated frontend build/typecheck is intentionally still a QA package-validation gate;
it cannot be claimed from the mixed worktree build because R1 and SummaryCard hunks
remain excluded.

## Re-gate Next Legal Route

Route to **User test-only implementation approval, then Planner final
source-of-truth reconciliation**. Only after that reconciliation may Developer add the
one bounded schema assertion. TASK_364B remains Integrator blocked; do not route to QA
or Integrator yet.

## Tests-Only Diff Gate

Date: 2026-07-19

Status: `reviewer_pass`

The authorized change is confined to the existing
`test_point_profile_schema_registers_cr_category_selection_table` node in
`tests/unit/test_contact_point_profile_schema.py`.

- The test wraps the `database` module's production
  `bootstrap_contact_point_profile_schema` reference while invoking real disposable
  `init_db()`. Immediately before the dedicated bootstrap, it observes that the CR
  selection table is absent; it then calls the real bootstrap and retains the table,
  UNIQUE, and composite-FK inspector assertions. This proves the exact B1 ordering
  boundary rather than a duplicated helper approximation.
- The exact node passes. The four permitted package modules were rerun and pass
  `31 passed`.
- `(Get-Content tests/unit/test_contact_point_profile_schema.py -Encoding UTF8).Count`
  is `384`, below the Python hard limit. The authorization document's `323` was a
  stale estimate; this observation requires only Planner source-of-truth correction,
  not a scope expansion or a code change.
- Scoped diff-check and UTF-8 trailing-whitespace checks are clean apart from existing
  repository LF/CRLF notices. The index remains empty. No product file, client type
  hunk, other test node, R1 UI/SummaryCard path, real data/file, or external residual
  was absorbed by this test-only gate.

## Next Legal Route

Route to **Planner minimal line-count/source-of-truth reconciliation**, then **QA
hunk-isolated package validation**. QA must produce the frontend build/typecheck
artifact with the exact authority baseline and client type hunk only, excluding R1 and
SummaryCard. TASK_364B remains Integrator blocked; do not route directly to Integrator.

## Backend-Only Package-Boundary Re-gate

Date: 2026-07-19

Status: `reviewer_pass`

QA correctly established that the client-only hunk is not self-contained. The narrowed
TASK_364C package is now coherent and contains only:

- eight reviewed backend/API/storage paths, including the exact one-line
  `database.py` exclusion; and
- four focused backend/API test paths, including the already authorized bootstrap-order
  assertion.

The candidate statistic reproduces as `596 additions / 17 deletions` across those
twelve paths. `frontend/src/api/client.ts` remains a separate `11`-addition hunk and is
not part of this package. The API's additive response fields remain backward-compatible
with the accepted frontend; the typed client and every required consumer/fixture must be
reviewed together later in TASK_364B.

Validation rerun for this revised boundary:

- four exact package tests: `31 passed`;
- `py_compile` for all eight candidate Python modules: passed;
- index: empty; no R1 selector/model/editor/CSS, SummaryCard, client, TASK_363C/D,
  TASK_365A/B/C, downstream consumer, or external dirty hunk is included.

## Next Legal Route

Route to **QA package validation** for the revised 12-path backend/test isolate. No
frontend build/typecheck is part of TASK_364C after client exclusion. TASK_364B remains
Integrator blocked until TASK_364C is accepted and TASK_364B completes its own
client-plus-consumer package re-gate. Do not route directly to Integrator.
