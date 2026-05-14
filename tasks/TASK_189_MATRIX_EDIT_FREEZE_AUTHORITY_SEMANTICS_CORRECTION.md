# TASK_189 Matrix Edit/Freeze Authority Semantics Correction

> Status: proposed
> Created: 2026-05-14
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 0. Execution Gate

- Current phase: `Phase 11`.
- Current board prerequisite: `TASK_189_MATRIX_EDIT_AND_FREEZE_FOUNDATION` implemented but failed acceptance semantics review.
- Why this task is allowed now:
  - User-approved acceptance review identified authority lifecycle mismatch and validation severity mismatch.
  - This task is a controlled correction of TASK_189 semantics, not new scope expansion.

Implementation gate:

- Do not implement code until a separate correction plan document is created and explicitly approved by the user.

---

## 1. Purpose

Correct TASK_189 authority lifecycle semantics so Matrix editing and confirm/freeze behavior matches the approved design.

---

## 2. In Scope

Backend semantics correction:

- Editing a `reviewed` draft must create a candidate draft without superseding current reviewed authority.
- Supersede of old reviewed authority must happen only after candidate confirm succeeds.
- Confirm blocker/warning classification must follow approved rule set.

Tests correction:

- Remove/update tests that assert `edit reviewed => old reviewed superseded immediately`.
- Add tests for `edit reviewed => old reviewed remains authority until confirm`.
- Add tests for corrected blocker/warning severity boundaries.

Documentation correction:

- Sync `docs/task_board.md` TASK_189 completion statement to remove incorrect authority wording.

---

## 3. Out Of Scope

- No new Matrix import channels.
- No output ledger model redesign.
- No new UI workflow stage.
- No record form generation, report generation, AI review, or history reuse expansion.

---

## 4. Required Semantic Rules

Authority lifecycle:

1. Current reviewed draft is authority.
2. Edit on reviewed draft creates candidate draft.
3. Authority remains current reviewed draft before candidate confirm.
4. On candidate confirm success, candidate becomes reviewed authority and prior reviewed becomes superseded.

Validation severity:

- Blockers:
  - invalid group identity
  - invalid/non-numeric token
  - sequence start not 1
  - duplicate sequence
  - non-continuous sequence
  - missing test item
- Warnings:
  - method
  - condition
  - requirement/judgement criteria
  - duration
  - source trace
  - step description

---

## 5. Acceptance Criteria

- Editing reviewed draft no longer supersedes previous reviewed authority immediately.
- Confirm candidate supersedes old reviewed authority only after successful confirm.
- Blocker/warning classification matches approved plan semantics.
- Tests explicitly cover corrected semantics and reject old behavior.
- Task board statement reflects corrected behavior.

---

## 6. Validation Plan

```powershell
python -m pytest tests\unit\test_project_test_plan_matrix_edit_service.py tests\integration\test_project_test_plan_matrix_edit_api.py -q
```

```powershell
python -m pytest tests\unit\test_matrix_step_sequence_validation.py -q
```

```powershell
python -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

---

## 7. Stop Condition

Stop after this correction task is implemented, verified, and board-synced. Do not advance to next feature task in the same turn.
