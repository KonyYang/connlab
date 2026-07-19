# TASK_365C Matrix Thermal And Voltage Surge MCR Extraction

## Status

Complete/accepted on 2026-07-19 after explicit user acceptance, Developer
implementation, focused Reviewer/QA, and Integrator hunk isolation. The accepted
package is committed locally without remote push. TASK_365A/TASK_365B remain
separately pending user acceptance; TASK_364B remains on its own gate.

## Phase / Lane

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Lane: `matrix-thermal-and-voltage-surge-mcr-extraction`.
- This lane must remain serial behind TASK_365A/TASK_365B parser hunk isolation.

## Goal

Add deterministic, source-faithful Matrix MCR extraction for three confirmed
families without changing Fee price authority:

1. Thermal Shock Condition extracts Method A, both temperature/dwell pairs,
   cycle count, and the derived dwell duration.
2. Thermal Shock and Temperature life use `No damage` only as an empty
   Requirement fallback.
3. Voltage surge Condition preserves Pin scope, parameter labels, values,
   units, waveform, and the `Not involved` state.

## Confirmed Business Contract

### Thermal Shock

For explicit source facts equivalent to:

`EIA-364-32, Method A, -40 ℃ (30 min), +105 ℃ (30 min); repeat 25 cycles.`

Matrix Condition becomes exactly:

`Method A, -40 ℃ (30 min), +105 ℃ (30 min); repeat 25 cycles; total 25 hours`

The duration is derived only when the same section explicitly provides two
temperature dwell durations and a cycle count:

`duration_hours = cycles * (dwell_1_minutes + dwell_2_minutes) / 60`

The accepted Method A example yields `25 * (30 + 30) / 60 = 25 hours`.
Transfer time or other unstated time is not inferred.

### Requirement Defaults

- `Thermal Shock` empty Requirement -> `No damage`.
- `Temperature life` empty Requirement -> `No damage`.
- Explicit extracted Requirement text remains authoritative and is not
  overwritten.
- Test Item family identity takes priority over incidental terms such as
  `contact resistance` inside environmental section prose.

### Voltage Surge

For explicit source facts equivalent to:

`Power Pin: Differential Mode: 10 kA, Common Mode: 20 kA, Waveform: 8/20 μs Signal Pin: Not involved`

Matrix Condition becomes exactly:

`Power Pin: Differential Mode 10 kA; Common Mode 20 kA; Waveform 8/20 μs; Signal Pin: Not involved`

The extractor must retain each label/value relationship. It accepts spacing and
case variants for `kA`, and waveform unit forms `μs`, `µs`, and `us`, while
canonicalizing output to `μs`. Voltage surge Requirement remains unchanged and
no default is introduced by this task.

## May Touch After Separate Implementation Approval

- `backend/modules/test_plan/thermal_shock_condition_parser.py` (new)
- `backend/modules/test_plan/voltage_surge_condition_parser.py` (new)
- `backend/modules/test_plan/spec_section_text_extractor.py` (narrow dispatches)
- `backend/modules/test_plan/method_template_library.py` (empty-only Requirement seeds)
- `backend/modules/test_plan/mcr_text_normalizer.py` only if a narrow Test Item
  precedence correction is still required after template fallback
- focused parser/MCR/Fee default-fill tests
- TASK_365C governance/evidence and narrow `docs/task_board.md` entries

## Must Not Touch / Locked Paths

- Fee rule seed values, active Fee manifest, prices, aliases, Unit Types, Base
  Fee policies, pricing-draft authority, exports, and workbook writers
- TASK_365A MFG parser/Fee behavior and TASK_365B PDF/DOCX infrastructure behavior
- TASK_363C/D, TASK_364B, CR/LLCR, Point Profile, and Measurement Plan
- frontend, API DTO/client/routes, database schema, repositories, migrations,
  authority lifecycle, Matrix persistence, and confirmed-record migration
- real specification files, real databases, generated outputs, release folders,
  public-drive paths, and remote Git operations

## Acceptance Criteria

1. The confirmed Thermal Shock source produces the exact canonical Condition
   and preserves Method `EIA-364-32`.
2. Thermal Shock Fee continues using the existing `30/hour` rule and reads
   Units `25`, Base Fee `0`, and Testing Fee `750` from canonical Matrix text
   without a Fee seed or Fee production-code change.
3. Missing or ambiguous Thermal Shock dwell/cycle facts do not create a derived
   hour value.
4. Thermal Shock and Temperature life fill only an empty Requirement with
   `No damage`; explicit Requirement text is preserved.
5. Incidental `contact resistance` prose cannot reclassify either environmental
   Test Item as CR.
6. Voltage surge produces the exact canonical Pin-scoped Condition for `10 kA`,
   `20 kA`, `8/20 μs`, and `Signal Pin: Not involved`.
7. Missing labels, conflicting duplicate values, or detached `kA`/`μs` tokens
   remain partial/reviewable and are not guessed into the canonical output.
8. Unrelated parser, Fee, and MCR families remain unchanged.

## Validation Gate

- TDD red/green tests with inline source text only
- pure helper tests for spacing/unit variants and missing/conflicting facts
- focused section extractor, MCR normalizer, Product Spec Matrix parser, method
  template, and Thermal Shock Fee default-fill regression
- `py_compile`, `git diff --check`, file-size, scope whitelist, and
  no-real-file/no-real-database checks

## Merge Gate

TASK_365A/TASK_365B shared parser hunks must first reach isolated Reviewer/QA
disposition. TASK_365C then requires Reviewer plan gate, explicit user
implementation approval, Developer implementation, Reviewer implementation
review, focused QA, and Integrator hunk isolation. Stop after this plan until
the user explicitly approves product implementation.
