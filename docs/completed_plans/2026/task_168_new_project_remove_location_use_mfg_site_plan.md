# TASK_168 New Project Remove Location Field And Use Mfg Site Plan

> Status: proposed
> Created: 2026-05-11
> Phase: Phase 10F - Real public-drive LTR workbook operational closure

---

## 1. Scope

In scope:

- Remove `Location*` input from New Project setup confirmation UI.
- Keep `Test Type in sheet*` UI and backend logic unchanged (still required).
- Keep backend LTR workbook flow using application form `Mfg. Site` for J-column (already implemented in TASK_167 correction).
- Remove now-unused New Project setup `location` option wiring where safe.

Out of scope:

- No Precheck field removal (`manufacturing_site` remains in precheck review).
- No lookup-options global schema redesign.
- No changes to non-New-Project pages unless required by compile/runtime contract.

---

## 2. Design / UX Behavior

- Setup panel no longer shows `Location*` selector.
- Missing-required checks no longer include `location`.
- Existing `Test Type in sheet*` remains visible and required.
- Completion payload no longer sends `location` from frontend.
- If historical draft/session data still contains `location`, it is ignored.

---

## 3. File-Level Changes

1. `frontend/src/features/new-project/NewProjectSetupConfirmationPanel.tsx`
- Remove `Location*` field block and related props usage.

2. `frontend/src/pages/IntakeInboxPage.tsx`
- Remove `location` from setup values/missing validation.
- Remove manufacturing-site -> location auto-match side-effect.
- Stop passing `locationOptions` and `location` into setup panel.
- Keep `testTypeInSheet` required behavior unchanged.

3. `frontend/src/features/new-project/useNewProjectCompletion.ts`
- Remove `location` from completion request payload.

4. `frontend/src/api/client.ts`
- Update `CompleteNewProjectRequest` typing to make `location` optional/removed for frontend contract.
- Keep backend-compatible optional field if needed for transition.

5. `backend/api/routes_new_project_completion.py` (minimal contract cleanup)
- Keep `location` optional input for compatibility, but no longer required by frontend.
- Optionally keep `location_options` response temporarily to avoid broader coupling (or remove if all callers updated).

6. Tests
- Update affected frontend shell/static tests for setup panel fields and payload expectations.
- Run targeted integration tests for completion API path.

7. `docs/task_board.md`
- Add TASK_168 completion note and validation summary.

---

## 4. Risks and Controls

Risk:
- Hidden coupling in frontend tests still expecting `location`.

Control:
- Update expected setup fields and payload assertions in the same task.

Risk:
- Backend still exposing `location_options` while frontend no longer uses it.

Control:
- Keep compatibility now; schedule cleanup in a later explicit contract task if needed.

---

## 5. Validation Plan

- `npm run build` (from `frontend`)
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "new_project or intake or setup"`
- `py -m pytest tests\integration\test_new_project_completion_api.py -q`
- Optional: `py -m pytest tests\unit tests\integration -q`

