# TASK_285 Fee Rule Seed Library Plan

> Status: superseded by completed execution plan and implementation
> Created: 2026-06-03
> Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
> Current active task: TASK_285_FEE_RULE_SEED_LIBRARY (planned)

## 1. Goal

Create a controlled, versioned fee rule seed library from the authoritative `Unit Price Reference` sheet so later fee-draft tasks can match Confirmed Matrix rows to reviewable pricing rules.

This task only creates the rule source, loader, validator, and deterministic matcher. It does not generate fee drafts, does not calculate project totals, does not write Excel files, and does not add a UI.

## 2. Inputs

### Confirmed Before Implementation

These inputs were confirmed before implementation:

1. Authoritative current fee reference workbook path.
   - Confirmed source: `D:\Source\Template\Testing Fee Evaluation-Even.xls`.
   - Required source sheet: `Unit Price Reference`.
   - Recorded source SHA256: `sha256:b19cce35f774ad3a83260805f7b717d5446f23ca1a90c209a08d8cb7f91fe226`.
2. `effective_from_basis` meaning.
   - Confirmed V1 basis: `project.sample_received_date`.
   - TASK_285 does not store a concrete project effective date. TASK_286 resolves this basis into `pricing_effective_from`.

### Runtime Input After Implementation

The runtime loader consumes only the reviewed structured seed file committed under the fee-evaluation module. Normal runtime code must not dynamically read arbitrary external Excel files for fee matching.

## 3. Outputs

1. A structured fee rule seed file with version metadata and rule entries.
2. Python dataclasses or typed value objects for fee rule versions, rules, match results, and validation errors.
3. A seed loader that validates metadata, required fields, duplicate aliases, and calculation strategy values.
4. A deterministic matcher that returns either a matched rule or a stable no-match result.
5. Unit tests for loading, validation, matching, duplicate aliases, review-required rules, and no-match behavior.

## 4. Scope Boundary

### In Scope

1. Add a bounded fee-evaluation module path.
2. Add one reviewed seed file for the active reference version.
3. Add loader and validation functions.
4. Add deterministic matching:
   - exact normalized alias match first;
   - conservative token match second;
   - no fuzzy or AI matching.
5. Preserve ambiguous rows as `review_required: true`.

### Out Of Scope

1. No Matrix-to-fee draft generation.
2. No API endpoint.
3. No frontend or Workbench UI.
4. No Excel export.
5. No SQLite fee-rule persistence.
6. No automatic import from arbitrary fee workbooks at runtime.
7. No modification of legacy `test_record_fee_*` services.
8. No changes to Matrix Editor, Test Record generation, report generation, or approval package behavior.

## 5. Proposed Module Shape

Add a new bounded module under:

```text
backend/modules/fee_evaluation/
  __init__.py
  fee_rule_models.py
  fee_rule_seed_loader.py
  fee_rule_matcher.py
  seeds/
    fee_rules_v2026_06_03.json
```

Rationale:

- `backend/modules` already hosts bounded implementation modules such as `test_plan`.
- TASK_285 is a rule-library and matching slice, not an application workflow yet.
- Later TASK_286 can depend on this module from an application service without making TASK_285 create an API or persistence layer.

## 6. Seed File Format

Use JSON for V1 because it is easy to review in diffs, deterministic to load, and does not add a dependency.

Top-level shape:

```json
{
  "version": {
    "version_id": "fee_rules_2026_06_03",
    "source_file_name": "Unit Price Reference workbook name.xlsx",
    "source_sheet": "Unit Price Reference",
    "source_hash": "sha256:<hex>",
    "effective_from_basis": "project.sample_received_date",
    "created_at": "2026-06-03T00:00:00+08:00"
  },
  "rules": [
    {
      "rule_id": "fee_rule_llcr",
      "display_name": "LLCR",
      "aliases": ["LLCR", "Low Level Contact Resistance"],
      "base_fee": {"amount": null, "text": ""},
      "unit_price": {"amount": null, "text": ""},
      "unit_label": "sample",
      "applicable_standard": "EIA-364-23 or reference text",
      "range_condition": "",
      "calculation_strategy": "per_sample",
      "review_required": false,
      "review_reason": null
    }
  ]
}
```

Rules where the workbook value is ambiguous, discounted, conditional, or judgment-based must preserve source text and set:

```json
{
  "calculation_strategy": "manual_required",
  "review_required": true,
  "review_reason": "Ambiguous source pricing text requires operator review."
}
```

## 7. Data Structures

Planned dataclasses:

```python
@dataclass(frozen=True, slots=True)
class FeeRuleVersion:
    version_id: str
    source_file_name: str
    source_sheet: str
    source_hash: str
    effective_from_basis: str
    created_at: str

@dataclass(frozen=True, slots=True)
class FeeAmount:
    amount: Decimal | None
    text: str

@dataclass(frozen=True, slots=True)
class FeeRule:
    rule_id: str
    display_name: str
    aliases: tuple[str, ...]
    base_fee: FeeAmount
    unit_price: FeeAmount
    unit_label: str
    applicable_standard: str
    range_condition: str
    calculation_strategy: str
    review_required: bool
    review_reason: str | None

@dataclass(frozen=True, slots=True)
class FeeRuleLibrary:
    version: FeeRuleVersion
    rules: tuple[FeeRule, ...]

@dataclass(frozen=True, slots=True)
class FeeRuleMatchResult:
    status: Literal["matched", "no_rule_match"]
    rule: FeeRule | None
    match_reason: str
    review_required: bool
```

## 8. Function Signatures

Seed loader:

```python
def load_fee_rule_library(path: Path) -> FeeRuleLibrary:
    """Load and validate one fee rule seed file."""
```

Validation helpers:

```python
def validate_fee_rule_library(library: FeeRuleLibrary) -> None:
    """Raise FeeRuleSeedValidationError for malformed rule data."""
```

Matcher:

```python
class FeeRuleMatcher:
    def __init__(self, library: FeeRuleLibrary) -> None:
        ...

    def match_test_item(self, text: str) -> FeeRuleMatchResult:
        """Match Matrix-style test item text to one fee rule."""
```

Normalization:

```python
def normalize_fee_rule_text(value: str) -> str:
    """Normalize aliases and Matrix item text for deterministic matching."""
```

## 9. Matching Rules

1. Normalize by trimming, lowercasing ASCII, collapsing whitespace, removing harmless punctuation, and preserving meaningful numeric/unit tokens.
2. Exact alias match wins.
3. Conservative token match may match only when all required alias tokens are present and the alias is configured as safe for token matching.
4. If more than one rule matches with equal strength, return no match with review-required reason rather than guessing.
5. Empty, unknown, or unsupported text returns `status="no_rule_match"`.

## 10. Tests

Add:

```text
tests/unit/test_fee_rule_seed_loader.py
tests/unit/test_fee_rule_matcher.py
```

Coverage:

1. Valid seed loads with metadata.
2. Missing required top-level fields fail with actionable errors.
3. Duplicate aliases fail validation.
4. Unknown calculation strategy fails validation.
5. Exact alias match succeeds for representative rules.
6. Conservative token match succeeds only for configured safe aliases.
7. Ambiguous duplicate token matches return no match or review-required result.
8. Manual/complex rules preserve `review_required`.
9. Unmatched Matrix text returns stable `no_rule_match`.

## 11. Validation Commands

Targeted validation:

```powershell
py -m pytest tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_matcher.py -q
```

Regression guard:

```powershell
py -m pytest tests/unit/test_test_record_fee_dataset_preview_service.py tests/unit/test_fee_evaluation_workbook_gateway.py -q
```

No frontend build is required because TASK_285 has no UI scope.

## 12. Risks And Mitigations

1. The authoritative workbook path is not yet confirmed.
   - Mitigation: block implementation until the selected file is confirmed.
2. `effective_from_basis` may be interpreted inconsistently.
   - Mitigation: record the user-confirmed meaning in the seed metadata and this task completion note.
3. Existing legacy fee services may tempt reuse.
   - Mitigation: do not modify them in TASK_285; treat them as historical reference only.
4. Seed rules may be incomplete.
   - Mitigation: V1 seed must be representative, conservative, and review-oriented; unmatched rules must not guess.
5. Alias collision could silently misprice later drafts.
   - Mitigation: duplicate alias and ambiguous-match tests are required before implementation closure.

## 13. Acceptance Criteria Mapping

1. Versioned seed file exists with source/version metadata.
2. Seed includes representative common families visible in the confirmed reference source.
3. Loader rejects malformed seeds with actionable errors.
4. Duplicate aliases are detected.
5. Matrix-style test item text can match deterministic aliases.
6. Ambiguous rules surface `review_required`.
7. Unmatched rows return stable no-match results.
8. Tests cover loading, validation, matching, and no-match behavior.
9. Scope boundary is held: no Matrix-to-fee generation, no UI, no Excel output.

## 14. Completion Note

Implementation was completed after:

1. This plan is reviewed and approved.
2. The authoritative `Unit Price Reference` workbook is identified.
3. The `effective_from_basis` meaning is confirmed as `project.sample_received_date`.

Final implementation details are recorded in `docs/task_285_fee_rule_seed_library_execution_plan.md` and `docs/task_board.md`.
