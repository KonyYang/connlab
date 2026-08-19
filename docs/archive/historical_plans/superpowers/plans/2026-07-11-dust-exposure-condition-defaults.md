# Dust Exposure Condition Defaults

## Scope

Populate the report-style default Condition for `Dust exposure` /
`EIA-364-91`.

## Expected Output

- Default: `Benign dust composition 1#, 1 hour, unmated for both connectors`.
- A source composition such as `2#` replaces the default `1#`.
- Explicit `mated`, `unmated only Receptacle`, or other non-bilateral states do
  not receive the automatic `unmated for both connectors` suffix.

## Boundary

Only Dust exposure Condition extraction changes. Existing MFG, requirement,
method, and unrelated family rules remain unchanged.

## Validation

Run the focused extractor/normalizer/parser tests and `git diff --check`.
