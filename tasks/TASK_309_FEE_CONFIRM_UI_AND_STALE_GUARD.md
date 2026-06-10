# TASK_309_FEE_CONFIRM_UI_AND_STALE_GUARD

Status: Complete.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

TASK_309 implementation is complete. TASK_310 requires a separate task file, executable plan, and explicit approval before implementation.

## Model Fit Assessment

GPT-5.3-codex is suitable for this task. The task is a bounded frontend/API-integration task that connects existing Fee Evaluation pricing draft persistence from TASK_301 with the Confirmed Fee backend authority foundation from TASK_308. It requires careful UI state and stale-status handling, but it does not require new pricing rules, Excel workbook editing, project-folder publishing, public-drive package placement, StepInstance execution persistence, AI review, permissions, or multi-user behavior.

## Goal

Add the operator-facing `Confirm Fee` action and confirmed/stale status to the Fee Evaluation page.

Confirmed Fee is the authority approval record for fee readiness. The operator should be able to edit the Fee Evaluation page, save those visible values as the current pricing draft, then confirm that saved draft as the pricing authority for later package tasks.

## Current Code Reality

- TASK_299/TASK_300/TASK_305 made the Fee Evaluation page editable and able to generate a Fee Form from current page values.
- TASK_301 persists Fee Evaluation pricing draft edits bound to active Confirmed Matrix id/revision and active fee rule version.
- TASK_308 added backend Confirmed Fee endpoints:
  - `GET /api/projects/{project_id}/confirmed-fee/latest`
  - `POST /api/projects/{project_id}/confirmed-fee/versions`
- The existing pricing draft response does not yet expose a saved pricing draft edit id to the frontend, but TASK_308 confirmation requires `expected_pricing_draft_edit_id`.
- The Fee Evaluation page already computes full and selected-scope totals, supports dirty local edits, and can save current edits.

## V1 User Contract

When the operator clicks `Confirm Fee`:

1. The frontend must build the current Fee Evaluation edit payload from the visible page state.
2. The frontend must save that payload through the existing pricing draft save endpoint.
3. The save response must return the saved pricing draft edit id.
4. The frontend must call the Confirmed Fee endpoint with that exact saved pricing draft edit id.
5. The confirmation summary must use full `All Group` totals, not the currently selected group filter.
6. The page must refresh Confirmed Fee status after success.

If local page values change after a successful confirmation, the page must show that the current visible edits are not confirmed yet, even if the backend latest Confirmed Fee is still current for the Matrix/rule tuple.

## In Scope

- Add Confirmed Fee API client types and functions in the frontend API layer.
- Expose `saved_draft_edit_id` from the existing pricing draft API response if needed by the UI.
- Add a compact Confirm Fee action/status area to the existing Fee Evaluation page.
- Confirm Fee by first saving current page edits and then creating a Confirmed Fee version.
- Display missing/current/stale/local-unconfirmed status in business-readable language.
- Show actionable errors for missing pricing draft, stale pricing draft, blank confirmer, expected draft id mismatch, and network/API failure.
- Add tests for the save-then-confirm workflow and stale/local-dirty status behavior.
- Update task board after implementation.

## Out Of Scope

- No Fee Form Excel gateway changes.
- No direct-download behavior changes.
- No ProjectOutputRecord changes.
- No project-folder placement or public-drive copy.
- No package orchestrator.
- No Customer Feedback Form generation.
- No Section 2 sync.
- No Matrix confirmation behavior changes.
- No StepInstance, execution persistence, image/evidence placement, report generation, AI review, permissions, multi-user, or server authority migration.
- No new pricing-rule calculation or rule-maintenance UI.

## Frontend/UI Preconditions

Before implementation, because this task changes frontend UI and user-facing copy, the agent must:

1. Read `AGENTS.md`.
2. Read `docs/task_board.md`.
3. Read this task file.
4. Load `$impeccable`.
5. Read `docs/02_ARCHITECTURE_RULES.md`.
6. Read `docs/frontend_architecture_rules.md`.
7. Read `docs/project_management/TASK_EXECUTION_SKILL.md`.
8. Read `docs/task_309_fee_confirm_ui_and_stale_guard_plan.md`.
9. Wait for explicit user approval before writing implementation code.

## UX Requirements

- Keep the Fee Evaluation page operator-focused and dense.
- Do not add a large management card.
- Prefer a compact status/action row near existing `Save changes` / `Fee Form` controls.
- The UI should distinguish:
  - `Not confirmed`
  - `Confirmed`
  - `Confirmed fee stale`
  - `Unconfirmed local changes`
  - `Cannot confirm`
- `Confirm Fee` must be visually separate from `Fee Form`; confirming does not generate or download the Excel file.
- The default confirmer for V1 may be the existing local operator label if available; otherwise use a non-empty editable fallback such as `Lab User`.

## Stale Semantics

Backend status is current only when latest Confirmed Fee still matches:

- current active Confirmed Matrix id
- current active Confirmed Matrix revision
- current active fee rule version id

Frontend local status must additionally treat the page as not fully confirmed when:

- pricing rows or summary fields have unsaved local edits
- the latest saved pricing draft id is different from the latest confirmed fee pricing draft id
- saved pricing draft load returned `missing` or `stale`

Implementation must keep enough page state to evaluate those conditions. V1 should track the latest saved pricing draft edit id returned by pricing-draft load/save and compare it with latest Confirmed Fee `pricing_draft_edit_id`.

## Acceptance Criteria

- Fee Evaluation page loads Confirmed Fee latest status.
- Missing Confirmed Fee shows a business-readable `Not confirmed` status.
- Current Confirmed Fee shows confirmed revision, confirmer, timestamp, and summary values without claiming a Fee Form was generated.
- Stale Confirmed Fee shows a warning explaining that Matrix authority or fee rule version changed.
- Editing any pricing row or summary field after confirmation changes the UI to `Unconfirmed local changes`.
- Clicking `Confirm Fee` saves current visible page values first, then confirms the saved draft id returned by that save.
- If pricing draft save succeeds but the response does not include `saved_draft_edit_id`, `Confirm Fee` must stop before calling the Confirmed Fee endpoint and show actionable copy telling the operator to save or refresh before confirming.
- Confirmation summary uses all Fee Evaluation rows and summary values, independent of the selected group filter.
- If latest saved pricing draft id differs from latest Confirmed Fee `pricing_draft_edit_id`, the page shows `Unconfirmed saved changes`.
- Blank confirmer is blocked before calling the Confirmed Fee endpoint.
- Confirmed Fee errors are displayed inline with actionable copy.
- Existing `Save changes` and `Fee Form` behavior remains unchanged.
- No Excel workbook is generated as a side effect of Confirm Fee.
- No ProjectOutputRecord or project-folder output is created as a side effect.

## Required Validation

The executable plan must define exact commands. Expected coverage includes:

- Frontend tests for Confirm Fee status rendering.
- Frontend tests for save-current-edits-then-confirm workflow.
- Frontend tests for dirty edits making confirmed status locally unconfirmed.
- Frontend API client/static tests for Confirmed Fee endpoints and saved pricing draft id exposure.
- Backend/API tests if pricing draft response is extended.
- Existing Fee Evaluation page tests remain passing.
- `npm run build`.
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or project_workbench"`.
- `git diff --check`.

## Stop Point

After TASK_309 implementation and validation, stop. Do not proceed to TASK_310 without a separate task file / executable plan review and explicit approval.
