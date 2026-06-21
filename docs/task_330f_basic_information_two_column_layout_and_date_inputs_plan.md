# TASK_330F Basic Information Two-Column Layout And Date Inputs Plan

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Current Active Task ID

`TASK_330F_BASIC_INFORMATION_TWO_COLUMN_LAYOUT_AND_DATE_INPUTS`

## Why This Task Is Allowed Now

`TASK_330E_PROJECT_FOLDER_REQUIRED_FORMS_BLOCKER_REMINDER_HOTFIX` is complete. The user requested a Basic Information page usability improvement after using the page directly. This task is a separately scoped frontend UI task and does not change Basic Information backend authority rules.

## Scope

### In Scope

- Basic Information page grouping and layout.
- Field config changes for grouping and date control type.
- CSS changes for two functional panels.
- Frontend tests for field placement and date inputs.

### Out Of Scope

- Backend Basic Information schema/API/persistence.
- Extraction rules from application forms.
- Required-field rules.
- Project Folder generation.
- Office write-back/template behavior.
- Report/StepInstance/AI/permissions/LAN/multi-user work.

## Design

### Layout

Keep the existing Basic Information route and autosave model. Replace the current stacked group rendering with a two-column content area:

- Left panel: application/source-facing information.
- Right panel: lab-facing information and schedule.

The project identity is displayed once inside the left `Product and request` panel. The duplicate visible DL/LTR Number input is not rendered, while `dl_number` stays in the draft values for API payload compatibility.

### Field Grouping

Use the existing field config boundary instead of hard-coding JSX.

Left panel groups:

- Product information:
  - Project Type
  - Description P/N
  - Product Description
  - Test Item
  - Applicable Specifications
  - Test Type
- Requester/application information:
  - Requested by
  - Phone
  - E-mail of Requestor
  - Location
  - Sub-contract

Right panel groups:

- Laboratory ownership:
  - Project Leader
  - Lab Performing the Tests
- Test/result and commercial:
  - Test Result
  - Failed Item
  - Sample Deposition
  - Test Fee
  - Remarks (PO)
  - Condition of Samples when Received
- Schedule:
  - Date Lab Received Samples
  - Estimated Completion Date
  - Start Test Date
  - Finish Test Date
  - Report Date

### Date Inputs

Change the five schedule field configs from `kind: "text"` to `kind: "date"`.

Compatibility requirement: existing business date strings such as `20 Jun 2026` must remain visible after the date-control change. Native date inputs expect `YYYY-MM-DD`, so implementation must either:

- normalize known business date strings to ISO format for the native date input while keeping the existing autosave payload behavior predictable; or
- use a documented fallback that avoids blanking known non-ISO date values.

Do not ship a date-control implementation that makes an existing known date appear empty.

### CSS

Use existing ConnLab product styling:

- Two columns on desktop.
- Stack to one column at the existing responsive breakpoint.
- Keep cards/panels flat with existing `basic-information-surface` vocabulary.
- Avoid modal or decorative treatment.

## File-Level Changes

Planned files:

- `frontend/src/features/project-basic-information/basicInformationFieldConfig.ts`
  - Rename/regroup fields and switch schedule date fields to `date`.
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx`
  - Render two functional panels from config.
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`
  - Add tests for panel grouping and date input type.
- `frontend/src/workbench.css`
  - Add/adjust Basic Information layout classes.

No backend files are planned.

## Risks

- Browser native date inputs may not display existing non-ISO date strings. Test coverage should catch this. If the current persisted value is non-ISO, do not silently alter it unless a narrow conversion is explicitly implemented in the model.
- Moving `Sub-contract` from result/commercial to application/source-facing information changes visual grouping only, not data semantics.
- Avoid making the page too card-heavy; use two functional panels, not nested cards.

## Validation Plan

```powershell
cd frontend
npm test -- --run ProjectBasicInformation --watch=false
npm run build
```

Manual smoke:

1. Open `/projects/{project_id}/basic-information`.
2. Confirm left panel contains product/requester/application information.
3. Confirm right panel contains laboratory/result/commercial/schedule information.
4. Confirm date fields open native date selection and still autosave through the existing model.
5. Confirm Confirm/Cancel behavior remains unchanged.

## Completion

`TASK_330F_BASIC_INFORMATION_TWO_COLUMN_LAYOUT_AND_DATE_INPUTS` is complete, including duplicate DL field and compact identity follow-ups.

Implemented:

- Basic Information page renders two functional panels:
  - `Product and request`
  - `Laboratory execution`
- Product/request panel contains product scope, requester information, and `Sub-contract`.
- Laboratory execution panel contains lab ownership, result/commercial state, sample condition, and schedule dates.
- Schedule fields now render as native date inputs.
- Existing business date strings such as `20 Jun 2026` are normalized to ISO display values for native date inputs instead of appearing blank.
- The duplicate visible `DL/LTR Number` readonly input was removed.
- The project identity was moved from a standalone header card into the `Product and request` panel to reduce wasted vertical space; `dl_number` remains in the existing model values and confirm payload.
- The redundant visible `Product and request` panel title was removed while retaining the panel's accessibility label.
- The redundant visible `Product and request` helper sentence was removed so the card starts directly with the project identity and field groups.
- The visible left-panel identity now shows only the project number in regular weight.
- The redundant visible `Product information` group title was removed from the left panel.
- `Product Description` was moved directly below the project number and its input width is aligned with `Project Type`.
- Basic Information textarea fields now auto-size their height to the current content line count.
- `Test Item` was moved beside `Product Description` and uses the same compact auto-height textarea treatment.
- `Applicable Specifications` was moved below `Product Description` and uses the same compact auto-height textarea treatment.
- `Description P/N` was moved beside `Applicable Specifications`.
- `Project Type` now uses the same six-option dropdown used by the New Project flow.
- `Test Type` now uses the same four-option dropdown used by the New Project flow.
- `Sub-contract` now uses a Yes/No radio choice instead of free text.
- `Sub-contract` was moved beside `Test Type`; `Project Type`, `Test Type`, and `Sub-contract` now share one compact row.
- The redundant visible `Requester information` group title was removed from the left panel.
- The persistent completion-dock helper sentence was removed; only the transient saving status remains when autosave is active.
- The redundant visible `Laboratory execution` panel title was removed while retaining the panel's accessibility label.
- The redundant visible `Laboratory execution` helper sentence was removed.
- The redundant visible `Laboratory ownership` group title was removed from the right panel.
- The redundant visible `Result and commercial` group title was removed from the right panel.
- The redundant visible `Schedule` group title was removed from the right panel while keeping the schedule date fields.
- `Project Leader` was shortened and `Lab Performing the Tests` was placed beside it on the same row.
- `Lab Performing the Tests` was changed from free text to a dropdown with `Choose an item.`, `Dongguan`, and `Valley Green` while preserving existing non-standard values as selectable current values.
- `Requested by`, `Phone`, `E-mail of Requestor`, and `Location` were shortened into one compact requester row.
- The requester row was rebalanced so `Location` is narrower and `E-mail of Requestor` receives the extra width.
- `Location` was changed to a dropdown using the same manufacturing-site options as the New Project `Mfg. Site` selector.
- `Phone` and `E-mail of Requestor` positions were swapped in the compact requester row.
- The visible `Location` label was renamed to `Mfg. Site` while keeping the existing `location` payload key.
- The remaining New Project application-form fields were added below the requester row: `Business Unit`, `Project #`, `Results Format`, `Requested Completion Date`, `Test Sample Status`, `Post-Testing Sample Disposition`, and `Send copies of test results/reports to`.
- `Results Format` was moved to the first position in the added application-form detail fields.
- `Confidential test or samples?` was added as a required Yes/No radio beside `Send copies of test results/reports to`, reusing the existing `confidential` payload key.
- The non-actionable `Draft saved automatically.` success status was hidden while keeping error, missing-required, source-review, and transient saving feedback available.
- `Test Result` was changed from free text to a fixed dropdown with `OK`, `Ref`, `NG`, `In progress`, and `In-waiting`.
- Existing autosave, Confirm, Cancel, missing-required, and source-review behavior remains unchanged.

Validation:

```powershell
cd frontend
npm test -- --run ProjectBasicInformation --watch=false
# 8 passed

npm run build
# passed
```
