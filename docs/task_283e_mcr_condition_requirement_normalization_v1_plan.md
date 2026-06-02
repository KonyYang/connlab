# TASK_283E Implementation Plan - MCR Condition/Requirement Normalization V1

## 1. Task Identity

- Task: `TASK_283E_MCR_CONDITION_REQUIREMENT_NORMALIZATION_V1`
- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Plan status: Draft for review (no implementation yet)
- Execution mode: `superpowers:executing-plans` (serial slices)

## 2. Why This Task Is Allowed Now

`TASK_283A` and `TASK_283B` established deterministic row-level MCR extraction and fallback. Current gap is report-ready phrasing for `Condition` and `Requirement` strings. This task is a bounded deterministic extension on top of existing row-level MCR flow.

Business-chain clarification:

TASK_283E does not generate reports and does not treat historical reports as the authority source.

The business flow is:
Product specification section text -> Matrix Editor row M/C/R prefill -> user review/confirm -> downstream Test Record / Report reuse.

Historical reports are expression references only.

## 3. Objective

Produce deterministic normalized expressions for high-frequency lab wording so Matrix Editor starts with concise values and operators only review/adjust.

Workflow alignment:

1. Parse Matrix row and its `Section`.
2. Resolve corresponding specification section text.
3. Convert raw extracted wording to report-table style (`5. TEST METHODS/REQUIREMENTS`) deterministic expression.
4. Keep value editable in Matrix Editor.

Examples in scope:

1. LLCR:
   - input: `shall not exceed 0.25 milliohms initially and maximum change is 0.17 milliohms after ...`
   - output: `Initial <= 0.25 m惟; 螖R <= 0.17 m惟`
2. Temperature rise:
   - input: `shall not exceed 30 鈩僠
   - output: `<= 30 鈩僠
3. Mating/Un-mating force:
   - input: `... shall not exceed 20N ... shall not less than 6N`
   - output: `Mating Force <= 20 N; Un-mating Force >= 6 N`

## 3.1 Key Resources (Confirmed for this task)

1. Specification source reference:
   - Primary project sample:
     `C:\Users\White\Desktop\AI information\Projects\DL-2025-11-073\DL-2025-11-073 Coolpower 3.40mm Pin Busbar To Socket Busbar Qualification Test\Submitted Material\GS-12-2113 CoolPower HDF 3.40mm product specification_20251219_Rev7.docx`
   - Optional same-source copy:
     `C:\Users\White\Desktop\AI information\Spec\GS-12-2113 CoolPower HDF 3.40mm product specification_20251219_Rev7.docx`
2. Report-style target reference:
   - `C:\Users\White\Desktop\AI information\Matrix Fill\DL-2024-09-074A PB Ultra Pro BTB Connector with Cable Assembly Group 7 test Report_Rev_A.docx`
3. Existing seed candidate inventory from TASK_283C:
   - `docs/task_283c_matrix_fill_seed_inventory.md`
4. Internal mapping artifact to produce in this task:
   - `docs/task_283e_condition_requirement_rule_mapping.md` (new, deterministic examples + expected output)

## 4. Hard Constraints

1. Deterministic only (no AI inference).
2. Unsupported or ambiguous text must remain unchanged.
3. Keep parser files within AGENTS line limits; split helpers if needed.
4. Do not change API contracts unless strictly required.
5. Do not modify frontend workflow in this task.

## 5. Proposed Design

### 5.1 New normalization module

Add a dedicated helper module under `backend/modules/test_plan/`, e.g.:

- `mcr_text_normalizer.py`

Responsibilities:

1. Unit normalization (`milliohms` -> `m惟`, spacing unification).
2. Comparator normalization (`shall not exceed`/`max` -> `<=`, `not less than`/`min` -> `>=`).
3. Family-aware canonicalization for:
   - LLCR
   - Temperature rise
   - Mating/Un-mating force

### 5.2 Integration point

Apply normalization after row-level extraction/fallback assembly in extractor path, before values are attached to `MatrixRowPreview`.

### 5.3 Safety model

1. Rule must require explicit pattern match.
2. If rule cannot parse complete pair (e.g., mating but no un-mating threshold), keep original text.
3. Never emit synthetic numbers; only transform extracted numeric text.

### 5.4 Normalization policy V1 (fixed)

1. Comparator normalization:
   - `shall not exceed`, `must not exceed`, `max` -> `<=`
   - `shall not less than`, `not less than`, `min` -> `>=`
2. Unit canonicalization:
   - `milliohms`/`mohm` -> `m惟`
   - `C`/`鈩僠 -> `鈩僠
   - `N` and `A` keep uppercase with standardized spacing.
3. Family templates:
   - LLCR: `Initial <= X m惟; 螖R <= Y m惟`
   - Temperature rise: `<= X 鈩僠
   - Mating/Un-mating Force: `Mating Force <= X N; Un-mating Force >= Y N`
4. Non-conversion rule:
   - if required pair/units are missing or ambiguous, return original extracted text.

### 5.5 Manual/No-Section fallback policy V1 (fixed)

1. Section text is primary when available.
2. No-section fallback applies only when Section is blank, missing, or unresolved.
3. Fallback may fill only empty fields.
4. Non-empty operator-entered values are never overwritten.
5. Unsupported/ambiguous test items remain blank.
6. All fallback values remain editable and require `Confirm Matrix`.

Allowed V1 fallback scope:

1. Visual Examination:
   - Method `EIA-364-18B`
   - Condition `10x min magnification`
   - Requirement `No detrimental condition`
2. LLCR:
   - Method only `EIA-364-23`
   - no synthetic Condition/Requirement without numeric source text
3. Temperature rise:
   - no synthetic Requirement without numeric source text
4. Mating/Un-mating Force:
   - no synthetic Requirement without numeric source text
5. Durability / MFG / Vibration / Shock:
   - method-only fallback when family match is deterministic
   - no guessed Condition/Requirement

## 6. File-Level Change Plan

1. Add `backend/modules/test_plan/mcr_text_normalizer.py`
2. Update `backend/modules/test_plan/spec_section_text_extractor.py` integration
3. Add tests:
   - `tests/unit/test_mcr_text_normalizer.py`
4. Update parser/extractor tests:
   - `tests/unit/test_spec_section_text_extractor.py`
   - `tests/unit/test_product_spec_matrix_parser.py`
5. Chain guard tests:
   - `tests/unit/test_matrix_import_commit_service.py` (ensure normalized text survives)
   - `tests/integration/test_project_test_plan_preview_api.py` (preview output shape intact)
6. Add task artifact:
   - `docs/task_283e_condition_requirement_rule_mapping.md`

## 7. Test Matrix (Must Cover)

1. LLCR complete dual-threshold conversion.
2. LLCR partial text should not produce malformed compact output.
3. Temperature rise variant forms:
   - `shall not exceed 30 C`
   - `Max 30 C`
4. Mating/un-mating paired conversion with synonyms:
   - `not exceed` + `not less than`
   - existing symbolic forms (`<=`, `>=`) idempotency.
5. Negative cases:
   - ambiguous/no numeric unit
   - unrelated family text
6. Section-to-report style fixtures (at least 3):
   - exact phrase from spec section mapped to compact report expression
   - synonym phrase variant mapped to same output
   - unresolved phrase remains unchanged
7. Manual/no-section fallback tests:
   - Section available -> section-derived values are normalized
   - Section blank/unresolved -> apply approved fallback only for empty fields
   - existing non-empty M/C/R are not overwritten
   - unsupported no-section test item remains blank
   - LLCR no-section fallback fills method only
   - Mating/Un-mating no-section fallback does not invent force values

## 8. Risks and Mitigation

1. Risk: Over-normalization changes meaning.
   - Mitigation: family-aware strict regex + non-conversion fallback.
2. Risk: Unit/encoding variants (`C`, `鈩僠, `mohm`, `milliohms`).
   - Mitigation: canonical unit map with tests.
3. Risk: parser file growth.
   - Mitigation: keep normalization logic in dedicated module.

## 9. Validation Commands (Implementation Phase)

1. `py -m pytest tests/unit/test_mcr_text_normalizer.py tests/unit/test_spec_section_text_extractor.py tests/unit/test_product_spec_matrix_parser.py -q`
2. `py -m pytest tests/unit/test_matrix_import_commit_service.py -q`
3. `py -m pytest tests/integration/test_project_test_plan_preview_api.py tests/integration/test_matrix_editor_session_api.py -q`
4. `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task283 or matrix_editor"`
5. `git diff --check`

## 10. Completion Criteria

1. Target examples convert into deterministic compact expressions.
2. Non-target text remains unchanged.
3. Parser/import/preview chains remain stable.
4. No scope expansion beyond deterministic backend normalization.
5. Mapping artifact (`docs/task_283e_condition_requirement_rule_mapping.md`) is delivered and test-covered.

