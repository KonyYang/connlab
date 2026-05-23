# TASK_265_END_TO_END_SMOKE_VALIDATION_AND_BOARD_SYNC

## Status

Complete on 2026-05-23. End-to-end Matrix authority to Test Record preview smoke validation is implemented and passing.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

none. `TASK_265_END_TO_END_SMOKE_VALIDATION_AND_BOARD_SYNC` is complete; awaiting next approved task.

## Why This Task Is Allowed Now

- `TASK_261_MATRIX_IMPORT_GROUP_SELECTION_COMMIT` is complete.
- `TASK_262_MATRIX_IMPORT_GROUP_SELECTION_VIEW` is complete.
- `TASK_262A_MATRIX_IMPORT_SELECTION_MODE_AND_ACTION_CLARITY` is complete.
- `TASK_262B_MATRIX_IMPORT_PREVIEW_DETECTION_FEEDBACK_HARDENING` is complete.
- `TASK_263_CONFIRMED_MATRIX_TEST_RECORD_PREVIEW_BACKEND` is complete.
- `TASK_264_MATRIX_TO_TEST_RECORD_SMOKE_UI` is complete.
- `TASK_265_END_TO_END_SMOKE_VALIDATION_AND_BOARD_SYNC` has been implemented under explicit user approval.
- `docs/matrix_authority_to_test_record_smoke_flow_plan.md` identifies this task as the final validation and board-sync slice for the Matrix authority to Test Record smoke flow.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- The task is a bounded integration validation and documentation synchronization task.
- It must exercise the existing APIs end to end without adding new product behavior.
- The main risk is scope creep: this task must not implement new runtime execution, UI, report generation, fee, equipment, or persistence domains.
- Medium reasoning is enough if the worker follows the approved test fixture and keeps changes limited to integration tests and board/status docs.

## Objective

Create a narrow end-to-end smoke validation for the complete Matrix authority to Test Record preview chain, then synchronize task status documentation after validation passes.

Primary flow:

```text
Matrix import commit
-> full SourceMatrix persisted
-> selected-only ProjectMatrixDraft created
-> selected draft confirmed into active ConfirmedMatrix
-> Test Record preview requested from ConfirmedMatrix authority
-> selected groups, sample quantity, and step rows verified
-> unselected group exclusion verified across downstream outputs
```

## Scope

Allowed:

- Add one narrow backend integration smoke test for the full API chain.
- Reuse existing FastAPI `TestClient` and temporary SQLite setup patterns.
- Verify SourceMatrix lineage retains all imported groups.
- Verify ProjectMatrixDraft contains selected groups only.
- Verify ConfirmedMatrix contains selected groups only.
- Verify Test Record preview contains selected groups only.
- Verify sample quantity survives from imported group to preview group.
- Verify deterministic group/order/token behavior for the smoke fixture.
- Run existing TASK_263/TASK_264 focused validations.
- Update `docs/task_board.md` only after validation passes.
- Update this task file to complete only after validation passes.
- Optionally create `docs/matrix_to_test_record_smoke_validation.md` if the implemented result needs a concise human-readable smoke record.

Forbidden:

- No frontend implementation changes.
- No backend service/route/repository/schema changes unless a test reveals a real defect and the user separately approves a fix task.
- No parser behavior changes.
- No Matrix import UI changes.
- No Project Workbench UI changes.
- No formal `TestRecord` aggregate.
- No StepInstance, execution state, result persistence, evidence/image persistence, reviewer workflow, structured LLCR sheet, runtime execution dashboard, report generation, fee generation, duration estimation, equipment matching, AI review, LAN, permissions, or deployment work.
- No `.docx`, PDF, Excel, or export generation.
- No broad task-board cleanup beyond the TASK_265 status sync.

## Candidate Impact Files

Expected:

- new `tests/integration/test_matrix_to_test_record_smoke_flow_api.py`
- `docs/task_board.md` after implementation completion
- `tasks/TASK_265_END_TO_END_SMOKE_VALIDATION_AND_BOARD_SYNC.md` after implementation completion

Optional:

- `docs/matrix_to_test_record_smoke_validation.md`

Avoid modifying:

- backend application services
- backend API routes
- storage models/repositories
- frontend source files
- Matrix parser
- report/fee/equipment services

## Smoke Fixture Requirements

Use a project with one imported Matrix preview payload containing three groups:

- `g1`, sample quantity `5`
- `g2`, sample quantity `6`
- `g3`, sample quantity `7`

Select only:

- `g1`
- `g3`

Rows:

- `Visual`, section `6.1`, group tokens:
  - `g1`: `1`
  - `g2`: `2`
  - `g3`: `3`
- `LLCR`, section `6.2`, group tokens:
  - `g1`: `4(a)`
  - `g2`: `5`
  - `g3`: `6,7`
- sample row `Samples Quantity (PCS)`:
  - `g1`: `5`
  - `g2`: `6`
  - `g3`: `7`

Required assertions:

- SourceMatrix snapshot groups are `["g1", "g2", "g3"]`.
- ProjectMatrixDraft groups are `["g1", "g3"]`.
- ConfirmedMatrix groups are `["g1", "g3"]`.
- Test Record preview groups are `["g1", "g3"]`.
- `g2` is absent from ProjectMatrixDraft, ConfirmedMatrix, and Test Record preview.
- `g2` remains present in SourceMatrix lineage.
- Preview sample quantities are `{"g1": "5", "g3": "7"}`.
- Preview step raw tokens for `g1` are `["1", "4(a)"]`.
- Preview step raw tokens for `g3` are `["3", "6", "7"]`.
- Preview response does not expose `source_section`.
- Preview response exposes `section`.

## Acceptance Criteria

- Backend integration smoke passes using at least two selected groups from a three-group source.
- Full SourceMatrix lineage still contains unselected group `g2`.
- ProjectMatrixDraft excludes unselected group `g2`.
- ConfirmedMatrix excludes unselected group `g2`.
- Test Record preview excludes unselected group `g2`.
- Sample quantity survives for selected groups.
- Step token order is deterministic and matches group order, row order, token order.
- TASK_264 component behavior test remains passing.
- TASK_263 API contract test remains passing.
- No fee/report/equipment/StepInstance/execution persistence scope is introduced.
- `docs/task_board.md` is updated only after validation passes.

## Validation

Minimum validation after implementation:

```powershell
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
```

Regression validation:

```powershell
py -m pytest tests\integration\test_confirmed_matrix_test_record_preview_api.py -q
```

```powershell
cd frontend; npm test -- --run TestRecordPreviewSmokePanel
```

```powershell
cd frontend; npm run build
```

Optional wider confidence check:

```powershell
py -m pytest tests\integration\test_matrix_import_group_selection_commit_api.py tests\unit\test_confirmed_matrix_test_record_preview_service.py -q
```

## Required Executable Plan Before Implementation

The executable plan for this task is:

```text
docs/task_265_end_to_end_smoke_validation_and_board_sync_plan.md
```

No implementation code may be written before this task file and plan are reviewed and explicitly approved.

## Residual Risk Record

- TASK_265 is validation and board synchronization only. If the end-to-end smoke test reveals a real product defect, stop and report it instead of expanding TASK_265 into an implementation fix.
- Existing integration test helpers duplicate temporary SQLite setup. This task may duplicate the local pattern for a narrow smoke test, but must not introduce a broad fixture refactor.
- This task proves smoke-flow correctness only. It does not make Test Record a formal persisted execution object.
