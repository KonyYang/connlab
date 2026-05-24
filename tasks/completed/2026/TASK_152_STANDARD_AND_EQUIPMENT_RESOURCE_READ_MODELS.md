# TASK_152 Standard And Equipment Resource Read Models

> Status: proposed
> Created: 2026-05-09
> Phase: Phase 10E - External resource settings and LTR workbook authority

---

## 1. Purpose

Prepare read-only structured access to public-drive Excel resources used later by reports and project records:

- EIA / standard record Excel
- Equipment number/name/calibration Excel

This task does not implement Report Generation. It only creates stable read models and validation summaries so later report workflows do not parse Excel ad hoc.

---

## 2. Dependencies

Depends on `TASK_149` for Settings UI resource configuration.

---

## 3. Scope

In scope:

- Read configured `standard_record_excel` into a structured list/search result.
- Read configured `equipment_calibration_excel` into structured equipment rows.
- Keep reads strictly read-only.
- Expose thin API endpoints for lookup/search if needed by later UI.
- Add tests using local fixture Excel files.

Out of scope:

- No report generation.
- No writing standard/equipment Excel.
- No Matrix.
- No equipment calibration workflow.
- No AI review.

---

## 4. Design Direction

Treat Excel files as external adapters:

```text
application read service
  -> port
      -> Excel adapter
```

The structured rows should be plain domain/application DTOs, not raw worksheet cells.

---

## 5. Tests And Validation

Expected validation:

```powershell
py -m pytest tests\unit\test_excel_structure_probe.py tests\unit\test_external_resource_service.py -q
py -m pytest tests\integration\test_external_resource_api.py -q
```

Manual smoke:

1. Configure local standard and equipment Excel files in Settings.
2. Validate both.
3. Run lookup endpoint or UI probe.
4. Confirm rows are business-readable.

---

## 6. Acceptance Criteria

- Standard and equipment Excel data can be read into structured records.
- Invalid structure returns actionable validation failure.
- No writes occur.
- Later report tasks can consume these read models instead of re-parsing Excel.

