# TASK_161 Historical Project/LTR Cleanup Dry Run

> Status: complete
> Created: 2026-05-10
> Phase: Phase 10F - Real public-drive LTR workbook operational closure

---

## 1. Purpose

Provide a read-only cleanup report for existing dirty Project/LTR records before any deletion, migration, or LTR recycle behavior is implemented.

The report must identify records created by earlier workflow bugs, including projects without registered LTR numbers and projects carrying invalid LTR numbers.

---

## 2. Scope

In scope:

- Add a read-only backend cleanup audit service.
- Add an API endpoint returning grouped cleanup candidates.
- Classify at least:
  - projects without registered LTR
  - registered LTR numbers with invalid format
  - projects with multiple registered LTR records
  - LTR records pointing to missing projects
- Include enough identifiers and labels for the operator to review before action.

Out of scope:

- No delete/soft-delete.
- No LTR recycle candidate table.
- No workbook mutation.
- No batch execution.
- No automatic correction.

---

## 3. Acceptance Criteria

- Dry-run endpoint is read-only.
- Report groups dirty records by issue type.
- Invalid LTR format includes examples such as `DL-2026-04-075810`.
- Tests cover the classification logic and API response.
- Task board is updated after validation.

---

## 4. Completion Notes (2026-05-10)

- Added read-only cleanup audit service for Project/LTR records.
- Added `GET /api/cleanup/project-ltr/dry-run`.
- The report classifies:
  - `project_without_registered_ltr`
  - `invalid_registered_ltr_number`
  - `project_multiple_registered_ltrs`
  - `orphan_ltr_record`
- No delete, update, workbook read/write, or automatic correction behavior was added.

## 5. Validation

- `py -m pytest tests/unit/test_project_ltr_cleanup_audit_service.py -q` passed (`1 passed`)
- `py -m pytest tests/integration/test_cleanup_api.py -q` passed (`1 passed`)
- Live local dry-run returned:
  - `total_projects=28`
  - `total_ltr_records=5`
  - `project_without_registered_ltr=25`
