# TASK_283E_MCR_CONDITION_REQUIREMENT_NORMALIZATION_V1

## Status

Complete (2026-06-01).

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Objective

Normalize extracted row-level `Condition` and `Requirement` text into laboratory report-ready concise expressions, while preserving deterministic parsing and user editability in Matrix Editor.

Business anchor for this task:

- Matrix `Section` in Qualification Test Table points to specification section text.
- Operators currently read that section text and manually fill the report `5. TEST METHODS/REQUIREMENTS` table.
- TASK_283E standardizes this manual language conversion with deterministic rules.

Scope clarification:

TASK_283E does not generate reports and does not treat historical reports as the authority source.

The business flow is:
Product specification section text -> Matrix Editor row M/C/R prefill -> user review/confirm -> downstream Test Record / Report reuse.

Historical reports are used only as examples of concise lab wording operators normally produce when manually converting specification section requirements into report-table style expressions.

This task targets high-frequency deterministic conversions such as:

- LLCR dual-threshold wording to compact expression (`Initial <= ...; ΔR <= ...`).
- `shall not exceed`/`not less than`/`max` style limit statements to symbolic form (`<=`, `>=`).
- Multi-clause force statements (mating/un-mating) into explicit paired output.

## Scope

### In Scope

1. Add deterministic normalization rules for row-level `condition` and `requirement`.
2. Apply normalization in backend parser/extractor output before Matrix Editor prefill.
3. Keep raw extraction authority path intact; normalization is a representation transform, not a new source.
4. Add focused tests for:
   - LLCR two-part requirement.
   - Temperature rise limit conversion.
   - Mating/Un-mating force paired conversion.
   - Synonym variants (`shall not exceed`, `max`, `<=`, `not less than`, `>=`).
5. Keep output still fully editable by operator in Matrix Editor.
6. Bind normalization examples to real workflow references:
   - spec source section text
   - expected report-table style expression
7. Manual/no-section fallback is in scope for TASK_283E V1.
   - When a Matrix row has no usable Section text, normalization may use approved deterministic defaults only for explicitly allowed test families and only for empty fields.

### Out Of Scope

- No AI/LLM-based semantic rewriting.
- No historical report ingestion (belongs to TASK_283C).
- No Matrix Editor UX redesign (belongs to TASK_283D).
- No StepInstance/execution persistence/report/fee/evidence expansion.

## Required Input Resources

Minimum resources required before implementation:

1. One specification source with section text examples:
   - Primary project sample:
     `C:\Users\White\Desktop\AI information\Projects\DL-2025-11-073\DL-2025-11-073 Coolpower 3.40mm Pin Busbar To Socket Busbar Qualification Test\Submitted Material\GS-12-2113 CoolPower HDF 3.40mm product specification_20251219_Rev7.docx`
   - Optional same-source copy:
     `C:\Users\White\Desktop\AI information\Spec\GS-12-2113 CoolPower HDF 3.40mm product specification_20251219_Rev7.docx`
2. One historical report target-style reference:
   - `C:\Users\White\Desktop\AI information\Matrix Fill\DL-2024-09-074A PB Ultra Pro BTB Connector with Cable Assembly Group 7 test Report_Rev_A.docx`
3. Rule mapping table (can be created inside plan/tests) with at least:
   - `family`, `source phrase pattern`, `target normalized phrase`
4. Negative examples where text must remain unchanged.

## Manual/No-Section Fallback Rules (V1)

1. Section text remains the primary source when available.
2. No-section fallback applies only when Section is blank, missing, or unresolved.
3. Fallback may fill only empty M/C/R fields.
4. Non-empty operator-entered values must never be overwritten.
5. Unsupported or ambiguous Test Items remain blank.
6. All fallback-filled values remain editable and require user confirmation through `Confirm Matrix`.

V1 allowed fallback families:

1. Visual Examination:
   - Method: `EIA-364-18B`
   - Condition: `10x min magnification`
   - Requirement: `No detrimental condition`
2. LLCR:
   - Method only: `EIA-364-23`
   - Do not fill Condition/Requirement without numeric source text.
3. Temperature rise:
   - Do not fill Requirement without numeric source text.
4. Mating/Un-mating Force:
   - Do not fill Requirement without numeric source text.
5. Durability / MFG / Vibration / Shock:
   - Method only if family match is deterministic.
   - Do not guess Condition/Requirement.

## Acceptance Criteria

1. Supported families produce deterministic normalized expressions from common wording variants.
2. Unsupported or ambiguous text remains unchanged (no unsafe rewrite).
3. Existing `method` extraction precedence and fallback rules from TASK_283A/B remain intact.
4. Matrix Editor continues to allow manual correction before `Confirm Matrix`.
5. Tests cover both positive conversions and non-conversion safety cases.
6. At least one end-to-end fixture demonstrates:
   - section text extraction -> normalized `Condition/Requirement` -> report-table style string.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for execution because this is bounded deterministic rule engineering with parser-level and unit-level regression tests.

## Stop Rule

Create a separate implementation plan before coding.
