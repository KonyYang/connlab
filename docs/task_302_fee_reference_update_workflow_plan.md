# TASK_302 Fee Reference Update Workflow - Executable Plan

## Summary

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_302_FEE_REFERENCE_UPDATE_WORKFLOW`, complete.

This plan was reviewed and approved before implementation.

TASK_302 adds a controlled maintenance workflow for future `Unit Price Reference` changes. It should allow a reviewed structured candidate update to become a new bundled fee-rule version with validation, diff reporting, and explicit activation, while keeping production runtime on bundled JSON through `load_active_fee_rule_library()`.

## Step 1 - Task Understanding

Goal:

- Create a controlled way to generate, review, validate, diff, and activate a new fee-rule seed version from future Unit Price Reference updates.

Inputs:

- Current active bundled fee-rule seed.
- Future reviewed Unit Price Reference source data represented as structured candidate rows.
- Candidate version metadata.

Outputs:

- Candidate bundled JSON seed.
- Candidate-vs-active diff report.
- Explicit activation of a reviewed bundled seed.
- Tests proving runtime still uses bundled JSON and stale boundaries still hold.

Modules involved:

- `backend/modules/fee_evaluation`
- `tests/unit`
- task docs and task board

Not allowed:

- No frontend rule-maintenance UI.
- No production API for arbitrary workbook upload.
- No production runtime Excel/COM dependency.
- No automatic activation.
- No database-backed rule-version store.
- No pricing judgment beyond preserving review-required ambiguity.

## Design Decisions

### V1 Boundary

V1 should be a backend maintenance/testable workflow, not an operator UI.

The workflow has three separated phases:

1. Candidate build: produce a candidate `FeeRuleLibrary` JSON payload.
2. Candidate review: generate a deterministic diff report against the active bundled seed.
3. Activation: explicitly point the active bundled seed loader at a reviewed candidate seed.

Production calls such as fee draft generation, Fee Form export, pricing draft load/save, and page load must not read Excel or an absolute template path.

### Candidate Source Shape

TASK_302 V1 does not parse `.xls` / `.xlsx` workbooks directly. It uses a controlled structured intermediate representation for candidate rows:

```python
@dataclass(frozen=True, slots=True)
class FeeReferenceCandidateRow:
    rule_id: str
    display_name: str
    aliases: tuple[str, ...]
    base_fee_amount: Decimal | None
    base_fee_text: str
    unit_price_amount: Decimal | None
    unit_price_text: str
    unit_label: str
    applicable_standard: str
    range_condition: str
    calculation_strategy: CalculationStrategy
    review_required: bool
    review_reason: str | None
```

Workbook/sheet extraction into this representation is a later task unless separately approved. The core candidate builder consumes this representation, so tests do not need Office and production runtime stays independent of Excel/COM.

### Candidate Metadata

Use the existing `FeeRuleVersion` shape.

Candidate metadata must include:

- `version_id`
- `source_file_name`
- `source_sheet`
- `source_hash`
- `effective_from_basis`
- `created_at`

`source_hash` must keep current format:

```text
sha256:<64 lowercase hex>
```

`effective_from_basis` remains:

```text
project.sample_received_date
```

### Diff Semantics

Diff by `rule_id`.

Use a simple report DTO:

```python
@dataclass(frozen=True, slots=True)
class FeeRuleFieldChange:
    field_name: str
    before: str
    after: str

@dataclass(frozen=True, slots=True)
class FeeRuleDiffEntry:
    rule_id: str
    status: Literal["added", "removed", "changed", "unchanged"]
    display_name: str
    field_changes: tuple[FeeRuleFieldChange, ...]

@dataclass(frozen=True, slots=True)
class FeeRuleLibraryDiff:
    active_version_id: str
    candidate_version_id: str
    added_count: int
    removed_count: int
    changed_count: int
    unchanged_count: int
    entries: tuple[FeeRuleDiffEntry, ...]
```

Changed fields:

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

### Activation Semantics

Keep activation intentionally small:

- Candidate JSON is placed under `backend/modules/fee_evaluation/seeds/`.
- Activation updates a single active seed selector.
- `load_active_fee_rule_library()` still uses importlib resources.

Implementation options:

1. Minimal V1: keep `_ACTIVE_SEED_NAME` in `fee_rule_seed_loader.py` and change it to the reviewed seed.
2. Slightly safer V1: add `active_fee_rule_seed.json` manifest containing `{ "active_seed_name": "..." }`.

Recommended V1: manifest file.

Rationale:

- Avoids editing code when activating a future reviewed JSON seed.
- Still bundled, deterministic, and testable.
- Keeps runtime free from Excel/COM and absolute paths.

Manifest shape:

```json
{
  "active_seed_name": "fee_rules_v2026_06_03.json"
}
```

Loader behavior:

- Read manifest through importlib resources.
- Validate `active_seed_name` is a file name only, not a path.
- Load the referenced bundled seed.
- Reject missing or non-JSON seed names with actionable loader errors.

Activation must also validate version identity before the manifest points at a candidate.

Add an explicit helper:

```python
def validate_candidate_activation(
    active: FeeRuleLibrary,
    candidate: FeeRuleLibrary,
    diff: FeeRuleLibraryDiff,
) -> None:
    ...
```

Required behavior:

- If candidate content differs from active content and `candidate.version.version_id == active.version.version_id`, raise an actionable activation validation error.
- If version metadata differs from active metadata and `candidate.version.version_id == active.version.version_id`, raise an actionable activation validation error.
- If content and metadata are unchanged, reusing the same version id is allowed but activation is a no-op.
- If candidate has a new version id, activation validation may pass after seed validation and diff review.

This is a hard TASK_302 contract because TASK_301 stale detection depends on `fee_rule_version_id` changing when pricing rules change.

### Stale Relationship

TASK_301 already binds saved pricing drafts to `fee_rule_version_id`.

When TASK_302 changes the active version:

- Future fee draft pages use the new version.
- Existing saved fee pricing drafts become stale because `fee_rule_version_id` no longer matches.
- TASK_300 export traces the active version through existing metadata.

Do not add broad output-record stale redesign in TASK_302. If the current output model cannot compare fee rule version ids, document it as a limitation rather than expanding output-ledger architecture.

## File-Level Design

### Backend Fee Evaluation Module

Create:

- `backend/modules/fee_evaluation/fee_rule_candidate_builder.py`

Responsibilities:

- Define `FeeReferenceCandidateRow`.
- Convert rows + metadata into `FeeRuleLibrary`.
- Reuse `validate_fee_rule_library(...)`.
- Serialize candidate library to canonical JSON for bundled seed review.

Create:

- `backend/modules/fee_evaluation/fee_rule_library_diff.py`

Responsibilities:

- Compare active and candidate `FeeRuleLibrary` values.
- Produce `FeeRuleLibraryDiff`.
- Provide stable ordering by `rule_id`.

Create:

- `backend/modules/fee_evaluation/fee_rule_activation_validator.py`

Responsibilities:

- Define an activation validation error type.
- Implement `validate_candidate_activation(active, candidate, diff)`.
- Compare version metadata fields as part of activation safety.
- Reject changed content/metadata with reused `version_id`.

Modify:

- `backend/modules/fee_evaluation/fee_rule_seed_loader.py`

Responsibilities:

- Load active seed name from a bundled manifest.
- Keep `load_fee_rule_library(path)` unchanged for direct validation tests.
- Add validation for manifest seed name.

Create:

- `backend/modules/fee_evaluation/seeds/active_fee_rule_seed.json`

Initial content:

```json
{
  "active_seed_name": "fee_rules_v2026_06_03.json"
}
```

Optional create:

- `backend/modules/fee_evaluation/fee_rule_maintenance_report.py`

Only if report formatting would otherwise bloat `fee_rule_library_diff.py`.

### Tests

Create:

- `tests/unit/test_fee_rule_candidate_builder.py`
- `tests/unit/test_fee_rule_library_diff.py`
- `tests/unit/test_fee_rule_activation_validator.py`

Modify:

- `tests/unit/test_fee_rule_seed_loader.py`
- `tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py`

Test responsibilities:

- Candidate builder creates valid library from structured rows.
- Candidate builder preserves review-required ambiguous rows.
- Candidate builder rejects invalid unit label through existing validation.
- Diff detects added/removed/changed/unchanged rules.
- Diff reports alias and price changes.
- Activation validator rejects changed content with reused version id.
- Activation validator rejects metadata-only changes with reused version id.
- Activation validator allows unchanged candidate with same version id as no-op.
- Activation validator allows changed candidate with a new version id.
- Active manifest loader loads current seed.
- Manifest rejects path traversal or missing seed names.
- TASK_301 stale behavior remains correct when stored draft version differs from active version.

### Documentation

Modify:

- `tasks/TASK_302_FEE_REFERENCE_UPDATE_WORKFLOW.md`
- `docs/task_302_fee_reference_update_workflow_plan.md`
- `docs/task_298_302_fee_pricing_automation_series_plan.md`
- `docs/task_board.md`

Only update task status after implementation.

## Task Breakdown

### Task 1 - Add Active Seed Manifest

Files:

- Create: `backend/modules/fee_evaluation/seeds/active_fee_rule_seed.json`
- Modify: `backend/modules/fee_evaluation/fee_rule_seed_loader.py`
- Modify: `tests/unit/test_fee_rule_seed_loader.py`

Steps:

1. Add manifest with current active seed name.
2. Add private manifest loader in `fee_rule_seed_loader.py`.
3. Validate active seed name is only a file name:
   - no `/`
   - no `\`
   - ends with `.json`
   - not the manifest file itself
4. Update `load_active_fee_rule_library()` to load the seed named by manifest.
5. Add tests for happy path and invalid manifest names.

Expected command:

```powershell
py -m pytest tests/unit/test_fee_rule_seed_loader.py -q
```

### Task 2 - Candidate Builder

Files:

- Create: `backend/modules/fee_evaluation/fee_rule_candidate_builder.py`
- Create: `tests/unit/test_fee_rule_candidate_builder.py`

Steps:

1. Define `FeeReferenceCandidateRow`.
2. Define `build_fee_rule_library_candidate(version, rows)`.
3. Convert candidate rows into existing `FeeRule` / `FeeAmount` / `FeeRuleLibrary`.
4. Call `validate_fee_rule_library(...)` before returning.
5. Define `fee_rule_library_to_seed_json(library)` with stable indentation and sorted deterministic object fields.
6. Add tests for valid candidate, review-required preservation, invalid unit label rejection, and duplicate alias rejection.

Expected command:

```powershell
py -m pytest tests/unit/test_fee_rule_candidate_builder.py tests/unit/test_fee_rule_seed_loader.py -q
```

### Task 3 - Candidate Diff

Files:

- Create: `backend/modules/fee_evaluation/fee_rule_library_diff.py`
- Create: `tests/unit/test_fee_rule_library_diff.py`

Steps:

1. Define diff dataclasses.
2. Implement `diff_fee_rule_libraries(active, candidate)`.
3. Compare rules by `rule_id`.
4. Sort entries by `rule_id`.
5. Report field-level changes for aliases, amounts, labels, strategy, and review metadata.
6. Add tests for added/removed/changed/unchanged and alias/price changes.

Expected command:

```powershell
py -m pytest tests/unit/test_fee_rule_library_diff.py -q
```

### Task 4 - Activation Validation

Files:

- Create: `backend/modules/fee_evaluation/fee_rule_activation_validator.py`
- Create: `tests/unit/test_fee_rule_activation_validator.py`

Steps:

1. Define `FeeRuleActivationValidationError`.
2. Implement `validate_candidate_activation(active, candidate, diff)`.
3. Treat any `added`, `removed`, or `changed` diff entry as content change.
4. Treat version metadata changes as activation-relevant changes:
   - `source_file_name`
   - `source_sheet`
   - `source_hash`
   - `effective_from_basis`
   - `created_at`
5. Reject content or metadata changes when the candidate reuses the active `version_id`.
6. Allow unchanged same-version activation as no-op.
7. Allow changed candidate with a new `version_id`.

Expected command:

```powershell
py -m pytest tests/unit/test_fee_rule_activation_validator.py -q
```

### Task 5 - Stale Regression

Files:

- Modify: `tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py`

Steps:

1. Keep existing stale fee-rule-version test.
2. Add or tighten assertion that active version changes make saved snapshot stale.
3. Do not change persistence schema.

Expected command:

```powershell
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py -q
```

### Task 6 - Documentation And Board Closure

Files:

- Modify: `tasks/TASK_302_FEE_REFERENCE_UPDATE_WORKFLOW.md`
- Modify: `docs/task_302_fee_reference_update_workflow_plan.md`
- Modify: `docs/task_298_302_fee_pricing_automation_series_plan.md`
- Modify: `docs/task_board.md`

Steps:

1. Mark TASK_302 complete only after implementation and validation pass.
2. Update series plan to state TASK_298-TASK_302 complete.
3. Update task board with validation results.
4. Do not add any next task as active unless the user explicitly approves it.

## Risks And Mitigations

Risk: Maintenance workflow accidentally becomes production Excel dependency.

Mitigation:

- Keep active runtime loader manifest-based and importlib-resource based.
- Keep workbook parsing out of normal API/page/export code.
- Tests should prove `load_active_fee_rule_library()` reads bundled JSON.

Risk: Candidate generation guesses ambiguous lab pricing.

Mitigation:

- Candidate rows must carry `review_required` and `review_reason`.
- Ambiguous or text-only prices keep `amount=None` with source text.
- Validation blocks review-required rows without reason.

Risk: Activation silently reuses an old version id.

Mitigation:

- `validate_candidate_activation(active, candidate, diff)` must reject reused version id when content or metadata changes.
- Unit tests must cover content changes, metadata-only changes, unchanged no-op activation, and changed new-version activation.

Risk: Output stale semantics are over-expanded.

Mitigation:

- Rely on existing fee-rule-version traceability and TASK_301 stale behavior.
- Document output-record stale limitations instead of changing output ledger architecture in this task.

## Validation Plan

Run:

```powershell
py -m pytest tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_matcher.py tests/unit/test_fee_rule_candidate_builder.py tests/unit/test_fee_rule_library_diff.py tests/unit/test_fee_rule_activation_validator.py -q
```

Run:

```powershell
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/unit/test_confirmed_matrix_fee_draft_service.py tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py -q
```

Run:

```powershell
git diff --check
```

No frontend build is required unless implementation changes frontend files. TASK_302 V1 should not change frontend files.

## Self-Check Before Implementation

- Does `load_active_fee_rule_library()` still avoid Excel/COM and absolute paths?
- Does candidate validation reuse existing seed validation?
- Does diff report alias/price/review changes clearly?
- Does activation validation reject changed candidates that reuse the active version id?
- Does active version change make TASK_301 saved drafts stale?
- Did the task avoid UI, database-backed rule stores, production upload APIs, and automatic pricing judgment?
