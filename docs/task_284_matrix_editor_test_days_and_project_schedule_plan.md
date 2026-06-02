# TASK_284 Matrix Editor Test Days And Project Schedule Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Also read `docs/project_management/TASK_EXECUTION_SKILL.md` before implementation and execute `docs/project_management/TASK_REVIEW_CHECKLIST.md` before completion.

**Goal:** Add Matrix Editor planned test-day estimation and project schedule planning fields that persist through draft save and Confirm Matrix.

**Architecture:** Treat test days and schedule dates as Matrix planning authority data, not execution data. Persist row-level `day_expression` with Matrix draft/confirmed rows and root-level planned schedule fields with Matrix draft/confirmed root records. Keep calculations deterministic in frontend selectors and backend validation helpers so downstream document tasks can reuse the confirmed values later.

**Tech Stack:** Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.x, SQLite, React + TypeScript, Vitest, pytest.

---

## 1. Task Identity

- Task: `TASK_284_MATRIX_EDITOR_TEST_DAYS_AND_PROJECT_SCHEDULE_PLAN`
- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Plan status: Complete.
- Execution mode: `superpowers:executing-plans` (serial, reviewable)

## 2. Why This Task Is Allowed Now

`docs/task_board.md` marks `TASK_284_MATRIX_EDITOR_TEST_DAYS_AND_PROJECT_SCHEDULE_PLAN` complete. The user approved the task before implementation.

## 3. Business Context

The lab needs to estimate project duration before test execution starts. The Matrix already defines which groups and steps must be tested; therefore the planned duration belongs next to the Matrix, not in a separate free-form note.

Planned dates are used by downstream outputs such as application form `SECTION 2`:

- `Date Lab Received Samples`
- `Estimated Completion Date`

These are planning values. Future actual dates may be earlier or later and must be recorded separately when execution/reporting scope is approved.

## 4. Scope Control

### In Scope

1. Add Matrix Editor `Day` row field after `Requirement`.
2. Add deterministic per-group `Test Days` calculation.
3. Add project schedule planning card.
4. Add planned date fields and validation.
5. Persist planning fields through draft save and Confirm Matrix.
6. Expose planning fields through existing Matrix draft/session/confirmed snapshot DTOs.
7. Add backend and frontend tests.

### Out Of Scope

1. No actual execution dates.
2. No StepInstance or execution persistence.
3. No evidence/image workflow.
4. No Test Record or report generation changes.
5. No Word `SECTION 2` writeback.
6. No fee engine.
7. No AI estimation.
8. No new standalone schedule page.

## 5. Fixed Data Contract

### 5.1 Row Field

Add `day_expression` to:

- `ProjectMatrixDraftRow`
- `ConfirmedMatrixRow`
- API DTOs:
  - `ProjectMatrixDraftRow`
  - `ProjectMatrixDraftSaveRowInput`
  - `MatrixEditorSessionRowResponse`
  - `MatrixEditorSessionRowRequest`
  - `ConfirmedMatrixRow`
  - active snapshot response rows

Accepted value:

```text
null | "" | decimal | decimal + "x"
```

Examples:

```text
1
0.1
2.5
0.5x
2x
```

### 5.2 Root Schedule Fields

Add planning root fields to draft root and confirmed authority root:

```text
pre_test_buffer_days
post_test_buffer_days
sample_received_date
planned_test_start_date
planned_test_complete_date
estimated_completion_date
```

Recommended storage:

- buffer days as nullable text or decimal-compatible string in API/domain if the project currently avoids numeric decimal columns.
- dates as ISO `YYYY-MM-DD` strings.
- four planned date fields render as native `<input type="date" />` controls in Matrix Editor.

Implementation may use SQLAlchemy `String` columns for dates and buffer values to stay consistent with existing text-first matrix persistence, but parsing/validation must treat buffer values as decimal numbers.

Buffer field contract:

- `pre_test_buffer_days` and `post_test_buffer_days` empty values mean `0` while editing and confirming.
- accepted values are non-negative decimal numbers only.
- negative values, non-numeric values, and multiplier suffix `x` are invalid.
- invalid buffer values highlight red and block `Confirm Matrix`.

### 5.3 Calculation Rules

For each selected group:

```text
group_test_days = sum(row_day_contribution(row, group_cell))
```

For each row/group:

```text
if day_expression is empty:
    contribution = 0
if day_expression is decimal:
    contribution = decimal when group cell contains at least one token, else 0
if day_expression is decimal + "x":
    contribution = decimal * token_count(group cell)
```

Token count must align with Matrix Editor's existing step token parsing.

Critical group:

```text
critical_group = selected group with maximum group_test_days
```

Total planned project cycle:

```text
total_cycle_days = pre_test_buffer_days + max_group_test_days + post_test_buffer_days
```

V1 uses calendar days only. It does not skip weekends, public holidays, or lab blackout dates.

Date sufficiency validation uses calendar-day ceiling for decimal planned days:

- `ceil()` is applied only when comparing date-only fields.
- `2.5` planned days requires at least `3` calendar days.
- `0.1` planned days requires at least `1` calendar day when a date sufficiency check is active.
- Visible `Test Days` summaries remain decimal and are not rounded.

### 5.4 Date Validation

The frontend and backend must enforce:

```text
planned_test_start_date >= sample_received_date + pre_test_buffer_days
planned_test_complete_date >= planned_test_start_date + critical_group_test_days
estimated_completion_date >= planned_test_complete_date + post_test_buffer_days
estimated_completion_date >= sample_received_date + total_cycle_days
```

Invalid fields:

- Red highlight in Matrix Editor.
- `Confirm Matrix` disabled.
- Backend returns typed validation error if an invalid payload reaches the API.

Empty date policy:

- Dates may be empty during editing.
- Confirm Matrix requires either all four planned dates are empty or all four are valid.
- If any planned date is filled, all four planned dates are required.

Draft save versus confirm policy:

- Draft save may preserve transient invalid `Day`, buffer, or date strings so the operator can finish editing values such as `0.` without creating auto-save errors.
- Matrix Editor should still highlight invalid values and disable `Confirm Matrix`.
- `Confirm Matrix` is the authoritative validation gate.
- Backend session confirm/publish must reject invalid planning fields with typed validation detail.
- Backend draft save should persist planning strings without applying strict schedule validation, except for structural payload sanity such as missing row ids.

UI control policy:

- Use native `<input type="date" />` for all four planned date fields.
- Do not introduce a custom calendar library in this task.
- Add a frontend test asserting each planned date field renders as `type="date"`.

### 5.5 Information And Sample Row Behavior

`Day` applies only to real Test Item rows.

- Information rows created by `Mark as Information` do not contribute test days.
- Sample quantity rows do not contribute test days.
- Information/sample rows must not block `Confirm Matrix` because of empty or invalid `Day` values.
- The UI may hide `Day` editing for those rows or ignore their values, but the behavior must be deterministic and covered by tests.

## 6. File-Level Change Plan

### Backend Domain And Storage

Modify:

- `backend/domain/project_matrix_draft_models.py`
- `backend/domain/confirmed_matrix_authority_models.py`
- `backend/infrastructure/storage/models_project_matrix_draft.py`
- `backend/infrastructure/storage/models_confirmed_matrix_authority.py`
- `backend/infrastructure/storage/repositories/project_matrix_draft.py`
- `backend/infrastructure/storage/repositories/confirmed_matrix_authority.py`
- `backend/infrastructure/storage/database.py`

Implementation must include lightweight existing-SQLite schema upgrade or ensure-column handling for all new nullable columns. This is required because local offline databases may already contain the old Matrix draft/confirmed authority tables.

Add helper:

- `backend/application/matrix_schedule_planning.py`

Responsibility:

- Parse `day_expression`.
- Count Matrix step tokens.
- Calculate per-group test days.
- Validate schedule date order and cycle sufficiency.

### Backend Services And API

Modify:

- `backend/application/project_matrix_draft_persistence_service.py`
- `backend/application/confirmed_matrix_authority_service.py`
- `backend/application/matrix_editor_session_service.py`
- `backend/api/routes_matrix_editor_session.py`
- `backend/api/routes_project_matrix_drafts.py`

Ensure:

- Draft save preserves planning fields.
- Session seed returns planning fields.
- Draft save may preserve transient invalid planning strings.
- Confirm session accepts valid planning fields and rejects invalid planning fields.
- Confirmed Matrix snapshot returns planning fields.

### Frontend API And State

Modify:

- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`

Create component:

- `frontend/src/features/matrix-editor/MatrixSchedulePlanningCard.tsx`

Add selector/helper:

- `frontend/src/features/matrix-editor/matrixSchedulePlanning.ts`

Responsibility:

- Parse day expressions.
- Count tokens from group cell text.
- Calculate group totals.
- Validate date sequence.
- Return UI-friendly invalid field ids.

### Frontend Styling

Modify:

- `frontend/src/workbench.css`

Add:

- Day column sizing.
- `Test Days` summary row styling.
- schedule card compact layout.
- invalid date/day input red highlight.

### Tests

Backend:

- `tests/unit/test_matrix_schedule_planning.py`
- `tests/unit/test_project_matrix_draft_persistence_service.py`
- `tests/unit/test_confirmed_matrix_authority_service.py`
- `tests/integration/test_matrix_editor_session_api.py`
- `tests/integration/test_confirmed_matrix_authority_api.py`

Frontend:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/features/matrix-editor/MatrixSchedulePlanningCard.test.tsx`
- `frontend/src/features/matrix-editor/matrixSchedulePlanning.test.ts`

Static guard:

- `tests/unit/test_frontend_shell_files.py`

## 7. Implementation Tasks

### Task 1: Backend schedule helper tests

**Files:**

- Create: `tests/unit/test_matrix_schedule_planning.py`
- Create: `backend/application/matrix_schedule_planning.py`

- [ ] **Step 1: Write failing parser tests**

Add tests for accepted expressions:

```python
from decimal import Decimal

from backend.application.matrix_schedule_planning import parse_day_expression


def test_parse_plain_decimal_day_expression() -> None:
    parsed = parse_day_expression("0.5")
    assert parsed.multiplier is False
    assert parsed.value == Decimal("0.5")


def test_parse_multiplier_day_expression() -> None:
    parsed = parse_day_expression("0.5x")
    assert parsed.multiplier is True
    assert parsed.value == Decimal("0.5")
```

- [ ] **Step 2: Write failing invalid expression tests**

```python
import pytest

from backend.application.matrix_schedule_planning import MatrixScheduleValidationError, parse_day_expression


@pytest.mark.parametrize("value", ["abc", "x", "0.x", "-1", "1xx"])
def test_parse_rejects_invalid_day_expression(value: str) -> None:
    with pytest.raises(MatrixScheduleValidationError):
        parse_day_expression(value)
```

- [ ] **Step 3: Write failing group calculation tests**

```python
from decimal import Decimal

from backend.application.matrix_schedule_planning import calculate_group_test_days


def test_multiplier_day_expression_counts_group_tokens() -> None:
    rows = [
        {"row_id": "r1", "day_expression": "0.5x"},
    ]
    cells = [
        {"row_id": "r1", "group_id": "g1", "cell_value": "2,7"},
    ]
    totals = calculate_group_test_days(rows=rows, cells=cells, selected_group_ids=["g1"])
    assert totals["g1"] == Decimal("1.0")
```

- [ ] **Step 4: Implement minimal helper**

Implement:

```python
@dataclass(frozen=True, slots=True)
class ParsedDayExpression:
    value: Decimal
    multiplier: bool
```

and functions:

```python
def parse_day_expression(value: str | None) -> ParsedDayExpression | None: ...
def count_step_tokens(cell_value: str | None) -> int: ...
def calculate_group_test_days(...): ...
def validate_planned_schedule(...): ...
```

- [ ] **Step 5: Run helper tests**

Run:

```powershell
py -m pytest tests/unit/test_matrix_schedule_planning.py -q
```

Expected: pass.

### Task 2: Persist planning fields in draft and confirmed authority

**Files:**

- Modify: `backend/domain/project_matrix_draft_models.py`
- Modify: `backend/domain/confirmed_matrix_authority_models.py`
- Modify: `backend/infrastructure/storage/models_project_matrix_draft.py`
- Modify: `backend/infrastructure/storage/models_confirmed_matrix_authority.py`
- Modify: `backend/infrastructure/storage/repositories/project_matrix_draft.py`
- Modify: `backend/infrastructure/storage/repositories/confirmed_matrix_authority.py`
- Modify: `backend/application/project_matrix_draft_persistence_service.py`
- Modify: `backend/application/confirmed_matrix_authority_service.py`

- [ ] **Step 1: Add failing draft persistence test**

Update `tests/unit/test_project_matrix_draft_persistence_service.py` so a saved draft row with `day_expression="0.5x"` reloads with the same value, and root schedule fields reload unchanged.

- [ ] **Step 2: Add failing confirmed authority test**

Update `tests/unit/test_confirmed_matrix_authority_service.py` so confirming a draft preserves `day_expression` and root schedule fields in active confirmed snapshot.

- [ ] **Step 3: Add domain fields**

Add:

```python
day_expression: str | None = None
```

to draft/confirmed row dataclasses.

Add root schedule fields to `ProjectMatrixDraftRecord` and `ConfirmedMatrixVersion`.

- [ ] **Step 4: Add SQLAlchemy columns**

Add nullable columns to root and row models.

- [ ] **Step 5: Add existing-SQLite ensure-column coverage**

Add a repository or integration test that creates/opens an old-schema SQLite database missing the new nullable columns, runs the database initialization/upgrade path, and verifies the new columns exist without dropping existing data.

- [ ] **Step 6: Update repository mapping**

Map every new field in model-to-domain and domain-to-model conversions.

- [ ] **Step 7: Run backend persistence tests**

Run:

```powershell
py -m pytest tests/unit/test_project_matrix_draft_persistence_service.py tests/unit/test_confirmed_matrix_authority_service.py -q
```

Expected: pass.

### Task 3: Extend Matrix Editor session API contract

**Files:**

- Modify: `backend/api/routes_matrix_editor_session.py`
- Modify: `backend/api/routes_project_matrix_drafts.py`
- Modify: `backend/application/matrix_editor_session_service.py`
- Modify: `frontend/src/api/client.ts`
- Modify: `tests/integration/test_matrix_editor_session_api.py`
- Modify: `tests/integration/test_confirmed_matrix_authority_api.py`

- [ ] **Step 1: Add failing API tests**

Add integration assertions:

- GET session returns row `day_expression`.
- POST session confirm accepts planning fields.
- Active confirmed snapshot returns planning fields.
- Invalid schedule returns typed 422 validation detail.

- [ ] **Step 2: Extend Pydantic DTOs**

Add `day_expression` to row request/response DTOs and schedule fields to session seed/confirm request DTOs.

- [ ] **Step 3: Wire service command fields**

Add the new fields to service command/dataclass conversions.

- [ ] **Step 4: Run API tests**

Run:

```powershell
py -m pytest tests/integration/test_matrix_editor_session_api.py tests/integration/test_confirmed_matrix_authority_api.py -q
```

Expected: pass.

### Task 4: Add frontend calculation helper

**Files:**

- Create: `frontend/src/features/matrix-editor/matrixSchedulePlanning.ts`
- Create: `frontend/src/features/matrix-editor/matrixSchedulePlanning.test.ts`

- [ ] **Step 1: Add failing helper tests**

Test:

- `0.5x` with `2,7` returns `1`.
- plain `1` with non-empty cell returns `1`.
- plain `1` with empty cell returns `0`.
- invalid dates are returned as invalid field ids.

- [ ] **Step 2: Implement helper**

Export:

```ts
export type MatrixScheduleValidation = {
  invalidDayRowIds: Set<string>;
  invalidDateFields: Set<string>;
  groupTotals: Record<string, number>;
  criticalGroupId: string | null;
  totalCycleDays: number | null;
};
```

and deterministic parse/calculate functions.

- [ ] **Step 3: Run helper tests**

Run:

```powershell
cd frontend; npm test -- --run matrixSchedulePlanning --watch=false
```

Expected: pass.

### Task 5: Add Matrix Editor UI fields

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- Create: `frontend/src/features/matrix-editor/MatrixSchedulePlanningCard.tsx`
- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- Create: `frontend/src/features/matrix-editor/MatrixSchedulePlanningCard.test.tsx`
- Modify: `frontend/src/workbench.css`

- [ ] **Step 1: Add failing UI tests**

Add tests that verify:

- `Day` header appears after `Requirement`.
- Editing `Day` updates `Test Days`.
- `0.5x` with two step tokens displays `1`.
- Invalid `Day` disables `Confirm Matrix`.
- planned date order violation highlights fields and disables `Confirm Matrix`.
- planned date fields render as native `input[type="date"]`.
- invalid buffer values disable `Confirm Matrix`.
- transient invalid planning strings can be saved/reloaded as draft values.
- Information rows and sample quantity rows do not contribute test days and do not block confirmation because of `Day`.

- [ ] **Step 2: Add row state field**

Extend frontend editable row type with:

```ts
dayExpression: string;
```

Load/save it from API `day_expression`.

- [ ] **Step 3: Render Day column**

Insert a compact input after `Requirement`.

- [ ] **Step 4: Render Test Days row**

Add bottom row below sample sizes/status-style rows in the Matrix edit table.

- [ ] **Step 5: Render schedule card**

Implement the card in `MatrixSchedulePlanningCard.tsx` and keep `MatrixEditorWorkspace.tsx` responsible only for state wiring and passing props.

Place a compact card near the Matrix editor bottom/action area, not above the main Matrix table. Include:

- Critical group.
- Max group test days.
- Pre-test buffer days input.
- Post-test buffer days input.
- Total planned cycle days.
- Four date inputs.

- [ ] **Step 6: Run Matrix Editor tests**

Run:

```powershell
cd frontend; npm test -- --run MatrixEditorWorkspace --watch=false
cd frontend; npm test -- --run MatrixSchedulePlanningCard --watch=false
```

Expected: pass.

### Task 6: Validation, guards, and docs

**Files:**

- Modify: `tests/unit/test_frontend_shell_files.py`
- Modify: `docs/task_board.md`
- Modify: `docs/task_plan_index.md`
- Modify: `tasks/TASK_284_MATRIX_EDITOR_TEST_DAYS_AND_PROJECT_SCHEDULE_PLAN.md`

- [ ] **Step 1: Add static guard**

Guard that Matrix Editor includes:

- `Day`
- `Test Days`
- `Project Schedule`
- planned date labels

and does not introduce actual execution terms such as `Actual completion` in this task.

- [ ] **Step 2: Run required validation**

Run:

```powershell
py -m pytest tests/unit/test_matrix_schedule_planning.py tests/unit/test_project_matrix_draft_persistence_service.py tests/unit/test_confirmed_matrix_authority_service.py -q
py -m pytest tests/integration/test_matrix_editor_session_api.py tests/integration/test_confirmed_matrix_authority_api.py -q
cd frontend; npm test -- --run matrixSchedulePlanning --watch=false
cd frontend; npm test -- --run MatrixSchedulePlanningCard --watch=false
cd frontend; npm test -- --run MatrixEditorWorkspace --watch=false
cd frontend; npm run build
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task284 or matrix_editor"
git diff --check
```

- [ ] **Step 3: Update task status**

After implementation and validation, update:

- `tasks/TASK_284_MATRIX_EDITOR_TEST_DAYS_AND_PROJECT_SCHEDULE_PLAN.md`
- `docs/task_board.md`
- `docs/task_plan_index.md`

## 8. Review Checklist Before Approval

Before approving implementation, confirm these product decisions:

1. Empty planned dates are allowed while editing.
2. Confirm Matrix requires either all planned dates empty or all four planned dates valid.
3. Word `SECTION 2` writeback is a later task that consumes confirmed planning fields.
4. Actual dates are a later execution/reporting task and must not overwrite planned dates.
5. `Day` values are row-level, not step-level.
6. Draft save may preserve transient invalid planning strings; Confirm Matrix is the strict validation gate.
7. Decimal planned days are rounded up only for date sufficiency checks.

## 9. Final Validation Expectations

Implementation is complete only when:

1. Backend tests pass.
2. Frontend tests pass.
3. Frontend build passes.
4. Static guard passes.
5. `git diff --check` reports no blocking whitespace errors.
6. No backend/API/DB changes outside the planned Matrix draft/confirmed authority planning fields.
7. No StepInstance or execution persistence appears in the diff.
