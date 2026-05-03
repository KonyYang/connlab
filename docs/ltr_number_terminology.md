# LTR Number Terminology

## Current Rule

`LTR` means `Laboratory Testing Request`. It names the request/business object, not the identifier by itself.

`LTR Number` is the project business identifier after registration. ConnLab UI and operator-facing documentation should use `LTR Number` when referring to the registered number.

## Display Rules

- Before registration, projects display `Pending LTR Number`.
- After registration, projects display the stored `ltr_number` value under the `LTR Number` label.
- Historical values such as `DL-2026-04-001` may remain stored values, but `DL` is not shown as a separate business concept.
- Avoid user-facing labels such as `LTR/DL`, `DL number`, or `DL-centric identity`.

## Implementation Boundary

This terminology cleanup does not rename database columns, API fields, or historical placeholder names in one step. Technical compatibility fields such as `dl_number` may remain until a dedicated migration task is approved.
