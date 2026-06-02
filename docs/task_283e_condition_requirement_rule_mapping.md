# TASK_283E Condition/Requirement Rule Mapping (V1)

Purpose:

- Deterministic normalization mapping from specification-section wording to Matrix Editor row M/C/R prefill expressions.
- This is formatting/reference guidance for Matrix confirmation workflow, not a report-generation authority.

## Family Rules

| Family | Source Phrase Pattern (examples) | Normalized Output |
|---|---|---|
| LLCR | `shall not exceed 0.25 milliohms initially` + `maximum change is 0.17 milliohms` | `Initial ≤ 0.25 mΩ; ΔR ≤ 0.17 mΩ` |
| Temperature rise | `shall not exceed 30 C` / `Max 30 C` / `≤ 30 C` | `≤ 30 ℃` |
| Mating/Un-mating Force | `... shall not exceed 20N ... shall not less than 6N` | `Mating Force ≤ 20 N; Un-mating Force ≥ 6 N` |

## TASK_283G Report-Style Requirement Family Normalization

Source examples:

- Product specification: `C:\Users\White\Desktop\AI information\Spec\GS-12-2113 CoolPower HDF 3.40mm product specification_20251219_Rev7.docx`
- Historical report: `C:\Users\White\Desktop\AI information\Projects\old Projects\DL-2025-11-073&074\DL-2025-11-073 Coolpower 3.40mm Pin Busbar To Socket Busbar Qualification Testing Report_Rev_A.docx`

Current symbol standard:

- Use `≤`, `≥`, `ΔR`, `mΩ`, and `℃` in normalized output.
- Discontinuity output is fixed to ASCII time unit `>1us`.

Allowlisted `No damage` families:

- Pre-Durability / Pe-Durability / Durability (Preconditioning 20 cycles)
- Durability
- Reseating
- Thermal Shock
- Cycling Temperature and Humidity / Cyclic Temperature and Humidity / Temperature Humidity
- High Temperature Life / Pre-High Temperature Life
- Thermal Disturbance
- MFG / Mixed Flowing Gas corrosion
- Dust exposure

Allowlisted discontinuity families:

- Random Vibration / Vibration (Random) -> `No damage, No discontinuity >1us`
- Mechanical Shock -> `No damage, No discontinuity >1us`

Preserve-regression families:

- LLCR and CR initial/delta rules.
- LLCR/CR single threshold rules.
- Resistance-change-only rules, for example `ΔR ≤ 10 mΩ`.
- Mating MAX / Un-mating MIN rules.
- IR threshold output, for example `≥1,000MΩ (1GΩ)`.
- DWV arc-over/leakage wording.
- Temperature rise remains concise threshold output, for example `≤ 30 ℃`.

Safety rule:

- `No damage` and `No damage, No discontinuity >1us` are applied only by exact normalized `test_item` family allowlist match.
- Do not infer `No damage` from section text alone.
- Non-allowlisted numeric rows remain extracted or require review; no values are guessed.

## No-Section Fallback (V1)

| Family | Allowed Fallback |
|---|---|
| Visual Examination | Method `EIA-364-18B`, Condition `10x min magnification`, Requirement `No detrimental condition` |
| LLCR | Method only `EIA-364-23` |
| Temperature rise | No synthetic requirement without numeric source text |
| Mating/Un-mating Force | No synthetic requirement without numeric source text |
| Durability/MFG/Vibration/Shock | Method-only fallback when family match is deterministic |

## Non-Conversion Safety

1. Unsupported or ambiguous text remains unchanged.
2. Non-empty operator-entered fields are never overwritten.
3. Numeric values are never invented.

