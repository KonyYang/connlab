# TASK_143_EMAIL_PACKAGE_SELECTION_TIME_DRAFT_LOADING_HOTFIX

## Status

done

## Phase / Active Task Justification

- Current Phase: `Phase 10C - New Project intake flow friction cleanup`
- Current Active Task on board: `TASK_143_EMAIL_PACKAGE_SELECTION_TIME_DRAFT_LOADING_HOTFIX`
- Why this task is allowed now: manual smoke testing of `TASK_142` found that duplicate draft handling is still surfaced too early and the left-side duplicate card interrupts the normal New Project intake flow. The user explicitly requested fixing these smoke issues before moving to the next task.

## Step 1 Plan Only

This document is the executable implementation plan for review.

No implementation code should be changed until the user explicitly approves this plan.

## Problem Statement

After importing a `.msg` email package, ConnLab currently shows the duplicate draft card in the left Email source panel before the operator selects an application form. This makes the workflow feel logically wrong:

1. Email import should only preserve the source email and list attachments.
2. Draft identity is meaningful only after an application form is selected.
3. A new, non-duplicate selected application form should load directly into the right-side `Application information` editor.
4. If the selected application form already has an existing unconfirmed draft, ConnLab should show a simplified duplicate card.
5. After the operator chooses `Open existing draft` or `Replace existing draft`, the selected or resolved draft should load into the right-side `Application information` editor.

## Task Understanding

Goal:

- Correct the operator flow after email import and application-form selection.

Input data:

- Imported `.msg` package.
- Attachment list with candidate Word application forms.
- Selected application-form asset.
- Backend duplicate draft response when the selected application form identity matches an existing unconfirmed draft.

Output data:

- New selected application-form draft loaded into right-side `Application information`, or
- Existing/replaced draft loaded into right-side `Application information` after the operator resolves the duplicate.

Involved modules:

- New Project intake page state orchestration.
- Intake source panel duplicate card rendering.
- Attachment import action.
- Existing intake package/select-form API client calls.
- Frontend shell/static tests.

Not allowed:

- Do not add Outlook inbox auto-scan.
- Do not add email sending.
- Do not change backend Office parsing.
- Do not implement Matrix, Report, AI review, permissions, or LAN features.
- Do not introduce a new modal flow.
- Do not show raw backend IDs, enum names, or JSON to the operator.
- Do not add extra duplicate comparison information to the simplified card.

## UX Rule

`$impeccable` product context applies. ConnLab is a product UI for lab coordinators using a Windows workstation during intake review. The UI should stay operational and dense. The duplicate state is a workflow interruption, not a diagnostic report.

## Required Behavior

### Normal email import

1. Operator imports a `.msg` email.
2. Left Email source panel shows source summary only.
3. Attachment list shows available files.
4. No duplicate draft card is shown at this point.
5. Right-side `Application information` remains empty until an application form is selected, or shows the current active draft if one was already selected in the current session.

### Selecting a new application form

1. Operator clicks the import/select action on a valid application-form attachment.
2. Frontend calls the existing select-form API.
3. If backend returns success, the returned draft is loaded into right-side `Application information`.
4. The selected attachment is reflected as the active application form.

### Selecting an existing application draft

1. Operator clicks the import/select action on a form whose draft identity matches an existing unconfirmed draft.
2. Frontend shows a simplified duplicate resolution card.
3. The simplified card contains only:
   - heading: `This application draft already exists`
   - selected application form filename
   - `Open existing draft`
   - `Replace existing draft`
4. No application/email/size comparison table is shown.
5. No `Create separate draft` button is shown for this hotfix unless a later task explicitly reintroduces it.
6. After either button succeeds, the resolved draft loads into right-side `Application information`.

## Proposed Frontend Design

Move duplicate resolution out of the Email source summary card and into the selection context.

Preferred placement:

- The duplicate card should appear near the attachment/application-form selection area or as a compact inline state between the left source panel and attachment list.
- It must visually read as a selection conflict, not as an email-source import failure.

Simplified card content:

```text
This application draft already exists
<application form filename>

[Open existing draft]
[Replace existing draft]
```

Button behavior:

- `Open existing draft`: call select-form or draft preparation with `open_existing`, then load right-side editor.
- `Replace existing draft`: call select-form with `replace_existing`, then load right-side editor.

State cleanup:

- Clear duplicate state when:
  - a new email package is imported,
  - another attachment is selected,
  - duplicate resolution succeeds,
  - direct Word upload replaces the source.

## Proposed File-Level Changes

Likely frontend files:

1. `frontend/src/pages/IntakeInboxPage.tsx`
   - Stop preparing a no-form draft immediately after every `.msg` import when the package has selectable application forms.
   - Keep package/source state after email import, but wait for selected-form action before draft identity checks.
   - Ensure successful select-form and successful duplicate resolution both call the existing right-side editor loading path.
   - Clear duplicate state when source or selected attachment changes.

2. `frontend/src/features/intake/IntakeSourcePanel.tsx`
   - Remove duplicate card rendering from the Email source panel.
   - Keep Email source focused on source summary and import action.

3. `frontend/src/features/intake/AttachmentList.tsx` or a new small feature component if needed
   - Render the simplified duplicate card in the selection context.
   - Keep JSX small and business-readable.

4. `frontend/src/intake-inbox.css`
   - Add or adjust compact duplicate card styles.
   - Keep restrained warning styling, no nested card inside card if avoidable.

5. `frontend/src/api/client.ts`
   - No API shape change expected. Only use existing duplicate response and resolution action support.

Likely tests:

1. `tests/unit/test_frontend_shell_files.py`
   - Assert duplicate card copy is simplified.
   - Assert removed comparison labels are not present in the duplicate card component.
   - Assert duplicate UI is not rendered by `IntakeSourcePanel`.
   - Assert `Open existing draft` and `Replace existing draft` remain present.

## Backend Scope

No backend implementation is planned unless frontend verification proves the API cannot support selection-time duplicate handling.

If backend changes are required, they must be limited to preserving the existing `TASK_142` contract:

- `.msg` import must not return draft duplicate conflicts for form-based packages.
- select-form remains the authoritative point for selected application-form duplicate checks.

## Acceptance Criteria

- Importing a `.msg` does not immediately show `This application draft already exists`.
- Duplicate checking is surfaced only after the operator selects an application form or explicitly enters a no-form draft path.
- A non-duplicate selected application form loads directly into the right-side `Application information`.
- A duplicate selected application form shows the simplified card with only two actions.
- The simplified card does not show application/email/size comparison rows.
- `Open existing draft` loads the existing draft into the right-side `Application information`.
- `Replace existing draft` replaces the unconfirmed draft and loads the resulting draft into the right-side `Application information`.
- The red header-gate validation message is not shown merely because an unselected or duplicate candidate exists; it should correspond to the currently selected/imported application-form candidate.
- Existing direct Word upload behavior remains intact.

## Validation Plan

Targeted frontend static checks:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "duplicate or msg_package or application_form_import"
```

Frontend build:

```powershell
cd frontend
npm run build
```

Diff hygiene:

```powershell
git diff --check
```

Manual smoke:

```text
1. Import a new .msg with application-form attachments.
2. Verify no duplicate card appears immediately after import.
3. Select a new application form.
4. Verify right-side Application information loads.
5. Re-import the same .msg and select the same application form.
6. Verify the simplified duplicate card appears only after selection.
7. Verify the card has only Open existing draft and Replace existing draft actions.
8. Click Open existing draft and verify Application information loads on the right.
9. Re-import/select again, click Replace existing draft, and verify Application information loads on the right.
10. Confirm direct Word upload still loads Application information.
```

## Risks And Mitigations

Risk: current page effect calls `ensureNewProjectApplicationDraft(packageId)` immediately after every package import.

- Mitigation: gate that effect so email packages with candidate forms do not create or resolve a draft until an application form is selected.

Risk: moving the duplicate panel could grow the page file.

- Mitigation: keep rendering in a small feature component if the JSX is more than a compact inline block.

Risk: no-form email behavior may rely on immediate draft preparation.

- Mitigation: preserve no-form draft preparation only when there are no selectable application-form candidates or when the no-form path is explicitly invoked.

## Approval Gate

Implementation was completed after user approval.

## Implementation Summary

- `.msg` import now preserves the email source and attachments without immediately selecting the first attachment or preparing a draft when selectable Word application forms are present.
- The New Project editor waits for an explicit application-form import/selection before selected-form duplicate handling runs.
- New selected application forms continue through the existing `select-form` path and load into the right-side `Application information` editor.
- Duplicate resolution moved out of the Email source panel and into the Attachments selection context.
- The duplicate card is simplified to the selected application-form filename plus `Open existing draft` and `Replace existing draft`.
- Both duplicate actions reuse the same selected-draft loading path so the resolved draft appears in right-side `Application information`.
- Follow-up manual-smoke fix: when a resolved duplicate draft already has `selectedPrecheckCaseId`, the New Project page now reloads the selected review directly instead of calling blank draft preparation again, preventing the right-side editor from flashing and then clearing.
- Follow-up UI copy polish: duplicate actions now read `Load existing` and `Reinitialize`, and the action row uses two equal columns on normal workbench widths.
- Follow-up completion friction cleanup: removed the extra controlled-workbook acknowledgement checkbox from New Project setup. ConnLab now treats this risk as accepted in this workflow and sends the existing backend preview acknowledgement automatically.
- Follow-up completion dock cleanup: replaced the sticky autosave guidance with the final completion dock, moved LTR mode and specified-number input beside `Apply LTR Number and Create Folder`, and kept the left setup panel focused on workbook row metadata.
- Follow-up specified LTR input clarity: specified-number mode now keeps the input highlighted and completion blocked until the value matches `DL-YYYY-MM-NNN`, `DL-YYYY-MM-NNN` plus letter-led suffix, or a letter-led alphanumeric suffix token; a `?` help control explains accepted examples.
- Follow-up sample-table blocker clarity: required empty sample cells now highlight the whole cell with a non-obstructive tint instead of adding capsule borders or placeholder text that would obscure table content; each non-empty sample row independently checks Product Name and Quantity.
- Follow-up default application-form loading: `.msg` import now preselects the first `.docx` application form and immediately runs the selected-form import/duplicate path; emails with no application form still prepare the no-form draft path. Duplicate buttons now place `Load existing` on the right as the primary/recommended action.
- Follow-up import logic review: selected-form and no-form duplicate enforcement were rechecked against the backend services. A stale duplicate-card state was fixed so any successful prepared or selected draft load clears previous duplicate state before showing right-side `Application information`.

## Validation Results

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "duplicate or msg_package or application_form_import"
```

Result: `3 passed, 52 deselected`.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py::test_task143_email_import_waits_for_application_form_selection -q
```

Result: `1 passed`.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py::test_task142_draft_duplicate_resolution_is_business_readable tests\unit\test_frontend_shell_files.py::test_task143_email_import_waits_for_application_form_selection -q
```

Result: `2 passed`.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell tests\unit\test_frontend_shell_files.py::test_task103_new_project_page_chrome_is_minimal tests\unit\test_frontend_shell_files.py::test_task134_new_project_uses_ltr_workbook_commit_before_folder -q
```

Result: `3 passed`.

```powershell
cd frontend
npm run build
```

Result: passed.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py::test_task143_email_import_waits_for_application_form_selection tests\unit\test_frontend_shell_files.py::test_task142_draft_duplicate_resolution_is_business_readable tests\unit\test_frontend_shell_files.py::test_task103_application_form_import_is_explicit_and_confirmed -q
```

Result: `3 passed`.

```powershell
cd frontend
npm run build
```

Result: passed.

```powershell
git diff --check
```

Result: passed with LF/CRLF working-copy warnings only.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py::test_task143_email_import_waits_for_application_form_selection tests\unit\test_frontend_shell_files.py::test_task142_draft_duplicate_resolution_is_business_readable -q
```

Result: `2 passed`.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell tests\unit\test_frontend_shell_files.py::test_task103_application_form_import_is_explicit_and_confirmed -q
```

Result: `2 passed`.

```powershell
cd frontend
npm run build
```

Result: passed.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell -q
```

Result: `1 passed`.

```powershell
cd frontend
npm run build
```

Result: passed.

```powershell
git diff --check
```

Result: passed with LF/CRLF working-copy warnings only.
