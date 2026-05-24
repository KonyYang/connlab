# Phase 10A Intake Entry Completion Plan

Date: 2026-04-29

## Purpose

Phase 10A corrects the product entry point.

Most real ConnLab projects start from a customer or requester email package, usually an exported `.msg` file with attachments. Some projects are exceptions: there is no email package, and the operator must enter the application request information directly.

Phase 10A makes both entry paths explicit and routes them into the same intake review flow before Project creation.

## Scope

Implement only these entry paths:

1. Manual `.msg` package import from a user-selected file.
2. Direct manual intake entry when no email exists.
3. Shared package/case review surfaces for selected application forms.
4. Confirmed intake case creation into Project, ApplicationForm, SampleInfo, and FileAsset records through existing backend service boundaries.

## Out Of Scope

- No Outlook inbox auto-scan.
- No email sending.
- No Matrix planning.
- No Report generation.
- No AI review.
- No permissions.
- No LAN deployment.
- No external LTR workbook mutation.
- No copied-workbook LTR write hardening in Phase 10A.

## Task Sequence

1. `TASK_060_PHASE10A_SCOPE_AND_BOARD_ACTIVATION`
   - Open Phase 10A and document intake entry priority.
2. `TASK_061_MSG_PACKAGE_IMPORT_API_AND_FRONTEND_ENTRY`
   - Add a manual `.msg` file import path in the Intake UI and API wiring.
3. `TASK_062_INTAKE_PACKAGE_DETAIL_REAL_DATA_WIRING`
   - Replace static package detail fixture data with backend package/assets/candidate state.
4. `TASK_063_DIRECT_MANUAL_INTAKE_ENTRY`
   - Add no-email manual intake entry for required application/project fields.
5. `TASK_064_UNIFIED_INTAKE_CASE_REVIEW_AND_CONFIRMATION_UI`
   - Route email and manual entries into one review/confirm experience.
6. `TASK_065_INTAKE_ENTRY_BROWSER_SMOKE_AND_DOCS_SYNC`
   - Close Phase 10A with validation, browser smoke checklist, and next recommendation.

## Acceptance Gate

- Operators can start from a `.msg` file without creating a project first.
- Operators can start from manual intake when no email exists.
- Both paths preserve source context and create structured records through the same review gate.
- One selected application form creates one project only after confirmation.
- Missing required information is visible before confirmation.
- No future-scope feature slips into Phase 10A.

## Next Recommendation After Phase 10A

After Phase 10A is complete and manually smoked, revisit copied-workbook LTR write hardening as a later phase candidate.
