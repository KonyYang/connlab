# TASK_068_REFERENCE_STYLE_PROJECTS_UI_POLISH

## Status

done

## Goal

Polish the ConnLab product shell and Projects registry UI closer to the approved reference image while keeping the current MVP scope intact and making the layout practical on common 14-inch laptops.

## Scope

- Add clear navigation icons to sidebar items.
- Add a reference-style top-right utility area with search, notification indicator, help button, and local user identity display.
- Move the Projects registry search and toolbar controls into the Project registry heading row.
- Add non-functional, UI-only filter/columns/view controls as disabled or display-only affordances where needed.
- Refine typography, spacing, table density, icon treatment, and responsive constraints for 14-inch laptop screens.
- Keep Projects metric cards visually aligned with the reference layout.
- Add/update static frontend guard tests.
- Update `docs/task_board.md` after validation.

## Out Of Scope

- No real authentication or user management.
- No real notification backend.
- No real help center.
- No real filter/column persistence implementation.
- No Outlook inbox auto-scan.
- No email sending.
- No external LTR workbook write hardening.
- No Matrix, Report, AI review, LAN deployment, permissions, or future-scope behavior.

## Design Notes

- Utility controls may be visual placeholders only, but must not claim unavailable backend behavior.
- 14-inch laptop target means the default desktop layout must work around 1366px width without wasteful spacing.
- Use product UI conventions from `PRODUCT.md` and `DESIGN.md`: dense, calm, operational, and not decorative.

## Validation

- Frontend build.
- Static frontend guard tests.

## Completion Notes

- Sidebar items now include line icons.
- Top bar now includes reference-style search, notification indicator, help button, and local user identity display.
- Projects registry toolbar now contains search, filter, columns, view toggle, refresh, and New Project controls.
- Projects layout and spacing were tightened for common 14-inch laptop widths around 1366px.
- Filter, columns, grid view, notification, help, and user controls are UI-only affordances in this phase.
- Validation:
  - `npm run build` from `frontend\` -> passed
  - `py -m pytest tests\unit\test_frontend_shell_files.py -q` -> `19 passed`
