# TASK_362A Complete Fee Reference Base Seed

Status: planned; written design approved, implementation plan awaiting user approval

Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

Lane: `complete-fee-reference-base-seed`

## Goal

Create a complete, versioned Fee Evaluation rule foundation from every effective row in
`D:\Template\FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls`, sheet
`Unit Price Reference`, while preserving all existing reviewed ConnLab aliases and
automation decisions as a separate extension layer.

## Allowed Reason

- TASK_361L is complete/accepted according to its later detailed board evidence.
- The user explicitly approved the source-faithful base plus curated extension design.
- The current representative seed does not cover all effective source rows and returns
  `no_rule_match` for valid items such as Insulation Resistance.
- TASK_302 provides the controlled candidate, diff, validation, and explicit activation
  foundation required for a version refresh.

## Source Authority

- File: `D:\Template\FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls`
- Sheet: `Unit Price Reference`
- SHA256: `FB788038631AA0A12F1A052B630513718D9FA1BB64BAE647E897E18529EF8A5D`
- Effective test/report rows: `4-47` (44 rows)
- Global discount policy row: `49`

## Required Design

1. Preserve all source facts in a versioned source snapshot.
2. Preserve reviewed aliases/default behavior in a versioned extension layer.
3. Deterministically compile both layers into a new runtime seed.
4. Keep the old seed immutable and available.
5. Activate the new seed only after validation, diff, reload, matcher, and regression
   gates pass.
6. Keep ambiguous, ranged, conditional, or mixed-mode prices review-required rather than
   inventing a default.
7. Store row 49 as policy metadata; do not automatically calculate discounts in this
   task.

## Acceptance Criteria

1. The source snapshot contains exactly source rows 4-47 and policy row 49.
2. Every row 4-47 maps to exactly one base runtime rule.
3. All raw source fields remain traceable to the workbook row.
4. Existing extension-only rules and reviewed aliases remain available.
5. IR and DWV match known `per reading` rules rather than `no_rule_match`.
6. Complex rows preserve source price/base-fee text and require review when no approved
   deterministic evaluator exists.
7. The new seed uses a new version ID and exact source hash.
8. The old seed remains unchanged.
9. The active manifest changes only after candidate validation and regression success.
10. Normal runtime does not read the external workbook.
11. No real workbook, public-drive file, project folder, or database authority data is
    mutated during implementation or tests.

## May Touch

- `backend/modules/fee_evaluation/fee_rule_models.py`
- `backend/modules/fee_evaluation/fee_rule_seed_loader.py`
- `backend/modules/fee_evaluation/fee_rule_candidate_builder.py`
- `backend/modules/fee_evaluation/fee_rule_library_diff.py`
- `backend/modules/fee_evaluation/fee_rule_activation_validator.py`
- a narrowly named compiler/helper under `backend/modules/fee_evaluation/`
- new versioned JSON artifacts under `backend/modules/fee_evaluation/seeds/`
- `backend/modules/fee_evaluation/seeds/active_fee_rule_seed.json`
- focused fee-rule, matcher, default-fill, and draft-service tests
- TASK_362A design/plan/evidence and `docs/task_board.md`

## Must Not Touch

- external workbook contents or layout
- runtime Excel/COM parsing
- database schema/migrations
- pricing-draft V2/CAS semantics
- Fee Evaluation visual redesign or unrelated frontend behavior
- Matrix authority/parser/import, Point Profile, Measurement Plan
- Test Record, Report generation, LTR/public drive, project-folder workflows
- release/desktop/packaging
- automatic discount application
- speculative calculation formulas outside existing approved behavior

## Locked Paths

- `backend/modules/test_plan/**`
- `frontend/src/features/matrix-editor/**`
- `frontend/src/features/contact-measurement/**`
- `backend/application/project_matrix_*`
- `backend/infrastructure/office/**`
- `backend/application/public_folder_*`
- `backend/application/*ltr*`
- database migrations
- real workbook/public-drive/project-folder paths
- `.agents/**`
- `docs/project_management/**`
- `dist_release/**`
- `packaging/**`

## Dependencies And Order

1. User reviews and approves the written design.
2. Planner/Developer writes a file-level implementation plan.
3. User explicitly approves that implementation plan.
4. Developer implements TASK_362A only.
5. Reviewer validates source coverage, provenance, and no invented policy.
6. QA runs focused rule/default-fill tests and browser smoke.
7. Integrator verifies package isolation and activation gates.

`TASK_362B` may later add additional deterministic evaluators. It is not part of this
task and cannot start automatically.

## Design Reference

`docs/superpowers/specs/2026-07-16-complete-fee-reference-base-seed-design.md`

## Implementation Plan Reference

`docs/superpowers/plans/2026-07-16-complete-fee-reference-base-seed.md`
