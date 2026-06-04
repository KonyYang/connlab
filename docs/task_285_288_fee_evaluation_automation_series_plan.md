# TASK_285-288 Fee Evaluation Automation Series Plan

> Status: proposed for review
> Created: 2026-06-03
> Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

## Current Progress

`TASK_285_FEE_RULE_SEED_LIBRARY` and `TASK_286_CONFIRMED_MATRIX_TO_FEE_DRAFT` are complete. `docs/task_board.md` currently marks `TASK_287_FEE_EVALUATION_REVIEW_UI` as the next planned task awaiting explicit approval.

## Business Goal

Convert the manually prepared `Testing Prices` fee sheet into a Matrix-derived, reviewable, traceable ConnLab workflow:

```text
Confirmed Matrix Authority
  + Project / LTR metadata
  + versioned Fee Rule Library
  -> Fee Evaluation Draft
  -> Operator Review
  -> Excel Fee Evaluation output
  -> ProjectOutputRecord lineage/freshness
```

The selected product direction is semi-automatic review:

- ConnLab fills deterministic fee candidates.
- ConnLab flags ambiguous or special-case fee items.
- Operators review discounts, special charges, report fees, and unmatched rows.
- Excel is the output format, not the primary data model.

## Task Sequence

### TASK_285 - Fee Rule Seed Library

Create a versioned fee rule seed from `Unit Price Reference`.

Deliverable:

- structured rules with version/source metadata;
- deterministic matcher;
- tests for loading, validation, and matching.

No Matrix-to-fee generation and no UI.

### TASK_286 - Confirmed Matrix To Fee Draft

Generate a backend fee draft from active Confirmed Matrix authority and the active fee rule version.

Deliverable:

- typed `FeeEvaluationDraft`;
- traceable line items;
- review-required warnings;
- API preview.

No frontend review UI and no Excel export.

### TASK_287 - Fee Evaluation Review UI

Add a Workbench derived-output review surface for the generated fee draft.

Deliverable:

- fee status entry;
- review table;
- review-required reasons;
- frontend tests.

No Excel export and no rule-maintenance UI.

### TASK_288 - Fee Evaluation Excel Export

Export reviewed fee draft data into the official fee workbook template and update output lineage.

Deliverable:

- Excel gateway writes `Testing Prices`;
- controlled output path;
- no-overwrite guard;
- `ProjectOutputRecord` update.

No rule-maintenance UI and no execution persistence.

## Versioning Policy

The `Unit Price Reference` sheet may change. ConnLab should therefore treat each imported or curated reference as a pricing-rule version.

The current V1 authoritative reference source is:

```text
D:\Source\Template\Testing Fee Evaluation-Even.xls
```

Use the workbook's `Unit Price Reference` sheet as the current business-approved pricing reference.

Every fee draft must record:

- `pricing_rule_version_id`
- `pricing_source_file_name`
- `pricing_source_hash`
- `generated_at`

The TASK_285 seed records `effective_from_basis: "project.sample_received_date"` instead of a concrete project date. For V1, TASK_286 resolves that basis from the active Confirmed Matrix authority version (`ConfirmedMatrixVersion.sample_received_date`) and records it as `pricing_effective_from`. TASK_286 must not add a Project model field or application-form lookup for this date.

TASK_286 must calculate fees only when the needed unit basis is deterministic from Confirmed Matrix authority. Numeric price alone is not enough. Photo count, reading count, cycle count, Day-to-hour conversion, marker-bearing sample expressions, and manual-required rules must produce review-required fee lines unless a later approved task defines deterministic derivation.

New pricing versions do not silently reprice historical drafts. Later tasks may add an explicit reprice action and version comparison surface.

## Fee Form Defaults

Generated fee forms use these V1 defaults:

- `Prepared by`: ConnLab login user first; if unavailable, fallback to the current Windows/computer user.
- `Approved by`: manually supplied for each export.

V1 may output `.xlsx` when `.xls` Excel automation is unavailable or unsuitable, provided the exported workbook preserves required fee rows, totals, and traceability.

## Main Risks

1. Fee rules include human judgment, especially discounts, report fees, setup fees, and chamber sharing.
2. Matrix row text may not match reference aliases exactly.
3. Sample quantity and step count semantics may vary by test family.
4. Legacy `test_record_fee_*` services exist but are not authority-driven fee engines.
5. Excel COM output must remain behind the infrastructure gateway.

## Validation Strategy

Each task gets focused tests:

- rule seed validation and matcher tests;
- fee draft service unit/integration tests;
- frontend review tests;
- Excel gateway/export tests.

Regression tests should include Confirmed Matrix authority and Workbench output status paths where touched.

## User Inputs Needed Before Implementation

1. Whether `Approved by` should be a free-text field only, or selected from a controlled approver list in a later task.

TASK_285 has no remaining blocking user-input questions after the confirmed source file and `effective_from_basis` decisions. The remaining `Approved by` choice belongs to later TASK_287/TASK_288 planning and must not block the seed-library plan review.

## Stop Rule

After writing this series plan and task files, stop. Do not implement TASK_285 until the user explicitly approves the task and its executable implementation plan.
