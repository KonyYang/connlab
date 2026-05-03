# TASK_088 Attachment Details Preview Completion

## Status

Done

## Phase

Phase 10A - Intake Entry Completion

## Goal

Complete the Intake `Attachment details` area for real business use by showing practical previews or clear metadata for selected attachments.

## Inputs

- Stored intake assets from `.msg` or direct `.docx` intake.
- Existing `/api/intake-assets/{asset_id}/preview` endpoint.
- Existing Intake page attachment selection state.

## Outputs

- Image attachments display a safe inline image preview.
- Application-form Word documents keep structured business preview focused on SECTION 1 and sample/requested-testing content.
- Non-application Word, Excel, PDF, `.msg`, and other attachments show simple metadata guidance instead of a misleading unavailable state.
- Local stored paths remain hidden from API responses.

## Allowed Scope

- Extend the preview service response model with optional image data URL and preview metadata fields.
- Update API DTO and frontend API types.
- Update Intake `AttachmentPreview` rendering and scoped CSS.
- Add/update focused unit, integration, and frontend static tests.
- Update `docs/task_board.md` when complete.

## Out Of Scope

- Full Excel grid rendering.
- Full PDF rendering.
- Nested `.msg` parsing or attachment extraction from `.msg` attachments.
- Full Word rendering for non-application documents.
- Download implementation.
- Precheck business changes.
- Workflow shell unification.
- Intake feature-folder structural extraction.
- Outlook inbox auto-scan, email sending, copied workbook write, Matrix, Report, AI review, LAN deployment, or permissions.

## Acceptance Criteria

- Existing application-form DOCX preview still works and hides local paths.
- DOCX preview no longer shows generic document structure.
- Image attachment preview returns and renders a data URL.
- Non-image unsupported business files return `metadata_only` with actionable operator text.
- Frontend shows metadata rows for metadata-only previews.
- No direct `fetch()` is added outside `frontend/src/api/client.ts`.
- `npm run build` passes.
- Relevant pytest tests pass.
