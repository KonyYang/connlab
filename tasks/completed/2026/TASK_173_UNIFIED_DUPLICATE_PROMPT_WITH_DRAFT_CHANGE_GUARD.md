# TASK_173 Unified Duplicate Prompt With Draft-Change Guard

> Status: complete
> Created: 2026-05-11
> Phase: Phase 10F - Real public-drive LTR workbook operational closure

---

## 0. Execution Gate

- Current phase: `Phase 10F`
- Current active task in board: `none`
- Why this task is allowed now: user explicitly requested a unified duplicate confirmation behavior and asked for a task document before implementation.

---

## 1. Purpose

Unify duplicate-draft handling for New Project so single-form and multi-form email packages behave consistently.

Target behavior:

- whenever an existing unconfirmed draft is detected, always show `Load existing / Reinitialize`;
- allow short-session decision reuse only when draft is unchanged.

---

## 2. Scope

In scope:

- unify duplicate prompt trigger for:
  - same package + same selected application form
  - same package + multi-form scenarios
  - cross-package same-email duplicate draft scenarios
- add draft-change guard for session decision reuse.
- add backend and frontend tests for the decision matrix.

Out of scope:

- no change to confirmed-project duplicate policy boundary.
- no LTR workbook flow changes.
- no database schema migration.

---

## 3. Business Rules

### 3.1 Always Prompt Rule

When duplicate target is an existing unconfirmed draft, UI must always ask:

- `Load existing`
- `Reinitialize`

No silent branch based on single-form vs multi-form package shape.

### 3.2 Session Reuse Rule (Guarded)

Frontend may reuse the last duplicate decision without re-prompt only if all are true:

1. same `case_id`
2. same selected form asset target
3. draft unchanged since decision (compare `draft.updated_at` or stable content signature)

If any condition fails, prompt again.

### 3.3 Action Semantics

- `Load existing`: open current existing draft, no overwrite.
- `Reinitialize`: rebuild same case draft content (no new case creation), replacing prior draft payload.

---

## 4. Implementation Plan

1. Backend selection/draft services
   - remove inconsistent single-form bypass branch for duplicate prompt.
   - enforce same duplicate contract for same-package and cross-package unconfirmed matches.
2. Frontend duplicate state
   - store last resolved duplicate decision with:
     - `case_id`
     - `selected_form_asset_id`
     - `draft_updated_at` snapshot
   - apply guarded reuse rule.
3. API contract
   - keep existing duplicate conflict payload shape; include/confirm `existing_case_id` and draft freshness data if needed.

---

## 5. Risks And Mitigation

1. Prompt fatigue on repeated clicks  
Mitigation: guarded session reuse only when draft unchanged.

2. Mis-overwrite risk  
Mitigation: any draft change invalidates reuse and forces prompt.

3. Regression in existing duplicate tests  
Mitigation: add explicit single-form vs multi-form parity tests.

---

## 6. Validation Plan

- Unit tests (backend):
  - same-package single-form duplicate now triggers duplicate conflict.
  - same-package multi-form duplicate keeps same conflict behavior.
  - reinitialize keeps one case and replaces draft payload.
- Unit tests (frontend):
  - decision reused only when same case + same asset + unchanged draft marker.
  - decision invalidated after any draft edit.
- Integration/API tests:
  - repeated import/select on single-form and multi-form packages both surface identical duplicate prompt contract.

Manual smoke:

1. Single-form email:
   - import -> duplicate prompt shown
   - choose `Load existing`
   - edit draft field
   - click import/select again -> prompt appears again
2. Multi-form email:
   - repeat same form selection -> same prompt semantics as above

---

## 7. Acceptance Criteria

- Single-form and multi-form duplicate interactions are behaviorally consistent.
- Duplicate prompt is always shown for unconfirmed duplicate drafts unless guarded reuse conditions are fully met.
- Draft edits invalidate prior session decision and re-enable prompt.
- No extra case creation during `Reinitialize`.

---

## 8. Completion Notes

- Backend duplicate detection now keeps consistent prompt semantics for same-package single-form and multi-form scenarios:
  - removed single-form bypass branch in `IntakeFormSelectionService._find_selected_form_duplicate`.
- Frontend now supports guarded session decision reuse:
  - stores last duplicate resolution decision (`case_id`, `asset_id`, `action`);
  - automatically reuses that decision only when draft is unchanged in current session;
  - any draft edit invalidates reuse and re-enables duplicate prompt.
- Reinitialize behavior remains same-case draft rebuild (no extra case creation).

Changed files:

- `backend/application/intake_form_selection_service.py`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `tests/unit/test_intake_form_selection_service.py`

Validation:

- `py -m pytest tests/unit/test_intake_form_selection_service.py -q` passed (`21 passed`)
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "duplicate or new_project"` passed (`8 passed, 50 deselected`)
- `npm run build` (frontend) passed
