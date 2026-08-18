# TASK_363A Fee Rule Temperature And Force Alias Safe Rebase

## Status

Complete / Integrator accepted. Developer implementation and bounded fixes, Reviewer
and QA package-boundary re-gates, and controlled final packaging passed.

## Lane

`fee-rule-temperature-and-force-alias-safe-rebase`

## Current Phase / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current board task: TASK_363A is complete/accepted.
- Current role: Integrator packaging/readiness.
- The accepted r5 baseline at `9e8dbe824334b7e41d55bbbd89d36a48a22edf7c` remains
  independent; the reconciled production composition hunk is packaged as TASK_363A.

## Goal

Correct deterministic Fee matching and defaults for Temperature life and approved
mechanical-force aliases, remove the broad force-family `50/per sample` fallback, and
make a fee-rule-version transition rebase existing pricing drafts without overwriting
provably manual fields.

## Gate History

- Reviewer plan re-gate: passed.
- User approval: Developer planning-first approved.
- Developer planning-first: complete as docs-only; no product candidate was written.
- Reviewer implementation-readiness re-gate: passed.
- User approval: product implementation explicitly approved.
- Developer implementation and bounded fix pass: complete.
- Reviewer implementation re-gate: passed.
- QA disposable gate: passed with `148 passed`.
- Planner package-boundary reconciliation and Reviewer/QA metadata re-gates: passed.
- Integrator: accepted with only the exact 6-addition/4-deletion composition hunk.
- No subsequent product lane is activated by this task.

## Accepted Baseline Resolution

TASK_363A loads the immutable prior rule set by saved version id
`fee_rules_v2026_07_16_r5`. The exact r5 identities are accepted in committed
baseline `9e8dbe824334b7e41d55bbbd89d36a48a22edf7c`; TASK_363A does not absorb the
two r5 baseline hunks.

The TASK_362A baseline repair is complete and accepted. TASK_363A packaging starts
from that committed baseline and excludes all TASK_362A and other external residuals.

## Authorized Production Composition Hunk

`backend/api/dependencies.py` is an existing oversized dependency-composition root.
TASK_363A may include exactly one logical composition change in
`_build_fee_evaluation_pricing_draft_service`:

1. Build local `measurement_plan_adapter` with
   `_confirmed_contact_measurement_consumer_adapter(session, get_settings())`.
2. Reuse that local as
   `ConfirmedMatrixFeeDraftService(contact_measurement_adapter=...)`.
3. Pass the same local as
   `FeeEvaluationPricingDraftPersistenceService(measurement_plan_provider=...)`.

No imports, other functions, business rules, authority semantics, or unrelated
composition may change. The audited fragments total `6` additions and `4` deletions,
net `+2`; the frozen checked-out UTF-8 physical-line metric, including blanks under
the QA command convention, is HEAD `1958` to worktree `1960`. This is a narrow
exception for pre-existing composition wiring, not authorization to grow business
logic in the file. Decomposing the oversized module is a separate future lane.

## Confirmed Business Contract

1. `Temperature life` maps exactly to `fee_rule_high_temperature_life`: Unit Price
   `15`, Unit Type `per hour`, Units from the existing explicit-hour parser.
2. `Lateral Force`, `contact retention force`, `Single Pin Mating Force`, and
   `Single Pin Unmating Force` map exactly to `fee_rule_mechanical_force`: Unit Price
   `20`, Unit Type `per reading`.
3. Mechanical-force Units use the existing approved explicit readings quantity path;
   missing readings remain Pending/review-required rather than using sample quantity
   alone.
4. Generic Mating/Unmating, Insertion, Withdrawal, and Latch text must not enter
   `50/per sample` through substring or token fallback.
5. The sole retained `50/per sample` exception is the exact normalized legacy
   business label `Mating/Un-mating Force`, previously approved by TASK_351. No other
   force text may use that exception without a later explicit business decision.
6. `CPA force`, `TPA force`, `Automotive mechanical force`, and the source canonical
   Automotive connector Mechanical force remain manual-required/Pending.
7. Existing pricing drafts may refresh only fields proved to be system defaults.
   Manual Unit Price, Units, Unit Type, Base Fee, Discount, Spend Time, Notes, and
   other operator-owned fields are preserved. Testing Fee remains derived.
8. Load and Cancel are zero-write. Rebase save uses TASK_361L CAS/current-V2 gates;
   stale or ambiguous provenance fails closed.

## Alias And Priority Contract

Normalization reuses `normalize_fee_rule_text`: trim, lowercase, and tokenize ASCII
letters/digits or contiguous CJK text; punctuation, slash, hyphen, whitespace, and
newlines collapse to single token separators. Display text is not rewritten.

Matching order is frozen:

1. exact normalized Automotive manual aliases;
2. exact normalized TASK_363A positive aliases;
3. exact normalized retained `Mating/Un-mating Force` exception;
4. existing exact aliases outside the changed force family;
5. existing generic token matching for unrelated rules only.

`fee_rule_mechanical_force` and `fee_rule_automotive_mechanical_force` must not be
selected by generic token-subset fallback. Exact mechanical aliases not named by this
task may continue to resolve to the source `20/per reading` rule, but none may invoke
the `50/per sample` exception unless it is the one retained exact label above.

### Positive Matrix

| Input | Rule | Unit Price | Unit Type | Quantity behavior |
|---|---|---:|---|---|
| `Temperature life` | high temperature life | 15 | per hour | explicit hours; otherwise Pending |
| `Lateral Force` | mechanical force | 20 | per reading | explicit/structured readings; otherwise Pending |
| `contact retention force` | mechanical force | 20 | per reading | explicit/structured readings; otherwise Pending |
| `Single Pin Mating Force` | mechanical force | 20 | per reading | explicit/structured readings; otherwise Pending |
| `Single Pin Unmating Force` | mechanical force | 20 | per reading | explicit/structured readings; otherwise Pending |
| `Mating/Un-mating Force` | explicit TASK_351 exception | 50 | per sample | Matrix group sample quantity |

### Negative Matrix

- Unapproved variants such as generic `Mating Force`, `Unmating Force`, `Insertion
  Force`, `Withdrawal Force`, `Latch`, `Latch Force`, `Latch strength`, and `Latch
  retention force` must never resolve to `50/per sample`.
- CPA/TPA/Automotive names remain typed manual-review/Pending, including inputs that
  also contain another force token.
- Qualifier-bearing strings do not inherit a TASK_363A exact alias by token subset.
  They either match another exact reviewed alias or remain manual/no-match.

## Rule Version And Seed Strategy

- Preserve accepted `fee_rules_v2026_07_16_r5` and its extension file unchanged.
- Create a new reviewed extension and compiled seed, proposed as
  `fee_rule_extensions_v2026_07_17.json` and `fee_rules_v2026_07_17.json`, with a new
  version id.
- Reuse the source snapshot/hash from TASK_362A; no runtime `.xls` read.
- Validate candidate, source provenance, alias uniqueness, positive/negative matrix,
  and default fill before changing `active_fee_rule_seed.json`.
- Activation is one isolated manifest change after validation; rollback is manifest
  selection of the accepted r5 seed.

## Pricing Draft Safe-Rebase Contract

Changing the active fee-rule version makes an old draft non-current. TASK_363A must
inspect the latest saved V2 draft when no exact current-context row exists; it must not
silently return `missing` and discard reviewable manual work.

An old draft is eligible for a reviewed rule-version rebase only when:

- Confirmed Matrix id/revision and Point Profile/Measurement Plan lineage are
  unchanged;
- saved row identities map one-to-one to current source rows;
- the saved fee-rule version identifies a bundled, immutable prior seed;
- prior backend defaults can be deterministically rebuilt from that seed;
- each field is classified from prior defaults plus V2 provenance.

Field policy:

- system Pending/blank values may refresh when the prior default metadata proves they
  were system/manual-required placeholders;
- numeric `0` may refresh only when trustworthy provenance proves it was system
  generated; ambiguous broad/legacy provenance blocks that field/row;
- any value differing from the reconstructed prior default is manual and preserved;
- explicit manual provenance always preserves Unit Price, Units, Unit Type, Base Fee,
  Discount, Spend Time, and Notes;
- Testing Fee is recalculated from the merged current values and is never restored as
  an independent stale value;
- unknown prior seed, changed lineage, duplicate/missing row identity, mixed
  provenance, or stale CAS returns typed `rebase_required`/`blocked`/`409` with no
  overwrite.

Load builds the candidate in memory and is zero-write. The operator must review and
save through the existing TASK_361L V2 CAS flow before Confirm/Update/export/Required
Forms/Matrix rebase can consume it. Only server-validated `current_v2` remains
consumable.

## May Touch For Future Implementation

- new `backend/modules/fee_evaluation/seeds/fee_rule_extensions_v2026_07_17.json`
- new `backend/modules/fee_evaluation/seeds/fee_rules_v2026_07_17.json`
- `backend/modules/fee_evaluation/seeds/active_fee_rule_seed.json`
- `backend/modules/fee_evaluation/fee_rule_matcher.py`
- optional narrow `backend/modules/fee_evaluation/fee_rule_alias_policy.py`
- `backend/modules/fee_evaluation/fee_reviewed_extension_defaults.py`
- optional narrow `backend/application/fee_rule_transition_safe_rebase.py`
- `backend/application/fee_evaluation_pricing_draft_v2_policy.py`
- `backend/application/fee_evaluation_pricing_draft_v2_rebase.py`
- `backend/application/fee_evaluation_pricing_draft_persistence_service.py`
- `backend/api/dependencies.py` only for the frozen
  `_build_fee_evaluation_pricing_draft_service` Measurement Plan adapter reuse and
  `measurement_plan_provider` injection hunk described above; every other hunk is
  excluded
- focused backend seed/matcher/default-fill/draft/CAS tests
- TASK_363A task/plan/evidence and precise board entries

## Must Not Touch

- accepted r5 seed/extension/source snapshot contents
- Fee formulas or prices outside the confirmed aliases
- Point Profile, Measurement Plan, Matrix Step, or sample-quantity authority
- Fee UI visual behavior, API DTOs, frontend API client, or workbook/Required Forms layout
- schema/migrations, real database/files, or real output generation
- TASK_362A, TASK_361L, release/dist, board, or other dirty residual cleanup

## Locked Paths

- `frontend/**`
- public API request/response DTO modules
- `backend/infrastructure/storage/models*.py` and migrations
- Point Profile and Measurement Plan modules
- Matrix parser/import modules
- workbook writers, Required Forms placement/layout, Generic Test Record/Report
- LTR/public-drive/folder workflows
- real DB/files and `dist_release/**`
- `.agents/**`, `docs/project_management/**`, remote push

## Acceptance Criteria

1. Each positive input matches the exact canonical rule, price, unit, and strategy.
2. Case, punctuation, slash/hyphen, whitespace, and newline variants normalize
   deterministically without widening to token-subset matching.
3. `Temperature life` with `48 hours` calculates Units `48` at `15/hour`; missing or
   conflicting hours stays review-required.
4. Each new mechanical alias uses `20/reading`; missing readings stays Pending.
5. `Single Pin Mating/Unmating Force` never enters `50/per sample`.
6. Only exact `Mating/Un-mating Force` retains `50/per sample`.
7. Generic Mating/Unmating/Insertion/Withdrawal/Latch variants do not silently use
   the 50-per-sample branch.
8. CPA/TPA/Automotive cases remain manual-required/Pending.
9. A disposable old V2 draft with proved system Pending defaults rebases to the new
   defaults; a proved system zero may rebase; ambiguous zero fails closed.
10. Manual Unit Price, Units, Unit Type, Base Fee, Discount, Spend Time, and Notes are
    preserved; Testing Fee is recalculated.
11. Load/Cancel performs no write; stale CAS returns typed `409` with no overwrite.
12. V1, unknown seed, changed authority lineage, or mixed provenance cannot become
    `current_v2` silently.
13. No real DB/file/output mutation occurs.

## Validation Gate

- seed compile/load/activation/diff tests with immutable r5 regression
- matcher positive/negative/normalization/priority matrix tests
- default-fill tests for Temperature life hours, force per-reading, retained exact
  exception, manual Automotive cases, and missing quantity review
- disposable V2 existing-draft tests for rule-version lookup, prior-default rebuild,
  system Pending/zero, manual-field preservation, row mismatch, V1/unknown seed,
  load/Cancel zero-write, CAS conflict, and current-V2 post-save
- focused TASK_351/TASK_361L/TASK_362A regressions, py_compile, diff/trailing/
  line-count/whitelist/forbidden-scope/no-real-mutation scans

## Merge Gate

Reviewer plan re-gate passed -> User approval for Developer planning-first recorded ->
Developer docs-only planning-first complete -> Reviewer implementation-readiness passed -> explicit User implementation
approval/reconciliation recorded -> Developer -> Reviewer -> QA disposable gate -> Integrator
hunk-isolated package.

## Definition Of Ready

Implementation scope and validation are complete, but Integrator acceptance remains pending. Goal, exact aliases, priority,
normalization, retained exception, negative matrix, seed versioning, safe-rebase
eligibility, field preservation, failure behavior, file ownership, validation, and
package isolation are explicit. The r5 baseline is committed; the exact production
composition boundary is now frozen and must pass Reviewer, QA, and Integrator re-gates.

## Blocking Questions

No business/design blocker. Reviewer must verify the exact composition hunk and its
oversized-file exception before QA/Integrator packaging resumes.
