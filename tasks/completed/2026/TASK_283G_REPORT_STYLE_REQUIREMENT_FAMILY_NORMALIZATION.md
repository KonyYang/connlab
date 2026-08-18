# TASK_283G_REPORT_STYLE_REQUIREMENT_FAMILY_NORMALIZATION

## Status

Complete (2026-06-02).

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Objective

Improve Matrix Editor `Requirement` prefill for selected report-style test families by using deterministic, allowlisted family rules derived from real product specification and historical report examples.

The task fills or normalizes Matrix row `Requirement` text before operator review. It does not change Test Record generation, StepInstance, execution persistence, or the Confirmed Matrix authority lifecycle.

## Source Examples

Use these business examples as reference material during implementation:

1. Product specification:
   - `C:\Users\White\Desktop\AI information\Spec\GS-12-2113 CoolPower HDF 3.40mm product specification_20251219_Rev7.docx`
   - Matrix source is the `9.7 Qualification Test Table`.
2. Historical report style reference:
   - `C:\Users\White\Desktop\AI information\Projects\old Projects\DL-2025-11-073&074\DL-2025-11-073 Coolpower 3.40mm Pin Busbar To Socket Busbar Qualification Testing Report_Rev_A.docx`
   - Reference table is section `5. TEST METHODS/REQUIREMENTS`.

## Business Rule

For selected families, the report-style `Requirement` is not always the same as every numeric phrase found in the product specification section.

Examples:

- Durability, thermal shock, humidity, high temperature life, MFG, dust exposure, and other explicitly allowlisted treatment/check families normally use `No damage`.
- Random Vibration and Mechanical Shock normally use `No damage, No discontinuity >1us`.
- Temperature rise must keep the current concise threshold style, for example `≤ 30 ℃`. Do not replace it with the longer report sample wording.

## Scope

### In Scope

1. Add a deterministic allowlist for report-style family `Requirement` normalization.
2. Apply the allowlist only to Matrix Editor MCR prefill/extraction path.
3. Preserve existing LLCR, temperature-rise, and mating/un-mating force normalization behavior.
4. Add tests that cover:
   - treatment/check families mapped to `No damage`.
   - Random Vibration and Mechanical Shock mapped to `No damage, No discontinuity >1us`.
   - Temperature rise remains `≤ X ℃`.
   - unrelated or ambiguous rows are not guessed.
5. Update the TASK_283E mapping artifact or add a TASK_283G mapping artifact with the new allowlist and examples.

### Out Of Scope

1. No Test Record Word generation behavior change.
2. No TASK_283F step-level Remark binding change.
3. No StepInstance model.
4. No execution data persistence.
5. No report-generation redesign.
6. No AI/LLM interpretation.
7. No frontend UX changes unless a static guard needs a wording update.

## Acceptance Criteria

1. Matrix Editor prefill maps allowlisted treatment/check family `Requirement` values to `No damage`.
2. Matrix Editor prefill maps Random Vibration and Mechanical Shock `Requirement` values to `No damage, No discontinuity >1us`.
3. Temperature rise output remains concise threshold style, for example `≤ 30 ℃`.
4. LLCR output remains unchanged:
   - `Initial ≤ X mΩ; ΔR ≤ Y mΩ` when both thresholds exist.
   - no guessed `ΔR` when the delta value is absent.
5. Recently accepted CR, IR, DWV, LLCR single-threshold, resistance-change, and mating MAX/MIN normalization rules do not regress.
6. Non-allowlisted rows keep existing extracted text or remain `Needs review`; no new guessed values.
7. `No damage` and `No damage, No discontinuity >1us` are applied only by exact normalized `test_item` family allowlist match, never by guessing from section text alone.
8. Scope boundary is held: no API expansion, no DB schema change, no Test Record generation change, no StepInstance/execution persistence.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task because it is a bounded deterministic backend normalization task with explicit family allowlists, fixture-driven tests, and no broad architecture change.

## Stop Rule

Create and approve a separate implementation plan before coding.
