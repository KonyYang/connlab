# TASK_171 New Project Unique Draft And Reinitialize Rebuild Plan

> Status: proposed
> Created: 2026-05-11
> Phase: Phase 10F - Real public-drive LTR workbook operational closure

---

## 0. Execution Context

- Current phase: `Phase 10F`
- Current active task: `none`
- Why this task is allowed: user explicitly requested optimization evaluation and agreed to unified strategy with clean rebuild semantics.

---

## 1. Problem

Current duplicate-draft handling has branching paths (same-package vs cross-package). In practice this can:

- preserve hidden state residue when "reinitialize" uses update semantics
- allow historical ambiguity about which draft is being continued
- increase maintenance complexity with no UI-level draft chooser

Business reality is simple: intake draft is a transient precheck preview surface with low edit depth. Operator intent is usually either:

- continue existing draft, or
- start over cleanly

---

## 2. Decision

Unify duplicate handling into **single-identity unique draft** model:

1. one business identity -> one active draft
2. `Load existing` -> continue that draft
3. `Reinitialize` -> **clean rebuild** (delete old draft state then create new clean draft state)
4. no parallel multi-draft choices for same identity

---

## 3. Scope

In scope:

- unify backend duplicate resolution path in New Project intake flow
- make `Reinitialize` semantics deterministic: rebuild, not patch/update
- ensure old draft residual data cannot survive reinitialize
- preserve current two-button UI flow (`Load existing`, `Reinitialize`)
- add tests for uniqueness and rebuild behavior

Out of scope:

- no new UI draft-management page
- no historical draft archive surface
- no workflow expansion beyond current duplicate resolution step

---

## 4. Functional Design

### 4.1 Identity Rule

Use existing duplicate identity rule (email-source + selected application form identity) as key.

For one key:

- at most one active draft chain is available for continue/reinitialize

### 4.2 `Load existing`

- resolve to existing case/draft by identity
- return existing records without mutation

### 4.3 `Reinitialize`

Clean rebuild semantics:

1. locate existing case/draft by identity
2. delete old draft content and rebuild clean state
3. keep one active draft only
4. clear manual overrides and transient review-state payloads
5. parse selected application form again and create fresh draft payload

Implementation note:

- case id reuse is allowed if simpler, but draft state must be physically recreated to avoid residuals.
- if safer in current repository model, delete+recreate both case and draft; return the new pair consistently.

### 4.4 Cross-Package Path

Remove branch-specific behavior differences. `Reinitialize` should yield same clean result regardless of prior package location, while still enforcing existing safety guard (no replace on confirmed project paths).

---

## 5. File-Level Change Plan

Primary backend:

- `backend/application/intake_form_selection_service.py`
  - simplify duplicate resolution flow
  - enforce unique active draft behavior
  - convert reinitialize to clean rebuild semantics

- `backend/application/new_project_application_draft_service.py`
  - align no-form duplicate resolution with same rebuild principle where applicable

Potential repository touchpoints:

- `backend/infrastructure/storage/repositories/intake.py`
  - ensure delete/recreate sequence is atomic enough for current SQLite model

Frontend (minimal):

- keep current buttons and action values
- adjust copy only if needed to reflect deterministic rebuild behavior

Tests:

- `tests/unit/test_intake_form_selection_service.py`
  - same identity reinitialize removes residual draft state
  - no multi-draft ambiguity for same identity

- `tests/integration/test_msg_package_intake_api.py`
  - `open_existing` continues same draft
  - `replace_existing` rebuilds clean draft deterministically

- `tests/unit/test_frontend_shell_files.py`
  - no branch-specific stale expectations remain

Docs:

- `docs/task_board.md` completion note + validation

---

## 6. Risks And Controls

Risk:
- delete+create may temporarily break references during operation.

Control:
- perform in controlled order with transactional repository operations where possible.

Risk:
- existing tests may assume old branch behavior.

Control:
- update tests to explicit business contract: unique draft + deterministic rebuild.

Risk:
- edge cases where existing case is already confirmed.

Control:
- keep strict block on confirmed/non-replaceable records; return clear business error.

---

## 7. Validation Plan

- `py -m pytest tests\unit\test_intake_form_selection_service.py -q`
- `py -m pytest tests\integration\test_msg_package_intake_api.py -q`
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "duplicate or new_project"`
- optional confidence run: `py -m pytest tests\unit tests\integration -q`

Manual smoke:

1. import a package and create draft
2. trigger duplicate prompt
3. click `Load existing` -> verify existing edits remain
4. click `Reinitialize` -> verify clean draft without prior overrides

---

## 8. Acceptance Criteria

1. duplicate identity has one deterministic active draft path
2. `Reinitialize` creates clean state with no residual override/history payload
3. `Load existing` does not create extra case/draft
4. no random draft selection behavior remains
5. tests and board update complete

