# TASK_142_EMAIL_PACKAGE_DRAFT_IDENTITY_AND_DUPLICATE_RESOLUTION

## Status

done

## Phase / Active Task Justification

- Current Phase: `Phase 10C - New Project intake flow friction cleanup`
- Current Active Task on board: `TASK_142_EMAIL_PACKAGE_DRAFT_IDENTITY_AND_DUPLICATE_RESOLUTION`
- Why this task is allowed now: `TASK_141` added package-level duplicate classification, but user review exposed a product-logic mismatch: duplicate handling must be based on the draft identity created from an email plus selected application form, not only on the email package. This task is the next controlled correction before finalizing duplicate resolution UI.

## Step 1 Plan Only

This document is the executable implementation plan for review.
Implementation was completed after the user resumed the interrupted TASK_142 execution.

## Problem Statement

The current implementation detects duplicate `.msg` imports before the operator selects an application form. That is too early and too coarse.

A single email can contain multiple application forms. Each selected application form should be able to create a separate application draft. Therefore, an exact duplicate email package is not always an exact duplicate draft.

The correct identity for an application-form draft is:

1. selected application form filename
2. email source filename
3. email source size

Only when all three match an existing unconfirmed draft should ConnLab ask the operator whether to open the existing draft or replace it.

For emails without any application form, a separate no-form draft identity is needed:

1. no selected application form
2. email source filename
3. email source size

No-form drafts must be checked only against other no-form email drafts, not against application-form drafts.

## Task Understanding

Confirmed product rules:

- `Case` is an internal persistence concept; UI should talk about `draft`, `application draft`, or `request draft`.
- Importing a `.msg` should preserve the email and attachments, but it should not block valid multi-application-form workflows just because the email file already exists.
- Selecting an application form is the point where an application draft identity becomes meaningful.
- Same email with different selected application form should create a new draft.
- Same selected application form name + same email name + same email size should prompt for operator resolution.
- Same email filename but different size should create a new draft.
- No-form email drafts should be separated from selected-application-form drafts.
- UI must show business-readable inline resolution, not raw backend JSON.

## Scope

Backend application/API:

1. Move or narrow duplicate conflict behavior away from package import for form-based workflows.
2. Add draft-level duplicate detection to the application-form selection path.
3. Add no-form draft-level duplicate detection for imported emails that have no selected application form.
4. Support explicit duplicate resolution actions for draft-level conflicts:
   - `open_existing`
   - `replace_existing`
   - `create_separate` where applicable
5. Preserve confirmed/project-linked draft protection.
6. Preserve existing email/attachment file storage behavior.
7. Return typed, structured conflict details suitable for UI rendering.

Frontend:

1. Update New Project `.msg` import flow so normal email import does not show raw duplicate errors.
2. Show duplicate resolution after selecting an application form when a draft-level duplicate is detected.
3. Show no-form duplicate resolution only for no-application-form email drafts.
4. Use inline/progressive resolution inside the New Project source area.
5. Use business copy:
   - `Open existing draft`
   - `Replace existing draft`
   - `Create separate draft`
6. Do not expose raw ids, enum names, route names, stack traces, or JSON payloads.

Tests:

1. Add/update backend unit tests for draft identity matching.
2. Add/update API integration tests for selection-time duplicate conflict and resolution.
3. Add/update frontend static tests for business-readable UI copy and no raw JSON error handling.
4. Run targeted backend tests and frontend build.

Documentation:

1. Update this task file after implementation with validation results.
2. Update `docs/task_board.md` after implementation.

## Out Of Scope

- No Outlook inbox auto-scan.
- No email sending.
- No Matrix, Report, AI review, LAN deployment, or permissions.
- No writing changes back to `.msg` or Word attachments.
- No merge workflow between two different drafts.
- No broad renaming of `IntakeCase` persistence model; this task can improve UI/API wording without a database-wide rename.
- No destructive cleanup of old stored files unless an existing unconfirmed package/draft is explicitly replaced and the operation is transaction-safe.

## Proposed Backend Design

### Draft Identity

Introduce application-level duplicate identity helpers, likely in a new service or inside `IntakeFormSelectionService` if the code remains small:

```text
selected-form draft identity:
- draft_kind = selected_application_form
- selected_form_original_name
- email_source_original_name
- email_source_size_bytes

no-form email draft identity:
- draft_kind = email_without_application_form
- email_source_original_name
- email_source_size_bytes
```

Use `sha256` internally as an additional safety detail when available, but the user-visible and required matching rule remains filename + size. Hash differences may be shown only as a secondary technical-safe difference if already available and useful.

### Selection-Time Behavior

`select_form_asset(package_id, asset_id, resolution_action?, resolution_case_id?)` should:

1. Validate selected asset eligibility as today.
2. Build incoming draft identity from selected asset and package email source asset.
3. Search existing unconfirmed drafts/cases across packages for the same identity.
4. If an exact draft identity exists and no resolution action is supplied, raise a structured conflict.
5. If `open_existing`, return the existing package/case/draft target.
6. If `replace_existing`, create/update the current selected draft and remove only the old unconfirmed records in a safe order.
7. If no duplicate, create a new draft instead of rebinding an unrelated unconfirmed case.

Important behavior change:

- Selecting a different application form in the same email should create/reuse a draft for that form identity, not overwrite the previous form's draft unless it is the same selected form identity and replacement is explicit.

### No-Form Behavior

When an imported email has no valid application form and the operator continues as a no-form draft, the backend should:

1. Search only drafts/cases that have `selected_form_asset_id is None`.
2. Match by email source filename and size.
3. Prompt only if both match.
4. Otherwise create a new no-form draft.

If current New Project still creates a blank draft too early in `ensureNewProjectApplicationDraft`, this task should narrow that behavior so blank no-form draft creation is deliberate and does not steal the application-form workflow.

### Existing TASK_141 Package-Level Detection

Revise TASK_141 behavior so package-level duplicate detection does not block the normal selected-application-form workflow.

Acceptable correction:

- Keep source-package comparison helpers for displaying differences.
- Do not return `409` at `.msg` import time for a package that may still produce distinct application-form drafts.
- Move `409` conflict to selection-time or no-form-draft-time where draft identity is known.

## Proposed API Contract

Add or extend selection endpoint request fields:

```json
{
  "resolution_action": "open_existing | replace_existing | create_separate",
  "resolution_case_id": "case-..."
}
```

Conflict response shape should be structured and business-safe:

```json
{
  "detail": {
    "classification": "exact_existing_application_draft | exact_existing_no_form_draft",
    "existing_package_id": "...",
    "existing_case_id": "...",
    "existing_source_original_name": "Request.msg",
    "incoming_source_original_name": "Request.msg",
    "existing_source_size_bytes": 2082816,
    "incoming_source_size_bytes": 2082816,
    "existing_application_form_name": "E-3718 request.docx",
    "incoming_application_form_name": "E-3718 request.docx",
    "allowed_actions": ["open_existing", "replace_existing"]
  }
}
```

Frontend should type this as a draft duplicate conflict, separate from generic API errors.

## Proposed Frontend Design

Physical scene: a lab coordinator is importing request material on a Windows workstation during daytime intake review; the interface must keep source traceability visible and interrupt only when there is a real draft identity conflict.

Register: `product`.

UI approach:

- Restrained inline panel inside the email/source area.
- No modal-first flow.
- No raw JSON.
- Show the three matching facts that caused the conflict:
  - application form name, when applicable
  - email name
  - email size
- For no-form draft conflict, explicitly say no application form was selected/found.
- Primary action for exact duplicate: `Open existing draft`.
- Secondary action: `Replace existing draft`.
- `Create separate draft` should appear only when backend allows it.

## Proposed File-Level Changes

Likely backend files:

1. `backend/application/intake_form_selection_service.py`
   - Add draft-level duplicate detection and resolution during selected form workflow.
2. `backend/application/new_project_application_draft_service.py`
   - Stop or narrow early blank draft creation if it conflicts with selected-form draft identity.
3. `backend/application/msg_package_intake_service.py`
   - Remove or narrow import-time duplicate blocking for form-based package imports.
4. `backend/api/routes_intake.py`
   - Add typed conflict response handling and resolution request fields.
5. `backend/api/dependencies.py`
   - Wire any new service dependencies if a dedicated duplicate service is extracted.
6. `backend/infrastructure/storage/repositories/intake_package.py`
   - Add repository read helpers only if existing list methods are insufficient.

Likely frontend files:

1. `frontend/src/api/client.ts`
   - Add draft duplicate conflict DTO and selection resolution request support.
2. `frontend/src/pages/IntakeInboxPage.tsx`
   - Handle selection-time duplicate conflict and resolution state.
3. `frontend/src/features/intake/IntakeSourcePanel.tsx`
   - Render draft duplicate resolution panel or delegate to extracted component.
4. `frontend/src/features/intake/EmailDuplicateResolutionPanel.tsx`
   - Preferred extraction if JSX becomes non-trivial.
5. `frontend/src/intake-inbox.css`
   - Restrained inline panel styling consistent with existing ConnLab vocabulary.

Likely tests:

1. `tests/unit/test_intake_form_selection_service.py`
2. `tests/unit/test_msg_package_intake_service.py`
3. `tests/integration/test_msg_package_intake_api.py`
4. `tests/unit/test_frontend_shell_files.py`

## Acceptance Criteria

- Importing a `.msg` with application-form attachments does not immediately block on email package duplicate alone.
- Selecting an application form checks draft identity: selected form name + email name + email size.
- If all selected-form identity fields match an existing unconfirmed draft, UI asks whether to open existing or replace.
- If any selected-form identity field differs, a new draft is created directly.
- Same email with multiple application forms can create multiple drafts.
- No-form email drafts are checked only against other no-form email drafts by email name + size.
- Existing confirmed/project-linked drafts cannot be replaced.
- UI never shows raw backend JSON for duplicate conflicts.
- UI does not use `Case` wording for operators.
- Existing New Project direct Word and normal `.msg` import flows still work.

## Validation Plan

Backend targeted:

```powershell
py -m pytest tests\unit\test_intake_form_selection_service.py tests\unit\test_msg_package_intake_service.py tests\integration\test_msg_package_intake_api.py -q
```

Frontend targeted:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "duplicate or msg_package or application_form_import"
cd frontend
npm run build
```

Diff hygiene:

```powershell
git diff --check
```

Manual smoke:

```text
1. Import a new .msg with one application form, select the form, verify a draft opens.
2. Re-import the same .msg, select the same form, verify duplicate panel appears.
3. Choose Open existing draft, verify existing draft opens.
4. Re-import the same .msg, select the same form, choose Replace existing draft, verify old unconfirmed draft is replaced.
5. Import the same .msg with a different application form selected, verify a separate draft is created without warning.
6. Import same-name but different-size .msg, verify a separate draft is created without warning.
7. Import a no-form .msg twice with same name and size, verify no-form duplicate panel appears.
8. Import a no-form .msg with same name but different size, verify a new no-form draft is created.
```

## Risks And Mitigations

Risk: current `ensureNewProjectApplicationDraft` creates blank cases too early.

- Mitigation: make blank draft creation deliberate for no-form flow or reuse only when it matches the selected-form identity.

Risk: replacing an existing draft may remove records that the current request still needs if done in the wrong order.

- Mitigation: stage the new target first, protect confirmed/project-linked records, and delete old unconfirmed database records only after new records are safely persisted.

Risk: selecting a different form currently rebinds the same case.

- Mitigation: change selection service to create/reuse by draft identity, not by first reusable case.

Risk: UI grows larger.

- Mitigation: extract duplicate resolution display into a feature component.

## Approval Gate

This updated plan changed TASK_142 from UI-only wiring to a backend + API + frontend correction. The interrupted implementation has now been completed within this task only.

## Implementation Summary

- `.msg` import no longer blocks on package-level duplicate identity before a draft exists.
- Application-form selection now detects duplicate draft identity by selected form name, email source name, and email source size.
- No-form email draft preparation now detects duplicates only against other no-form email drafts.
- Duplicate conflicts return structured `409` details and support `open_existing`, `replace_existing`, and backend-allowed `create_separate` resolution.
- New Project UI renders an inline business-readable duplicate draft panel instead of raw backend JSON.
- Confirmed/project-linked drafts remain protected from replacement.

## Validation Results

```powershell
py -m pytest tests\unit\test_intake_form_selection_service.py tests\unit\test_msg_package_intake_service.py tests\integration\test_msg_package_intake_api.py -q
```

Result: `36 passed`.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "duplicate or msg_package or application_form_import"
```

Result: `3 passed, 51 deselected`.

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
py -m pytest tests\unit tests\integration -q
```

Result: `415 passed, 9 failed`. Remaining failures are existing unrelated baseline expectations in historical frontend shell checks, board phase checks, and the legacy LTR workbook snapshot expectation.
