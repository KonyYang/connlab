# Lightweight Authority Change History Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a minimal read-only authority change history for ConfirmedMatrix revisions so the operator can see when active Matrix authority changed and whether a Test Record draft may need regeneration.

**Architecture:** Derive history from existing immutable ConfirmedMatrix snapshots. Add a repository project-list method, an application read service, one thin API route, a typed API client function, and a compact Project Workbench panel. Do not add a new history table or workflow model.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy repositories, Pydantic v2, React, TypeScript, Vitest, Testing Library, pytest.

---

## Anti-Skip Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_272_LIGHTWEIGHT_AUTHORITY_CHANGE_HISTORY` (planned)
- Allowed reason: `TASK_271_TEST_RECORD_WORD_GENERATION_V1` is complete, the task board has no active implementation task, and `docs/post_phase11_matrix_driven_laboratory_execution_workflow_guideline.md` names TASK_272 as the next Matrix-driven laboratory execution slice.

Implementation must wait for explicit user approval after this plan is reviewed.

## Required Project Protocol

Before implementation, use:

- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `$impeccable` product context for the frontend history view and status copy

## Product / UI Context

ConnLab is a `product` UI. The operator is a lab coordinator on an offline Windows workstation. They have confirmed Matrix authority, may have generated a Word Test Record draft, and need a quick answer to: "Has the authority changed since then?"

UI constraints:

- Authority first, derived output second.
- History is read-only visibility, not a workflow.
- Use compact operational copy.
- No approval, permission, report, fee, AI, equipment, or execution-data expansion.
- No action buttons in the history panel.

## Scope Boundary

In scope:

- Read-only project authority history from ConfirmedMatrix snapshots.
- Lightweight adjacent revision comparison.
- API endpoint returning typed history entries.
- Project Workbench compact read-only panel.
- Tests and static guards.

Out of scope:

- Permission or approval workflow.
- StepInstance / execution persistence.
- LLCR runtime persistence.
- Formal TestRecord aggregate.
- Test Record generation ledger.
- Report, fee, AI, equipment, or evidence features.
- Full diff viewer.
- Multi-Matrix append/merge history.
- Mutating authority from Project Workbench.

## Existing Baseline

Observed implementation facts:

- `ConfirmedMatrixVersion` already stores `confirmed_revision`, active/superseded state, `confirmed_by`, `confirmed_at`, and supersession metadata.
- `ConfirmedMatrixAuthorityRepository` can load a single snapshot and the active snapshot, but does not yet expose all project revisions.
- `MatrixRevisionFlowService` confirms revision drafts by superseding the previous active authority and creating a new snapshot.
- Project Workbench already renders confirmed Matrix projection and the TASK_271 generation action from `frontend/src/api/client.ts`.

Design implication:

- TASK_272 should not create a new history table. It should add `list_by_project(project_id)` and derive history from snapshots.

## File Structure

Create:

- `backend/application/confirmed_matrix_authority_history_service.py`
  - Owns history derivation and adjacent snapshot comparison.
  - Returns application-owned dataclasses.
  - Knows nothing about API/Pydantic or ORM models.

- `backend/api/routes_confirmed_matrix_authority_history.py`
  - Adds `GET /api/projects/{project_id}/confirmed-matrix/authority-history`.
  - Maps application dataclasses to Pydantic responses.
  - Returns `entries: []` for no confirmed history.

- `frontend/src/features/project-workbench/AuthorityChangeHistoryPanel.tsx`
  - Fetches and renders compact read-only history.
  - Shows loading, empty, ready, and error states.
  - Contains no mutation controls.

- `frontend/src/features/project-workbench/AuthorityChangeHistoryPanel.test.tsx`
  - Covers ready history, empty state, regeneration warning, and no-button constraint.

- `tests/unit/test_confirmed_matrix_authority_history_service.py`
  - Covers initial event, active revision change counts, source changes, and regeneration recommendation.

- `tests/integration/test_confirmed_matrix_authority_history_api.py`
  - Seeds confirm + revision flow and validates API response ordering and fields.

Modify:

- `backend/infrastructure/storage/repositories/confirmed_matrix_authority.py`
  - Add `list_by_project(project_id)` ordered by `confirmed_revision.asc()`.

- `backend/api/dependencies.py`
  - Wire `ConfirmedMatrixAuthorityHistoryService`.

- `backend/api/main.py`
  - Include the new route.

- `frontend/src/api/client.ts`
  - Add `ConfirmedMatrixAuthorityHistory` types and `fetchConfirmedMatrixAuthorityHistory(projectId)`.

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
  - Render `AuthorityChangeHistoryPanel` near confirmed Matrix projection context.

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`
  - Assert the history panel is present without adding action controls.

- `frontend/src/workbench.css`
  - Add compact timeline/list styles.

- `tests/unit/test_frontend_shell_files.py`
  - Add TASK_272 guards for API client boundary, no `<button>` in history component, and no forbidden action copy.

- `docs/task_board.md`, `docs/task_plan_index.md`, `tasks/TASK_272_LIGHTWEIGHT_AUTHORITY_CHANGE_HISTORY.md`
  - Update after implementation and validation.

---

### Task 1: Add Backend History Service Tests

**Files:**

- Create: `tests/unit/test_confirmed_matrix_authority_history_service.py`
- Create later: `backend/application/confirmed_matrix_authority_history_service.py`

- [ ] **Step 1: Write failing service tests**

Cover:

- Initial confirmation produces one entry with `change_summary` indicating initial authority.
- Revision 2 with same source but changed group/row/cell counts reports group/step/token changes.
- Revision with different `source_snapshot_id` sets `source_snapshot_changed`.
- Active revision with changes sets `record_regeneration_recommended`.
- Service output entries are ordered newest first even though repository fixtures are loaded in ascending revision order.
- No snapshots returns an empty history response.

- [ ] **Step 2: Use lightweight domain fixtures**

Build small `ConfirmedMatrixSnapshot` fixtures directly with:

- one revision 1 snapshot
- one revision 2 snapshot with added group
- one revision 2 snapshot with added row/cell
- one source snapshot change variant

Do not use database or API fixtures in unit service tests.

### Task 2: Implement Backend History Service

**Files:**

- Create: `backend/application/confirmed_matrix_authority_history_service.py`

- [ ] **Step 1: Add application dataclasses**

Recommended model:

```python
@dataclass(frozen=True, slots=True)
class ConfirmedMatrixAuthorityHistoryEntry:
    confirmed_matrix_id: str
    confirmed_revision: int
    is_active_authority: bool
    status: str
    confirmed_by: str
    confirmed_at: str
    superseded_at: str | None
    superseded_reason: str | None
    source_snapshot_changed: bool
    group_change_count: int
    step_change_count: int
    token_change_count: int
    record_regeneration_recommended: bool
    change_summary: str
```

```python
@dataclass(frozen=True, slots=True)
class ConfirmedMatrixAuthorityHistory:
    project_id: str
    entries: tuple[ConfirmedMatrixAuthorityHistoryEntry, ...]
```

- [ ] **Step 2: Add store protocol**

```python
class ConfirmedMatrixAuthorityHistoryStore(Protocol):
    def list_by_project(self, project_id: str) -> tuple[ConfirmedMatrixSnapshot, ...]:
        ...
```

- [ ] **Step 3: Compare adjacent snapshots deterministically**

Use stable comparison keys:

- groups: `(group_key, group_label, sample_quantity_expression)`
- steps/rows: `(test_item, source_section, method, condition, requirement)`
- tokens/cells: row key + group key + `cell_value`

Keep comparison count-based. Do not expose full row/cell diffs in v1.

- [ ] **Step 4: Build readable summaries**

Rules:

- Revision 1: `Initial confirmed Matrix authority.`
- No detected content change: `Revision N confirmed with no Matrix content changes detected.`
- Changes: include group/step/token counts and source change when applicable.

`record_regeneration_recommended` must use this exact boolean definition:

- `is_active_authority == false` -> `true`
- `is_active_authority == true` and the entry differs from the previous revision by source/group/step/token comparison -> `true`
- otherwise -> `false`

UI copy must phrase this as "may need regeneration" and must not claim a generated draft exists.

### Task 3: Add Repository Project Listing

**Files:**

- Modify: `backend/infrastructure/storage/repositories/confirmed_matrix_authority.py`
- Modify: `tests/unit/test_confirmed_matrix_authority_repository.py`

- [ ] **Step 1: Add `list_by_project(project_id)`**

Return all snapshots for a project ordered by `confirmed_revision.asc()`.

The repository ordering is intentionally ascending so adjacent revision comparison is deterministic. The history service must convert final output entries to `confirmed_revision.desc()` before returning to the API layer.

- [ ] **Step 2: Add repository coverage**

Extend existing repository tests to confirm:

- revision 1 and 2 are returned in order
- active and superseded metadata are preserved
- snapshots include groups/rows/cells

### Task 4: Add API Route And Integration Test

**Files:**

- Create: `backend/api/routes_confirmed_matrix_authority_history.py`
- Modify: `backend/api/dependencies.py`
- Modify: `backend/api/main.py`
- Create: `tests/integration/test_confirmed_matrix_authority_history_api.py`

- [ ] **Step 1: Add dependency wiring**

Create `get_confirmed_matrix_authority_history_service(...)` using `ConfirmedMatrixAuthorityRepository`.

- [ ] **Step 2: Add route**

```text
GET /api/projects/{project_id}/confirmed-matrix/authority-history
```

Return typed Pydantic response:

- `project_id`
- `entries`

No request body.

- [ ] **Step 3: Add integration coverage**

Seed using existing Matrix import/draft/confirm/revision helpers where possible:

- no history returns `entries: []`
- confirm + revision returns two entries ordered newest first
- active entry indicates current authority
- at least one changed revision indicates regeneration may be needed
- integration response order is fixed at `confirmed_revision.desc()`

### Task 5: Add Frontend API Client And Panel Tests

**Files:**

- Modify: `frontend/src/api/client.ts`
- Create: `frontend/src/features/project-workbench/AuthorityChangeHistoryPanel.test.tsx`
- Create later: `frontend/src/features/project-workbench/AuthorityChangeHistoryPanel.tsx`

- [ ] **Step 1: Add API client types and function**

Types:

- `ConfirmedMatrixAuthorityHistoryEntry`
- `ConfirmedMatrixAuthorityHistory`

Function:

```ts
export function fetchConfirmedMatrixAuthorityHistory(
  projectId: string
): Promise<ConfirmedMatrixAuthorityHistory>
```

- [ ] **Step 2: Write component tests**

Cover:

- loading state
- empty state
- current authority row
- regeneration warning text
- no `<button>` rendered
- API failure message

Mock only `frontend/src/api/client.ts`.

### Task 6: Implement Frontend History Panel

**Files:**

- Create: `frontend/src/features/project-workbench/AuthorityChangeHistoryPanel.tsx`
- Modify: `frontend/src/workbench.css`

- [ ] **Step 1: Implement compact read-only panel**

Render:

- title `Authority Change History`
- latest/current marker
- revision, actor, confirmed time
- summary text
- regeneration advisory if flagged

Use semantic list/table markup. Do not render buttons.

- [ ] **Step 2: Add styles**

Use existing Workbench density and typography. Keep it compact and readable; avoid card nesting.

### Task 7: Wire Panel Into Project Workbench Projection

**Files:**

- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`

- [ ] **Step 1: Render the panel**

Place it near the confirmed Matrix projection context so operators can connect current authority, projection, and Test Record generation freshness.

- [ ] **Step 2: Update tests**

Assert the history panel is mounted for a project and does not alter existing projection readiness behavior.

### Task 8: Add Static Guards

**Files:**

- Modify: `tests/unit/test_frontend_shell_files.py`

- [ ] **Step 1: Add TASK_272 static assertions**

Guard:

- `AuthorityChangeHistoryPanel.tsx` exists
- component does not contain `<button`
- component does not contain forbidden action phrases such as `approve`, `permission`, `equipment`, `AI review`, `report generation`, `fee`
- API call lives in `frontend/src/api/client.ts`
- Project Workbench imports the panel

### Task 9: Run Validation And Update Task State

**Files:**

- Modify: `tasks/TASK_272_LIGHTWEIGHT_AUTHORITY_CHANGE_HISTORY.md`
- Modify: `docs/task_board.md`
- Modify: `docs/task_plan_index.md`

- [ ] **Step 1: Run backend tests**

```powershell
py -m pytest tests\unit\test_confirmed_matrix_authority_history_service.py -q
py -m pytest tests\unit\test_confirmed_matrix_authority_repository.py -q
py -m pytest tests\integration\test_confirmed_matrix_authority_history_api.py -q
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
```

- [ ] **Step 2: Run frontend tests**

```powershell
cd frontend
npm test -- --run AuthorityChangeHistoryPanel
npm test -- --run ProjectWorkbenchMatrixProjectionPanel
npm run build
```

- [ ] **Step 3: Run static and diff validation**

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task272 or task271 or project_workbench"
git diff --check
```

- [ ] **Step 4: Update task and board**

Mark TASK_272 complete only after validation passes. Do not activate TASK_273 in the same implementation turn unless the user explicitly starts that task later.

## Review Checklist

Before final response after implementation:

- [ ] `docs/project_management/TASK_REVIEW_CHECKLIST.md` has been applied.
- [ ] No new database table was added.
- [ ] No permission/approval workflow was added.
- [ ] No StepInstance or execution persistence was added.
- [ ] No generation ledger claim was made.
- [ ] UI is read-only and has no history action buttons.
- [ ] Existing TASK_257 through TASK_271 tests remain intact.
