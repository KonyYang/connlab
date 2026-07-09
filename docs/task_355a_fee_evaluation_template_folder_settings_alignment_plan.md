# TASK_355A Fee Evaluation Template Folder Settings Alignment Plan

> Status: complete after user approval on 2026-07-07.

## Anti-Skip Status

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task on board: `TASK_353A_BASIC_INFORMATION_CONFIRMED_IDENTITY_AUTHORITY`, already complete/accepted
- Why this plan is allowed now: the user reported a release bug in Fee Evaluation draft generation and clarified the desired behavior. This document is a proposed hotfix plan only; it does not start implementation or change product code.

## Goal

Make Fee Evaluation workbook template discovery use the Template folder configured on the Settings page instead of the packaged runtime default `settings.templates_dir`.

The Settings page currently stores Template folder as external resource type:

```text
ExternalResourceType.PROJECT_FOLDER_TEMPLATE = "project_folder_template"
```

After this task, Fee Evaluation export should discover `FDQF-E-176` templates from that configured folder.

## Root Cause Summary

Current behavior has two separate template-folder concepts:

- Settings page `Template folder`: persisted as `ExternalResourceType.PROJECT_FOLDER_TEMPLATE` through `/api/external-resources/project_folder_template`.
- Fee Evaluation draft generation: reads `settings.templates_dir`, which packaged runtime defaults to `%LOCALAPPDATA%\ConnLab\templates`.

The reported release error happens because the required file:

```text
FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls
```

exists in `D:\Template`, but Fee Evaluation export is looking in the packaged default local folder instead.

## Scope

In scope:

- Direct Fee Evaluation draft generation endpoint.
- Required Forms staging path when it generates Fee Form.
- Fee Form template context reader used for Required Forms reuse/staleness checks.
- Backend tests proving the configured Settings Template folder is used.
- Error behavior when Template folder is not configured, inactive, missing, or does not contain a unique `FDQF-E-176` `.xls`.

Out of scope:

- No new Settings UI layout.
- No new resource type unless implementation discovery proves reusing `PROJECT_FOLDER_TEMPLATE` is unsafe.
- No workbook template redesign.
- No Fee default-fill pricing rule changes.
- No `.xls` to `.xlsx` conversion.
- No LAN/server/multi-user permission model.
- No release packaging broad cleanup.

## Design

Introduce a small backend resolver that translates the Settings page Template folder external resource into the Fee Evaluation template path.

Proposed responsibility:

```text
ExternalResourceRepository
  -> Fee Evaluation template folder resolver
  -> discover_fee_evaluation_template(template_folder)
  -> FDQF-E-176 .xls path
```

This keeps template filename matching in the existing `fee_evaluation_template_discovery.py` module and only changes where the folder comes from.

## File-Level Plan

### 1. Add a focused application resolver

Modify or create:

```text
backend/application/fee_evaluation_template_resource.py
```

Proposed interface:

```python
from pathlib import Path
from typing import Protocol

from backend.domain import ExternalResource, ExternalResourceType
from backend.application.fee_evaluation_template_discovery import (
    discover_fee_evaluation_template,
)


class FeeEvaluationTemplateResourceError(ValueError):
    """Raised when the configured Template folder cannot provide a Fee template."""


class FeeEvaluationTemplateResourceStore(Protocol):
    """Repository behavior required to resolve the Fee Evaluation template."""

    def get_by_type(
        self,
        resource_type: ExternalResourceType,
    ) -> ExternalResource | None:
        """Return one configured external resource by type."""


def resolve_fee_evaluation_template_path(
    resource_store: FeeEvaluationTemplateResourceStore,
) -> Path:
    """Return the Fee Evaluation template from the Settings Template folder."""
```

Behavior:

- Load `ExternalResourceType.PROJECT_FOLDER_TEMPLATE`.
- If missing: raise `FeeEvaluationTemplateResourceError("Template folder is not configured.")`.
- If inactive: raise `FeeEvaluationTemplateResourceError("Template folder is inactive.")`.
- Otherwise call `discover_fee_evaluation_template(Path(resource.path))`.
- Preserve existing discovery errors for missing folder, no match, and multiple matches.

### 2. Wire direct Fee Evaluation draft generation

Modify:

```text
backend/api/routes_confirmed_matrix_fee_evaluation_export.py
```

Current behavior:

```python
template_path = discover_fee_evaluation_template(settings.templates_dir)
```

Target behavior:

```python
template_path = resolve_fee_evaluation_template_path(resource_store)
```

Dependency strategy:

- Inject `ExternalResourceRepository` through FastAPI dependency wiring, or add a small dependency provider that returns the resolved `Path`.
- Keep the route thin.
- Keep HTTP error mapping as `404` for template readiness problems unless existing route conventions indicate `400`.

### 3. Wire Required Forms Fee Form generation

Modify:

```text
backend/api/dependencies.py
```

Current affected areas:

- `_FeeFormTemplateContextReader(settings.templates_dir)`
- `_RequiredFormsStagingGenerator.generate(... key == "fee_form")`

Target behavior:

- `_FeeFormTemplateContextReader` should receive an `ExternalResourceRepository` or a resolver object, not `settings.templates_dir`.
- Fee Form staging generation should call the same configured-folder resolver before export.
- Customer Feedback already uses `ExternalResourceType.PROJECT_FOLDER_TEMPLATE`; Fee Form should match that pattern.

### 4. Keep existing discovery rules

No behavioral change in:

```text
backend/application/fee_evaluation_template_discovery.py
```

Rules remain:

- file suffix must be `.xls`
- filename must contain `FDQF-E-176`
- direct child of Template folder
- exactly one match

### 5. Tests

Add/update:

```text
tests/unit/test_fee_evaluation_template_resource.py
tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py
tests/unit/test_project_folder_required_forms_service.py
```

Required assertions:

- Resolver returns `D:\Template\FDQF-E-176...xls` when `PROJECT_FOLDER_TEMPLATE` points to `D:\Template`.
- Missing Settings Template folder resource raises `Template folder is not configured.`
- Inactive resource raises `Template folder is inactive.`
- Direct Fee Evaluation file generation no longer uses `settings.templates_dir`.
- Required Forms Fee Form generation and template context reader use the same Settings Template folder source.
- Existing `discover_fee_evaluation_template` no-match and ambiguous-match tests continue to pass.

## Validation Commands

Focused backend validation:

```powershell
py -m pytest tests\unit\test_fee_evaluation_template_discovery.py tests\unit\test_fee_evaluation_template_resource.py -q
```

Fee export / Required Forms regression:

```powershell
py -m pytest tests\unit\test_confirmed_matrix_fee_evaluation_export_service.py tests\unit\test_project_folder_required_forms_service.py tests\integration\test_project_folder_required_forms_api.py -q
```

If route-level coverage is added or already exists:

```powershell
py -m pytest tests\integration\test_confirmed_matrix_fee_evaluation_export_api.py -q
```

Manual release smoke:

1. In Settings, set `Template folder` to `D:\Template`.
2. Confirm that folder contains exactly one `*FDQF-E-176*.xls`.
3. Open a project Fee Evaluation page.
4. Click `生成草稿费用表`.
5. Expected: workbook downloads/generates without the `Fee Evaluation template was not found...` error.

## Risks

- `PROJECT_FOLDER_TEMPLATE` is shared by project folder creation, Customer Feedback, and Fee Form. This is desired by the user's clarification, but the folder must contain all required official templates.
- If an operator points Template folder to a project-folder structure root instead of the actual official template folder, Fee Evaluation will still fail with the existing actionable message.
- Settings resource validation currently only checks that `PROJECT_FOLDER_TEMPLATE` is a directory. It does not validate that all required templates exist. A later UI/readiness improvement can add per-template status, but this hotfix should stay narrow.

## Approval Gate

Implementation was approved by the user with "请执行".

Completion summary:

- Added a focused Fee Evaluation template resource resolver that reads Settings `Template folder` (`project_folder_template`).
- Updated direct Fee Evaluation file generation to use the Settings Template folder instead of packaged `settings.templates_dir`.
- Updated Required Forms Fee Form template context and staging generation to use the same Settings Template folder source.
- Kept existing `FDQF-E-176` `.xls` unique-match rules unchanged.
- Updated tests for the new resource path and synchronized stale Fee Evaluation export fixtures with the current draft model fields.

Validation:

```powershell
py -m pytest tests\unit\test_fee_evaluation_template_discovery.py tests\unit\test_fee_evaluation_template_resource.py tests\integration\test_confirmed_matrix_fee_file_download_api.py tests\unit\test_required_forms_staging_generator.py tests\unit\test_confirmed_matrix_fee_evaluation_export_service.py tests\unit\test_project_folder_required_forms_service.py tests\integration\test_project_folder_required_forms_api.py -q
```

Result: `77 passed in 2.94s`.
