# Fee editing and confirmation contract

Fee Evaluation autosave stores an editable draft, not authority. Confirm reviews all active
groups, including rows hidden by the group filter. Fee Form publication remains a separate action.

## Editing and calculations

- Reloading the same source context retains reviewed quantities and cleared optional cells.
  Matrix/sample/measurement changes still use the existing reviewed rebase; automatic quantities
  follow the new Matrix rather than an obsolete override.
- The client serializes trimmed strings, blank optional base fee/discount/condition/external cost
  as zero, and leaves required blanks incomplete. The server rechecks the saved draft.
- Use decimal ROUND_HALF_UP for display: hours one decimal, row fees and manpower whole amounts,
  totals two decimals. Manpower multiplies **unrounded** hours by the hourly rate. External cost
  retains its entered precision until the total is rounded.
- Confirmation independently checks row inputs, non-negative finite numbers, 0–100% discounts,
  and row arithmetic. Existing default/imported rows can retain the exact calculated amount;
  UI-rounded whole amounts must match the same formula. Arbitrary supplied totals are rejected.
- Production confirmation also requires all Matrix test-row identities. Incomplete drafts can
  still autosave; missing rows cannot become confirmed authority.

### Row pricing fields and summary roles

- A row fee follows `unit_price * units * (1 - discount / 100) + base_fee`.
  Use `unit_price` and `units` for quantity-based pricing; use `base_fee` for the fixed or additive
  part of a row. A fixed whole-row fee can therefore use `unit_price = 0` and put the amount in
  `base_fee`, but not every fee belongs in `base_fee`.
- `testing_fee` is the derived row-fee snapshot sent by the client. It is not independent pricing
  authority or a manually retained provenance field: confirmation recomputes the row arithmetic
  and rejects an unrelated value. After that validation, the saved `testing_fee` values are summed
  to derive `testing_fee_total` and `grand_cost`, so `testing_fee` is not merely unused display text.
- The shared acceptance cases under `tests/contract_fixtures` pin these roles and the display
  boundaries across the frontend and backend; they do not replace either production implementation.

### Deferred hardening, when justified

The current shared acceptance cases are the regression baseline. Further hardening is deliberately
deferred until a related behavior change, demonstrated gap, or repeated drift justifies it:

- expose the canonical summary calculation as a public pure domain function instead of testing a
  private application helper;
- add property-based coverage for decimal normalization, rounding boundaries, and equivalent input
  representations;
- add a real HTTP API contract test that carries the frontend-shaped confirmation payload through
  transport validation into backend confirmation.

These are optional follow-ups, not authorization for an immediate refactor or expansion of the Fee
workflow.

## Confirmation, cancel and retry

- Writes retain exact draft ID/generation/fingerprint/token checks. Context changes and concurrent
  edits are not bypassed by retrying.
- Read-side currentness compares the latest confirmed content and source context for the same draft.
  Cancel can restore that content without rewriting confirmation history or resetting a generation.
  A different source, changed notes/prices, or a different draft still requires confirmation.
- A failed Confirm retains inputs, reports its reason and can retry without an unrelated edit.
  Retry re-saves/reloads after failure. Read-only projects and incomplete input remain blocked.

## Verification and deployment

Regression seams: preview calculation, save/reload hydration, page Confirm/re-entry/retry, real
in-memory draft persistence plus confirmation, stale-token rejection, source-context changes,
Matrix/measurement rebase and Fee Form publication/archive tests.

No schema migration, historical authority rewrite or real project file repair is part of this fix.
The frontend and backend must be deployed together; an already packaged release needs rebuilding.
