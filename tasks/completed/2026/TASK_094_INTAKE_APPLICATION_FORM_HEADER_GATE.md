# TASK_094_INTAKE_APPLICATION_FORM_HEADER_GATE

## Status

done

## Current Phase

Phase 10A is complete. This task is a proposed controlled follow-up for the Intake to Precheck entry gate.

## Active Task Rule

Do not implement this task until `docs/task_board.md` explicitly marks `TASK_094_INTAKE_APPLICATION_FORM_HEADER_GATE` as the current active task or a ready task approved by the user.

When active, this task is allowed because it stays inside the MVP Intake and Precheck flow:

- Project stage: Intake before Precheck review.
- Input: selected intake Word attachment.
- Output: application-form eligibility result, disabled reason, selected Precheck case only when eligible.
- Domain impact: `IntakeAsset`, `IntakeCase`, `IntakeDraft`; no new future-scope domain object.
- MVP scope: application form intake and precheck only.

## Goal

Prevent `Continue to Precheck` from activating unless the selected document is a valid `.docx` Laboratory Testing Request application form.

A selected file is eligible only when:

1. The selected asset extension is `.docx`.
2. The Word document page header table cell `(1,2)` contains:

```text
Laboratory Testing Request
```

The validation must be authoritative in the backend. The frontend should display a concise disabled reason so an operator can quickly understand whether the issue is file extension, wrong document, changed header content, unreadable Word content, or missing Microsoft Word automation.

## Background

Current behavior is too permissive:

- `Continue to Precheck` activates when `selectedApplicationForm` exists.
- Frontend Word detection accepts `.doc` and `.docx`.
- Backend form selection allows `.doc` or `.docx`, or an existing application-form candidate role.
- Existing `WordDocumentGateway` uses `python-docx` and flattens header content, but the new gate depends on a precise header table coordinate: row 1, column 2.

Real Word documents may have section headers, linked headers, compatibility-mode structures, or complex header tables. Use Microsoft Word COM through the Office facade/gateway boundary for the authoritative header cell check.

## Inputs

- Existing intake package ID.
- Selected intake asset ID.
- Stored `.docx` file path from the intake asset record.
- Expected header marker text:

```text
Laboratory Testing Request
```

## Outputs

- Structured application-form eligibility result.
- Backend log entry with diagnostic context.
- Frontend disabled state and business-readable reason.
- Precheck review case and draft only when the selected asset passes the gate.

## Modules

- `backend/infrastructure/office/*`
- `backend/application/intake_form_selection_service.py`
- `backend/application/direct_word_intake_service.py`
- `backend/application/email_package_application_form_service.py`
- `backend/application/intake_candidate_service.py`
- `backend/api/routes_intake.py`
- `backend/api/dependencies.py`
- `frontend/src/api/client.ts`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/features/intake/*`
- `tests/unit`
- `tests/integration`

## Required Read Order

Before implementation, read:

1. `AGENTS.md`
2. `docs/task_board.md`
3. `tasks/TASK_094_INTAKE_APPLICATION_FORM_HEADER_GATE.md`
4. `docs/project_management/TASK_EXECUTION_SKILL.md`
5. `docs/project_management/TASK_REVIEW_CHECKLIST.md`
6. `docs/02_ARCHITECTURE_RULES.md`
7. `docs/frontend_architecture_rules.md`
8. `PRODUCT.md`
9. `DESIGN.md`

Use `$impeccable` before frontend/UI or UX-copy changes.

## Design

### Backend Eligibility Result

Add a small structured result for the gate. Keep it in application or infrastructure DTO boundaries, not in domain unless a domain need appears.

Recommended shape:

```python
@dataclass(frozen=True, slots=True)
class ApplicationFormEligibility:
    eligible: bool
    reason_code: str
    message: str
    observed_header_cell: str | None = None
    expected_text: str = "Laboratory Testing Request"
```

Recommended reason codes:

- `ok`
- `missing_asset`
- `not_docx`
- `header_cell_empty`
- `header_cell_mismatch`
- `word_automation_unavailable`
- `word_header_unreadable`

### Office Facade Boundary

Add the Word header gate behind `OfficeFacade`.

Recommended facade method:

```python
def inspect_laboratory_testing_request_header(self, source_path: Path) -> WordHeaderGateResult:
    ...
```

or:

```python
def read_word_header_table_cell(self, source_path: Path, row: int, column: int) -> str | None:
    ...
```

Implementation rules:

1. Do not call COM from API routes, frontend, domain, or parser code.
2. Use `OfficeFacade -> Word gateway -> Word COM lifecycle/helper`.
3. Use Microsoft Word COM for the authoritative `(1,2)` header table cell read.
4. Keep the Word application hidden.
5. Open the document read-only.
6. Disable alerts.
7. Close the document and quit the Word application in `finally`.
8. Clean Word control characters such as `\r`, `\x07`, and repeated whitespace.
9. Never write to or save the selected document.

Recommended COM behavior:

```text
Word.Application via DispatchEx
Documents.Open(path, ReadOnly=True, AddToRecentFiles=False)
Sections -> Headers -> Tables -> Cell(1, 2).Range.Text
```

Check primary, first-page, and even-page headers where available. Passing any applicable header cell containing the expected text is enough.

### Application Service Rule

Backend selection remains authoritative.

`IntakeFormSelectionService.select_form_asset()` must reject an asset before case/draft creation when:

- extension is not `.docx`
- the Word header gate fails
- the selected asset belongs to the wrong package
- the selected asset is an ignored/email-source asset

Do not rely on frontend disabled state as business truth.

### Candidate Detection Rule

Update application-form candidate handling so false candidates are less likely to appear as selectable:

- `.docx` and header gate passes: eligible application-form candidate.
- `.docx` and header gate fails: supporting attachment or unknown, with diagnostic reason available.
- `.doc`: not eligible for Precheck entry in this task.
- non-Word files: not eligible.

If candidate detection cannot safely run COM during package import because of performance or Office availability, keep import tolerant but enforce the gate during explicit selection. In that case, the frontend must display selection failure cleanly.

### API Contract

Prefer adding eligibility information to package detail/assets or a focused validation endpoint only if needed by the frontend.

Acceptable options:

1. Add eligibility fields to intake asset DTOs:

```json
{
  "application_form_eligible": false,
  "application_form_ineligible_reason": "header_cell_mismatch",
  "application_form_header_cell": "Connector Test Request"
}
```

2. Add a focused endpoint:

```text
POST /api/intake-assets/{asset_id}/application-form/validate
```

Option 1 is preferred if package detail already loads the attachment list and can carry the display state without extra UI calls.

Do not expose local file paths, stack traces, COM object names, or raw backend identifiers as user guidance.

### Frontend Behavior

`Continue to Precheck` must activate only when the currently selected attachment is a `.docx` asset that the backend considers an eligible Laboratory Testing Request form.

Frontend display rules:

- Keep the main action button disabled until eligibility is true.
- Show the reason in the existing footer guidance area where the selected file name appears.
- Keep copy operational and business-readable.
- Do not mention COM, API routes, database fields, or stack traces.
- Do not show full local paths.

Recommended copy:

```text
Application form: {filename}
```

```text
Select a .docx Laboratory Testing Request form to continue.
```

```text
Selected document is not recognized as Laboratory Testing Request. Header table cell (1,2): "{observed_header_cell}"
```

```text
Unable to verify the Word header. Open the document in Word and check the form header.
```

Observed header cell display rules:

- Trim whitespace.
- Collapse newlines and tabs.
- Limit to 80-120 characters.
- If blank, display `empty`.
- Never display full document content.

### Logging

Backend logging should include enough information to troubleshoot why the gate failed.

Log fields:

- `package_id`
- `asset_id`
- `original_name`
- `extension`
- `reason_code`
- expected header text
- observed header cell text, cleaned and length-limited
- observed header cell length
- gateway mode, e.g. `word_com`
- exception type and concise error message when validation fails unexpectedly

Do not log full document content. Do not swallow exceptions silently.

## Out Of Scope

- Do not implement Matrix, Report Generation, AI review, LAN deployment, permissions, Outlook inbox auto-scan, or email sending.
- Do not add `.doc` support for Precheck entry.
- Do not mutate, convert, or save the selected Word document.
- Do not change deterministic Precheck rules beyond entry gating.
- Do not redesign the Intake page.
- Do not add a new frontend state management library.
- Do not call Office COM outside `backend/infrastructure/office`.
- Do not expose raw COM errors or stack traces in the UI.

## Acceptance Criteria

- `Continue to Precheck` is disabled when no package is loaded.
- `Continue to Precheck` is disabled when no attachment is selected.
- `Continue to Precheck` is disabled for `.doc`, `.pdf`, `.xlsx`, images, `.msg`, and unknown files.
- `Continue to Precheck` is disabled for `.docx` files whose header table cell `(1,2)` does not contain `Laboratory Testing Request`.
- The footer guidance shows a concise reason, including the observed `(1,2)` header text when available.
- A valid `.docx` whose header table cell `(1,2)` contains `Laboratory Testing Request` can continue to Precheck.
- Backend `select-form` rejects invalid assets even if the frontend is bypassed.
- Rejection messages are actionable and do not expose stack traces or local paths.
- Backend logs include the observed header cell diagnostic context.
- Existing direct Word intake and supplemental email-package form upload flows still work for valid `.docx` forms.
- No future-scope work is added.

## Validation

Add or update tests:

- Unit tests for header cell result normalization and eligibility reason codes.
- Unit tests for `IntakeFormSelectionService` rejecting non-`.docx` assets.
- Unit tests for `IntakeFormSelectionService` rejecting `.docx` assets with mismatched header gate result.
- Unit tests for `IntakeFormSelectionService` accepting `.docx` assets with matching header gate result.
- Integration test for `POST /api/intake-packages/{package_id}/select-form` returning 400 for invalid header gate.
- Integration test for valid `.docx` selection still creating/reusing case and draft.
- Frontend static tests that the continue button uses eligibility state, not only file extension.
- Frontend static tests for footer disabled guidance copy.

Recommended validation commands:

```powershell
py -m pytest tests\unit\test_intake_form_selection_service.py -q
py -m pytest tests\integration\test_msg_package_intake_api.py -q
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

If frontend files are changed, also run from `frontend/`:

```powershell
npm run build
```

Manual Windows verification:

1. Use a valid `.docx` application form with header table cell `(1,2)` containing `Laboratory Testing Request`.
2. Verify `Continue to Precheck` activates and opens the Precheck review.
3. Edit a copy so header table cell `(1,2)` contains another value.
4. Verify `Continue to Precheck` stays disabled.
5. Verify the footer shows the observed header text.
6. Verify logs contain the same observed header text and reason code.

## Required Markdown Updates After Completion

When this task is implemented and verified, update these Markdown files in the same turn:

1. `docs/task_board.md`
   - Mark `TASK_094_INTAKE_APPLICATION_FORM_HEADER_GATE` done.
   - Update `Last Updated`.
   - Add completion notes.
   - Add validation summary.
   - Set the next recommended task or stop point.

2. `tasks/TASK_094_INTAKE_APPLICATION_FORM_HEADER_GATE.md`
   - Change `Status` from `proposed` or `active` to `done`.
   - Add completion notes.
   - Record exact validation commands and results.
   - Record known limitations, especially COM availability or manual-only checks.

3. `docs/intake_precheck_field_contract.md`
   - Document the `.docx` only application-form entry gate.
   - Document the required header table cell `(1,2)` marker.
   - Document disabled reason expectations for Intake to Precheck entry.

4. `docs/frontend_architecture_rules.md`
   - Update only if new frontend eligibility fields, selectors, or API DTO patterns are introduced.
   - Do not rewrite unrelated frontend rules.

5. `docs/02_ARCHITECTURE_RULES.md`
   - Update only if a new Word COM gateway/facade method becomes a stable Office boundary rule.
   - Keep the Office gateway principle intact.

6. Any task-specific validation or smoke checklist document if the implementation adds one.

Do not update unrelated future-scope documentation.

## Task Review Checklist

After implementation, run `docs/project_management/TASK_REVIEW_CHECKLIST.md` and explicitly verify:

- Office COM is only used behind infrastructure gateway/facade classes.
- API routes call application services only.
- Frontend consumes typed API state and does not inspect local files.
- UI copy is business-readable and does not expose backend internals.
- The task did not add `.doc` support, Matrix, Report, AI review, LAN, permissions, Outlook inbox auto-scan, email sending, or LTR workbook work.

## Stop Rule

After completing this task:

1. Update the required Markdown files.
2. Report validation results.
3. Stop.
4. Do not start the next task.

## Completion Notes

Completed on 2026-05-04.

- Added an application-form eligibility gate for Intake to Precheck.
- Added focused validation API:

```text
POST /api/intake-assets/{asset_id}/application-form/validate
```

- Backend `select-form` now enforces `.docx` plus header table cell `(1,2)` containing `Laboratory Testing Request`.
- Intake `Continue to Precheck` now depends on backend eligibility state and shows a business-readable disabled reason, including the observed header cell when available.
- Direct and supplemental application-form uploads now accept `.docx` only.
- Word header cell reading stays behind `OfficeFacade` and `WordDocumentGateway`. The gateway reads standard `.docx` headers with python-docx first and retains Word COM fallback for cases where the standard read cannot find the header cell.

Validation:

```powershell
py -m pytest tests\unit\test_application_form_eligibility_service.py tests\unit\test_intake_form_selection_service.py -q
```

Result: `18 passed`.

```powershell
py -m pytest tests\unit\test_intake_form_selection_service.py -q
```

Result: `12 passed`.

```powershell
py -m pytest tests\integration\test_msg_package_intake_api.py -q
```

Result: `9 passed`.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

Result: `43 passed`.

```powershell
npm run build
```

Result: passed.

Known limitations:

- Manual Windows smoke verification with a real edited Word application form is still recommended.
- Word COM is retained as infrastructure fallback, but the automated tests use generated `.docx` files that are readable through python-docx.

## Hotfix Notes

2026-05-04 manual smoke hotfix:

- Attachment selection now drives the Intake footer and `Continue to Precheck` state from the currently selected attachment.
- Selecting a non-`.docx` attachment clears the previous selected application form and disables `Continue to Precheck`.
- Selecting a `.docx` attachment triggers backend eligibility validation immediately, matching the selected attachment preview behavior.
- Empty/no-source state now tells the operator to import an email package with an application form or upload the application form.
- Supplemental application-form uploads into an email package now convert header-gate selection failures to business-readable 400 responses instead of `Internal Server Error`.
- Non-`.docx` attachment guidance now explicitly says the selected file is not `.docx`.

Hotfix validation:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

Result: `43 passed`.

```powershell
npm run build
```

Result: passed.

Supplemental upload hotfix validation:

```powershell
py -m pytest tests\integration\test_msg_package_intake_api.py::test_email_package_supplemental_application_form_rejects_bad_header tests\integration\test_msg_package_intake_api.py::test_email_package_without_form_accepts_supplemental_application_form tests\integration\test_msg_package_intake_api.py::test_email_package_supplemental_application_form_rejects_non_word -q
```

Result: `3 passed`.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py::test_task093_email_package_missing_form_upload_continuation tests\unit\test_frontend_shell_files.py::test_task094_intake_continue_uses_application_form_header_gate -q
```

Result: `2 passed`.

```powershell
npm run build
```

Result: passed.
