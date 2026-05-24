# TASK_147 LTR Application Duplicate and Suffix Guards

## Status

done

## Current Phase

Phase 10D - New Project completion handoff and Project workspace boundary

## Why This Task Is Allowed

`TASK_146_NEW_PROJECT_APPLY_LTR_ONLY_AND_COMPLETION_HANDOFF` is complete and
the board has no active implementation task. Manual smoke discussion found one
remaining LTR-application boundary that should be hardened before Project
Workbench folder creation UX:

- an application form that already produced a Project/LTR should be recognized
  on re-import and shown as an already-created project, not treated as a
  replaceable draft;
- LTR suffix input copy and validation must make the business rule explicit:
  suffixes must start with a letter and then contain only letters or digits.

## Goal

Prevent duplicate or confusing LTR application outcomes and clarify specified
LTR suffix input rules before folder creation becomes the main Project
Workbench task.

## Confirmed Business Rules

1. `Apply LTR Number` is the New Project completion action.
2. A case that has already applied an LTR and created/linked a Project is no
   longer a replaceable draft.
3. Re-importing the same email/application-form identity after Project/LTR
   creation should remind the operator that the project already exists.
4. Valid suffix token rule:
   - must start with an ASCII letter;
   - remaining characters may be ASCII letters or digits;
   - examples: `A`, `W`, `AA`, `A1`, `SAMPLE2`.
5. Invalid suffix examples:
   - `123`;
   - `DL-2026-02-003123`;
   - `A-1`;
   - `A 1`;
   - `A_1`.
6. Full specified LTR values with valid suffixes remain allowed:
   - `DL-2026-02-003A`;
   - `DL-2026-02-056AA`;
   - `DL-2026-02-003A1`.

## Scope

1. Backend LTR suffix validation:
   - update suffix-token and full-number suffix parsing so suffixes must start
     with a letter;
   - reject pure numeric suffixes for both suffix-token-only and full-number
     input.
2. Frontend LTR specified-number help:
   - update New Project completion dock placeholder/help text to explain
     letter-led suffixes;
   - keep copy short and operator-readable.
3. Confirmed Project/LTR duplicate reminder:
   - extend selected application-form duplicate lookup to detect matching
     confirmed cases by email content identity and application form identity;
   - expose a typed conflict/reminder payload through existing selection-time
     API handling or a narrowly extended DTO;
   - show a business-readable reminder in New Project with an `Open project`
     path.
4. Apply LTR post-success guard:
   - ensure already-confirmed active cases remain disabled in New Project;
   - preserve backend idempotency for repeat completion of the same case.

## Out Of Scope

1. Do not implement Project Workbench folder creation UX in this task.
2. Do not add Drafts / In Progress expansion.
3. Do not implement Outlook inbox auto-scan, email sending, Matrix, Report, AI
   review, LAN deployment, permissions, or future-scope workflows.
4. Do not change workbook lock/backup/short transaction design except for
   suffix validation behavior.
5. Do not create a generalized project search page.

## Step 1 Understanding

Input data:

- imported email source asset with `sha256`, size, and display filename;
- selected application form asset;
- existing intake cases and drafts;
- confirmed Project/LTR records;
- operator-specified LTR input from New Project completion dock.

Output data:

- accepted or rejected specified LTR classification;
- selected-form duplicate/reminder response when a confirmed Project/LTR exists;
- frontend reminder copy/action for already-created project;
- unchanged successful LTR application handoff for non-duplicate cases.

Modules involved:

- `backend/modules/ltr/ltr_number_rules.py`
- `backend/application/ltr_workbook_write_commit_service.py`
- `backend/application/intake_form_selection_service.py`
- `backend/api/routes_intake.py`
- `frontend/src/api/client.ts`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/features/intake/AttachmentList.tsx`
- `frontend/src/features/new-project/NewProjectCompletionDock.tsx`

## Step 2 Design

### Data Structure Design

1. LTR suffix parsing stays in the LTR rule module.
   - suffix token: `^[A-Za-z][A-Za-z0-9]*$`
   - full number with suffix: base `DL-YYYY-MM-NNN` plus the same suffix token
2. Confirmed duplicate reminder should be structurally distinct from
   unconfirmed draft duplicate.
   - proposed classification:
     `existing_confirmed_project_ltr`
   - include:
     - `existing_package_id`
     - `existing_case_id`
     - `existing_project_id`
     - `existing_ltr_number`
     - source display names for business-readable copy
     - application form names
3. Keep email identity comparison content-based:
   - `sha256 + size_bytes`
   - display filenames stay display-only.

### API / Function Shape

Proposed backend additions:

```python
@dataclass(frozen=True)
class IntakeConfirmedProjectDuplicateCheck:
    classification: str
    existing_package_id: str
    existing_case_id: str
    existing_project_id: str
    existing_ltr_number: str | None
    existing_source_original_name: str
    incoming_source_original_name: str
    existing_application_form_name: str | None
    incoming_application_form_name: str | None
```

`IntakeFormSelectionService.select_form_asset(...)` should check in order:

1. matching unconfirmed draft duplicate;
2. matching confirmed Project/LTR reminder;
3. normal selected-form case/draft creation.

### Frontend Behavior

When confirmed Project/LTR reminder is returned:

- show concise inline state near attachment selection;
- do not show `Load existing` / `Reinitialize`, because this is not a draft;
- primary action: `Open project`;
- secondary guarded action may be deferred unless needed for smoke acceptance.

New Project completion dock copy:

- placeholder: `DL-YYYY-MM-NNN or A1`
- help examples:
  - valid: `A`, `AA`, `A1`, `SAMPLE2`, `DL-2026-02-003A`
  - invalid: `123`, `DL-2026-02-003123`, `A-1`

### Dependencies

- Frontend remains API-client-only, no direct SQLite/Office access.
- API routes remain thin and call application services.
- LTR rule module remains the single parser/validator source.

## Risks And Mitigations

1. Risk: confirmed duplicate reminder blocks legitimate repeat testing.
   - Mitigation: first implementation should present a reminder and `Open
     project`; any `Import as new anyway` should be guarded or deferred if
     business rules are not final.
2. Risk: pure numeric suffix rejection changes existing tests.
   - Mitigation: update LTR number rule tests and workbook commit tests
     together.
3. Risk: duplicate classification DTO grows confusingly.
   - Mitigation: keep draft duplicate and confirmed project duplicate as
     separate classifications with different UI actions.

## Validation Plan

Required automated checks:

```powershell
py -m pytest tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py -q
py -m pytest tests\unit\test_intake_form_selection_service.py tests\integration\test_msg_package_intake_api.py tests\integration\test_new_project_completion_api.py -q
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "ltr or duplicate or new_project"
```

Frontend build:

```powershell
cd frontend
npm run build
```

Manual smoke:

1. Import a new `.msg`, apply LTR, verify Project handoff.
2. Re-import the same `.msg` and same application form, verify already-created
   Project/LTR reminder.
3. Verify `Open project` navigates to the Project workspace.
4. Verify suffix inputs:
   - accepted: `A`, `AA`, `A1`, `SAMPLE2`, `DL-2026-02-003A`;
   - rejected: `123`, `DL-2026-02-003123`, `A-1`, `A 1`, `A_1`.

## Approval Gate

This file is the reviewable execution plan. Implementation must not start until
the user explicitly approves this TASK_147 plan.

## Implementation Summary

- LTR suffix rules are now explicitly guarded and documented as letter-led:
  suffix-token-only input and full DL suffixes must start with a letter, then
  use only letters or digits.
- New Project specified LTR help copy now includes pure-letter suffix examples
  and explicitly rejects pure numeric suffixes.
- Selected application-form duplicate handling now has a separate confirmed
  Project/LTR classification: `existing_confirmed_project_ltr`.
- Re-importing the same email/application-form identity after project creation
  returns a project reminder instead of draft replacement actions.
- New Project attachment duplicate UI now shows `This application already has a
  project` with the LTR number when available and an `Open project` action.

## Validation Results

```powershell
py -m pytest tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py -q
```

Result: `39 passed`.

```powershell
py -m pytest tests\unit\test_intake_form_selection_service.py tests\integration\test_msg_package_intake_api.py tests\integration\test_new_project_completion_api.py -q
```

Result: `40 passed`.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "ltr or duplicate or new_project"
```

Result: `10 passed, 46 deselected`.

```powershell
cd frontend
npm run build
```

Result: passed.

```powershell
git diff --check
```

Result: passed with LF/CRLF working-copy warnings only.

## Stop Point

TASK_147 is complete. Do not start Project Workbench folder creation UX until
the user explicitly approves the next controlled task.
