# TASK_362C Force and Mating Defaults Developer Evidence

Status: developer_complete
Date: 2026-07-17
Role: Developer

## Implementation

- Added a Test Item-only family predicate matching a `force` token or distinct
  mating plus un-mating concepts.
- Consolidated numeric displacement/cross-head speed extraction for existing
  Force branches.
- Replaced generic label-fragment collection with numeric speed extraction.
- Applied `mm/min` and `N` review placeholders after existing template fallback
  and MCR normalization.
- Preserved explicit speeds, specialized composite Conditions, numeric force
  Requirements, and meaningful text such as `No damage`.

## TDD Evidence

Initial TASK_362C tests failed as expected: `7 failed, 1 passed`, proving the
missing defaults and label-only speed defect. A self-review boundary test then
failed specifically for `Un-mating cycles`, proving the first predicate counted
the `mating` token inside `un mating`; the implementation was corrected to
require a distinct mating concept.

## Scope

Product changes are limited to the existing specification-section extraction
path plus focused parser tests. No real files or persistence were used.
