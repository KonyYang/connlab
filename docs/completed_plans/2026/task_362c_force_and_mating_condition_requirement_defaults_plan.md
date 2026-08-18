# TASK_362C Force and Mating Condition Requirement Defaults Plan

## Discovery Gate

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package
controlled foundation.

Current task: `TASK_362C_FORCE_AND_MATING_CONDITION_REQUIREMENT_DEFAULTS`,
planned-only. `TASK_362B` is complete/accepted.

Why planning is allowed: the user explicitly confirmed uniform `mm/min` and
`N` review placeholders after the existing Force-family behavior was compared.

### Confirmed By User

- All Force/Mating Test Items use their section text to fill Condition and
  Requirement.
- Missing speed defaults to `mm/min`.
- Missing Requirement defaults to `N`.

### Confirmed By Repository Evidence

- Specialized condition branches currently have inconsistent no-speed behavior:
  Normal Force and Offset Mating use `mm/min`, while Mating, Floater, and
  Terminal Extraction return blank.
- Requirement extraction recognizes Normal, Offset, Floater, Terminal, and
  generic no-damage patterns but not every Force label.
- Generic Force condition collection does not create a consistent placeholder.

### Scope Decision

Implement a narrow Force/Mating final-default step after existing specialized
extraction and normalization. The Test Item predicate matches either a
normalized `force` token or an explicit pair of mating and un-mating concepts.
It does not match a label merely because it contains `mating`. The final step
must never overwrite source-derived numeric values, valid specialized
composite output, or existing meaningful Requirement text.

## Design

1. Add a single normalized Force/Mating family predicate shared by the final
   Condition and Requirement fallback decision. Match on the Test Item label
   only: `force`, or both mating and un-mating concepts. Do not inspect section
   prose to decide family membership.
2. Keep all specialized section extractors as first-choice parsing.
3. Consolidate or reuse the existing numeric Force speed recognition so a
   generic branch cannot preserve a label-only fragment such as `Cross Head
   Speed -` as a valid Condition.
4. After existing template fallback and normalization, set Condition to
   `mm/min` when the family matches and there is no usable numeric speed or
   valid specialized composite Condition. Preserve outputs such as `25.4
   mm/min` and `10 times, mm/min`.
5. After normalization, set Requirement to `N` only when the family matches
   and Requirement is empty. `No damage` and any parsed numeric/textual
   Requirement remain untouched.
6. Use focused test fixtures for each existing branch plus generic Force,
   explicit mating/un-mating without `force`, mating-only exclusion, missing
   data, label-only speed text, valid composite preservation, no-damage
   preservation, and a non-Force control.

## File Boundary

- Primary: `backend/modules/test_plan/spec_section_text_extractor.py` and its
  focused tests.
- Secondary only if required to prevent duplicate label normalization:
  `backend/modules/test_plan/mcr_text_normalizer.py`.
- No API, frontend, persistence, Fee, Office, or real-file code.

## Risks

- A broad substring match could classify unrelated text. The predicate is
  limited to Test Item labels and requires `force` or the explicit mating plus
  un-mating pair.
- Existing generic condition collection can return non-empty but unusable
  speed-label text. The Condition gate therefore validates a recognized speed
  or specialized composite result rather than relying on truthiness alone.
- Applying defaults before existing Requirement normalization could overwrite
  `No damage`; defaults therefore run last.
- This file already exceeds the project target size. No unrelated refactor is
  authorized; any structural residual is recorded for later dedicated work.

## Approval Boundary

Reviewer plan gate passed after tightening family membership and usable-speed
semantics. This plan authorizes no product code; a separate explicit user
implementation approval is still required.
