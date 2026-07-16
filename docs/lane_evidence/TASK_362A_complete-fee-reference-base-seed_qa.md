# TASK_362A QA Evidence

Date: 2026-07-16

Role: QA

Task: `TASK_362A_COMPLETE_FEE_REFERENCE_BASE_SEED`

Status: `qa_pass`

## Automated Verification

- Backend Fee suite: `337 passed, 1 skipped`.
- Frontend Fee Evaluation suite: `3 files, 57 passed`.
- Focused Python compilation: passed.
- Frontend TypeScript/Vite production build: passed; only the established chunk-size
  warning remains.

## Browser Smoke

Project `ce15026d119f408f80970ea7077f6e41` was refreshed at the local Fee Evaluation
page.

- IR Condition `2 minutes`: Unit Price `10`, Unit Type `per reading`, Units `1`,
  Base Fee `0`, Testing Fee `10`, and no Base Fee reminder.
- DWV Condition `60 seconds`: Unit Price `5`, Unit Type `per reading`, Units `1`,
  Base Fee `0`, Testing Fee `5`, and no duration-price review.
- Thermal Shock without an extracted duration: Unit Price `30`, Unit Type `per hour`,
  Units Pending, Testing Fee Pending, and the duration review remains visible.
- Current Rating with Matrix Condition `A`: Unit Type is `per sample` through the
  Temperature rise rule and the reminder is `Confirm current`; no current tier is
  guessed without a numeric ampere value.
- Specification extraction/MCR/Matrix preview suite: `123 passed`; Test Voltage
  examples normalize to `500VDC` and `1500VAC`.
- No Update Fee, export, workbook write, or authority mutation was performed.
