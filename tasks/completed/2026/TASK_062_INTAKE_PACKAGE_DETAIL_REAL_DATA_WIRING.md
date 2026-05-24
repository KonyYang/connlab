# TASK_062_INTAKE_PACKAGE_DETAIL_REAL_DATA_WIRING

## Status

done

## Goal

Replace static Intake package detail data with real backend package, asset, and candidate state.

## Scope

- Load package metadata, preserved source file state, attachments, and candidate application forms.
- Show no-form and multi-form outcomes using real package data.
- Preserve one selected application form creates one intake case.
- Follow `$impeccable` product UI rules.

## Out Of Scope

- No Outlook inbox auto-scan.
- No email sending.
- No manual intake entry.
- No Matrix, Report, AI review, LAN deployment, permissions, or external LTR workbook mutation.

## Validation

- Frontend build.
- Relevant frontend static tests.
- Relevant intake package API/repository tests.
