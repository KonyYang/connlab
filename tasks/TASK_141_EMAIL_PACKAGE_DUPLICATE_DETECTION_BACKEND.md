# TASK_141_EMAIL_PACKAGE_DUPLICATE_DETECTION_BACKEND

## Status

done

## Phase / Active Task Justification

- Current Phase: `Phase 10C - New Project intake flow friction cleanup`
- Current Active Task on board: `None - awaiting next approved task`
- Why this task is allowed to plan now: New Project now treats imported request packages as durable drafts. Re-importing the same or similarly named `.msg` package needs a controlled backend decision surface before the UI can present `open existing`, `replace`, or `create separate draft`.

## Step 1 Plan Only

This document is the executable implementation plan for review.
No implementation code may be written until the user approves this plan.

## Purpose

Add backend duplicate detection and resolution support for manually imported `.msg` packages.

When an operator imports a `.msg` file that matches an existing draft by name or content, ConnLab should not silently create confusing duplicate drafts. The backend should compare the source message and attachment manifest, then return a business-readable conflict summary that the frontend can use in the next task.

## Task Understanding

Confirmed product rules:

- Manual `.msg` package import remains user-selected file import only.
- No Outlook inbox auto-scan is introduced.
- Existing package/case/draft state is durable.
- File name alone is not enough to determine whether two imports are the same request.

Goal:

- Detect exact duplicate `.msg` drafts.
- Detect same-name but different-content `.msg` drafts.
- Provide enough structured comparison data for the UI to ask the operator whether to open existing, replace existing, or create a separate draft.
- Keep confirmed packages/projects protected from destructive replacement.

## Duplicate Classes

Use these backend-level classes:

- `no_conflict`: no existing draft package needs operator resolution.
- `exact_existing_draft`: same source original name, same source size/hash, and same attachment manifest.
- `same_name_different_content`: same source original name, but source size/hash or attachment manifest differs.

Attachment manifest comparison should include, where available:

- attachment original name
- extension
- size bytes
- sha256
- detected role

## Scope

Backend/API:

1. Persist source `.msg` file metadata needed for comparison:
   - source size bytes
   - source sha256
2. Build an attachment manifest for existing and incoming packages.
3. Add an application service that compares incoming `.msg` import material against unconfirmed draft packages.
4. Expose an API response that can report duplicate classification and differences before destructive replacement.
5. Add explicit resolution input for import continuation:
   - open existing draft/package
   - replace existing draft/package
   - create separate draft/package
6. Ensure replacement is allowed only for unconfirmed creation drafts.
7. Reuse existing package graph deletion/storage cleanup for replacement where possible.

Frontend:

1. No UI implementation in this task beyond typed client DTOs if needed for integration tests.

Documentation:

1. Update `docs/task_board.md` after implementation.
2. Mark this task `done` after validation.

## Out Of Scope

- No New Project duplicate resolution UI; that belongs to `TASK_142`.
- No Outlook inbox scanning.
- No automatic email sending.
- No fuzzy subject/body matching.
- No merge of two packages.
- No duplicate handling for direct Word-only import unless implementation discovery shows it shares the same import path cleanly.
- No Matrix, Report, AI review, permissions, or LAN deployment.

## Proposed Backend Design

Preferred shape:

```text
EmailPackageDuplicateCheck
  classification
  incoming
  existing_package nullable
  source_differences
  attachment_differences
  allowed_actions
```

Possible actions:

```text
open_existing
replace_existing
create_separate
```

Resolution behavior:

- `open_existing`: do not create a new package; return existing package/case/draft routing data.
- `replace_existing`: delete the unconfirmed existing package graph and stored files, then import the new file as the replacement package.
- `create_separate`: import the incoming `.msg` as a new package even if name matches.

Implementation must avoid deleting confirmed packages or packages that already created a Project.

## Proposed File-Level Changes

Likely backend files:

1. `backend/domain/models.py`
   - Add optional source metadata fields to `IntakePackage` if no suitable place exists.
2. `backend/infrastructure/storage/models.py`
   - Add nullable columns for source size/hash.
   - Include lightweight SQLite migration/backfill behavior if needed.
3. `backend/infrastructure/storage/repositories/intake_package.py`
   - Map new source metadata fields.
4. `backend/application/msg_package_intake_service.py`
   - Capture source metadata during import.
   - Integrate duplicate check/resolution command.
5. New narrow service if cleaner:
   - `backend/application/email_package_duplicate_service.py`
6. `backend/api/routes_intake.py`
   - Add typed request/response fields for duplicate classification and resolution.

Likely tests:

1. `tests/unit/test_msg_package_intake_service.py`
2. `tests/unit/test_email_package_duplicate_service.py` if a new service is created.
3. `tests/integration/test_msg_package_intake_api.py`
4. Repository/migration tests if new persisted columns are added.

## Acceptance Criteria

- First import of a `.msg` package behaves as before.
- Re-importing an identical draft package can be identified as `exact_existing_draft`.
- Importing a same-name `.msg` with different source or attachment manifest is identified as `same_name_different_content`.
- API response includes existing package id, package source name, source size/hash summary, attachment count, and attachment differences.
- Replacement cannot delete or overwrite confirmed packages or packages tied to a created Project.
- `open_existing`, `replace_existing`, and `create_separate` are represented as explicit backend actions.
- No UI workflow is exposed beyond backend/API responses in this task.

## Validation Plan

Required:

```powershell
py -m pytest tests\unit\test_msg_package_intake_service.py tests\integration\test_msg_package_intake_api.py -q
```

If new service/repository tests are added:

```powershell
py -m pytest tests\unit\test_email_package_duplicate_service.py tests\integration\test_intake_package_repositories.py -q
```

Final:

```powershell
py -m pytest tests\unit tests\integration -q
git diff --check
```

## Risks And Mitigations

Risk: duplicate detection becomes too broad and blocks legitimate repeated requests.

- Mitigation: classify only exact duplicate or same-name conflicts; non-matching names import normally.

Risk: replacement deletes useful draft edits.

- Mitigation: replacement is explicit and only allowed for unconfirmed drafts.

Risk: attachment comparison is unstable due to extraction ordering.

- Mitigation: compare sorted manifest entries by name, size, hash, and role.

## Approval Gate

After user explicitly approves this task, Step 2 implementation may start.

## Implementation Notes

- `POST /api/intake-packages/import-msg` now supports duplicate resolution inputs:
  - `resolution_action`: `open_existing` / `replace_existing` / `create_separate`
  - `resolution_package_id`
- Backend duplicate check now classifies same-name existing unconfirmed Outlook `.msg` drafts as:
  - `exact_existing_draft`
  - `same_name_different_content`
- On duplicate without explicit resolution, API returns `409` with structured duplicate detail.
- `open_existing` returns existing package state.
- `replace_existing` stages the new package first, then removes the old unconfirmed package records. Old stored files are not deleted inside the uncommitted database request to avoid rollback leaving restored rows pointing to missing files.
- Replacement for confirmed/project-linked package is blocked.
- `open_existing` treats an already selected application form as ready so the response does not regress to the missing-form action.

## Validation Summary

- `py -m pytest tests\unit\test_msg_package_intake_service.py tests\integration\test_msg_package_intake_api.py -q` passed (`21 passed`).
- `py -m pytest tests\unit tests\integration -q` currently has existing unrelated baseline failures (frontend shell historical checks, board-phase historical checks, and LTR workbook snapshot legacy expectation).
- `git diff --check` passed with LF/CRLF working-copy warnings only.
