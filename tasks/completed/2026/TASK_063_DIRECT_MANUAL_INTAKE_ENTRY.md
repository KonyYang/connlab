# TASK_063_DIRECT_MANUAL_INTAKE_ENTRY

## Status

done

## Goal

Add the no-email exception path where an operator manually enters application request information.

## Scope

- Provide a direct manual intake entry workflow for required project/application/sample/testing fields.
- Store manual intake as structured intake case data before Project creation.
- Make missing required information visible before confirmation.
- Follow `$impeccable` product UI rules.

## Out Of Scope

- No email import changes.
- No Outlook inbox auto-scan.
- No email sending.
- No Matrix, Report, AI review, LAN deployment, permissions, or external LTR workbook mutation.

## Validation

- Frontend build.
- Relevant frontend static tests.
- Manual intake service/API tests.
