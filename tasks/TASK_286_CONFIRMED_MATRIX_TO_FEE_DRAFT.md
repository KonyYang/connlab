# TASK_286_CONFIRMED_MATRIX_TO_FEE_DRAFT

## Status

Planned follow-up. Blocked until TASK_285 is complete.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Objective

Generate a reviewable `FeeEvaluationDraft` from the active Confirmed Matrix authority and a selected fee rule version.

This task creates backend fee-draft preview data only. It does not create a fee review UI and does not export Excel files.

## Business Context

Matrix is the execution authority map. Fee Evaluation is a derived output. ConnLab should use Confirmed Matrix rows, selected groups, group step tokens, sample quantities, planned `Day` values, and project/LTR metadata to produce a traceable fee draft for operator review.

The draft must remain semi-automatic: ConnLab fills deterministic candidates and highlights manual review items rather than pretending that all discounts and special lab judgments can be inferred.

## Scope

### In Scope

1. Add domain/application dataclasses for:
   - `FeeEvaluationDraft`
   - `FeeEvaluationHeader`
   - `FeeEvaluationGroup`
   - `FeeEvaluationLineItem`
   - `FeeEvaluationWarning`
2. Build a backend application service that reads active Confirmed Matrix authority for a project.
3. Use the active fee rule version from TASK_285.
4. Create line candidates from selected Matrix rows/groups only.
5. Preserve source traceability for each line:
   - confirmed authority id/revision
   - group key/label
   - source row id or row index
   - test item
   - section
   - step tokens
   - matched rule id and rule version id
6. Calculate deterministic fields where strategy allows:
   - unit price
   - units
   - base fee
   - discount default
   - testing fee
7. Mark ambiguous rows as `review_required`.
8. Return typed API response for fee-draft preview.
9. Add unit and integration tests for matching, selected-group-only output, rule-version traceability, manual-review rows, and no-confirmed-Matrix errors.

### Out Of Scope

1. No frontend review UI.
2. No Excel export.
3. No persistence for edited fee drafts.
4. No automatic discount decision beyond rule defaults.
5. No AI/LLM matching.
6. No StepInstance or execution persistence.
7. No changes to Matrix authority semantics.
8. No report/test-record generation changes.

## Data Semantics

### Fee Draft Source

Fee drafts are derived from active Confirmed Matrix authority, not draft Matrix state and not source Excel files.

### Pricing Rule Version

Every draft must include:

- `pricing_rule_version_id`
- `pricing_source_file_name`
- `pricing_source_hash`
- concrete `pricing_effective_from`
- `generated_at`

For the current V1 rule source, `pricing_effective_from` is the project `sample_received_date`.

### Review Required

Rows must be review-required when:

- no rule matches
- the matched rule uses `manual_required`
- the rule contains ambiguous pricing text
- discount or base-fee logic depends on operator judgment
- the Matrix row lacks enough quantity basis for deterministic calculation

## Acceptance Criteria

1. API can return a fee draft for a project with active Confirmed Matrix authority.
2. The draft includes pricing rule version metadata.
3. The draft records concrete `pricing_effective_from` from project `sample_received_date` for the current rule source.
4. Only selected/confirmed groups contribute fee line candidates.
5. Matrix source row/group/step traceability is preserved per line.
6. Deterministic rules produce calculated fees.
7. Manual/ambiguous/unmatched rows are marked review-required with business-readable reasons.
8. Existing `test_record_fee_*` services are not expanded into the new authority-driven fee engine.
9. Tests cover happy path, no authority, no rule match, manual-required, and selected-group behavior.
10. Scope boundary is held: no UI, no Excel export, no persistence for edited fee drafts.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task because it is a bounded application-service and typed-API feature built on existing Confirmed Matrix authority and deterministic matching rules.

## Required Execution Mode

Use `superpowers:executing-plans` for implementation. Also read `docs/project_management/TASK_EXECUTION_SKILL.md` before coding and run `docs/project_management/TASK_REVIEW_CHECKLIST.md` before completion.

## Stop Rule

Do not implement until this task file and its executable plan are reviewed and explicitly approved by the user.
