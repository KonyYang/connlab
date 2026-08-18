# TASK_283G Report-Style Requirement Family Normalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Also read `docs/project_management/TASK_EXECUTION_SKILL.md` before implementation and execute `docs/project_management/TASK_REVIEW_CHECKLIST.md` before completion.

**Goal:** Extend deterministic Matrix Editor `Requirement` prefill for selected report-style test families while keeping Temperature rise, LLCR, and existing authority flow stable.

**Architecture:** Keep Matrix row `method/condition/requirement` as editable authority input. Add a small backend-only allowlist helper in the existing MCR extraction/normalization path, so Product Spec -> Matrix Editor prefill improves before operator review without touching Test Record generation or execution persistence.

**Tech Stack:** Python 3.11, pytest, existing `backend/modules/test_plan` parser/normalizer modules, no new dependencies.

---

## 1. Task Identity

- Task: `TASK_283G_REPORT_STYLE_REQUIREMENT_FAMILY_NORMALIZATION`
- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Plan status: Completed (2026-06-02)
- Execution mode: `superpowers:executing-plans` (serial, minimal-risk)

## 2. Why This Task Is Allowed Now

`TASK_283A/B/C/E/D/F` have completed the current Matrix MCR extraction, template fallback, review UX, and Test Record Remark binding sequence. TASK_283G was approved and completed as a controlled backend-only refinement for Matrix Editor `Requirement` prefill.

## 3. Business Context

The user provided two real reference documents:

- Product specification: `C:\Users\White\Desktop\AI information\Spec\GS-12-2113 CoolPower HDF 3.40mm product specification_20251219_Rev7.docx`
- Historical report: `C:\Users\White\Desktop\AI information\Projects\old Projects\DL-2025-11-073&074\DL-2025-11-073 Coolpower 3.40mm Pin Busbar To Socket Busbar Qualification Testing Report_Rev_A.docx`

The product specification `9.7 Qualification Test Table` drives Matrix import. The historical report section `5. TEST METHODS/REQUIREMENTS` shows the lab's report-style `Requirement` phrasing.

Important user correction: Temperature rise must keep the current concise form such as `≤ 30 ℃`. The longer report sample wording with curve text is a special case and must not become the default rule.

## 4. Scope Control

### In Scope

1. Backend-only deterministic `Requirement` family normalization.
2. Allowlisted report-style defaults for selected treatment/check families.
3. Explicit Random Vibration and Mechanical Shock discontinuity handling.
4. Regression protection for LLCR, Temperature rise, Mating/Un-mating Force, and non-allowlisted rows.
5. Mapping documentation update.

### Out Of Scope

1. No Test Record Word generation change.
2. No `TASK_283F` step-level Remark binding change.
3. No frontend UX change.
4. No API route or schema expansion.
5. No DB migration.
6. No StepInstance or execution persistence.
7. No AI/LLM interpretation.

## 5. Fixed Rule Contract

### 5.1 Preserve Existing Numeric Families

These existing behaviors must remain unchanged:

| Family | Expected Requirement |
| --- | --- |
| LLCR with initial + delta | `Initial ≤ X mΩ; ΔR ≤ Y mΩ` |
| LLCR with initial only | `Initial ≤ X mΩ` when the initial value is explicit and no delta value exists |
| CR / Contact Resistance with initial + delta | `Initial ≤ X mΩ; ΔR ≤ Y mΩ` |
| LLCR / CR single threshold without initial wording | `≤ X mΩ` when the source is a direct resistance limit |
| Resistance change only | `ΔR ≤ X mΩ` for phrases such as `10mΩ change in resistance` |
| Temperature rise | `≤ X ℃` |
| Mating/Un-mating Force | `Mating Force ≤ X N; Un-mating Force ≥ Y N` |
| Mating MAX / Un-mating MIN wording | `Mating Force ≤ X N; Un-mating Force ≥ Y N` for inputs such as `55N MAX` / `30N MIN` |
| IR / Insulation Resistance | `≥1,000MΩ (1GΩ)` when the source expresses the accepted insulation threshold |
| DWV / Dielectric Withstanding Voltage | `No evidence of arc-over... leakage current >1mA` style output must not regress |

### 5.2 Add Treatment/Check Family Defaults

When the row test item belongs to one of these allowlisted families, normalize `Requirement` to `No damage`:

| Family | Accepted aliases/examples | Requirement |
| --- | --- | --- |
| Pre-Durability | `Pre-Durability`, `Pe-Durability`, `Durability (Preconditioning 20 cycles)` | `No damage` |
| Durability | `Durability` | `No damage` |
| Reseating | `Reseating` | `No damage` |
| Thermal Shock | `Thermal Shock` | `No damage` |
| Cycling Temperature and Humidity | `Cycling Temperature& Humidity`, `Cyclic Temperature and Humidity`, `Temperature Humidity` | `No damage` |
| High Temperature Life | `High temperature Life`, `Pre-High Temperature Life` | `No damage` |
| Thermal Disturbance | `Thermal Disturbance` | `No damage` |
| MFG | `MFG`, `Mixed Flowing Gas corrosion` | `No damage` |
| Dust exposure | `Dust exposure`, `Dust Exposure` | `No damage` |

### 5.3 Add Discontinuity Family Defaults

When the row test item belongs to one of these allowlisted families, normalize `Requirement` to `No damage, No discontinuity >1us`:

| Family | Accepted aliases/examples | Requirement |
| --- | --- | --- |
| Random Vibration | `Random Vibration`, `Vibration (Random)` | `No damage, No discontinuity >1us` |
| Mechanical Shock | `Mechanical Shock` | `No damage, No discontinuity >1us` |

Unit normalization must accept `µs`, `μs`, `us`, and `uS` as input variants and always output `No damage, No discontinuity >1us`.

### 5.4 Safety Rules

1. The allowlist must be exact normalized `test_item` family matching, not broad substring guessing.
2. Do not infer `No damage` from section text alone. Words such as `thermal`, `shock`, `temperature`, or `vibration` in section text are not sufficient unless the row `test_item` matches the allowlist.
3. Do not apply `No damage` to unrelated rows with force, voltage, resistance, temperature threshold, IR, DWV, or dimensional numeric requirements.
4. Do not change Temperature rise to the longer report example. Keep `≤ X ℃`.
5. Do not change Matrix authority persistence or Test Record generation.

## 6. File-Level Change Plan

### Modify

1. `backend/modules/test_plan/mcr_text_normalizer.py`
   - Add or call a focused report-style requirement family normalizer.
   - Keep the file under the 500-line hard limit.
2. `backend/modules/test_plan/spec_section_text_extractor.py`
   - Wire the family normalization only in the existing row detail extraction path if `mcr_text_normalizer.py` is not already the right entry point.
3. `docs/task_283e_condition_requirement_rule_mapping.md`
   - Add a TASK_283G section with the allowlist and source examples.
4. `tasks/TASK_283G_REPORT_STYLE_REQUIREMENT_FAMILY_NORMALIZATION.md`
   - Mark complete only after implementation and validation.
5. `docs/task_board.md`
   - Update only after implementation completes.
6. `docs/task_plan_index.md`
   - Update after plan approval/implementation status changes.

### Test

1. `tests/unit/test_mcr_text_normalizer.py`
2. `tests/unit/test_spec_section_text_extractor.py`
3. `tests/unit/test_product_spec_matrix_parser.py`

## 7. Implementation Tasks

### Task 1: Add focused normalizer tests

**Files:**
- Modify: `tests/unit/test_mcr_text_normalizer.py`

- [ ] **Step 1: Add treatment/check family test cases**

Add a parameterized test with these cases:

```python
import pytest

@pytest.mark.parametrize(
    ("test_item", "source_text"),
    [
        ("Pre-Durability", "Number Cycles - 20 cycles."),
        ("Durability", "Number Cycles - 200 cycles. Maximum Change: 0.17 mΩ."),
        ("Reseating", "Failure Criteria - No evidence of physical damage."),
        ("Thermal Shock", "Temperature Range - from -55 to +85 ℃."),
        ("Cycling Temperature& Humidity", "Duration - 24 cycles."),
        ("High temperature Life", "Test Temperature - 125℃. Maximum Change: 0.17 mΩ."),
        ("Thermal Disturbance", "Temperature range between 15 ℃ and 85 ℃."),
        ("MFG", "Class IIA. Maximum Change: 0.17 mΩ."),
        ("Dust exposure", "Benign Dust Composition. Maximum Change: 0.17 mΩ."),
    ],
)
def test_report_style_treatment_families_normalize_requirement_to_no_damage(
    test_item: str,
    source_text: str,
) -> None:
    result = normalize_condition_requirement(
        test_item=test_item,
        condition=None,
        requirement="Maximum Change: 0.17 mΩ",
        source_text=source_text,
    )
    assert result.requirement == "No damage"
```

- [ ] **Step 2: Add vibration/shock discontinuity test cases**

```python
@pytest.mark.parametrize(
    "test_item",
    ["Random Vibration", "Vibration (Random)", "Mechanical Shock"],
)
def test_report_style_discontinuity_families_include_no_discontinuity(
    test_item: str,
) -> None:
    result = normalize_condition_requirement(
        test_item=test_item,
        condition=None,
        requirement="No discontinuities greater than 1 μs",
        source_text="No discontinuities greater than 1 μs. Maximum Change: 0.17 mΩ.",
    )
    assert result.requirement == "No damage, No discontinuity >1us"
```

- [ ] **Step 3: Add Temperature rise regression test**

```python
def test_temperature_rise_keeps_concise_threshold_not_report_curve_text() -> None:
    result = normalize_condition_requirement(
        test_item="Temperature rise (Via current cycling)",
        condition=None,
        requirement="The temperature rise shall not exceed 30 ℃.",
        source_text="Output temperature vs. Current and Voltage Drop vs. Current curve.",
    )
    assert result.requirement == "≤ 30 ℃"
```

- [ ] **Step 4: Add non-allowlisted safety test**

```python
def test_unrelated_numeric_requirement_is_not_replaced_with_no_damage() -> None:
    original = "Displacement Force ≤ 40 N"
    result = normalize_condition_requirement(
        test_item="Floater Displacement Force",
        condition=None,
        requirement=original,
        source_text=original,
    )
    assert result.requirement == original
```

- [ ] **Step 5: Add preserve-regression tests for existing numeric families**

Add or keep tests that assert the following outputs remain unchanged:

```python
def test_task283g_preserves_existing_numeric_family_rules() -> None:
    llcr = normalize_condition_requirement(
        test_item="LLCR",
        condition=None,
        requirement="shall not exceed 0.25 milliohms initially and maximum change is 0.17 milliohms",
        source_text="shall not exceed 0.25 milliohms initially and maximum change is 0.17 milliohms",
    )
    assert llcr.requirement == "Initial ≤ 0.25 mΩ; ΔR ≤ 0.17 mΩ"

    single = normalize_condition_requirement(
        test_item="Contact Resistance",
        condition=None,
        requirement="shall not exceed 25mΩ initially",
        source_text="shall not exceed 25mΩ initially",
    )
    assert single.requirement == "Initial ≤ 25 mΩ"

    cr_change = normalize_condition_requirement(
        test_item="Contact Resistance",
        condition=None,
        requirement="10mΩ change in resistance",
        source_text="10mΩ change in resistance",
    )
    assert cr_change.requirement == "ΔR ≤ 10 mΩ"

    mating = normalize_condition_requirement(
        test_item="Mating/Un-mating Force",
        condition=None,
        requirement="Mating 55N MAX, Un-mating 30N MIN",
        source_text="Mating 55N MAX, Un-mating 30N MIN",
    )
    assert mating.requirement == "Mating Force ≤ 55 N; Un-mating Force ≥ 30 N"

    ir = normalize_condition_requirement(
        test_item="Insulation Resistance",
        condition=None,
        requirement="1000 megohms minimum",
        source_text="1000 megohms minimum",
    )
    assert ir.requirement == "≥1,000MΩ (1GΩ)"
```

Also preserve the accepted DWV wording in the existing DWV test file or add a focused assertion if the project already exposes that normalizer path.

- [ ] **Step 6: Run the focused tests and verify they fail before implementation**

Run:

```powershell
py -m pytest tests/unit/test_mcr_text_normalizer.py -q
```

Expected before implementation: the new report-style family tests fail because the new allowlist behavior is not implemented yet.

### Task 2: Implement deterministic report-style requirement family normalization

**Files:**
- Modify: `backend/modules/test_plan/mcr_text_normalizer.py`

- [ ] **Step 1: Add family constants**

Add exact normalized alias sets for:

```python
_NO_DAMAGE_REQUIREMENT_FAMILIES = {
    "pre durability",
    "pe durability",
    "durability",
    "durability preconditioning 20 cycles",
    "reseating",
    "thermal shock",
    "cycling temperature humidity",
    "cyclic temperature humidity",
    "temperature humidity",
    "high temperature life",
    "pre high temperature life",
    "thermal disturbance",
    "mfg",
    "mixed flowing gas corrosion",
    "dust exposure",
}

_NO_DAMAGE_DISCONTINUITY_REQUIREMENT_FAMILIES = {
    "random vibration",
    "vibration random",
    "mechanical shock",
}
```

Normalize family labels by lowercasing and replacing punctuation with spaces. Keep matching exact against the normalized aliases. Do not pass `source_text` into this family decision.

- [ ] **Step 2: Add a report-style requirement helper**

Implement:

```python
def _normalize_report_style_family_requirement(test_item: str | None) -> str | None:
    normalized = _normalize_family_label(test_item)
    if normalized in _NO_DAMAGE_DISCONTINUITY_REQUIREMENT_FAMILIES:
        return "No damage, No discontinuity >1us"
    if normalized in _NO_DAMAGE_REQUIREMENT_FAMILIES:
        return "No damage"
    return None
```

- [ ] **Step 3: Wire helper with safe priority**

In `normalize_condition_requirement(...)`, apply this helper after existing LLCR / CR / IR / DWV / Temperature rise / Mating force logic and before returning. Do not let it override these families:

```python
report_style_requirement = _normalize_report_style_family_requirement(test_item)
if family == "other" and report_style_requirement is not None:
    normalized_requirement = report_style_requirement
    notes.append("normalized-report-style-requirement")
```

This keeps LLCR, CR, IR, DWV, Temperature rise, and Mating force behavior stable.

- [ ] **Step 4: Run focused tests**

Run:

```powershell
py -m pytest tests/unit/test_mcr_text_normalizer.py -q
```

Expected: all tests pass.

### Task 3: Add extractor/parser regression tests

**Files:**
- Modify: `tests/unit/test_spec_section_text_extractor.py`
- Modify: `tests/unit/test_product_spec_matrix_parser.py`

- [ ] **Step 1: Add extractor-level regression**

Add a test that calls `extract_row_details(...)` for these section examples:

```python
def test_report_style_requirement_family_normalization_on_section_extraction() -> None:
    vibration = extract_row_details(
        section="8.8",
        section_text=(
            "8.8 Vibration (Random) - EIA 364-28. "
            "No discontinuities greater than 1 μs. Maximum Change: 0.17 mΩ."
        ),
        test_item="Random Vibration",
    )
    assert vibration.requirement == "No damage, No discontinuity >1us"

    mfg = extract_row_details(
        section="8.6",
        section_text=(
            "8.6 Mixed Flowing Gas corrosion. "
            "Class IIA. Maximum Change: 0.17 mΩ."
        ),
        test_item="MFG",
    )
    assert mfg.requirement == "No damage"
```

- [ ] **Step 2: Add parser-level regression for real Matrix-style rows**

Add a parser test with rows for MFG, Dust exposure, Random Vibration, Mechanical Shock, and Temperature rise. Assert:

```python
assert mfg.requirement == "No damage"
assert dust.requirement == "No damage"
assert vibration.requirement == "No damage, No discontinuity >1us"
assert shock.requirement == "No damage, No discontinuity >1us"
assert temperature.requirement == "≤ 30 ℃"
```

- [ ] **Step 3: Run extractor/parser tests**

Run:

```powershell
py -m pytest tests/unit/test_spec_section_text_extractor.py tests/unit/test_product_spec_matrix_parser.py -q
```

Expected: all tests pass.

### Task 4: Update mapping documentation

**Files:**
- Modify: `docs/task_283e_condition_requirement_rule_mapping.md`

- [ ] **Step 1: Add a TASK_283G section**

Add a section named:

```markdown
## TASK_283G Report-Style Requirement Family Normalization
```

Include:

- the source spec/report file paths,
- the `No damage` allowlist,
- the `No damage, No discontinuity >1us` allowlist,
- the Temperature rise non-change rule,
- the current symbol standard: `≤`, `≥`, `ΔR`, `mΩ`, `℃`,
- the preserve-regression list for CR/IR/DWV/LLCR/Mating rules,
- the safety rule that unrelated numeric rows are not guessed.

Also fix the existing TASK_283E rows in this mapping document so they use the current symbol standard instead of old ASCII or corrupted symbols.

- [ ] **Step 2: Run diff check**

Run:

```powershell
git diff --check
```

Expected: no blocking whitespace errors. CRLF warnings are acceptable.

### Task 5: Final validation and board sync

**Files:**
- Modify: `tasks/TASK_283G_REPORT_STYLE_REQUIREMENT_FAMILY_NORMALIZATION.md`
- Modify: `docs/task_board.md`
- Modify: `docs/task_plan_index.md`

- [ ] **Step 1: Run full relevant validation**

Before running tests, execute the review checklist from `docs/project_management/TASK_REVIEW_CHECKLIST.md` and confirm the implementation did not cross into Test Record generation, API expansion, DB schema, StepInstance, or execution persistence.

Run:

```powershell
py -m pytest tests/unit/test_mcr_text_normalizer.py tests/unit/test_spec_section_text_extractor.py tests/unit/test_product_spec_matrix_parser.py -q
py -m pytest tests/unit/test_matrix_import_commit_service.py tests/unit/test_source_matrix_persistence_service.py tests/unit/test_matrix_editor_session_service.py -q
py -m pytest tests/integration/test_project_test_plan_preview_api.py tests/integration/test_matrix_editor_session_api.py -q
py -m pytest tests/integration/test_matrix_to_test_record_smoke_flow_api.py -q
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task283 or matrix_editor"
git diff --check
```

Expected:

- focused backend tests pass,
- matrix import/session integration tests pass,
- smoke flow remains green,
- no backend API/schema expansion appears in diff.

- [ ] **Step 2: Update task state after implementation passes**

Set:

- `tasks/TASK_283G_REPORT_STYLE_REQUIREMENT_FAMILY_NORMALIZATION.md` status to `Complete`.
- `docs/task_board.md` status string to include `TASK_283G complete`.
- `docs/task_board.md` current active task remains `none`.
- `docs/task_plan_index.md` latest completed task plan becomes `TASK_283G`.

## 8. Risks and Mitigation

1. Risk: accidentally replacing numeric force/voltage/resistance requirements with `No damage`.
   - Mitigation: exact family allowlist and explicit non-allowlisted numeric regression test.
2. Risk: changing Temperature rise to special report wording.
   - Mitigation: required regression that keeps `≤ X ℃`.
3. Risk: treating MFG/Dust `Maximum Change` as the row Requirement when report style expects `No damage`.
   - Mitigation: allowlisted report-style override only for selected treatment/check families.
4. Risk: expanding into Test Record generation.
   - Mitigation: no changes to `confirmed_matrix_test_record_preview_service.py` or `test_record_document_gateway.py` in this task unless a failing regression proves an existing consumer path is affected.

## 9. Validation Commands

```powershell
py -m pytest tests/unit/test_mcr_text_normalizer.py tests/unit/test_spec_section_text_extractor.py tests/unit/test_product_spec_matrix_parser.py -q
py -m pytest tests/unit/test_matrix_import_commit_service.py tests/unit/test_source_matrix_persistence_service.py tests/unit/test_matrix_editor_session_service.py -q
py -m pytest tests/integration/test_project_test_plan_preview_api.py tests/integration/test_matrix_editor_session_api.py -q
py -m pytest tests/integration/test_matrix_to_test_record_smoke_flow_api.py -q
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task283 or matrix_editor"
git diff --check
```

## 10. Completion Criteria

1. Allowlisted treatment/check family requirements render as `No damage`.
2. Random Vibration and Mechanical Shock render as `No damage, No discontinuity >1us`.
3. Temperature rise remains concise threshold format.
4. LLCR, CR, IR, DWV, resistance-change, and Mating/Un-mating behavior do not regress.
5. Non-allowlisted numeric rows are not guessed.
6. `No damage` overrides are only applied by exact normalized `test_item` family allowlist.
7. Scope boundary is held: no API expansion, no DB schema change, no Test Record generation change, no StepInstance/execution persistence.
