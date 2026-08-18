# TASK_363A Fee Rule Temperature And Force Alias Safe Rebase Plan

## Status

Complete / Integrator accepted. The r5 baseline is accepted; the production
Measurement Plan provider change is limited to its exact approved fragments; and the
Reviewer/QA metadata re-gates plus final controlled package validation passed.

## 1. Discovery Summary

### Current Phase / Active Task / Role / Why Allowed

- Phase: Phase 11 controlled Matrix foundation.
- Active task: TASK_363A is complete/accepted.
- Final role: Integrator packaging/readiness.
- Allowed because Integrator proved that required production composition was
  authorized by the plan but contradicted by QA whole-file exclusion wording.

### Confirmed By User

- Temperature life is High temperature Life at `15/hour`, using explicit hours.
- Lateral Force, contact retention force, Single Pin Mating Force, and Single Pin
  Unmating Force are Mechanical force at `20/reading`.
- Broad Mating/Insertion/Withdrawal/Latch `50/per sample` inference must be removed or
  reduced to enumerated approved exceptions.
- CPA/TPA/Automotive mechanical force stays manual.
- Existing pricing drafts may receive new system defaults but manual fields must not
  be overwritten.
- No implementation, real data/file access, staging, commit, or push is authorized.

### Confirmed By Repository Evidence

- The active manifest selects `fee_rules_v2026_07_16.json`, version
  `fee_rules_v2026_07_16_r5`.
- Source row 4 is `fee_rule_high_temperature_life` at `15/hour`, but `Temperature
  life` is not an alias.
- Source row 22 is `fee_rule_mechanical_force` at `20/reading`; its reviewed extension
  currently contains broad Mating/Insertion/Withdrawal/Latch aliases.
- Source row 23 is the separate manual-required Automotive rule with CPA/TPA aliases.
- `FeeRuleMatcher` normalizes case/punctuation/newlines, tries exact alias first, then
  performs multi-token subset matching.
- `_is_mechanical_force_per_sample()` currently uses substring checks and sends broad
  mating/insertion/withdrawal/latch text to `50/per sample`.
- TASK_351 explicitly approved exact `Mating/Un-mating Force` at `50/per sample`, but
  its wider “force family” wording is superseded by the user's latest narrowing.
- TASK_361L V2 stores generation/context/fingerprints/provenance and CAS guards, but
  current provenance inference marks the editable manual-field set broadly; its rebase
  always refreshes Units/testing fee and preserves the other configured fields.
- Pricing-draft load currently queries the exact current rule-version context; an old
  rule-version row can appear missing instead of becoming a reviewed transition.
- The worktree contains accepted TASK_362A and release/dist residuals, including the
  current r5 seed/matcher-adjacent files. They are external to this Planner pass.

### Planner Inference

- Preserve accepted r5 artifacts and produce a new r6-equivalent 2026-07-17 candidate
  rather than editing r5 in place.
- Retain only exact normalized `Mating/Un-mating Force` as the explicit legacy
  50-per-sample exception because it is separately named in accepted TASK_351.
- Make Mechanical and Automotive rules exact-alias-only in the generic matcher; this
  prevents qualifier-bearing text from inheriting a shorter force alias.
- Treat an ambiguous numeric zero as manual/blocked unless V2/prior-default evidence
  positively proves system ownership.

### Not Yet Confirmed

- The final candidate version id and file date may be advanced by Integrator if a
  same-day version already exists at implementation time.
- No real-project browser smoke is authorized; disposable fixtures are the gate.
- These are non-blocking because version naming has a deterministic collision rule
  and real data is explicitly excluded.

## 2. Architecture Boundary

### Rule Layer

The source reference snapshot remains immutable. A new extension file changes only
reviewed aliases and runtime interpretation. The compiler creates a new candidate
seed; activation happens only after validation. This preserves source-row provenance
and rollback.

### Matcher Layer

Add a narrow rule-id policy to distinguish exact-only aliases from the existing
generic token matcher. Exact Automotive manual aliases have negative precedence.
TASK_363A aliases and the retained 50 exception are exact after the existing
normalizer. Unrelated rules retain current matching semantics.

### Default-Fill Layer

Replace the current substring-based 50-per-sample check with an exact normalized
allowlist containing only `Mating/Un-mating Force`. Every other Mechanical-force rule
uses `20/reading` and existing structured/explicit reading quantities; absent quantity
remains review-required. Temperature life reuses the existing hour parser.

### Pricing-Draft Layer

When exact current context is absent, inspect the latest project draft read-only. A
supported old-rule-version V2 draft becomes a reviewed transition candidate only if
all non-rule authority fingerprints remain compatible. Rebuild prior defaults with
the bundled prior seed and compare them to saved values before field merge.

The merge uses three ownership states:

- `system_default`: prior metadata/value/provenance proves system ownership; refresh;
- `manual`: explicit provenance or value differs from prior default; preserve;
- `ambiguous`: cannot prove ownership; block/fail closed.

Pending/blank may be system placeholders when prior metadata proves it. Numeric zero
requires positive system provenance; otherwise it is ambiguous. Units becomes a
provenance-aware editable field for rebase, while Testing Fee remains derived.

Reviewed save reuses TASK_361L generation/old-snapshot CAS and produces a new
`current_v2` generation only after server revalidation. Load/Cancel stays zero-write.

## 3. Exact File Plan

### TDD Step 1: Rule Candidate And Matcher Tests

- add focused cases in `tests/unit/test_fee_rule_seed_loader.py`
- add focused cases in `tests/unit/test_fee_rule_matcher.py`
- add new 2026-07-17 extension and compiled seed fixtures
- implement exact-only policy in `fee_rule_matcher.py` or a narrow alias-policy module
- update active manifest only after candidate tests pass

### TDD Step 2: Default Fill

- update focused cases in `tests/unit/test_fee_default_fill.py`
- replace broad substring 50-per-sample branch in
  `fee_reviewed_extension_defaults.py`
- verify explicit hours and mechanical readings behavior

### TDD Step 3: Safe Rebase

- add focused V2 rule-transition tests in a new narrowly named test module
- add prior-rule default reconstruction helper
- update V2 policy/rebase/persistence only as needed for field ownership and
  latest-old-context candidate loading
- use dependency composition only to inject the prior/current default builders

### TDD Step 4: Regressions And Isolation

- run TASK_351/TASK_361L/TASK_362A focused suites
- verify r5 remains byte-for-byte unchanged
- verify candidate package excludes every pre-existing TASK_362A/release residual

## 4. May Touch

Future implementation uses exactly the paths listed in the task. Any need for API
DTO/client, frontend visual, schema, workbook, Matrix authority, Point Profile, or
Measurement Plan changes stops for Planner/Reviewer re-gate.

## 5. Validation Matrix

### Matcher

- exact normalized positive aliases and punctuation/case/newline variants
- Automotive negative precedence
- generic-force no-token-fallback
- unrelated rule token-match regression
- alias uniqueness/source provenance/new version activation

### Default Fill

- Temperature life 48 hours -> price 15, type hour, units 48
- missing/conflicting hour -> review-required
- four new force aliases -> price 20, type reading
- structured readings -> deterministic Units; absent readings -> Pending
- Single Pin names never enter 50/sample
- exact retained exception does enter 50/sample
- generic Mating/Insertion/Withdrawal/Latch does not enter that branch
- CPA/TPA/Automotive remains manual

### Existing Draft Rebase

- old r5 V2 + exact unchanged authority -> reviewed candidate
- system Pending/blank refresh
- proved system zero refresh
- ambiguous zero blocks
- manual Unit Price/Units/Unit Type/Base Fee/Discount/Spend Time/Notes preserved
- Testing Fee recalculated
- V1/unknown seed/changed lineage/row mismatch/mixed provenance blocked
- load/Cancel zero-write
- stale generation/snapshot CAS -> `409`, winner unchanged
- reviewed save -> server revalidation -> `current_v2`

## 6. Risks And Controls

- **Alias overreach:** exact-only force policy and negative matrix.
- **Historical rule loss:** immutable r5 plus manifest rollback.
- **Manual overwrite:** prior-default reconstruction, provenance ownership states,
  ambiguous fail-closed, and field-level assertions.
- **Dirty worktree contamination:** new seed filenames, hunk-level staging, explicit
  whitelist, and external residual report.
- **Large service growth:** use narrow pure policy/helper modules; do not add rule
  transition logic to API routes.

## 7. Definition Of Ready

Ready for Developer implementation. Reviewer plan re-gate passed, the user approved
Developer planning-first, Developer completed planning-first as docs-only, Reviewer
implementation-readiness re-gate passed, and the user explicitly approved product
implementation. No blocking question remains. Implementation is authorized only
within the frozen scope and locks in this plan.

## 8. Developer Planning-First Refinement

### Current Code Anchors

- `backend/modules/fee_evaluation/seeds/active_fee_rule_seed.json` selects
  `fee_rules_v2026_07_16.json`; this r5 seed and its extension remain immutable.
- `fee_rule_seed_loader.py` loads the manifest-selected package and validates the
  compiled library; `fee_rule_seed_compiler.py` combines the approved reference
  snapshot with the reviewed extension before writing a candidate seed.
- `fee_rule_matcher.py` currently performs normalized exact alias matching followed by
  generic token-subset matching. The new force-family policy must be applied between
  those stages without changing unrelated rule matching.
- `fee_reviewed_extension_defaults.py` dispatches reviewed defaults and currently
  routes mechanical-force text through `_is_mechanical_force_per_sample`; that
  substring branch is the only default-fill replacement point for the retained
  exception.
- `fee_evaluation_pricing_draft_v2_policy.py` carries source-context and operator
  provenance; `fee_evaluation_pricing_draft_v2_rebase.py` currently merges the
  configured manual field set. The transition must add prior-rule default
  reconstruction and field ownership decisions without changing the public DTO.

### Exact Implementation Sequence After Explicit Authorization

1. Add red tests for r5 immutability, candidate version/source identity, positive and
   negative alias matrix, exact normalization, exact-only force-family priority, and
   manifest activation/rollback. Add a narrow alias-policy module only if keeping
   the policy out of `FeeRuleMatcher` reduces coupling.
2. Create the next immutable extension and compiled seed from the existing approved
   snapshot. Add `Temperature life` and the four exact mechanical aliases with their
   existing source rule IDs and prices. Keep only normalized exact
   `Mating/Un-mating Force` in the 50/sample exception metadata. Do not edit r5.
3. Update matcher policy so Automotive/CPA/TPA exact manual aliases win, the five
   TASK_363A positives are exact-only, and mechanical/Automotive rules cannot be
   selected by generic token-subset fallback. Generic token matching remains active
   for unrelated rules. Qualifier-bearing force text remains no-match or typed
   review-required unless another explicit exact alias owns it.
4. Update reviewed defaults: `Temperature life` uses the existing explicit-hours
   parser and remains Pending on missing/conflicting hours; the four force aliases
   use `20/reading` plus explicit or structured readings; only the retained exact
   exception uses `50/sample`. CPA/TPA/Automotive remains manual/Pending.
5. Add a pure prior-default reconstruction/transition helper under
   `backend/application/fee_rule_transition_safe_rebase.py` or an equally narrow
   application module. Load the latest old V2 draft read-only when current context
   is absent, resolve its bundled immutable seed, rebuild old defaults, and classify
   each field as system_default, manual, or ambiguous before merging current values.
6. Compose the prior/current default providers through the single frozen
   `_build_fee_evaluation_pricing_draft_service` hunk in
   `backend/api/dependencies.py`. Construct one local Measurement Plan adapter, reuse
   it for `ConfirmedMatrixFeeDraftService.contact_measurement_adapter`, and inject it
   as `FeeEvaluationPricingDraftPersistenceService.measurement_plan_provider`. Reuse
   TASK_361L CAS/current-V2 persistence; a
   rebase candidate is saved only after visible review and server revalidation.
   Load, Cancel, unknown seed, V1, changed lineage, row mismatch, mixed provenance,
   and stale CAS remain zero-write/fail-closed.
7. Validate the candidate library and extension/source provenance, then make one
   manifest-only activation change. Rollback is restoring the prior manifest value;
   no r5 file or source snapshot is rewritten.

### Field-Level Rebase Contract

The prior seed is authoritative only for reconstructing the old system default. A
saved value that differs from that default, or has explicit operator provenance, is
manual and is preserved. System Pending/blank values may refresh; numeric zero may
refresh only with positive system provenance. Ambiguous zero, unknown provenance,
and any conflicting source lineage block the row or draft. Manual Unit Price, Units,
Unit Type, Base Fee, Discount, Spend Time, Notes, and other operator fields are
never overwritten. Testing Fee is recalculated after the merge and is not treated as
an independent saved input.

### Exact Future May Touch / Locked Boundary

Future implementation may touch only the two new seed artifacts and
`active_fee_rule_seed.json` at activation time, `fee_rule_matcher.py`, an optional
`fee_rule_alias_policy.py`, `fee_reviewed_extension_defaults.py`, the narrow
`fee_rule_transition_safe_rebase.py`, the named TASK_361L V2 policy/rebase/
persistence helpers, dependency composition if required, focused backend tests, and
TASK_363A governance docs/evidence. Any public API DTO/client, frontend, schema,
workbook, Required Forms, Matrix/Point Profile/Measurement Plan, or authority change
requires a new Planner/Reviewer gate.

Locked: accepted r5 seed/extension/reference snapshot contents; Fee formulas or
prices outside the frozen aliases; `frontend/**`; public API DTO/client modules;
storage models/migrations; Matrix parser/import; Matrix Step/sample authority;
Point Profile/Measurement Plan; workbook writers and Required Forms layout; Generic
Test Record/Report; LTR/public-drive/folder workflows; real DB/files/output;
TASK_362A-C and release/dist residuals; `.agents/**`; `docs/project_management/**`;
remote push.

### Validation And Package Isolation

The implementation gate must run seed loader/compiler and r5 byte/hash regression;
matcher exact/negative/normalization/priority tests; default-fill hours/readings/
Pending tests; and disposable old-V2 transition tests covering prior-default rebuild,
system Pending/zero, manual preservation, unknown/V1/lineage/row mismatch,
load/Cancel zero-write, CAS `409`, and post-save `current_v2`. Then run focused
TASK_351, TASK_361L, and TASK_362A regressions, `py_compile`, physical UTF-8 line
counts, diff/trailing/whitelist/forbidden-scope/no-real-mutation scans. Candidate
files must be staged by explicit whitelist/hunks only; all existing r5/TASK_362A,
release/dist, frontend, parser, and unrelated worktree residuals stay excluded.

## 9. Accepted Baseline Reconciliation

- TASK_362A commits `614f4e5f` through `44f2073b` contain the main approved package.
- The exact r5 identity repair is independently accepted in
  `9e8dbe824334b7e41d55bbbd89d36a48a22edf7c`.
- TASK_363A starts from that accepted HEAD and does not absorb either r5 baseline
  seed hunk, TASK_362A governance, or any other external residual.
- Saved-version prior-default reconstruction therefore has a packageable immutable
  r5 source and the earlier baseline blocker is closed.

## 10. Production Composition Package Boundary

The `backend/api/dependencies.py` candidate contains one logical composition change,
split into three zero-context fragments (two default-context diff hunks), only inside
`_build_fee_evaluation_pricing_draft_service`. It is required because the production
pricing-draft source context must read the same effective Measurement Plan lineage as
automatic Fee defaults. Without `measurement_plan_provider`, lineage changes can be
missed by the production composition even though lower-level tests pass.

Exact whitelist:

1. Assign `measurement_plan_adapter` from
   `_confirmed_contact_measurement_consumer_adapter(session, get_settings())`.
2. Replace the existing inline automatic-default adapter construction with that local.
3. Inject the same local through the existing
   `FeeEvaluationPricingDraftPersistenceService(measurement_plan_provider=...)`
   constructor boundary.

The audited fragments total `6` additions / `4` deletions, net `+2`. Under the frozen
QA checked-out UTF-8 physical-line command convention, including blanks, the source
fact is HEAD `1958` -> worktree `1960`. The change adds no import, branch, validation,
transformation, persistence,
or business rule. `dependencies.py` is a pre-existing oversized composition root;
this narrow wiring exception does not waive the project size rule generally. Any
other hunk is forbidden, and decomposition of this module belongs to a separate
future lane. A new helper split is not required here because it would not remove the
production call-site wiring and would expand the current package.

QA package isolation must treat this exact hunk as TASK_363A-owned while excluding
all TASK_362A, TASK_361L, LTR, frontend, release/dist, and other content or hunks in
the same file. Reviewer package-boundary re-gate is next, followed by QA and
Integrator package isolation. No r5 pair is part of the TASK_363A package.
