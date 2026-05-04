# TASK_091_INTAKE_PRECHECK_MANUAL_SMOKE_AND_UI_POLISH_BACKLOG

Status: Done

## Goal

Stabilize the Intake and Precheck operator UI after the recent workflow, attachment preview, requested-testing, and editable draft changes.

This task is a controlled UI polish and smoke-validation backlog task. It should improve maintainability and visual consistency without changing business flow.

## Scope

- Define a small shared typography/action vocabulary for Intake and Precheck UI surfaces.
- Apply the shared vocabulary to visible panel titles, preview titles, section titles, and primary/secondary workflow actions.
- Keep existing Intake and Precheck layout, data flow, API calls, parser behavior, and persistence behavior stable.
- Add static frontend tests that guard the shared UI vocabulary on the key Intake/Precheck components.
- Run focused frontend shell tests and production build.

## Out of Scope

- Do not change backend APIs, parser extraction, draft persistence, precheck rules, or project confirmation behavior.
- Do not redesign the Intake or Precheck page layout.
- Do not add new features.
- Do not start copied-workbook LTR write hardening.
- Do not expose Matrix, Report generation, AI review, email sending, Outlook inbox auto-scan, LAN deployment, or permissions.

## Typography And Action Rules

- Page title: top shell title, `18px / 700 / primary`.
- Panel title: major panel/card title, `18px / 800 / ink`.
- Preview title: selected document/attachment preview title, `16px / 800 / primary-strong`.
- Section title: table and business subsection title, `14px / 800 / primary-strong`.
- Label: field labels and table headers, `12px / 800 / ink`.
- Data text: field and table values, `13px / 400 / ink`.
- Primary action: `14px / 800`, primary action color.
- Secondary action: `14px / 800`, restrained secondary color.
- Compact action: `12px / 800`, used for add-row/add-sample controls.

## Acceptance Criteria

- Intake `Import source`, `Email information`, and `Attachments` use the same panel-title treatment.
- Attachment preview title and Download action use shared preview/action vocabulary.
- Precheck `Source document & template check`, `Key Information Edit & Confirm`, `Test Sample Information`, `Description of Requested Testing`, and `Additional Information` use shared title vocabulary.
- Intake `Continue to Precheck` and Precheck footer actions use shared action vocabulary.
- Existing layout and behavior remain stable.
- `tests/unit/test_frontend_shell_files.py` includes static guards for the shared UI vocabulary.
- `npm run build` passes.

## Validation

- `py -m pytest tests\unit\test_frontend_shell_files.py -q`, result `36 passed`.
- `npm run build` from `frontend/`, result passed.
- `py -m pytest -q`, result `297 passed`.
- `git diff --check`, result blocked by pre-existing trailing whitespace in `docs/Other_AI_Modified/2026-05-03_ConnLab_UI_修改记录.md`; no TASK_091 files were reported with whitespace errors.

## Notes

- This task is activated by explicit user approval after `TASK_090_INTAKE_WORKFLOW_STRUCTURE_EXTRACTION`.
- TASK_091 added shared UI typography/action tokens and semantic classes, then applied them to Intake and Precheck visible titles and workflow actions.
