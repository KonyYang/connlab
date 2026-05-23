# TASK_263 Confirmed Matrix Test Record Preview Backend Plan

> For agentic workers: REQUIRED SUB-SKILL for implementation: use `superpowers:executing-plans` or equivalent task-by-task execution. This document is the executable plan only. Do not implement until the user explicitly approves this plan.

## Protocol Status

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_263_CONFIRMED_MATRIX_TEST_RECORD_PREVIEW_BACKEND`
- Why this task is allowed now: `docs/task_board.md` marks TASK_263 as the planned active task after TASK_261, TASK_262, TASK_262A, and TASK_262B completed.
- Implementation status: planning only.
- Approval gate: implementation remains blocked until the user explicitly approves this plan.

## Goal

Build a backend-only, read-only Test Record preview API from active ConfirmedMatrix authority.

## Architecture

The new consumer service will read the active `ConfirmedMatrixSnapshot` through the existing `ConfirmedMatrixAuthorityRepository.get_active_by_project(project_id)` path. It will map confirmed groups, rows, and sparse cells into a minimal Test Record preview DTO, using `backend.modules.test_plan.matrix_step_sequence_validation.parse_step_tokens()` to expand step tokens. The API route remains thin and returns typed Pydantic DTOs.

## Tech Stack

- Python 3.11+
- FastAPI
- Pydantic v2
- SQLAlchemy-backed repository already present
- pytest + FastAPI `TestClient`

---

## Existing Code Facts

Confirmed authority model:

- `backend/domain/confirmed_matrix_authority_models.py`
- Root aggregate: `ConfirmedMatrixSnapshot`
- Version fields include:
  - `confirmed_matrix_id: str`
  - `project_id: str`
  - `confirmed_revision: int`
  - `is_active_authority: bool`
- Group fields include:
  - `group_order`
  - `group_key`
  - `group_label`
  - `sample_quantity_expression`
- Row fields include:
  - `row_order`
  - `test_item`
  - `source_section`
  - `method`
  - `condition`
  - `requirement`
- Cell fields include:
  - `confirmed_row_id`
  - `confirmed_group_id`
  - `cell_value`

Existing read path:

- `backend/infrastructure/storage/repositories/confirmed_matrix_authority.py`
- `ConfirmedMatrixAuthorityRepository.get_active_by_project(project_id: str) -> ConfirmedMatrixSnapshot | None`
- Repository already orders groups by `group_order` and rows by `row_order`.

Existing confirmed-authority consumer pattern:

- `backend/application/confirmed_matrix_runtime_projection_service.py`
- Defines a narrow `ConfirmedMatrixAuthorityStore` protocol.
- Raises not-found when active ConfirmedMatrix is absent.
- Uses application service + thin API route pattern.

Existing token parser:

- `backend/modules/test_plan/matrix_step_sequence_validation.py`
- `parse_step_tokens(value: str | None) -> tuple[tuple[ParsedStepToken, ...], tuple[str, ...]]`
- Parser preserves raw token and numeric sequence.
- Invalid or empty values return no parsed tokens plus warnings.

Existing route registration pattern:

- `backend/api/dependencies.py`
- `backend/api/main.py`
- `backend/api/routes_confirmed_matrix_runtime_projection.py`

## Scope Decisions

Implement:

- New application service.
- New API route.
- New dependency provider.
- New route registration.
- Unit tests for service behavior.
- Integration tests for API behavior.
- Task board completion update only after implementation and verification.

Do not implement:

- Frontend UI.
- Test Record persistence.
- StepInstance.
- Execution result persistence.
- Evidence/image persistence.
- Report, fee, duration, equipment, approval package, AI, LAN, permissions, or deployment features.
- `.docx`, PDF, Excel, or any generated file output.
- Request-body Matrix payload support.
- SourceMatrix or ProjectMatrixDraft consumption as preview authority.

## DTO Contract

Use application dataclasses internally and Pydantic response DTOs in the API route.

Application dataclasses in `backend/application/confirmed_matrix_test_record_preview_service.py`:

```python
@dataclass(frozen=True, slots=True)
class BuildConfirmedMatrixTestRecordPreviewCommand:
    project_id: str


@dataclass(frozen=True, slots=True)
class ConfirmedMatrixTestRecordPreviewStep:
    sequence: int
    raw_token: str
    test_item: str
    section: str
    method: str
    condition: str
    requirement: str


@dataclass(frozen=True, slots=True)
class ConfirmedMatrixTestRecordPreviewGroup:
    group_key: str
    group_label: str
    sample_quantity_expression: str
    step_count: int
    steps: tuple[ConfirmedMatrixTestRecordPreviewStep, ...]


@dataclass(frozen=True, slots=True)
class ConfirmedMatrixTestRecordPreview:
    project_id: str
    confirmed_matrix_id: str
    preview_status: str
    groups: tuple[ConfirmedMatrixTestRecordPreviewGroup, ...]
```

Pydantic response DTOs in `backend/api/routes_confirmed_matrix_test_record_preview.py`:

```python
class ConfirmedMatrixTestRecordPreviewStepResponse(BaseModel):
    sequence: int
    raw_token: str
    test_item: str
    section: str
    method: str
    condition: str
    requirement: str


class ConfirmedMatrixTestRecordPreviewGroupResponse(BaseModel):
    group_key: str
    group_label: str
    sample_quantity_expression: str
    step_count: int
    steps: list[ConfirmedMatrixTestRecordPreviewStepResponse]


class ConfirmedMatrixTestRecordPreviewResponse(BaseModel):
    project_id: str
    confirmed_matrix_id: str
    preview_status: str
    groups: list[ConfirmedMatrixTestRecordPreviewGroupResponse]
```

Field rules:

- `project_id` is always a string.
- Step field name is `section`, not `source_section`.
- Missing `method`, `condition`, or `requirement` becomes `""`.
- Missing `source_section` becomes `""`.
- `preview_status` is exactly:
  - `"ready"` when at least one group contains at least one step
  - `"empty"` when active ConfirmedMatrix exists but no previewable steps exist

No `parser_warnings` field will be added in TASK_263. Invalid tokens simply do not produce preview steps. This keeps the smoke preview contract narrow.

## API Contract

Route:

```text
GET /api/projects/{project_id}/confirmed-matrix/test-record-preview
```

No request body.

Success example:

```json
{
  "project_id": "P1",
  "confirmed_matrix_id": "cmv-1",
  "preview_status": "ready",
  "groups": [
    {
      "group_key": "g1",
      "group_label": "G1",
      "sample_quantity_expression": "5",
      "step_count": 2,
      "steps": [
        {
          "sequence": 1,
          "raw_token": "1",
          "test_item": "Visual",
          "section": "6.1",
          "method": "",
          "condition": "",
          "requirement": ""
        }
      ]
    }
  ]
}
```

Empty active authority example:

```json
{
  "project_id": "P1",
  "confirmed_matrix_id": "cmv-empty",
  "preview_status": "empty",
  "groups": []
}
```

Error:

- No active ConfirmedMatrix: HTTP `404`, detail `"Active confirmed matrix not found."`
- Invalid confirmed cell lineage: HTTP `422`

## Mapping Algorithm

Service method:

```python
class ConfirmedMatrixTestRecordPreviewService:
    def build_preview(
        self,
        command: BuildConfirmedMatrixTestRecordPreviewCommand,
    ) -> ConfirmedMatrixTestRecordPreview:
        ...
```

Algorithm:

1. Load active snapshot with `confirmed_store.get_active_by_project(command.project_id)`.
2. If no snapshot, raise `ConfirmedMatrixTestRecordPreviewNotFoundError("Active confirmed matrix not found.")`.
3. Build `groups_by_id` from `snapshot.groups`.
4. Build `rows_by_id` from `snapshot.rows`.
5. Build sparse cell lookup by `(confirmed_group_id, confirmed_row_id)`.
6. Iterate groups sorted by `group_order`.
7. For each group, iterate rows sorted by `row_order`.
8. Find the sparse cell for that group/row pair.
9. If no cell or `cell_value.strip()` is blank, skip.
10. Parse `cell_value` using `parse_step_tokens(cell_value)`.
11. For each parsed token in parser output order, append a step:
    - `sequence=token.sequence`
    - `raw_token=token.raw_token`
    - `test_item=row.test_item.strip()`
    - `section=(row.source_section or "").strip()`
    - `method=(row.method or "").strip()`
    - `condition=(row.condition or "").strip()`
    - `requirement=(row.requirement or "").strip()`
12. If a group has at least one step, include it with `step_count=len(steps)`.
13. If no groups have steps, return `preview_status="empty"` and `groups=()`.
14. Otherwise return `preview_status="ready"`.

Invalid lineage rule:

- If a cell references a missing group or row, raise `ConfirmedMatrixTestRecordPreviewError("Confirmed matrix cell lineage is invalid.")`.

Ordering rule:

- Group order first.
- Row order second.
- Parsed token order inside each cell third.
- Do not sort globally by numeric sequence because the smoke-flow plan says preserve confirmed group order, then step token order inside each group.

## Files

Create:

- `backend/application/confirmed_matrix_test_record_preview_service.py`
- `backend/api/routes_confirmed_matrix_test_record_preview.py`
- `tests/unit/test_confirmed_matrix_test_record_preview_service.py`
- `tests/integration/test_confirmed_matrix_test_record_preview_api.py`

Modify:

- `backend/api/dependencies.py`
- `backend/api/main.py`
- `docs/task_board.md` after implementation completion only

No changes expected:

- ConfirmedMatrix repository/schema
- SourceMatrix persistence
- ProjectMatrixDraft persistence
- Matrix import parser
- Frontend files
- Fee/test-record document generation services

## Implementation Tasks

### Task 1: Service Unit Tests

Files:

- Create: `tests/unit/test_confirmed_matrix_test_record_preview_service.py`

Test cases:

- `test_confirmed_matrix_test_record_preview_happy_path_preserves_group_row_token_order`
- `test_confirmed_matrix_test_record_preview_not_found`
- `test_confirmed_matrix_test_record_preview_empty_when_active_authority_has_no_steps`
- `test_confirmed_matrix_test_record_preview_uses_empty_strings_for_missing_fields`
- `test_confirmed_matrix_test_record_preview_rejects_invalid_cell_lineage`

Important assertions:

```python
preview.project_id == "P1"
preview.confirmed_matrix_id == "cmv-1"
preview.preview_status == "ready"
[group.group_key for group in preview.groups] == ["g1", "g2"]
preview.groups[0].sample_quantity_expression == "5"
[step.raw_token for step in preview.groups[0].steps] == ["1", "2(a)", "5"]
preview.groups[0].steps[0].section == "6.1"
preview.groups[0].steps[0].method == ""
```

Run:

```powershell
py -m pytest tests\unit\test_confirmed_matrix_test_record_preview_service.py -q
```

Expected before implementation:

- Import failure or missing class failure.

Expected after implementation:

- All tests pass.

### Task 2: Application Service

Files:

- Create: `backend/application/confirmed_matrix_test_record_preview_service.py`

Implementation requirements:

- Define exceptions:
  - `ConfirmedMatrixTestRecordPreviewError(ValueError)`
  - `ConfirmedMatrixTestRecordPreviewNotFoundError(LookupError)`
- Define `ConfirmedMatrixAuthorityStore` protocol with `get_active_by_project`.
- Define dataclasses listed in the DTO Contract section.
- Implement `ConfirmedMatrixTestRecordPreviewService.build_preview`.
- Import and use `parse_step_tokens`.
- Keep functions small:
  - `_build_group_preview(...)`
  - `_normalize_text(value: str | None) -> str`
  - `_cell_lookup(...)`

Run:

```powershell
py -m pytest tests\unit\test_confirmed_matrix_test_record_preview_service.py -q
```

Expected:

- Unit tests pass.

### Task 3: API Route Tests

Files:

- Create: `tests/integration/test_confirmed_matrix_test_record_preview_api.py`

Fixture strategy:

- Reuse the integration setup style from `tests/integration/test_confirmed_matrix_runtime_projection_api.py`.
- Seed a project.
- Seed SourceMatrix through `SourceMatrixImportPersistenceService`.
- Create selected-only draft through `POST /api/projects/P1/matrix-drafts`.
- Confirm draft through `POST /api/projects/P1/matrix-drafts/{draft_id}/confirm`.
- Call the new preview endpoint.

Test cases:

- `test_confirmed_matrix_test_record_preview_api_happy_path`
  - Assert `200`.
  - Assert `project_id == "P1"`.
  - Assert `confirmed_matrix_id` matches confirmed response.
  - Assert `preview_status == "ready"`.
  - Assert only selected group appears.
  - Assert sample quantity survives.
  - Assert step fields use `section`, not `source_section`.
  - Assert missing fields are `""`.
- `test_confirmed_matrix_test_record_preview_api_returns_404_when_no_active_confirmed`
  - Seed project only.
  - Assert `404`.
- `test_confirmed_matrix_test_record_preview_api_empty_active_authority`
  - If direct DB seeding is simpler than API-based setup, seed a ConfirmedMatrixSnapshot with no cells through `ConfirmedMatrixAuthorityRepository`.
  - Assert `200`, `preview_status == "empty"`, `groups == []`.

Run:

```powershell
py -m pytest tests\integration\test_confirmed_matrix_test_record_preview_api.py -q
```

Expected before route implementation:

- 404 route-not-found or import failure.

Expected after route implementation:

- All tests pass.

### Task 4: API Route And Mapper

Files:

- Create: `backend/api/routes_confirmed_matrix_test_record_preview.py`

Implementation requirements:

- Define response DTO classes in the route module.
- Add mapper functions:
  - `_to_response(preview: ConfirmedMatrixTestRecordPreview) -> ConfirmedMatrixTestRecordPreviewResponse`
  - `_to_group_response(...)`
  - `_to_step_response(...)`
- Route signature:

```python
@router.get(
    "/api/projects/{project_id}/confirmed-matrix/test-record-preview",
    response_model=ConfirmedMatrixTestRecordPreviewResponse,
)
def get_confirmed_matrix_test_record_preview(
    project_id: str,
    service: ConfirmedMatrixTestRecordPreviewService = Depends(
        get_confirmed_matrix_test_record_preview_service
    ),
) -> ConfirmedMatrixTestRecordPreviewResponse:
    ...
```

- Map:
  - `ConfirmedMatrixTestRecordPreviewNotFoundError` -> 404
  - `ConfirmedMatrixTestRecordPreviewError` -> 422

Run:

```powershell
py -m pytest tests\integration\test_confirmed_matrix_test_record_preview_api.py -q
```

Expected:

- Route import may still fail until dependencies/main are wired in Task 5.

### Task 5: Dependency And Main Wiring

Files:

- Modify: `backend/api/dependencies.py`
- Modify: `backend/api/main.py`

Dependency provider:

```python
def get_confirmed_matrix_test_record_preview_service(
    session: Session = Depends(get_session),
) -> ConfirmedMatrixTestRecordPreviewService:
    """Build confirmed-authority Test Record preview service."""
    return ConfirmedMatrixTestRecordPreviewService(
        confirmed_store=ConfirmedMatrixAuthorityRepository(session),
    )
```

Main wiring:

- Import router from `backend.api.routes_confirmed_matrix_test_record_preview`.
- Add `app.include_router(confirmed_matrix_test_record_preview_router)`.

Run:

```powershell
py -m pytest tests\unit\test_confirmed_matrix_test_record_preview_service.py tests\integration\test_confirmed_matrix_test_record_preview_api.py -q
```

Expected:

- New unit and integration tests pass.

### Task 6: Regression Tests

Run:

```powershell
py -m pytest tests\unit\test_confirmed_matrix_runtime_projection_service.py tests\integration\test_confirmed_matrix_runtime_projection_api.py -q
```

Expected:

- Existing confirmed-authority runtime projection behavior remains passing.

Run:

```powershell
py -m pytest tests\unit\test_matrix_import_commit_service.py tests\unit\test_project_matrix_draft_persistence_service.py -q
```

Expected:

- Existing Matrix import/draft persistence tests remain passing.

Run:

```powershell
py -m pytest tests\integration\test_matrix_import_group_selection_commit_api.py tests\integration\test_project_test_plan_preview_api.py -q
```

Expected:

- Existing import commit and preview integration tests remain passing.

### Task 7: Board Update After Implementation Only

Files:

- Modify: `docs/task_board.md`
- Modify: `tasks/TASK_263_CONFIRMED_MATRIX_TEST_RECORD_PREVIEW_BACKEND.md`

Update only after all validation passes:

- TASK_263 status to complete.
- Completion notes with exact deliverables.
- Validation summary with exact commands and pass counts.
- Next recommended task: `TASK_264_MATRIX_TO_TEST_RECORD_SMOKE_UI`, pending explicit user approval.

Do not activate TASK_264 automatically.

## Acceptance Checklist

- [ ] API reads active ConfirmedMatrix from backend persistence.
- [ ] API accepts no request body.
- [ ] No active ConfirmedMatrix returns 404.
- [ ] Active but empty ConfirmedMatrix returns `200`, `preview_status="empty"`, `groups=[]`.
- [ ] Successful preview returns string `project_id`.
- [ ] Successful preview returns string `confirmed_matrix_id`.
- [ ] Preview contains selected confirmed groups only.
- [ ] Sample quantity expression is preserved.
- [ ] Step rows use field `section`.
- [ ] `source_section` is not exposed in API response.
- [ ] Missing `method`, `condition`, and `requirement` return `""`.
- [ ] No fee/report/equipment fields are returned.
- [ ] No StepInstance or execution persistence is introduced.
- [ ] No frontend files are modified.
- [ ] Route remains thin.
- [ ] Unit and integration tests pass.
- [ ] Task board is updated only after implementation completion.

## Risks And Fallbacks

Risk: Existing runtime projection service already maps confirmed authority, so duplicate mapping logic may drift.

Fallback: Keep TASK_263 mapping local and minimal because its output contract differs from runtime projection. Do not change `confirmed_matrix_runtime_projection_service.py`.

Risk: Invalid tokens produce parser warnings that are not returned.

Fallback: This is acceptable for smoke preview because TASK_263 is not a validation UI. Invalid tokens produce no step rows; if all tokens are invalid, return `empty`.

Risk: Direct DB seeding for empty active authority could be verbose in integration tests.

Fallback: Use `ConfirmedMatrixAuthorityRepository.create_snapshot()` in the integration fixture with a valid version and empty groups/rows/cells. This tests the API empty-response contract without creating future behavior.

Risk: Confirmed cells are ordered by `confirmed_cell_id` in repository.

Fallback: Service ignores cell order for preview ordering by building a lookup and iterating group order then row order. Parsed token order inside each cell is preserved.

## Self-Review

- Spec coverage: The plan covers active ConfirmedMatrix-only consumption, selected group propagation, sample quantity propagation, deterministic ordering, empty-result semantics, DTO naming, 404 behavior, and scope exclusions.
- Placeholder scan: No implementation placeholder or later-fill item remains.
- Type consistency: Internal dataclasses and route DTO names consistently use `section`, string `project_id`, string `confirmed_matrix_id`, and empty-string missing fields.
- Scope control: No frontend, generated document, fee, equipment, StepInstance, or execution persistence work is included.
