# Fee Form import

Fee Evaluation's **Import Fee Form** reads an unencrypted ConnLab-exported `.xls`
or `.xlsx`, previews the proposed changes, and applies them only after the user
chooses **Apply … rows to draft**. Existing draft autosave and **Update Fee** remain
the persistence and authority boundary. Inspection does not modify the project.

## Matching and editable fields

- **Same Matrix:** a target Group must match the source Group and its entire ordered
  sequence of test descriptions. Repeated test items are paired by sequence, not
  collapsed by name. Restore man-hour, unit price/type, units, base fee, discount
  and notes. Unmatched Groups remain unchanged. Blank numeric inputs do not erase
  existing values. Report preparation is matched separately.
- **Other project:** match test description and row category regardless of Group
  and step. Only unit price, unit type and base fee are reused. Multiple distinct
  price tuples require an explicit selection; the default is to skip that item.
  This is exact matching after case/whitespace normalization, not fuzzy matching
  or an assertion that similarly named tests have equivalent conditions.
- No Matrix rows are inserted or removed. Quantities, hours, discounts and notes
  stay unchanged in cross-project mode. Page summary inputs (condition confirmation,
  hourly rate, external cost and cost note) are not imported. Derived totals are
  recalculated by the existing page model, never copied from Excel.

## Format and safety boundary

The reader expects the current nine-column ConnLab Fee Form layout with headers
in row 4, Group boundaries at Sample preparation, and notes in column I comments.
It accepts the current export's actual multiline headings and numeric Group labels.
It rejects unknown or ambiguous layouts, invalid editable numbers, unsupported unit
types, macro extensions, and oversized files. `.xlsx` input formulas must be replaced
with values; calculated total cells are ignored. `.xls` is read using xlrd's stored
values. Neither reader starts Office or executes formulas/macros.

The upload is capped at 10 MB, with limits on sheet count, rows, expanded XLSX size
and numeric representation. Files are not retained by the inspection endpoint.
Changing the current fee rows invalidates an open preview; cancelling or changing
the upload invalidates outstanding inspection responses.

## Acceptance checks

Regression coverage is in the fee import gateway/API tests and Fee Evaluation
frontend tests: repeated items, mismatched sequences, conflicting prices, readonly
mode, cancellation, stale previews, malformed files, and apply-to-draft without
automatic confirmation. A real exported `.xls` has also been parsed read-only.

For manual acceptance, import an exported same-Matrix workbook, inspect before
applying, and verify the saved draft after reopening. Then use another project's
workbook in price-only mode and confirm that current quantities stay unchanged.
The Windows browser release must be rebuilt to include the new route, UI and xlrd
dependency; existing release directories are not updated by source changes.

Development startup uses `C:/PythonEnvs/connlab/.venv/Scripts/python.exe` from
`scripts/run_backend.ps1`, not necessarily the `python` found on PATH. Install
the declared dependencies in that environment after pulling this change. An
`xlrd` installation in another Python environment does not satisfy this backend;
a missing installation stops API startup and Vite then reports ECONNREFUSED on
port 8000. Verify backend imports and tests with the startup interpreter.
