# TASK_281 Test Record Header Metadata Fill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fill the approved Test Record Word template header fields from project/LTR/application-form authority data while leaving Estimated Completion Date blank.

**Architecture:** Keep the existing TASK_280 generation path: API route -> application service -> infrastructure Word gateway. Add a small application-layer metadata resolution step, pass a typed header metadata object into the writer, and keep all Word manipulation inside the infrastructure gateway.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy repositories, python-docx, pytest.

---

## Current Phase And Task Gate

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task before approval: none.
- Proposed task: `TASK_281_TEST_RECORD_HEADER_METADATA_FILL`.
- Allowed reason: TASK_280 is complete and user requested the next controlled Test Record Word-generation refinement.

Do not implement until the user explicitly approves TASK_281 execution and `docs/task_board.md` remains consistent.

## Task Understanding

Input:

- Active ConfirmedMatrix preview groups from TASK_280.
- Project record.
- Registered LTR record.
- Intake/application-form authority data containing applicable specification.
- Approved Word template:

```text
D:\Source\Office Auto\TestDocument\Template\FDQF-E-036 Test Record Template-Even.docx
```

Output:

- Generated Test Record `.docx` with these header values filled:
  - Lab Test Request Number
  - Product Description
  - Applicable Specification

Explicit non-output:

- Estimated Completion Date remains blank.

## Files And Responsibilities

- `backend/application/confirmed_matrix_test_record_document_generation_service.py`
  - Define `TestRecordHeaderMetadata`.
  - Resolve metadata before writer call.
  - Extend writer protocol signature.

- `backend/infrastructure/office/test_record_document_gateway.py`
  - Accept `header_metadata`.
  - Locate header value cells by label text.
  - Fill only the three allowed header values.
  - Preserve Estimated Completion Date blank.

- `backend/api/dependencies.py`
  - Wire any additional repositories required by the service.

- `backend/infrastructure/storage/repositories/intake_package.py`
  - Add a narrow lookup only if needed to find the confirmed intake case/draft for a project.

- `tests/unit/test_test_record_document_gateway.py`
  - Verify header table filling directly against a template fixture.

- `tests/unit/test_confirmed_matrix_test_record_document_generation_service.py`
  - Verify metadata resolution and writer call payload.

- `tests/integration/test_confirmed_matrix_test_record_generation_api.py`
  - Verify downloaded `.docx` contains header values.

## Data Contracts

Add:

```python
@dataclass(frozen=True, slots=True)
class TestRecordHeaderMetadata:
    lab_test_request_number: str = ""
    product_description: str = ""
    applicable_specification: str = ""
```

Extend the writer protocol:

```python
def generate_from_confirmed_matrix(
    self,
    *,
    template_path: Path,
    output_path: Path,
    project_id: str,
    project_no: str,
    product_description: str,
    applicable_specification: str,
    confirmed_matrix_id: str,
    groups: tuple,
    header_metadata: TestRecordHeaderMetadata,
) -> Path:
    ...
```

Keep the legacy `product_description` / `applicable_specification` parameters only if they are still used by existing tests during migration; otherwise route all header fill through `header_metadata`.

## Metadata Resolution Rules

### Lab Test Request Number

- Load `LtrRecordRepository.list_by_project(project_id)`.
- Select registered records:

```python
ltr.status is LtrStatus.REGISTERED
```

- Use the latest registered record by `registered_on`, then `ltr_number`.
- If no registered LTR exists, use `""`.

### Product Description

- Parse selected LTR record `notes` as JSON.
- Use `sample_description` when present and non-empty.
- Fallback to `project.product_name`.
- If still missing, use `""`.

### Applicable Specification

Preferred:

- Find the confirmed intake case for the project.
- Load its intake draft.
- Parse `requested_testing_json`.
- Collect non-empty `applicable_specification` values in source order.
- Deduplicate while preserving order.
- Join with `; `.

Fallback:

- Use application-form `requested_testing` only when deterministic specification tokens can be extracted (for example `EIA-`, `GS-`, `QG-`, `IEC`, `ASTM`, `UL` pattern tokens).
- Otherwise use `""`.

Strict guard:

- Do not use broad free-text heuristic matching that can map narrative testing descriptions into specification header output.

## Implementation Tasks

### Task 1: Add Writer Header Fill Test

**Files:**

- Modify: `tests/unit/test_test_record_document_gateway.py`

- [ ] **Step 1: Add a template fixture with header tables**

Create a helper that builds:

```python
def _build_template_with_header(path: Path) -> Path:
    document = Document()
    section = document.sections[0]
    header = section.header
    table0 = header.add_table(rows=1, cols=3, width=Inches(7))
    table0.cell(0, 2).text = "Lab Test Request Number:\n实验室测试项目编号："
    table1 = header.add_table(rows=1, cols=6, width=Inches(7))
    table1.cell(0, 0).text = "Product Description\n产品描述"
    table1.cell(0, 2).text = "Applicable Specification\n适用的规范"
    table1.cell(0, 4).text = "Estimated Completion Date\n预计完成日期"
    document.add_paragraph("Group Number 组别编号: # ;   Sample Quantity & Number 样品数量及编号: #")
    step_table = document.add_table(rows=1, cols=9)
    step_table.rows[0].cells[0].text = "Step"
    equipment_table = document.add_table(rows=1, cols=7)
    equipment_table.rows[0].cells[0].text = "Equipment"
    document.save(path)
    return path
```

- [ ] **Step 2: Add failing assertion**

Expected test shape:

```python
def test_gateway_fills_test_record_header_metadata(tmp_path: Path) -> None:
    template = _build_template_with_header(tmp_path / "template.docx")
    output = tmp_path / "record.docx"

    TestRecordDocumentGateway().generate_from_confirmed_matrix(
        template_path=template,
        output_path=output,
        project_id="P1",
        project_no="DL-2026-05-003",
        product_description="legacy",
        applicable_specification="legacy",
        confirmed_matrix_id="cmv-1",
        groups=(_ConfirmedGroup(),),
        header_metadata=TestRecordHeaderMetadata(
            lab_test_request_number="DL-2026-05-003",
            product_description="Coolpower HDF 3.40mm pin",
            applicable_specification="GS-12-1507",
        ),
    )

    document = Document(output)
    header_tables = document.sections[0].header.tables
    assert "DL-2026-05-003" in header_tables[0].cell(0, 2).text
    assert header_tables[1].cell(0, 1).text == "Coolpower HDF 3.40mm pin"
    assert header_tables[1].cell(0, 3).text == "GS-12-1507"
    assert header_tables[1].cell(0, 5).text == ""
```

- [ ] **Step 3: Run the failing test**

Run:

```powershell
py -m pytest tests\unit\test_test_record_document_gateway.py -q
```

Expected: fail because `header_metadata` and header filling do not exist yet.

### Task 2: Implement Word Header Filling

**Files:**

- Modify: `backend/infrastructure/office/test_record_document_gateway.py`
- Modify: `backend/application/confirmed_matrix_test_record_document_generation_service.py`

- [ ] **Step 1: Add `TestRecordHeaderMetadata` dataclass**

Place it in the application service module so application and infrastructure can share the payload without introducing a domain object for a derived Word output.

- [ ] **Step 2: Update writer protocol and gateway signature**

Add `header_metadata: TestRecordHeaderMetadata` to both the protocol and gateway method.

- [ ] **Step 3: Fill header cells by label**

Implement helpers in the gateway:

```python
def _fill_header_metadata(document: Document, metadata: TestRecordHeaderMetadata) -> None:
    for section in document.sections:
        _fill_lab_test_request_number(section.header, metadata.lab_test_request_number)
        _fill_labeled_header_value(
            section.header,
            label_tokens=("product description", "产品描述"),
            value=metadata.product_description,
        )
        _fill_labeled_header_value(
            section.header,
            label_tokens=("applicable specification", "适用的规范"),
            value=metadata.applicable_specification,
        )
        _clear_labeled_header_value(
            section.header,
            label_tokens=("estimated completion date", "预计完成日期"),
        )
```

Rules:

- For label/value rows, write to the next cell to the right of the matched label cell.
- For Lab Test Request Number, do not destroy the existing label text. Update only value run/placeholder region, or append value text while preserving existing label runs and formatting.
- Do not write placeholder text when the metadata value is blank.
- Do not use whole-cell replacement (`cell.text = ...`) on labeled header cells.

- [ ] **Step 4: Run writer tests**

Run:

```powershell
py -m pytest tests\unit\test_test_record_document_gateway.py -q
```

Expected: pass.

### Task 3: Resolve Header Metadata In Application Service

**Files:**

- Modify: `backend/application/confirmed_matrix_test_record_document_generation_service.py`
- Modify: `backend/api/dependencies.py`
- Modify: `backend/infrastructure/storage/repositories/intake_package.py` only if needed

- [ ] **Step 1: Add repository protocols and explicit lookup boundary**

Add narrow protocols:

```python
class LtrRecordLookup(Protocol):
    def list_by_project(self, project_id: str):
        """Return LTR records linked to a project."""

class ApplicationFormLookup(Protocol):
    def list_by_project(self, project_id: str):
        """Return application forms linked to a project."""
```

If intake draft requested-testing rows are needed:

```python
class IntakeCaseLookup(Protocol):
    def get_by_confirmed_project(self, project_id: str):
        """Return the intake case that confirmed this project."""

class IntakeDraftLookup(Protocol):
    def get_by_case(self, case_id: str):
        """Return the draft for one intake case."""
```

Repository note:

- Current `IntakeDraftRepository` already supports `get_by_case`.
- Add a narrow confirmed-project intake-case lookup (for example in `IntakeCaseRepository`) instead of ad hoc SQL in the generation service.
- Keep data traversal explicit: `project_id -> confirmed intake case -> intake draft -> requested_testing_json`.

- [ ] **Step 2: Add `_resolve_header_metadata(project_id, project)`**

Algorithm:

1. Find registered LTR.
2. Parse `ltr.notes` JSON.
3. Resolve:
   - `lab_test_request_number`
   - `product_description`
   - `applicable_specification`
4. Return `TestRecordHeaderMetadata`.

- [ ] **Step 3: Pass metadata to writer**

Add:

```python
header_metadata = self._resolve_header_metadata(command.project_id, project)
```

and pass `header_metadata=header_metadata` into `generate_from_confirmed_matrix`.

### Task 4: Add Service Tests

**Files:**

- Modify: `tests/unit/test_confirmed_matrix_test_record_document_generation_service.py`

- [ ] **Step 1: Verify metadata payload passed to writer**

Test data:

- Project `product_name="fallback product"`.
- Registered LTR:

```python
notes='{"sample_description":"Coolpower HDF 3.40mm pin"}'
```

- Applicable specification source: `GS-12-1507`.

Assertion:

```python
assert writer.calls[0]["header_metadata"].lab_test_request_number == "DL-2026-05-003"
assert writer.calls[0]["header_metadata"].product_description == "Coolpower HDF 3.40mm pin"
assert writer.calls[0]["header_metadata"].applicable_specification == "GS-12-1507"
```

- [ ] **Step 2: Verify missing values are blank/non-blocking**

Use no LTR, no spec source:

```python
assert writer.calls[0]["header_metadata"].lab_test_request_number == ""
assert writer.calls[0]["header_metadata"].applicable_specification == ""
```

Run:

```powershell
py -m pytest tests\unit\test_confirmed_matrix_test_record_document_generation_service.py -q
```

Expected: pass.

### Task 5: Add Integration Test

**Files:**

- Modify: `tests/integration/test_confirmed_matrix_test_record_generation_api.py`

- [ ] **Step 1: Seed registered LTR + application-form/spec data**

Add or extend fixture setup so project `P1` has:

```text
LTR: DL-2026-05-003
LTR notes sample_description: Coolpower HDF 3.40mm pin
Applicable Specification: GS-12-1507
```

- [ ] **Step 2: Assert downloaded DOCX header fields**

After writing `response.content` to `downloaded.docx`:

```python
document = Document(output)
header_tables = document.sections[0].header.tables
header_text = "\n".join(
    cell.text
    for table in header_tables
    for row in table.rows
    for cell in row.cells
)
assert "DL-2026-05-003" in header_text
assert "Coolpower HDF 3.40mm pin" in header_text
assert "GS-12-1507" in header_text
assert "Estimated Completion Date" in header_text
assert "2026" not in header_tables[1].cell(0, 5).text
```

Run:

```powershell
py -m pytest tests\integration\test_confirmed_matrix_test_record_generation_api.py -q
```

Expected: pass.

### Task 6: Validation And Documentation Sync

**Files:**

- Modify: `tasks/TASK_281_TEST_RECORD_HEADER_METADATA_FILL.md`
- Modify: `docs/task_board.md`
- Modify: `docs/task_plan_index.md`

- [ ] **Step 1: Run targeted validation**

```powershell
py -m pytest tests\unit\test_test_record_document_gateway.py -q
py -m pytest tests\unit\test_confirmed_matrix_test_record_document_generation_service.py -q
py -m pytest tests\integration\test_confirmed_matrix_test_record_generation_api.py -q
git diff --check
```

- [ ] **Step 2: Update task status after implementation**

Only after tests pass:

- `tasks/TASK_281_TEST_RECORD_HEADER_METADATA_FILL.md` -> Complete.
- `docs/task_board.md` -> TASK_281 complete, Current Active Task none.
- `docs/task_plan_index.md` -> latest completed plan TASK_281.

## Risks And Controls

- Risk: header table position differs across template revisions.
  - Control: fill by label matching first; indexes are fallback only.

- Risk: Product Description accidentally uses `Project.product_name` instead of LTR `Sample Description`.
  - Control: unit test with different values proves LTR note sample description wins.

- Risk: Applicable Specification source is not available for older projects.
  - Control: blank value is non-blocking and tested.

- Risk: Estimated Completion Date gets accidentally populated.
  - Control: writer and integration tests assert it stays blank.

## Validation Commands

```powershell
py -m pytest tests\unit\test_test_record_document_gateway.py -q
py -m pytest tests\unit\test_confirmed_matrix_test_record_document_generation_service.py -q
py -m pytest tests\integration\test_confirmed_matrix_test_record_generation_api.py -q
git diff --check
```

## Self-Review

- Spec coverage: covers LTR number, Product Description from Sample Description, Applicable Specification, and keeps Estimated Completion Date blank.
- Placeholder scan: no TBD/TODO implementation placeholders.
- Type consistency: `TestRecordHeaderMetadata` is the single payload shared from application service to writer.

## Execution Handoff

Plan complete and saved to `docs/task_281_test_record_header_metadata_fill_plan.md`.

Recommended execution mode: `superpowers:executing-plans`, serially, because this is a narrow Word-template behavior task where each test should be reviewed before moving to the next step.
