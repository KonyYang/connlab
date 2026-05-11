# TASK_166 LTR Project Type Workbook Mapping Plan

> Status: proposed
> Created: 2026-05-11
> Phase: Phase 10F - Real public-drive LTR workbook operational closure

---

## 1. Scope

In scope:

- Add backend-controlled Project Type -> LTR workbook E-column mapping in the workbook write preview path.
- Apply the same mapping guard to workbook commit flow through existing preview dependency.
- Add tests for:
  - mapped values are written as workbook abbreviations
  - missing mapping is blocked with actionable error
  - confirmed `Innovation` and `Lab Activities (Lab Use Only)` map to `ADM`
- Update `docs/task_board.md` with completion notes and validation summary after implementation.

Out of scope:

- No frontend changes.
- No SQLite configurable mapping table in this task.
- No lookup options UI/configuration extension.

---

## 2. Mapping Decision (Confirmed)

This task applies the following fixed mapping:

- `New Product Development` -> `NPD`
- `Product Extension` -> `PEX`
- `Innovation` -> `ADM`
- `Lab Activities (Lab Use Only)` -> `ADM`
- `Operational Support` -> `OPS`
- `Cost Reduction` -> `CR`

Any other value is rejected before workbook write with:

- `Project Type has no LTR workbook mapping: <value>`

---

## 3. File-Level Changes

1. `backend/application/ltr_workbook_write_preview_service.py`
- Add a private mapping function for Project Type workbook value conversion.
- Replace direct `form.project_type` passthrough with mapped workbook value.
- Raise `LtrWorkbookWritePreviewError` when mapping is missing or source is empty.

2. `tests/unit/test_ltr_workbook_write_preview_service.py`
- Update expected E-column value to mapped abbreviation.
- Add explicit tests for `Innovation` and `Lab Activities (Lab Use Only)` -> `ADM`.
- Add test for unmapped Project Type rejection.

3. `tests/unit/test_ltr_workbook_write_commit_service.py`
- Add test asserting commit fails when Project Type mapping is missing (through preview call).

4. `tests/integration/test_ltr_workbook_write_preview_api.py`
- Assert E-column preview value is mapped abbreviation.

5. `docs/task_board.md`
- Add a completion note for this controlled mapping task with test validation summary.

---

## 4. Risks and Controls

Risk:
- Existing data may contain Project Type values outside the six confirmed options.

Control:
- Strong fail-fast validation prevents wrong workbook writes and returns actionable error for business correction.

Risk:
- Mapping behavior change may affect existing test assumptions.

Control:
- Update impacted tests and add explicit mapping regression tests.

---

## 5. Validation Plan

Run focused tests:

- `py -m pytest tests/unit/test_ltr_workbook_write_preview_service.py -q`
- `py -m pytest tests/unit/test_ltr_workbook_write_commit_service.py -q`
- `py -m pytest tests/integration/test_ltr_workbook_write_preview_api.py -q`

Optional broader confidence run if needed:

- `py -m pytest tests/unit tests/integration -q`

