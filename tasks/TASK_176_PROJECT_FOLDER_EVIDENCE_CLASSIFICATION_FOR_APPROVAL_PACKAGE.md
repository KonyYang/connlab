# TASK_176 Project Folder Evidence Classification For Approval Package

> Status: complete
> Created: 2026-05-12
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 0. Execution Gate

- Current phase at creation time: `Phase 11`
- Current active task in board at creation time: `none; TASK_175 complete`
- Why this task is allowed now: `TASK_175_PROJECT_TEST_PLAN_REVIEW_AND_DRAFT_PERSISTENCE` is complete, and the user approved execution of the next controlled task.
- User approval: `批准执行 TASK_176`

---

## 1. Purpose

Align project-folder evidence placement with the approval-package business workflow.

The project folder already supports safe evidence preview and no-overwrite copy. This task narrows the classification target for approval-package inputs:

- source emails belong in `E-mail`;
- customer-submitted documents, product specifications, application forms, fee forms, and test-record templates belong in `Submitted Material`;
- photos belong in `Photos`;
- result data remains outside this task.

---

## 2. Scope

In scope:

- Refine deterministic evidence classification target folders.
- Keep preview-before-copy and no-overwrite behavior unchanged.
- Preserve source traceability through existing `FileAsset` records.
- Update backend tests for approval-package folder expectations.

Out of scope:

- No frontend/UI changes.
- No Section 2 preview or write-back.
- No test record template generation.
- No fee evaluation generation.
- No report generation.
- No Matrix UI.
- No Office file mutation.
- No folder overwrite strategy.
- No PDF or `.doc` parsing.

---

## 3. Business Rules

Target folders:

```text
E-mail/
  *.msg

Submitted Material/
  application/request forms
  product specifications
  customer documents
  drawings
  fee evaluation forms
  test record templates
  supporting approval-package documents

Photos/
  images
```

Existing specialized evidence such as LTR audit evidence and corrections may remain in dedicated subfolders under `Submitted Material`, because they are not the core approval-package source documents.

---

## 4. Acceptance Criteria

- `.msg` evidence is planned under `E-mail`.
- product specification files are planned directly under `Submitted Material`.
- application forms are planned directly under `Submitted Material`.
- fee evaluation and test-record template files are planned under `Submitted Material`.
- image files are planned under `Photos`.
- preview detects conflicts before copy.
- execution copies without overwrite.
- existing evidence placement API remains stable.
- targeted tests pass.

---

## 5. Validation Plan

```powershell
py -m pytest tests\unit\test_evidence_placement_service.py tests\integration\test_evidence_placement_api.py -q
```

Related folder smoke if needed:

```powershell
py -m pytest tests\integration\test_folder_generation_api.py tests\integration\test_project_lifecycle_gating_api.py -q
```

---

## 6. Stop Condition

After implementation and validation:

- update `docs/task_board.md`;
- record validation;
- stop;
- do not start `TASK_177` without explicit approval.

---

## 7. Completion Notes

Implemented:

- Adjusted approval-package evidence placement so product specification files are planned directly under `Submitted Material`.
- Kept `.msg` evidence under `E-mail`.
- Kept application/request forms under `Submitted Material`.
- Kept fee evaluation and test-record template-like source documents under `Submitted Material` through the existing supporting attachment path.
- Kept photos under `Photos`.
- Preserved specialized subfolders for non-approval-source evidence such as LTR evidence and corrections.
- Preserved preview-before-copy, no-overwrite, duplicate-target detection, and API response shape.

Validation:

- `py -m pytest tests\unit\test_evidence_placement_service.py tests\integration\test_evidence_placement_api.py -q` passed, 6 passed.
- `py -m pytest tests\integration\test_folder_generation_api.py tests\integration\test_project_lifecycle_gating_api.py -q` passed, 4 passed.
