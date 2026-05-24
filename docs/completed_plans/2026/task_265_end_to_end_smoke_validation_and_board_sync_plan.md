# TASK_265 End-To-End Smoke Validation And Board Sync Implementation Plan

> **For agentic workers:** Optional workflow aid: use `superpowers:executing-plans` to execute step-by-step with checklist tracking (`- [ ]`).

**Goal:** Add one narrow end-to-end smoke test proving Matrix import group selection flows through SourceMatrix, ProjectMatrixDraft, ConfirmedMatrix, and ConfirmedMatrix-backed Test Record preview, then update task status documentation after validation passes.

**Architecture:** This plan adds no new runtime behavior. It uses existing FastAPI routes and repositories in an integration test: `POST /api/projects/{project_id}/matrix-import/commit`, `POST /api/projects/{project_id}/matrix-drafts/{draft_id}/confirm`, and `GET /api/projects/{project_id}/confirmed-matrix/test-record-preview`. Repository reads are used only inside the test to verify lineage and selected-only projections.

**Tech Stack:** Python 3.11+, pytest, FastAPI `TestClient`, SQLAlchemy temporary SQLite database, existing ConnLab repositories and DTOs.

---

## Protocol Status

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_265_END_TO_END_SMOKE_VALIDATION_AND_BOARD_SYNC`
- Why allowed now: `TASK_264_MATRIX_TO_TEST_RECORD_SMOKE_UI` is complete and `docs/task_board.md` marks `TASK_265_END_TO_END_SMOKE_VALIDATION_AND_BOARD_SYNC` as the current planned active task.
- Implementation status: planning only.
- Approval gate: implementation remains blocked until the user explicitly approves this plan.

## File Structure

Create:

- `tests/integration/test_matrix_to_test_record_smoke_flow_api.py`

Modify after validation passes:

- `tasks/TASK_265_END_TO_END_SMOKE_VALIDATION_AND_BOARD_SYNC.md`
- `docs/task_board.md`

Do not modify:

- backend application services
- backend API routes
- backend repositories/models
- frontend source files
- Matrix parser
- report/fee/equipment code

## Task 1: Add The End-To-End Integration Smoke Test

**Files:**

- Create: `tests/integration/test_matrix_to_test_record_smoke_flow_api.py`

- [ ] **Step 1: Create test file with temporary app/database fixture**

Use this exact starting structure:

```python
from __future__ import annotations

from collections.abc import Generator
from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session, get_settings
from backend.api.main import app
from backend.domain import Project, ProjectStatus
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    ConfirmedMatrixAuthorityRepository,
    ProjectMatrixDraftRepository,
    ProjectRepository,
    SourceMatrixImportRepository,
)
from backend.shared.config import Settings


def _client(tmp_path: Path) -> tuple[TestClient, object, object]:
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    engine = create_database_engine(settings)
    init_db(engine)
    session_factory = create_session_factory(engine)

    def override_session() -> Generator[Session, None, None]:
        with session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app), engine, session_factory


def _seed_project(project_id: str, session_factory: object) -> None:
    with session_factory() as session:  # type: ignore[operator]
        ProjectRepository(session).create(
            Project(
                project_id=project_id,
                project_no=f"DL-2026-05-{project_id}",
                product_name="Connector",
                requestor="Alice",
                status=ProjectStatus.LTR_REGISTERED,
                created_on=date(2026, 5, 23),
            )
        )
        session.commit()
```

Run:

```powershell
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
```

Expected:

- The file imports but has no actual test yet, or pytest reports no tests. Continue to Step 2 before treating this as useful.

- [ ] **Step 2: Add preview payload helper**

Add this helper:

```python
def _commit_payload() -> dict[str, object]:
    return {
        "source_document_path": "C:/spec.docx",
        "source_document_name": "spec.docx",
        "source_format": ".docx",
        "selected_group_keys": ["g1", "g3"],
        "preview_payload": {
            "groups": [
                {
                    "group_key": "g1",
                    "group_label": "Group 1",
                    "sample_quantity_expression": "5",
                },
                {
                    "group_key": "g2",
                    "group_label": "Group 2",
                    "sample_quantity_expression": "6",
                },
                {
                    "group_key": "g3",
                    "group_label": "Group 3",
                    "sample_quantity_expression": "7",
                },
            ],
            "rows": [
                {
                    "source_row_index": 1,
                    "test_item": "Visual",
                    "source_section": "6.1",
                    "method": "",
                    "condition": "",
                    "requirement": "",
                    "group_tokens": {"g1": "1", "g2": "2", "g3": "3"},
                    "is_sample_row": False,
                },
                {
                    "source_row_index": 2,
                    "test_item": "LLCR",
                    "source_section": "6.2",
                    "method": "",
                    "condition": "",
                    "requirement": "",
                    "group_tokens": {"g1": "4(a)", "g2": "5", "g3": "6,7"},
                    "is_sample_row": False,
                },
                {
                    "source_row_index": 3,
                    "test_item": "Samples Quantity (PCS)",
                    "source_section": None,
                    "group_tokens": {"g1": "5", "g2": "6", "g3": "7"},
                    "is_sample_row": True,
                },
            ],
            "warnings": [],
            "blockers": [],
        },
    }
```

Run:

```powershell
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
```

Expected:

- Still no meaningful test result until Step 3.

- [ ] **Step 3: Add repository assertion helper**

Add this helper:

```python
def _assert_lineage_and_authority(
    *,
    session_factory: object,
    source_import_id: str,
    draft_id: str,
    confirmed_id: str,
) -> None:
    with session_factory() as session:  # type: ignore[operator]
        source = SourceMatrixImportRepository(session).get_snapshot_by_import(source_import_id)
        assert source is not None
        assert [group.group_key for group in source.groups] == ["g1", "g2", "g3"]

        draft = ProjectMatrixDraftRepository(session).get(draft_id)
        assert draft is not None
        assert [group.group_key for group in draft.groups] == ["g1", "g3"]
        assert "g2" not in {group.group_key for group in draft.groups}

        confirmed = ConfirmedMatrixAuthorityRepository(session).get(confirmed_id)
        assert confirmed is not None
        assert [group.group_key for group in confirmed.groups] == ["g1", "g3"]
        assert "g2" not in {group.group_key for group in confirmed.groups}
```

Run:

```powershell
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
```

Expected:

- Still no meaningful test result until Step 4.

- [ ] **Step 4: Add the main end-to-end test**

Add this test:

```python
def test_matrix_to_test_record_smoke_flow_preserves_source_and_excludes_unselected(
    tmp_path: Path,
) -> None:
    client, engine, session_factory = _client(tmp_path)
    try:
        _seed_project("P1", session_factory)

        commit = client.post("/api/projects/P1/matrix-import/commit", json=_commit_payload())
        assert commit.status_code == 201
        commit_body = commit.json()
        assert commit_body["selected_group_keys_committed"] == ["g1", "g3"]
        assert [group["group_key"] for group in commit_body["project_matrix_draft"]["groups"]] == [
            "g1",
            "g3",
        ]
        source_import_id = commit_body["source_import_id"]
        draft_id = commit_body["project_matrix_draft"]["record"]["project_matrix_draft_id"]

        confirm = client.post(
            f"/api/projects/P1/matrix-drafts/{draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert confirm.status_code == 201
        confirmed_body = confirm.json()
        confirmed_id = confirmed_body["version"]["confirmed_matrix_id"]
        assert [group["group_key"] for group in confirmed_body["groups"]] == ["g1", "g3"]

        preview = client.get("/api/projects/P1/confirmed-matrix/test-record-preview")
        assert preview.status_code == 200
        preview_body = preview.json()
        assert preview_body["project_id"] == "P1"
        assert preview_body["confirmed_matrix_id"] == confirmed_id
        assert preview_body["preview_status"] == "ready"
        assert [group["group_key"] for group in preview_body["groups"]] == ["g1", "g3"]
        assert "g2" not in {group["group_key"] for group in preview_body["groups"]}

        samples = {
            group["group_key"]: group["sample_quantity_expression"]
            for group in preview_body["groups"]
        }
        assert samples == {"g1": "5", "g3": "7"}

        steps_by_group = {
            group["group_key"]: [step["raw_token"] for step in group["steps"]]
            for group in preview_body["groups"]
        }
        assert steps_by_group["g1"] == ["1", "4(a)"]
        assert steps_by_group["g3"] == ["3", "6", "7"]

        first_step = preview_body["groups"][0]["steps"][0]
        assert first_step["section"] == "6.1"
        assert "source_section" not in first_step

        _assert_lineage_and_authority(
            session_factory=session_factory,
            source_import_id=source_import_id,
            draft_id=draft_id,
            confirmed_id=confirmed_id,
        )
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
```

Run:

```powershell
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
```

Expected:

- `1 passed`.

If this fails because an existing route behaves differently, stop and report the exact failure. Do not expand TASK_265 into an implementation fix without user approval.

## Task 2: Regression Validation

**Files:**

- No source changes expected.

- [ ] **Step 1: Run TASK_263 API contract test**

Run:

```powershell
py -m pytest tests\integration\test_confirmed_matrix_test_record_preview_api.py -q
```

Expected:

- `3 passed`.

- [ ] **Step 2: Run TASK_264 component test**

Run:

```powershell
cd frontend; npm test -- --run TestRecordPreviewSmokePanel
```

Expected:

- Component test passes, including the assertion that unselected `Group 2 (g2)` is not rendered.

- [ ] **Step 3: Run frontend build**

Run:

```powershell
cd frontend; npm run build
```

Expected:

- Build passes.

- [ ] **Step 4: Run focused import/preview regression**

Run:

```powershell
py -m pytest tests\integration\test_matrix_import_group_selection_commit_api.py tests\unit\test_confirmed_matrix_test_record_preview_service.py -q
```

Expected:

- Existing tests pass.

## Task 3: Documentation And Board Sync

**Files:**

- Modify: `tasks/TASK_265_END_TO_END_SMOKE_VALIDATION_AND_BOARD_SYNC.md`
- Modify: `docs/task_board.md`
- Optional Create: `docs/matrix_to_test_record_smoke_validation.md`

- [ ] **Step 1: Update TASK_265 task file to complete**

Change `Status` to:

```markdown
Complete on 2026-05-23. End-to-end Matrix authority to Test Record preview smoke validation is implemented and passing.
```

Change `Current Active Task` to:

```markdown
none. `TASK_265_END_TO_END_SMOKE_VALIDATION_AND_BOARD_SYNC` is complete; awaiting next approved task.
```

- [ ] **Step 2: Update task board top status**

In `docs/task_board.md`:

- Add `TASK_265 complete` to the status line.
- Set Current Active Task to `none`.
- Add completion notes with:
  - new test file
  - validation commands and pass counts
  - statement that no fee/report/equipment/StepInstance scope was introduced
- Do not activate a next task automatically.

- [ ] **Step 3: Optional smoke validation note**

Create `docs/matrix_to_test_record_smoke_validation.md` only if useful for human audit. Keep it short:

```markdown
# Matrix To Test Record Smoke Validation

Date: 2026-05-23

Validated flow:

Import commit -> SourceMatrix -> ProjectMatrixDraft -> ConfirmedMatrix -> Test Record preview.

Result:

- SourceMatrix retained groups g1, g2, g3.
- Selected-only draft retained g1 and g3.
- ConfirmedMatrix retained g1 and g3.
- Test Record preview retained g1 and g3.
- Unselected g2 remained source lineage only.
- Sample quantities survived for g1 and g3.

Validation:

- `py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q`
```

## Final Validation Commands

Run all before final response:

```powershell
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
```

```powershell
py -m pytest tests\integration\test_confirmed_matrix_test_record_preview_api.py -q
```

```powershell
py -m pytest tests\integration\test_matrix_import_group_selection_commit_api.py tests\unit\test_confirmed_matrix_test_record_preview_service.py -q
```

```powershell
cd frontend; npm test -- --run TestRecordPreviewSmokePanel
```

```powershell
cd frontend; npm run build
```

## Self-Review

- Spec coverage: Covers full SourceMatrix lineage, selected-only ProjectMatrixDraft, ConfirmedMatrix authority, Test Record preview, sample quantity propagation, unselected group exclusion, and board sync.
- Placeholder scan: No task step depends on unspecified behavior.
- Type consistency: Uses existing API routes and repository methods already present in TASK_261 through TASK_264.
- Scope control: No new backend service, frontend UI, database schema, report, fee, equipment, StepInstance, or execution persistence work is included.
