# TASK_362A Developer Evidence

Date: 2026-07-16

Role: Developer

Task: `TASK_362A_COMPLETE_FEE_REFERENCE_BASE_SEED`

Status: `developer_complete`

## Implementation

- Captured all 44 effective `Unit Price Reference` rows plus row 49 policy metadata
  with the approved workbook identity and SHA256.
- Added a reviewed extension layer, deterministic compiler, source provenance, and
  activated `fee_rules_v2026_07_16_r3` without modifying the legacy seed.
- Preserved existing Visual, LLCR, Dust, force, CR, duration, temperature-rise,
  sample-preparation, reseating, and report defaults.
- Added shared IR/DWV Condition pricing: explicit 1 minute or 60 seconds selects
  `5/reading`; explicit 2 minutes or 120 seconds selects `10/reading`. Missing,
  unsupported, or conflicting duration text leaves Unit Price and Testing Fee Pending.
- IR/DWV calculated rows default Base Fee to `0`, Units to `1`, and Testing Fee to
  the selected per-reading price without a Base Fee reminder. `1mA` is treated as a
  non-duration condition and therefore leaves Unit Price Pending.
- Frontend manual-required Unit Price and Units remain blank with a `Pending`
  placeholder. Thermal Shock without duration no longer receives a synthetic Units `1`.
- Added IR/DWV specification-section extraction for `Test Voltage`, preserving source
  polarity as `500 volts DC -> 500VDC` and `1500 volts AC -> 1500VAC`.
- Added the reviewed `Current Rating` alias to the source Temperature rise rule, so
  Current Rating uses the existing current-tier evaluator rather than remaining
  unmatched.

## TDD Evidence

- New duration-tier tests first failed for all 40 deterministic IR/DWV cases.
- The Base Fee correction first failed in all 40 deterministic duration cases plus
  the Confirmed Matrix draft integration case, then passed after the result became
  fully calculated.
- Confirmed Matrix draft integration plus default-fill passed `90` tests.
- The generic frontend manual-Base-Fee fallback remains covered with a neutral
  non-IR fixture.
- The complete related backend suite passed `337` tests with `1` skipped after the
  final rule-version and legacy-fixture corrections.
- Specification extraction, MCR normalization, Matrix parsing, and preview API passed
  `123` tests after the Test Voltage correction.

## Boundaries

No external workbook, database schema, real project folder, public-drive authority,
Matrix authority, report generation, or TASK_362B behavior was changed.
