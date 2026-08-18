# TASK_338 Project Lifecycle Write Guard Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add focused backend write guards so stopped and closed projects reject selected high-risk writes while active projects and approved readonly previews keep current behavior.

**Architecture:** Introduce a small lifecycle readonly guard primitive in the application layer that reads TASK_337A `Project.lifecycle_state` / `closure_type` from the existing project repository. Inject that guard into a first slice of write services at the application boundary before downstream repository, file, Office, public-drive, or output mutations happen. API routes map the shared guard error to a stable `409 project_lifecycle_readonly` response.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.x, SQLite, pytest.

## Global Constraints

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current approved lane: `write-guard-integration` / `TASK_338_PROJECT_LIFECYCLE_WRITE_GUARD_INTEGRATION`.
- Current role: Developer planning first.
- This document is planning only; product code changes require explicit user approval of this plan.
- May create only `docs/task_338_project_lifecycle_write_guard_integration_plan.md` during this planning turn.
- Do not change frontend UI, styling, Workbench shell, Projects registry UI, or frontend readonly model.
- Do not implement StepInstance, Report generation, AI, permissions, LAN/server, or multi-user scope.
- Do not replace public-drive LTR Excel authority.
- Do not block non-mutating preview/read endpoints unless an approved implementation step proves they mutate state.
- Do not edit Office gateway internals except explicit test fakes or approved guard insertion points.
- Use TASK_337A lifecycle overlay as authority: `active` allows existing business write rules, `stopped` and `closed` are readonly except lifecycle Resume/Close actions.

---

## 1. Current Task Understanding

### Objective

Implement a first backend slice of lifecycle write guards after TASK_337A lifecycle/API shape and TASK_337B guard inventory are complete.

### Inputs

- `Project.lifecycle_state` and `Project.closure_type` from TASK_337A.
- Existing project repositories and dependency wiring.
- TASK_337B route/service inventory.
- Existing service commands for selected write paths.
- Existing preview/read endpoints for the same feature areas.

### Outputs

- Shared application guard primitive for write operations.
- Stable `409` error shape for stopped/closed project writes:

```json
{
  "code": "project_lifecycle_readonly",
  "project_id": "P1",
  "lifecycle_state": "stopped",
  "closure_type": null,
  "message": "This project is stopped. Resume it before making changes.",
  "allowed_actions": ["resume", "close"]
}
```

- Guarded first-slice write paths:
  - Basic Information draft save and confirm
  - Matrix Editor session draft save, draft discard, and confirm
  - Fee Evaluation pricing draft save and discard
  - Project Folder Required Forms generate
  - LTR workbook Basic Information sync commit
- Tests proving stopped/closed writes are rejected before downstream mutation.
- Tests proving active-project behavior remains available.
- Tests proving selected readonly preview/read endpoints remain available.

### Inputs Not Available In This Worktree

The current worktree is missing these required input files:

- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`
- `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`

Mitigation for this plan:

- Use `docs/task_board.md`, `tasks/TASK_338_PROJECT_LIFECYCLE_WRITE_GUARD_INTEGRATION.md`, `tasks/TASK_337A_PROJECT_LIFECYCLE_BACKEND_API_SHAPE.md`, `docs/task_337a_project_lifecycle_backend_api_shape_plan.md`, `tasks/TASK_337B_PROJECT_LIFECYCLE_GUARD_INVENTORY_AND_TEST_MATRIX.md`, and `docs/task_337b_project_lifecycle_guard_inventory_and_test_matrix.md` as the available source of truth.
- Do not recreate missing governance or contract files in this lane.
- Require Reviewer/Integrator to confirm the missing-input packaging state before merge if those files are expected to exist in the final branch.

### Explicit Non-Goals

- No frontend readonly model.
- No Workbench shell implementation.
- No broad endpoint-by-endpoint guard expansion beyond the first slice listed in this plan.
- No changes to TASK_337A lifecycle API shape except using its persisted lifecycle fields.
- No new database schema.
- No Office gateway internals or public-drive authority replacement.

## 2. Design Decisions

### 2.1 New Guard Primitive

Create `backend/application/project_lifecycle_write_guard.py`.

The helper must be application-layer only:

```python
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from backend.domain import Project, ProjectClosureType, ProjectLifecycleState


class LifecycleWriteOperation(StrEnum):
    BASIC_INFORMATION_DRAFT = "basic_information_draft"
    BASIC_INFORMATION_CONFIRM = "basic_information_confirm"
    MATRIX_EDITOR_DRAFT_SAVE = "matrix_editor_draft_save"
    MATRIX_EDITOR_DRAFT_DISCARD = "matrix_editor_draft_discard"
    MATRIX_EDITOR_CONFIRM = "matrix_editor_confirm"
    FEE_PRICING_DRAFT_SAVE = "fee_pricing_draft_save"
    FEE_PRICING_DRAFT_DISCARD = "fee_pricing_draft_discard"
    REQUIRED_FORMS_GENERATE = "required_forms_generate"
    LTR_WORKBOOK_BASIC_INFORMATION_SYNC_COMMIT = (
        "ltr_workbook_basic_information_sync_commit"
    )


class ProjectLifecycleReadonlyError(ValueError):
    def __init__(
        self,
        *,
        project_id: str,
        lifecycle_state: ProjectLifecycleState,
        closure_type: ProjectClosureType | None,
        message: str,
        allowed_actions: tuple[str, ...],
    ) -> None:
        super().__init__(message)
        self.project_id = project_id
        self.lifecycle_state = lifecycle_state
        self.closure_type = closure_type
        self.message = message
        self.allowed_actions = allowed_actions


class ProjectLifecycleWriteGuardNotFoundError(LookupError):
    """Raised when a write guard cannot load the project."""


@dataclass(frozen=True, slots=True)
class ProjectLifecycleWriteGuardResult:
    project_id: str
    lifecycle_state: ProjectLifecycleState
    closure_type: ProjectClosureType | None
    readonly: bool
    allowed_actions: tuple[str, ...]
    message: str | None = None


class ProjectStore(Protocol):
    def get(self, project_id: str) -> Project | None:
        """Return a project by ID."""


class ProjectLifecycleWriteGuard:
    def __init__(self, project_store: ProjectStore) -> None:
        self._projects = project_store

    def check_write_allowed(
        self,
        project_id: str,
        operation: LifecycleWriteOperation,
    ) -> ProjectLifecycleWriteGuardResult:
        """Return readonly state for one write operation."""

    def require_write_allowed(
        self,
        project_id: str,
        operation: LifecycleWriteOperation,
    ) -> None:
        """Raise ProjectLifecycleReadonlyError when the project is readonly."""
```

Decision:

- Use TASK_337A overlay fields, not legacy `Project.status`.
- Keep existing `backend/application/project_lifecycle_service.py` unchanged for old status-based LTR/folder/evidence gates. Do not expand it because it still encodes `cancelled` as closed-like legacy status.
- Guard must run before service validation that can perform expensive downstream reads only when doing so is not needed to decide readonly. In selected write services, call it at the top after the command `project_id` is available.

### 2.2 Readonly Messages And Allowed Actions

Guard behavior:

| Lifecycle state | Error message | Allowed actions |
|---|---|---|
| `active` | no error | operation continues |
| `stopped` | `This project is stopped. Resume it before making changes.` | `("resume", "close")` |
| `closed`, `completed` | `This project is closed as completed and is readonly.` | `()` |
| `closed`, `administrative` | `This project is closed administratively and is readonly.` | `()` |
| `closed`, unknown closure type | `This project is closed and is readonly.` | `()` |

HTTP behavior:

- API status: `409 Conflict`
- API error code: `project_lifecycle_readonly`
- Detail fields: `code`, `project_id`, `lifecycle_state`, `closure_type`, `message`, `allowed_actions`

### 2.3 First-Slice Write Paths

First slice is intentionally representative, not exhaustive:

| Area | Write methods to guard | Why selected |
|---|---|---|
| Basic Information | `ProjectBasicInformationService.save_draft`, `confirm` | direct project authority writes |
| Matrix | `MatrixEditorSessionService.save_editor_draft`, `discard_editor_draft`, `confirm_session` | Matrix authority/draft mutation and Fee rebase side effects |
| Fee | `FeeEvaluationPricingDraftPersistenceService.save`, `discard` | Fee authority-adjacent draft mutation |
| Project Folder outputs | `ProjectFolderRequiredFormsService.generate` | file, Office, and output-record writes |
| LTR workbook | `LtrWorkbookBasicInformationSyncService.commit` | external workbook authority write |

Readonly endpoints to explicitly preserve:

| Area | Readonly method/route |
|---|---|
| Basic Information | `ProjectBasicInformationService.get` / `GET /basic-information` |
| Matrix | `MatrixEditorSessionService.get_session` / `GET /matrix-editor/session` |
| Fee | pricing draft `GET` route |
| Required Forms | `ProjectFolderRequiredFormsService.preview` / `GET /project-folder/required-forms/preview` |
| LTR workbook | `preview` and `open_readonly_at_ltr` routes |

## 3. File Structure

### Create

- `backend/application/project_lifecycle_write_guard.py`
  - Shared guard primitive and readonly error.

- `tests/unit/test_project_lifecycle_write_guard.py`
  - Pure guard behavior tests.

- `tests/integration/test_project_lifecycle_write_guard_api.py`
  - API-level stopped/closed/active/readonly-preview coverage for first slice.

### Modify

- `backend/application/project_basic_information_service.py`
  - Inject optional `lifecycle_write_guard`.
  - Call guard in `save_draft` and `confirm`.

- `backend/application/matrix_editor_session_service.py`
  - Inject optional `lifecycle_write_guard`.
  - Call guard in `save_editor_draft`, `discard_editor_draft`, and `confirm_session`.

- `backend/application/fee_evaluation_pricing_draft_persistence_service.py`
  - Inject optional `lifecycle_write_guard`.
  - Call guard in `save` and `discard`.

- `backend/application/project_folder_required_forms_service.py`
  - Inject optional `lifecycle_write_guard`.
  - Call guard at the start of `generate` before preview validation, staging generation, final placement, or output registration.

- `backend/application/ltr_workbook_basic_information_sync_service.py`
  - Inject optional `lifecycle_write_guard`.
  - Call guard at the start of `commit` before opening workbook write transaction.
  - Do not guard `preview` or `open_readonly_at_ltr`.

- `backend/api/dependencies.py`
  - Add `get_project_lifecycle_write_guard`.
  - Pass guard into selected services.

- `backend/api/routes_project_basic_information.py`
  - Map `ProjectLifecycleReadonlyError` to structured 409.

- `backend/api/routes_matrix_editor_session.py`
  - Map `ProjectLifecycleReadonlyError` to structured 409.

- `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`
  - Map `ProjectLifecycleReadonlyError` to structured 409.

- `backend/api/routes_project_folder_required_forms.py`
  - Map `ProjectLifecycleReadonlyError` to structured 409.

- `backend/api/routes_ltr_workbook_basic_information_sync.py`
  - Map `ProjectLifecycleReadonlyError` to structured 409 for commit only.

- Existing first-slice tests as needed:
  - `tests/integration/test_project_basic_information_api.py`
  - `tests/integration/test_matrix_editor_session_api.py`
  - `tests/integration/test_fee_evaluation_pricing_draft_api.py`
  - `tests/integration/test_project_folder_required_forms_api.py`
  - `tests/integration/test_ltr_workbook_basic_information_sync_api.py`

## 4. Implementation Tasks

### Task 1: Shared Lifecycle Write Guard

**Files:**

- Create: `backend/application/project_lifecycle_write_guard.py`
- Create: `tests/unit/test_project_lifecycle_write_guard.py`

**Interfaces:**

- Produces:
  - `LifecycleWriteOperation`
  - `ProjectLifecycleReadonlyError`
  - `ProjectLifecycleWriteGuardNotFoundError`
  - `ProjectLifecycleWriteGuardResult`
  - `ProjectLifecycleWriteGuard.check_write_allowed(...)`
  - `ProjectLifecycleWriteGuard.require_write_allowed(...)`

- [ ] **Step 1: Write failing guard tests**

Create `tests/unit/test_project_lifecycle_write_guard.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pytest

from backend.application.project_lifecycle_write_guard import (
    LifecycleWriteOperation,
    ProjectLifecycleReadonlyError,
    ProjectLifecycleWriteGuard,
    ProjectLifecycleWriteGuardNotFoundError,
)
from backend.domain import (
    Project,
    ProjectClosureType,
    ProjectLifecycleState,
    ProjectStatus,
)


def test_active_project_write_is_allowed() -> None:
    guard = ProjectLifecycleWriteGuard(_ProjectStore(_project()))

    guard.require_write_allowed("P1", LifecycleWriteOperation.BASIC_INFORMATION_DRAFT)


def test_stopped_project_write_is_blocked_with_resume_and_close_actions() -> None:
    guard = ProjectLifecycleWriteGuard(
        _ProjectStore(_project(lifecycle_state=ProjectLifecycleState.STOPPED))
    )

    with pytest.raises(ProjectLifecycleReadonlyError) as exc_info:
        guard.require_write_allowed(
            "P1",
            LifecycleWriteOperation.BASIC_INFORMATION_DRAFT,
        )

    exc = exc_info.value
    assert exc.project_id == "P1"
    assert exc.lifecycle_state is ProjectLifecycleState.STOPPED
    assert exc.closure_type is None
    assert exc.allowed_actions == ("resume", "close")
    assert exc.message == "This project is stopped. Resume it before making changes."


def test_closed_completed_project_write_is_blocked_as_readonly_archive() -> None:
    guard = ProjectLifecycleWriteGuard(
        _ProjectStore(
            _project(
                lifecycle_state=ProjectLifecycleState.CLOSED,
                closure_type=ProjectClosureType.COMPLETED,
            )
        )
    )

    with pytest.raises(ProjectLifecycleReadonlyError) as exc_info:
        guard.require_write_allowed(
            "P1",
            LifecycleWriteOperation.REQUIRED_FORMS_GENERATE,
        )

    assert exc_info.value.lifecycle_state is ProjectLifecycleState.CLOSED
    assert exc_info.value.closure_type is ProjectClosureType.COMPLETED
    assert exc_info.value.allowed_actions == ()
    assert (
        exc_info.value.message
        == "This project is closed as completed and is readonly."
    )


def test_closed_administrative_project_write_is_blocked_as_readonly_archive() -> None:
    guard = ProjectLifecycleWriteGuard(
        _ProjectStore(
            _project(
                lifecycle_state=ProjectLifecycleState.CLOSED,
                closure_type=ProjectClosureType.ADMINISTRATIVE,
            )
        )
    )

    with pytest.raises(ProjectLifecycleReadonlyError) as exc_info:
        guard.require_write_allowed(
            "P1",
            LifecycleWriteOperation.LTR_WORKBOOK_BASIC_INFORMATION_SYNC_COMMIT,
        )

    assert exc_info.value.closure_type is ProjectClosureType.ADMINISTRATIVE
    assert exc_info.value.message == (
        "This project is closed administratively and is readonly."
    )


def test_missing_project_raises_not_found() -> None:
    guard = ProjectLifecycleWriteGuard(_ProjectStore(None))

    with pytest.raises(ProjectLifecycleWriteGuardNotFoundError):
        guard.require_write_allowed("P1", LifecycleWriteOperation.MATRIX_EDITOR_CONFIRM)


@dataclass
class _ProjectStore:
    project: Project | None

    def get(self, project_id: str) -> Project | None:
        if self.project is None or self.project.project_id != project_id:
            return None
        return self.project


def _project(
    *,
    lifecycle_state: ProjectLifecycleState = ProjectLifecycleState.ACTIVE,
    closure_type: ProjectClosureType | None = None,
) -> Project:
    return Project(
        project_id="P1",
        project_no="DL-2026-06-001",
        product_name="Connector",
        requestor="Alice",
        status=ProjectStatus.LTR_REGISTERED,
        created_on=date(2026, 6, 27),
        lifecycle_state=lifecycle_state,
        closure_type=closure_type,
    )
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
py -m pytest tests\unit\test_project_lifecycle_write_guard.py -q
```

Expected:

- FAIL with `ModuleNotFoundError: No module named 'backend.application.project_lifecycle_write_guard'`.

- [ ] **Step 3: Implement guard primitive**

Create `backend/application/project_lifecycle_write_guard.py` with the interfaces in section 2.1 and message rules in section 2.2.

Implementation notes:

- `check_write_allowed` returns `readonly=False` for active.
- `require_write_allowed` raises `ProjectLifecycleReadonlyError` only when `readonly=True`.
- Do not import FastAPI or infrastructure modules.

- [ ] **Step 4: Run tests to verify GREEN**

Run:

```powershell
py -m pytest tests\unit\test_project_lifecycle_write_guard.py -q
```

Expected:

- PASS.

### Task 2: API Error Mapper And Dependency Wiring

**Files:**

- Modify: `backend/api/dependencies.py`
- Modify: selected route modules listed in section 3
- Test: route integration tests listed in later tasks

**Interfaces:**

- Consumes:
  - `ProjectLifecycleReadonlyError`
  - `ProjectLifecycleWriteGuard`
- Produces:
  - `get_project_lifecycle_write_guard(session)`
  - common route helper or duplicated minimal mapping for first slice

- [ ] **Step 1: Add dependency factory**

In `backend/api/dependencies.py`:

```python
from backend.application.project_lifecycle_write_guard import ProjectLifecycleWriteGuard


def get_project_lifecycle_write_guard(
    session: Session = Depends(get_session),
) -> ProjectLifecycleWriteGuard:
    """Build a lifecycle write guard using Project lifecycle overlay state."""
    return ProjectLifecycleWriteGuard(ProjectRepository(session))
```

- [ ] **Step 2: Add route error mapping helper**

Preferred local helpers in each touched route module, or small shared helpers if repeated imports become noisy:

```python
def _lifecycle_readonly_conflict(exc: ProjectLifecycleReadonlyError) -> HTTPException:
    return HTTPException(
        status_code=409,
        detail={
            "code": "project_lifecycle_readonly",
            "project_id": exc.project_id,
            "lifecycle_state": exc.lifecycle_state.value,
            "closure_type": exc.closure_type.value if exc.closure_type else None,
            "message": exc.message,
            "allowed_actions": list(exc.allowed_actions),
        },
    )


def _lifecycle_guard_not_found(
    exc: ProjectLifecycleWriteGuardNotFoundError,
) -> HTTPException:
    return HTTPException(status_code=404, detail=str(exc))
```

If shared, create `backend/api/lifecycle_errors.py` with that helper and list it in the implementation changed files before coding.

- [ ] **Step 3: Add missing-project API test coverage**

At least one first-slice API test must prove guard not-found errors map to 404 instead of 500. Use Basic Information because its write route has the lightest setup:

```python
def test_missing_project_guard_error_maps_to_404(client):
    response = client.put(
        "/api/projects/NOPE/basic-information/draft",
        json={"values": {"project_no": "DL-2026-06-001"}},
    )

    assert response.status_code == 404
    assert "Project not found" in response.json()["detail"]
```

Implementation requirement:

- Route handlers that catch `ProjectLifecycleReadonlyError` must also catch `ProjectLifecycleWriteGuardNotFoundError` and map it to `404`.
- Do not let guard not-found bypass existing service/route 404 behavior as an unhandled `500`.

- [ ] **Step 4: Wire selected services**

Pass `lifecycle_write_guard=get_project_lifecycle_write_guard(session)` into:

- `ProjectBasicInformationService(...)`
- `MatrixEditorSessionService(...)`
- `FeeEvaluationPricingDraftPersistenceService(...)`
- `ProjectFolderRequiredFormsService(...)`
- `LtrWorkbookBasicInformationSyncService(...)`

Do not wire the guard into read-only preview services or unrelated services in this task.

### Task 3: Basic Information Guard

**Files:**

- Modify: `backend/application/project_basic_information_service.py`
- Modify: `backend/api/routes_project_basic_information.py`
- Test: `tests/integration/test_project_basic_information_api.py`

**Interfaces:**

- Consumes:
  - `lifecycle_write_guard.require_write_allowed(project_id, operation)`
- Guards:
  - `SaveProjectBasicInformationDraftCommand`
  - `ConfirmProjectBasicInformationCommand`
- Preserves:
  - `GET /api/projects/{project_id}/basic-information`

- [ ] **Step 1: Add failing API tests**

Append tests to `tests/integration/test_project_basic_information_api.py`:

```python
def test_stopped_project_rejects_basic_information_draft_save(client):
    project_id = _create_project_with_lifecycle(client, lifecycle_state="stopped")

    response = client.put(
        f"/api/projects/{project_id}/basic-information/draft",
        json={"values": {"project_no": "DL-2026-06-001"}},
    )

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "project_lifecycle_readonly"
    assert detail["project_id"] == project_id
    assert detail["lifecycle_state"] == "stopped"
    assert detail["allowed_actions"] == ["resume", "close"]
```

Add equivalent closed completed or closed administrative confirm test:

```python
def test_closed_project_rejects_basic_information_confirm(client):
    project_id = _create_project_with_lifecycle(
        client,
        lifecycle_state="closed",
        closure_type="completed",
    )

    response = client.post(
        f"/api/projects/{project_id}/basic-information/confirm",
        json={"values": _valid_basic_information_values()},
    )

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "project_lifecycle_readonly"
    assert detail["closure_type"] == "completed"
    assert detail["allowed_actions"] == []
```

Add no-mutation assertions for Basic Information draft and confirm:

```python
def test_stopped_project_basic_information_draft_save_does_not_create_record(
    client,
    session_factory,
):
    project_id = _create_project_with_lifecycle(client, lifecycle_state="stopped")
    before_count = _basic_information_record_count(session_factory, project_id)

    response = client.put(
        f"/api/projects/{project_id}/basic-information/draft",
        json={"values": {"project_no": "DL-2026-06-001"}},
    )

    after_count = _basic_information_record_count(session_factory, project_id)
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "project_lifecycle_readonly"
    assert after_count == before_count


def test_closed_project_basic_information_confirm_does_not_create_record(
    client,
    session_factory,
):
    project_id = _create_project_with_lifecycle(
        client,
        lifecycle_state="closed",
        closure_type="completed",
    )
    before_count = _basic_information_record_count(session_factory, project_id)

    response = client.post(
        f"/api/projects/{project_id}/basic-information/confirm",
        json={"values": _valid_basic_information_values()},
    )

    after_count = _basic_information_record_count(session_factory, project_id)
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "project_lifecycle_readonly"
    assert after_count == before_count
```

Helper requirement:

```python
def _basic_information_record_count(session_factory, project_id: str) -> int:
    with session_factory() as session:
        return len(ProjectBasicInformationRepository(session).list_by_project(project_id))
```

If `ProjectBasicInformationRepository` does not expose `list_by_project`, use a direct SQLAlchemy `select(func.count())` against `ProjectBasicInformationRecordModel` inside the test. The point is explicit proof that the guard runs before draft/confirmed record creation.

Also assert read remains available:

```python
def test_stopped_project_can_read_basic_information(client):
    project_id = _create_project_with_lifecycle(client, lifecycle_state="stopped")

    response = client.get(f"/api/projects/{project_id}/basic-information")

    assert response.status_code == 200
```

Use existing project/API fixtures in the file. If no helper exists, create a local helper that inserts a project through existing repository/session setup and sets `lifecycle_state` directly.

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
py -m pytest tests\integration\test_project_basic_information_api.py -q
```

Expected:

- New stopped/closed write tests fail because writes are still accepted or return old errors.
- Read test passes or fails only if setup helper is wrong.

- [ ] **Step 3: Inject and call guard**

In `ProjectBasicInformationService.__init__`, add optional dependency:

```python
lifecycle_write_guard: ProjectLifecycleWriteGuard | None = None,
```

Store it as `self._lifecycle_write_guard`.

At the top of `save_draft`:

```python
if self._lifecycle_write_guard is not None:
    self._lifecycle_write_guard.require_write_allowed(
        command.project_id,
        LifecycleWriteOperation.BASIC_INFORMATION_DRAFT,
    )
```

At the top of `confirm`:

```python
if self._lifecycle_write_guard is not None:
    self._lifecycle_write_guard.require_write_allowed(
        command.project_id,
        LifecycleWriteOperation.BASIC_INFORMATION_CONFIRM,
    )
```

Call before creating/updating `ProjectBasicInformationRecord`.

- [ ] **Step 4: Map route errors**

In `routes_project_basic_information.py`, catch `ProjectLifecycleReadonlyError` around draft save and confirm and raise structured 409.

- [ ] **Step 5: Run tests to verify GREEN**

Run:

```powershell
py -m pytest tests\integration\test_project_basic_information_api.py -q
```

Expected:

- Existing active behavior passes.
- Stopped/closed write tests return structured 409.
- Read endpoint remains 200.

### Task 4: Matrix Editor Session Guard

**Files:**

- Modify: `backend/application/matrix_editor_session_service.py`
- Modify: `backend/api/routes_matrix_editor_session.py`
- Test: `tests/integration/test_matrix_editor_session_api.py`

**Interfaces:**

- Guards:
  - `save_editor_draft`
  - `discard_editor_draft`
  - `confirm_session`
- Preserves:
  - `GET /api/projects/{project_id}/matrix-editor/session`

- [ ] **Step 1: Add failing tests**

Add stopped/closed assertions to `tests/integration/test_matrix_editor_session_api.py` using existing session setup helpers:

```python
def test_stopped_project_rejects_matrix_editor_draft_save(client):
    project_id = _seed_project_with_active_confirmed_matrix(
        client,
        lifecycle_state="stopped",
    )
    seed = client.get(f"/api/projects/{project_id}/matrix-editor/session").json()

    response = client.put(
        f"/api/projects/{project_id}/matrix-editor/session/draft",
        json=_draft_payload_from_seed(seed),
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "project_lifecycle_readonly"
```

Add closed confirm test:

```python
def test_closed_project_rejects_matrix_editor_confirm(client):
    project_id = _seed_project_with_active_confirmed_matrix(
        client,
        lifecycle_state="closed",
        closure_type="administrative",
    )
    seed = client.get(f"/api/projects/{project_id}/matrix-editor/session").json()

    response = client.post(
        f"/api/projects/{project_id}/matrix-editor/session/confirm",
        json=_confirm_payload_from_seed(seed),
    )

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["lifecycle_state"] == "closed"
    assert detail["closure_type"] == "administrative"
```

Add read preservation:

```python
def test_stopped_project_can_read_matrix_editor_session(client):
    project_id = _seed_project_with_active_confirmed_matrix(
        client,
        lifecycle_state="stopped",
    )

    response = client.get(f"/api/projects/{project_id}/matrix-editor/session")

    assert response.status_code == 200
```

Use existing helper shapes from the file; if absent, add local helpers that mirror existing seed payloads exactly.

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
py -m pytest tests\integration\test_matrix_editor_session_api.py -q
```

Expected:

- New write tests fail because Matrix editor writes are not yet lifecycle guarded.

- [ ] **Step 3: Inject and call guard**

In `MatrixEditorSessionService.__init__`, add optional `lifecycle_write_guard`.

At the start of each write method:

```python
self._require_write_allowed(command.project_id, LifecycleWriteOperation.MATRIX_EDITOR_DRAFT_SAVE)
self._require_write_allowed(command.project_id, LifecycleWriteOperation.MATRIX_EDITOR_DRAFT_DISCARD)
self._require_write_allowed(command.project_id, LifecycleWriteOperation.MATRIX_EDITOR_CONFIRM)
```

Add a private helper:

```python
def _require_write_allowed(
    self,
    project_id: str,
    operation: LifecycleWriteOperation,
) -> None:
    if self._lifecycle_write_guard is not None:
        self._lifecycle_write_guard.require_write_allowed(project_id, operation)
```

Call before creating revision drafts, saving payloads, deleting pending rebase, or confirming authority.

- [ ] **Step 4: Map route errors**

Catch `ProjectLifecycleReadonlyError` in draft save, discard, and confirm routes.

- [ ] **Step 5: Run tests to verify GREEN**

Run:

```powershell
py -m pytest tests\integration\test_matrix_editor_session_api.py -q
```

Expected:

- New stopped/closed write tests pass.
- Existing active Matrix editor session tests continue to pass.

### Task 5: Fee Pricing Draft Guard

**Files:**

- Modify: `backend/application/fee_evaluation_pricing_draft_persistence_service.py`
- Modify: `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`
- Test: `tests/integration/test_fee_evaluation_pricing_draft_api.py`

**Interfaces:**

- Guards:
  - `save`
  - `discard`
- Preserves:
  - pricing draft load/GET route

- [ ] **Step 1: Add failing tests**

Add:

```python
def test_stopped_project_rejects_fee_pricing_draft_save(client):
    project_id = _seed_project_with_confirmed_matrix_and_fee_context(
        client,
        lifecycle_state="stopped",
    )

    response = client.put(
        f"/api/projects/{project_id}/confirmed-matrix/fee-evaluation/pricing-draft",
        json=_valid_pricing_draft_payload(project_id),
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "project_lifecycle_readonly"
```

Add:

```python
def test_closed_project_rejects_fee_pricing_draft_discard(client):
    project_id = _seed_project_with_confirmed_matrix_and_fee_context(
        client,
        lifecycle_state="closed",
        closure_type="completed",
    )

    response = client.delete(
        f"/api/projects/{project_id}/confirmed-matrix/fee-evaluation/pricing-draft",
        json=_valid_discard_payload(project_id),
    )

    assert response.status_code == 409
    assert response.json()["detail"]["closure_type"] == "completed"
```

Add GET/read preservation for stopped project if the route has a GET operation.

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
py -m pytest tests\integration\test_fee_evaluation_pricing_draft_api.py -q
```

Expected:

- New write tests fail until guard is implemented.

- [ ] **Step 3: Inject and call guard**

Add optional guard to service constructor.

At the top of `save`:

```python
self._require_write_allowed(
    command.project_id,
    LifecycleWriteOperation.FEE_PRICING_DRAFT_SAVE,
)
```

At the top of `discard`:

```python
self._require_write_allowed(
    command.project_id,
    LifecycleWriteOperation.FEE_PRICING_DRAFT_DISCARD,
)
```

Call before `_build_basic_fill(...)` so no draft/context work is performed for readonly projects.

- [ ] **Step 4: Map route errors and run tests**

Run:

```powershell
py -m pytest tests\integration\test_fee_evaluation_pricing_draft_api.py -q
```

Expected:

- New lifecycle readonly tests pass.
- Existing active fee pricing draft tests pass.

### Task 6: Required Forms Generate Guard

**Files:**

- Modify: `backend/application/project_folder_required_forms_service.py`
- Modify: `backend/api/routes_project_folder_required_forms.py`
- Test: `tests/integration/test_project_folder_required_forms_api.py`

**Interfaces:**

- Guards:
  - `ProjectFolderRequiredFormsService.generate`
- Preserves:
  - `preview`

- [ ] **Step 1: Add failing tests**

Add tests:

```python
def test_stopped_project_rejects_required_forms_generate_before_output_registration(client):
    project_id = _seed_required_forms_ready_project(client, lifecycle_state="stopped")

    before = client.get(f"/api/projects/{project_id}/output-records/status").json()
    response = client.post(
        f"/api/projects/{project_id}/project-folder/required-forms/generate",
        json=_valid_required_forms_generate_payload(project_id),
    )
    after = client.get(f"/api/projects/{project_id}/output-records/status").json()

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "project_lifecycle_readonly"
    assert after == before
```

Add preview preservation:

```python
def test_stopped_project_can_preview_required_forms(client):
    project_id = _seed_required_forms_ready_project(client, lifecycle_state="stopped")

    response = client.get(
        f"/api/projects/{project_id}/project-folder/required-forms/preview"
    )

    assert response.status_code in {200, 409}
    if response.status_code == 409:
        assert response.json()["detail"].get("code") != "project_lifecycle_readonly"
```

The preview test allows existing business blockers but forbids lifecycle-readonly blocking.

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
py -m pytest tests\integration\test_project_folder_required_forms_api.py -q
```

Expected:

- Generate lifecycle readonly test fails until guard is added.

- [ ] **Step 3: Inject and call guard**

Add optional guard to service constructor.

At the very start of `generate`:

```python
self._require_write_allowed(
    command.project_id,
    LifecycleWriteOperation.REQUIRED_FORMS_GENERATE,
)
```

Call before `preview(command.project_id)`, file staging, final placement, and output registration.

- [ ] **Step 4: Map route errors and run tests**

Run:

```powershell
py -m pytest tests\integration\test_project_folder_required_forms_api.py -q
```

Expected:

- Stopped/closed generate returns structured 409.
- Preview remains not lifecycle-blocked.
- Existing active tests pass.

### Task 7: LTR Workbook Basic Information Sync Commit Guard

**Files:**

- Modify: `backend/application/ltr_workbook_basic_information_sync_service.py`
- Modify: `backend/api/routes_ltr_workbook_basic_information_sync.py`
- Test: `tests/integration/test_ltr_workbook_basic_information_sync_api.py`

**Interfaces:**

- Guards:
  - `commit`
- Preserves:
  - `preview`
  - `open_readonly_at_ltr`

- [ ] **Step 1: Add failing tests**

Add:

```python
def test_stopped_project_rejects_ltr_workbook_basic_information_sync_commit(
    client,
    fake_ltr_workbook_transaction_gateway,
):
    project_id = _seed_ltr_workbook_sync_ready_project(
        client,
        lifecycle_state="stopped",
    )
    preview = client.get(
        f"/api/projects/{project_id}/ltr-workbook/basic-information-sync/preview"
    ).json()

    response = client.post(
        f"/api/projects/{project_id}/ltr-workbook/basic-information-sync/commit",
        json={
            "operator_confirmed": True,
            "preview_acknowledged": True,
            "expected_confirmed_basic_information_version": preview[
                "confirmed_basic_information_version"
            ],
            "expected_confirmed_basic_information_source_signature_hash": preview[
                "confirmed_basic_information_source_signature_hash"
            ],
            "expected_ltr_number": preview["ltr_number"],
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "project_lifecycle_readonly"
    assert fake_ltr_workbook_transaction_gateway.write_transaction_opened is False
    assert fake_ltr_workbook_transaction_gateway.saved is False
```

If the existing integration fixture does not expose the transaction gateway, add a service-level unit test with a fake transaction gateway and repository-backed stopped project:

```python
def test_stopped_project_ltr_workbook_sync_commit_does_not_open_write_transaction():
    transaction = _FakeLtrWorkbookTransactionGateway()
    service = LtrWorkbookBasicInformationSyncService(
        ltr_store=_LtrStore([_registered_ltr()]),
        basic_information_reader=_BasicInformationReader(_confirmed_basic_information()),
        transaction_gateway=transaction,
        lifecycle_write_guard=ProjectLifecycleWriteGuard(
            _ProjectStore(_project(lifecycle_state=ProjectLifecycleState.STOPPED))
        ),
    )

    with pytest.raises(ProjectLifecycleReadonlyError):
        service.commit(
            CommitLtrWorkbookBasicInformationSyncCommand(
                project_id="P1",
                operator_confirmed=True,
                preview_acknowledged=True,
                expected_confirmed_basic_information_version=1,
                expected_confirmed_basic_information_source_signature_hash="sig",
                expected_ltr_number="DL-2026-06-001",
            )
        )

    assert transaction.write_transaction_opened is False
    assert transaction.saved is False
```

Fake gateway requirement:

```python
class _FakeLtrWorkbookTransactionGateway:
    def __init__(self) -> None:
        self.write_transaction_opened = False
        self.saved = False

    def open_transaction(self):
        self.write_transaction_opened = True
        raise AssertionError("write transaction must not open for readonly project")

    def open_read_only_transaction(self):
        raise AssertionError("readonly transaction is not used by commit")

    def run_short_transaction(self, operation):
        self.write_transaction_opened = True
        raise AssertionError("write transaction must not run for readonly project")
```

Use whichever form best fits the existing test harness, but TASK_338 implementation must include an explicit no-downstream-write assertion for LTR sync commit.

Add readonly open preservation:

```python
def test_stopped_project_can_open_ltr_workbook_readonly(client):
    project_id = _seed_ltr_workbook_sync_ready_project(
        client,
        lifecycle_state="stopped",
    )

    response = client.post(
        f"/api/projects/{project_id}/ltr-workbook/basic-information-sync/open-readonly",
        json={},
    )

    assert response.status_code in {200, 400, 409}
    if response.status_code == 409:
        assert response.json()["detail"].get("code") != "project_lifecycle_readonly"
```

The read-only open test allows environment/workbook setup errors but forbids lifecycle-readonly blocking.

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
py -m pytest tests\integration\test_ltr_workbook_basic_information_sync_api.py -q
```

Expected:

- Commit lifecycle readonly test fails until guard is added.

- [ ] **Step 3: Inject and call guard**

Add optional guard to service constructor.

At the top of `commit`, before preview acknowledgement and before `_latest_registered_ltr` / `_require_basic_information`:

```python
self._require_write_allowed(
    command.project_id,
    LifecycleWriteOperation.LTR_WORKBOOK_BASIC_INFORMATION_SYNC_COMMIT,
)
```

Do not call guard in `preview` or `open_readonly_at_ltr`.

- [ ] **Step 4: Map route errors and run tests**

Run:

```powershell
py -m pytest tests\integration\test_ltr_workbook_basic_information_sync_api.py -q
```

Expected:

- Commit returns structured 409 for stopped/closed projects.
- Preview/read-only open are not lifecycle-readonly blocked.
- Existing active tests pass.

### Task 8: Final TASK_338 Validation And Evidence

**Files:**

- Modify: `docs/lane_evidence/TASK_338_write-guard-integration_developer.md`

- [ ] **Step 1: Run focused first-slice tests**

Run:

```powershell
py -m pytest tests\unit\test_project_lifecycle_write_guard.py tests\integration\test_project_basic_information_api.py tests\integration\test_matrix_editor_session_api.py tests\integration\test_fee_evaluation_pricing_draft_api.py tests\integration\test_project_folder_required_forms_api.py tests\integration\test_ltr_workbook_basic_information_sync_api.py -q
```

Expected:

- All selected first-slice tests pass.

- [ ] **Step 2: Run lifecycle baseline tests**

Run:

```powershell
py -m pytest tests\unit\test_project_lifecycle_state_service.py tests\integration\test_project_lifecycle_api.py tests\integration\test_project_lifecycle_migration.py tests\integration\test_project_registry_summary_api.py -q
```

Expected:

- TASK_337A lifecycle API/state behavior remains passing.

- [ ] **Step 3: Run whitespace check**

Run:

```powershell
git diff --check -- backend/application/project_lifecycle_write_guard.py backend/application/project_basic_information_service.py backend/application/matrix_editor_session_service.py backend/application/fee_evaluation_pricing_draft_persistence_service.py backend/application/project_folder_required_forms_service.py backend/application/ltr_workbook_basic_information_sync_service.py backend/api/dependencies.py backend/api/routes_project_basic_information.py backend/api/routes_matrix_editor_session.py backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py backend/api/routes_project_folder_required_forms.py backend/api/routes_ltr_workbook_basic_information_sync.py tests/unit/test_project_lifecycle_write_guard.py tests/integration/test_project_basic_information_api.py tests/integration/test_matrix_editor_session_api.py tests/integration/test_fee_evaluation_pricing_draft_api.py tests/integration/test_project_folder_required_forms_api.py tests/integration/test_ltr_workbook_basic_information_sync_api.py docs/lane_evidence/TASK_338_write-guard-integration_developer.md
```

Expected:

- No whitespace errors. CRLF normalization warnings are non-blocking.

- [ ] **Step 4: Confirm forbidden surfaces unchanged**

Run:

```powershell
git status --short -- frontend backend/infrastructure/office backend/infrastructure/files
```

Expected:

- No output unless files were already dirty before implementation.
- If pre-existing dirty files exist, record them as unrelated and do not modify them.

- [ ] **Step 5: Update lane evidence and stop**

Record:

- plan approval reference
- files changed
- RED/GREEN validation
- focused test commands and results
- confirmation that TASK_338 did not implement frontend readonly model, Workbench shell, StepInstance, Report, AI, permissions, LAN/server, multi-user, or public-drive authority replacement

Do not update global `docs/task_board.md` as Developer.

## 5. Risks And Mitigations

### Risk: Existing services do work before write mutation

Mitigation:

- Guard at the top of selected write methods before any repository write, file generation, Office transaction, workbook transaction, pending rebase, output registration, or final placement.
- Tests include no-mutation assertions where practical.

### Risk: Existing API route tests use complex fixtures

Mitigation:

- Prefer extending existing integration test files and helpers.
- If a route setup is too expensive, use service-level unit tests with fake downstream ports to prove no mutation, plus one API route test for error mapping in the same feature area.

### Risk: Preview endpoints may mutate hidden state

Mitigation:

- Do not guard preview endpoints in TASK_338 first slice.
- Add tests that previews are not blocked by lifecycle-readonly guard.
- If a preview is found to mutate state, record it and require explicit follow-up approval before changing its classification.

### Risk: Old `ProjectLifecycleService` conflicts with new overlay guard

Mitigation:

- Do not expand `backend/application/project_lifecycle_service.py`.
- New guard uses TASK_337A `Project.lifecycle_state` and `closure_type`.
- Existing old status-based service remains for historical status preconditions until a future cleanup task.

### Risk: Broad scope creep

Mitigation:

- First slice is limited to five representative areas.
- Inventory categories outside this plan remain for future tasks.
- No frontend or Workbench shell work.

## 6. Acceptance Criteria

TASK_338 implementation is ready for review when:

- Shared lifecycle write guard exists and uses TASK_337A lifecycle overlay fields.
- Stopped project writes return `409 project_lifecycle_readonly` with `allowed_actions=["resume", "close"]`.
- Closed completed writes return `409 project_lifecycle_readonly` with `closure_type="completed"` and empty `allowed_actions`.
- Closed administrative writes return `409 project_lifecycle_readonly` with `closure_type="administrative"` and empty `allowed_actions`.
- Guard not-found errors map to API `404` instead of unhandled `500`.
- Active project write behavior remains covered by existing tests.
- Selected readonly preview/read endpoints are not blocked by lifecycle readonly guard.
- Tests prove no downstream mutation for at least Basic Information, Required Forms, and LTR workbook sync paths.
- TASK_338 does not change frontend, Workbench shell, Office gateway internals, database schema, StepInstance, Report, AI, permissions, LAN/server, multi-user, or public-drive authority semantics.

## 7. Plan-Only Validation

Before implementation approval, validate only the plan file:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Test-Path docs\task_338_project_lifecycle_write_guard_integration_plan.md
Select-String -Path docs\task_338_project_lifecycle_write_guard_integration_plan.md -Pattern 'ProjectLifecycleWriteGuard' -Encoding UTF8
Select-String -Path docs\task_338_project_lifecycle_write_guard_integration_plan.md -Pattern 'project_lifecycle_readonly' -Encoding UTF8
Select-String -Path docs\task_338_project_lifecycle_write_guard_integration_plan.md -Pattern 'Required Forms' -Encoding UTF8
Select-String -Path docs\task_338_project_lifecycle_write_guard_integration_plan.md -Pattern 'LTR workbook Basic Information sync commit' -Encoding UTF8
rg -n "[ \t]$" docs\task_338_project_lifecycle_write_guard_integration_plan.md
git diff --check -- docs/task_338_project_lifecycle_write_guard_integration_plan.md
```

Expected:

- Plan file exists.
- Guard helper, error code, selected first-slice paths, and validation commands are present.
- Trailing whitespace scan returns no matches.
- `git diff --check` reports no whitespace errors.

## 8. Stop Point

Stop after creating `docs/task_338_project_lifecycle_write_guard_integration_plan.md`.

Do not write product code, update `docs/task_board.md`, update lane evidence, implement TASK_338, start TASK_340, or enter any frontend/Workbench implementation lane until the TASK_338 plan is explicitly reviewed and approved.
