# TASK_363B Mating Unmating Force Alias Normalization Corrective

## Status

`complete / integrator_accepted` after Developer implementation, Reviewer gate, QA
contained smoke, and controlled Integrator packaging.

## Lane

`mating-unmating-force-alias-normalization-corrective`

## Current Phase / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Upstream: TASK_363A is complete/accepted at
  `937688dea5f581258f66ec71b52220abe162c5f2`.
- Final role: Integrator packaging/readiness.
- Allowed after Developer implementation plus passed Reviewer and QA gates.

## Goal

Treat the complete business label `Mating/Unmating Force` as equivalent to the
accepted `Mating/Un-mating Force` label across case, slash-adjacent whitespace, and
the optional hyphen in `Un-mating`, while preserving the accepted `50/per sample`
result. Also recognize the exact browser label `Single Pin Mating/Unmating Force` as
the combined form of the accepted Single Pin aliases at `20/per reading`. Preserve
every TASK_363A negative boundary.

## Confirmed Business Contract

The following complete labels are one exact business family:

- `Mating/Un-mating Force`
- `MATING /UNMATING FORCE`
- `MATING/ UNMATING FORCE`
- `MATING / UNMATING FORCE`
- `MATING/UNMATING FORCE`
- corresponding case combinations and `Un-mating`/`Unmating` variants

For this family only:

- Unit Price: `50`
- Unit Type: `per sample`
- Units: the current Fee row's owning Confirmed Matrix Group sample quantity, with no
  readings multiplier and no cross-Group aggregation
- missing/invalid sample quantity: preserve the existing typed manual-review path

For the complete `Single Pin Mating/Unmating Force` family, with the same case,
slash-space, and optional-hyphen normalization:

- Unit Price: `20`
- Unit Type: `per reading`
- Units: existing explicit/structured readings path
- missing readings: keep Unit Price and Unit Type, with typed `Complete Units` review

Normalization must be full-label scoped. It may ignore case, whitespace around `/`,
and the optional hyphen between `Un` and `mating`; it must not remove arbitrary spaces
from other names or restore token-subset force matching.

## Negative Contract

- `Mating/Unmating` without `Force` does not enter this family.
- Generic `Mating Force`, `Unmating Force`, `Insertion Force`, `Withdrawal Force`,
  and `Latch` variants do not receive this `50/per sample` exception.
- `Single Pin Mating Force`, `Single Pin Unmating Force`, and their exact combined
  slash form remain TASK_363A `20/per reading` behavior and never enter `50/sample`.
- `CPA force`, `TPA force`, and `Automotive mechanical force` remain typed
  manual-review cases.

## Repository Facts

- `normalize_fee_rule_text()` already lowercases and tokenizes punctuation, so case
  and slash spacing are already insensitive.
- It currently produces `mating un mating force` for `Un-mating` and
  `mating unmating force` for `Unmating`; those forms are not equal.
- The accepted r6 seed already contains `Mating/Un-mating Force` as an exact
  Mechanical force alias.
- Mechanical and Automotive force token fallback is blocked.
- `_is_mechanical_force_per_sample()` currently accepts only
  `mating un mating force`.
- TASK_361L source-context currentness includes the canonical automatic-defaults
  fingerprint, so a changed computed default is review/rebase-visible even when the
  accepted r6 rule version remains unchanged.
- The exact browser string is confirmed by the user; it is not stored as a repository
  fixture or evidence artifact.
- A read-only matcher probe confirms `contact retention force` and `Lateral Force`
  already resolve to Mechanical force `20/reading`; only their Units remain reviewable
  when no readings quantity is available. The two combined slash labels currently
  return `no_rule_match`.

## Future Authorized May Touch

- `backend/modules/fee_evaluation/fee_rule_matcher.py`
- `tests/unit/test_fee_rule_mating_unmating_alias_normalization.py`
- `tests/unit/test_confirmed_matrix_fee_draft_mating_unmating_units.py`
- TASK_363B task/plan/evidence and the exact board row

The existing `tests/unit/test_fee_rule_temperature_force_alias_safe_rebase.py`,
728-line `tests/unit/test_fee_default_fill.py`, 478-line
`tests/unit/test_confirmed_matrix_fee_draft_service.py`, and focused pricing-draft
suites are read-only regression execution only. TASK_363B must not add or modify
tests in those existing modules.

The current checked-out UTF-8 line facts use exactly
`(Get-Content <path> -Encoding UTF8 | Measure-Object -Line).Lines`: 728 lines for
`test_fee_default_fill.py` and 478 lines for
`test_confirmed_matrix_fee_draft_service.py`. Any earlier incorrect-count checkpoint
is superseded and is not a current source-of-truth fact.

## Must Not Touch

- accepted r6 seed/extension or active manifest
- TASK_363A accepted commit/history
- general force token matching or unrelated normalization
- `backend/modules/fee_evaluation/fee_reviewed_extension_defaults.py`; the existing
  `mating un mating force` predicate and calculator are locked production behavior
- `backend/application/confirmed_matrix_fee_draft_service.py`; current code is an
  inspected dependency only. If the focused regression exposes a production defect,
  Developer must stop and return to Planner before modifying it.
- Fee price tables, discounts, UI, DTO, API client, workbook, or export layout
- Point Profile, Measurement Plan, Matrix quantity, or sample authority
- real database, operator files, public drive, or generated output
- current TASK_364A and all unrelated worktree residuals

## Locked Paths

- `backend/modules/fee_evaluation/seeds/**`
- frontend and public API/client DTO paths
- Generic Test Record/Report, Matrix parser/import, LTR/public drive
- `.agents/**`, `docs/project_management/**`, release/dist, remote push

## Acceptance Criteria

1. All frozen complete-label variants exact-match `fee_rule_mechanical_force`.
2. Base Mating/Unmating variants return Unit Price `50`, Unit Type `sample`, and
   Units exactly equal to the owning Confirmed Matrix Group sample quantity.
3. Single Pin combined variants return Unit Price `20`, Unit Type `reading`, and the
   existing readings path; missing readings reports only the Units blocker.
4. Normalization canonicalizes only the complete approved force labels; it does not
   globally delete spaces.
5. Contact retention and Lateral Force remain `20/per reading`; the frozen negative
   labels never receive the `50/per sample` exception.
6. CPA/TPA/Automotive remains manual and TASK_363A aliases remain unchanged.
7. Existing automatic-default fingerprint currentness, pricing-draft rebase, and
   manual-field protection regressions pass.
8. Accepted r6 seed/extension/manifest has no diff.
9. A production-assembly regression builds at least two Confirmed Matrix Groups with
   different sample quantities, base Mating/Unmating Force alias variants, and
   divergent Step readings. Each Fee line uses only its owning Group sample quantity;
   it does not aggregate Groups, read another Group quantity, or multiply by readings.
10. Missing or invalid owning Group sample quantity remains typed manual-review.
11. Every approved complete base-family form, including the accepted r6 hyphenated
    alias, canonicalizes to the existing key `mating un mating force`; no default-fill
    predicate change is required or authorized.

## Validation Gate

- `tests/unit/test_fee_rule_mating_unmating_alias_normalization.py`: bounded matcher,
  default-fill, positive, negative, and preservation regressions
- `tests/unit/test_confirmed_matrix_fee_draft_mating_unmating_units.py`: bounded
  two-Group owning-quantity isolation, divergent readings, and missing/invalid
  owning-quantity regressions
- existing TASK_363A/default-fill/confirmed Fee draft/pricing-draft suites execute
  read-only and receive no TASK_363B test hunk
- accepted TASK_363A alias/default regression suite
- focused TASK_361L pricing-draft safety regression as needed
- `py -m py_compile` for touched Python modules
- diff/trailing/line/whitelist/forbidden-seed/no-real-mutation scans

## Merge Gate

Reviewer plan gate passed -> user approved Developer planning-first -> Developer
planning-first complete -> Reviewer final B4R2 implementation-readiness passed ->
user implementation approval reconciled -> Developer -> Reviewer -> QA -> Integrator
hunk-isolated package.

## Definition Of Ready

Satisfied for Developer implementation. Reviewer final B4R2 readiness passed and the
user explicitly authorized product implementation. Authorization is limited to the
matcher-only product change and two bounded focused test modules defined in this task;
all Must Not Touch and Locked Paths remain in force.

## Closeout

TASK_363B is complete/accepted. The external LLCR API regression is retained as an
excluded residual for its owning lane; it does not reopen or expand this task.
