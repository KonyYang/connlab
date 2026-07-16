# TASK_362A Reviewer Evidence

Date: 2026-07-16

Role: Reviewer

Task: `TASK_362A_COMPLETE_FEE_REFERENCE_BASE_SEED`

Status: `reviewer_pass`

## Review Result

This was a same-session sequential review, not an independent reviewer thread.

- Source and extension loaders fail closed on wrong source identity, missing rows,
  duplicate mappings, invalid aliases, unsupported strategies, and invalid units.
- The compiler is deterministic and writes atomically; runtime uses committed JSON
  and does not read the external workbook.
- Every source row is traceable through `source_kind` and `source_row`; the old seed
  remains available and was not included in TASK_362A commits.
- IR/DWV fee parsing reads only Matrix Condition. Explicit 60/120-second tiers are
  honored; absent, unsupported, or mixed durations cannot silently select a price.
  `1mA` remains a current limit rather than being misread as one minute.
- A decisive 60/120-second IR/DWV tier is a complete calculated result: Base Fee is
  `0`, Units is `1`, and Testing Fee equals the selected per-reading price. The UI
  does not present a Base Fee reminder for that result.
- Manual-required Unit Price and Units stay Pending in the UI; saved drafts from an
  older rule version cannot silently restore numeric placeholders.
- `Current Rating` is a reviewed alias of the source-row-33 Temperature rise rule;
  current-tier pricing remains conditional on a numeric Matrix current and does not
  infer a tier from a bare `A` unit.
- IR/DWV Test Voltage extraction is confined to those two Matrix families and
  preserves AC/DC from the specification source.

Blocking findings: none.
