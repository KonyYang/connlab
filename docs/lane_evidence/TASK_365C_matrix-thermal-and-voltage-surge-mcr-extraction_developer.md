# TASK_365C Developer Evidence

## Status

Developer implementation complete locally on 2026-07-19. Reviewer/QA and package
isolation passed; user acceptance remains pending.

## Implemented Contract

- Thermal Shock extracts Method A, two signed temperature/dwell pairs, repeat cycles,
  and derives total dwell hours only from one unambiguous complete schedule.
- The confirmed schedule canonicalizes to
  `Method A, -40 ℃ (30 min), +105 ℃ (30 min); repeat 25 cycles; total 25 hours`.
- Thermal Shock and Temperature life use the existing fill-empty template path for
  `No damage`; explicit non-residual Requirement text is preserved.
- Thermal Shock/Temperature life Test Item identity outranks incidental Contact
  Resistance prose without changing other MCR family precedence.
- Voltage surge binds Power Pin Differential/Common Mode values, waveform, and the
  Signal Pin state; `μs`, `µs`, and `us` canonicalize to `μs`.
- Existing Thermal Shock Fee authority remains unchanged and consumes `25 hours` as
  Unit Price 30/hour, Units 25, Base Fee 0, and Testing Fee 750.

## TDD Evidence

- Initial red run failed at collection because the two approved helper modules did
  not exist.
- First green attempt exposed generic MCR conversion of `μs` to `us`; a Voltage
  surge-only canonicalization fixed the public-path failure.
- A second red test proved explicit Temperature life Requirement was overwritten;
  the report-style fallback was narrowed to preserve explicit non-residual text.
- Focused TASK_365C suite: `112 passed`.
- Combined TASK_365A/B/C parser, PDF parity, Fee, and preview regression:
  `276 passed in 5.99s`.

## Real-Sample Read-Only Smoke

Both the user-provided GS-12-2268 PDF and DOCX returned `supported` with 28 rows:

- 8.3 Voltage surge -> exact canonical Power/Signal Pin Condition.
- 8.5 Temperature life -> Requirement `No damage`.
- 8.6 Thermal Shock -> Method `EIA-364-32`, exact canonical Condition ending
  `total 25 hours`, Requirement `No damage`.

The files were read only. No import, confirmation, database write, or generated
output operation was executed.

## Isolation

TASK_365C owns two new pure helper modules, narrow shared-extractor/template/MCR
hunks, focused tests, and governance files. Existing TASK_365A MFG and TASK_365B PDF
changes were retained but not modified as part of this lane. No Fee production or
seed path was changed.
