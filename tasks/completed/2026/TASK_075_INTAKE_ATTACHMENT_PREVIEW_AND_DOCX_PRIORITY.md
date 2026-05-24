# TASK_075_INTAKE_ATTACHMENT_PREVIEW_AND_DOCX_PRIORITY

## Status

done

## Goal

Stabilize the New Project Intake attachment details workspace by showing a real preview for the selected attachment, with `.docx` Laboratory Testing Request preview implemented first because it is the business-critical step for confirming the correct application form before Precheck.

## Why This Task Is Allowed Now

- Current board state is Phase 10A complete with no active implementation task.
- The user explicitly approved adding this controlled task before moving to the next phase.
- The work is still within the approved MVP intake/precheck scope.
- This task does not advance copied-workbook LTR write hardening or future Matrix/Report/AI scope.

## Reference Application Form

User-provided local baseline:

```text
D:\TestFlowManager\Template\E-3718_H Laboratory Test Request-Even.docx
```

Observed baseline characteristics:

- Standardized Laboratory Testing Request template.
- Template revision is stable except for minor version/number updates.
- The document is table-driven rather than paragraph-driven.
- Local inspection found 5 non-empty paragraphs and 18 Word tables.
- Key requestor, sample, requested testing, disposition, additional information, and Yes/No fields should be previewed from the Word table structure.

The reference file is a local operator baseline only. Do not commit the original file into the repository unless the user explicitly approves that.

## Scope

Backend:

- Add a safe intake asset preview application service.
- Add an API endpoint for previewing a registered intake asset by `asset_id`.
- Look up the asset through the intake asset repository. Do not accept arbitrary file paths from the frontend.
- Do not expose `stored_path` to the frontend.
- Implement `.docx` preview first using deterministic parsing.
- Reuse or align with the existing application form parser where practical, instead of creating a second conflicting extraction path.
- Return a typed preview response with:
  - preview kind
  - file metadata
  - parsed field summary
  - table/section preview rows
  - parser warnings
  - unsupported/error state where applicable

Frontend:

- Replace the current placeholder preview in `Attachment details` with preview data loaded from the backend when the selected attachment changes.
- Render `.docx` preview as a structured application-form preview:
  - filename and file type
  - business field summary
  - sample rows
  - requested testing rows
  - disposition/confidential/subcontract values
  - additional information preview
- Keep Word-only radio selection behavior unchanged.
- Show clear loading, empty, unsupported, and error states.
- Maintain the existing ConnLab product UI style and 14-inch laptop fit.

## Out Of Scope

- No high-fidelity Word page rendering.
- No Office COM preview automation.
- No editing Word content from the preview.
- No template update/write-back.
- No Outlook inbox auto-scan.
- No email sending.
- No LTR Number allocation or copied-workbook write changes.
- No Matrix, Report, AI review, LAN deployment, or permissions.

## Preview Type Policy

MVP priority order:

1. `.docx`: structured Laboratory Testing Request preview, implemented in this task.
2. Image/PDF: may return safe content metadata or simple preview support if low-risk, but should not delay `.docx`.
3. `.xlsx`, `.pptx`, `.msg`, and unknown binary files: return explicit unsupported/metadata preview unless a small, deterministic summary already exists.

## Design Notes

- The `.docx` preview exists to help the operator answer: "Is this the correct Laboratory Testing Request to use for Precheck?"
- The preview should emphasize business-recognizable content, not exact Word layout.
- If parsing is partial, show the sections that were parsed and surface warnings. Partial preview should not block selecting the Word file.
- The selected Word used for preview and the selected Word sent to Precheck must remain the same `asset_id`.
- UI copy should avoid backend terms such as `asset_id` except in developer-only logs or tests.

## Implementation Plan

1. Add typed preview DTOs in the intake API layer.
2. Add an application service that resolves one registered intake asset and dispatches preview by extension/MIME type.
3. Implement `.docx` structured preview using existing parser output plus table summaries where needed.
4. Add frontend API client method for asset preview.
5. Update `IntakeInboxPage` so selected attachment changes trigger preview loading.
6. Replace placeholder paper preview with typed preview components.
7. Add tests and update frontend smoke checklist.

## Validation

Backend tests:

- `.docx` asset preview returns structured fields and table/section preview.
- Missing asset returns a typed 404 or actionable error.
- Unsupported asset returns an unsupported preview response, not a server error.
- Preview service never returns local storage paths.

Frontend/static tests:

- Intake page has `.docx` preview loading, success, unsupported, and error states.
- Attachment details remains connected to selected attachment state.
- Word-only application-form selection remains present.

Manual smoke:

1. Import one `.msg` package.
2. Click each attachment and confirm `Attachment details` updates for that attachment.
3. Click a `.docx` application form and confirm business fields and sample/requested-testing preview are visible.
4. Select that Word file as the application form.
5. Continue to Precheck and confirm Precheck uses the same selected Word data.

## Stop Condition

Stop after TASK_075 validation and board update. Do not proceed into LTR Number or Project Folder implementation without explicit user approval.

## Completion Notes

- Added a safe intake asset preview service and API endpoint for registered intake assets.
- Implemented `.docx` Laboratory Testing Request preview as structured fields, sample table, requested testing table, and document structure outline.
- Kept Office handling behind the existing parser/module boundary; application and API layers do not import Office libraries directly.
- Updated New Project Intake so selecting an attachment loads a real preview state in `Attachment details`.
- Non-Word attachments now show explicit unsupported/metadata preview instead of the previous fake document preview.
- Updated frontend smoke checklist for Intake attachment preview verification.

## Validation Result

- `py -m pytest tests\unit\test_intake_asset_preview_service.py tests\integration\test_msg_package_intake_api.py tests\unit\test_frontend_shell_files.py -q`: `31 passed`
- `npm run build` from `frontend/`: passed
- `py -m pytest tests\unit\test_office_integration_boundary.py tests\unit\test_intake_asset_preview_service.py tests\integration\test_msg_package_intake_api.py -q`: `15 passed`
- `py -m pytest tests\unit\test_application_form_parser.py -q`: `5 passed`
