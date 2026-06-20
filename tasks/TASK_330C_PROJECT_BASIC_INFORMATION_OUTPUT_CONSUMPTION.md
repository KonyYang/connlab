# TASK_330C_PROJECT_BASIC_INFORMATION_OUTPUT_CONSUMPTION

## Status

Draft task file ready for user review. Implementation not started.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed

TASK_330C depends on TASK_330A confirmed Basic Information authority and TASK_330B operator confirmation UI. It is not authorized until both are complete and the user explicitly approves output integration.

## Goal

Make formal project folder create/update consume the latest confirmed Basic Information snapshot.

## Core Behavior

- If no confirmed Basic Information snapshot exists, project folder create/update returns a backend blocker before file mutation.
- If a confirmed snapshot exists, formal output generators receive that snapshot.
- If Basic Information is reconfirmed, `Update project folder` can refresh formal outputs only when managed-output safety allows it.

## Formal Outputs

Use confirmed Basic Information for:

- Fee form base identity fields,
- Customer Feedback form base/contact/date fields,
- copied LTR application Word write-back fields.

## Refresh Safety

Reuse TASK_321 managed-output fingerprint semantics:

- Refresh only ConnLab-managed outputs.
- Recheck current disk fingerprint before replace.
- If unmanaged, manually edited, missing metadata, or fingerprint changed, return conflict/block.
- Do not overwrite user-edited files.
- Stage before final placement.
- Output records must include Basic Information version/signature context.

## In Scope

- Project folder create/update blocker for missing confirmed Basic Information.
- Required forms generation consuming confirmed Basic Information.
- Copied application Word write-back consuming confirmed Basic Information.
- Output records including Basic Information version/signature context.
- Unit/API tests for blocker, consumption, and safe refresh.

## Out Of Scope

- No Basic Information editor UI changes.
- No source assembly changes beyond reading TASK_330A confirmed snapshot.
- No LTR workbook writeback.
- No report generation.
- No public-drive upload redesign.
- No Matrix/Fee authority semantic changes.

## Acceptance Criteria

- Project folder create/update blocks without confirmed Basic Information and does not mutate files.
- Fee form receives and writes Basic Information base identity fields.
- Customer Feedback form receives and writes Basic Information base/contact/date fields.
- Copied application Word document in Submitted Material receives known Basic Information fields.
- Reconfirmed Basic Information can trigger output refresh only when managed-output fingerprints are safe.
- Manually edited or unmanaged target files block instead of being overwritten.
- Output records expose which Basic Information version/signature was used.

## Validation

```powershell
py -m pytest tests/unit/test_project_folder_required_forms_service.py -q
py -m pytest tests/unit/test_official_project_workspace_service.py -q
py -m pytest tests/integration/test_official_project_workspace_api.py -q
```

Manual smoke:

- Confirm Basic Information.
- Run `Generate/Update project folder`.
- Verify Fee form, Customer Feedback form, and copied Word application contain confirmed values.
- Manually alter one generated file.
- Reconfirm Basic Information and click `Update project folder`.
- Verify the altered file blocks instead of being overwritten.

## Stop Point

Stop after TASK_330C is implemented and validated. Do not proceed to LTR workbook writeback, report generation, StepInstance, AI, permissions, LAN, or multi-user scope without a separate approved task.
