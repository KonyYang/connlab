# TASK 008 — Precheck Engine

## Goal

Implement deterministic precheck rules for parsed application forms.

## Scope

Rules only. No UI.

## Requirements

- Add `backend/modules/precheck/precheck_engine.py`.
- Implement rule classes/functions.
- Input: parsed ApplicationForm + SampleInfo rows + optional registered attachments.
- Output: PrecheckResult + PrecheckIssue list.

## Required Rules

- FORM-001 Form number expected E-3718.
- FORM-002 Form revision expected Rev H.
- REQUESTOR required fields.
- SAMPLE required fields per non-empty row.
- SAMPLE quantity expression warning for `+`, `/`, or free text.
- TESTING description missing error.
- TESTING attachment reference warning if no attachments registered.
- SUBCONTRACT missing warning.
- LAB_SECTION estimated completion date missing warning.

## Tests

- Valid application form produces PASSED or no ERROR.
- Missing sample field produces issue.
- “依附件” without attachment produces warning.
- Wrong Rev produces issue.

## Out of Scope

- No AI.
- No duration estimation.
- No standard/spec verification.

## Acceptance Criteria

- Precheck is deterministic.
- Issue messages are actionable.
