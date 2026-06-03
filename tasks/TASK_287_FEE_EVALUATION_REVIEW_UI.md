# TASK_287_FEE_EVALUATION_REVIEW_UI

## Status

Planned follow-up. Blocked until TASK_286 is complete.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Objective

Add a restrained operator review surface for the Matrix-derived Fee Evaluation draft.

This task lets the user inspect generated fee line candidates, identify review-required items, and confirm readiness for export. It does not write Excel output.

## Business Context

ConnLab fee generation is intentionally semi-automatic. The system should fill the mechanical parts of the fee table and make uncertain items explicit. Operators must be able to review rule matches, quantities, discounts, base fees, and warnings before generating the official Excel fee form.

## Scope

### In Scope

1. Add frontend API client types for the fee-draft preview endpoint from TASK_286.
2. Add a Workbench-derived-output entry for Fee Evaluation:
   - missing
   - draft ready
   - needs review
   - stale against Matrix or pricing version
3. Add a Fee Evaluation Review surface in product UI style.
4. Show fee draft header:
   - LTR number when available
   - project/sample description
   - pricing rule version id
   - generated timestamp
5. Show review table with:
   - group
   - Matrix source/test item
   - matched fee rule
   - unit price
   - units
   - base fee
   - discount
   - calculated fee
   - review status
6. Highlight review-required rows with business-readable reasons.
7. Keep operator edits local to the review surface unless a later task explicitly adds persistence.
8. Add frontend tests for loading, needs-review state, no-authority state, and review table rendering.

### Out Of Scope

1. No Excel export.
2. No persistent edited fee draft.
3. No pricing rule maintenance UI.
4. No direct Matrix editing in the fee review surface.
5. No AI/LLM fee explanation.
6. No StepInstance or execution persistence.
7. No changes to Matrix Editor authority behavior.

## UI Boundary

Matrix Editor remains the authority definition surface. Fee Evaluation Review is a derived-output review surface and must not become an Excel-like replacement for Matrix editing.

Frontend work must follow `$impeccable`, `docs/02_ARCHITECTURE_RULES.md`, and `docs/frontend_architecture_rules.md`.

## Acceptance Criteria

1. Workbench shows Fee Evaluation as a derived output with clear status.
2. Opening the review surface fetches the fee draft preview.
3. Review table displays calculated and review-required rows.
4. Review-required rows show concise reasons.
5. No Excel export action is active in this task.
6. UI copy avoids technical backend terms and remains operator-readable.
7. Tests cover loading, empty/no-authority, calculated rows, and review-required rows.
8. Scope boundary is held: no export, no rule maintenance UI, no Matrix editing changes.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task because it is a bounded frontend/API-consumer workflow with existing product UI rules and a typed backend response from TASK_286.

## Required Execution Mode

Use `superpowers:executing-plans` for implementation. Also read `docs/project_management/TASK_EXECUTION_SKILL.md` before coding and run `docs/project_management/TASK_REVIEW_CHECKLIST.md` before completion.

## Stop Rule

Do not implement until this task file and its executable plan are reviewed and explicitly approved by the user.
