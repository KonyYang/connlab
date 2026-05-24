# TASK_067_PROJECTS_REGISTRY_AND_LTR_NUMBER_TERMINOLOGY_REALIGNMENT

## Status

done

## Goal

Realign ConnLab frontend workflow language and project registry layout around real business usage: users start new work from "New Project", and the project business identifier after registration is "LTR Number".

## Scope

- Add/rename the sidebar entry to `New Project` for the existing intake entry workflow.
- Keep `/intake` route compatibility while presenting it as project creation.
- Rework the Projects page toward the approved reference layout:
  - top context/search area
  - metric cards
  - project registry table
  - business-readable status badges
- Keep metric cards aligned with current MVP capabilities and the reference design.
- Replace UI/documentation wording that conflates `LTR`, `LTR/DL`, `DL number`, or `DL-centric` with the clearer business term `LTR Number`.
- Preserve historical number values such as `DL-...` as string values only; do not expose `DL` as a separate UI concept.
- Add/update focused tests for navigation labels, registry layout markers, and terminology guardrails.
- Update `docs/task_board.md` after validation.

## Out Of Scope

- No external LTR workbook write hardening.
- No database field migration or broad backend rename.
- No Outlook inbox auto-scan.
- No email sending.
- No Matrix, Report, AI review, LAN deployment, permissions, or future-scope navigation.
- No rewrite of intake backend behavior.

## Design Notes

- `LTR` means Laboratory Testing Request.
- `LTR Number` is the project business identifier after registration.
- Projects without an LTR Number remain `Pending LTR Number`.
- Any historical `DL-...` value remains the stored number value but is labeled as `LTR Number`.
- The UI should use a restrained product register layout consistent with `PRODUCT.md` and `DESIGN.md`.

## Validation

- Frontend build.
- Static frontend guard tests.
- Relevant backend tests if API response behavior changes.

## Completion Notes

- Sidebar now presents the existing request-package entry workflow as `New Project`.
- Projects page now uses a reference-style registry layout with five metric cards, page search, refresh, progress display, and a dense project table.
- Project business identity is shown as `LTR Number`; projects without a number display `Pending LTR Number`.
- Frontend LTR wording now distinguishes LTR from `LTR Number`.
- `docs/ltr_number_terminology.md` records the terminology rule for future tasks.
- Validation:
  - `npm run build` from `frontend\` -> passed
  - `py -m pytest tests\unit\test_frontend_shell_files.py -q` -> `19 passed`
