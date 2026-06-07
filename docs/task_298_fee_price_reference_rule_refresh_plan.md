# TASK_298 Fee Price Reference Rule Refresh - Executable Plan

## Execution Context

- Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Active task: TASK_298_FEE_PRICE_REFERENCE_RULE_REFRESH.
- Allowed now because: TASK_297 is complete and the task board allows the next explicit task file and plan to be created for review.
- Status: complete.

## Model Fit Assessment

GPT-5.3-codex is suitable for this task. The work is bounded to deterministic rule-library modeling, validation, matcher behavior, and regression tests. It should preserve current fee behavior while preparing structured defaults for later editable Fee Evaluation tasks.

## Goal

Refresh the active fee pricing reference layer so later tasks can default Fee Evaluation editable fields from a controlled `Unit Price Reference` snapshot without making production runtime depend on Excel or hardcoded local paths.

## Scope

### In Scope

- Fee rule model constants and validation.
- Fee seed loader validation.
- Fee rule matcher hardening.
- Bundled active seed refresh evaluation. If the reference snapshot is unchanged, retain the current active seed and document the decision.
- Tests for validation, matching, and regressions.
- Task-board update after implementation.

### Out Of Scope

- Frontend editable cells.
- Frontend local fee calculation.
- Exporting edited values.
- Persisting fee edits.
- Database migration.
- Rule-maintenance UI.
- New production API endpoint.
- Runtime Excel/COM dependency for active rule loading.
- Matrix Editor or Test Record changes.

## File-Level Design

### `backend/modules/fee_evaluation/fee_rule_models.py`

Add an `ALLOWED_UNIT_LABELS` constant:

```python
ALLOWED_UNIT_LABELS: tuple[str, ...] = (
    "sample",
    "reading",
    "cycle",
    "hour",
    "day",
    "photo",
    "specimen",
    "group",
    "contact",
    "time",
    "report",
)
```

Do not remove or rename existing calculation strategies.

`time` is a canonical backend unit label in TASK_298 and means per occurrence / `每次`, not duration.

### `backend/modules/fee_evaluation/fee_rule_seed_loader.py`

Import `ALLOWED_UNIT_LABELS`.

Add validation in `validate_fee_rule_library()`:

```text
if rule.unit_label not in ALLOWED_UNIT_LABELS:
    raise FeeRuleSeedValidationError(...)
```

Keep existing validations:

- source sheet must be `Unit Price Reference`
- source hash format
- `effective_from_basis`
- duplicate aliases
- calculation strategy
- review-required reason

### `backend/modules/fee_evaluation/fee_rule_matcher.py`

Preserve the public result model and statuses.

Required behavior:

- exact normalized alias match remains first
- deterministic keyword/contains matching remains bounded
- longest/more-specific alias wins
- equal-score ties return `no_rule_match` with review-required ambiguity

Implementation should avoid returning a new status such as `ambiguous`.

### Bundled Seed

The active seed remains a bundled JSON file loaded by `load_active_fee_rule_library()`.

TASK_298 implementation decision:

- TASK_289 documented that `Testing Fee Evaluation-Even.optimized-v1.xls` preserved `Unit Price Reference` unchanged.
- Therefore TASK_298 does not create a new active seed version or replace `fee_rules_v2026_06_03.json`.
- Active seed metadata intentionally remains the TASK_285 reviewed source snapshot until a controlled future reference-update task.

If the seed is refreshed:

- preserve source metadata
- keep `effective_from_basis: "project.sample_received_date"`
- keep numeric amounts only when unambiguous
- keep conditional/ranged/special pricing review-required
- keep `group` and `specimen` labels where existing rules require them

### Optional Maintenance Helper

If source extraction from the optimized `.xls` is needed, it must be a controlled maintenance or test helper, not runtime loading.

If source sheet structure is ambiguous, stop and document manual curation needs instead of guessing.

## Tests

### Seed Loader Tests

Add or update tests in `tests/unit/test_fee_rule_seed_loader.py`:

- active seed loads
- source metadata and `effective_from_basis` load
- active seed metadata intentionally remains the original reviewed reference snapshot when no new reference snapshot is created
- `group` and `specimen` are accepted
- `contact` and `report` are accepted
- invalid unit label fails validation
- duplicate alias still fails validation

### Matcher Tests

Add or update tests in `tests/unit/test_fee_rule_matcher.py`:

- exact alias match
- keyword/contains alias match
- longest alias wins
- ambiguous equal-score match returns:
  - `status == "no_rule_match"`
  - `review_required is True`
  - review reason mentions ambiguity or multiple matched rules
- no new `FeeRuleMatchStatus` value is introduced

### Regression Tests

Run fee consumers that depend on the active rule library:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_fee_draft_service.py tests/integration/test_confirmed_matrix_fee_draft_api.py -q
py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_confirmed_matrix_fee_template_basic_fill_service.py -q
```

## Validation Commands

Run after implementation:

```powershell
py -m pytest tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_matcher.py -q
py -m pytest tests/unit/test_confirmed_matrix_fee_draft_service.py tests/integration/test_confirmed_matrix_fee_draft_api.py -q
py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_confirmed_matrix_fee_template_basic_fill_service.py -q
git diff --check
```

## Risks And Mitigations

- Risk: unit-label validation accidentally rejects existing seeds.
  - Mitigation: include explicit `group` and `specimen` regression tests.
- Risk: `time` is mistaken for duration.
  - Mitigation: document and test `time` as per occurrence / `每次`; duration-priced rules continue to use `hour` or `day`.
- Risk: matcher hardening changes API semantics.
  - Mitigation: keep `FeeRuleMatchStatus` unchanged and test ambiguous ties as `no_rule_match`.
- Risk: runtime becomes dependent on the local template path.
  - Mitigation: keep runtime on bundled JSON; use template path only as documented baseline or maintenance input.

## Completion Validation

Completed validation:

```powershell
py -m pytest tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_matcher.py -q -> 17 passed
py -m pytest tests/unit/test_confirmed_matrix_fee_draft_service.py tests/integration/test_confirmed_matrix_fee_draft_api.py -q -> 12 passed
py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_confirmed_matrix_fee_template_basic_fill_service.py -q -> 16 passed
```

Seed-loader tests explicitly assert that active seed metadata remains the original reviewed `Unit Price Reference` snapshot. Final `git diff --check` result is recorded in `docs/task_board.md`.

## Stop Point

After implementation and validation, update `docs/task_board.md` and stop. Do not proceed to TASK_299 editable UI without a separate approved task.
