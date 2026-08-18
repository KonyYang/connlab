# TASK_283A_REPORT_STYLE_MCR_EXTRACTOR_V2

## Status

Complete.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Allowed Reason

TASK_282 is complete and the user requested the next controlled improvement for Matrix Editor Method/Condition/Requirement automation. This task is limited to deterministic report-style extraction from the same imported engineering specification, using the existing Matrix row `Section` values and keeping all values editable before `Confirm Matrix`.

## Objective

Improve the current specification-section Method/Condition/Requirement extraction so Matrix Editor prefilled values are closer to the manually prepared `5. TEST METHODS/REQUIREMENTS` table in real Test Reports.

The first target real-file behavior is the GS-12-2113 CoolPower HDF specification and its corresponding manually completed report table. The goal is not perfect natural-language understanding; it is to make common EIA-364 rows produce report-style Method/Condition/Requirement values with deterministic, test-covered rules.

## Business Context

Lab engineers currently read the engineering specification section body and manually summarize it into report-ready rows:

```text
Test Items | Test Method | Condition | Requirement
```

TASK_282 started direct section extraction, but some extracted values are too raw or wrong for report use, for example condition fragments such as `31 a` or incomplete requirements such as `Maximum Change: 0`. TASK_283A tightens this extraction without introducing a method library database or historical-report learning.

## Scope

### In Scope

1. Improve `spec_section_text_extractor.py` deterministic extraction for report-style fields.
2. Add test fixtures based on representative GS-12-2113 section text.
3. Cover common EIA-364 families:
   - Visual Examination / Design and Construction.
   - LLCR.
   - Specified-current contact resistance.
   - Temperature rise.
   - Mating/Un-mating Force.
   - Durability.
   - Thermal Shock.
   - Temperature/Humidity.
   - High Temperature Life.
   - Thermal Disturbance.
   - MFG.
   - Dust.
   - Random Vibration.
   - Mechanical Shock.
   Each listed family must have at least one unit-test assertion in TASK_283A. For lower-confidence families, the minimum acceptable assertion is that extraction leaves uncertain fields blank or partial and does not emit known bad fragments.
4. Fix known bad extraction fragments such as `31 a`, `65 a`, and truncated `Maximum Change: 0`.
5. Keep output editable and user-confirmed through Matrix Editor.
6. Preserve existing parser, source snapshot, session, and confirm flows.

### Out Of Scope

Do not implement in TASK_283A:

- A persistent Method Library.
- Importing historical Test Reports.
- UI for reviewing extraction confidence.
- AI/LLM summarization.
- StepInstance, execution persistence, evidence/image, report generation expansion, fee, permissions, or multi-user behavior.
- Any automatic post-load overwrite of user-edited Matrix Editor cells.

## Data Contract

No new persistent data model is expected in TASK_283A.

The task improves existing row-level fields:

```text
method
condition
requirement
detail_extraction_status
detail_extraction_notes
```

If confidence is insufficient, leave a field blank rather than inventing values.

## Acceptance Criteria

1. GS-12-2113-like Visual/Examination rows use the lab default visual-inspection rule:
   - Match only a tested Visual family alias such as `Visual Examination`, `Examination`, `Examination of Product`, `Visual Inspection`, or `Visual Check`.
   - If the section text does not explicitly specify another method, fill Method as `EIA-364-18B`.
   - Fill Condition as `10x min magnification`.
   - Fill Requirement as `No detrimental condition`.
   - If the section text explicitly specifies a conflicting method/condition/requirement, prefer explicit text and add an extraction note.
2. LLCR produces:
   - Method from the EIA-364-23 section reference.
   - Condition from test voltage/current details.
   - Requirement including initial limit and delta/change limit.
3. Specified-current contact resistance produces current condition and voltage-drop requirement.
4. Environmental rows do not output bad fragments such as `31 a`, `65 a`, or truncated `Maximum Change: 0`.
5. High Temperature Life, Thermal Disturbance, Dust, Durability, Temperature Rise, Force, Vibration, and Shock each have at least one test-covered report-style or safe-partial extraction behavior.
6. Existing TASK_282 parser, persistence, session, API, and frontend tests still pass.
7. No Method Library or historical-report import is introduced.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for execution.

Reason:

- This is a bounded deterministic parser-quality task.
- The implementation can be driven by targeted unit tests and real-file smoke tests.
- No broad architecture or frontend redesign is required.

## Required Plan

Implementation must follow:

```text
docs/task_283a_report_style_mcr_extractor_v2_plan.md
```

Do not implement until that plan is reviewed and explicitly approved.
