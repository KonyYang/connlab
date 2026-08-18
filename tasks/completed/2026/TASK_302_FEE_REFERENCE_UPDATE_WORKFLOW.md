# TASK_302 Fee Reference Update Workflow

Status: Complete.

Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Allowed reason: TASK_298, TASK_299, TASK_300, and TASK_301 are complete. The approved TASK_298-TASK_302 series defines TASK_302 as the next controlled step for maintaining future `Unit Price Reference` updates. Implementation was performed only after explicit user approval.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task if the scope remains a bounded backend maintenance workflow with deterministic parsing, candidate generation, diff reporting, seed validation, and regression tests. It is suitable for comparing structured fee-rule snapshots and preserving version/stale boundaries. It is not suitable in this task for inventing new pricing policy, automatically interpreting ambiguous lab judgment prices, replacing human review of the Unit Price Reference, or building a full rule-maintenance UI without a separate approved UI task.

## Goal

Create a controlled maintenance workflow for future `Unit Price Reference` updates so ConnLab can review, validate, diff, and activate a new bundled fee-rule version without making production runtime depend on Excel or absolute template paths.

TASK_302 closes the TASK_298-TASK_302 pricing automation series by defining how a new reviewed pricing reference becomes a new active fee rule version.

## Input Data

Inputs:

- Current active bundled fee rule seed loaded through `load_active_fee_rule_library()`.
- A future reviewed `Unit Price Reference` update represented as a controlled structured candidate row list.
- Operator-provided or maintenance-provided version metadata:
  - candidate `version_id`
  - source file name
  - source sheet
  - source hash
  - `effective_from_basis`
  - created timestamp
- Existing rule aliases/keyword semantics from TASK_298.

Current business baseline:

- `D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls`
- sheet `Unit Price Reference`

The baseline path may be documented and used by controlled maintenance/manual verification, but production runtime must not hardcode this absolute path.

TASK_302 V1 does not parse the workbook directly. Workbook/sheet extraction into the structured candidate row representation is a later task unless explicitly approved. This task may use workbook-derived fixtures or manually reviewed structured rows for tests and maintenance validation.

## Output Data

Outputs:

- A candidate fee-rule JSON seed that follows the existing `FeeRuleLibrary` schema.
- A human-reviewable diff report comparing candidate vs active rule version.
- Validation results that block malformed or ambiguous candidate seeds.
- A controlled activation mechanism for switching the active bundled seed to the reviewed candidate version.
- Traceability metadata:
  - source file name
  - source sheet
  - source hash
  - candidate version id
  - effective-from basis

## Scope

In scope:

- Add a backend maintenance module for candidate fee-rule seed generation/diffing.
- Add an activation validator that blocks candidate activation when content or metadata changed but `candidate.version_id == active.version_id`.
- Add strict validation for candidate metadata, duplicate aliases, duplicate rule ids, allowed unit labels, and allowed calculation strategies.
- Add deterministic candidate-vs-active diff output:
  - added rules
  - removed rules
  - changed aliases
  - changed unit price
  - changed base fee
  - changed unit label
  - changed calculation strategy
  - changed review-required status/reason
- Preserve ambiguous or lab-judgment pricing as `review_required=true`.
- Add a controlled activation path that only switches to an already-reviewed bundled JSON seed.
- Keep downstream stale behavior tied to fee rule version id:
  - TASK_286 fee draft uses active version
  - TASK_301 saved pricing drafts become stale when active fee rule version changes
  - TASK_300 exports trace the active rule version in generated output metadata
- Add unit/integration tests for candidate generation, validation, diffing, and activation metadata.
- Update task board and series plan when complete.

Out of scope:

- No frontend rule-maintenance UI.
- No automatic activation of a candidate seed.
- No production API endpoint for arbitrary workbook upload.
- No production runtime dependency on Excel COM, `.xls`, `.xlsx`, or an absolute template path.
- No automatic pricing judgment for ambiguous ranges, discounts, special lab pricing, or manually reviewed rules.
- No database migration for a server-side rule-version store.
- No StepInstance, execution persistence, report generation, AI review, permissions, or multi-user workflow.
- No change to Fee Evaluation local edit/export/persistence behavior beyond naturally consuming the active fee rule version.

## Runtime And Maintenance Boundary

- Production runtime continues to use bundled JSON through `load_active_fee_rule_library()`.
- The active seed remains importlib-resource based.
- Controlled maintenance tooling in V1 reads a structured candidate representation or fixture to produce a candidate JSON seed and diff report.
- Direct workbook extraction is out of scope for V1 and must be handled by a later approved maintenance-adapter task.
- If `.xls` parsing requires Excel COM, that COM dependency must stay inside a maintenance/manual path and must not be called by normal API requests, fee draft generation, Fee Form export, or page load.
- Activation means changing the active bundled seed name or manifest after candidate review; it does not mean reading the workbook live.

## Version And Stale Policy

- Every activated candidate must have a new `version_id`.
- `version_id` must not equal the previous active version id when rule content or metadata changes.
- TASK_302 must implement a concrete activation guard, for example `validate_candidate_activation(active, candidate, diff)`, that raises an actionable validation error when any rule diff or version metadata diff exists and the candidate reuses the active `version_id`.
- Active rule version changes make saved TASK_301 pricing drafts stale because they are bound to `fee_rule_version_id`.
- Fee draft/export traceability must keep showing the active fee rule version.
- V1 does not retrofit historical output records. If output-record stale comparison for fee rule versions is not already supported by the current output model, TASK_302 should document that limitation and stop rather than inventing a broad output-ledger redesign.

## Candidate Diff Policy

Diffs are keyed by `rule_id`.

Candidate diff report must classify:

- `added`
- `removed`
- `changed`
- `unchanged`

Changed fields must include field-level before/after values for:

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

Alias-only changes are reviewable changes and must not be silently ignored.

## Acceptance Criteria

- Candidate seed generation can create a valid `FeeRuleLibrary` JSON file from a controlled source representation or fixture.
- Candidate seed validation rejects:
  - duplicate rule ids
  - duplicate normalized aliases
  - invalid unit labels
  - invalid calculation strategies
  - missing review reason when `review_required=true`
  - invalid source hash format
- Candidate activation validation rejects changed candidate content or metadata that reuses the active `version_id`.
- Candidate diff report clearly identifies added/removed/changed/unchanged rules.
- Active seed activation is explicit and only targets a bundled JSON candidate.
- `load_active_fee_rule_library()` continues to work without Excel/COM and without absolute path dependency.
- TASK_301 stale behavior remains correct when active fee rule version changes.
- Existing TASK_298/TASK_299/TASK_300/TASK_301 tests remain passing.

## Validation

Expected validation for implementation:

- `py -m pytest tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_matcher.py -q`
- New unit tests for candidate generation/diffing/activation helpers.
- TASK_301 stale regression tests when fee rule version changes.
- Fee draft/export regression tests consuming active rule library.
- `git diff --check`

## Stop Point

After TASK_302 implementation, stop. Do not start UI rule maintenance, database-backed rule stores, server deployment, or TASK_303/TASK_304 work from this task.
