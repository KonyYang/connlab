# TASK_061_MSG_PACKAGE_IMPORT_API_AND_FRONTEND_ENTRY

## Status

done

## Goal

Add the manual `.msg` email package import entry point to the frontend Intake workflow and wire it to backend import behavior.

## Scope

- Add an Intake UI action to choose an exported `.msg` file.
- Route the file through API/client code instead of direct frontend Office handling.
- Persist source email and extracted attachments through existing intake storage boundaries.
- Show imported package identity and next review action.
- Follow `$impeccable` product UI rules.

## Out Of Scope

- No Outlook inbox auto-scan.
- No email sending.
- No direct manual intake entry.
- No Matrix, Report, AI review, LAN deployment, permissions, or external LTR workbook mutation.

## Validation

- Frontend build.
- Relevant frontend static tests.
- Relevant `.msg` import and intake storage backend tests.
