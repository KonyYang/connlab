# TASK_363B Mating Unmating Force Alias Normalization Corrective Plan

## Status

`complete / integrator_accepted` after Developer implementation, Reviewer gate, QA
contained smoke, and controlled Integrator packaging.

## 1. Discovery Summary

### Confirmed By User

- The browser label `MATING /UNMATING FORCE` is the same business rule as
  `Mating/Un-mating Force`.
- Case, whitespace around `/`, and the `Un-mating`/`Unmating` hyphen difference are
  irrelevant for this complete force name.
- The result remains `50/per sample`.
- Units equal the current Fee row's owning Confirmed Matrix Group sample quantity;
  there is no readings multiplier or cross-Group aggregation.
- Generic Mating/Unmating, Insertion, Withdrawal, Latch, CPA/TPA, and Automotive
  behavior must not broaden.
- Browser feedback also identifies `Single Pin Mating/Unmating Force`; this exact
  combined label must use the existing Single Pin `20/per reading` path. Existing
  `contact retention force` and `Lateral Force` remain `20/per reading`; a `Complete
  Units` message is a quantity blocker, not a missing Unit Type.

### Confirmed By Repository Evidence

- TASK_363A is accepted at `937688de` and r6 is active.
- `normalize_fee_rule_text()` lowercases and tokenizes with
  `[a-z0-9]+|[\u4e00-\u9fff]+`.
- Slash whitespace already normalizes away, but `Un-mating` becomes `un mating` and
  `Unmating` remains `unmating`.
- r6 has the exact alias `Mating/Un-mating Force`; Mechanical/Automotive token fallback
  is disabled.
- The `50/per sample` predicate currently checks only `mating un mating force`.
- TASK_361L source context fingerprints the canonical automatic defaults and compares
  the saved context against freshly computed defaults on load.
- No repository text contains the exact browser label; the user browser confirmation
  is the authority for that input fact.
- A read-only active-library probe produced:
  `contact retention force -> mechanical force / reading / 20`,
  `Lateral Force -> mechanical force / reading / 20`, while
  `Single Pin Mating/Unmating Force` and `MATING /UNMATING FORCE` returned no match.

### Planner Decision

This is a small backend-only corrective, not a seed-version or general force-matcher
lane. Keep r6 immutable. Add two anchored full-label canonicalizations before generic
token normalization: the base label reuses the accepted sample exception; the exact
Single Pin combined label reuses the existing Single Pin Mechanical force key and
therefore remains per reading. Align only the base per-sample predicate.

### Not Yet Confirmed

None blocking. Exact private symbol names may follow local style without changing the
frozen full-label grammar.

## 2. Frozen Normalization Design

Introduce a narrowly anchored, case-insensitive full-label rule equivalent to:

```text
^\s*mating\s*/\s*un\s*-?\s*mating\s+force\s*$
```

When it matches, return the canonical normalized value:

```text
mating un mating force
```

Otherwise, run the existing generic lowercase/token normalization unchanged. The
full-match requirement prevents `Single Pin ...`, missing-`Force`, or qualifier-bearing
labels from entering the exception. It also avoids deleting all whitespace globally.

Add a second full-label rule equivalent to:

```text
^\s*single\s+pin\s+mating\s*/\s*un\s*-?\s*mating\s+force\s*$
```

Canonicalize it to the existing r6 exact key `single pin mating force`. This is an
internal match key only; it does not rewrite user-visible Matrix text. Because the
per-sample predicate remains anchored to `mating un mating force`, the Single Pin
combined label follows the existing `20/per reading` Mechanical force path.

The existing exact alias map will normalize r6 `Mating/Un-mating Force` to the same
canonical key as every approved browser variant. No seed/extension/manifest change is
needed.

## 3. Default-Fill Boundary

Keep the existing Mechanical force per-sample predicate and calculator unchanged.
All approved complete base-family forms, including the accepted r6 hyphenated alias,
must canonicalize to its existing `mating un mating force` key. Default-fill tests must
prove that this matcher key reaches the existing contract:

- Unit Price `50`
- Unit Type `sample`
- Units exactly from the current row's owning Confirmed Matrix Group sample quantity
- no readings multiplier and no cross-Group aggregation
- missing quantity -> existing manual-review result

No Fee formula, rule price, discount, base-fee, or other alias behavior changes.

## 4. Safe-Rebase Boundary

Do not modify TASK_361L/TASK_363A persistence or rebase code. The existing automatic-
default fingerprint/currentness comparison is the reviewed compatibility boundary for
this code-level default change even though r6 remains active. Focused regressions must
prove the changed default becomes review/rebase-visible, stale saved values do not
silently override it, manual fields remain protected, and load/Cancel remains zero-write.

## 5. File-Level Plan

1. Add the two full-label canonicalizations to
   `backend/modules/fee_evaluation/fee_rule_matcher.py`.
2. Do not modify the default-fill production module. Use its focused tests to verify
   the existing per-sample predicate consumes the canonical matcher key.
3. Add the bounded focused module
   `tests/unit/test_fee_rule_mating_unmating_alias_normalization.py` for matcher
   positive/negative cases and default-fill contract calls through the public
   `build_fee_default_fill()` API. Keep the module at or below 500 physical lines.
4. Add the bounded focused module
   `tests/unit/test_confirmed_matrix_fee_draft_mating_unmating_units.py` for two-Group
   production assembly: distinct sample quantities, divergent Step readings, owning
   Group Units, no cross-Group/no multiplier behavior, and missing/invalid manual
   review. Keep it at or below 500 physical lines and reuse existing small fixtures
   where possible.
5. Treat the existing
   `tests/unit/test_fee_rule_temperature_force_alias_safe_rebase.py`,
   `tests/unit/test_fee_default_fill.py` (728 current physical lines), and
   `tests/unit/test_confirmed_matrix_fee_draft_service.py` (478 current physical lines)
   as read-only
   regression dependencies. Do not add TASK_363B tests to any of these files.
   The governing count command is
   `(Get-Content <path> -Encoding UTF8 | Measure-Object -Line).Lines`; any earlier
   incorrect-count checkpoint is superseded by the checked-out 728/478 facts.
6. Run existing pricing-draft safety tests without changing their product code.

`backend/modules/fee_evaluation/fee_reviewed_extension_defaults.py` and
`backend/application/confirmed_matrix_fee_draft_service.py` are inspected production
context, not authorized product May Touch paths. If focused regressions expose a defect
in either locked module, Developer must stop and return to Planner for a new scope
decision.

## 6. Package Isolation

TASK_363B packages only the `fee_rule_matcher.py` backend hunk, the two new focused test
modules, and its governance docs. It must not absorb accepted TASK_363A files unless they contain an
explicit TASK_363B hunk, TASK_364A docs, TASK_362A/TASK_361L/frontend/release residuals,
or any seed/manifest file. The shared dirty worktree requires hunk-level staging.

## 7. Validation

Positive matrix:

- `Mating/Un-mating Force`
- `MATING /UNMATING FORCE`
- `MATING/ UNMATING FORCE`
- `MATING / UNMATING FORCE`
- `MATING/UNMATING FORCE`
- lower/mixed-case and optional `Un-mating` combinations
- every base-label positive case uses Units equal to its own Group sample quantity
- `Single Pin Mating/Unmating Force`, slash-space/case variants, and its optional
  `Un-mating` form -> `20/per reading`

Negative matrix:

- `Mating/Unmating` and case/separator variants without `Force`
- generic `Mating Force`, `Unmating Force`, `Insertion Force`, `Withdrawal Force`
- `Latch`, `Latch Force`, `CPA force`, `TPA force`, `Automotive mechanical force`

Regression assertions also keep `contact retention force`, `Lateral Force`,
`Single Pin Mating Force`, and `Single Pin Unmating Force` at `20/per reading`; missing
readings must preserve Unit Type and ask only for Units.

Production assembly regression:

- create two Confirmed Matrix Groups with distinct sample quantities
- place a complete base Mating/Unmating Force alias variant in each Group
- provide divergent Step quantity/readings facts for the two rows
- assert each generated Fee line is `50/per sample` and Units equal only its owning
  Group sample quantity
- assert no cross-Group total, no other-Group quantity, and no readings multiplier
- assert missing or invalid owning Group sample quantity is typed manual-review
- retain Single Pin combined `20/reading`, contact retention/Lateral `20/reading`,
  no-`Force` generic negatives, and CPA/TPA/Automotive manual-review regressions

Commands:

```powershell
py -m pytest tests/unit/test_fee_rule_mating_unmating_alias_normalization.py -q
py -m pytest tests/unit/test_confirmed_matrix_fee_draft_mating_unmating_units.py -q
py -m pytest tests/unit/test_fee_rule_temperature_force_alias_safe_rebase.py tests/unit/test_fee_default_fill.py tests/unit/test_confirmed_matrix_fee_draft_service.py -q
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/unit/test_fee_evaluation_pricing_draft_v2_rebase.py -q
py -m py_compile backend/modules/fee_evaluation/fee_rule_matcher.py
git diff --check
```

Also verify no diff under `backend/modules/fee_evaluation/seeds/**`, no frontend/API
client changes, no real DB/file/output operation, and no unrelated staged hunk.

## 8. Definition Of Ready

Ready for Developer implementation. Scope, existing canonical key, grammar, positive
and negative cases, production owning-Group assembly regression, matcher-only product
boundary, immutable seed constraint, regression path, and package isolation are
explicit. Reviewer final B4R2 readiness passed and user implementation approval is
formally reconciled.

## 9. Developer Planning-First Refinement

### Exact future TDD order

1. Add red matcher positive/negative parametrizations first. They must fail on the
   combined browser labels while preserving all current negative and existing-positive
   expectations.
2. Add the default-fill contract tests second. They prove base aliases produce
   `50/sample` and owning Group quantity, while Single Pin remains `20/reading` and
   missing/invalid quantity stays typed manual-review. No default-fill production code
   is planned.
3. Add the test-only production assembly regression in
   `tests/unit/test_confirmed_matrix_fee_draft_mating_unmating_units.py`: two Confirmed Matrix Groups,
   distinct sample quantities, base alias in each, and divergent Step readings. It must
   prove per-line owning-Group Units with no cross-Group or readings multiplier. If this
   red test exposes a service defect, stop and return to Planner; the service is locked.
4. Only after those red tests are fixed, add two private, full-string canonicalization
   helpers in `backend/modules/fee_evaluation/fee_rule_matcher.py`. They run before the existing
   `_TOKEN_PATTERN` normalization and return `None` when the complete label grammar does
   not match. The base helper accepts optional whitespace around `/`, optional whitespace
   after `Un`, the optional `-`, and case variation, then returns
   `mating un mating force`. The Single Pin helper uses the same grammar and returns the
   existing exact alias key `single pin mating force`. No generic input has its spaces
   removed or its tokens rewritten.
5. Keep `_is_mechanical_force_per_sample()` and the default-fill production module
   unchanged. Default-fill tests prove that the canonical base key reaches the existing
   `50/sample`, owning Group quantity, and missing-quantity review contract.
6. Extend focused tests without changing r6 seed files, manifest, API DTOs, or the
   TASK_361A/TASK_361L currentness/rebase implementation. The tests must assert the
   matcher key and default-fill result separately so a Single Pin alias cannot enter the
   base sample exception.
7. Run the accepted TASK_363A alias/default suite and the narrow TASK_361L pricing-draft
   currentness/rebase suite as read-only compatibility checks. No production pricing
   draft or fingerprint code is planned for modification; the expected signal is that
   a changed computed default remains visible to the existing currentness boundary.

### Frozen helper contract

- `canonicalize_complete_force_alias(value: str | None) -> str | None` is anchored to
  the entire input and recognizes only the base `Mating / Un-mating Force` grammar.
- `canonicalize_complete_single_pin_force_alias(value: str | None) -> str | None` is
  anchored to the entire input and recognizes only the Single Pin combined grammar.
- The two helpers must be called by `normalize_fee_rule_text()` before generic token
  extraction, with the generic path unchanged for every non-match.
- The base canonical key is the only key accepted by the sample predicate. The Single
  Pin canonical key is resolved through the existing exact Mechanical force alias and
  therefore remains `20/per reading`.

### Required test nodes

- Base positive parametrization covers the six approved browser forms plus lower/mixed
  case and both `Un-mating`/`Unmating` spellings; each asserts Mechanical rule,
  `50/sample`, and Units equal to the supplied owning Group quantity.
- Single Pin positive parametrization covers slash spacing, case, and both hyphen forms;
  each asserts Mechanical rule, `20/reading`, and the existing readings quantity path.
- Negative parametrization covers missing `Force`, generic Mating/Unmating, Insertion,
  Withdrawal, Latch, CPA, TPA, and Automotive labels; none may receive the base sample
  exception or broaden to a new rule.
- Preservation parametrization covers `contact retention force`, `Lateral Force`,
  `Single Pin Mating Force`, and `Single Pin Unmating Force` at `20/reading`, including
  the existing Units-only review when readings are absent.
- `test_confirmed_matrix_fee_draft_mating_unmating_units.py` must prove the production
  assembly boundary with two Groups, different sample quantities, and divergent
  readings. The existing service test file is read-only and cannot receive new lines.
- Read-only TASK_361L regressions continue to prove automatic-default fingerprint
  currentness/rebase visibility, no silent stale overwrite, manual-field retention, and
  zero-write load/Cancel. These are validation-only and are not implementation targets.

### Package and validation boundary

The implementation package may contain only the `fee_rule_matcher.py` backend hunk, the
two new focused test modules (each <=500 physical lines), and TASK_363B governance/evidence.
A package check must prove no diff under
`backend/modules/fee_evaluation/seeds/**`, no frontend/API client or public DTO change,
no TASK_361A/TASK_361L code, and no release/dist, real DB/file, parser, workbook, or
external residual content. Physical UTF-8 line counts use
`(Get-Content <path> -Encoding UTF8 | Measure-Object -Line).Lines`; each new module
must remain below the 500-line Python hard limit. Required checks are focused pytest,
accepted TASK_363A/TASK_361L
regressions, `py_compile`, `git diff --check`, UTF-8 trailing whitespace, line-count,
seed-lock, forbidden-scope, and no-real-mutation scans.

## 10. Closeout

TASK_363B is complete/accepted. The package is limited to the matcher canonicalizer,
two bounded focused test modules, and TASK_363B governance/evidence. The external
LLCR API regression remains excluded for its owning lane; it is not a TASK_363B fix.
