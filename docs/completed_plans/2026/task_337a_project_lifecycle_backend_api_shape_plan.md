# TASK_337A Project Lifecycle Backend API Shape Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a backend Project lifecycle overlay and action API for Stop, Resume, Close as completed, and Close administrative while preserving existing project progress/status compatibility.

**Architecture:** Add a narrow lifecycle overlay to Project records, plus a lifecycle event ledger for traceability. Keep existing `Project.status` as compatibility/progress data and treat legacy `cancelled` rows as stopped when no lifecycle overlay exists. Expose typed FastAPI lifecycle DTOs under Project routes; defer broad write-operation guarding to TASK_338.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.x, SQLite, pytest.

## Global Constraints

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current approved lane: `lifecycle-backend-api`.
- Role: Developer.
- First step is planning only; product code changes require explicit user approval of this plan.
- Do not implement broad write guard integration from TASK_338.
- Do not change frontend UI, Workbench shell, Projects registry UI, Office gateway internals, public-drive LTR authority, Matrix/Fee/LTR/Folder/Basic Information behavior outside lifecycle action shape.
- Do not implement StepInstance, Report generation, AI, permissions, LAN/server, or multi-user scope.
- Preserve TASK_336 semantics: Stop means pause/resumable; stopped is readonly except Resume/Close; closed is readonly archive; closed cannot resume; completed close v1 is manual confirmation plus output status summary; completed close defaults to formal/registered projects; temporary/no-LTR projects default to administrative close.

---

## 1. Current Task Understanding

### Objective

Create the approved implementation plan for TASK_337A. After user approval, implement backend lifecycle state/API shape only.

### Inputs

- Existing Project records in `projects`.
- Existing `Project.status` values, including legacy `cancelled`.
- Existing temporary project context and LTR records to determine formal/registered eligibility.
- Existing output status summary for completed-close summary signals.
- Operator request DTOs for stop/resume/close actions.

### Outputs

- Backend domain/application/API shape for:
  - `GET /api/projects/{project_id}/lifecycle`
  - `POST /api/projects/{project_id}/lifecycle/stop`
  - `POST /api/projects/{project_id}/lifecycle/resume`
  - `POST /api/projects/{project_id}/lifecycle/close-completed`
  - `POST /api/projects/{project_id}/lifecycle/close-administrative`
- Persisted lifecycle overlay fields.
- Persisted lifecycle event records.
- Focused unit and integration tests for transitions, reason/note requirements, compatibility, and API responses.

### Involved Modules

- `backend/domain/enums.py`
- `backend/domain/models.py`
- `backend/application/project_lifecycle_management_service.py`
- `backend/application/project_registry_summary_service.py` only if lifecycle response needs registry/formal identity helpers; avoid broad registry behavior changes.
- `backend/application/project_output_record_service.py` only as an output-summary input; do not change output semantics.
- `backend/infrastructure/storage/models.py`
- `backend/infrastructure/storage/database.py`
- `backend/infrastructure/storage/repositories/project.py`
- New lifecycle event repository under `backend/infrastructure/storage/repositories/`.
- `backend/api/routes_project.py`
- `backend/api/dependencies.py`
- Tests under `tests/unit/` and `tests/integration/`.

### Explicit Non-Goals

- No TASK_338 broad lifecycle write guards.
- No Matrix/Fee/Folder/LTR/Public Drive/Office write-path guarding beyond the lifecycle action endpoints.
- No frontend or Workbench shell behavior.
- No project registry view redesign.
- No StepInstance, Report generation, AI, permissions, LAN/server, multi-user.

## 2. Design Decisions

### 2.1 Lifecycle Overlay Representation

Add lifecycle fields to `Project` and `projects`:

```text
lifecycle_state: active | stopped | closed
closure_type: null | completed | administrative
stopped_reason: string | null
stopped_at: string | null
stopped_by: string | null
resumed_reason: string | null
resumed_at: string | null
resumed_by: string | null
closed_reason: string | null
closed_at: string | null
closed_by: string | null
completion_summary_json: string | null
```

Reasoning:

- TASK_336 says lifecycle is an overlay separate from existing progress/status values.
- Updating `Project.status` alone would keep encoding stopped as `cancelled`, which TASK_336 explicitly rejects as the long-term product meaning.
- Columns on `projects` give efficient read access for registry/workbench API consumers; an event table keeps traceability.

### 2.2 Lifecycle Events

Create a `project_lifecycle_events` table:

```text
event_id: string primary key
project_id: string foreign key
event_type: stop | resume | close_completed | close_administrative
previous_lifecycle_state: string
new_lifecycle_state: string
previous_closure_type: string | null
new_closure_type: string | null
reason: string | null
operator: string | null
created_at: string
metadata_json: string | null
```

Reasoning:

- Existing `project_cleanup_audit_records` is cleanup-oriented and uses required `previous_status`/`new_status` fields. It can remain for legacy cleanup/stop history, but TASK_337A should not overload cleanup audit as the lifecycle event ledger.
- Lifecycle events are future-readable by Workbench history without implying cleanup.

### 2.3 Compatibility With Existing `cancelled`

Rules:

- New lifecycle state is authoritative when `Project.lifecycle_state` is present.
- Existing rows without lifecycle columns are migrated to `active` by default.
- Existing rows with `status='cancelled'` are migrated to `lifecycle_state='stopped'`, `closure_type=null`, preserving `status='cancelled'` as compatibility status.
- Existing rows with `status='closed'` are migrated to `lifecycle_state='closed'`, `closure_type='administrative'`, preserving `status='closed'` as compatibility status because old rows do not distinguish completed vs administrative close.
- New Stop action must set `lifecycle_state='stopped'` and must also set `Project.status='cancelled'` during this compatibility phase. This is the concrete TASK_337A compatibility policy, not an implementation-time option.
- Stop must record `previous_project_status` in `project_lifecycle_events.metadata_json` before changing compatibility status to `cancelled`.
- Resume must restore `Project.status` from the latest lifecycle stop event `previous_project_status` metadata.
- Resume must not guess `draft` for legacy stopped rows. If a migrated `cancelled` row has no lifecycle stop event metadata and no usable cleanup audit `previous_status`, Resume returns `409 Conflict` with a business-readable legacy-data message instead of corrupting progress state.
- Lifecycle API responses must expose `lifecycle_state='stopped'` as product authority even while legacy `status='cancelled'` remains for current frontend compatibility.

Implementation note:

- During migration, if a `project_cleanup_audit_records` row with `cleanup_type='project_stopped'` exists for a legacy `cancelled` project, TASK_337A may create a lifecycle stop event seeded with that audit `previous_status`.
- If no reliable previous status exists, do not synthesize one.
- The old `/api/projects/{project_id}/stop` response may continue returning `status='cancelled'` and `status_label='Stopped'`, but new lifecycle endpoints are authoritative for future frontend lanes.

### 2.4 API Shape

Recommended routes in `backend/api/routes_project.py`:

```text
GET  /api/projects/{project_id}/lifecycle
POST /api/projects/{project_id}/lifecycle/stop
POST /api/projects/{project_id}/lifecycle/resume
POST /api/projects/{project_id}/lifecycle/close-completed
POST /api/projects/{project_id}/lifecycle/close-administrative
```

Request DTOs:

```python
class ProjectLifecycleStopRequest(BaseModel):
    reason: str | None = None
    operator: str | None = None

class ProjectLifecycleResumeRequest(BaseModel):
    reason: str | None = None
    operator: str | None = None

class ProjectLifecycleCloseCompletedRequest(BaseModel):
    close_note: str = Field(min_length=1)
    operator: str | None = None
    manual_completion_confirmed: bool
    output_summary_acknowledged: bool

class ProjectLifecycleCloseAdministrativeRequest(BaseModel):
    reason: str = Field(min_length=1)
    operator: str | None = None
```

Response DTO:

```python
class ProjectLifecycleResponse(BaseModel):
    project_id: str
    lifecycle_state: str
    closure_type: str | None = None
    status_label: str
    readonly: bool
    allowed_actions: list[str]
    status: str
    stopped_at: str | None = None
    stopped_reason: str | None = None
    closed_at: str | None = None
    closed_reason: str | None = None
    completion_summary: dict[str, object] | None = None
    warnings: list[str] = Field(default_factory=list)
```

Lifecycle action errors:

```python
class ProjectLifecycleActionErrorResponse(BaseModel):
    code: str
    project_id: str
    lifecycle_state: str
    closure_type: str | None = None
    message: str
    allowed_actions: list[str]
```

Map action conflicts to HTTP `409`.

### 2.5 Completed Close Summary

`Close completed` v1 must not claim test execution completion. It should store a manual summary:

```json
{
  "manual_completion_confirmed": true,
  "output_summary_acknowledged": true,
  "close_note": "Operator note",
  "signals": {
    "project_identity": "...",
    "registered_ltr": true,
    "output_status_summary_available": true
  },
  "warning": "Testing completion is manually confirmed in this phase because StepInstance does not exist."
}
```

TASK_337A can use available lightweight signals only:

- formal identity from `Project.project_no` or registered LTR records
- output record summary from `ProjectOutputRecordService.get_status_summary()` if already available through repository wiring
- no StepInstance checks
- no Office/file/public-drive probing

### 2.6 Temporary/No-LTR Boundary

Completed close v1:

- allow only when the project has formal identity:
  - `project.project_no` is present, or
  - at least one LTR record exists for the project
- reject temporary/no-LTR planning projects with `409` and a message directing administrative close.

Administrative close:

- allow for active or stopped projects.
- require non-empty reason.

## 3. File Structure

### Create

- `backend/application/project_lifecycle_state_service.py`
  - Owns lifecycle transition rules and DTO-like dataclasses.
  - Keeps `ProjectLifecycleManagementService` from growing into a mixed safe-delete/lifecycle god service.

- `backend/infrastructure/storage/repositories/project_lifecycle_event.py`
  - Persists `ProjectLifecycleEvent` records.

- `tests/integration/test_project_lifecycle_migration.py`
  - Creates a legacy SQLite schema/data state without lifecycle columns and verifies `init_db` backfills lifecycle overlay fields.

- `tests/unit/test_project_lifecycle_state_service.py`
  - Unit tests for transition rules, reason/note requirements, compatibility, and formal/temporary completed-close boundary.

- `tests/integration/test_project_lifecycle_api.py`
  - API tests for GET/stop/resume/close completed/close administrative.

### Modify

- `backend/domain/enums.py`
  - Add `ProjectLifecycleState`, `ProjectClosureType`, `ProjectLifecycleEventType`.

- `backend/domain/models.py`
  - Add lifecycle fields to `Project`.
  - Add immutable helper methods such as `with_lifecycle(...)` or a focused replacement helper.
  - Add `ProjectLifecycleEvent` dataclass.

- `backend/domain/__init__.py`
  - Export `ProjectLifecycleState`, `ProjectClosureType`, `ProjectLifecycleEventType`, and `ProjectLifecycleEvent` following existing domain package patterns.

- `backend/infrastructure/storage/models.py`
  - Add lifecycle columns to `ProjectModel`.
  - Add `ProjectLifecycleEventModel`.

- `backend/infrastructure/storage/database.py`
  - Add migration function for project lifecycle columns and event table.
  - Call it from `init_db`.

- `backend/infrastructure/storage/repositories/project.py`
  - Map lifecycle fields between ORM and domain.

- `backend/infrastructure/storage/repositories/__init__.py`
  - Export `ProjectLifecycleEventRepository` following existing repository package patterns.

- `backend/api/dependencies.py`
  - Add `get_project_lifecycle_state_service(...)`.

- `backend/api/routes_project.py`
  - Add lifecycle request/response DTOs and routes.
  - Keep existing `/stop` endpoint for compatibility if needed, but implement new `/lifecycle/stop` route as the contract path.

- `tests/unit/test_project_lifecycle_management_service.py`
  - Keep existing safe-delete/legacy stop tests or adapt only if the old stop route delegates to new lifecycle state service.

- `tests/integration/test_project_api.py`
  - Update only if `ProjectResponse` gains lifecycle fields. Prefer not to add lifecycle fields to general `ProjectResponse` in TASK_337A unless reviewer asks; use the lifecycle endpoint instead.

## 4. Implementation Tasks

### Task 1: Domain Lifecycle Types And Project Fields

**Files:**

- Modify: `backend/domain/enums.py`
- Modify: `backend/domain/models.py`
- Modify: `backend/domain/__init__.py`
- Test: `tests/unit/test_project_lifecycle_state_service.py`

**Interfaces:**

- Produces:
  - `ProjectLifecycleState`
  - `ProjectClosureType`
  - `ProjectLifecycleEventType`
  - lifecycle fields on `Project`
  - `ProjectLifecycleEvent`

- [ ] Add enum definitions:

```python
class ProjectLifecycleState(StrEnum):
    """Lifecycle overlay for project mutability."""

    ACTIVE = "active"
    STOPPED = "stopped"
    CLOSED = "closed"


class ProjectClosureType(StrEnum):
    """Closure reason category for closed projects."""

    COMPLETED = "completed"
    ADMINISTRATIVE = "administrative"


class ProjectLifecycleEventType(StrEnum):
    """Audited lifecycle transition event type."""

    STOP = "stop"
    RESUME = "resume"
    CLOSE_COMPLETED = "close_completed"
    CLOSE_ADMINISTRATIVE = "close_administrative"
```

- [ ] Add fields to `Project` with defaults:

```python
lifecycle_state: ProjectLifecycleState = ProjectLifecycleState.ACTIVE
closure_type: ProjectClosureType | None = None
stopped_reason: str | None = None
stopped_at: str | None = None
stopped_by: str | None = None
resumed_reason: str | None = None
resumed_at: str | None = None
resumed_by: str | None = None
closed_reason: str | None = None
closed_at: str | None = None
closed_by: str | None = None
completion_summary_json: str | None = None
```

- [ ] Add a helper on `Project`:

```python
def with_lifecycle(
    self,
    *,
    lifecycle_state: ProjectLifecycleState,
    closure_type: ProjectClosureType | None = None,
    stopped_reason: str | None = None,
    stopped_at: str | None = None,
    stopped_by: str | None = None,
    resumed_reason: str | None = None,
    resumed_at: str | None = None,
    resumed_by: str | None = None,
    closed_reason: str | None = None,
    closed_at: str | None = None,
    closed_by: str | None = None,
    completion_summary_json: str | None = None,
) -> "Project":
    """Return a copy of the project with updated lifecycle overlay fields."""
```

- [ ] Add `ProjectLifecycleEvent` dataclass with fields listed in section 2.2.

- [ ] Run focused import test:

```powershell
py -m pytest tests\unit\test_project_service.py -q
```

Expected: existing project creation tests still pass.

### Task 2: Storage Columns, Event Table, And Repository Mapping

**Files:**

- Modify: `backend/infrastructure/storage/models.py`
- Modify: `backend/infrastructure/storage/database.py`
- Modify: `backend/infrastructure/storage/repositories/project.py`
- Modify: `backend/infrastructure/storage/repositories/__init__.py`
- Create: `backend/infrastructure/storage/repositories/project_lifecycle_event.py`
- Test: `tests/unit/test_project_service.py`
- Test: `tests/integration/test_project_api.py`
- Test: `tests/integration/test_project_lifecycle_migration.py`

**Interfaces:**

- Consumes domain lifecycle fields/events from Task 1.
- Produces:
  - project lifecycle columns loaded through `ProjectRepository`
  - `ProjectLifecycleEventRepository.create(...)`
  - `ProjectLifecycleEventRepository.list_by_project(...)`

- [ ] Add nullable lifecycle columns to `ProjectModel`, with `lifecycle_state` non-null for new rows:

```python
lifecycle_state: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
closure_type: Mapped[str | None] = mapped_column(String(32))
stopped_reason: Mapped[str | None] = mapped_column(Text)
stopped_at: Mapped[str | None] = mapped_column(String(64))
stopped_by: Mapped[str | None] = mapped_column(String(255))
resumed_reason: Mapped[str | None] = mapped_column(Text)
resumed_at: Mapped[str | None] = mapped_column(String(64))
resumed_by: Mapped[str | None] = mapped_column(String(255))
closed_reason: Mapped[str | None] = mapped_column(Text)
closed_at: Mapped[str | None] = mapped_column(String(64))
closed_by: Mapped[str | None] = mapped_column(String(255))
completion_summary_json: Mapped[str | None] = mapped_column(Text)
```

- [ ] Add `ProjectLifecycleEventModel` with the table shape in section 2.2.

- [ ] Add `_migrate_project_lifecycle_columns_and_events(engine)` to `database.py`:
  - if `projects.lifecycle_state` is missing, add all lifecycle columns
  - set `lifecycle_state='stopped'` where `status='cancelled'`
  - set `lifecycle_state='closed'` and `closure_type='administrative'` where `status='closed'` unless a future migration has better closure data
  - set remaining null/blank lifecycle states to `active`
  - create `project_lifecycle_events` if missing

- [ ] Update `ProjectRepository._to_model`, `_to_domain`, and `update`.

- [ ] Add repository tests either to `tests/unit/test_project_service.py` or a focused repository test:

```python
def test_project_repository_round_trips_lifecycle_fields(...):
    ...
```

- [ ] Add migration integration test in `tests/integration/test_project_lifecycle_migration.py`:

```python
from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine

from backend.infrastructure.storage.database import init_db


def test_init_db_backfills_lifecycle_columns_for_legacy_projects(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "connlab.sqlite3"
    engine = create_engine(f"sqlite:///{database_path.as_posix()}", future=True)
    with engine.begin() as connection:
        connection.exec_driver_sql(
            """
            CREATE TABLE projects (
                project_id VARCHAR(64) NOT NULL,
                project_no VARCHAR(128),
                product_name VARCHAR(255) NOT NULL,
                requestor VARCHAR(255) NOT NULL,
                status VARCHAR(64) NOT NULL,
                business_unit VARCHAR(255),
                created_on DATE,
                PRIMARY KEY (project_id)
            )
            """
        )
        connection.exec_driver_sql(
            """
            INSERT INTO projects (
                project_id, project_no, product_name, requestor, status, business_unit, created_on
            )
            VALUES
                ('P-ACTIVE', 'DL-2026-06-001', 'Connector A', 'Alice', 'ltr_registered', NULL, NULL),
                ('P-STOPPED', 'DL-2026-06-002', 'Connector B', 'Bob', 'cancelled', NULL, NULL),
                ('P-CLOSED', 'DL-2026-06-003', 'Connector C', 'Cara', 'closed', NULL, NULL)
            """
        )

    init_db(engine)

    with engine.connect() as connection:
        rows = {
            row.project_id: row
            for row in connection.exec_driver_sql(
                "SELECT project_id, status, lifecycle_state, closure_type FROM projects"
            ).all()
        }

    assert rows["P-ACTIVE"].lifecycle_state == "active"
    assert rows["P-ACTIVE"].closure_type is None
    assert rows["P-STOPPED"].status == "cancelled"
    assert rows["P-STOPPED"].lifecycle_state == "stopped"
    assert rows["P-STOPPED"].closure_type is None
    assert rows["P-CLOSED"].status == "closed"
    assert rows["P-CLOSED"].lifecycle_state == "closed"
    assert rows["P-CLOSED"].closure_type == "administrative"
```

- [ ] Export the new repository in `backend/infrastructure/storage/repositories/__init__.py`:

```python
from backend.infrastructure.storage.repositories.project_lifecycle_event import (
    ProjectLifecycleEventRepository,
)

__all__ = [
    ...
    "ProjectLifecycleEventRepository",
    ...
]
```

- [ ] Run:

```powershell
py -m pytest tests\unit\test_project_service.py tests\integration\test_project_api.py tests\integration\test_project_lifecycle_migration.py -q
```

Expected: existing project behavior remains compatible.

### Task 3: Lifecycle State Service

**Files:**

- Create: `backend/application/project_lifecycle_state_service.py`
- Test: `tests/unit/test_project_lifecycle_state_service.py`

**Interfaces:**

- Consumes:
  - `ProjectStore.get/update`
  - `LtrRecordStore.list_by_project`
  - `ProjectOutputRecordService.get_status_summary` or a narrow output summary port
  - `ProjectLifecycleEventStore.create`

- Produces:
  - `ProjectLifecycleStateService.get_lifecycle(project_id)`
  - `stop_project(command)`
  - `resume_project(command)`
  - `close_completed(command)`
  - `close_administrative(command)`

- [ ] Define command/result dataclasses:

```python
@dataclass(frozen=True, slots=True)
class StopProjectLifecycleCommand:
    project_id: str
    reason: str | None = None
    operator: str | None = None

@dataclass(frozen=True, slots=True)
class ResumeProjectLifecycleCommand:
    project_id: str
    reason: str | None = None
    operator: str | None = None

@dataclass(frozen=True, slots=True)
class CloseCompletedProjectCommand:
    project_id: str
    close_note: str
    manual_completion_confirmed: bool
    output_summary_acknowledged: bool
    operator: str | None = None

@dataclass(frozen=True, slots=True)
class CloseAdministrativeProjectCommand:
    project_id: str
    reason: str
    operator: str | None = None
```

- [ ] Define result dataclass:

```python
@dataclass(frozen=True, slots=True)
class ProjectLifecycleView:
    project_id: str
    lifecycle_state: ProjectLifecycleState
    closure_type: ProjectClosureType | None
    status: ProjectStatus
    status_label: str
    readonly: bool
    allowed_actions: tuple[str, ...]
    stopped_at: str | None
    stopped_reason: str | None
    closed_at: str | None
    closed_reason: str | None
    completion_summary: dict[str, object] | None
    warnings: tuple[str, ...]
```

- [ ] Define errors:

```python
class ProjectLifecycleStateError(ValueError):
    """Raised when a lifecycle transition cannot be completed."""

class ProjectLifecycleStateNotFoundError(ProjectLifecycleStateError):
    """Raised when a project cannot be found."""
```

- [ ] Implement transition rules:
  - active -> stopped
  - stopped -> active
  - active/stopped -> closed completed
  - active/stopped -> closed administrative
  - closed -> any action is blocked
  - repeated stop on stopped returns the current stopped view without creating a new event
  - resume restores the compatibility `Project.status` from latest lifecycle stop event metadata `previous_project_status`
  - resume rejects legacy stopped rows without reliable previous status instead of defaulting to `draft`

- [ ] Enforce requiredness:
  - stop reason optional, default message acceptable
  - resume reason optional
  - close administrative reason required after stripping whitespace
  - close completed note required after stripping whitespace
  - close completed requires `manual_completion_confirmed is True`
  - close completed requires `output_summary_acknowledged is True`

- [ ] Enforce formal/registered completed close:
  - allow if `project.project_no` has text or LTR repository returns at least one record
  - reject temporary/no-LTR projects with message: `Close as completed is available only for formal or registered projects in this phase. Use Administrative close for temporary planning projects.`

- [ ] Unit tests:

```powershell
py -m pytest tests\unit\test_project_lifecycle_state_service.py -q
```

Expected cases:

- active stop creates stopped view and event
- stopped resume restores active and event
- closed project cannot resume
- active formal project can close completed with manual confirmation
- temporary/no-LTR project cannot close completed
- active project can close administrative with reason
- blank administrative reason is rejected
- blank completed close note is rejected
- legacy `status=cancelled` without lifecycle overlay is treated as stopped if implementation needs compatibility normalization
- new Stop keeps compatibility `status=cancelled` and records `previous_project_status`
- Resume restores compatibility status from stop event metadata
- legacy migrated `cancelled` row with no previous status metadata is not resumed with guessed `draft`

### Task 4: FastAPI Lifecycle Routes And DTO Mapping

**Files:**

- Modify: `backend/api/dependencies.py`
- Modify: `backend/api/routes_project.py`
- Test: `tests/integration/test_project_lifecycle_api.py`

**Interfaces:**

- Consumes `ProjectLifecycleStateService`.
- Produces lifecycle API routes from section 2.4.

- [ ] Add dependency factory:

```python
def get_project_lifecycle_state_service(
    session: Session = Depends(get_session),
) -> ProjectLifecycleStateService:
    """Build Project lifecycle state/action service."""
```

- [ ] Add Pydantic request/response DTOs in `routes_project.py`.

- [ ] Add route handlers:
  - `get_project_lifecycle`
  - `stop_project_lifecycle`
  - `resume_project_lifecycle`
  - `close_project_completed`
  - `close_project_administrative`

- [ ] Preserve old `POST /api/projects/{project_id}/stop`:
  - Delegate it to `ProjectLifecycleStateService.stop_project(...)`.
  - Return the legacy response shape so existing callers do not break.
  - Keep `status='cancelled'` in the legacy response during this compatibility phase.

- [ ] Map service errors:
  - not found -> `404`
  - transition/requiredness/business conflict -> `409`

- [ ] Integration tests:

```powershell
py -m pytest tests\integration\test_project_lifecycle_api.py -q
```

Expected cases:

- `GET /lifecycle` returns active lifecycle for new project
- `POST /lifecycle/stop` returns stopped, readonly true, allowed actions `resume` and `close`
- stop reason may be omitted
- `POST /lifecycle/resume` returns active after stopped
- closed completed cannot resume
- close administrative requires non-empty reason
- close completed requires non-empty note, manual confirmation, and output summary acknowledgement
- temporary/no-LTR project close completed returns 409 with administrative-close guidance
- formal project close completed succeeds
- closed project cannot be stopped again

### Task 5: Compatibility And Existing Tests

**Files:**

- Modify: `tests/unit/test_project_lifecycle_management_service.py` only if old stop delegates or behavior changes.
- Modify: `tests/integration/test_project_registry_summary_api.py` only if old stop response/status expectations require compatibility assertions.
- Do not modify frontend tests in TASK_337A.

**Interfaces:**

- Existing `/api/projects/{project_id}/stop` remains compatible enough for current frontend/tests.
- New lifecycle endpoints are the authority for future frontend lanes.

- [ ] If old stop delegates to new service, preserve legacy response fields:

```text
project_id
previous_status
status
status_label
reason
audit_recorded
```

- [ ] Keep `status_label="Stopped"` for stopped projects.

- [ ] Ensure existing tests still pass:

```powershell
py -m pytest tests\unit\test_project_lifecycle_management_service.py tests\integration\test_project_registry_summary_api.py tests\integration\test_project_api.py -q
```

Expected: existing compatibility checks pass or are updated only to reflect explicit lifecycle overlay addition.

### Task 6: Final Validation For TASK_337A

**Files:**

- No new implementation files beyond approved plan list.
- Update `docs/lane_evidence/TASK_337A_lifecycle-backend-api_developer.md` after implementation validation only.

- [ ] Run focused TASK_337A validation:

```powershell
py -m pytest tests\unit\test_project_lifecycle_state_service.py tests\unit\test_project_lifecycle_management_service.py tests\integration\test_project_lifecycle_api.py tests\integration\test_project_lifecycle_migration.py tests\integration\test_project_api.py -q
```

- [ ] Run affected existing lifecycle/registry group:

```powershell
py -m pytest tests\unit\test_project_lifecycle_service.py tests\integration\test_project_lifecycle_gating_api.py tests\integration\test_project_registry_summary_api.py tests\integration\test_project_lifecycle_migration.py -q
```

- [ ] Run whitespace check:

```powershell
git diff --check -- backend/domain/enums.py backend/domain/models.py backend/domain/__init__.py backend/application/project_lifecycle_state_service.py backend/application/project_lifecycle_management_service.py backend/infrastructure/storage/models.py backend/infrastructure/storage/database.py backend/infrastructure/storage/repositories/project.py backend/infrastructure/storage/repositories/project_lifecycle_event.py backend/infrastructure/storage/repositories/__init__.py backend/api/dependencies.py backend/api/routes_project.py tests/unit/test_project_lifecycle_state_service.py tests/unit/test_project_lifecycle_management_service.py tests/integration/test_project_lifecycle_api.py tests/integration/test_project_lifecycle_migration.py tests/integration/test_project_api.py tests/integration/test_project_registry_summary_api.py docs/lane_evidence/TASK_337A_lifecycle-backend-api_developer.md
```

- [ ] Confirm no forbidden files changed:

```powershell
git status --short -- frontend backend/infrastructure/office backend/infrastructure/files
```

Expected:

- No frontend files.
- No Office gateway internals.
- Only approved backend/API/storage/test files.

## 5. Risks And Mitigations

### Risk: Adding lifecycle columns changes broad Project responses

Mitigation:

- Keep existing `ProjectResponse` stable in TASK_337A unless explicitly needed.
- Use `GET /api/projects/{project_id}/lifecycle` for lifecycle details.

### Risk: Legacy `cancelled` compatibility conflicts with new stopped overlay

Mitigation:

- Migrate old `cancelled` rows to lifecycle stopped.
- Preserve old status where needed for current frontend compatibility.
- Make lifecycle response authoritative for future frontend work.

### Risk: Resume cannot restore pre-stop progress for legacy stopped rows

Mitigation:

- Store previous project status in new stop event metadata.
- Use existing cleanup audit `previous_status` only when it is available and reliable.
- Block Resume for legacy migrated `cancelled` rows without a recoverable previous status instead of guessing `draft`.

### Risk: Close completed overclaims test completion

Mitigation:

- Require manual confirmation, output summary acknowledgement, and close note.
- Include explicit warning that StepInstance does not exist and completion is manually confirmed.

### Risk: TASK_337A accidentally becomes TASK_338

Mitigation:

- Do not add lifecycle checks to Matrix/Fee/Folder/LTR/Public Drive write paths in TASK_337A.
- TASK_337A only provides state/API shape for downstream guard integration.

## 6. Acceptance Criteria

TASK_337A implementation is acceptable after plan approval when:

- lifecycle overlay is persisted and loaded through Project repository
- lifecycle event ledger records stop/resume/close actions
- new lifecycle API routes return typed DTOs
- stop reason optional behavior is covered
- administrative close reason required behavior is covered
- completed close note/manual-confirmation/output-summary acknowledgement are covered
- completed close default formal/registered boundary is covered
- stopped project can resume or close
- closed project cannot resume, stop, or close again
- legacy `cancelled` compatibility is explicit and tested
- active project behavior outside lifecycle endpoints remains unchanged
- broad TASK_338 write guard integration is not implemented

## 7. Plan-Only Validation

Before product implementation, validate only planning files:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Test-Path docs\task_337a_project_lifecycle_backend_api_shape_plan.md
Select-String -Path docs\task_337a_project_lifecycle_backend_api_shape_plan.md -Pattern 'ProjectLifecycleState' -Encoding UTF8
Select-String -Path docs\task_337a_project_lifecycle_backend_api_shape_plan.md -Pattern 'CloseCompletedProjectCommand' -Encoding UTF8
Select-String -Path docs\task_337a_project_lifecycle_backend_api_shape_plan.md -Pattern 'TASK_338' -Encoding UTF8
Select-String -Path docs\lane_evidence\TASK_337A_lifecycle-backend-api_developer.md -Pattern 'ready_for_review' -Encoding UTF8
rg -n "[ \t]$" docs\task_337a_project_lifecycle_backend_api_shape_plan.md docs\lane_evidence\TASK_337A_lifecycle-backend-api_developer.md
```

Expected:

- plan file exists
- lifecycle DTO/service terms are present
- TASK_338 is explicitly deferred
- evidence is ready for review
- trailing whitespace scan returns no matches

## 8. Stop Point

Stop after creating this plan and updating `docs/lane_evidence/TASK_337A_lifecycle-backend-api_developer.md`.

Do not write backend/API/storage/test product implementation until the user explicitly approves this plan.
