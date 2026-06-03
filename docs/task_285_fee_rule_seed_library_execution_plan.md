# TASK_285 Execution Plan: Fee Rule Seed Library

## Task Context
- Current Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active Task: `TASK_285_FEE_RULE_SEED_LIBRARY`
- Why allowed now: It is marked as current active task on `docs/task_board.md` and not blocked by another active task.

## 1. Objective
Build a bounded, versioned fee-rule seed module that can load and validate a reviewed JSON seed file and provide deterministic matching from Matrix-style test item text to fee rules.

## 2. Confirmed Inputs
1. Authoritative `Unit Price Reference` source file:
   `D:\Source\Template\Testing Fee Evaluation-Even.xls`
2. Authoritative source sheet:
   `Unit Price Reference`
3. The seed records `effective_from_basis: "project.sample_received_date"`.
4. TASK_285 does not store a concrete project effective date. TASK_286 resolves the basis against the project and records `pricing_effective_from`.

Implementation must still wait for explicit approval of TASK_285 execution, but these source/semantic inputs are confirmed.

## 3. Scope (No-Expansion Policy)
In scope:
- Versioned seed file structure and version metadata.
- Rule data models (version + rule + amount + match result).
- Seed loader and strict structural validation.
- Duplicate-alias validation.
- Deterministic matcher: exact alias first, then conservative token fallback, else stable `no_rule_match`.
- Unit tests for happy path, duplicate validation, malformed seeds, exact match, token match, and no-match.
- Built-in seed loading should use `importlib.resources` so runtime behavior does not depend on the current working directory.

Out of scope:
- No fee draft generation.
- No Excel/COM export.
- No UI.
- No new DB persistence for fee rules.
- No `test_record_fee_*` workflow rewiring.

## 4. Proposed Files
- `backend/modules/fee_evaluation/__init__.py`
- `backend/modules/fee_evaluation/fee_rule_models.py`
- `backend/modules/fee_evaluation/fee_rule_seed_loader.py`
- `backend/modules/fee_evaluation/fee_rule_matcher.py`
- `backend/modules/fee_evaluation/seeds/fee_rules_v2026_06_03.json`
- `tests/unit/test_fee_rule_seed_loader.py`
- `tests/unit/test_fee_rule_matcher.py`

## 5. Data Model (Draft)
- `FeeRuleVersion` with:
  - `version_id`
  - `source_file_name`
  - `source_sheet`
  - `source_hash`
  - `effective_from_basis`
  - `created_at`
- `FeeAmount` with:
  - `amount: Decimal | None`
  - `text: str`
- `FeeRule` with:
  - `rule_id`
  - `display_name`
  - `aliases`
  - `base_fee`
  - `unit_price`
  - `unit_label`
  - `applicable_standard`
  - `range_condition`
  - `calculation_strategy`
  - `review_required`
  - `review_reason`
- `FeeRuleLibrary` with:
  - `version`
  - `rules`
- `FeeRuleMatchResult`
  - status: `matched | no_rule_match`
  - rule/status details
  - deterministic reason and whether review is required
- `FeeRuleSeedValidationError`

Allowed strategies:
`per_sample`, `per_reading`, `per_cycle`, `per_hour`, `per_photo`, `per_specimen`, `fixed_per_group`, `manual_required`, `unknown`.

## 6. Matching Rules
1. Normalize text:
   - lowercase, trim, collapse whitespace, replace punctuation with spaces.
2. Exact alias match wins.
3. Token fallback only when exact fails.
4. Token fallback condition:
   - all alias tokens must exist in input,
   - alias token ratio must be at least 2 tokens,
   - alias token match score includes full alias string containment and bounded ambiguity handling.
5. If multiple matches at same strength, return `no_rule_match` with explicit ambiguity reason.
6. If no match found, return stable `no_rule_match`.

## 7. Validation Rules
- Required top-level fields and rule fields must exist.
- `aliases` must be non-empty.
- `source_hash` must be `sha256:<hex>`.
- `effective_from_basis` must be a supported basis value. V1 supports `project.sample_received_date`.
- `created_at` is a date/iso8601-like string (parser-level check).
- Duplicate aliases are disallowed (case-insensitive normalized alias scope).
- Unknown strategy -> validation error.
- Duplicate `rule_id` -> validation error.

## 8. Test Coverage
- `tests/unit/test_fee_rule_seed_loader.py`:
  - valid seed loads
  - source file/sheet/hash and `effective_from_basis` metadata loads
  - missing metadata field fails
  - bad strategy fails
  - duplicate alias fails
  - duplicate rule_id fails
  - malformed json path/file -> action error
- `tests/unit/test_fee_rule_matcher.py`:
  - exact alias match
  - token fallback match
  - ambiguous token case -> `no_rule_match`
  - unmatched text -> `no_rule_match`
  - review-required preserved in match result

## 9. Risks
1. Seed rules are manually curated; coverage can be incomplete, so unmatched rows are intentionally explicit.
2. Overly broad token matching can over-match; algorithm will stay conservative and bias to `no_rule_match` when ambiguous.
3. Initial rule set quality depends on approved `Unit Price Reference` interpretation.

## 10. Exit Criteria
- All acceptance criteria in `tasks/TASK_285_FEE_RULE_SEED_LIBRARY.md` satisfied.
- Target tests pass.
- No touch to Matrix/factory/test-record/GUI/export logic.

