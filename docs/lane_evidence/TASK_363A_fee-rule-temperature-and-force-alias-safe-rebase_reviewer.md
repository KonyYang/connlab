# TASK_363A Reviewer Plan Gate

Date: 2026-07-17

Role: Reviewer

Status: reviewer_blocked

Task: `TASK_363A_FEE_RULE_TEMPERATURE_AND_FORCE_ALIAS_SAFE_REBASE`

Lane: `fee-rule-temperature-and-force-alias-safe-rebase`

## Blocking Finding

### B1: The lane documents contradict the task-board active-task source of truth

`docs/task_board.md` names `TASK_363A_FEE_RULE_TEMPERATURE_AND_FORCE_ALIAS_SAFE_REBASE`
as the current active planned-only task and declares this Reviewer plan gate as the
next legal action. In contrast, the task, plan, and Planner evidence each state that
the current board active task is `none`. The lane remains planned-only in both
accounts, but this is still an evidence/board contradiction at the required
phase/task/role/why-allowed checkpoint.

**Required bounded Planner fix:** update the current-active-task wording in the
TASK_363A task, plan, and Planner evidence to identify TASK_363A as the board's
current planned-only active task, while retaining that product implementation is
unauthorized. Do not change product code, tests, seeds, the board's product scope,
or any external residual.

## Review Notes

- The board confirms Phase 11 and TASK_363A as planned-only, ready for this plan
  gate, with implementation unauthorized.
- The product contract is otherwise sufficiently specific for a corrected plan:
  `Temperature life` is an exact `15/hour` alias; the four enumerated force labels
  are exact `20/reading` aliases; only exact normalized `Mating/Un-mating Force`
  keeps the `50/per sample` exception; Automotive/CPA/TPA aliases stay manual.
  Mechanical and Automotive are explicitly excluded from generic token fallback.
- Current repository facts support the proposed boundary: the active r5 seed lacks
  `Temperature life`, the r5 force extension still contains the broad aliases, and
  the default-fill helper still uses the broad substring branch that this lane
  confines for replacement.
- The safe-rebase read prerequisite already exists: both the pricing-draft store
  protocol and SQLite repository expose deterministic `get_latest_by_project()`
  ordering. The plan's application-layer May Touch list can use that existing
  read-only boundary without a schema, API DTO, frontend, or real-data change.
- Immutable next-seed activation, manifest-only rollback, prior-default
  reconstruction, field provenance, Pending/zero fail-closed handling, CAS, and
  load/Cancel zero-write behavior are appropriately bounded. Existing TASK_362A
  seed/draft/frontend/test and release residuals remain excluded.

## Validation Notes

- Read `AGENTS.md`, `docs/task_board.md`, the TASK_363A task/plan/Planner evidence,
  orchestration protocol, and task review checklist.
- Inspected the active manifest, r5 seed/extension, matcher, reviewed extension
  defaults, pricing-draft protocol/repository/service, and focused existing tests.
  The repository's `get_latest_by_project()` orders by `updated_at` then draft id,
  matching the planned deterministic latest-draft lookup.
- `git status --short` shows only TASK_363A governance files from this Planner pass;
  all visible backend/frontend/test/seed changes belong to pre-existing TASK_362A or
  release/dist residuals and were not reviewed as candidate product edits.
- No product code, tests, real database/files, staging, commit, or push was used.

## Decision

`reviewer_blocked`

Recommended next role/action: Planner fix pass for B1, then Reviewer plan re-gate.
Do not route Developer planning-first or product implementation.

Blocking summary: TASK_363A's task/plan/Planner evidence say the active task is
`none`, contrary to the task board's explicit TASK_363A planned-only active state.

---

# TASK_363A Reviewer Plan Re-Gate

Date: 2026-07-17

Role: Reviewer

Status: reviewer_pass

Task: `TASK_363A_FEE_RULE_TEMPERATURE_AND_FORCE_ALIAS_SAFE_REBASE`

Lane: `fee-rule-temperature-and-force-alias-safe-rebase`

## Re-Gate Result

B1 is closed. The task, plan, and Planner evidence now identify TASK_363A as the
current planned-only active task pending this Reviewer plan re-gate, matching
`docs/task_board.md`. They retain the explicit prohibition on product
implementation.

The business and implementation contract remains complete and bounded:

- exact normalized `Temperature life` maps to High temperature Life at `15/hour`;
- the four enumerated force labels map to Mechanical force at `20/reading`, with
  existing explicit/structured readings required;
- only exact normalized `Mating/Un-mating Force` retains the `50/per sample`
  exception, while force-family token fallback is excluded;
- Automotive/CPA/TPA aliases keep exact manual precedence;
- a new immutable seed/extension generation plus manifest-only activation and r5
  rollback preserve the accepted seed; and
- V2 safe rebase uses the existing deterministic latest-project draft read boundary,
  prior-seed default reconstruction, provenance-aware Pending/zero handling, CAS,
  and read-only load/Cancel behavior.

No Fee UI/API DTO/client, schema, Matrix/Point Profile/Measurement Plan authority,
workbook/Required Forms layout, real DB/files, or external TASK_362A/release
residuals enter the allowed package.

## Validation Notes

- Re-read the corrected TASK_363A task, plan, and Planner evidence against
  `docs/task_board.md`; all now state the same planned-only active-task and
  implementation-unauthorized condition.
- Targeted stale-status scan found no remaining `active task: none`, `board has no
  active task`, or obsolete pre-re-gate wording in the three corrected documents.
- Reconfirmed matcher/default-fill/r5 seed facts and the pricing-draft
  protocol/repository's deterministic `get_latest_by_project()` read contract.
- The target documents and this evidence have no trailing whitespace. Only TASK_363A
  governance files are present for the lane; all existing product/test/seed/release
  changes remain external and excluded. No product code, test, real DB/file,
  staging, commit, or push action occurred.

## Decision

`reviewer_pass`

Recommended next role/action: User approval, then Developer planning-first only.
Product implementation remains unauthorized until the later readiness, explicit
implementation approval, and source-of-truth reconciliation gates.

Blocking summary: none for the Reviewer plan re-gate.

---

# TASK_363A Reviewer Implementation-Readiness Gate

Date: 2026-07-17

Role: Reviewer

Status: reviewer_blocked

Task: `TASK_363A_FEE_RULE_TEMPERATURE_AND_FORCE_ALIAS_SAFE_REBASE`

Lane: `fee-rule-temperature-and-force-alias-safe-rebase`

## Blocking Finding

### B2: The board and lane governance have not been reconciled to the readiness gate

The new Developer evidence is a valid docs-only planning-first checkpoint, but the
current task board still names TASK_363A as `planned-only / ready for Reviewer plan
gate`, and the task and plan still say `pending Reviewer plan re-gate` with the
Planner governance-fix role. None of those sources records the completed Reviewer
plan pass, the user-approved Developer planning-first transition, or this requested
implementation-readiness gate.

The board/evidence source of truth therefore conflicts with the delegated readiness
status. A Reviewer implementation-readiness result must not itself repair that
governance state or infer implementation authorization.

**Required bounded Planner reconciliation:** update only the TASK_363A board row,
task/plan status wording, and reconciliation evidence to record the completed
Reviewer plan re-gate and docs-only Developer planning-first checkpoint, and to mark
the lane as ready for Reviewer implementation-readiness while retaining product
implementation as unauthorized. Do not modify product code, seeds, tests, API/UI,
schema, real DB/files, or external residuals.

## Review Notes

- The Developer evidence is internally consistent with a docs-only planning-first
  pass and preserves the exact alias/negative matrix, immutable seed/manifest
  rollback, V2 prior-default/provenance/CAS boundary, package locks, and validation
  matrix.
- Targeted status confirms no TASK_363A product candidate files exist; the visible
  Fee seed/service/frontend/test changes are pre-existing external TASK_362A
  residuals and remain excluded.
- This finding is governance-only. It does not reopen the Reviewer plan decision and
  does not authorize Developer product implementation.

## Validation Notes

- Re-read `AGENTS.md`, `docs/task_board.md`, TASK_363A task/plan, Planner/Reviewer/
  Developer evidence, and current candidate/product status.
- The board explicitly continues to state `ready for Reviewer plan gate`; the task
  and plan explicitly continue to state `pending Reviewer plan re-gate`; the
  Reviewer evidence contains `reviewer_pass`; and Developer evidence contains the
  docs-only planning-first checkpoint. This is the smallest source-of-truth mismatch.
- No product code, tests, real DB/files, staging, commit, or push action occurred.

## Decision

`reviewer_blocked`

Recommended next role/action: Planner source-of-truth reconciliation, then Reviewer
implementation-readiness re-gate. Do not route Developer product implementation.

Blocking summary: board/task/plan do not yet record the passed plan gate and
planning-first transition required to enter the readiness gate.

---

# TASK_363A Reviewer Implementation-Readiness Re-Gate

Date: 2026-07-17

Role: Reviewer

Status: reviewer_pass

Task: `TASK_363A_FEE_RULE_TEMPERATURE_AND_FORCE_ALIAS_SAFE_REBASE`

Lane: `fee-rule-temperature-and-force-alias-safe-rebase`

## Re-Gate Result

B2 is closed. The board, task, plan, Planner evidence, Developer evidence, and
Planner reconciliation evidence consistently record the passed Reviewer plan gate,
user-approved docs-only Developer planning-first checkpoint, and the current
implementation-readiness re-gate. Product implementation remains unauthorized.

The refined implementation sequence is ready for later approval:

- establish immutable r5 byte/hash baseline and candidate-seed tests before the
  manifest activation;
- apply exact-only matcher policy for the Mechanical and Automotive families, keep
  exact Automotive manual precedence, and limit the `50/per sample` default path to
  exact normalized `Mating/Un-mating Force`;
- preserve the explicit-hour and structured/explicit-reading default-fill paths for
  the new Temperature/force aliases;
- use the existing deterministic latest-project pricing-draft read boundary to build
  an in-memory V2 prior-rule transition candidate;
- reconstruct defaults from the bundled prior immutable seed, merge only fields
  proven system-owned, reject ambiguous Pending/zero/provenance/lineage states, and
  save only through the existing generation and old-snapshot CAS/revalidation flow;
  and
- validate the candidate, then make the single manifest activation change, with r5
  manifest selection as rollback.

The V2 envelope already carries row-level provenance as arbitrary field names, so
the planned `units` provenance refinement is contained in the authorized policy,
rebase, and persistence helpers. It requires no public DTO, API client, storage
schema, Matrix authority, Fee UI, or workbook change.

## Validation Notes

- Re-read `AGENTS.md`, board, TASK_363A task/plan, Planner/Reviewer/Developer/
  reconciliation evidence, and the active seed/matcher/default-fill/pricing-draft
  V2 boundaries.
- Confirmed all TASK_363A governance sources state ready for Reviewer
  implementation-readiness and implementation unauthorized; stale plan-gate wording
  is absent.
- Reconfirmed exact positive/negative alias matrix, retained exception, manual
  CPA/TPA/Automotive path, r5 immutable activation/rollback, latest-old-context read
  contract, field-level provenance/CAS/no-write failure design, and disposable
  regression matrix.
- No TASK_363A product candidate exists. Visible fee seed/service/frontend/test
  changes are external TASK_362A/TASK_361L residuals and remain excluded. No product
  code, tests, real DB/files, staging, commit, or push action occurred.

## Decision

`reviewer_pass`

Recommended next role/action: User implementation approval, followed by Planner
final source-of-truth reconciliation. Do not start Developer product implementation
until those two gates have completed.

Blocking summary: none for Reviewer implementation-readiness re-gate.

---

# TASK_363A Reviewer Implementation Gate

Date: 2026-07-17

Role: Reviewer

Status: reviewer_blocked

Task: `TASK_363A_FEE_RULE_TEMPERATURE_AND_FORCE_ALIAS_SAFE_REBASE`

Lane: `fee-rule-temperature-and-force-alias-safe-rebase`

## Blocking Findings

### B1: Rule-version transition does not reconstruct or verify the prior defaults

`fee_rule_transition_safe_rebase.py` loads the active automatic defaults at lines
30-36 and passes them directly to the rebase. Its only old-seed operation is the
boolean existence check at lines 79-84. The loaded immutable r5 library is never
used to rebuild the prior defaults or to verify the saved V2 automatic-defaults
fingerprint.

Consequently, a value such as a manually retained Unit Price, Units, or Base Fee
cannot be classified against the r5 system baseline required by TASK_363A. The code
also lets a prior seed with different alias/default behavior qualify merely because a
bundle with its version id exists.

### B2: Old-context candidate loading omits the required non-rule lineage guard

`load_rebase_candidate()` checks only Matrix id/revision, fee-rule id consistency,
and bundled-version existence at lines 57-63. It does not establish that the saved
Point Profile / Measurement Plan authority remains compatible before returning a
`rebase_required` candidate. The current source context contains Point Profile
facts, and a deterministic prior-default reconstruction can verify the legacy
automatic-default fingerprint; neither is used here.

This violates the frozen contract that changed lineage must fail closed, rather than
presenting a candidate that the operator can save under a changed authority.

**Required bounded Developer fix:**

1. Use the loaded immutable prior seed to construct prior automatic defaults through
   the planned injected prior-default builder. Compare its canonical fingerprint and
   row identities with the saved V2 source context before field ownership merge.
2. Require all non-rule authority lineage to match: compare saved/current source
   context fields that are independent of rule version, and fail closed when the
   reconstructed old-default fingerprint cannot prove unchanged Point Profile,
   Measurement Plan, or other automatic-default inputs.
3. Merge values only after those checks, using the reconstructed r5 defaults plus
   row provenance. Retain current r6 defaults solely as the target for a valid
   reviewed rebase.
4. Add disposable regressions for: a saved manual value differing from r5 default
   that remains preserved; an r5 system default that refreshes to r6; changed Point
   Profile/Measurement Plan lineage that returns typed `blocked` with zero write;
   unknown/invalid old seed or prior-default fingerprint mismatch that blocks; and
   a valid unchanged r5-to-r6 transition that remains CAS-saveable.

Keep the existing exact alias/default behavior, public API/DTO/schema locks, and
no-real-data boundary unchanged. Do not route QA or Integrator.

## Validation Notes

- Re-read board, task, reconciliation, Developer evidence, the complete candidate
  diff, V2 authority context/policy/rebase/persistence helpers, new transition
  helper, seed loader, matcher/default-fill changes, and the dedicated alias test.
- Re-ran focused matcher/default-fill/pricing-draft policy suite:
  `py -m pytest tests/unit/test_fee_rule_temperature_force_alias_safe_rebase.py
  tests/unit/test_fee_evaluation_pricing_draft_v2_rebase.py
  tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py
  tests/unit/test_fee_default_fill.py tests/unit/test_fee_rule_seed_loader.py -q`
  -> `130 passed`. The suite confirms the existing coverage but does not exercise
  prior-seed reconstruction or changed non-rule lineage blocking.
- Exact alias token fencing and the single exact `50/per sample` branch are scoped
  correctly. The candidate uses a new seed/extension and manifest activation; r5
  remains an external immutable baseline. Candidate Python application modules are
  below 500 physical UTF-8 lines.
- External TASK_362A/TASK_361L/frontend/API/release residuals remain excluded. No
  real DB/files, staging, commit, or push occurred during review.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer bounded fix pass for B1-B2, then Reviewer
implementation re-gate. Do not route QA or Integrator.

Blocking summary: the safe-rebase implementation validates old-seed existence but
does not reconstruct/attest old defaults or fail closed on changed non-rule lineage.

---

# TASK_363A Reviewer Implementation Re-Gate: B1-B2

Date: 2026-07-17

Role: Reviewer

Status: reviewer_pass

Task: `TASK_363A_FEE_RULE_TEMPERATURE_AND_FORCE_ALIAS_SAFE_REBASE`

Lane: `fee-rule-temperature-and-force-alias-safe-rebase`

## Re-Gate Result

B1 and B2 are closed. `fee_rule_transition_safe_rebase.py` now loads the immutable
saved-rule library, injects it into a prior default builder, and verifies both the
saved automatic-default fingerprint and ordered row identities before it creates a
reviewed candidate. Current r6 defaults are used only after that prior-state
attestation succeeds.

The V2 source context now also carries a deterministic confirmed Measurement Plan
status/revision/fingerprint projection. Candidate loading compares its non-rule
Matrix, Point Profile, and Measurement Plan lineage before rebase. Any missing or
changed lineage, old-seed failure, old-default fingerprint mismatch, or row-identity
mismatch returns typed `blocked` with no persistence action.

The exact alias policy remains bounded: the new Temperature and four force aliases
are exact-only; Mechanical and Automotive rules cannot enter generic token fallback;
only exact normalized `Mating/Un-mating Force` uses `50/per sample`; and CPA/TPA/
Automotive remains manual/Pending. The manifest selects the new r6 candidate while
r5 remains bundled for rollback and prior reconstruction.

## Validation Notes

- Directly reviewed the B1-B2 helper, V2 source-context/contract additions,
  dependency composition, and six new transition regressions. The tests cover
  changed/missing Point Profile or Measurement Plan lineage, prior fingerprint and
  row-identity mismatch, and a valid r5-to-r6 candidate that preserves manual Unit
  Price while refreshing automatic Units.
- Re-ran focused unit and API regression suite:
  `py -m pytest tests/unit/test_fee_rule_transition_safe_rebase.py
  tests/unit/test_fee_rule_temperature_force_alias_safe_rebase.py
  tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py
  tests/unit/test_fee_evaluation_pricing_draft_v2_rebase.py
  tests/unit/test_fee_default_fill.py tests/unit/test_fee_rule_seed_loader.py
  tests/integration/test_fee_evaluation_pricing_draft_compatibility_api.py
  tests/integration/test_confirmed_matrix_fee_draft_api.py
  tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py -q`
  -> `148 passed`.
- Re-ran focused `py_compile` for the TASK_363A application and Fee modules; it
  passed. `npm run build` passed with only the established Vite chunk-size warning.
  Diff check, trailing-whitespace scan, and physical UTF-8 line-count scan passed;
  all reviewed TASK_363A Python files are below the 500-line hard limit.
- External TASK_362A/TASK_361L/frontend/API/release/Test Points residuals remain
  excluded. No real DB/files, staging, commit, or push occurred.

## Decision

`reviewer_pass`

Recommended next role/action: QA gate. QA should run the declared disposable
backend/API rebase smoke, including the positive alias matrix, exact retained
exception, manual Automotive path, r5-to-r6 manual-field preservation, lineage
blocked/no-write cases, manifest rollback selection, and package isolation. Do not
route Integrator directly.

Blocking summary: none for Reviewer implementation re-gate.

---

# TASK_363A Reviewer Package-Isolation Re-Gate

Date: 2026-07-17

Role: Reviewer

Status: reviewer_pass

Task: `TASK_363A_FEE_RULE_TEMPERATURE_AND_FORCE_ALIAS_SAFE_REBASE`

Lane: `fee-rule-temperature-and-force-alias-safe-rebase`

## Accepted Baseline And Isolation

- Rebased the review on local `HEAD` `9e8dbe824334b7e41d55bbbd89d36a48a22edf7c`.
  Its controlled TASK_362A repair contains only the two 2026-07-16 seed identity
  changes and its baseline-repair evidence.
- Both committed r5 artifacts expose
  `fee_rules_v2026_07_16_r5` and the same approved source hash. The active manifest
  in `HEAD` still selects the 2026-07-16 baseline. Neither r5 artifact nor the
  TASK_362A repair evidence has a working-tree diff against `HEAD`.
- TASK_363A remains self-contained as an r6 transition: the new r6 seed/extension
  and manifest activation are its only seed changes, while the safe-rebase helper
  resolves the immutable r5 library by the saved version id for prior-default
  reconstruction and attestation.
- Existing TASK_361L/frontend/Test Points, release/dist, and other worktree
  residuals were inspected as external and excluded. No TASK_362A baseline hunk is
  included in the TASK_363A candidate package.

## Behavioral Regression Check

The prior implementation-gate conclusions remain valid against the accepted r5
baseline: exact Temperature and force aliases are fenced from token fallback, only
the normalized `Mating/Un-mating Force` exception receives `50/per sample`, and
CPA/TPA/Automotive stays manual. The rebase helper reconstructs the r5 defaults,
attests automatic-default fingerprint and row identity, and blocks on changed Point
Profile or Measurement Plan lineage before any reviewed-save path.

## Validation

- Re-ran:
  `py -m pytest tests/unit/test_fee_rule_temperature_force_alias_safe_rebase.py
  tests/unit/test_fee_rule_transition_safe_rebase.py tests/unit/test_fee_rule_seed_loader.py -q`
  -> `47 passed`.
- Rechecked the r5/r6 seed identities, manifest boundaries, candidate diff, staged
  index, diff check, candidate line counts, and external-residual scope. The staged
  index remains empty. `git diff --check` reported only established LF/CRLF notices.
- No real database/files were accessed or changed. No staging, commit, or push was
  performed.

## Decision

`reviewer_pass`

Recommended next role/action: QA package-isolation re-gate only. QA should validate
the disposable r5-to-r6 transition from the accepted `HEAD` baseline and preserve
the existing external-residual exclusions. Do not route Integrator directly.

Blocking summary: none for TASK_363A package-isolation Reviewer re-gate.

---

# TASK_363A Reviewer Package-Boundary Re-Gate

Date: 2026-07-18

Role: Reviewer

Status: reviewer_pass

Task: `TASK_363A_FEE_RULE_TEMPERATURE_AND_FORCE_ALIAS_SAFE_REBASE`

Lane: `fee-rule-temperature-and-force-alias-safe-rebase`

## Hunk Review

`backend/api/dependencies.py` contains exactly the reconciled composition change in
`_build_fee_evaluation_pricing_draft_service`:

1. Construct one local `measurement_plan_adapter` through the existing confirmed
   Measurement Plan consumer adapter.
2. Reuse it for `ConfirmedMatrixFeeDraftService`.
3. Pass that same adapter as the existing
   `FeeEvaluationPricingDraftPersistenceService(measurement_plan_provider=...)`
   dependency.

The zero-context diff has exactly `6` additions and `4` deletions (net `+2`). The
then-recorded `2214 -> 2216` count is a **superseded historical audit metric**. The
frozen checked-out UTF-8 physical-line convention, including blanks, is HEAD
`1958 -> 1960`; see the later metadata re-gate below. The hunk adds no branch,
validation, transformation, persistence operation, or authority decision. It is
therefore a narrow production-composition exception for the pre-existing oversized
root, not a general line-limit waiver.

## Boundary Verification

- The receiving persistence service already accepts and consumes
  `measurement_plan_provider` exclusively when it builds the V2 authority source
  context. The reviewed hunk supplies that dependency at the production call site;
  it does not alter the lineage or rebase business contract.
- QA evidence now explicitly supersedes its earlier whole-file exclusion with this
  exact hunk-level whitelist, retaining the exclusion for every other
  `dependencies.py` hunk/content.
- The committed TASK_362A r5 accepted baseline remains independent at
  `9e8dbe824334b7e41d55bbbd89d36a48a22edf7c`; neither r5 seed artifact nor its
  baseline-repair evidence is changed in the worktree. TASK_361L, LTR, frontend/Test
  Points, release/dist, real DB/files, and all other residuals remain excluded.

## Validation

- Reviewed the zero-context diff, default-context function body, persistence-service
  receiving boundary, QA package-isolation evidence, staged index, and accepted-r5
  baseline comparison.
- `py -m py_compile backend/api/dependencies.py
  backend/application/fee_evaluation_pricing_draft_persistence_service.py
  backend/application/fee_evaluation_pricing_draft_v2_authority_context.py` passed.
- `git diff --check` found no whitespace defect; only existing LF/CRLF notices were
  emitted. The staged index is empty.
- No product code was modified and no real DB/files were accessed. No stage, commit,
  or push occurred.

## Decision

`reviewer_pass`

Recommended next role/action: QA package-boundary/isolation re-gate only. QA must
validate this exact hunk-level whitelist with the accepted r5 baseline and continue
to exclude all external residuals. Do not route Integrator directly.

Blocking summary: none for Reviewer package-boundary re-gate.

---

# TASK_363A Reviewer Package-Boundary Metadata Re-Gate

Date: 2026-07-18

Role: Reviewer

Status: reviewer_pass

Task: `TASK_363A_FEE_RULE_TEMPERATURE_AND_FORCE_ALIAS_SAFE_REBASE`

Lane: `fee-rule-temperature-and-force-alias-safe-rebase`

## Source-Of-Truth Verification

- Reproduced the frozen checked-out UTF-8 physical-line commands: accepted HEAD is
  `1958` lines and the worktree candidate is `1960` lines, including blanks.
- `git hash-object backend/api/dependencies.py` is
  `916da2dce7d6e1b39994e2117d54792beb39716e`, matching the frozen worktree hash.
  The actual hunk remains `6` additions / `4` deletions, net `+2`, under
  `_build_fee_evaluation_pricing_draft_service` only.
- TASK, plan, Planner/reconciliation/package-boundary evidence, QA evidence, and
  board all record `1958 -> 1960` as the current metric. The prior `2214 -> 2216`
  wording is retained only as explicitly superseded historical audit context.
- The exact adapter reuse/provider-injection whitelist and the narrow oversized
  composition exception are unchanged. The accepted r5 baseline, TASK_362A/TASK_361L,
  LTR, frontend/Test Points, release/dist, real DB/files, and every unrelated
  residual remain excluded.

## Validation

- Rechecked line counts, git blob hash, `git diff --numstat`, zero-context diff, and
  staged index. The index remains empty.
- Reviewed QA's corrected hunk-level whitelist and its existing `148/148`
  disposable suite result; no product behavior was changed by this metadata pass.
- Governance diff check and trailing-whitespace scan passed. No product code was
  modified and no stage, commit, or push occurred.

## Decision

`reviewer_pass`

Recommended next role/action: QA metadata/package-isolation re-gate only. QA must
certify the corrected `1958 -> 1960` convention with the exact hunk whitelist before
any Integrator package action.

Blocking summary: none for Reviewer package-boundary metadata re-gate.
