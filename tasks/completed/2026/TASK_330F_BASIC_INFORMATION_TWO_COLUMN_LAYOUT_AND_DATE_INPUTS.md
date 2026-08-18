# TASK_330F_BASIC_INFORMATION_TWO_COLUMN_LAYOUT_AND_DATE_INPUTS

## Status

Complete, including duplicate DL field and compact identity follow-ups.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed

TASK_330E_PROJECT_FOLDER_REQUIRED_FORMS_BLOCKER_REMINDER_HOTFIX is complete and stopped at the approved boundary. The user requested a narrow Basic Information page usability improvement:

- split Basic Information into two functional areas;
- keep product/request/application-form-derived information separate from laboratory execution information;
- render date fields as date-selectable controls.

This is a frontend Basic Information layout/control task only.

## Goal

Improve the Basic Information page so operators can scan and edit the form in two clear columns:

1. Product and requester/application information.
2. Laboratory information, result/commercial state, and schedule dates.

Also render schedule fields as date inputs.

## In Scope

- Frontend Basic Information page layout.
- Basic Information field grouping/configuration.
- Basic Information page CSS for two side-by-side functional panels with responsive stacking on narrow screens.
- Date controls for:
  - Date Lab Received Samples
  - Estimated Completion Date
  - Start Test Date
  - Finish Test Date
  - Report Date
- Frontend tests proving the new grouping and date input behavior.

## Out Of Scope

- No backend Basic Information schema/API/persistence changes.
- No field extraction/source-provider changes.
- No Basic Information required-field rule changes.
- No Project Folder output behavior changes.
- No Office generation, Word/Excel write-back, LTR workbook, report, StepInstance, AI, permissions, LAN/server, or multi-user scope.
- No broad Workbench redesign.

## Acceptance Criteria

- Basic Information still loads, autosaves, confirms, and cancels with the existing API payload.
- Left panel groups application/source-facing fields such as product/project/requester/sub-contract details.
- Right panel groups lab-facing fields such as Project Leader, Lab Performing the Tests, Test Result, Failed Item, Sample Deposition, Test Fee, Remarks (PO), sample condition, and schedule dates.
- Date schedule fields render as `type="date"` inputs.
- Existing business date strings such as `20 Jun 2026` remain visible after the date-control change, either through ISO normalization for the native control or through a documented fallback that avoids blanking known date values.
- Existing read-only DL/LTR Number remains read-only.
- Duplicate visible DL/LTR Number input is removed; the project identity is shown once inside the `Product and request` panel, while `dl_number` remains in the draft/confirm payload.
- Responsive layout stacks the two panels on smaller widths.
- Existing missing-required and source-review warnings remain visible.

## Validation

Completed validation:

```powershell
cd frontend
npm test -- --run ProjectBasicInformation --watch=false
# 8 passed

npm run build
# passed
```

Follow-up completed:

- Removed the duplicate visible `DL/LTR Number` readonly field from the Basic Information page.
- Moved the project identity from a standalone header card into the `Product and request` panel to reduce wasted vertical space.
- Removed the redundant visible `Product and request` panel title while retaining the panel's accessibility label.
- Removed the redundant visible `Product and request` helper sentence so the card starts directly with the project identity and field groups.
- Changed the visible left-panel identity to show only the project number in regular weight.
- Removed the redundant visible `Product information` group title from the left panel.
- Moved `Product Description` directly below the project number and kept its input width aligned with `Project Type`.
- Basic Information textarea fields now auto-size their height to the current content line count.
- Moved `Test Item` beside `Product Description` and applied the same compact auto-height textarea treatment.
- Moved `Applicable Specifications` below `Product Description` and applied the same compact auto-height textarea treatment.
- Moved `Description P/N` beside `Applicable Specifications`.
- Changed `Project Type` to the same six-option dropdown used by the New Project flow.
- Changed `Test Type` to the same four-option dropdown used by the New Project flow.
- Changed `Sub-contract` from free text to a Yes/No radio choice.
- Moved `Sub-contract` beside `Test Type`; `Project Type`, `Test Type`, and `Sub-contract` now share one compact row.
- Removed the redundant visible `Requester information` group title from the left panel.
- Removed the persistent completion-dock helper sentence; only the transient saving status remains when autosave is active.
- Removed the redundant visible `Laboratory execution` panel title while retaining the panel's accessibility label.
- Removed the redundant visible `Laboratory execution` helper sentence.
- Removed the redundant visible `Laboratory ownership` group title from the right panel.
- Removed the redundant visible `Result and commercial` group title from the right panel.
- Removed the redundant visible `Schedule` group title from the right panel while keeping the schedule date fields.
- Shortened `Project Leader` and placed `Lab Performing the Tests` beside it on the same row.
- Changed `Lab Performing the Tests` from free text to a dropdown with `Choose an item.`, `Dongguan`, and `Valley Green` while preserving existing non-standard values as selectable current values.
- Shortened `Requested by`, `Phone`, `E-mail of Requestor`, and `Location` into one compact requester row.
- Rebalanced the requester row so `Location` is narrower and `E-mail of Requestor` receives the extra width.
- Changed `Location` to a dropdown using the same manufacturing-site options as the New Project `Mfg. Site` selector.
- Swapped `Phone` and `E-mail of Requestor` positions in the compact requester row.
- Renamed the visible `Location` label to `Mfg. Site` while keeping the existing `location` payload key.
- Added the remaining New Project application-form fields below the requester row: `Business Unit`, `Project #`, `Results Format`, `Requested Completion Date`, `Test Sample Status`, `Post-Testing Sample Disposition`, and `Send copies of test results/reports to`.
- Moved `Results Format` to the first position in the added application-form detail fields.
- Added `Confidential test or samples?` as a required Yes/No radio beside `Send copies of test results/reports to`, reusing the existing `confidential` payload key.
- Hid the non-actionable `Draft saved automatically.` success status while keeping error, missing-required, source-review, and transient saving feedback available.
- Changed `Test Result` from free text to a fixed dropdown with `OK`, `Ref`, `NG`, `In progress`, and `In-waiting`.
- Kept `dl_number` in the existing model values so confirm payload compatibility remains unchanged.

## Stop Point

Stop after TASK_330F is implemented and validated. Do not proceed to backend source-provider changes, output generation changes, Office automation, report generation, StepInstance, AI, permissions, LAN/server, or multi-user scope without a separate approved task.
