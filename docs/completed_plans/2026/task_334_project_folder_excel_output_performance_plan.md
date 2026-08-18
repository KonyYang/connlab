# TASK_334 Project Folder Excel Output Performance Plan

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Current Active Task

`TASK_334_PROJECT_FOLDER_EXCEL_OUTPUT_PERFORMANCE` is complete after explicit user approval on 2026-06-24.

## User Problem

Manual smoke shows `Update project folder` takes about 70 seconds. The progress dialog helps prevent operators from thinking ConnLab has frozen, but the better fix is to shorten the slow path.

The user suspects the Excel outputs may be opening Excel COM twice:

- Customer Feedback Form is `.xlsx`.
- Fee Form is `.xls`.
- The user remembers a dual-engine design where Python handles formats it can safely edit and COM handles legacy Office formats.

## Current Code Findings

The current implementation already uses different engines:

- `backend/infrastructure/office/customer_feedback_workbook_gateway.py`
  - Uses `openpyxl.load_workbook`.
  - Copies the `.xlsx` template with `shutil.copy2`.
  - Writes label-target cells through Python.
  - Does not use Excel COM.

- `backend/infrastructure/office/fee_evaluation_workbook_gateway.py`
  - Uses `win32com.client.DispatchEx("Excel.Application")`.
  - Opens the `.xls` template through Excel COM.
  - Writes Basic Information headers and Matrix basic-fill rows into the workbook.
  - Saves as `.xls`.

- `backend/application/project_folder_required_forms_service.py`
  - Already returns timing entries such as `customer_feedback_form.generate`, `fee_form.generate`, `fee_form.reuse_lookup`, `*.place`, and `*.register_output`.
  - Already has a `ReusableFeeFormArtifactReader` hook for safe Fee Form reuse before regeneration.

Conclusion: the likely Excel bottleneck is Fee Form `.xls` COM generation, not Customer Feedback `.xlsx`.

## Product Decision

TASK_334 should optimize Excel outputs only:

1. Keep Customer Feedback on the Python `openpyxl` path.
2. Make Fee Form reuse/current-output behavior more reliable before opening Excel.
3. Reduce COM chatter inside Fee Form cold generation.
4. Expose enough timing data to prove where time is spent.

Application Form Word COM write-back is a separate bottleneck candidate and should be handled by a later task after Excel timing is stable.

Performance intent:

- Repeated updates with unchanged context should avoid opening Excel COM for Fee Form.
- Cold Fee Form generation should be materially faster than the current roughly 40-second smoke observation, or the implementation must stop with timing evidence that identifies the remaining bottleneck.

## Implemented Result

- Customer Feedback remains on the Python `openpyxl` path and has a regression test guarding against Excel COM imports/dispatch.
- Fee Form safe-reuse context includes the Fee template path/content hash and explicit output mapping mode.
- Required Forms generation runs Customer Feedback before Fee Form so displayed progress and timings isolate the Fee Form cost.
- Fee Form Matrix basic-fill writing is split into focused helper modules and batches contiguous row-segment writes, reducing COM `Value` chatter in the tested path.
- Application Form Word COM write-back remains out of scope.

## File-Level Design

### Customer Feedback Path

Files to inspect/modify only if tests expose a problem:

- `backend/infrastructure/office/customer_feedback_workbook_gateway.py`
- `backend/application/customer_feedback_form_generation_service.py`
- `tests/unit/test_customer_feedback_workbook_gateway.py`
- `tests/unit/test_customer_feedback_form_generation_service.py`

Responsibilities:

- Keep `.xlsx` generation on `openpyxl`.
- Add/keep tests proving no Excel COM dependency is introduced.
- Keep existing label/offset filling behavior.

### Fee Form Path

Files likely to modify:

- `backend/infrastructure/office/fee_evaluation_workbook_gateway.py`
- possible new helper module under `backend/infrastructure/office/` if the gateway must be split before editing
- `backend/application/project_folder_required_forms_service.py`
- `backend/api/dependencies.py` or the existing reusable Fee Form reader implementation if reuse wiring has gaps
- `tests/unit/test_fee_evaluation_workbook_gateway.py`
- `tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py`
- `tests/unit/test_project_folder_required_forms_service.py`
- `tests/integration/test_project_folder_required_forms_api.py`

Responsibilities:

- Prefer safe reuse/current-output checks before opening Excel COM.
- Keep `.xls` generation through COM because `openpyxl` cannot write `.xls`.
- Optimize Matrix basic-fill writes by reducing per-cell COM calls where safe.
- Preserve existing Fee Form header placement behavior.
- Keep `fee_evaluation_workbook_gateway.py` from growing further. If the implementation needs substantial Fee Form writer changes, first extract focused helper modules, such as a Matrix basic-fill writer, identity header writer, or COM batch writer.

### Timing / Observability

Files likely to modify if timing is not visible enough:

- `backend/application/project_folder_required_forms_service.py`
- Required Forms API response DTO module
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- related frontend tests

Responsibilities:

- Keep Customer Feedback and Fee Form as separate progress steps.
- Ensure timing diagnostics are inspectable as stable labels and elapsed milliseconds.
- If browser console logging remains useful, log JSON strings instead of opaque `Object` values.

## Implementation Tasks

### Task 1: Lock Current Engine Behavior With Tests

Expected tests:

- Customer Feedback gateway imports/uses `openpyxl` and does not call an Excel COM factory.
- Required Forms staging calls Customer Feedback generation separately from Fee Form generation.
- Fee Form `.xls` generation remains COM-bound.

Acceptance:

- Tests make it impossible to accidentally route `.xlsx` Customer Feedback through Excel COM.

### Task 2: Improve Required Forms Timing Visibility

Expected changes:

- Before changing Fee Form generation logic, run the current implementation once in the same smoke scenario and record the baseline timings for:
  - `customer_feedback_form.generate`
  - `fee_form.generate`
  - `required_forms.total`
- Ensure each Required Forms batch returns timing entries for:
  - `required_forms.preview`
  - `required_forms.validate_context`
  - `customer_feedback_form.generate`
  - `customer_feedback_form.place`
  - `customer_feedback_form.register_output`
  - `fee_form.reuse_lookup`
  - `fee_form.generate`
  - `fee_form.place`
  - `fee_form.register_output`
  - `required_forms.total`
- If frontend console output is used for smoke analysis, serialize timing payloads as JSON strings.

Acceptance:

- Manual smoke can identify whether Fee Form or Customer Feedback is slow without attaching a debugger.
- The final task notes include before/after timing evidence for the same project and same user path.

### Task 3: Make Fee Form Reuse The First-Class Fast Path

Expected behavior:

- If a managed Fee Form artifact exists, its complete Fee Form context matches the current preview context, and its file still exists, project folder update reuses or copies that artifact instead of opening Excel.
- If the final target already contains a current managed Fee Form, generation should be skipped by preview/status rather than regenerated.
- If the current artifact is missing, stale, unmanaged, or has a changed fingerprint, the service must regenerate or block according to existing managed-output safety rules.

The complete Fee Form context must include at least:

- Basic Information version and source-signature hash.
- Confirmed Matrix identity and revision.
- Confirmed Fee authority identity/version or equivalent confirmed Fee context.
- Fee template identity/path/hash.
- Fee Form output mapping mode, currently Matrix basic-fill with Basic Information header filling.

If any of these inputs change, reuse is forbidden.

Acceptance:

- Repeated project folder update with unchanged Basic Information / Matrix / Fee context does not pay Excel COM cold-start time.
- Tests cover the safe reuse branch and the stale/missing branch.
- Tests prove reuse is rejected when any required context factor changes.

### Task 4: Optimize Fee Form Cold Generation

Expected changes:

- Keep the existing Excel lifecycle safety settings:
  - hidden Excel instance
  - alerts disabled
  - screen updating disabled
  - events disabled
  - manual calculation where available
  - workbook close and Excel quit in `finally`
- Profile or unit-test the slow helper boundaries.
- Reduce per-cell COM writes in `_write_matrix_basic_fill()` where safe:
  - build row values in Python first
  - write contiguous ranges in fewer COM calls when formulas/formatting do not require individual handling
  - avoid comment creation unless notes/review text exists
  - avoid repeated label scans after target rows are known
- Add a fake COM workbook/sheet counter or equivalent observable seam proving the optimized Matrix basic-fill writer performs fewer cell-value calls than the old row/cell loop for a representative workbook.
- Do not change workbook business values, formulas, or visible layout.
- If this task touches the Fee gateway implementation beyond small wiring changes, split focused writer helpers out of `fee_evaluation_workbook_gateway.py` before adding new behavior.

Acceptance:

- Existing Fee Form output tests still pass.
- Header placement remains cell-beside-label.
- Cold generation has fewer COM calls in the tested writer path, demonstrated by a fake COM call-count/counter test or equivalent.
- The Fee gateway file does not grow further beyond the existing project hard limit; substantial new behavior lives in focused helper modules.

### Task 5: Validate End-To-End Required Forms Behavior

Expected validation:

```powershell
py -m pytest tests/unit/test_customer_feedback_workbook_gateway.py tests/unit/test_customer_feedback_form_generation_service.py -q
py -m pytest tests/unit/test_fee_evaluation_workbook_gateway.py tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py -q
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
```

If frontend timing output changes:

```powershell
cd frontend; npm test -- --run ProjectWorkbenchLayout useProjectWorkbenchModel --watch=false
cd frontend; npm run build
```

Manual smoke:

- Record the baseline before optimization using the current implementation.
- Run `Update project folder` once after deleting/rebuilding the official folder and record timings.
- Run it again without changing Basic Information / Matrix / Fee and verify Fee Form reuse/current behavior.
- Confirm Customer Feedback `.xlsx`, Fee Form `.xls`, Test Record, and Application Form outputs are still present and readable.

## Risks

- `.xls` output cannot be written by `openpyxl`; replacing COM with Python would require a new dependency or an output-format decision and is not part of TASK_334.
- Excel COM timing varies heavily depending on whether Excel is cold-started, add-ins are loaded, or Office is recovering a previous session.
- Fee Form gateway is already larger than the project target size. TASK_334 must not grow it further with substantial implementation; focused helpers are required for new writer logic.
- Reuse must remain fingerprint/context-safe. Speed must not silently reuse stale Fee Form content after Basic Information, Matrix, or Fee authority changes.
- The total 70-second project folder update also includes Application Form Word COM write-back. TASK_334 can reduce the Excel portion, but total time may still need a follow-up Word optimization task.

## Out Of Scope

- Application Form Word COM write-back optimization.
- Replacing `.xls` Fee Form with `.xlsx`.
- Changing Fee calculation or Matrix/Fee authority behavior.
- Changing project folder conflict behavior.
- Report generation.
- Basic Information schema/API/persistence changes.
- StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.

## Approval Gate

Implementation may start only after the user explicitly approves `TASK_334_PROJECT_FOLDER_EXCEL_OUTPUT_PERFORMANCE`.

Until then, this task is plan-only.
