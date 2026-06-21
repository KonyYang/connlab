# TASK_330D Project Folder Update Performance And Collect DTO Hotfix Plan

## Governance

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task ID: TASK_330D_PROJECT_FOLDER_UPDATE_PERFORMANCE_AND_COLLECT_DTO_HOTFIX.
- Why this task is allowed now: TASK_330C is complete, and browser/API timing review found independent Project Folder update button defects that are not Basic Information output-consumption scope.
- Stop rule: implement only TASK_330D after this plan is reviewed and explicitly approved. Do not reopen TASK_330C semantics or proceed to later execution/reporting scope.

## Task Understanding

Goal:

- Fix the `request-material/collect` 500 caused by incorrect API DTO conversion.
- Avoid unnecessary Fee Form Excel COM generation when a safe current Fee Form artifact already exists.

Inputs:

- Project ID.
- Post-copy request-material preview context.
- Required forms preview context.
- Current ProjectOutputRecord status for Fee Form output.
- Active Matrix/Fee/pricing source context.
- Expected Required forms targets.

Outputs:

- Typed collect API response.
- Required forms generation result.
- Official project-folder Fee Form placement from either a reused safe artifact or the existing Excel export path.

Modules:

- `backend/api/routes_project_request_material.py`
- `backend/application/project_request_material_collection_types.py`
- `backend/application/project_request_material_collection_service.py`
- `backend/application/project_folder_required_forms_service.py`
- `backend/api/dependencies.py`
- request-material and required-forms tests.

Not allowed:

- No Basic Information output-consumption changes.
- No Office field mapping changes.
- No broad Excel COM rewrite.
- No frontend workflow redesign.

## Design

### 1. Correct collect DTO conversion

Preferred implementation:

- Extend `RequestMaterialCollectResult` with:
  - `local_workspace_path: Path | None`
  - `source_book_path: Path | None`
  - `official_project_folder_path: Path | None`
- Populate those values from the `after` preview inside `_collect_result_from_preview(...)`.
- Change `_collect_response(...)` to serialize `RequestMaterialCollectResult` directly instead of passing it to `_preview_response(...)`.

Reason:

- Returning null placeholders would hide useful folder context from the frontend.
- The service already has the post-copy preview, so the response can preserve real paths without adding a new lookup.

### 2. Add a narrow reusable Fee Form artifact reader

Add an internal application-layer dependency to Required forms generation:

```python
class ReusableFeeFormArtifactReader(Protocol):
    def find_current_artifact(
        self,
        *,
        project_id: str,
        source_context_signature: str,
        final_target_path: Path,
    ) -> Path | None:
        ...
```

Allowed source:

- Existing current `ProjectOutputKind.FEE_EVALUATION` output record.

Reuse checks:

- status is current;
- source is ConnLab generated, not manual;
- source context exactly matches current Matrix/Fee/pricing context;
- output path exists;
- file extension is `.xls`;
- stored sha256 exists and matches disk content;
- if the output path is the final official target and preview already marks it current, generation keeps the existing skip path;
- if the output path is outside the final official target, Required forms may copy it through the existing file gateway.

Fallback:

- If any check fails, use the existing `_RequiredFormsStagingGenerator.generate(..., key="fee_form")` path, which invokes Excel COM as today.

### 3. Integrate reuse without changing placement safety

In `ProjectFolderRequiredFormsService.generate(...)`:

- For `fee_form` items with action `generate` or `update`, check the reusable artifact reader before calling the generator.
- If a reusable source is found, use it as `source` for existing `create_new(...)` / `update_managed(...)` placement.
- If not found, call the generator exactly as before.
- Preserve existing target fingerprint checks and output registration.
- Add timing labels such as `fee_form.reuse_lookup` and keep `fee_form.generate` only when generation actually runs.

## File-Level Changes

Expected files:

- `backend/api/routes_project_request_material.py`
- `backend/application/project_request_material_collection_types.py`
- `backend/application/project_request_material_collection_service.py`
- `backend/application/project_folder_required_forms_service.py`
- `backend/api/dependencies.py`
- `tests/unit/test_project_request_material_collection_service.py`
- `tests/integration/test_project_request_material_collection_api.py`
- `tests/unit/test_project_folder_required_forms_service.py`
- `tests/integration/test_project_folder_required_forms_api.py`

## Tests

Write failing tests first:

```powershell
py -m pytest tests/unit/test_project_request_material_collection_service.py -q
py -m pytest tests/unit/test_project_folder_required_forms_service.py -q
```

Required test cases:

- collect result carries post-copy workspace paths;
- collect API returns 200 and serializes workspace plus collection fields;
- safe generated Fee Form artifact is reused;
- Fee Form generator is not called on a safe reuse path;
- Excel generation still runs when artifact is missing, manual, stale, hash-mismatched, wrong extension, or wrong context;
- existing managed target conflict behavior remains unchanged.

Final validation:

```powershell
py -m pytest tests/unit/test_project_request_material_collection_service.py -q
py -m pytest tests/integration/test_project_request_material_collection_api.py -q
py -m pytest tests/unit/test_project_folder_required_forms_service.py -q
py -m pytest tests/integration/test_project_folder_required_forms_api.py -q
```

## Risks

- Reusing a stale Fee Form would be worse than slow generation, so reuse checks must be strict.
- If the only current Fee Form record points to the already-current final official target, the correct behavior is skip, not copy.
- If no safe generated artifact exists, this task will not reduce cold Excel COM generation time.
- Existing unrelated worktree changes must not be reverted or overwritten.

## Review Checklist

- Layering remains API -> application -> infrastructure.
- UI does not touch files or Office.
- No Basic Information consumption behavior is changed.
- No broad Office gateway rewrite is introduced.
- Tests cover both reuse and fallback.

## Stop Point

After approval and implementation, stop at TASK_330D. Do not start any next task automatically.
