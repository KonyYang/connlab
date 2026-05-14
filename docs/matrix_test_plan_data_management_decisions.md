# Matrix Test Plan Data Management Decisions

> Created: 2026-05-14
> Scope: Product/workflow decisions for Matrix, test record, output freshness, and future reuse.

## 1. Purpose

This document records confirmed business and data-management decisions for ConnLab's Matrix-first Project Workbench direction.

It is not an implementation task by itself. Future tasks must use this document as a constraint source when planning Matrix editing, test record generation/import, image management, fee evaluation, report generation, and historical reuse.

## 2. Core Product Direction

ConnLab should adapt to the current lab workflow first:

```text
Spec or existing Matrix
  -> ConnLab Matrix/TestPlan draft
  -> engineer review/edit
  -> freeze/confirm Matrix version
  -> generate Word test record forms
  -> manual testing and manual record filling
  -> import filled records back into ConnLab
  -> attach images/evidence
  -> generate fee/report/approval package from structured data
```

Do not jump directly to a full online test execution system.

## 3. Authority Model

Use this authority hierarchy:

```text
Original spec / Word Matrix / Excel Matrix = source evidence
ConnLab confirmed ProjectTestPlanDraft = project plan authority
Generated Word / Excel / PDF files = output artifacts
Imported test results/images = project execution evidence
```

The latest confirmed ConnLab Matrix draft is the source of truth for downstream generation and stale checks.

## 4. Matrix Role

Matrix is the first Workbench work surface because it shows the test plan at a glance.

Matrix responsibilities:

- show test items and group/step coverage;
- show source traceability from spec or imported Matrix;
- provide access to group/step details;
- drive Section 2, test record form, fee evaluation, approval package, and future report generation;
- support future historical project reuse.

Matrix must not become a giant Excel replacement. Complex actions belong in group/step detail panels.

## 5. Matrix Data Shape

Future Matrix data should be stored as structured group/step data, not only as table cell text.

Suggested conceptual shape:

```text
ProjectTestPlanDraft
  draft_id
  project_id
  version
  status: draft / confirmed / superseded

ProjectTestGroup
  group_id
  draft_id
  group_number
  sample_size

ProjectTestStep
  step_id
  group_id
  sequence
  raw_token
  suffix_note
  test_item
  section
  method
  condition
  requirement
  step_description
  duration_value
  duration_unit
  source_trace
  note
```

## 6. Step Token And Continuity Rules

Matrix cells may contain values such as:

```text
1,8
1,14
3(a)
4(b)
2(c)
```

Parsing rules:

- comma, whitespace, and newline are separators;
- each token produces one step;
- leading digits become `step_sequence`;
- trailing non-digits are preserved as `suffix_note`;
- sorting and continuity use `step_sequence` only.

Examples:

```text
3(a) -> step_sequence 3, suffix_note "(a)"
4(b) -> step_sequence 4, suffix_note "(b)"
```

Validation rules:

- each group must start at step 1;
- each group must have unique step numbers;
- each group must be continuous with no gaps;
- duplicate or missing step numbers block Matrix freeze/confirmation.

Examples:

```text
Allowed: 1,2,3,4,5
Blocked: 2,3,4
Blocked: 1,2,3,4,6
Blocked: 1,2,2,3
```

## 7. Repeated Test Items

The same test item can appear multiple times inside one group and each occurrence is a separate step.

Example:

```text
Step 2  LLCR  Initial LLCR
Step 5  LLCR  After Thermal Shock
Step 11 LLCR  Final LLCR
```

Stable matching for record generation/import must use group + step sequence, not only test item name.

## 8. Test Record Workflow

Current real workflow:

- one Word record form/table per group;
- form is generated from Matrix;
- engineer manually fills results/comments;
- table structure normally remains stable;
- ConnLab should import filled Word records back into structured group/step results.

Record columns to support first:

```text
Step
Test
Requirement
Step Description
Result
Comment
```

Result/comment handling must keep both normalized status and original human text.

Initial normalized statuses:

```text
pass
fail
ref
na
waive
pending
text_only
```

## 9. Images And Evidence

Images should eventually attach to project steps.

Initial image categories:

```text
before_sample
before_equipment
after_sample
failure_location
other
```

Suggested naming pattern:

```text
{DL_NUMBER}_G{GROUP_NUMBER}_S{STEP_SEQUENCE}_{TEST_ITEM}_{IMAGE_CATEGORY}_{INDEX}
```

Names should be previewed and editable before copying/renaming.

## 10. Duration And Fee Decisions

Duration:

- maintained at group/step level;
- test item may provide default duration;
- final scheduling uses step-level duration.

Fee:

- depends on test item, step count, sample size, and a standard price table;
- current fee workbook mapping requires a dedicated task;
- do not hide fee uncertainty when mapping is missing.

## 11. Output Version Ledger

Projects normally have one current Matrix, but that Matrix can be revised.

Downstream outputs should be traced to the Matrix draft/version that produced them:

```text
section2_write_back
test_record_form
fee_evaluation
approval_package
record_import
test_image_set
report_draft
final_report
```

Status vocabulary:

```text
missing
current
stale
manual
failed
```

When a newer Matrix version becomes current, outputs from older versions must become stale rather than being deleted.

## 12. Historical Reuse Direction

Future similar-project startup should use structured historical data:

- copy a prior Matrix as a new draft;
- reuse prior duration as defaults;
- compare test item/group patterns;
- reference prior results and report wording;
- reference prior image/evidence categories;
- reuse fee mapping assumptions with explicit review.

Do not start with AI. First build deterministic search by:

```text
product name
part number
test item
section
standard/method
requirement
group pattern
sample size
result status
```

## 13. Recommended Task Sequence

1. `TASK_188_PROJECT_OUTPUT_VERSION_LEDGER_CORRECTION`: persistent output version ledger.
2. `TASK_189_MATRIX_EDIT_AND_FREEZE_FOUNDATION`.
3. `TASK_190_PROJECT_WORKBENCH_MATRIX_AUTHORITY_WORKSPACE`: reshape Workbench so Matrix authority is the primary work surface and downstream outputs become compact status/entry points.
4. `TASK_191_MATRIX_DRAFT_STARTER_IMPORT_AND_MANUAL_EMPTY_STATE`: add the Workbench entry path to import a `.docx` Matrix preview into a draft or create a manual blank Matrix draft.
5. `TASK_192_MATRIX_SOURCE_CANDIDATES_AND_BROWSE_FALLBACK_CORRECTION`: prefer Project-owned email attachment/file asset candidates before external browse/path/manual Matrix fallback.
6. `TASK_193_MATRIX_GROUP_STEP_DETAIL_PANEL`: deepen group/step editing and validation detail after the Matrix starter source-selection path and Matrix-first workspace are stable.
7. `TASK_194_GROUP_RECORD_FORM_GENERATION`.
8. `TASK_195_FILLED_RECORD_FORM_IMPORT`.
9. `TASK_196_STEP_IMAGE_AND_EVIDENCE_MANAGEMENT`.
10. `TASK_197_HISTORICAL_MATRIX_AND_PROJECT_REUSE`.

Each task must still go through the ConnLab task-board approval protocol before implementation.

## 14. Implementation Guardrails

Future implementation must follow these guardrails:

- Do not continue adding Workbench-only frontend state when the business requirement is traceability after reload.
- Do not let Matrix editing proceed without a durable way to mark downstream outputs stale.
- Do not treat generated Word/Excel/PDF files as the source of truth.
- Do not collapse repeated test items into one row when they appear as different group steps.
- Do not match imported record results by test item name alone; match by project, Matrix version, group, and step sequence.
- Do not make Matrix a giant spreadsheet UI. Use Matrix overview plus group/step detail panels.
- Do not implement report generation before Matrix, record results, and images have structured persistence.
- Do not start AI-based reuse before deterministic historical search over structured data exists.

## 15. Current Correction Decision

The existing TASK_188 frontend freshness display is useful but incomplete for the confirmed business need.

The next controlled implementation should be `TASK_188_PROJECT_OUTPUT_VERSION_LEDGER_CORRECTION`, which adds minimal persistent output lineage before moving to Matrix editing/freeze work.
