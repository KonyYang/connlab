# Test Record Word Generation v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate a downloadable Word `.docx` Test Record draft from the active ConfirmedMatrix authority.

**Architecture:** Reuse the existing ConfirmedMatrix Test Record preview service as the read model, map it into a small application-owned document model, and write the Word file only through the infrastructure Office gateway. Add one backend download endpoint and a narrow Project Workbench action that calls the API through `frontend/src/api/client.ts`.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy repositories, python-docx behind `backend/infrastructure/office`, React, TypeScript, Vitest, Testing Library, pytest.

---

## Anti-Skip Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_271_TEST_RECORD_WORD_GENERATION_V1` (planned)
- Allowed reason: `TASK_270_RECORD_STEP_WORKSPACE_PANEL` is complete, the task board has no active implementation task, and `docs/post_phase11_matrix_driven_laboratory_execution_workflow_guideline.md` names TASK_271 as the next Matrix to Test Record continuity slice.

Implementation must wait for explicit user approval after this plan is reviewed.

## Required Project Protocol

Before implementation, use:

- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `$impeccable` product context for the frontend button and status copy

## Product / UI Context

ConnLab is a `product` UI. The operator is a lab coordinator on an offline Windows workstation after Matrix authority confirmation. The task should feel like a controlled derived-output action, not a report center.

UI constraints:

- State before action.
- Matrix before output.
- Test Record is derived from active ConfirmedMatrix.
- Use operational copy: `Generate Test Record Draft`.
- No Report, Fee, AI, equipment, permission, or execution-data action expansion.
- No arbitrary local path input in the frontend.

## Scope Boundary

In scope:

- Backend generation from active ConfirmedMatrix only.
- Word `.docx` draft generation through infrastructure gateway using a controlled default Test Record layout.
- Downloadable response.
- Minimal Project Workbench action and status feedback.
- Tests and static guards.

Out of scope:

- Formal `TestRecord` aggregate.
- StepInstance or execution persistence.
- Report engine.
- Fee generation.
- AI review.
- Equipment assignment.
- Permission workflow.
- Generation history.
- Historical Test Record template selection.
- Generic template engine.
- Saving generated files under project folder as a managed artifact.

## File Structure

Create:

- `backend/application/confirmed_matrix_test_record_document_generation_service.py`
  - Owns generation orchestration from active ConfirmedMatrix preview.
  - Builds a small document model.
  - Chooses a controlled output directory under settings-provided data path.
  - Calls the Office gateway through a protocol.

- `backend/api/routes_confirmed_matrix_test_record_generation.py`
  - Adds `POST /api/projects/{project_id}/confirmed-matrix/test-record-draft/generate`.
  - Returns `FileResponse` for the generated `.docx`.
  - Maps known not-found and invalid-source errors to `404` / `422`.

- `frontend/src/features/project-workbench/TestRecordDraftGenerationButton.tsx`
  - Renders one action labelled `Generate Test Record Draft`.
  - Calls the API client function.
  - Triggers browser download from a returned Blob.
  - Shows concise loading/error state.

- `frontend/src/features/project-workbench/TestRecordDraftGenerationButton.test.tsx`
  - Covers ready click, disabled state, loading label, and error feedback.

- `tests/unit/test_confirmed_matrix_test_record_document_generation_service.py`
  - Verifies active ConfirmedMatrix only, empty preview rejection, deterministic output naming, and writer payload.

- `tests/integration/test_confirmed_matrix_test_record_generation_api.py`
  - Seeds ConfirmedMatrix through existing source import/draft/confirm path.
  - Posts generation endpoint.
  - Opens returned `.docx` and checks selected group/step content.

Modify:

- `backend/infrastructure/office/models.py`
  - Add a small `ConfirmedMatrixTestRecordDocumentWriteResult` if existing result fields are insufficient.

- `backend/infrastructure/office/test_record_document_gateway.py`
  - Add a ConfirmedMatrix-backed generation method using python-docx.
  - Keep existing legacy `generate(...)` behavior unchanged.

- `backend/infrastructure/office/__init__.py`
  - Export any new result model if added.

- `backend/api/dependencies.py`
  - Wire `ConfirmedMatrixTestRecordDocumentGenerationService`.

- `backend/api/main.py`
  - Include the new generation router.

- `frontend/src/api/client.ts`
  - Add typed Blob generation client function.
  - Keep `fetch()` inside API client only.

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
  - Render the generation button in the confirmed Matrix projection header or summary area.
  - Enable only when preview state is `ready`.

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`
  - Assert the generation action is visible and disabled/unavailable for not-ready state.

- `frontend/src/workbench.css`
  - Add compact action/status styles near matrix projection rules.

- `tests/unit/test_frontend_shell_files.py`
  - Add TASK_271 static guard for API boundary, button copy, no forbidden future actions, and backend route wiring.

- `docs/task_board.md`, `docs/task_plan_index.md`, `tasks/TASK_271_TEST_RECORD_WORD_GENERATION_V1.md`
  - Update only after implementation and validation.

---

### Task 1: Add Backend Service Tests

**Files:**

- Create: `tests/unit/test_confirmed_matrix_test_record_document_generation_service.py`
- Create later: `backend/application/confirmed_matrix_test_record_document_generation_service.py`

- [ ] **Step 1: Write the failing service tests**

Create `tests/unit/test_confirmed_matrix_test_record_document_generation_service.py`:

```python
from __future__ import annotations

from pathlib import Path

import pytest

from backend.application.confirmed_matrix_test_record_document_generation_service import (
    ConfirmedMatrixTestRecordDocumentGenerationError,
    ConfirmedMatrixTestRecordDocumentGenerationNotFoundError,
    ConfirmedMatrixTestRecordDocumentGenerationService,
    GenerateConfirmedMatrixTestRecordDocumentCommand,
)
from backend.application.confirmed_matrix_test_record_preview_service import (
    ConfirmedMatrixTestRecordPreview,
    ConfirmedMatrixTestRecordPreviewGroup,
    ConfirmedMatrixTestRecordPreviewNotFoundError,
    ConfirmedMatrixTestRecordPreviewStep,
)


def test_generation_service_writes_preview_groups_to_controlled_output(tmp_path: Path) -> None:
    writer = _Writer()
    service = ConfirmedMatrixTestRecordDocumentGenerationService(
        preview_service=_PreviewService(_preview()),
        project_store=_ProjectStore(),
        writer=writer,
    )

    result = service.generate(
        GenerateConfirmedMatrixTestRecordDocumentCommand(
            project_id="P1",
            output_dir=tmp_path,
        )
    )

    assert result.project_id == "P1"
    assert result.confirmed_matrix_id == "cmv-1"
    assert result.output_path.name == "P1_test_record_draft.docx"
    assert writer.calls[0]["product_description"] == "Connector"
    assert writer.calls[0]["groups"][0].group_label == "Group 1"
    assert writer.calls[0]["groups"][0].sample_quantity_expression == "5"
    assert writer.calls[0]["groups"][0].steps[0].raw_token == "1"


def test_generation_service_uses_active_confirmed_preview_only(tmp_path: Path) -> None:
    service = ConfirmedMatrixTestRecordDocumentGenerationService(
        preview_service=_PreviewService(None),
        project_store=_ProjectStore(),
        writer=_Writer(),
    )

    with pytest.raises(ConfirmedMatrixTestRecordDocumentGenerationNotFoundError):
        service.generate(
            GenerateConfirmedMatrixTestRecordDocumentCommand(
                project_id="P1",
                output_dir=tmp_path,
            )
        )


def test_generation_service_rejects_empty_preview(tmp_path: Path) -> None:
    empty = ConfirmedMatrixTestRecordPreview(
        project_id="P1",
        confirmed_matrix_id="cmv-empty",
        preview_status="empty",
        groups=(),
    )
    service = ConfirmedMatrixTestRecordDocumentGenerationService(
        preview_service=_PreviewService(empty),
        project_store=_ProjectStore(),
        writer=_Writer(),
    )

    with pytest.raises(ConfirmedMatrixTestRecordDocumentGenerationError, match="no previewable"):
        service.generate(
            GenerateConfirmedMatrixTestRecordDocumentCommand(
                project_id="P1",
                output_dir=tmp_path,
            )
        )


class _PreviewService:
    def __init__(self, preview: ConfirmedMatrixTestRecordPreview | None) -> None:
        self.preview = preview

    def build_preview(self, command):
        if self.preview is None:
            raise ConfirmedMatrixTestRecordPreviewNotFoundError("Active confirmed matrix not found.")
        return self.preview


class _Project:
    project_id = "P1"
    product_name = "Connector"
    project_no = "DL-001"


class _ProjectStore:
    def get(self, project_id: str):
        return _Project() if project_id == "P1" else None


class _Writer:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def generate_from_confirmed_matrix(self, **kwargs):
        self.calls.append(kwargs)
        kwargs["output_path"].write_bytes(b"docx")
        return kwargs["output_path"]


def _preview() -> ConfirmedMatrixTestRecordPreview:
    return ConfirmedMatrixTestRecordPreview(
        project_id="P1",
        confirmed_matrix_id="cmv-1",
        preview_status="ready",
        groups=(
            ConfirmedMatrixTestRecordPreviewGroup(
                group_key="g1",
                group_label="Group 1",
                sample_quantity_expression="5",
                step_count=1,
                steps=(
                    ConfirmedMatrixTestRecordPreviewStep(
                        sequence=1,
                        raw_token="1",
                        test_item="Visual",
                        section="6.1",
                        method="EIA-364-18",
                        condition="10x",
                        requirement="No damage",
                    ),
                ),
            ),
        ),
    )
```

- [ ] **Step 2: Run the service tests and verify they fail**

Run:

```powershell
py -m pytest tests\unit\test_confirmed_matrix_test_record_document_generation_service.py -q
```

Expected: FAIL because the service module does not exist.

---

### Task 2: Implement Backend Generation Service

**Files:**

- Create: `backend/application/confirmed_matrix_test_record_document_generation_service.py`
- Modify: `backend/api/dependencies.py`

- [ ] **Step 1: Add the application service**

Create `backend/application/confirmed_matrix_test_record_document_generation_service.py`:

```python
"""Generate Word Test Record drafts from active Confirmed Matrix authority."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from backend.application.confirmed_matrix_test_record_preview_service import (
    BuildConfirmedMatrixTestRecordPreviewCommand,
    ConfirmedMatrixTestRecordPreview,
    ConfirmedMatrixTestRecordPreviewNotFoundError,
    ConfirmedMatrixTestRecordPreviewService,
)


class ConfirmedMatrixTestRecordDocumentGenerationError(ValueError):
    """Raised when active confirmed Matrix data cannot generate a document."""


class ConfirmedMatrixTestRecordDocumentGenerationNotFoundError(LookupError):
    """Raised when required active authority or project data is missing."""


class ProjectLookup(Protocol):
    """Project read operations needed for document metadata."""

    def get(self, project_id: str):
        """Return one project domain object by id."""


class ConfirmedMatrixTestRecordDocumentWriter(Protocol):
    """Infrastructure writer for Word Test Record drafts."""

    def generate_from_confirmed_matrix(
        self,
        *,
        output_path: Path,
        project_id: str,
        project_no: str,
        product_description: str,
        applicable_specification: str,
        confirmed_matrix_id: str,
        groups: tuple,
    ) -> Path:
        """Write one `.docx` draft and return its output path."""


@dataclass(frozen=True, slots=True)
class GenerateConfirmedMatrixTestRecordDocumentCommand:
    """Command for ConfirmedMatrix-backed Test Record Word generation."""

    project_id: str
    output_dir: Path
    overwrite: bool = True


@dataclass(frozen=True, slots=True)
class ConfirmedMatrixTestRecordDocumentGenerationResult:
    """Result for one generated Test Record Word draft."""

    project_id: str
    confirmed_matrix_id: str
    output_path: Path
    file_name: str


class ConfirmedMatrixTestRecordDocumentGenerationService:
    """Generate one Word Test Record draft from active ConfirmedMatrix preview data."""

    def __init__(
        self,
        *,
        preview_service: ConfirmedMatrixTestRecordPreviewService,
        project_store: ProjectLookup,
        writer: ConfirmedMatrixTestRecordDocumentWriter,
    ) -> None:
        """Create the service with read-model and Office writer boundaries."""
        self._preview_service = preview_service
        self._project_store = project_store
        self._writer = writer

    def generate(
        self,
        command: GenerateConfirmedMatrixTestRecordDocumentCommand,
    ) -> ConfirmedMatrixTestRecordDocumentGenerationResult:
        """Generate a downloadable Word draft from active ConfirmedMatrix authority."""
        output_dir = Path(command.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        preview = self._load_preview(command.project_id)
        if preview.preview_status != "ready" or not preview.groups:
            raise ConfirmedMatrixTestRecordDocumentGenerationError(
                "Active confirmed matrix has no previewable Test Record steps."
            )

        project = self._project_store.get(command.project_id)
        project_no = str(getattr(project, "project_no", "") or "")
        product_description = str(getattr(project, "product_name", "") or "")
        file_name = _safe_file_name(command.project_id)
        output_path = output_dir / file_name
        if output_path.exists() and not command.overwrite:
            raise ConfirmedMatrixTestRecordDocumentGenerationError(
                f"Output file already exists: {output_path}"
            )

        written = self._writer.generate_from_confirmed_matrix(
            output_path=output_path,
            project_id=command.project_id,
            project_no=project_no,
            product_description=product_description,
            applicable_specification="",
            confirmed_matrix_id=preview.confirmed_matrix_id,
            groups=preview.groups,
        )
        return ConfirmedMatrixTestRecordDocumentGenerationResult(
            project_id=command.project_id,
            confirmed_matrix_id=preview.confirmed_matrix_id,
            output_path=written,
            file_name=file_name,
        )

    def _load_preview(self, project_id: str) -> ConfirmedMatrixTestRecordPreview:
        """Load active confirmed preview and translate not-found errors."""
        try:
            return self._preview_service.build_preview(
                BuildConfirmedMatrixTestRecordPreviewCommand(project_id=project_id)
            )
        except ConfirmedMatrixTestRecordPreviewNotFoundError as exc:
            raise ConfirmedMatrixTestRecordDocumentGenerationNotFoundError(str(exc)) from exc


def _safe_file_name(project_id: str) -> str:
    """Build a deterministic download file name without path separators."""
    safe_project = project_id.replace("/", "_").replace("\\", "_").strip() or "project"
    return f"{safe_project}_test_record_draft.docx"
```

- [ ] **Step 2: Wire the service dependency**

In `backend/api/dependencies.py`, import:

```python
from backend.application.confirmed_matrix_test_record_document_generation_service import (
    ConfirmedMatrixTestRecordDocumentGenerationService,
)
```

Add:

```python
def get_confirmed_matrix_test_record_document_generation_service(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> ConfirmedMatrixTestRecordDocumentGenerationService:
    """Build the ConfirmedMatrix-backed Test Record Word generation service."""
    return ConfirmedMatrixTestRecordDocumentGenerationService(
        preview_service=ConfirmedMatrixTestRecordPreviewService(
            confirmed_store=ConfirmedMatrixAuthorityRepository(session),
        ),
        project_store=ProjectRepository(session),
        writer=TestRecordDocumentGateway(),
    )
```

The API route will pass `settings.data_dir / "generated_test_records"` as the controlled output directory.

- [ ] **Step 3: Run service tests**

Run:

```powershell
py -m pytest tests\unit\test_confirmed_matrix_test_record_document_generation_service.py -q
```

Expected: PASS.

---

### Task 3: Extend Word Gateway For ConfirmedMatrix Drafts

**Files:**

- Modify: `backend/infrastructure/office/test_record_document_gateway.py`
- Modify: `tests/unit/test_test_record_document_gateway.py`

- [ ] **Step 1: Add a failing gateway test**

Append to `tests/unit/test_test_record_document_gateway.py`:

```python
def test_gateway_generates_confirmed_matrix_test_record_docx(tmp_path: Path) -> None:
    output = tmp_path / "confirmed-record.docx"
    group = _ConfirmedGroup()

    result = TestRecordDocumentGateway().generate_from_confirmed_matrix(
        output_path=output,
        project_id="P1",
        project_no="DL-001",
        product_description="Connector",
        applicable_specification="GS-12-1507",
        confirmed_matrix_id="cmv-1",
        groups=(group,),
    )

    assert result == output
    document = Document(output)
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    table_text = "\n".join(
        cell.text for table in document.tables for row in table.rows for cell in row.cells
    )
    assert "ConnLab Test Record Draft" in text
    assert "Project No.: DL-001" in text
    assert "Product Description: Connector" in text
    assert "Applicable Specification: GS-12-1507" in text
    assert "Group Number: Group 1" in text
    assert "Sample Quantity & Number:" in text
    assert "5" in text
    assert "Start Date/Time:" in text
    assert "Equipment ID No.:" in text
    assert "Tested By:" in text
    assert "Visual" in table_text
    assert "EIA-364-18" in table_text
    assert "No damage" in table_text


class _ConfirmedStep:
    sequence = 1
    raw_token = "1"
    test_item = "Visual"
    section = "6.1"
    method = "EIA-364-18"
    condition = "10x"
    requirement = "No damage"


class _ConfirmedGroup:
    group_key = "g1"
    group_label = "Group 1"
    sample_quantity_expression = "5"
    step_count = 1
    steps = (_ConfirmedStep(),)
```

- [ ] **Step 2: Run gateway tests and verify failure**

Run:

```powershell
py -m pytest tests\unit\test_test_record_document_gateway.py -q
```

Expected: FAIL because `generate_from_confirmed_matrix` does not exist.

- [ ] **Step 3: Add gateway method**

In `backend/infrastructure/office/test_record_document_gateway.py`, add a method to `TestRecordDocumentGateway`:

```python
    def generate_from_confirmed_matrix(
        self,
        *,
        output_path: Path,
        project_id: str,
        project_no: str,
        product_description: str,
        applicable_specification: str,
        confirmed_matrix_id: str,
        groups: tuple,
    ) -> Path:
        """Generate a v1 Test Record Word draft from ConfirmedMatrix preview groups."""
        target = Path(output_path)
        if target.suffix.lower() != ".docx":
            raise ValueError(f"Only .docx output is supported: {target}")
        if not target.parent.exists():
            raise FileNotFoundError(f"Output directory does not exist: {target.parent}")

        document = Document()
        document.add_heading("ConnLab Test Record Draft", level=1)
        document.add_paragraph(f"Project ID: {project_id}")
        document.add_paragraph(f"Project No.: {project_no}")
        document.add_paragraph(f"Product Description: {product_description}")
        document.add_paragraph(f"Applicable Specification: {applicable_specification}")
        document.add_paragraph(f"Confirmed Matrix: {confirmed_matrix_id}")
        document.add_paragraph("Start Date/Time:")
        document.add_paragraph("Complete Date/Time:")
        document.add_paragraph("Equipment ID No.:")
        document.add_paragraph("Tested By:")

        for group in groups:
            document.add_heading(f"Group Number: {group.group_label}", level=2)
            document.add_paragraph(
                f"Sample Quantity & Number: {group.sample_quantity_expression}"
            )
            table = document.add_table(rows=1, cols=7)
            headers = table.rows[0].cells
            headers[0].text = "Step"
            headers[1].text = "Token"
            headers[2].text = "Test items"
            headers[3].text = "Test Method"
            headers[4].text = "Test conditions"
            headers[5].text = "Remarks"
            headers[6].text = "Execution data"
            for step in group.steps:
                row = table.add_row().cells
                row[0].text = str(step.sequence)
                row[1].text = step.raw_token
                row[2].text = step.test_item
                row[3].text = step.method
                row[4].text = step.condition
                row[5].text = step.requirement
                row[6].text = ""
        document.save(target)
        return target
```

Keep the existing legacy `generate(...)` method unchanged.

- [ ] **Step 4: Run gateway tests**

Run:

```powershell
py -m pytest tests\unit\test_test_record_document_gateway.py -q
```

Expected: PASS.

---

### Task 4: Add Download API

**Files:**

- Create: `backend/api/routes_confirmed_matrix_test_record_generation.py`
- Modify: `backend/api/main.py`
- Test: `tests/integration/test_confirmed_matrix_test_record_generation_api.py`

- [ ] **Step 1: Write failing integration test**

Create `tests/integration/test_confirmed_matrix_test_record_generation_api.py` by following the seeding pattern in `tests/integration/test_confirmed_matrix_test_record_preview_api.py`. The core assertions:

```python
def test_confirmed_matrix_test_record_generation_api_downloads_docx(tmp_path: Path) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_id = _seed_source_import("P1", tmp_path)
        draft = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_id, "selected_group_keys": ["g1"]},
        )
        draft_id = draft.json()["record"]["project_matrix_draft_id"]
        confirm = client.post(
            f"/api/projects/P1/matrix-drafts/{draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert confirm.status_code == 201

        response = client.post(
            "/api/projects/P1/confirmed-matrix/test-record-draft/generate"
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        output = tmp_path / "downloaded.docx"
        output.write_bytes(response.content)
        document = Document(output)
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        table_text = "\n".join(
            cell.text for table in document.tables for row in table.rows for cell in row.cells
        )
        assert "ConnLab Test Record Draft" in text
        assert "Product Description: Connector" in text
        assert "Group Number: G1" in text
        assert "Sample Quantity & Number: 5" in text
        assert "Visual" in table_text
        assert "LLCR" in table_text
        assert "G2" not in text
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
```

Also add:

```python
def test_confirmed_matrix_test_record_generation_api_returns_404_without_active_matrix(
    tmp_path: Path,
) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        response = client.post(
            "/api/projects/P1/confirmed-matrix/test-record-draft/generate"
        )
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
```

- [ ] **Step 2: Run integration test and verify failure**

Run:

```powershell
py -m pytest tests\integration\test_confirmed_matrix_test_record_generation_api.py -q
```

Expected: FAIL because the route does not exist.

- [ ] **Step 3: Add route**

Create `backend/api/routes_confirmed_matrix_test_record_generation.py`:

```python
"""Confirmed-Matrix-backed Test Record Word generation API route."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from backend.api.dependencies import (
    get_confirmed_matrix_test_record_document_generation_service,
    get_settings,
)
from backend.application.confirmed_matrix_test_record_document_generation_service import (
    ConfirmedMatrixTestRecordDocumentGenerationError,
    ConfirmedMatrixTestRecordDocumentGenerationNotFoundError,
    ConfirmedMatrixTestRecordDocumentGenerationService,
    GenerateConfirmedMatrixTestRecordDocumentCommand,
)
from backend.shared.config import Settings


router = APIRouter(tags=["confirmed-matrix-test-record-generation"])


@router.post("/api/projects/{project_id}/confirmed-matrix/test-record-draft/generate")
def generate_confirmed_matrix_test_record_draft(
    project_id: str,
    service: ConfirmedMatrixTestRecordDocumentGenerationService = Depends(
        get_confirmed_matrix_test_record_document_generation_service
    ),
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    """Generate and return one Word Test Record draft from active ConfirmedMatrix."""
    try:
        result = service.generate(
            GenerateConfirmedMatrixTestRecordDocumentCommand(
                project_id=project_id,
                output_dir=settings.data_dir / "generated_test_records",
            )
        )
    except ConfirmedMatrixTestRecordDocumentGenerationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ConfirmedMatrixTestRecordDocumentGenerationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return FileResponse(
        path=result.output_path,
        filename=result.file_name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
```

- [ ] **Step 4: Register router**

In `backend/api/main.py`, import:

```python
from backend.api.routes_confirmed_matrix_test_record_generation import (
    router as confirmed_matrix_test_record_generation_router,
)
```

Include after the preview router:

```python
app.include_router(confirmed_matrix_test_record_generation_router)
```

- [ ] **Step 5: Run backend tests**

Run:

```powershell
py -m pytest tests\unit\test_confirmed_matrix_test_record_document_generation_service.py -q
py -m pytest tests\unit\test_test_record_document_gateway.py -q
py -m pytest tests\integration\test_confirmed_matrix_test_record_generation_api.py -q
```

Expected: PASS.

---

### Task 5: Add Frontend API Client

**Files:**

- Modify: `frontend/src/api/client.ts`

- [ ] **Step 1: Add client function**

Add near the confirmed Matrix Test Record preview client:

```ts
export function generateConfirmedMatrixTestRecordDraft(
  projectId: string
): Promise<Blob> {
  return requestBlob(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-matrix/test-record-draft/generate`,
    { method: "POST" }
  );
}
```

If `requestBlob` does not accept options yet, update it narrowly to mirror `requestJson` options while preserving existing callers.

- [ ] **Step 2: Run frontend type build after UI wiring**

Do not run yet if no component imports the function. It will be verified in Task 6.

---

### Task 6: Add Project Workbench Generation Button

**Files:**

- Create: `frontend/src/features/project-workbench/TestRecordDraftGenerationButton.tsx`
- Create: `frontend/src/features/project-workbench/TestRecordDraftGenerationButton.test.tsx`
- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`
- Modify: `frontend/src/workbench.css`

- [ ] **Step 1: Write failing button tests**

Create `frontend/src/features/project-workbench/TestRecordDraftGenerationButton.test.tsx`:

```tsx
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { TestRecordDraftGenerationButton } from "./TestRecordDraftGenerationButton";

const apiMocks = vi.hoisted(() => ({
  generateConfirmedMatrixTestRecordDraft: vi.fn(),
}));

vi.mock("../../api/client", () => ({
  generateConfirmedMatrixTestRecordDraft: apiMocks.generateConfirmedMatrixTestRecordDraft,
}));

describe("TestRecordDraftGenerationButton", () => {
  beforeEach(() => {
    apiMocks.generateConfirmedMatrixTestRecordDraft.mockReset();
  });

  it("generates a Test Record draft when ready", async () => {
    apiMocks.generateConfirmedMatrixTestRecordDraft.mockResolvedValue(
      new Blob(["docx"], {
        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      })
    );

    render(<TestRecordDraftGenerationButton projectId="P1" ready />);

    fireEvent.click(screen.getByRole("button", { name: "Generate Test Record Draft" }));

    await waitFor(() => {
      expect(apiMocks.generateConfirmedMatrixTestRecordDraft).toHaveBeenCalledWith("P1");
    });
  });

  it("disables generation when confirmed Matrix preview is not ready", () => {
    render(<TestRecordDraftGenerationButton projectId="P1" ready={false} />);

    expect(screen.getByRole("button", { name: "Generate Test Record Draft" })).toBeDisabled();
    expect(screen.getByText("Confirm Matrix authority before generating a Test Record draft.")).toBeTruthy();
  });

  it("shows an error when generation fails", async () => {
    apiMocks.generateConfirmedMatrixTestRecordDraft.mockRejectedValue(new Error("failed"));

    render(<TestRecordDraftGenerationButton projectId="P1" ready />);

    fireEvent.click(screen.getByRole("button", { name: "Generate Test Record Draft" }));

    expect(await screen.findByText("Unable to generate Test Record draft. Confirm Matrix authority and try again.")).toBeTruthy();
  });
});
```

- [ ] **Step 2: Run button test and verify failure**

Run:

```powershell
cd frontend
npm test -- --run TestRecordDraftGenerationButton
```

Expected: FAIL because the component does not exist.

- [ ] **Step 3: Implement the button**

Create `frontend/src/features/project-workbench/TestRecordDraftGenerationButton.tsx`:

```tsx
import { useState, type ReactElement } from "react";
import { generateConfirmedMatrixTestRecordDraft } from "../../api/client";

type TestRecordDraftGenerationButtonProps = {
  projectId: string;
  ready: boolean;
};

export function TestRecordDraftGenerationButton({
  projectId,
  ready,
}: TestRecordDraftGenerationButtonProps): ReactElement {
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleGenerate(): Promise<void> {
    if (!ready || generating) {
      return;
    }
    setGenerating(true);
    setError(null);
    try {
      const blob = await generateConfirmedMatrixTestRecordDraft(projectId);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `${projectId}_test_record_draft.docx`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    } catch {
      setError("Unable to generate Test Record draft. Confirm Matrix authority and try again.");
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div className="runtime-console-test-record-generation">
      <button
        disabled={!ready || generating}
        onClick={() => void handleGenerate()}
        type="button"
      >
        {generating ? "Generating..." : "Generate Test Record Draft"}
      </button>
      {!ready ? (
        <p>Confirm Matrix authority before generating a Test Record draft.</p>
      ) : null}
      {error ? <p className="error">{error}</p> : null}
    </div>
  );
}
```

- [ ] **Step 4: Wire into Matrix projection panel**

In `ProjectWorkbenchMatrixProjectionPanel.tsx`, import:

```tsx
import { TestRecordDraftGenerationButton } from "./TestRecordDraftGenerationButton";
```

In the projection header, render:

```tsx
<TestRecordDraftGenerationButton projectId={projectId} ready={state === "ready" && !!viewModel} />
```

Place it in the header action area so it is visibly tied to active ConfirmedMatrix projection, not to inactive mock step controls.

- [ ] **Step 5: Add styles**

In `frontend/src/workbench.css`, add near matrix projection rules:

```css
.runtime-console-test-record-generation {
  display: grid;
  justify-items: end;
  gap: 4px;
}

.runtime-console-test-record-generation button {
  border: 1px solid var(--color-primary-strong);
  border-radius: 8px;
  background: var(--color-primary-strong);
  color: var(--color-surface);
  padding: 8px 12px;
  font-weight: 700;
}

.runtime-console-test-record-generation button:disabled {
  border-color: var(--color-border);
  background: var(--color-surface-muted);
  color: var(--color-ink-muted);
}

.runtime-console-test-record-generation p {
  margin: 0;
  color: var(--color-ink-muted);
  font-size: 12px;
}
```

- [ ] **Step 6: Run frontend tests**

Run:

```powershell
cd frontend
npm test -- --run TestRecordDraftGenerationButton
npm test -- --run ProjectWorkbenchMatrixProjectionPanel
```

Expected: PASS.

---

### Task 7: Add Static Guards

**Files:**

- Modify: `tests/unit/test_frontend_shell_files.py`

- [ ] **Step 1: Add TASK_271 guard**

Append near TASK_270 guard:

```python
def test_task271_test_record_word_generation_v1_is_wired() -> None:
    api_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(encoding="utf-8")
    projection_source = (
        FRONTEND_ROOT
        / "src"
        / "features"
        / "project-workbench"
        / "ProjectWorkbenchMatrixProjectionPanel.tsx"
    ).read_text(encoding="utf-8")
    button_source = (
        FRONTEND_ROOT
        / "src"
        / "features"
        / "project-workbench"
        / "TestRecordDraftGenerationButton.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(encoding="utf-8")
    lower_button = button_source.lower()

    assert "generateConfirmedMatrixTestRecordDraft" in api_source
    assert "/confirmed-matrix/test-record-draft/generate" in api_source
    assert "TestRecordDraftGenerationButton" in projection_source
    assert "Generate Test Record Draft" in button_source
    assert "Confirm Matrix authority before generating a Test Record draft." in button_source
    assert "runtime-console-test-record-generation" in styles_source
    for forbidden_copy in ["report", "fee", "ai review", "ai recommendation", "equipment", "permission"]:
        assert forbidden_copy not in lower_button
```

Add backend route static guard if a backend shell guard section already exists:

```python
    backend_root = FRONTEND_ROOT.parent / "backend"
    route_source = (backend_root / "api" / "routes_confirmed_matrix_test_record_generation.py").read_text(
        encoding="utf-8"
    )
    assert "FileResponse" in route_source
    assert "ConfirmedMatrixTestRecordDocumentGenerationService" in route_source
```

- [ ] **Step 2: Run static guard**

Run:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task271 or task270 or task269 or project_workbench"
```

Expected: PASS.

---

### Task 8: Full Verification

**Files:**

- No code changes unless verification exposes a defect.

- [ ] **Step 1: Backend unit and integration**

Run:

```powershell
py -m pytest tests\unit\test_confirmed_matrix_test_record_document_generation_service.py -q
py -m pytest tests\unit\test_test_record_document_gateway.py -q
py -m pytest tests\integration\test_confirmed_matrix_test_record_generation_api.py -q
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
```

Expected: all pass.

- [ ] **Step 2: Frontend tests and build**

Run:

```powershell
cd frontend
npm test -- --run TestRecordDraftGenerationButton
npm test -- --run ProjectWorkbenchMatrixProjectionPanel
npm run build
```

Expected: all pass.

- [ ] **Step 3: Static guard and whitespace check**

Run:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task271 or task270 or task269 or project_workbench"
git diff --check
```

Expected: guard passes; `git diff --check` has no whitespace errors. Existing CRLF warnings are acceptable if they match repository baseline.

---

### Task 9: Update Task State After Implementation

**Files:**

- Modify: `tasks/TASK_271_TEST_RECORD_WORD_GENERATION_V1.md`
- Modify: `docs/task_board.md`
- Modify: `docs/task_plan_index.md`

- [ ] **Step 1: Mark the task file complete**

In `tasks/TASK_271_TEST_RECORD_WORD_GENERATION_V1.md`, update:

```md
## Status

Planned. Awaiting user approval before implementation.
```

to:

```md
## Status

Complete.
```

Add implementation summary and validation results from Task 8.

- [ ] **Step 2: Mark the board complete**

In `docs/task_board.md`, update:

```md
> Current Active Task: TASK_271_TEST_RECORD_WORD_GENERATION_V1 (planned; executable plan created, awaiting user approval before implementation).
```

to:

```md
> Current Active Task: none (`TASK_271_TEST_RECORD_WORD_GENERATION_V1` complete; awaiting next approved task).
```

Add a TASK_271 completion note with deliverables, validation, and scope boundary.

- [ ] **Step 3: Mark plan index complete**

In `docs/task_plan_index.md`, update current active planned task plan to `none` and latest completed task plan history to:

```text
docs/task_271_test_record_word_generation_v1_plan.md
```

---

## Self-Review Checklist

- [ ] The plan generates from active ConfirmedMatrix only.
- [ ] The plan does not generate from SourceMatrix, ProjectMatrixDraft, frontend state, or unconfirmed preview.
- [ ] Word writing stays inside `backend/infrastructure/office`.
- [ ] API route calls application service only.
- [ ] Frontend calls API only through `frontend/src/api/client.ts`.
- [ ] UI copy is operational and does not expose future-scope features.
- [ ] Manual execution fields remain blank.
- [ ] Tests cover selected-groups-only output.
- [ ] No database migration, StepInstance, report, fee, AI, equipment, permission, or generation history scope is introduced.

## Approval Gate

Stop here. Do not implement until the user explicitly approves TASK_271 execution.
