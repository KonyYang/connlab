# TASK_283E Condition/Requirement Rule Mapping (V1)

Purpose:

- Deterministic normalization mapping from specification-section wording to Matrix Editor row M/C/R prefill expressions.
- This is formatting/reference guidance for Matrix confirmation workflow, not a report-generation authority.

## Family Rules

| Family | Source Phrase Pattern (examples) | Normalized Output |
|---|---|---|
| LLCR | `shall not exceed 0.25 milliohms initially` + `maximum change is 0.17 milliohms` | `Initial <= 0.25 m惟; 螖R <= 0.17 m惟` |
| Temperature rise | `shall not exceed 30 C` / `Max 30 C` / `<= 30 C` | `<= 30 鈩僠 |
| Mating/Un-mating Force | `... shall not exceed 20N ... shall not less than 6N` | `Mating Force <= 20 N; Un-mating Force >= 6 N` |

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

