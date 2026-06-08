# TASK_301 Fee Pricing Draft Persistence

Status: Complete.

Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Allowed reason: TASK_298, TASK_299, and TASK_300 are complete. The approved TASK_298-TASK_302 series defines TASK_301 as the next controlled step: persist and reload operator-edited Fee Evaluation pricing draft values. Implementation was performed only after explicit user approval.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task. TASK_301 is a bounded full-stack persistence task with existing typed edit payloads, stable Matrix basic-fill row identity, FastAPI route patterns, SQLite repositories, and frontend Fee Evaluation state already in place. It is suitable for adding a narrow persistence read/write model, validation, and UI save/reload behavior. It is not suitable for inventing pricing policy, rule-reference maintenance, multi-user permissions, or Excel template redesign inside this task.

## Goal

Persist the operator's Fee Evaluation pricing draft edits so that reopening the Fee Evaluation page restores the latest saved values for the current active Confirmed Matrix authority version and active fee rule version.

TASK_301 makes ConnLab a reliable working surface for fee preparation before export. It remains draft persistence only.

## Input Data

Existing TASK_299/TASK_300 Fee Evaluation page edit state:

- matrix-step row values:
  - stable row identity matching backend Matrix basic-fill step-expanded rows:
    - `source_line_id`
    - `confirmed_group_id`
    - `confirmed_row_id`
    - `step_token`
    - `step_index`
  - `Man-hour`
  - `Unit Price`
  - `Unit Type`
  - `Units`
  - `Base Fee`
  - `Discount`
  - calculated `Testing Fee`
  - `Notes`
- manual row values:
  - `Report preparation`
- summary values:
  - `Condition confirmation`
  - `External Cost`
  - `External Cost` note
  - Lab manpower hourly rate

Server authority inputs:

- active Confirmed Matrix authority id and revision
- active fee rule version id
- TASK_286/TASK_290/TASK_300 row identity rules

## Output Data

- A persisted Fee Evaluation pricing draft tied to:
  - `project_id`
  - active `confirmed_matrix_id`
  - active `confirmed_revision`
  - active fee rule version id
- API response that can reload the saved edit payload into the Fee Evaluation page.
- Frontend save/load state:
  - no saved draft
  - saved for current Matrix and fee rule version
  - stale/not applicable because active Confirmed Matrix or fee rule version changed
  - save error

## Scope

In scope:

- Add a backend application service for Fee Evaluation pricing draft persistence.
- Add SQLite persistence for the edit payload.
- Add typed API routes to load and save the current project's Fee Evaluation pricing draft.
- Validate saved row identities against the current backend Matrix basic-fill rows before accepting a save.
- Reload saved values into the Fee Evaluation page after the TASK_286 fee draft and page context load.
- Add a simple explicit `Save changes` action and saved/unsaved/error status copy.
- Keep `Fee Form` export using the current page state; saved values become current page state after reload.

Out of scope:

- No automatic pricing-rule maintenance.
- No TASK_302 Unit Price Reference update workflow.
- No Excel template layout changes.
- No automatic export after save.
- No project-output record changes.
- No StepInstance, execution persistence, report generation, AI review, permission system, or multi-user conflict workflow.
- No attempt to merge stale edits across different active Confirmed Matrix authority versions or fee rule versions.

## Stale And Compatibility Policy

- V1 saved drafts are valid only when all of the following match the current authority context:
  - active Confirmed Matrix id
  - active Confirmed Matrix revision
  - active fee rule version id
- If no saved draft exists, the page uses current preview defaults from TASK_299.
- If a saved draft exists for an older Matrix authority or older fee rule version, the API should report it as stale/not applicable and the frontend should keep current defaults.
- TASK_301 should not silently apply stale edits to a new Matrix authority or a new fee rule version.
- If row identity validation fails during save, return an actionable error and do not persist partial edits.

## Notes Requirement

`Notes` is a real editable field from user requirements and TASK_300 export behavior. TASK_301 must persist row-level Notes and restore them exactly as draft text. Blank Notes are valid.

## Acceptance Criteria

- Opening Fee Evaluation with no saved edits keeps TASK_299 defaults.
- Saving edited rows and summary values persists them for the current active Confirmed Matrix.
- Reopening the page restores saved row values, manual row values, summary values, and Notes.
- Saving rejects duplicate or unknown row identities.
- Saved edits are not applied after active Confirmed Matrix id/revision or active fee rule version changes.
- Saved backend payload rows are mapped back into frontend edit state through the current preview row stable identity tuple, not by local `lineId` alone.
- `Fee Form` export after reload uses restored saved values because they are loaded into current page state.
- Existing no-body direct download compatibility remains.

## Validation

Expected implementation validation:

- Backend unit tests for persistence service:
  - save/load current Matrix and fee rule version draft
  - no saved draft
  - stale Matrix draft not applied
  - stale fee rule version draft not applied
  - duplicate/unknown row identity rejected
  - Notes preserved
- Repository/API tests:
  - save endpoint persists payload
  - load endpoint returns current payload
  - stale saved payload is reported without applying values when Matrix or fee rule version changes
- Frontend tests:
  - saved values load into preview state
  - saved rows map through stable identity tuple into `FeeEvaluationPreviewEditState`
  - unmatched saved rows are not applied and produce stale/validation copy
  - `Save changes` sends edited payload
  - save success/error states render
  - reload/project change reset logic remains correct
- Regression:
  - TASK_300 export tests remain passing
  - `npm run build`
  - `git diff --check`
