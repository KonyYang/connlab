# Future Extension Map

These are intentionally outside MVP but must be protected by architecture.

## MatrixPlan

A structured test plan generated from product specification, customer request, old reports, or manual selection.

## TestRecord

Execution form generated from MatrixPlan.

## TestResult

Structured result data imported from Excel or instruments.

## TestAsset

Images, charts, and raw files bound to Project/Group/TestItem.

## LabReport

ReportDataset built from Project, MatrixPlan, TestResult, and TestAsset. Word is an export format, not the master data.

## ReportAudit

Deterministic checks first:

- Requirement/result consistency.
- Pass/fail correctness.
- Table and figure numbering.
- Method/version consistency.

AI later:

- Semantic review.
- Old report module recommendation.
- Wording improvement.
- Consistency hints.

## KnowledgeBase

Standard library, product specification library, historical report library, method templates, and requirement rules.
