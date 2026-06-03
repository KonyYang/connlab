# TASK_285_FEE_RULE_SEED_LIBRARY

## Status

Planned. Awaiting user review and approval before implementation.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Objective

Create the first controlled ConnLab fee rule seed library from the fee workbook `Unit Price Reference` sheet, with explicit pricing-rule version metadata and deterministic rule matching support.

This task creates a structured fee rule source for later fee-draft generation. It does not generate fee drafts, does not calculate project fees from Matrix authority, and does not write Excel output.

## Business Context

The `Testing Prices` sheet is manually produced from the product specification Matrix, section detail, and the laboratory's fee reference rules. ConnLab needs a structured, versioned rule library so later tasks can generate reviewable fee-evaluation drafts from Confirmed Matrix authority.

The `Unit Price Reference` sheet may change over time. Each imported or curated rule seed must therefore carry a version identity and source traceability. Existing fee evaluations must never be silently repriced when a newer reference version appears.

## Scope

### In Scope

1. Add a versioned fee rule seed file under a bounded fee-evaluation module path.
2. Model rule metadata:
   - `version_id`
   - `source_file_name`
   - `source_sheet`
   - `source_hash`
   - `effective_from`
   - `created_at`
3. Model individual fee rules:
   - stable `rule_id`
   - display name
   - English/Chinese aliases
   - base fee text or numeric value where deterministic
   - unit price text or numeric value where deterministic
   - unit label
   - applicable standard text
   - range/condition text
   - calculation strategy
   - review-required flag and reason
4. Add deterministic matcher support for Matrix row text:
   - exact normalized alias match first
   - conservative token match second
   - no fuzzy AI matching
   - unmatched rows return explicit `no_rule_match`
5. Add tests for seed loading, version metadata, duplicate alias detection, matching, and review-required rules.

### Out Of Scope

1. No fee draft generation from Matrix.
2. No Excel export.
3. No UI for maintaining fee rules.
4. No SQLite fee-rule persistence.
5. No automatic activation from arbitrary external Excel files.
6. No AI/LLM rule extraction.
7. No changes to Matrix Editor.
8. No changes to Test Record/report generation.

## Data Semantics

### Fee Rule Version

A fee rule version is the pricing authority snapshot used by later fee-draft generation. Later tasks must record the selected `version_id` on generated fee drafts.

### Source Traceability

The source Excel file is a reference input, not the runtime data model. ConnLab runtime code must consume the reviewed structured seed file, not read `Unit Price Reference` dynamically during normal fee draft generation.

### Calculation Strategy

Allowed V1 strategy labels:

- `per_sample`
- `per_reading`
- `per_cycle`
- `per_hour`
- `per_photo`
- `per_specimen`
- `fixed_per_group`
- `manual_required`
- `unknown`

Rules with ambiguous base fee, discount, or special lab judgment must use `review_required: true`.

## Acceptance Criteria

1. A versioned fee rule seed file exists and includes source/version metadata.
2. The seed contains representative rules for common families visible in the reference sheet, including LLCR, Visual Examination, Durability, environmental tests, report preparation, and manual/complex items.
3. The loader rejects malformed rule files with actionable errors.
4. Duplicate aliases inside the active version are detected.
5. Matrix-style test item text can match deterministic aliases.
6. Ambiguous or special-case rules surface `review_required`.
7. Unmatched rows return a stable no-match result instead of guessing.
8. Tests cover seed loading, rule validation, matching, and no-match behavior.
9. Scope boundary is held: no Matrix-to-fee generation, no UI, no Excel output.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task because it is a bounded backend modeling and deterministic matching task with clear data validation and no broad architectural redesign.

## Required Execution Mode

Use `superpowers:executing-plans` for implementation. Also read `docs/project_management/TASK_EXECUTION_SKILL.md` before coding and run `docs/project_management/TASK_REVIEW_CHECKLIST.md` before completion.

## Stop Rule

Do not implement until this task file and its executable plan are reviewed and explicitly approved by the user.
