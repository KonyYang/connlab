# TASK_332B Basic Information Test Type In Sheet LTR Mapping Plan

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Current Active Task ID

`TASK_332B_BASIC_INFORMATION_TEST_TYPE_IN_SHEET_LTR_MAPPING`

## Why This Task Is Allowed For Planning

The user reviewed the Basic Information / Workbench summary mapping and clarified that the current `Test Type` display is wrong for the LTR update context. The Application Form `Test Type` must remain separate. The public-drive LTR workbook `"Test Type"` column must map to New Project Project setup confirmation `Test Type in sheet*`.

This is allowed for planning only because it is a controlled follow-up to Phase 11 Basic Information and LTR workbook sync behavior. It must not be implemented until the user explicitly approves this task.

## Step 1 - Task Understanding

### Goal

Introduce `test_type_in_sheet` as a separate Basic Information value sourced from New Project setup confirmation, display it in the Basic Information right-side card, and use it for public-drive LTR workbook `"Test Type"` writes.

### Input Data

- New Project setup confirmation field:
  - `test_type_in_sheet`
- Existing registered LTR record notes containing structured `operator_note`.
- Existing Application Form field:
  - `test_type`
- Existing Basic Information draft/confirmed JSON values.

### Output Data

- Basic Information draft/confirmed values may include:
  - `test_type` for Application Form `Test Type`
  - `test_type_in_sheet` for LTR sheet `Test Type in sheet`
- Basic Information editor displays `Test Type in sheet` in the Laboratory execution card.
- Workbench summary displays `Test Type in sheet`.
- Public-drive LTR workbook sync writes the workbook `"Test Type"` column from `test_type_in_sheet`.

### Modules

- Backend Basic Information source assembly:
  - `backend/application/project_basic_information_service.py`
  - `backend/application/project_identity.py`
- Backend LTR workbook sync:
  - `backend/application/ltr_workbook_basic_information_sync_service.py`
- Frontend Basic Information:
  - `frontend/src/api/client.ts`
  - `frontend/src/features/project-basic-information/useProjectBasicInformationModel.ts`
  - `frontend/src/features/project-basic-information/basicInformationFieldConfig.ts`
  - `frontend/src/features/project-basic-information/basicInformationSelectors.ts`
  - `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx`
  - `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx`
- Tests:
  - `tests/unit/test_project_basic_information_service.py`
  - `tests/unit/test_ltr_workbook_basic_information_sync_service.py`
  - `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`
  - `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.test.tsx`
  - `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`

### Not Allowed

- Do not rename or repurpose existing `test_type`.
- Do not use Application Form `test_type` as fallback for `test_type_in_sheet`.
- Do not change New Project setup confirmation behavior.
- Do not add a SQL schema migration.
- Do not change LTR workbook append/new-registration behavior.
- Do not introduce a second hardcoded `Test Type in sheet` option list that can drift from New Project setup confirmation.
- Do not implement broad unrelated Basic Information lookup-option infrastructure beyond reusing the existing New Project completion options endpoint for this field.

## Step 2 - Design

### Data Model

Use the existing JSON-backed Basic Information values model.

Add one new value key:

```text
test_type_in_sheet
```

No database schema change is required.

### Field Source

Basic Information source assembly should:

1. Select the latest relevant LTR record using the same registered-LTR logic already used by project identity helpers where possible.
2. Read the structured setup payload from `LtrRecord.notes` through `setup_payload_from_ltr_notes()`.
3. Add a source suggestion:

```python
"test_type_in_sheet": (
    "project_setup_confirmation",
    setup.get("test_type_in_sheet"),
)
```

4. Keep the existing source suggestion unchanged:

```python
"test_type": ("application_form", latest_form.test_type if latest_form else None)
```

Because source suggestions feed the Basic Information source signature, adding `test_type_in_sheet` can mark an existing confirmed record as `needs_review` when the registered LTR note provides this value and the confirmed values do not yet contain it. This is intended. The operator should confirm the newly visible sheet field before using Workbench `Update LTR`.

### UI Field Configuration And Option Source

Reuse the existing API client function:

```ts
getNewProjectCompletionOptions()
```

The Basic Information model should load `test_type_in_sheet_options` from `/api/new-project/completion-options`, the same source used by New Project Project setup confirmation. This preserves administrator-imported `project_setup_test_type_in_sheet` lookup options.

Add a field in the `Result and commercial` group, with options supplied from the loaded model instead of a Basic Information-only hardcoded list:

```ts
{
  key: "test_type_in_sheet",
  label: "Test Type in sheet",
  kind: "select",
  layout: "quarter",
  preserveUnknownOption: true,
}
```

Keep `test_type` in the Product information group unchanged.

### UI Placement

The right-side Basic Information card currently renders the `Laboratory execution` panel from field groups after index 3. `Result and commercial` belongs to that right-side panel. Add `Test Type in sheet` beside `Failed item` in that group.

Current CSS makes `.basic-information-field.is-textarea` span all 12 grid columns, and `failed_item` currently has no layout override. Therefore the implementation must also adjust `failed_item` to a partial-width layout so the new field can sit beside it.

Planned layout:

- `failed_item`: `kind: "textarea"`, `layout: "wideQuarter"` or another explicit partial-width layout that renders beside the new field on normal desktop widths.
- `test_type_in_sheet`: `kind: "select"`, `layout: "quarter"`.

If existing CSS precedence prevents `layout` from overriding textarea span behavior, update `workbench.css` with a narrow targeted rule so textarea fields with explicit layout classes can use that layout. Do not redesign the whole Basic Information grid.

### Workbench Summary

Update `SUMMARY_KEYS` in `basicInformationSelectors.ts`:

- Remove `test_type`.
- Add `test_type_in_sheet` in the same summary position.

Expected summary order around the affected area:

```text
Project Type
Test Type in sheet
Requested by
Project Leader
Failed item
```

### LTR Workbook Mapping

Update `_row_data_from_basic_information()` in `ltr_workbook_basic_information_sync_service.py`:

Current:

```python
test_type=_required(values, ("test_type",), "Test Type")
```

Planned:

```python
test_type=_required(values, ("test_type_in_sheet",), "Test Type in sheet")
```

Do not include `"test_type"` in the fallback tuple.

Do not add a new required-key abstraction just for this task. The current required behavior lives in `_row_data_from_basic_information()` through `_required(...)`; update that call and its business label only.

### Missing Historical Value Behavior

If `test_type_in_sheet` is absent:

- Basic Information can still load.
- LTR workbook sync preview should block with missing `Test Type in sheet`.
- The operator can select `Test Type in sheet` in Basic Information and confirm again.
- The sync must not silently use Application Form `Test Type`.

## Step 3 - Implementation Tasks

### Task 1: Backend Source Assembly

**Files**

- Modify: `backend/application/project_basic_information_service.py`
- Test: `tests/unit/test_project_basic_information_service.py`

**Steps**

1. Import `setup_payload_from_ltr_notes` or a narrowly scoped helper from `backend.application.project_identity`.
2. Resolve the latest registered LTR from `ltrs` in `ProjectBasicInformationSourceAssembler.assemble()` using the existing registered-LTR selection semantics. Do not rely on raw repository list order.
3. Parse the setup payload from LTR notes.
4. Add `test_type_in_sheet` to `raw_values` with source label `project_setup_confirmation`.
5. Add a unit test proving:
   - `test_type` still comes from `ApplicationForm.test_type`.
   - `test_type_in_sheet` comes from New Project setup confirmation payload.
   - the two values can differ.
   - draft/stale LTR records do not override the registered LTR setup payload.
   - an existing confirmed record without `test_type_in_sheet` becomes `needs_review` when the registered LTR note supplies it.

**Validation**

```powershell
py -m pytest tests/unit/test_project_basic_information_service.py -q
```

### Task 2: Frontend Field, Dynamic Options, and Summary

**Files**

- Modify: `frontend/src/api/client.ts` only if exported types/functions are not already sufficient
- Modify: `frontend/src/features/project-basic-information/useProjectBasicInformationModel.ts`
- Modify: `frontend/src/features/project-basic-information/basicInformationFieldConfig.ts`
- Modify: `frontend/src/features/project-basic-information/basicInformationSelectors.ts`
- Modify if needed: `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx`
- Modify if needed: `frontend/src/workbench.css`
- Test: `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`
- Test: `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.test.tsx`
- Test: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`

**Steps**

1. Reuse existing `getNewProjectCompletionOptions()` from `frontend/src/api/client.ts`.
2. Extend `useProjectBasicInformationModel()` to load completion options alongside Basic Information, storing `test_type_in_sheet_options`.
3. If completion options fail to load, keep the Basic Information page usable and surface the same page-level error style already used for load failures, because an empty option list would prevent reliable confirmation of this field.
4. Add `test_type_in_sheet` field to `Result and commercial`, beside `Failed item`, with options supplied from the loaded completion options.
5. Set `failed_item` to an explicit partial-width layout and add/update CSS only if needed so it no longer spans all 12 columns when paired with `Test Type in sheet`.
6. Keep Application Form `test_type` field unchanged in `Product information`.
7. Change Workbench summary keys to show `test_type_in_sheet` instead of `test_type`.
8. Update tests to assert:
   - editor still has Application Form `Test Type`;
   - editor also has `Test Type in sheet`;
   - `Test Type in sheet` options come from mocked `getNewProjectCompletionOptions()`, including a custom imported option such as `Reliability`, to prevent option drift;
   - `Failed item` and `Test Type in sheet` both have partial-width layout classes and `Failed item` appears before `Test Type in sheet` in the Laboratory execution panel;
   - Workbench summary labels include `Test Type in sheet`;
   - summary no longer uses Application Form `Test Type` for the LTR update-focused row.

**Validation**

```powershell
cd frontend; npm test -- --run ProjectBasicInformationWorkspace ProjectBasicInformationSummaryCard ProjectWorkbenchLayout --watch=false
```

### Task 3: LTR Workbook Basic Information Sync Mapping

**Files**

- Modify: `backend/application/ltr_workbook_basic_information_sync_service.py`
- Test: `tests/unit/test_ltr_workbook_basic_information_sync_service.py`

**Steps**

1. Change row-data mapping so workbook row `test_type` is populated from `values["test_type_in_sheet"]`.
2. Change missing-field label to `Test Type in sheet`.
3. Do not introduce a new required-key constant; the service currently expresses the requirement directly through `_required(...)` inside `_row_data_from_basic_information()`.
4. Add tests proving:
   - workbook row data uses `test_type_in_sheet`.
   - workbook row data ignores a conflicting Application Form `test_type`.
   - missing `test_type_in_sheet` blocks preview/row-data creation.

**Validation**

```powershell
py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py -q
```

### Task 4: Regression Build and Board Update

**Files**

- Modify after implementation: `docs/task_board.md`

**Steps**

1. Run targeted backend tests.
2. Run targeted frontend tests.
3. Run frontend build.
4. Run whitespace check.
5. Update `docs/task_board.md` with completion notes only after implementation validation passes.

**Validation**

```powershell
py -m pytest tests/unit/test_project_basic_information_service.py tests/unit/test_ltr_workbook_basic_information_sync_service.py -q
cd frontend; npm test -- --run ProjectBasicInformationWorkspace ProjectBasicInformationSummaryCard ProjectWorkbenchLayout --watch=false
cd frontend; npm run build
git diff --check
```

## Step 4 - Review Checklist

- `test_type` remains Application Form `Test Type`.
- `test_type_in_sheet` is added as a separate Basic Information key.
- existing confirmed snapshots can enter `needs_review` when this new source value appears and is not yet confirmed.
- No fallback from `test_type_in_sheet` to `test_type` exists in LTR workbook sync.
- Workbench summary shows the LTR update-relevant `Test Type in sheet`.
- Basic Information editor shows both concepts clearly.
- No SQL migration is introduced.
- No New Project setup confirmation behavior is changed.
- No future Report, StepInstance, AI, permissions, LAN/server, or multi-user scope is introduced.

## Step 5 - Recommended Verification Commands

```powershell
py -m pytest tests/unit/test_project_basic_information_service.py -q
py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py -q
cd frontend; npm test -- --run ProjectBasicInformationWorkspace ProjectBasicInformationSummaryCard ProjectWorkbenchLayout --watch=false
cd frontend; npm run build
git diff --check
```

## Risks

- Historical Basic Information confirmed records may not contain `test_type_in_sheet`; sync should block rather than use the wrong field.
- Some already confirmed records may become `needs_review` after the new source suggestion is added. This is acceptable and should be covered by tests, because the operator must explicitly confirm the sheet field before public-drive LTR sync.
- Existing tests that expected `Product/Process Qualification` in Workbench summary need to be updated because the summary will now show the sheet value.
- If an imported project was created outside the current New Project setup flow, the operator may need to select `Test Type in sheet` manually before LTR sync.

## Stop Point

This plan is ready for review. Do not implement `TASK_332B` until the user explicitly approves execution.
