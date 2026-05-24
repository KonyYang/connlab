# TASK_162 No-LTR Project Cleanup Execution

> Status: complete
> Created: 2026-05-10
> Phase: Phase 10F - Real public-drive LTR workbook operational closure

---

## 1. Purpose

Provide a controlled cleanup execution path for historical Project records that have no registered LTR.

This follows `TASK_161` dry-run. The goal is to remove no-LTR project residues from the normal Project Registry by marking them cancelled with an auditable cleanup record, not by physically deleting database rows.

---

## 2. Scope

In scope:

- Add a cleanup execution API for `project_without_registered_ltr` candidates only.
- Require explicit project IDs and a human reason.
- Re-check each project at execution time before changing status.
- Change eligible Project status to `cancelled`.
- Write cleanup audit records.

Out of scope:

- No physical delete.
- No LTR recycle candidate table.
- No cleanup of invalid registered LTR numbers.
- No workbook changes.
- No automatic cleanup of projects that now have registered LTRs.

---

## 3. Acceptance Criteria

- Execution rejects projects that have any registered LTR.
- Execution marks eligible projects as `cancelled`.
- Execution writes one audit record per changed project.
- Execution is idempotent for already cancelled eligible projects.
- API tests cover success and rejection cases.

---

## 4. Completion Notes

- Added `NoLtrProjectCleanupService` for controlled no-LTR Project cleanup execution.
- Added `project_cleanup_audit_records` storage and repository.
- Added `POST /api/cleanup/project-ltr/no-ltr-projects/execute`.
- The execution path requires explicit `project_ids` and a human `reason`.
- The execution path re-checks registered LTR records before changing any Project.
- Eligible Projects are soft-cancelled with `ProjectStatus.CANCELLED`; no rows or files are physically deleted.
- Invalid registered LTR cleanup, LTR recycle handling, workbook changes, and UI filtering remain out of scope.

Validation:

- `py -m pytest tests\unit\test_no_ltr_project_cleanup_service.py tests\integration\test_cleanup_api.py -q` passed, 6 passed.
