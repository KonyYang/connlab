# TASK_126_NEW_PROJECT_SETUP_CONFIRMATION_REQUIRED_FIELDS_REWORK

## Status

done

## Purpose

Rework New Project LTR/folder activation requirements so old application-form blockers do not block completion, and add explicit project setup confirmation fields required before LTR number and folder creation.

## Scope

- Move LTR number mode controls into a left-side `Project setup confirmation` card below Attachments.
- Keep `Apply LTR Number and Create Folder` in the Application information footer.
- Remove completion blocking from blank Project #, non-key sample columns, and Additional Information.
- Require sample rows only by at least one Product Name and Quantity text containing a digit.
- Add required setup fields: Test Item, Sample Description, Location, Test Type in sheet, Project Leader.
- Provide Location and Test Type in sheet dropdown options from backend, plus default Project Leader from the current Windows user.
- Persist setup confirmation values into local LTR audit notes for future LTR.xls write mapping.

## Out Of Scope

- Do not implement copied/external LTR workbook write.
- Do not implement final Word generation, report naming, Matrix, Report, AI review, Outlook auto-scan, email sending, LAN, or permissions.

## Validation

Required:

```powershell
py -m pytest tests\unit tests\integration -q
npm run build
```

## Stop Rule

Stop after implementation and update `docs/task_board.md`.

