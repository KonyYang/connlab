# TASK_363B Reviewer Plan Gate Evidence

Date: 2026-07-18

Role: Reviewer

Status: reviewer_pass

TASK_ID: `TASK_363B_MATING_UNMATING_FORCE_ALIAS_NORMALIZATION_CORRECTIVE`

Lane: `mating-unmating-force-alias-normalization-corrective`

## Gate Basis

- Current phase is Phase 11. `docs/task_board.md` identifies TASK_363B as the active
  planned-only lane, pending this Reviewer plan gate. Implementation is not
  authorized.
- TASK_363A is accepted at `937688dea5f581258f66ec71b52220abe162c5f2`; TASK_363B
  is a separate, post-acceptance corrective and does not reopen its r6 seed,
  manifest, pricing-draft rebase, or package history.
- The worktree contains only TASK_363B governance files for this planning pass.
  Existing route/service, TASK_362A, frontend/Test Points, release/dist, and other
  residuals are external and excluded.

## Repository Findings

- The current generic normalizer distinguishes `mating un mating force` from
  `mating unmating force`. A read-only probe confirms that the accepted hyphenated
  label matches Mechanical force, while the user-confirmed combined base and Single
  Pin slash labels are currently unmatched.
- `Lateral Force` and `contact retention force` already resolve to Mechanical force;
  `CPA force` resolves to the reviewed Automotive manual path. Mechanical and
  Automotive token-subset fallback is already disabled.
- The proposed anchored base-label canonical key will be used both while building the
  exact alias map and while matching input. The separate anchored Single Pin key maps
  to its existing exact `single pin mating force` alias and cannot satisfy the base
  `50/sample` predicate.

## Review Decision

The plan is sufficiently bounded and implementable:

1. Canonicalize only complete case-insensitive labels matching the declared slash
   whitespace and optional `Un-mating` hyphen grammar. Do not change generic token
   normalization or delete arbitrary spaces.
2. Keep the base family on the existing `50/sample` calculator and route only the
   combined Single Pin family to the established `20/reading` Mechanical path.
3. Preserve generic Mating/Unmating/Insertion/Withdrawal/Latch negatives,
   CPA/TPA/Automotive manual behavior, and Lateral/contact-retention `20/reading`.
   Missing readings remain a quantity review, not alias-match failure.
4. Lock r6 seed/extension/manifest, TASK_361L/TASK_363A rebase code, frontend/API
   client, formula/pricing/UI, authority models, workbook/output paths, and real
   DB/files. The May Touch list is limited to matcher/default-fill predicate and
   focused tests.
5. The positive/negative matrix, existing pricing-draft fingerprint/currentness
   regression, compilation, diff/trailing, whitelist, and no-real-mutation checks
   provide proportionate validation and package isolation.

## Validation

- Read task board, TASK_363B task/plan/Planner evidence, TASK_363A accepted evidence
  and commit context, current matcher/default-fill code, r6 seed aliases, and focused
  alias/default tests.
- Read-only probe confirmed current behavior for hyphenated/base slash/Single Pin,
  Lateral/contact-retention, and CPA paths.
- Governance diff check and trailing-whitespace scan found no defect; staged index is
  empty. No product code, tests, real DB/files, stage, commit, or push action occurred.

## Decision

`reviewer_pass`

Recommended next role/action: User approval for Developer planning-first only. Do
not start Developer product implementation until the user has approved planning-first
and source-of-truth reconciliation completes.

Blocking summary: none for TASK_363B Reviewer plan gate.

---

# TASK_363B Reviewer Plan Re-Gate: Units Ownership Contract

Date: 2026-07-18

Role: Reviewer

Status: reviewer_blocked

TASK_ID: `TASK_363B_MATING_UNMATING_FORCE_ALIAS_NORMALIZATION_CORRECTIVE`

Lane: `mating-unmating-force-alias-normalization-corrective`

## Finding

### B1: The plan does not authorize a regression that proves owning-Group isolation

The updated product contract is correctly written: base Mating/Unmating Units must
equal the current Fee line's owning Confirmed Matrix Group sample quantity, without
a readings multiplier or cross-Group aggregation. Current production assembly is
also aligned: `_calculate_line()` receives one `ConfirmedMatrixGroup` and passes
only `group.sample_quantity_expression` into `FeeDefaultFillContext`; the existing
`50/sample` helper reads that value directly and never consumes `step_quantities`.

However, the current May Touch and validation matrix allow only matcher/default-fill
tests. A `FeeDefaultFillContext` unit test can prove direct no-multiplier arithmetic,
but cannot prove the production Group-plus-row assembly does not accidentally use a
different Group's sample quantity. The plan must authorize a focused existing
Confirmed Matrix Fee draft service (or equivalent API) regression that constructs at
least two Groups with different sample quantities and asserts each base-label Fee
line uses its own Group quantity, even when Step readings differ.

## Required Planner Docs-Only Fix

1. Add the exact existing service/API regression file to TASK_363B May Touch and
   validation scope.
2. Freeze a two-Group case: distinct group sample quantities and divergent available
   readings; each complete base-label variant yields `50/sample` with Units equal
   only to its own Group quantity. Assert no cross-Group total and no readings
   multiplier.
3. Retain the existing missing/invalid owning Group quantity manual-review test and
   all Single Pin, contact-retention/Lateral, generic-negative, and Automotive
   regressions.

No product change is requested. r6 seed/manifest, TASK_361L/TASK_363A rebase,
frontend/API client, and every locked residual remain unchanged.

## Validation Notes

- Re-read the updated task, plan, Planner evidence, and board. They consistently
  record the new Units contract.
- Read `confirmed_matrix_fee_draft_service.py`: each Fee line is constructed with
  its current `group`, and its default-fill context receives that group's sample
  expression. Read the reviewed Mechanical force per-sample helper: it parses that
  expression directly and does not use readings/Step quantities.
- Reconfirmed the two anchored alias families and their existing negative/manual
  boundaries. Governance diff/trailing checks are clean; no product code, test,
  real DB/file, stage, commit, or push action occurred.

## Decision

`reviewer_blocked`

Recommended next role/action: Planner docs-only fix pass for B1, followed by Reviewer
plan re-gate. Do not route Developer planning-first until the production ownership
regression is in the frozen validation plan.

Blocking summary: B1 is a validation-scope gap for the newly frozen owning-Group
Units contract; the existing production code path itself is not a reported defect.

---

# TASK_363B Reviewer Plan Re-Gate: B1

Date: 2026-07-18

Role: Reviewer

Status: reviewer_pass

TASK_ID: `TASK_363B_MATING_UNMATING_FORCE_ALIAS_NORMALIZATION_CORRECTIVE`

Lane: `mating-unmating-force-alias-normalization-corrective`

## B1 Resolution

The task, plan, and Planner evidence now authorize exactly one additional test-only
file: `tests/unit/test_confirmed_matrix_fee_draft_service.py`. The frozen regression
creates two Confirmed Matrix Groups with distinct owning sample quantities, a complete
base Mating/Unmating alias in each Group, and divergent Step readings. It must prove
every generated base-family Fee line is `50/sample` with Units equal to its own
Group's sample quantity, with no readings multiplier, cross-Group total, or
other-Group lookup.

Missing or invalid owning Group quantity remains typed manual-review. The plan also
retains the Single Pin combined `20/reading`, contact-retention/Lateral `20/reading`,
no-`Force` generic-negative, and CPA/TPA/Automotive manual regressions. The inspected
`confirmed_matrix_fee_draft_service.py` remains locked: a failing assembly regression
requires a new Planner scope decision before any production-service edit.

## Validation

- Re-read the updated TASK_363B task, plan, Planner evidence, board, prior B1
  finding, and the existing Group-plus-row default-fill boundary.
- Confirmed May Touch, acceptance criteria, file-level plan, validation commands,
  and required test nodes all contain the same two-Group ownership contract.
- Governance diff check and trailing-whitespace scan are clean; staged index is
  empty. No product code, tests, real DB/files, stage, commit, or push action occurred.

## Decision

`reviewer_pass`

Recommended next role/action: Developer planning-first. User approval for this
planning-first pass is recorded in the current delegation; product implementation
remains unauthorized pending the later readiness and implementation gates.

Blocking summary: none for TASK_363B Reviewer plan re-gate.

---

# TASK_363B Reviewer Implementation-Readiness Gate

Date: 2026-07-18

Role: Reviewer

Status: reviewer_blocked

TASK_ID: `TASK_363B_MATING_UNMATING_FORCE_ALIAS_NORMALIZATION_CORRECTIVE`

Lane: `mating-unmating-force-alias-normalization-corrective`

## Blocking Findings

### B2: Frozen canonical key cannot reach the locked existing sample predicate

The planning-first plan and Developer evidence freeze the base canonical key as
`mating unmating force` and lock
`fee_reviewed_extension_defaults.py` unchanged. The current
`_is_mechanical_force_per_sample()` predicate, however, accepts only
`normalize_fee_rule_text(context.test_item) == "mating un mating force"`.

Consequently, the planned combined browser forms can become exact Mechanical matches
yet still bypass the retained `50/sample` branch. The planning claim that the new key
reaches the unchanged predicate is not true under the current code. Resolve this
before implementation by choosing exactly one bounded contract:

1. Canonicalize every approved base-family form, including the r6 hyphenated alias,
   to the existing `mating un mating force` key and keep default-fill locked; or
2. Retain `mating unmating force` and explicitly re-authorize the one predicate hunk
   in `fee_reviewed_extension_defaults.py`, with matching focused tests.

The Single Pin canonical key and all negative/manual boundaries must remain unchanged.

### B3: Board/source-of-truth is not reconciled to the planning-first boundary

`docs/task_board.md` still records TASK_363B as pending Reviewer plan re-gate and
lists `fee_reviewed_extension_defaults.py` as May Touch. The updated plan and
Developer evidence instead claim planning-first complete / pending readiness and
lock the default-fill production module. Reconcile the board to the selected B2
contract before any later implementation authorization.

## Validation Notes

- Directly reviewed the updated plan, Developer evidence, task, board, current
  matcher, current sample predicate, and Fee Group-plus-row assembly boundary.
- The two-Group test-only ownership regression is now sufficiently specified, and
  `confirmed_matrix_fee_draft_service.py` remains correctly locked. It does not cure
  the canonical-key mismatch.
- Planning files are docs-only; no TASK_363B product/test code changed, staged index
  is empty, and governance diff/trailing checks are clean.

## Decision

`reviewer_blocked`

Recommended next role/action: Planner docs-only contract and source-of-truth fix pass
for B2-B3, then Reviewer implementation-readiness re-gate. Do not route product
implementation approval or Developer implementation.

Blocking summary: canonical output and locked predicate disagree; board May Touch and
gate state also require reconciliation.

---

# TASK_363B Reviewer Implementation-Readiness Re-Gate: B2-B3

Date: 2026-07-18

Role: Reviewer

Status: reviewer_blocked

TASK_ID: `TASK_363B_MATING_UNMATING_FORCE_ALIAS_NORMALIZATION_CORRECTIVE`

Lane: `mating-unmating-force-alias-normalization-corrective`

## B2-B3 Verification

B2 is closed: the task, plan, Planner evidence, Developer evidence, reconciliation
evidence, and board now freeze every approved complete base Mating/Unmating form to
the existing `mating un mating force` key. That is the exact key accepted by the
locked `_is_mechanical_force_per_sample()` predicate, so the unchanged `50/sample`
calculator receives the intended path. The combined Single Pin family remains
`single pin mating force` and therefore stays on the existing `20/per reading` path.

B3 is also closed: the current board and lane documents consistently record
planning-first complete and pending this Reviewer implementation-readiness re-gate.
`fee_reviewed_extension_defaults.py` and
`confirmed_matrix_fee_draft_service.py` are locked production dependencies. The
two-Group owning-sample-quantity regression remains test-only and correctly proves
no readings multiplier or cross-Group lookup.

## Blocking Finding

### B4: The frozen test-file plan violates the Python hard line limit

The plan explicitly authorizes an extension to
`tests/unit/test_fee_default_fill.py`, which currently contains 728 physical lines.
That is already above the repository's 500-line hard limit, so authorizing new
TASK_363B assertions in that file is not implementation-ready. The plan also assigns
the two-Group production assembly regression to
`tests/unit/test_confirmed_matrix_fee_draft_service.py`, currently 478 lines, leaving
insufficient safe headroom for the required isolated fixture and assertions.

## Required Developer Docs-Only Planning Fix

1. Replace the oversized default-fill test-file addition with a new, bounded focused
   TASK_363B test module (or an existing in-limit module with documented headroom).
2. Move the two-Group production assembly regression to a bounded dedicated test
   module rather than growing the 478-line service test file past the hard limit.
3. Update task, plan, Planner/Developer/reconciliation evidence, board May Touch,
   commands, and package-isolation checks to name the replacement test modules.
   Keep all production ownership unchanged: only `fee_rule_matcher.py` may change;
   default-fill and confirmed Fee draft service production files remain locked.

## Validation Notes

- Re-read the task, plan, Planner/Developer/reconciliation evidence, board, current
  matcher, current per-sample predicate, and Group-plus-row assembly boundary.
- Confirmed the B2 canonical key reaches the existing predicate exactly, while the
  locked calculator continues to use only the owning Group sample quantity.
- Verified the planned files are docs-only, the staged index is empty, and targeted
  governance trailing-whitespace checks are clean. Existing dirty worktree entries,
  including the confirmed Fee draft service, remain external and excluded.
- Counted the planned Python test files: `test_fee_default_fill.py` is 728 lines and
  `test_confirmed_matrix_fee_draft_service.py` is 478 lines.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer docs-only planning fix for B4, then Reviewer
implementation-readiness re-gate. Product implementation remains unauthorized.

Blocking summary: B2 and B3 are resolved; the planned test-file ownership must be
made line-limit compliant before implementation can be authorized.

---

# TASK_363B Reviewer Implementation-Readiness Re-Gate: B4

Date: 2026-07-18

Role: Reviewer

Status: reviewer_blocked

TASK_ID: `TASK_363B_MATING_UNMATING_FORCE_ALIAS_NORMALIZATION_CORRECTIVE`

Lane: `mating-unmating-force-alias-normalization-corrective`

## Finding

### B4R: New bounded test modules are planned, but source-of-truth still authorizes the old files

The updated plan and Developer evidence correctly introduce the bounded future modules
`tests/unit/test_fee_rule_mating_unmating_alias_normalization.py` and
`tests/unit/test_confirmed_matrix_fee_draft_mating_unmating_units.py`; neither exists
yet, which is correct for this docs-only pass. They also correctly state that the
728-line `test_fee_default_fill.py` and 478-line
`test_confirmed_matrix_fee_draft_service.py` are read-only regressions.

However, the task's `Future Authorized May Touch` list still names both old files as
the new default-fill and production assembly test targets. Its validation section also
still assigns the two-Group ownership regression to the old service test. The current
board repeats that old service-test filename in the TASK_363B product candidate and
validation text. This leaves conflicting implementation authority and does not close
the B4 hard-limit finding.

## Required Planner Docs-Only Fix

1. Replace the old test-file entries in TASK_363B May Touch and its two-Group
   validation contract with the two new bounded module names.
2. Update the TASK_363B board row and active-task summary to name the new modules.
3. Align Planner and reconciliation evidence so any mention of the old files is
   explicitly read-only regression execution only, never a newly authorized edit or
   assembly-test destination.
4. Retain the frozen production boundary: `fee_rule_matcher.py` is the only product
   candidate; default-fill and confirmed Fee draft service production remain locked.

## Validation Notes

- Re-read task, plan, Planner/Developer/reconciliation evidence, Reviewer history,
  board, and current matcher/default-fill/assembly facts.
- Confirmed B2 remains exact: the planned base canonical key is
  `mating un mating force`, matching the locked sample predicate; combined Single Pin
  remains `single pin mating force` / `20 per reading`.
- Confirmed the two new test paths are absent, as required before implementation, and
  old-file physical counts remain 728 and 478. The staged index is empty; no product
  or test implementation occurred.

## Decision

`reviewer_blocked`

Recommended next role/action: Planner docs-only source-of-truth correction, then
Reviewer implementation-readiness re-gate. Product implementation remains
unauthorized; do not treat the recorded implementation-authorization intent as an
implementation start signal until this correction and final reconciliation are done.

Blocking summary: B4 module split is not yet reflected consistently in the task and
board, leaving an unsafe May Touch conflict.

---

# TASK_363B Reviewer Implementation-Readiness Re-Gate: B4R

Date: 2026-07-18

Role: Reviewer

Status: reviewer_blocked

TASK_ID: `TASK_363B_MATING_UNMATING_FORCE_ALIAS_NORMALIZATION_CORRECTIVE`

Lane: `mating-unmating-force-alias-normalization-corrective`

## B4R Verification

The B4R source-of-truth module ownership is now otherwise aligned. TASK, plan,
Planner/Developer/reconciliation evidence, and the board name only
`test_fee_rule_mating_unmating_alias_normalization.py` and
`test_confirmed_matrix_fee_draft_mating_unmating_units.py` as future bounded
TASK_363B test additions. The old default-fill and Confirmed Matrix Fee draft suites
are explicitly read-only regression execution; both future modules are absent, as
expected before implementation. The base canonical key, Single Pin path, production
locks, and authorization boundary remain correct.

## Blocking Finding

### B4R2: Recorded physical line counts do not match the checked-out files

The revised task, plan, Planner evidence, and Developer evidence state that the two
old read-only tests are 828 and 564 physical lines. Direct UTF-8 physical-line counts
from the checked-out files are instead 728 for `test_fee_default_fill.py` and 478 for
`test_confirmed_matrix_fee_draft_service.py`. These are the same line counts observed
at the prior B4 review. Because the hard-limit rationale and package-isolation check
depend on this factual record, the governance evidence must not carry invented or
stale counts.

## Required Planner Docs-Only Fix

1. Correct every TASK_363B current-state reference to the checked-out UTF-8 physical
   counts: 728 and 478, including task, plan, Planner/Developer/reconciliation
   evidence, and board if it contains those values.
2. State the exact counting command used for the current working copy and retain the
   two old files as read-only regression execution only.
3. Do not alter the newly reconciled May Touch modules, matcher-only production scope,
   or the pending readiness/final-reconciliation authorization boundary.

## Validation Notes

- Verified the B4R module paths across task, plan, Planner/Developer/reconciliation
  evidence, and board; no future creation occurred in this docs-only pass.
- Directly measured checked-out UTF-8 files with `Get-Content <path> -Encoding UTF8 |
  Measure-Object -Line`: 728 and 478, not 828 and 564.
- Reconfirmed the locked predicate matches `mating un mating force` and production
  assembly passes its current Group sample quantity into the default-fill context.
- Staged index is empty; no product or test implementation was performed.

## Decision

`reviewer_blocked`

Recommended next role/action: Planner docs-only factual-count correction, then
Reviewer implementation-readiness re-gate. Product implementation remains
unauthorized pending readiness and final source-of-truth reconciliation.

Blocking summary: B4R authority is aligned, but its line-limit evidence contains
incorrect current-file facts.

---

# TASK_363B Reviewer Implementation-Readiness Re-Gate: Final B4R2

Date: 2026-07-18

Role: Reviewer

Status: reviewer_pass

TASK_ID: `TASK_363B_MATING_UNMATING_FORCE_ALIAS_NORMALIZATION_CORRECTIVE`

Lane: `mating-unmating-force-alias-normalization-corrective`

## Readiness Verification

B2 through B4R2 are closed. The current task, plan, Planner/Developer/reconciliation
evidence, and board consistently freeze all complete base Mating/Unmating forms to
`mating un mating force`, which exactly reaches the locked `50/sample` predicate.
Combined Single Pin remains `single pin mating force` and follows the unchanged
`20/per reading` path. Generic no-Force, Insertion/Withdrawal/Latch,
CPA/TPA/Automotive, contact-retention, and Lateral boundaries remain unchanged.

Future test ownership is now bounded and unambiguous:

- `tests/unit/test_fee_rule_mating_unmating_alias_normalization.py`
- `tests/unit/test_confirmed_matrix_fee_draft_mating_unmating_units.py`

Both are absent before implementation, as required. The existing
`test_fee_default_fill.py` and `test_confirmed_matrix_fee_draft_service.py` are
explicitly read-only regressions. Direct UTF-8 physical-line counts using
`(Get-Content <path> -Encoding UTF8 | Measure-Object -Line).Lines` are 728 and 478,
matching every active TASK_363B governance reference. New modules must remain at or
below 500 physical lines.

The two-Group test contract remains adequate: distinct owning sample quantities and
divergent readings must prove base-family Units equal only the current Group's sample
quantity, without a readings multiplier or cross-Group lookup. The existing production
assembly passes `group.sample_quantity_expression` into the default-fill context, and
the locked calculator does not require an authorized change.

## Scope And Authorization

`fee_rule_matcher.py` is the only future production candidate. Default-fill and
Confirmed Fee draft service production files, seeds/manifest, TASK_363A/TASK_361L,
frontend/API client, Fee pricing/UI, workbooks, parser, LTR/public drive, real
DB/files, and all external residuals remain locked. The staged index is empty and this
review found no product or test implementation.

The user has expressed implementation intent, but implementation remains unauthorized
until Planner records the final source-of-truth reconciliation.

## Decision

`reviewer_pass`

Recommended next role/action: Planner final source-of-truth reconciliation to record
the explicit implementation authorization, then stop for the next delegated route.
Do not start Developer implementation from this Reviewer gate.

Blocking summary: none for implementation readiness.

---

# TASK_363B Reviewer Implementation Gate

Date: 2026-07-18

Role: Reviewer

Status: reviewer_pass

TASK_ID: `TASK_363B_MATING_UNMATING_FORCE_ALIAS_NORMALIZATION_CORRECTIVE`

Lane: `mating-unmating-force-alias-normalization-corrective`

## Implementation Review

The candidate product diff is limited to
`backend/modules/fee_evaluation/fee_rule_matcher.py`. Two full-label anchored
canonicalizers run before generic token extraction:

- complete base Mating/Unmating variants resolve to `mating un mating force`, the
  exact existing `50/sample` predicate key;
- complete combined Single Pin variants resolve to `single pin mating force`, retaining
  the existing `20/per reading` behavior.

The anchors prevent generic Mating/Unmating, partial force labels, and unrelated
labels from being normalized into either exception. Existing contact-retention/Lateral
and CPA/TPA/Automotive boundaries remain on their prior paths.

The new bounded test modules cover the accepted browser spelling variants, negative
families, combined Single Pin behavior, missing/invalid owning Group quantity, and the
two-Group production assembly. The latter uses distinct sample quantities and
divergent structured readings, then proves per-line Units and fees are `5/250` and
`9/450`; this rejects both cross-Group lookup and a readings multiplier.

## Scope And Validation

- Re-ran the new focused tests plus read-only TASK_363A/TASK_361L/default-fill/service
  regressions: `154 passed`.
- `py -m py_compile backend/modules/fee_evaluation/fee_rule_matcher.py` passed.
- Candidate physical lines are 135 for the matcher, 115 for the alias test, and 132
  for the two-Group test; all are below 500. The Developer evidence's earlier 136/148
  count is non-blocking but superseded here by the checked-out UTF-8 count.
- Candidate diff/trailing-whitespace checks are clean and the staged index is empty.
- `fee_reviewed_extension_defaults.py`, seed/manifest, frontend/API client, and all
  TASK_361L/TASK_363A paths have no TASK_363B candidate hunk. The visible
  `confirmed_matrix_fee_draft_service.py` worktree diff is external and excluded.

## Decision

`reviewer_pass`

Recommended next role/action: QA gate. QA should run the declared focused tests and a
disposable two-Group/API smoke only; do not access real DB/files or package the lane.

Blocking summary: none.
