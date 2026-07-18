# TASK_363B Planner Discovery Evidence

Date: 2026-07-18

Role: Planner

Status: `implementation_authorized / pending_developer_implementation`

TASK_ID: `TASK_363B_MATING_UNMATING_FORCE_ALIAS_NORMALIZATION_CORRECTIVE`

Lane: `mating-unmating-force-alias-normalization-corrective`

## Current Phase / Why Allowed

Phase 11 controlled Matrix foundation. TASK_363A is complete/accepted at `937688de`.
The user confirmed a browser-discovered exact-label equivalence and requested a
separate narrow corrective lane. TASK_364A remains an unrelated proposed planning
item and is not activated by this pass.

## Evidence Read

- `AGENTS.md`, task board, Planner Discovery, parallel, orchestration, and role-thread
  protocols
- TASK_363A task/plan/Developer/Reviewer/QA/Integrator evidence and accepted commit
- current matcher, reviewed Mechanical force defaults, r6 seed/extension/manifest,
  and focused alias/default tests
- current git status/diff and external residuals

## Findings

- Existing normalization already ignores case and punctuation/slash spacing.
- The actual gap is token shape: `Un-mating` -> `un mating`, while `Unmating` ->
  `unmating`.
- The accepted r6 exact alias and `50/sample` predicate therefore do not cover the
  confirmed browser label together.
- The browser also shows `Single Pin Mating/Unmating Force`. A read-only active-rule
  probe confirms it is currently unmatched, while `contact retention force` and
  `Lateral Force` already resolve to Mechanical force `20/reading` and only lack Units
  when no readings quantity is available.
- Mechanical and Automotive token fallback remains blocked, so a full-label
  canonicalizer is sufficient without restoring broad matching.
- TASK_361L compares a saved source context with freshly computed canonical automatic
  defaults, including their fingerprint; no seed-version edit is required to make a
  changed default review/rebase-visible.
- The exact browser label is user-confirmed; repository search found no stored copy.

## Frozen Decision

- Use TASK_363B; no numbering conflict was found.
- Backend-only, full-label normalization corrective.
- Canonicalize only complete `Mating / Un-mating Force` variants to
  the existing `mating un mating force` key for the locked `50/sample` exception;
  Units equal the owning
  Confirmed Matrix Group sample quantity with no readings multiplier or cross-Group
  aggregation.
- Canonicalize only complete `Single Pin Mating / Un-mating Force` variants to the
  existing `single pin mating force` exact key for `20/reading`.
- Align the existing per-sample predicate; reuse existing r6 alias and calculator.
- Do not modify r6 seed/extension/manifest or safe-rebase code.
- Preserve all negative aliases and manual-review behavior.

## Scope

May Touch: matcher normalization as the only product candidate, the two bounded new
modules `tests/unit/test_fee_rule_mating_unmating_alias_normalization.py` and
`tests/unit/test_confirmed_matrix_fee_draft_mating_unmating_units.py`, and TASK_363B
governance.

Existing TASK_363A/default-fill/confirmed Fee draft/pricing-draft test modules are
read-only regression execution only. In particular, the current 728-line
`test_fee_default_fill.py` and 478-line `test_confirmed_matrix_fee_draft_service.py`
must receive no TASK_363B hunk.

These current checked-out UTF-8 facts use exactly
`(Get-Content <path> -Encoding UTF8 | Measure-Object -Line).Lines`. The prior
incorrect-count checkpoint is superseded and must not be used as current evidence.

`backend/modules/fee_evaluation/fee_reviewed_extension_defaults.py` is locked. Its
existing `mating un mating force` predicate and calculator are retained without a
production hunk.

`backend/application/confirmed_matrix_fee_draft_service.py` remains an inspected,
locked production dependency. The current code already passes the owning Group sample
quantity into each line's `FeeDefaultFillContext`; TASK_363B does not authorize a
service change. A failing assembly regression must return to Planner before any such
change.

Must Not Touch: seeds/manifest, frontend/API client, Fee prices/formulas/UI, authority
models, workbooks, real DB/files, TASK_363A history, TASK_364A, and external residuals.

Locked: Generic outputs, Matrix parser/import, LTR/public drive, release/dist,
`.agents/**`, `docs/project_management/**`, remote push.

## Reviewer B1 Fix

The validation scope now freezes a service-level regression with at least two
Confirmed Matrix Groups, distinct sample quantities, one base Mating/Unmating Force
alias variant per Group, and divergent Step readings. Assertions require each Fee
line's Units to equal only its owning Group sample quantity, with no cross-Group
aggregation, no other-Group quantity, and no readings multiplier. Missing/invalid
owning Group quantity remains typed manual-review. Single Pin combined `20/reading`,
contact retention/Lateral `20/reading`, generic no-`Force` negatives, and
CPA/TPA/Automotive manual behavior remain required regressions.

## Reviewer B2/B3 Fix

- Reviewer plan re-gate passed, the user approved Developer planning-first, and the
  docs-only Developer planning-first pass completed.
- Every approved complete base-family form, including the accepted r6 hyphenated alias,
  now canonicalizes to the existing key `mating un mating force`.
- Default-fill production is removed from May Touch and remains locked. Single Pin
  combined stays on `single pin mating force` and `20/reading`.
- The B1 test-only two-Group owning-quantity contract remains unchanged.
- Reviewer final B4R2 implementation-readiness passed; the user explicitly authorized
  product implementation, and this reconciliation activates only the frozen scope.

## Reviewer B4R Fix

- All newly authorized TASK_363B test code is confined to the two bounded modules
  named above, each subject to the 500-line hard limit.
- The two-Group owning-quantity assembly target moved to
  `test_confirmed_matrix_fee_draft_mating_unmating_units.py`.
- Old default-fill and confirmed Fee draft service tests are read-only regression
  execution only; they are not May Touch or new assembly destinations.
- Reviewer readiness passed and the user's implementation approval is now formally
  reconciled; implementation is authorized only within the frozen matcher/test scope.

## Reviewer B4R2 Factual Count Fix

- The read-only regression files are 728 and 478 lines under the mandated checked-out
  UTF-8 command `(Get-Content <path> -Encoding UTF8 | Measure-Object -Line).Lines`.
- This B4R2 fact supersedes any earlier incorrect-count Planner checkpoint without changing
  May Touch, test-module ownership, product contracts, or authorization state.

## Definition Of Ready

Satisfied for Developer implementation. User approval, existing canonical key,
positive and negative matrices, matcher-only product ownership, validation, and package
isolation are explicit. No blocker remains; all locks continue to apply.

## Validation Of This Planner Pass

- governance diff-check and trailing-whitespace scan
- targeted status confirms no product/seed/test/frontend/API-client change from this pass
- stale/duplicate TASK_363B ID scan
- staging index remains empty

## Next Legal Role

Developer implementation pass.
