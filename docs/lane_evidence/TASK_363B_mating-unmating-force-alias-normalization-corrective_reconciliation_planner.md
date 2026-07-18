# TASK_363B Planner B2/B3/B4R/B4R2 Reconciliation Evidence

Date: 2026-07-18

Role: Planner

Status: `implementation_authorized / pending_developer_implementation`

TASK_ID: `TASK_363B_MATING_UNMATING_FORCE_ALIAS_NORMALIZATION_CORRECTIVE`

Lane: `mating-unmating-force-alias-normalization-corrective`

## Gate Facts Reconciled

- Reviewer plan re-gate passed.
- User approved Developer planning-first.
- Developer docs-only planning-first completed.
- Reviewer implementation-readiness found B2/B3/B4R/B4R2 gaps, all subsequently
  reconciled.
- Reviewer final B4R2 implementation-readiness passed.
- User explicitly approved TASK_363B product implementation.
- Product implementation is authorized only within the frozen scope below.

## B2 Contract Resolution

The minimum contract is matcher-only. Every approved complete base
`Mating/Unmating Force` form, including the accepted r6 hyphenated alias, slash-space
variants, case variants, and `Un-mating`/`Unmating`, canonicalizes to the existing key
`mating un mating force`. The current default-fill predicate already accepts that key.

`backend/modules/fee_evaluation/fee_reviewed_extension_defaults.py` is therefore
locked production code and removed from May Touch. The combined Single Pin family
continues to canonicalize to `single pin mating force` and remains `20/per reading`.
All generic no-`Force`, Insertion/Withdrawal/Latch, CPA/TPA/Automotive, and other
negative/manual boundaries remain unchanged.

## B3 Source-Of-Truth Resolution

Task, plan, Planner evidence, Developer evidence, and board now record
`implementation_authorized / pending Developer implementation`. The B1 test-only
two-Group owning-sample-quantity regression remains required.

Future product May Touch is limited to `fee_rule_matcher.py`. Focused matcher/default,
TASK_363A/TASK_361L compatibility, and the two new bounded modules
`tests/unit/test_fee_rule_mating_unmating_alias_normalization.py` and
`tests/unit/test_confirmed_matrix_fee_draft_mating_unmating_units.py` remain authorized
validation. Existing `test_fee_rule_temperature_force_alias_safe_rebase.py`,
`test_fee_default_fill.py`, and `test_confirmed_matrix_fee_draft_service.py` are
read-only regression execution only and must receive no TASK_363B hunk. Both
default-fill production and confirmed Fee draft service production remain locked
inspected dependencies; a failing regression requires a new Planner scope decision.

## B4R Test-Module Reconciliation

- New matcher/default-fill assertions belong only to
  `test_fee_rule_mating_unmating_alias_normalization.py`.
- New two-Group assembly assertions belong only to
  `test_confirmed_matrix_fee_draft_mating_unmating_units.py`.
- Each new module must remain at or below 500 physical UTF-8 lines.
- Reviewer final readiness passed and the user's implementation approval is formally
  reconciled. Authorization remains limited to the frozen matcher/test scope.

## B4R2 Factual Count Reconciliation

- The current checked-out UTF-8 counts are 728 physical lines for
  `tests/unit/test_fee_default_fill.py` and 478 physical lines for
  `tests/unit/test_confirmed_matrix_fee_draft_service.py`.
- The governing count command is
  `(Get-Content <path> -Encoding UTF8 | Measure-Object -Line).Lines`.
- Any historical incorrect-count checkpoint in Reviewer history is retained only as a
  superseded checkpoint. It is not a current task, plan, May Touch, validation, or
  package fact.
- This correction changes no product contract or file ownership:
  both old tests remain read-only, the two new bounded test modules remain the only
  TASK_363B test implementation targets, and implementation is now authorized only
  within that exact boundary.

## Final Implementation Authorization

- Product May Touch: `backend/modules/fee_evaluation/fee_rule_matcher.py` only.
- New tests may be created only at
  `tests/unit/test_fee_rule_mating_unmating_alias_normalization.py` and
  `tests/unit/test_confirmed_matrix_fee_draft_mating_unmating_units.py`, each at or
  below 500 physical lines.
- Base complete aliases canonicalize to `mating un mating force`, retain `50/sample`,
  and use only the owning Group sample quantity. Single Pin combined aliases
  canonicalize to `single pin mating force` and retain `20/reading`.
- Contact retention/Lateral remain `20/reading`; generic no-`Force`,
  Insertion/Withdrawal/Latch, CPA/TPA/Automotive remain negative/manual boundaries.
- Default-fill and confirmed Fee draft service production, old 728/478 tests,
  seed/manifest, TASK_361L/TASK_363A rebase, frontend/API client, real DB/files, and
  all external residuals remain locked or read-only exactly as specified.

## Validation

- exact mandated UTF-8 count command returned 728 and 478
- current-governance stale-count scan found no incorrect historical count literals
- governance diff-check and UTF-8 trailing-whitespace scan passed
- stale canonical/status/May Touch scan passed
- final authorization scan confirmed task/plan/Planner/reconciliation/board all record
  `implementation_authorized / pending Developer implementation`
- targeted status confirmed no product or test implementation from this pass
- authorized matcher and new focused test targets remain unchanged or absent; the
  existing dirty confirmed Fee draft service remains an excluded external residual
- staging index remained empty

## Next Legal Role

Developer implementation pass.
