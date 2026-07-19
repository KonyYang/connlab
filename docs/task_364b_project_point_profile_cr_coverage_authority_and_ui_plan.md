# TASK_364B Project Point Profile CR Coverage Authority And UI Plan

## 1. Status And Authorization

`complete / Integrator accepted`

Implementation completed within the frozen scope. Focused Reviewer acceptance, QA,
production build, scoped checks, controlled `514x831` browser smoke, and explicit user
acceptance passed. No downstream CR-consumer implementation is authorized by this plan.

User acceptance previously requested a frontend-only R1. The superseding executable
plan is `docs/task_364b_r1_inline_cr_table_corrective_plan.md`. Where the two plans
conflict on editor layout, mode presentation, or new-row selection, the R1 plan is
current. R1 is implemented, reviewed, QA-passed, and user-accepted.

## 2. Discovery Gate

### Confirmed By User

- CR coverage is project-wide, like LLCR; Matrix groups differ only in sample quantity.
- CR custom selection always selects complete categories, never point subsets inside
  a category.
- CR defaults to following LLCR and diverges only after `Customize CR`.
- HP/LP were examples only. No category name is a universal rule or may be hard-coded.

### Confirmed By Repository Evidence

- Confirmed Point Profile revisions already own ordered categories with stable
  project-scoped `ppc-N` ids, exact point expressions, prefixes, and derived counts.
- Current direct Confirm atomically issues/retains category ids, supersedes the prior
  confirmed revision, stores one snapshot, and uses a revision fingerprint for CAS.
- Existing workspace and summary projections expose confirmed categories and the LLCR
  `points_per_sample` total.
- The Setup UI already owns local-only Point Profile rows and has a single Confirm
  command; this is the correct boundary for adding a local CR coverage draft.
- Measurement Plan has LLCR/CR target concepts, but the requested coverage is one
  project policy, not a repeated target or Matrix-group policy.
- Current schema bootstrap is fail-closed and supports transactional additive Point
  Profile migration. Existing revisions use V1/V2 opaque fingerprints.

### Planner Decisions

- Persist custom coverage in a new selection snapshot table. Absence means follow.
  This avoids rewriting old revisions and keeps custom-all distinct from follow.
- Put `cr_selected` on each confirm category row rather than accept only an id list.
  New rows have no server id before Confirm, so per-row selection is the only simple
  way to select them in the same atomic command without label matching or a two-step
  save.
- Keep existing `points_per_sample` as the LLCR total. Add a nested `cr_coverage` read
  object instead of renaming or weakening an accepted compatibility field.
- Display the confirmed CR policy both in Setup and in the existing Matrix summary.
  Do not integrate group sample quantities or output consumers in this task.

### Non-Blocking Assumption

Once the operator is in custom mode, a subsequently added category starts unselected.
This preserves deliberate divergence. `Customize CR` itself initially selects every
currently visible category so the action starts from the default policy rather than
from an empty invalid state.

## 3. Task Inputs And Outputs

### Inputs

- current confirmed Point Profile revision id/fingerprint;
- ordered local category rows: category id when retained, prefix, point expression;
- CR mode: `follow_llcr` or `custom`;
- per-row custom CR selection boolean;
- actor.

### Outputs

- one new confirmed Point Profile revision containing the canonical LLCR categories;
- zero ordered CR selection rows for follow mode, or one-or-more rows bound to stable
  category ids for custom mode;
- a V3 fingerprint covering both category and CR coverage authority;
- typed workspace/summary revision data with CR mode, selected ids, and CR
  points/sample;
- Setup and Matrix-summary UI reflecting the confirmed policy.

## 4. Data Structure Design

### New Model

`ContactPointProfileCrCategorySelectionModel`

Fields:

- `contact_point_profile_cr_selection_id: str` primary key;
- `contact_point_profile_revision_id: str`;
- `category_id: str`;
- `selection_ordinal: int`.

Constraints:

- composite foreign key `(revision_id, category_id)` to the unique category snapshot
  key `(revision_id, category_id)`;
- unique `(revision_id, category_id)`;
- unique `(revision_id, selection_ordinal)`;
- `selection_ordinal >= 0`.

No mode column is required:

```text
selection row count = 0  -> follow_llcr
selection row count > 0  -> custom
```

Custom-empty is invalid at the application boundary, so storage remains unambiguous.

### Read Value

Add a small application/API value:

```text
cr_coverage:
  mode: follow_llcr | custom
  selected_category_ids: ordered stable ids
  points_per_sample: derived integer
```

In follow mode, `selected_category_ids` is the ordered full category id list in the
read projection, even though storage contains no redundant rows. This makes the
effective policy explicit to clients while preserving normalized persistence.

## 5. Application And API Design

### Confirm Signature

Conceptually extend the existing command to:

```text
confirm_direct(
  project_id,
  expected_revision_id,
  expected_fingerprint,
  rows[{category_id, prefix, point_expression, cr_selected}],
  cr_coverage_mode,
  actor,
)
```

The route request adds `cr_coverage_mode` and `cr_selected` with typed enum/boolean
validation. The route stays thin and calls the lifecycle service.

### Transaction Order

1. Validate mode and canonical Point Profile rows.
2. Validate follow/custom selection rules against ordered input rows.
3. Open the existing repository transaction and validate expected confirmed CAS.
4. Create/supersede revision state exactly as today.
5. Retain/issue stable category ids and write canonical category snapshots.
6. Convert selected row positions to the issued stable ids.
7. Write zero follow rows or ordered custom selection rows.
8. Compute the V3 fingerprint from canonical categories, explicit mode, and ordered
   selected ids.
9. Update the root and flush/commit once.

Any failure rolls back categories, selections, revision state, and root pointers.

### Repository Methods

Add focused methods rather than expose Session to application code:

- `cr_category_ids(revision_id) -> list[str]`;
- `replace_cr_category_selections(revision_id, category_ids, id_factory) -> None`.

The read method returns current category order, not arbitrary table/insertion order.
The write method relies on DB constraints and application validation; it never
matches labels or prefixes.

### Fingerprint

Extend `point_profile_fingerprint` with an explicit optional coverage payload and
emit version `point-profile:v3` only for new confirmations. A V3 payload includes:

- ordered canonical categories;
- `cr_coverage_mode`;
- ordered selected stable ids (empty for follow storage semantics).

Existing V1/V2 values are never recalculated during bootstrap or reads.

## 6. Schema Migration Design

Update the dedicated Point Profile migration registry and `database.py` profile-table
set from three to four tables.

Supported starting states:

- no Point Profile tables: create all four;
- exact current three-table V2 authority: add the exact selection table;
- exact four-table authority: validate and no-op;
- an allowed partial root/revision/category bootstrap state already covered by current
  tests: validate existing tables, then create remaining exact tables in dependency
  order;
- any malformed existing selection table or incompatible existing authority: fail
  closed before new DDL.

Use `BEGIN IMMEDIATE`, validate the final transaction-visible four-table shape, then
commit. Failure rolls back created objects. No table rebuild or data-row rewrite.

## 7. Frontend Design

### Local Model

Extend each local draft row with a local stable key and `cr_selected`. Hydration:

- reads the confirmed `cr_coverage.mode`;
- marks rows selected from effective `selected_category_ids`;
- defaults not-started/legacy data to follow.

Model commands:

- `customizeCr()` sets mode to custom and selects every current row;
- `useSameAsLlcr()` sets follow and clears custom flags;
- `setCrSelected(rowKey, selected)` changes one dynamic row;
- `addCategory()` preserves current behavior and sets `cr_selected=false` when custom;
- Confirm serializes mode and each row's boolean atomically.

Selectors derive LLCR total, CR total, selected count, and validation. They do not use
category labels.

### Editor

Keep the current `LLCR` header and compact table. Below it, place one quiet inline
`CR coverage` section.

- Follow: `Same as LLCR`, points/sample, `Customize CR`.
- Custom: dynamic checkbox rows showing prefix and expression, selected count,
  points/sample, `Use same as LLCR`.

Use semantic fieldset/legend or equivalent accessible grouping. Avoid nested cards,
modal flows, decorative panels, or color-only state. Preserve the existing 600px
compact editor width and make labels/actions wrap safely at 514px.

### Matrix Summary

Keep the existing confirmed LLCR category list. Add one concise CR line:

- follow: `CR: Same as LLCR · N points / sample`;
- custom: `CR: X categories · N points / sample`.

This is verification of confirmed project authority only, not a Matrix group total.

## 8. File-Level Implementation Order (TDD)

1. Add schema red tests for fresh/current/idempotent/malformed/rollback states; then
   add the model, migration registry, repository table set, and database table set.
2. Add fingerprint/lifecycle red tests for follow/custom/new-row/stale/rollback; then
   update fingerprint, repository, and lifecycle.
3. Add read/API red tests; then update read projection and typed route DTOs.
4. Update typed client DTO/command only after backend contract passes.
5. Add selector/hook red tests; then implement local mode/selection state and command
   serialization.
6. Add editor and summary red tests; then implement the inline UI and scoped CSS.
7. Run Point Profile compatibility tests, focused frontend tests, build, disposable
   browser smoke, and package-isolation scans.

## 9. Exact May Touch

The task file's Authorized May Touch list controls. It is limited to existing Point
Profile storage/application/API files, the Point Profile table registration fragment
in `database.py`, typed Point Profile client surface, Point Profile selectors/model/
editor/summary/CSS, focused tests, and TASK_364B governance.

## 10. Must Not Touch

- Measurement Plan target authority and target-specific coverage.
- Matrix group/sample authority or `points x samples` calculations.
- CR/LLCR workbook generation, Fee Units/pricing/rebase, Generic Test Record/Report,
  or any downstream consumer.
- Category-name rules, including HP/LP matching.
- Parser/import, LTR/public drive, Office, real DB/files/folders, dependencies,
  release/dist, TASK_363B, or unrelated residuals.

## 11. Risks And Mitigations

- Risk: custom all-selected could collapse into follow. Mitigation: persist rows for
  every selected category in custom; only zero rows means follow.
- Risk: a new category lacks an id at command time. Mitigation: selection travels on
  the same ordered row, then binds to the issued id inside the transaction.
- Risk: schema bootstrap could accept a partial/wrong table. Mitigation: exact columns,
  composite FK, unique/check/index validation before and after transactional DDL.
- Risk: old fingerprints change. Mitigation: V3 only on new confirmations; historical
  fingerprints are opaque and untouched.
- Risk: UI state detaches after row delete/add. Mitigation: local stable row keys and
  row-owned selection state; component tests cover add/delete/custom transitions.
- Risk: downstream CR behavior appears implemented. Mitigation: summary explicitly
  reports points/sample only; all Matrix-group totals and consumers remain locked.
- Risk: shared dirty worktree absorbs other tasks. Mitigation: exact path/hunk review,
  `git diff --check`, whitelist scan, and no staging/commit in implementation unless
  separately requested.

## 12. Validation

Backend:

- focused Point Profile schema, fingerprint, lifecycle, read, consumer-regression,
  and API tests using temporary SQLite only;
- `py -m py_compile` on changed Python modules;
- no access to `data/connlab.sqlite3` or operator project files.

Frontend:

- focused selector, hook, editor, Setup regression, and summary tests;
- `npm run build` from `frontend/`;
- desktop and 514px disposable browser smoke for follow, custom arbitrary categories,
  add-new-unselected, return-to-follow, Confirm, reload, summary, keyboard/focus, and
  console errors.

Package:

- UTF-8/trailing whitespace and line-count checks;
- exact May Touch / forbidden-path scan;
- `git diff --check` with unrelated existing residuals excluded from conclusions;
- no-real-DB/file mutation scan.

## 13. Approval Request

Approval received: `批准 TASK_364B 实施`.

Implementation will stop at this task. Any group sample-quantity
total, Fee, workbook, or other CR consumer integration requires a separate task and
approval.

## 14. Local Completion

- Developer evidence:
  `docs/lane_evidence/TASK_364B_project-point-profile-cr-coverage-authority-and-ui_developer.md`
- Backend Point Profile set: `46 passed`.
- Frontend Contact Measurement Plan/Matrix regression: `89 passed`.
- Frontend build, Python compile, scoped diff, no-hard-coded-category scan, and
  desktop/514px browser smoke passed.
- Status: user accepted; TASK_364C dependency accepted; pending Reviewer package re-gate.
- Final package is the seven exact R1 frontend files/hunks plus TASK_364B governance and
  the controlled 514px QA PNG. Backend/API/client/summary and external residuals remain
  excluded from the R1 package. This historical R1 boundary is now serialized behind
  TASK_364C, which accepted the backend/API/storage authority baseline at `b34f2c2c`.
  The client contract remains deferred to the TASK_364B package re-gate.

## 15. Package-Boundary Dependency

TASK_364C accepted the CR coverage backend/API/storage authority baseline at
`b34f2c2cbcc3b27266b480d6ff76a604f06be452`. TASK_364B now requires a separate
Reviewer package re-gate for the seven R1 files, exact client +11 hunk, and only the
single `cr_coverage` fixture line from `ContactMeasurementPlanSummaryCard.test.tsx`.
The SummaryCard production file and all other SummaryCard-test visual hunks remain
excluded. Expected source numstat is 355 additions / 23 deletions; Reviewer must verify
an isolated frontend build before QA/Integrator routing.
