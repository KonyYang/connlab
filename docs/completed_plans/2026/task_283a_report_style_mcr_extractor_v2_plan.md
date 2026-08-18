# TASK_283A Report-Style MCR Extractor V2 Plan

> REQUIRED SUB-SKILL: Use `superpowers:test-driven-development` and `superpowers:executing-plans`. Implement serially. Do not parallelize parser changes.

## Current Phase And Gate

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task before planning: none.
- Proposed task: `TASK_283A_REPORT_STYLE_MCR_EXTRACTOR_V2`.
- Allowed reason: TASK_282 is complete and the user requested the next controlled Method/Condition/Requirement automation task.
- Implementation gate: do not write implementation code until the user explicitly approves TASK_283A execution.

## Task Understanding

Input:

- Imported engineering specification `.docx`.
- Matrix rows with `Test Items` and `Section`.
- Specification section body text already available through the TASK_282 parser path.

Output:

- Better row-level `method`, `condition`, and `requirement` strings for Matrix Editor.
- Values remain editable and user-confirmed through `Confirm Matrix`.

Non-output:

- No Method Library persistence.
- No historical Test Report ingestion.
- No UI review redesign.
- No report generation expansion.

## Design Strategy

TASK_283A improves extraction quality only. It does not add a new data source.

The implementation should separate three concepts:

1. `section block`: raw text from the specification section.
2. `extraction candidates`: standards, conditions, and requirements found in the block.
3. `report-style formatter`: deterministic rules that turn candidates into concise MCR cell text.

## Target Examples From GS-12-2113

The first implementation should target representative rows from the real GS-12-2113 pattern:

| Section | Test Item | Target Direction |
| --- | --- | --- |
| 5.4 | Examination of Product | Lab default visual inspection wording unless section explicitly says otherwise |
| 6.1 | Contact Resistance (Low Level) | EIA-364-23, 20mV/100mA, initial and delta resistance limits |
| 6.2 | Contact Resistance, Specified Current | EIA-364-06C, 75ADC, voltage drop limit |
| 6.3.1 | Temperature rise | EIA-364-70, Method 2/current, T-Rise limit |
| 7.1 | Mating/Un-mating Force | EIA-364-37, speed, mate/un-mate force limits |
| 7.2/7.3 | Durability | cycles/rate when explicit; no damage/change criterion when explicit |
| 8.1 | Thermal Shock | EIA-364-32, temperature range/cycles/dwell, no damage/change criterion |
| 8.2 | Cycling Temperature& Humidity | EIA-364-31, temperature/RH/cycles/dwell, no damage/change criterion |
| 8.3/8.4 | High Temperature Life | EIA-364-17, temperature/duration, no damage/change criterion |
| 8.5 | Thermal Disturbance | EIA-364-110, temperature range/ramp/dwell/cycles, no damage/change criterion |
| 8.6 | MFG | EIA-364-65, Class IIA and unmated/mated duration, no damage/change criterion |
| 8.7 | Dust exposure | EIA-364-91, dust composition when explicit, no damage/change criterion |
| 8.8 | Random Vibration | EIA-364-28, condition/axis duration, no discontinuity |
| 8.9 | Mechanical Shock | EIA-364-27, 50G/11ms/shocks, no discontinuity |

Exact wording will be locked by tests only for deterministic cases.

## Implementation Steps

### Step 1: Add Failing Extractor Tests

Files:

- `tests/unit/test_spec_section_text_extractor.py`

Add tests for:

1. Visual family aliases (`Visual Examination`, `Examination`, `Examination of Product`, `Visual Inspection`, `Visual Check`) fill the lab default visual-inspection values when no explicit conflicting method/condition/requirement is present: `EIA-364-18B`, `10x min magnification`, `No detrimental condition`.
2. LLCR extracts method, voltage/current condition, initial and delta requirement.
3. Specified-current resistance extracts current condition and voltage requirement.
4. Temperature rise extracts method/current or safe partial output and never emits method-number fragments as condition.
5. Mating/Un-mating Force extracts speed and force limits when explicit.
6. Durability extracts cycle count/rate or safe partial output.
7. Thermal Shock extracts temperature range/cycles/dwell or safe partial output.
8. Temperature/humidity does not return `31 a` and extracts temperature/RH/cycles/dwell when explicit.
9. High Temperature Life extracts temperature/duration or safe partial output.
10. Thermal Disturbance extracts temperature range/ramp/dwell/cycles or safe partial output.
11. MFG does not return `65 a` and extracts Class/duration.
12. Dust extracts dust composition or safe partial output and does not invent values.
13. Random Vibration extracts condition/axis duration and no-discontinuity requirement when explicit.
14. Mechanical Shock extracts 50G/11ms/shock count and no-discontinuity requirement when explicit.
15. Maximum Change is not truncated to `0`.
16. Unknown/ambiguous section leaves fields blank or partial instead of inventing values.

Command:

```powershell
py -m pytest tests\unit\test_spec_section_text_extractor.py -q
```

Expected before implementation: newly added tests fail.

### Step 2: Refine Candidate Extraction Helpers

Files:

- `backend/modules/test_plan/spec_section_text_extractor.py`

Add or refine small helpers:

```text
extract_standard_method()
extract_voltage_current_condition()
extract_temperature_condition()
extract_duration_cycles_condition()
extract_force_requirement()
extract_resistance_requirement()
extract_no_damage_or_discontinuity_requirement()
```

Rules:

- Prefer explicit text from the section.
- Visual family is the only TASK_283A default exception. For tested Visual aliases, fill the lab default values `EIA-364-18B`, `10x min magnification`, and `No detrimental condition` when no explicit conflicting value is present. Do not apply this default to non-Visual rows.
- Normalize common EIA method formatting.
- Preserve useful standard revisions when explicit, for example `EIA-364-06C`.
- Avoid using method numbers as condition text.
- Do not infer missing numeric limits unless a narrow test fixture explicitly permits a default.

### Step 3: Add Report-Style Formatters Per Family

Files:

- `backend/modules/test_plan/spec_section_text_extractor.py`

Use row `test_item` and section content to choose small deterministic family formatters:

```text
LLCR
specified current resistance
temperature rise
force
durability
thermal shock
temperature humidity
MFG
vibration
shock
```

Guard:

- Family formatters must be short and test-covered.
- If formatter confidence is low, return partial output.

### Step 4: Parser Integration Regression

Files:

- `tests/unit/test_product_spec_matrix_parser.py`

Add one compact parser-level fixture proving MCR improvements attach to `MatrixRowPreview` rows, not only the extractor helper.

Command:

```powershell
py -m pytest tests\unit\test_product_spec_matrix_parser.py -q
```

### Step 5: Keep Existing Data Flow Stable

Run existing TASK_282 flow tests:

```powershell
py -m pytest tests\unit\test_source_matrix_persistence_service.py -q
py -m pytest tests\unit\test_matrix_editor_session_service.py -q
py -m pytest tests\unit\test_matrix_import_commit_service.py -q
py -m pytest tests\integration\test_project_test_plan_preview_api.py -q
py -m pytest tests\integration\test_matrix_editor_session_api.py -q
```

Expected: no source snapshot/session regression.

### Step 6: Frontend Regression Only

TASK_283A should not require new UI behavior. Run Matrix Editor regression:

```powershell
cd frontend
npm test -- --run MatrixEditorWorkspace --watch=false
npm run build
```

### Step 7: Static Guard And Scope Check

Run:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task283 or task282 or matrix_editor"
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
git diff --check
```

## Files Expected To Change

Likely:

- `backend/modules/test_plan/spec_section_text_extractor.py`
- `tests/unit/test_spec_section_text_extractor.py`
- `tests/unit/test_product_spec_matrix_parser.py`
- `docs/task_board.md`
- `docs/task_plan_index.md`
- `tasks/TASK_283A_REPORT_STYLE_MCR_EXTRACTOR_V2.md`

Possible but avoid unless necessary:

- `backend/modules/test_plan/product_spec_matrix_parser.py`

Not expected:

- Frontend source changes.
- Database/schema changes.
- API route changes.
- Test Record generation code.

## Risk Controls

- Wrong values are worse than blanks: leave uncertain fields blank or partial.
- Do not apply historical report wording or broad template defaults in TASK_283A.
- The only approved default is the Visual family lab default; it is alias-gated and must not override explicit conflicting section text.
- Do not add broad fuzzy matching.
- Keep parser files under AGENTS.md hard limits.
- Keep row-level MCR distinct from step-level preview metadata.

## Review Checklist

- [ ] Domain/application/infrastructure boundaries remain unchanged.
- [ ] No frontend Office or filesystem access.
- [ ] No AI/LLM.
- [ ] No Method Library persistence.
- [ ] No historical Test Report import.
- [ ] Existing Matrix Editor import/session/confirm behavior remains stable.
- [ ] Tests cover the real bad examples: `31 a`, `65 a`, and truncated `Maximum Change: 0`.
- [ ] Every In Scope family has at least one unit-test assertion, including safe-partial or blank behavior where appropriate.

## Stop Rule

After TASK_283A implementation and validation, stop. Do not continue into TASK_283B/C/D without a separate approval.
