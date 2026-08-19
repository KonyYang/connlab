# Mating Force Condition Default

## Scope

Extract the numeric cross-head speed for `Mating/Un-mating Force` rows from
the specification section.

## Expected Output

- `Cross Head Speed - 25.4±6 mm per minute` becomes `25.4 mm/min`.
- If the speed number is absent, Condition remains empty.

## Boundary

Only the Mating/Un-mating Force Condition rule changes. Existing Requirement,
Offset Mating Force, Floater Displacement Force, and unrelated family rules
remain unchanged.

## Validation

Run the focused extractor/normalizer/parser tests and `git diff --check`.
