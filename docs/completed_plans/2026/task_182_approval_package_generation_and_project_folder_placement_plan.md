# TASK_182 Plan - Approval Package Generation And Project Folder Placement

## 1. Current Phase And Gate

- Current phase: `Phase 11 - Project planning data foundation before downstream document automation`.
- Current active task before creation: `none; TASK_181 complete`.
- This plan is proposal-only. Implementation must wait for explicit user approval: `批准执行 TASK_182`.

## 2. Goal

Create a backend workflow that assembles the approval package into the Project folder for supervisor review.

This should connect the outputs from prior tasks instead of creating another document-generation path.

## 3. Design Direction

Use a preview-then-execute model:

- Preview builds the target placement plan and reports blockers.
- Execute reuses the same planning result and copies files only when the plan is safe.

The service should reuse existing evidence placement classification behavior from `TASK_176` where it fits, while adding explicit required approval-package inputs for completed application form, generated test record, and fee evaluation output.

## 4. Data Flow

1. API receives Project ID, Project folder path, required output files, optional evidence files, and overwrite flag.
2. Application service validates Project exists.
3. Application service validates Project folder exists and expected subfolders are present or can be addressed.
4. Service classifies source files into approval package destinations.
5. Preview returns target paths, warnings, and blockers.
6. Execute copies files if no blockers exist and `overwrite=false` has no conflicts.
7. API returns copied/skipped item statuses.

## 5. Proposed Data Structures

Command:

```python
@dataclass(frozen=True, slots=True)
class ApprovalPackageCommand:
    project_id: str
    project_folder_path: Path
    completed_application_form_path: Path
    test_record_output_path: Path
    fee_evaluation_output_path: Path | None = None
    evidence_source_paths: tuple[Path, ...] = ()
    overwrite: bool = False
```

Item:

```python
@dataclass(frozen=True, slots=True)
class ApprovalPackageItem:
    source_path: Path
    target_relative_path: Path
    target_path: Path
    classification: str
    status: str
    warnings: tuple[str, ...] = ()
```

Result:

```python
@dataclass(frozen=True, slots=True)
class ApprovalPackageResult:
    project_id: str
    project_folder_path: Path
    mode: str
    items: tuple[ApprovalPackageItem, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
```

## 6. API Contract

Endpoints:

```text
POST /api/projects/{project_id}/approval-package/preview
POST /api/projects/{project_id}/approval-package/execute
```

The preview and execute request body should be the same. The endpoint path determines whether files are copied.

## 7. File-Level Changes

Add:

- `backend/application/approval_package_service.py`
- `backend/api/routes_approval_package.py`
- `tests/unit/test_approval_package_service.py`
- `tests/integration/test_approval_package_api.py`

Modify:

- `backend/api/dependencies.py`
- `backend/api/main.py`
- `docs/task_board.md`

## 8. Implementation Boundaries

Allowed:

- Validate paths.
- Build placement plans.
- Copy files into the Project folder during execute.
- Reuse existing evidence classification rules.
- Return warnings/blockers.

Forbidden:

- Do not modify Office file contents.
- Do not generate new Office documents.
- Do not calculate fees.
- Do not mutate New Project intake records.
- Do not mutate ProjectTestPlanDraft records.
- Do not add frontend UI.
- Do not upload or write outside the operator-provided Project folder.

## 9. Risk And Mitigation

Risk: Inputs may already point inside the Project folder.

Mitigation: Preview should detect same source/target paths and mark them as `already_in_place` instead of copying over themselves.

Risk: File names can collide.

Mitigation: Existing targets block by default. A future task can add conflict naming if operators need it.

Risk: Evidence classification and approval package required-file logic can overlap.

Mitigation: Required package files should be added explicitly first, then optional evidence paths should be classified through the existing placement rules.

## 10. Validation

Targeted validation:

```powershell
py -m pytest tests\unit\test_approval_package_service.py tests\integration\test_approval_package_api.py -q
```

Regression validation:

```powershell
py -m pytest tests\unit\test_evidence_placement_service.py tests\integration\test_evidence_placement_api.py -q
py -m pytest tests\unit\test_test_record_fee_document_generation_service.py tests\integration\test_test_record_fee_document_generation_api.py -q
```

Board guard validation:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

## 11. Review Checklist Result For Plan Stage

- Architecture boundary: application service coordinates, API remains thin, file copying stays in application-level workflow already used by existing evidence placement service.
- Scope: approval package placement only.
- Office boundary: no Office content writes.
- Frontend: no UI change.
- Stop condition: wait for explicit implementation approval.
