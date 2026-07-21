# TASK_366C Reviewer Plan Gate

Date: 2026-07-21

Role: Reviewer

Lane: `import-matrix-replace-method-authority-sync`

Status: `reviewer_blocked / Planner docs-only fix required`

Implementation authorization: none.

## Scope Reviewed

- `AGENTS.md`, task board, TASK_366C task, plan, and Planner discovery evidence.
- Accepted TASK_366B baseline at `18df3f34ce0f3bbac8c714b38f9b8aa747d100d7`.
- The current Import Matrix commit service, source-import persistence service and
  repository, request-session transaction boundary, Matrix Method sync service, parser,
  import route, and draft repository.

No product or test code was modified. No database, public-drive workbook, attachment,
or other real operator file was accessed.

## Confirmed Contract Boundaries

- The intended write target is correctly limited to one editable Matrix draft. Existing
  Confirm Matrix remains the only publication action; Generic Test Record and TASK_360B
  are not write targets.
- Reusing TASK_366B's canonical EIA-364 parser/proposal construction preserves the
  existing family-format and safe-candidate rules instead of duplicating them.
- The planned row policy correctly distinguishes source-level authority blockers from
  row-local `current`, no-core, ambiguity, downgrade, and malformed outcomes. Workbook
  reads remain `.xlsx`/COM read-only and the stated non-Matrix locks are appropriate.

## Blocking Findings

### B1: Source-authority no-write guarantee conflicts with the proposed persistence order

The plan requires source-level catalog failures to be typed `no-write` outcomes
([plan](D:\PythonProject\connlab\docs\task_366c_import_matrix_replace_method_authority_sync_plan.md:57)),
but its implementation sequence persists Source Matrix lineage before the sole Standard
catalog read ([plan](D:\PythonProject\connlab\docs\task_366c_import_matrix_replace_method_authority_sync_plan.md:43)).
That mirrors the current service: `persist_from_preview(...)` occurs before selected
draft construction ([matrix_import_commit_service.py](D:\PythonProject\connlab\backend\application\matrix_import_commit_service.py:154)),
whereas the planned authority read comes later. The FastAPI session currently rolls
back route exceptions, but that implicit route behavior is not an adequate application
contract for direct service tests or for a future composition change.

**Required Planner docs-only fix:** freeze one concrete atomic boundary before any
implementation. Either build and validate the selected in-memory source/draft facts,
then read/validate the catalog before *any* source-import or draft persistence; or
introduce an explicitly authorized shared transaction/unit-of-work boundary that
contains source lineage plus draft creation and guarantees rollback on every authority
error. The test matrix must assert source-import count, source-snapshot count, and
draft count remain unchanged for missing resource, unreadable/invalid worksheet, and
malformed catalog failures. “No new draft” alone is insufficient for the board's
frozen `no-write` promise.

### B2: Existing source-import reuse bypasses catalog identity and stale-authority policy

The current commit service returns the existing draft immediately when the TASK_261
payload/selected-group fingerprint matches
([matrix_import_commit_service.py](D:\PythonProject\connlab\backend\application\matrix_import_commit_service.py:129)).
The proposed plan preserves that fingerprint as the idempotency key but calls for the
catalog read only after this branch. Therefore an unchanged import payload can reuse a
draft whose import-mode Method context was built against a different Standard resource,
sheet, or catalog revision, without evaluating the required catalog/source/row/target
TOCTOU facts.

**Required Planner docs-only fix:** define the exact replay rule before Developer
planning-first. For a matching import fingerprint, the plan must require a one-read
catalog/source validation before returning the old draft and compare it with a complete
persisted import-mode context (resource id, canonical path, effective worksheet,
catalog fingerprint, pre/post Method fingerprints, selected-group/source fingerprint,
and schema version). It must then freeze whether a mismatch is a typed `409` no-write
or an explicitly defined new operation with a distinct persistence identity; do not
leave the current early return as the behavior. Add deterministic regressions for
same-payload/current-catalog reuse, identical-row source/sheet switch, catalog revision
change, missing/stale import context, and no duplicate source/draft writes on every
blocked branch.

## Validation Performed

- The board records TASK_366C as planned-only and pending this Reviewer plan gate;
  Developer routing is not legal.
- The accepted TASK_366B commit is the current local HEAD.
- Governance diff check is clean except for the existing board LF/CRLF working-copy
  notice; targeted trailing-whitespace checks are clean and the index is empty.

## Next Legal Route

Route only to **Planner docs-only fix pass** for B1 and B2. Do not route Developer
planning-first or implementation until the Replace transaction and existing-import
replay rules make source/catalog authority failures and reuse behavior deterministic.

## B1/B2 Plan Re-Gate

Date: 2026-07-21

Status: `reviewer_pass`

The Planner's revised contract closes both authority-ordering blockers without
expanding the planned product surface:

- It freezes a complete no-write preflight before source-import lineage, source
  snapshot, draft, or method-context/audit persistence: imported payload and selected
  source facts, Standard resource/path/effective worksheet/catalog, row proposals, and
  all source/root/row/pre- and post-transform fingerprints are evaluated first.
- Source-level authority failures now expressly preserve all four persistence counts.
  The later source-lineage, transformed draft, and context writes occur in one
  deterministic transaction; uniqueness or stale conflicts roll back the whole unit
  and map to typed `409`.
- TASK_261 payload/selected-group fingerprint reuse no longer permits the current early
  return. Reuse requires a new no-write read/validation pass and exact persisted
  import-mode context equality for source identity, canonical payload and selection,
  resource/path/sheet/catalog, proposal/result, pre/post Method fingerprints, and
  schema version. Missing or divergent context is explicitly `409`/zero-write; this
  lane does not create another source import under the legacy fingerprint.
- The regression matrix now covers each authority failure's unchanged source/draft/
  audit counts, same-context idempotency, source/sheet/catalog switches, missing or
  stale context, persistence rollback, row-local safe/unsafe results, and the existing
  Confirm Matrix/TASK_366B boundaries.

### Re-Gate Validation

- Read-only reconciliation of the corrected task, plan, Planner evidence, reviewer
  findings, board, and current import/session persistence behavior.
- Targeted stale-ordering scan confirms the old early-return rule is forbidden and the
  required before-write/current-context clauses are present.
- Governance diff check is clean apart from the repository's existing board LF/CRLF
  working-copy notice; targeted trailing-whitespace scan is clean and the index is
  empty. No product, test, database, public-drive, or attachment path was modified or
  accessed.

## Next Legal Route

Recommend only **User approval for Developer planning-first**. TASK_366C remains
planned-only and product implementation remains unauthorized; do not route Developer
implementation directly.

## Implementation-Readiness Gate

Date: 2026-07-21

Status: `reviewer_blocked / Planner docs-only fix required`

Implementation authorization: none.

## Readiness Confirmed

- The proposed prepared-source aggregate, single Standard-catalog authority result,
  exact replay context, nested write transaction, reload/read-verify, typed response,
  and inline returned-draft consumption are technically coherent. They preserve the
  confirmed-only publication boundary, source workbook read-only behavior, and the
  TASK_366B parser/Preview-Apply contract.
- The proposed tests correctly cover source-level all-table zero-write, strict reuse,
  source/context switches, persistence rollback, safe and row-local unsafe proposals,
  and Matrix Editor consumption.

## Blocking Findings

### B3: Formal task May Touch does not authorize the refined no-write implementation package

The Developer planning-first evidence and the updated plan correctly identify that
zero-write preflight requires mechanical extraction of the current source aggregate and
draft construction. Their exact future package includes
`source_matrix_import_persistence_service.py`, `source_matrix_import_builder.py`,
`matrix_import_draft_builder.py`, and `matrix_import_method_authority.py`.

However, the controlling task's May Touch list still authorizes only the commit service,
the saved-draft sync service or one optional helper, route/dependencies, conditional
draft repository work, frontend client/workspace, and unnamed focused tests
([task](D:\PythonProject\connlab\tasks\TASK_366C_IMPORT_MATRIX_REPLACE_METHOD_AUTHORITY_SYNC.md:109)).
It neither authorizes the source persistence service nor names the three required
bounded modules. Implementing the Developer plan as written would therefore expand the
formal lane boundary during coding.

**Required Planner docs-only fix:** reconcile task, board, Planner/reconciliation,
plan, and Developer evidence to one exact May Touch list: the mechanical source
persistence delegation, the three named bounded application modules, the exact
transaction-provider dependency hunk, route/client/workspace response hunks, and the
named fixture/test modules. Preserve the existing locks: no repository/schema changes,
no TASK_366B saved-draft service behavior/context change, and no parser/import
extraction-rule change. The task must also mark the accepted TASK_366B service as a
read-only dependency, rather than leaving it as a potentially mutable alternative.

### B4: Recorded current line counts are stale and undermine the package-size gate

Developer evidence describes the current source persistence and commit services as
`536` and `465` lines, while this read-only gate measures their UTF-8 physical counts
as `480` and `409`. The planned extraction remains reasonable because future code must
stay below the 500-line hard limit, but the active size facts and resulting split budget
must be corrected before approval. Do not treat historical figures as current package
evidence.

**Required Planner docs-only fix:** record the current UTF-8 physical-line command and
the measured values, then freeze the post-change limits for each touched/new module.
No product or test file may be changed in this reconciliation.

## Validation Performed

- Read-only audit of the task, plan, Planner/Developer/reconciliation/Reviewer
evidence, board, current import commit/persistence/session composition, accepted
TASK_366B resolver, route, and dependency wiring.
- Current UTF-8 physical counts: source persistence service `480`, import commit
service `409`, accepted saved-draft sync service `326`.
- No product, test, database, public-drive, attachment, or source-workbook path was
modified or accessed.

## Next Legal Route

Route only to **Planner docs-only fix pass** for B3 and B4. Do not seek or act on user
product implementation approval until the formal task boundary and line-count evidence
match the refined implementation plan.

## B3/B4 Implementation-Readiness Re-Gate

Date: 2026-07-21

Status: `reviewer_pass`

Product implementation authorization: none.

The corrected formal package is implementation-ready:

- Task, plan, Planner/Developer/reconciliation evidence, and board now name the same
  narrow implementation surface: the mechanical source-persistence delegation, three
  bounded pure application modules, exact commit-service transaction wiring, thin
  route/client/workspace response hunks, and the named fixture/unit/API/frontend test
  nodes. The accepted TASK_366B service, parser, Excel reader, source/draft
  repositories, Matrix session, and Confirm services are expressly read-only
  dependencies.
- The source builder prepares one compatible aggregate without repository calls; the
  draft builder consumes that exact aggregate; the authority module performs one
  resource/catalog read and derives proposals, transformed Methods, fingerprints,
  strict replay context, and summary from those immutable facts. The commit service
  then performs exact reuse comparison or one nested transaction with read-verify and
  rollback. This implements the B1/B2 authority and zero-write contracts without a
  schema, repository, parser, or saved-draft Preview/Apply change.
- Current UTF-8 physical facts are consistently `480` for source persistence and `409`
  for import commit. The superseded `536`/`465` figures are historical only. The plan
  requires a mechanical extraction before behavior additions, keeps each touched/new
  Python module below `500` lines, and prohibits blank-line suppression as a size
  workaround.
- TDD covers all-table source-level zero-write, one-read authority, strict replay and
  mismatch `409`, persistence/read-verify rollback, row-local proposals, typed summary,
  Matrix Editor returned-draft consumption, and the accepted TASK_366B/Confirm Matrix
  regressions. Package isolation remains hunk-level for mixed dependencies and UI/API
  files.

### Re-Gate Validation

- Read-only audit of the reconciled task, plan, Planner/Developer/reconciliation and
  Reviewer evidence, board, current source/import/session composition, accepted
  TASK_366B resolver, and dependency wiring.
- Reproduced UTF-8 physical count command yields source persistence `480`, import
  commit `409`, and accepted saved-draft sync `326` lines.
- Governance diff check is clean apart from the existing board LF/CRLF working-copy
  notice; no product/test/schema/API-client path was changed, no real file was accessed,
  and the index is empty.

## Next Legal Route

Recommend only **User product implementation approval followed by Planner final
source-of-truth reconciliation**. Do not route Developer implementation directly.

## Fixture-Scope / Readiness Re-Gate

Date: 2026-07-21

Status: `reviewer_pass / Developer tests-only fix authorized`

## Scope Decision

The requested test-only fixture adjustment is necessary and sufficiently bounded:

- The existing success/reuse node seeds only `Project` and still asserts the original
  `201 created` plus same-input `201 reused` behavior. It has no Standard resource or
  catalog setup, while the accepted TASK_366C implementation correctly makes that
  authority a Replace precondition.
- Reproducing exactly that node yields `422` at the existing first `201` assertion.
  This is consistent with the approved typed authority/no-fallback contract, not a
  product regression to repair by restoring legacy behavior.
- The formal task, plan, board, and Planner reconciliation authorize only disposable
  Standard resource/catalog fixture setup for this one existing success/reuse node.
  Its existing created/reused, selected-group, lineage, and identity assertions remain
  intact. The other test nodes, all product paths, source workbooks, and external
  residuals remain locked.
- The current test module is `183` UTF-8 physical lines and has no candidate diff. The
  future hunk must stay below the hard limit, use only the test's temporary directory
  and SQLite database, and must not weaken the source-level `422`/zero-write tests.

### Validation

- `py -m pytest tests/integration/test_matrix_import_group_selection_commit_api.py::test_matrix_import_commit_api_creates_selected_only_draft_and_reuses_same_input -q`
  currently fails exactly at `assert response.status_code == 201` with actual `422`,
  after only `_seed_project(...)` has run.
- Read-only diff/scope review confirms this pass did not modify the legacy test, product
  candidate, assertions, or other test nodes. The index remains outside this Reviewer
  action.

## Next Legal Route

Route only to **Developer tests-only fix pass**. Permit one bounded fixture/setup hunk
in `tests/integration/test_matrix_import_group_selection_commit_api.py` for the named
success/reuse node; do not route QA or Integrator yet.

## Implementation Re-Gate After Fixture Fix

Date: 2026-07-21

Status: `reviewer_pass`

### Review Conclusion

- The authorized fixture-only hunk is correctly confined to
  `test_matrix_import_commit_api_creates_selected_only_draft_and_reuses_same_input`.
  It creates a Standard catalog workbook below pytest's `tmp_path`, registers that
  temporary path through the existing External Resource API, and leaves the original
  created/reused `201`, selected-group, lineage, and identity assertions unchanged.
  It does not restore a no-authority fallback or alter another node in the module.
- The actual Replace path performs payload/source/draft preparation without repository
  writes, resolves the configured Standard resource and catalog before looking up a
  TASK_261 reuse candidate, and fails the authority preflight before entering the
  nested persistence transaction. Reuse validates the persisted import, source, draft,
  and complete import-mode context; changed source/catalog/proposal facts return the
  typed conflict path rather than duplicating an import.
- New persistence writes source then draft inside the injected nested transaction and
  reload/read-verify source fingerprints, transformed Method fingerprints, and the
  stored authority context before the savepoint is released. The resolver keeps the
  configured Standard resource request-scoped and derives the row summary and
  transformed draft from the one catalog read. Confirm Matrix remains outside this
  flow.
- The route exposes the typed Method summary, while Matrix Editor continues to consume
  the returned editable draft and adds only an inline `aria-live` outcome. The reviewed
  candidate stays inside TASK_366C's authorized hunk set; unrelated Fee, TASK_364/365,
  release, and other dirty-worktree paths remain excluded.

### Reviewer Validation

- `py -m pytest tests/unit/test_matrix_import_commit_service.py tests/unit/test_matrix_import_method_authority.py tests/integration/test_matrix_import_method_authority_commit_api.py tests/integration/test_matrix_import_group_selection_commit_api.py tests/integration/test_project_test_plan_source_matrix_import_persistence_api.py tests/unit/test_standard_method_version_parser.py tests/unit/test_matrix_method_version_sync_service.py tests/integration/test_matrix_method_version_sync_api.py -q`: `28 passed`.
- `npm test -- MatrixEditorWorkspace --run`: `1 file / 44 passed`.
- `npm run build`: passed; only the existing Vite chunk-size warning was emitted.
- Candidate Python compile passed. Tracked candidate `git diff --check` passed with
  only the existing LF/CRLF notices; reviewed new modules have no UTF-8 trailing
  whitespace. All reviewed bounded Python modules and tests remain below 500 physical
  lines. No staged changes, `data/**` changes, real database, public-drive file,
  attachment, or source workbook access occurred during this review.

## Next Legal Route

Route only to **QA gate** for the declared disposable API and Matrix Editor smoke
validation. Do not route Integrator from this Reviewer pass.
