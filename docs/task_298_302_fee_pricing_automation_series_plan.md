# TASK_298-TASK_302 Fee Pricing Automation Series Plan

## Status

Controlled series in progress.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current board context: TASK_298 and TASK_299 are complete. TASK_300 requires a separate task file, executable plan, and explicit approval before implementation.

## Goal

Move Fee Evaluation from a Matrix-derived preview and manually completed Excel form toward controlled pricing automation:

```text
Rule/reference defaults -> local editable pricing preview -> export edited values -> persist edits -> maintain reference updates
```

The series keeps Excel as the delivery form while gradually making ConnLab the structured working surface for fee review and preparation.

## Series Tasks

### TASK_298_FEE_PRICE_REFERENCE_RULE_REFRESH

Completed. Refreshed the fee rule/reference validation and matching foundation so later Fee Evaluation tasks can default editable fields from the reviewed `Unit Price Reference` source.

Implementation note:

- The active bundled seed data/version was not replaced in TASK_298.
- TASK_289 documented that `Testing Fee Evaluation-Even.optimized-v1.xls` preserved `Unit Price Reference` unchanged.
- Therefore active rule metadata intentionally remains the TASK_285 reviewed source snapshot until a controlled reference-update task creates a new version.

In scope:

- bundled fee rule seed refresh evaluation
- canonical unit-label validation
- alias and keyword matching hardening
- numeric default `Unit Price` / `Base Fee` preservation
- ambiguity held for operator review

Out of scope:

- frontend editable cells
- export edited values
- persistence
- rule-maintenance UI
- database migration
- new production API endpoint

### TASK_299_FEE_EDITABLE_PRICING_PREVIEW_UI

Completed.

Make the Fee Evaluation preview table locally editable.

Planned fields:

- `Spend Time`
- `Unit Price`
- `Unit Type`
- `Units`
- `Base Fee`
- `Discount`

`Testing Fee` should calculate locally as:

```text
Unit Price * Units * (1 - Discount) + Base Fee
```

V1 should treat `10` and `10%` as 10% discount.

### TASK_300_FEE_EDITED_VALUES_TO_FEE_FORM_EXPORT

Carry frontend-edited pricing values into Fee Form generation.

The generated workbook should reflect the same row order and editable field values shown in the Fee Evaluation preview.

### TASK_301_FEE_PRICING_DRAFT_PERSISTENCE

Persist and reload operator-edited fee values.

Persistence should be attached to the project and active Confirmed Matrix authority version so stale behavior can be reasoned about later.

### TASK_302_FEE_REFERENCE_UPDATE_WORKFLOW

Add a controlled workflow for future `Unit Price Reference` updates.

Expected concerns:

- source version/hash tracking
- diff/review before activating a new reference
- active rule version switch
- derived output stale status
- project-level traceability to the rule version used

## Cross-Series Boundaries

- Do not make production runtime depend on Excel COM or an absolute template path for loading active rules.
- Do not silently calculate prices when the source reference requires lab judgment.
- Do not replace Excel as the delivery artifact in this series.
- Do not implement StepInstance, execution persistence, report generation, AI review, permission systems, or multi-user workflows.

## Current Assumptions

- The current business reference baseline is `D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls`, sheet `Unit Price Reference`.
- Runtime rule loading remains bundled JSON through `load_active_fee_rule_library()`.
- Active seed metadata remains the TASK_285 source snapshot while `Unit Price Reference` is unchanged.
- Matching uses exact alias first, then deterministic keyword/contains matching.
- Ambiguous matches remain review-required.
- UI dropdown wording such as `per sample` maps to backend canonical labels such as `sample`.
