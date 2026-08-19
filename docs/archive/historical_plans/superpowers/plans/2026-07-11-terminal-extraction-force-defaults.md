# Terminal Extraction Force Defaults

## Scope

Populate the Matrix defaults for `Terminal extraction force` from section
`7.6`.

## Expected Output

- `Cross Head Speed - 50mm max per minute` becomes `50 mm/min`.
- `minimum extraction force ... is 150N` becomes `≥ 150 N`.
- Missing source numbers remain blank.

## Boundary

Only the Terminal extraction force family gets this specialized rule. Existing
Mating/Un-mating Force, Offset Mating Force, Floater Displacement Force, and
unrelated family rules remain unchanged.

## Validation

Run the focused extractor/normalizer/parser tests and `git diff --check`.
