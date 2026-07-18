# TASK_363B Developer Planning-First Evidence

Date: 2026-07-18

Role: Developer

Status: `developer_implementation_complete / pending_reviewer_implementation_gate`

TASK_ID: `TASK_363B_MATING_UNMATING_FORCE_ALIAS_NORMALIZATION_CORRECTIVE`

Lane: `mating-unmating-force-alias-normalization-corrective`

## Current Phase / Why Allowed

Phase 11. TASK_363B is the active planned-only lane, explicitly approved by the user
for Developer planning-first after TASK_363A was accepted at
`937688dea5f581258f66ec71b52220abe162c5f2`. Product implementation remains
unauthorized at the start of this pass; implementation stayed within the reconciled
TASK_363B authorization.
The user's implementation-approval intent is recorded but cannot start implementation
before Reviewer readiness and final source-of-truth reconciliation.

## Source Context Reconciled

- `fee_rule_matcher.py` currently performs lower-case token extraction. Slash spacing
  is naturally ignored, but `Un-mating` and `Unmating` produce different normalized
  token keys.
- r6 already owns the accepted `Mating/Un-mating Force` alias and the active manifest;
  no seed or manifest change is needed.
- `_is_mechanical_force_per_sample()` currently recognizes only the hyphenated token
  shape. Its existing calculator correctly uses the owning Group sample quantity.
- The accepted Single Pin individual aliases, `contact retention force`, and `Lateral
  Force` already use the Mechanical `20/per reading` path; the combined Single Pin
  slash label is the only planned matching gap.
- Mechanical and Automotive token-subset fallback is already blocked. CPA/TPA/
  Automotive remains manual review.
- TASK_361L currentness compares the saved automatic-default fingerprint against newly
  computed defaults. It is a read-only compatibility regression for this lane, not a
  target for code changes.

## Implementation-Readiness Strategy / TDD Order

1. First add red matcher positive/negative tests for the complete browser labels and
   all frozen negative/legacy-positive labels.
2. Add the new bounded
   `tests/unit/test_fee_rule_mating_unmating_alias_normalization.py` for default-fill
   contract coverage, then the new
   `tests/unit/test_confirmed_matrix_fee_draft_mating_unmating_units.py` for the
   two-Group production assembly regression. Each new module is frozen at <=500 physical
   lines. If assembly exposes a service defect, stop and route Planner because
   `confirmed_matrix_fee_draft_service.py` is locked.
3. Add anchored full-label canonicalization in `fee_rule_matcher.py` only. Base forms
   canonicalize to the existing `mating un mating force`; Single Pin combined forms canonicalize to
   the existing `single pin mating force` key. The generic normalizer remains unchanged
   for non-matches, so arbitrary spaces and unrelated labels are not rewritten.
4. Keep the existing Mechanical sample predicate and default-fill production module
   unchanged. Default-fill tests prove that the canonical base key reaches the accepted
   `50/sample` contract without changing calculator behavior.
5. Add focused matcher/default-fill parametrizations for all approved positive and
   negative forms, Group-quantity Units, Single Pin readings, and preservation of
   contact-retention/Lateral/individual Single Pin behavior in the new modules. Existing
   `test_fee_default_fill.py` (728 current lines) and
   `test_confirmed_matrix_fee_draft_service.py` (478 current lines) remain read-only.
6. Run the accepted TASK_363A alias/default tests and narrow TASK_361L currentness/
   rebase tests as compatibility checks. Load/Cancel remains zero-write and manual
   fields remain protected.

## May Touch / Locked Boundary

May Touch only:

- `backend/modules/fee_evaluation/fee_rule_matcher.py`
- `tests/unit/test_fee_rule_mating_unmating_alias_normalization.py`
- `tests/unit/test_confirmed_matrix_fee_draft_mating_unmating_units.py`
- TASK_363B plan and governance evidence

Locked: `backend/modules/fee_evaluation/fee_reviewed_extension_defaults.py`,
`backend/application/confirmed_matrix_fee_draft_service.py` production code, the
existing 728-line `tests/unit/test_fee_default_fill.py` and 478-line
`tests/unit/test_confirmed_matrix_fee_draft_service.py` (read-only regressions), r6
seed/extension/manifest, TASK_363A history, TASK_361L production code,
frontend/API client/DTOs, Fee UI/pricing tables, Point Profile/Measurement Plan/Matrix
authority, workbooks/generic outputs, parser/import, LTR/public drive, real DB/files,
release/dist, `.agents/**`, `docs/project_management/**`, remote push, and unrelated
worktree residuals.

## Validation Plan

- `py -m pytest tests/unit/test_fee_rule_mating_unmating_alias_normalization.py -q`
- `py -m pytest tests/unit/test_confirmed_matrix_fee_draft_mating_unmating_units.py -q`
- Existing `test_fee_default_fill.py` and `test_confirmed_matrix_fee_draft_service.py`
  suites run read-only for regression.
- Existing `test_fee_rule_temperature_force_alias_safe_rebase.py` also runs read-only;
  all new TASK_363B assertions belong to the two bounded modules.
- Accepted TASK_363A alias/default regression suite.
- Read-only TASK_361L pricing-draft currentness/rebase regression.
- `py -m py_compile backend/modules/fee_evaluation/fee_rule_matcher.py`.
- Physical line count uses exactly
  `(Get-Content <path> -Encoding UTF8 | Measure-Object -Line).Lines` and must report
  each new focused module at <=500; existing 728/478-line modules are not modified.
- `git diff --check`, UTF-8 trailing whitespace, physical line-count, seed-lock,
  forbidden-scope, whitelist, and no-real-mutation scans.

No product code, seed, frontend, API client, database, file, stage, commit, or push
action outside the authorized matcher change and two new test modules occurred.

## Implementation Evidence

- TDD red phase: the new modules initially failed 11 cases for unrecognized base and
  combined Single Pin labels.
- Product change is limited to `backend/modules/fee_evaluation/fee_rule_matcher.py`:
  two anchored full-label regex canonicalizers run before generic token extraction.
  Base variants resolve to `mating un mating force`; combined Single Pin variants
  resolve to `single pin mating force`; generic normalization remains unchanged.
- New modules are `tests/unit/test_fee_rule_mating_unmating_alias_normalization.py`
  (136 physical lines) and
  `tests/unit/test_confirmed_matrix_fee_draft_mating_unmating_units.py` (148 physical
  lines), both below the 500-line limit.
- New focused tests passed: `25 passed`. The two-Group assembly regression proves
  owning-Group Units `5` and `9` despite divergent Step readings; missing/invalid
  quantity remains typed manual review.
- Read-only regression set passed: `154 passed`, including the existing 728-line
  default-fill suite, existing 478-line Confirmed Matrix Fee service suite,
  TASK_363A alias/defaults, and TASK_361L pricing-draft persistence/rebase safety.
- `py_compile`, task diff-check, UTF-8 trailing whitespace, physical line-count, and
  locked-scope scans passed. No frontend build was needed because frontend/API paths
  were untouched.

## Planning-First Validation

- `git diff --check` on the TASK_363B plan/evidence passed; only the repository's
  existing LF/CRLF warnings are present elsewhere in the dirty worktree.
- UTF-8 trailing-whitespace scan on both touched governance files is clean.
- Targeted status confirms the only new TASK_363B files are the plan and this evidence;
  existing backend/frontend/test changes are external residuals and no TASK_363B
  product file was modified.
- B4 planning correction is recorded: the existing 728-line
  `test_fee_default_fill.py` and 478-line `test_confirmed_matrix_fee_draft_service.py`
  are read-only dependencies; future TASK_363B tests belong to two new bounded
  modules, each frozen at <=500 physical lines.
- Future physical line-count validation is explicitly based on
  `(Get-Content <path> -Encoding UTF8 | Measure-Object -Line).Lines` for every new
  module. This 728/478 B4R2 fact supersedes the earlier incorrect-count checkpoint.
- No implementation, dependency, seed, manifest, staging, commit, push, or real-file
  operation was performed.

## Next Legal Role

Reviewer implementation gate.
