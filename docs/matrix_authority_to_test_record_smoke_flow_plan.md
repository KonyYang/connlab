# Matrix Authority → Test Record Smoke Flow Plan

## Protocol Status

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `none`
- Why this plan is allowed now: `docs/task_board.md` shows `TASK_260_CONFIRMED_MATRIX_RUNTIME_PROJECTION_CONSUMER` complete and no active task.
- This document proposes the next controlled workflow phase only.
- Implementation status: planning only.
- No backend/frontend implementation is authorized directly by this document.
- Current business stage: actual business workflow stabilization stage, not MVP experimentation stage.
- Current architecture priority: stabilize authority workflow before execution system expansion.
- Recommended implementation model: `GPT-5.3-codex` with medium reasoning, deterministic backend/frontend implementation, and strict scope control.

---

## Reference Understanding

The supplied reference documents are used only to understand the business shape:

- Product specification documents contain Matrix tables with test items, sections, and group columns.
- Test Record examples contain repeated group-level test record tables where selected Matrix groups become separate test-record sections with step rows, methods, conditions, and result columns.

These references do not authorize full template generation, report generation, fee generation, equipment assignment, or structured LLCR implementation in this phase.

---

## Phase Goal

Current phase goal:

```text
Workflow correctness over metadata completeness.
```

Primary validation flow:

```text
Import Matrix
→ Group Selection
→ ProjectMatrixDraft
→ Confirmed Matrix
→ Test Record Preview
```

Current phase focuses on validating:

- Matrix authority workflow correctness
- selected group propagation
- sample quantity propagation
- execution projection behavior
- downstream consumer boundaries
- authority lifecycle stability

Current phase explicitly does not focus on:

- report generation
- fee AI
- equipment AI
- metadata perfection
- runtime execution system
- structured LLCR execution
- UI polish

---

## 1. Matrix Workspace Positioning

Matrix Editor should evolve into:

```text
Matrix Workspace
```

Matrix Workspace is not project-only.

Future supported modes:

- project mode
- estimation mode
- library mode
- revision mode

Current implementation phase:

```text
project mode only
```

However, architecture and UI structure must not lock future modes.

---

## 2. Matrix Workspace Responsibilities

Matrix Workspace responsibilities:

- import/load matrix
- source matrix preview
- group selection
- matrix editing
- matrix authority confirmation
- revision draft workflow

Matrix Workspace is not responsible for:

- test record generation
- fee generation
- duration generation
- report generation
- runtime execution
- structured execution persistence
- equipment recommendation
- downstream derived outputs

---

## 3. Import / Load Matrix Direction

Current button:

```text
Import Matrix
```

Should evolve into:

```text
Import / Load Matrix
```

Future supported sources:

- Word / DOCX
- PDF
- XLS / XLSX
- historical project
- matrix library
- template

Current phase:

```text
DOCX only
```

DOCX import must be fully stabilized first. Other import types are future extensions only.

---

## 4. Matrix Authority Lifecycle

Matrix authority lifecycle:

```text
SourceMatrix
→ ProjectMatrixDraft
→ ConfirmedMatrix
```

### SourceMatrix

Immutable imported source lineage.

Contains:

- full imported matrix
- all groups
- original structure
- import metadata
- parser metadata
- sparse source cells
- source file references

### ProjectMatrixDraft

Editable project execution projection.

Contains:

- selected groups only
- editable execution projection
- temporary working state
- revision workflow state

### ConfirmedMatrix

Execution authority object.

Only ConfirmedMatrix is authority.

Downstream consumers must consume:

```text
ConfirmedMatrix only
```

Not:

- SourceMatrix
- Draft state
- frontend temporary state

---

## 5. Source vs Projection Boundary

Full imported matrix must always remain preserved as source lineage.

Selected groups are:

```text
project execution projection
```

Not:

```text
source replacement
```

Unselected groups:

- remain traceable
- remain preserved in source lineage
- do not enter execution projection
- do not appear in downstream outputs

This boundary is critical for:

- revision drafts
- historical comparison
- group reselection
- future matrix library reuse
- estimation mode reuse

---

## 6. Group Selection View

Group Selection View belongs to:

```text
Matrix authority workflow
```

Not:

- runtime workflow
- report workflow
- execution system

Workflow:

```text
Import Matrix
→ Matrix Preview
→ Group Selection
→ Draft Creation
→ Matrix Editing
→ Confirm Matrix
```

Rules during Group Selection phase:

Display:

- group label/key
- sample quantity expression
- optional step count
- checkbox selection

Do not display:

- Test Item
- Method
- Condition
- Requirement
- execution rows
- report data

Reason:

Group Selection is a workflow gate, not a second matrix editor.

Only after selected groups are confirmed, `ProjectMatrixDraft` is created.

---

## 7. Matrix Editing Boundary

Matrix Editing starts after selected groups confirmation.

At this stage, full matrix editing UI becomes visible:

- Test Item
- Section
- Method
- Condition
- Requirement
- selected group columns

Matrix editing is authority definition workflow, not downstream execution preview.

---

## 8. Project Workbench Responsibilities

Project Workbench is:

```text
Confirmed Matrix downstream consumer workspace
```

Project Workbench responsibilities:

- Test Record preview
- future fee evaluation
- future duration estimation
- future approval package
- future report preview

Project Workbench is not responsible for:

- Matrix authority editing
- source matrix editing
- group selection editing

---

## 9. Test Record Boundary

Test Record Preview is not authority.

ConfirmedMatrix remains the only authority source.

Test Record is derived output projection.

Current phase:

```text
preview only
```

No persisted formal TestRecord aggregate yet.

---

## 10. Consumer Pattern

All downstream outputs consume:

```text
ConfirmedMatrix only
```

Examples:

- Test Record
- Fee Evaluation
- Duration Estimation
- Approval Package
- Future Report Projection

Consumers must not consume:

- SourceMatrix directly
- Draft state directly
- frontend temporary projection state

---

## 11. Test Record Smoke Flow

Current phase:

```text
Smoke Validation Only
```

Smoke validation goals:

- selected groups propagation
- sample quantity propagation
- execution ordering
- hidden group exclusion
- downstream projection correctness

Allowed during current phase:

- placeholder metadata
- partial fields
- simplified preview
- non-final formatting

Current goal is workflow correctness, not document perfection.

---

## 12. Execution Ordering Rule

Current smoke flow ordering:

```text
preserve confirmed group order,
then preserve step token order inside each group
```

This ordering rule remains fixed during smoke phase.

Future execution modes may later support:

- group-first execution
- step-first execution
- lab-optimized execution
- parallel execution

Current phase does not expand execution modes.

---

## 13. Observation vs Structured Measurement

Current architecture must reserve classification boundary:

- observation
- measurement
- future-structured

### Observation

Examples:

- visual inspection
- appearance
- simple pass/fail

Usually requires:

- PASS/FAIL
- remark
- optional image

### Measurement

Examples:

- LLCR
- DWV
- current rating

Usually requires:

- sample
- point
- measured value
- unit
- judgement

Current phase does not implement structured execution forms. However, the classification boundary must already exist.

---

## 14. UI Boundary

Do not embed Test Record Preview inside Matrix editing grid.

Reason:

Matrix Workspace:

- authority lifecycle
- matrix definition

Project Workbench:

- downstream consumer preview
- derived outputs

These are different architecture layers.

---

## 15. Current Phase Non Goals

Current phase explicitly does not implement:

- Report generation
- LLCR structured execution sheet
- Runtime execution system
- AI recommendation
- Equipment matching
- Matrix Library full implementation
- Historical reuse automation
- Final document export perfection
- UI polish
- full execution persistence

---

## 16. Future Direction (Not Current Phase)

Future architecture direction:

```text
Execution Result Persistence
→ Structured Measurement Flow
→ Living Report Projection
```

Future phases may include:

- structured LLCR execution forms
- execution result persistence
- evidence persistence
- reviewer workflow
- live report projection
- runtime execution dashboard
- equipment matching
- fee estimation consumers
- estimation mode consumers

Current phase does not implement these systems.

---

## 17. TASK_261_MATRIX_IMPORT_GROUP_SELECTION_COMMIT

Goal:

Create the backend import-commit boundary that persists the full Source Matrix while creating a project-specific `ProjectMatrixDraft` from selected groups.

### Impact Files

- `backend/application/source_matrix_import_persistence_service.py`
- `backend/application/project_matrix_draft_persistence_service.py`
- new `backend/application/matrix_import_commit_service.py`
- `backend/api/routes_project_test_plan.py` or new `backend/api/routes_matrix_import_commit.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`
- `frontend/src/api/client.ts` only for typed DTO names if this task includes API contract exposure
- tests:
  - `tests/unit/test_matrix_import_commit_service.py`
  - `tests/integration/test_matrix_import_group_selection_commit_api.py`

### Backend Flow

1. Input:
   - Matrix preview payload
   - `selected_group_keys`
2. Validate:
   - project exists
   - selected group keys are non-empty
   - all selected group keys exist in preview groups
3. Persist:
   - full immutable SourceMatrix lineage
   - all groups
   - all rows
   - sparse source cells
4. Create:
   - ProjectMatrixDraft
   - selected-group projection only
5. Return:
   - source metadata
   - created draft aggregate

### Frontend Flow

- No visible UI is required in this task unless the API contract is exposed in `client.ts`.
- Existing import preview behavior remains unchanged.

### Acceptance Criteria

- Full source Matrix is persisted even when only a subset of groups is selected.
- Project draft contains the selected groups needed for editing and confirmation.
- Unselected source groups are not copied into downstream confirmed authority or preview outputs.
- Sample quantity expressions for selected groups are preserved.
- Unknown or empty selected group keys return typed 400/422 errors.
- The route remains thin and calls application service only.
- Existing preview APIs and existing draft save APIs remain unchanged.

### Risks

- Current source import persistence was originally attached to legacy `ProjectTestPlanDraft` creation. This task must avoid relying on a legacy draft id as business authority.
- If the draft keeps hidden unselected groups, frontend save could accidentally drop or re-enable them. The preferred smoke-flow behavior is to keep the full source in `SourceMatrix` and keep the editable `ProjectMatrixDraft` selected-only.

---

## 18. TASK_262_MATRIX_IMPORT_GROUP_SELECTION_VIEW

Goal:

Add Group Selection View after Matrix import preview confirmation and before entering Matrix Editor editing state.

### Impact Files

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- new `frontend/src/features/matrix-editor/MatrixImportGroupSelectionView.tsx`
- optional `frontend/src/features/matrix-editor/matrixImportSelectionSelectors.ts`
- `frontend/src/api/client.ts`
- `frontend/src/workbench.css` only for minimal existing-pattern classes
- tests:
  - `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
  - `tests/unit/test_frontend_shell_files.py`

### Frontend Flow

1. Operator imports a Matrix document and reviews the existing import preview.
2. Operator clicks import confirmation action.
3. UI shows Group Selection View.
4. View lists groups only:
   - group label/key
   - sample quantity expression if extracted
   - checkbox
5. View must not show Test Item, Method, Condition, Requirement, step preview, or Matrix cell details.
6. Operator confirms selected groups.
7. Frontend calls the TASK_261 commit API.
8. Returned ProjectMatrixDraft is loaded into Matrix Editor.
9. Matrix Editor enters normal editable state with only selected project groups visible.

### Acceptance Criteria

- Group Selection View appears after import preview confirmation, not before parsing.
- At least one group must be selected before confirm.
- Only groups are displayed.
- Confirm creates/loads a project-specific draft.
- Matrix Editor displays selected groups only.
- Existing manual edit/save behavior still works.
- No new route page or broad Matrix Editor visual refactor is introduced.

### Risks

- `MatrixEditorWorkspace.tsx` is already large. Keep the new view as a named feature component and move selection conditions into selectors where practical.
- Avoid turning group selection into a Matrix editing surface. It is a gate, not a second editor.

---

## 19. TASK_263_CONFIRMED_MATRIX_TEST_RECORD_PREVIEW_BACKEND

Goal:

Generate read-only Test Record preview from the active ConfirmedMatrix authority.

### Impact Files

- new `backend/application/confirmed_matrix_test_record_preview_service.py`
- `backend/api/routes_confirmed_matrix_test_record_preview.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`
- optional shared mapper/module if existing test-record DTOs are reused
- tests:
  - `tests/unit/test_confirmed_matrix_test_record_preview_service.py`
  - `tests/integration/test_confirmed_matrix_test_record_preview_api.py`

### Backend Flow

1. Load active ConfirmedMatrix for a project.
2. For each confirmed selected group, build a Test Record preview group.
3. Use confirmed group `sample_quantity_expression` as sample quantity authority.
4. Expand confirmed sparse cell token values into step rows using existing Matrix token parsing/projection utilities.
5. For each step row, carry:
   - sequence/raw token
   - test item
   - source section
   - method
   - condition
   - requirement
6. If method/condition/requirement are blank, return empty fields or explicit placeholder strings for smoke visibility only.
7. Return read-only preview DTO.
8. Do not write `.docx`.

### Acceptance Criteria

- A project with active confirmed Matrix can request Test Record preview without sending Matrix rows in the request body.
- Preview contains only confirmed groups.
- Preview preserves sample quantity per selected group.
- Unselected source groups never appear.
- No fee dataset is returned.
- No report/test-record file is generated.
- No equipment table is generated.
- No StepInstance or execution persistence is introduced.
- No active confirmed Matrix returns typed 404.

### Risks

- Existing `test_record_fee_dataset_preview_service.py` is tied to legacy `ProjectTestPlanDraft` and fee. Do not extend fee scope.
- Step ordering must be deterministic. For smoke flow, preserve group order, then row order, then parsed token order.

---

## 20. TASK_264_MATRIX_TO_TEST_RECORD_SMOKE_UI

Goal:

Add minimal operator smoke UI to prove selected Matrix groups drive Test Record preview.

### Recommended Placement

Prefer Project Workbench or a Project Workbench-equivalent downstream consumer panel.

Do not embed Test Record Preview into the Matrix editing grid.

### Impact Files

- `frontend/src/api/client.ts`
- new `frontend/src/features/matrix-editor/TestRecordPreviewSmokePanel.tsx` or project-workbench equivalent
- `frontend/src/features/project-workbench/*` for composition where suitable
- `frontend/src/workbench.css` only for minimal existing-pattern classes
- tests:
  - frontend smoke/static tests
  - `tests/unit/test_frontend_shell_files.py`

### Frontend Flow

1. Operator imports Matrix.
2. Operator selects groups in Group Selection View.
3. Operator edits/saves draft.
4. Operator confirms Matrix authority.
5. Operator opens Test Record Preview smoke panel.
6. UI calls confirmed-Matrix Test Record preview API.
7. UI shows group rows with:
   - group label/key
   - sample quantity
   - step count
   - compact list/table of step rows
8. UI visibly proves:
   - selected groups appear
   - sample quantity is preserved
   - unselected groups do not appear

### Acceptance Criteria

- Smoke UI has no fee/report/equipment actions.
- It does not expose future execution controls.
- It does not polish Matrix UI layout.
- It displays selected groups, sample quantity, and step count from confirmed Matrix preview.
- It displays clear empty/error state when no confirmed Matrix exists.
- Static/frontend tests verify API client symbols and that unselected group labels from mocked response are not rendered.
- `cd frontend; npm run build` passes.

### Risks

- Placing the smoke panel inside Matrix Editor may grow the file and blur architecture boundaries.
- If the confirmed Matrix path only exists after save/confirm, users may expect preview before confirmation. This smoke task should explicitly require confirmed authority as input.

---

## 21. TASK_265_END_TO_END_SMOKE_VALIDATION_AND_BOARD_SYNC

Goal:

Create narrow integration/smoke validation for the whole chain and update the task board after implementation tasks pass.

### Impact Files

- `docs/task_board.md`
- optional `docs/matrix_to_test_record_smoke_validation.md`
- tests:
  - `tests/integration/test_matrix_to_test_record_smoke_flow_api.py`
  - frontend smoke/static test updates if not covered in TASK_264

### End-to-End Flow

1. Import/commit full Source Matrix with selected groups.
2. Create project-specific draft from selected groups.
3. Save draft.
4. Confirm Matrix.
5. Request Test Record preview.
6. Assert selected groups drive preview.
7. Assert sample quantity survives.
8. Assert unselected groups are absent.

### Acceptance Criteria

- Backend integration smoke passes with at least two groups selected from a three-group source.
- Unselected group is still present in SourceMatrix lineage but absent from ProjectMatrixDraft visible/editable output, ConfirmedMatrix, and Test Record preview.
- No fee/report/equipment/StepInstance persistence is introduced.
- `docs/task_board.md` is updated only after actual implementation completion.

### Risks

- This task should not become another implementation task. It is validation and board synchronization only.

---

## 22. Recommended Execution Order

1. `TASK_261_MATRIX_IMPORT_GROUP_SELECTION_COMMIT`
2. `TASK_262_MATRIX_IMPORT_GROUP_SELECTION_VIEW`
3. `TASK_263_CONFIRMED_MATRIX_TEST_RECORD_PREVIEW_BACKEND`
4. `TASK_264_MATRIX_TO_TEST_RECORD_SMOKE_UI`
5. `TASK_265_END_TO_END_SMOKE_VALIDATION_AND_BOARD_SYNC`

---

## 23. Core Acceptance For This Phase

The phase succeeds when:

- Matrix import preview leads to Group Selection.
- Selected groups create ProjectMatrixDraft.
- Full SourceMatrix lineage remains immutable.
- ConfirmedMatrix becomes authority.
- Test Record Preview consumes ConfirmedMatrix only.
- Selected groups propagate correctly.
- Sample quantity survives correctly.
- Unselected groups remain excluded.
- No non-goal system is accidentally implemented.
