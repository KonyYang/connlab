# TASK_087_MSG_ATTACHMENT_EXTRACTION_HOTFIX

Status: Done

## Goal

Fix real Outlook `.msg` intake so the Intake attachment list matches user-visible Outlook attachments.

## Scope

- Do not show the imported source `.msg` itself in the Intake page attachment list.
- Filter inline mail body images that Outlook stores as OLE attachments with Content-ID values.
- Extract embedded Outlook item attachments as `.msg` attachment records with a readable filename.
- Display `.msg` attachment chips as `MSG`, not `FILE`.
- Preserve backend source-email asset storage for traceability and downstream folder evidence.

## Out of Scope

- Do not add Outlook inbox auto-scan.
- Do not send email.
- Do not implement a full `.msg` rendering preview.
- Do not change project confirmation, precheck, LTR, or folder behavior.

## Acceptance Criteria

- A real exported Outlook `.msg` with 3 Word documents, 2 PDFs, and 1 embedded `.msg` item should list those 6 user-visible attachments, not body images.
- The original imported source `.msg` remains stored but is not shown as an attachment row in Intake.
- Embedded Outlook item attachments receive a `.msg` extension and `application/vnd.ms-outlook` MIME type.
- Frontend attachment chips show `MSG` for `.msg` attachments.

## Validation

- `py -m pytest tests\unit\test_outlook_msg_source_import.py tests\unit\test_frontend_shell_files.py -q`, result `42 passed`.
- `py -m pytest tests\unit\test_msg_package_intake_service.py tests\integration\test_msg_package_intake_api.py -q`, result `8 passed`.
- `npm run build` from `frontend/`, result passed.
- Real sample probe for `D:\test_samples\Coolopower HDF 3 40mm Busbar to Busbar &Busbar to PCB Connector Qualification Testing_NPD.msg`, result 6 visible attachments: 3 Word, 2 PDF, 1 embedded MSG; inline body images filtered.
- `py -m pytest -q`, result `289 passed`.
- `git diff --check`, result passed with CRLF working-copy warnings only.
