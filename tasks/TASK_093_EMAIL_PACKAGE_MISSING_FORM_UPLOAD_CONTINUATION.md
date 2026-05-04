# TASK_093_EMAIL_PACKAGE_MISSING_FORM_UPLOAD_CONTINUATION

## Status

done

## Goal

Allow an imported Outlook `.msg` intake package with no detected application form to continue by uploading a Word application form into the same package.

This closes the missing path where a valid request email and its attachments are stored, but no application form candidate exists. The uploaded application form must remain attached to the original email package so the later project can keep traceability to the source email, original attachments, and supplemental form.

## Inputs

- Existing `outlook_msg` intake package ID.
- Uploaded `.doc` or `.docx` application form.
- Existing package assets, including the stored source email and supporting attachments.

## Outputs

- New `IntakeAsset` in the existing package for the uploaded Word file.
- Selected application form review case and draft created through the existing form-selection path.
- Frontend session updated so `Continue to Precheck` opens the review case for the supplemental form.

## Modules

- `backend/application`
- `backend/api/routes_intake.py`
- `backend/api/dependencies.py`
- `frontend/src/api/client.ts`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/features/intake/*`
- `tests/integration`
- `tests/unit`

## Design

### Data Structure

No database schema change.

The supplemental form is represented as a normal `IntakeAsset`:

- `package_id`: existing `.msg` package ID
- `asset_role`: `selected_application_form` after selection
- `stored_path`: copied under the existing package storage root
- `extension`: `.doc` or `.docx`

### API

Add:

```text
POST /api/intake-packages/{package_id}/application-form
```

Request:

- multipart file field named `file`

Response:

- existing `SelectApplicationFormResponse`

### Application Service

Add `EmailPackageApplicationFormService`:

```python
def upload_application_form(package_id: str, source_path: Path) -> FormSelectionResult
```

Responsibilities:

1. Validate package exists.
2. Validate package source type is `outlook_msg`.
3. Validate uploaded file is `.doc` or `.docx` through `OfficeFacade`.
4. Copy file into the existing package storage.
5. Create an `IntakeAsset` in the same package.
6. Call `IntakeFormSelectionService.select_form_asset()` to parse, create/reuse case, and draft.

### Frontend

`Upload application form` becomes context-aware:

- If no package is loaded, keep current direct Word intake behavior.
- If a `.msg` package is loaded, upload the Word file into that existing package and update session assets with the returned selected asset.
- Do not add replacement flow, Outlook auto-scan, email sending, or multi-form management.

### User-Facing Copy

When a `.msg` package has no selected Word form:

```text
No application form found in this email. Upload the application form to continue with this email package.
```

## Acceptance Criteria

- Imported `.msg` package with no application form can continue after supplemental Word upload.
- The supplemental Word file is stored as an asset under the original package.
- The original source email and original attachments remain visible and managed in the package.
- `Continue to Precheck` opens the review case for the supplemental Word form.
- Direct no-email Word upload behavior remains unchanged when no package is loaded.
- Non-Word supplemental uploads are rejected with an actionable error.
- No Matrix, Report, AI review, LAN, permissions, Outlook inbox auto-scan, email sending, or copied-workbook LTR work is added.

## Validation

- Add focused backend integration tests for supplemental form upload into an existing `.msg` package.
- Add frontend static tests for context-aware upload wiring and no-form guidance.
- Run relevant pytest tests and frontend build.

## Completion Notes

- Added supplemental Word application-form upload into an existing Outlook `.msg` package.
- The uploaded form is stored as an `IntakeAsset` under the original package and selected through the existing Precheck case/draft path.
- The Intake UI now keeps direct Word upload behavior when no package is loaded, and switches to supplemental package upload when an email package is loaded.
- No future-scope features were added.
