# TASK_307 Matrix Editor Test Record Draft Preview Entry - Executable Plan

## Summary

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_307_MATRIX_EDITOR_TEST_RECORD_DRAFT_PREVIEW_ENTRY`, complete.

TASK_307 was explicitly approved, implemented, and validated.

TASK_307 adds a `Test record` action to Matrix Editor so operators can download a Test Record draft from the current Matrix Editor page state at click time, including unconfirmed visible edits, for review. V1 captures that current page state by sending a bounded current UI state payload, following the Fee Evaluation `Fee Form` preview/export style. This is separate from the Workbench authority `Test record` action, which uses active Confirmed Matrix and is the version intended for later project-folder/package placement.

Mandatory frontend preconditions before implementation:

- Load `$impeccable` project context.
- Read `docs/02_ARCHITECTURE_RULES.md`.
- Read `docs/frontend_architecture_rules.md`.
- Treat this as a ConnLab product UI change.

## Task Understanding

Goal:

- Let users inspect a Test Record draft before Confirm Matrix by generating it from the current Matrix Editor page state at the moment they click the action.

Inputs:

- Matrix Editor project id.
- Current Matrix Editor page state, including unconfirmed visible edit content, captured directly from the UI state at click time.
- Existing Test Record template configuration and writer/gateway behavior.

Outputs:

- Matrix Editor shows a `Test record` action.
- Clicking it downloads a `.docx` draft generated from the Matrix Editor page state.
- UI copy makes clear this is a draft preview, not the Workbench authority version.

Modules likely involved:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- Matrix Editor action/header component(s), if split locally.
- `frontend/src/api/client.ts` if a new draft-source download endpoint is required.
- Backend application/API/gateway tests if an unconfirmed-draft generation path is required.
- `tests/unit/test_frontend_shell_files.py`

Not allowed:

- No public-drive placement.
- No package orchestrator.
- No ProjectOutputRecord registration for unconfirmed preview output.
- No Confirm Matrix side effect.
- No change to Workbench authority Test Record generation unless only copy clarification is needed.
- No Fee Form, Customer Feedback, evidence placement, StepInstance, report, AI, permissions, or multi-user scope.

## Key Source Distinction

TASK_307 must preserve this distinction:

```text
Matrix Editor Test record
  source: bounded current Matrix Editor UI state payload at click time, possibly unsaved/unconfirmed
  purpose: preview/download for operator review
  authority: not authoritative
  package placement: no

Workbench Test record
  source: active Confirmed Matrix authority
  purpose: official derived output candidate
  authority: active Matrix authority version
  package placement: future TASK_312/TASK_313
```

## Design

V1 source-state decision:

- Send a bounded current UI state payload, modeled after the Fee Evaluation `Fee Form` approach.
- Do not force-save the Matrix Editor draft before preview generation.
- Do not read an arbitrary latest saved draft and assume it matches the visible page.
- Do not send historical draft/revision data. The payload represents only the Matrix Editor page state visible at the moment the operator clicks `Test record`.
- Confirm Matrix remains the authority gate for official Workbench/package outputs.

Implementation should first inspect whether the existing Test Record document generation service can safely accept this current-state payload source.

If yes:

- Add a thin backend/API route or service method that generates from the bounded current UI state payload without marking output authority.
- Reuse existing Test Record writer/gateway.

If no:

- Add a bounded draft-source generation adapter that converts current Matrix Editor payload groups/rows/cells into the existing Test Record document writer input shape.
- Keep the adapter in application/backend boundaries, not in UI code.

Frontend:

- Add `Test record` action in Matrix Editor draft/action area.
- Disable or block it when the current page state has no previewable rows.
- Build the request from the current Matrix Editor UI state at click time, including dirty/unsaved visible edits if present.
- Do not require the draft to be saved before preview download.
- On success, download the returned `.docx`.
- Use copy that indicates unconfirmed draft preview when applicable.

Avoid:

- Adding the action to Workbench package/output area.
- Using active Confirmed Matrix when the operator expects the current unconfirmed editor draft.
- Reading/exporting historical draft versions or revision history when the operator expects the current page state.
- Writing files into project folders or public-drive targets.

## Data And API Contract

Preferred V1 behavior:

- Return a direct `.docx` response for browser download, similar to existing confirmed-Matrix Test Record draft download.
- Request identifies the current project and carries the bounded current Matrix Editor page state payload needed by the Test Record writer.
- The backend must generate from the payload exactly as supplied; it must not fall back to latest saved draft or active Confirmed Matrix.
- The payload should include only the current editor state needed for the draft: matrix identity context, groups, rows, step tokens/ordering, test item, section/method/condition/requirement fields, sample quantities, and any fields already visible/editable in Matrix Editor. It must not include historical revisions or revision lists.
- Response must not create ProjectOutputRecord.
- Response filename should include a preview marker, for example `{project_id}_matrix_editor_test_record_preview.docx` or an equivalent business-readable filename containing `Preview`.
- The document body should include a visible `Unconfirmed Matrix draft preview` marker when the source is not active authority, or the filename marker must be covered by tests if the document body cannot be changed safely in V1.

Potential API shape if needed:

```text
POST /api/projects/{project_id}/matrix-draft/test-record-draft/generate
```

The exact route can be adjusted during implementation, but it must clearly distinguish unconfirmed Matrix draft source from confirmed Matrix authority source.

Potential request model if needed:

```json
{
  "source": "matrix_editor_current_ui_state",
  "matrix_context": {
    "project_id": "project-id",
    "draft_id": "optional-current-draft-id-for-traceability-only"
  },
  "groups": [
    {
      "group_label": "1",
      "rows": [
        {
          "step_token": "1",
          "test_item": "Visual Examination",
          "section": "5",
          "method": "...",
          "condition": "...",
          "requirement": "...",
          "sample_quantity": "5"
        }
      ]
    }
  ],
  "preview_label": "Unconfirmed Matrix draft preview"
}
```

Do not accept historical draft/revision ids selected by the operator in TASK_307. A `draft_id`, if included, is traceability only and must not cause the backend to load that saved draft instead of using the supplied current-state payload.

## Tests

Frontend/static:

- Matrix Editor renders `Test record` action.
- Action copy indicates current Matrix page state / preview intent.
- Action is disabled or blocked without previewable current Matrix page state.
- Dirty/unsaved visible editor state is included in the generated current-state payload without requiring a save.
- Editing a visible Matrix value and immediately clicking `Test record` generates from the latest visible value, not from the pre-edit baseline or last saved draft.
- Static checks confirm Matrix Editor action does not call the confirmed-Matrix authority endpoint when generating an unconfirmed draft.
- Static or API tests confirm the action does not export all historical Matrix draft versions/revisions.
- Download filename or document content includes `Preview` / `Unconfirmed Matrix draft` wording.
- Workbench confirmed-Matrix Test Record behavior remains separate.

Backend/API if added:

- Current-state generation succeeds for Matrix editor rows/groups/steps.
- Backend generation uses supplied payload values even when they differ from the last saved draft.
- Missing current state returns actionable error.
- Empty/unpreviewable current state returns actionable error.
- Generation does not create ProjectOutputRecord.
- Generation does not create ConfirmedMatrixSnapshot.
- Generated download is visibly marked as preview/unconfirmed through filename or document content.
- Existing confirmed-Matrix Test Record generation tests continue to pass.

Run:

- `cd frontend; npm test -- --run MatrixEditorWorkspace TestRecord --watch=false`
- `cd frontend; npm run build`
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "matrix_editor or test_record"`
- Relevant backend tests if a route/service is added.
- `git diff --check`

## Risks And Guards

- Users may confuse unconfirmed draft preview with the Workbench authority Test Record. Mitigate with placement and copy.
- Sending the current Matrix page state from frontend duplicates some shape mapping, but this is acceptable for TASK_307 because the output is an unconfirmed preview and mirrors the already-accepted Fee Evaluation `Fee Form` preview/export interaction.
- Using a persisted draft id can export stale data. Guard by treating any draft id as traceability only and generating from the supplied payload.
- A downloaded file can be separated from the UI copy. Guard with `Preview` / `Unconfirmed Matrix draft` wording in filename or document content.
- Do not create hidden side effects. Generating a draft preview must not confirm Matrix, register output records, or publish to folder/public drive.
- If existing generation code is tightly coupled to Confirmed Matrix authority, add a small adapter rather than weakening authority semantics.

## Completion Criteria

- TASK_307 task file remains the source of implementation scope.
- Matrix Editor exposes `Test record` draft preview/download for current page state at click time through a bounded current UI state payload.
- The downloaded draft is visibly marked as preview/unconfirmed.
- Workbench authority Test Record remains semantically separate.
- Tests/build/checks pass.
- `docs/task_board.md` is updated to TASK_307 complete with validation results and the next task awaiting explicit approval.
