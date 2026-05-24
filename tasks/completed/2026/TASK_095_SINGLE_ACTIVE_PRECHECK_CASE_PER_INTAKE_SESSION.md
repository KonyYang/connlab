# TASK_095_SINGLE_ACTIVE_PRECHECK_CASE_PER_INTAKE_SESSION

## Status

done

## Current Phase

Phase 10A is complete. This task is a proposed controlled follow-up for Intake to Precheck session consistency.

## Active Task Rule

Do not implement this task until `docs/task_board.md` explicitly marks `TASK_095_SINGLE_ACTIVE_PRECHECK_CASE_PER_INTAKE_SESSION` as the current active task or a ready task approved by the user.

When active, this task is allowed because it stays inside the MVP Intake and Precheck flow:

- Project stage: Intake before Project confirmation.
- Input: imported email package, direct Word package, selected application-form asset, current intake session.
- Output: one active Precheck review case for the current selected application form.
- Domain impact: `IntakePackage`, `IntakeAsset`, `IntakeCase`, `IntakeDraft`; no new future-scope domain object.
- MVP scope: application form intake and precheck only.

## User Problem

Manual smoke found a serious confusion path:

1. Import or select application form A in Intake.
2. Continue to Precheck. Backend creates a review case.
3. Go back to Intake.
4. Select application form B and continue to Precheck.
5. Backend creates another review case.
6. Precheck shows both cases in a `Review cases` card and both can be edited.

This is confusing because the operator is in one New Project intake workflow. Before Project confirmation, the workflow should not behave like a multi-case work queue.

## Assessment

The user recommendation is reasonable.

Reasoning:

- ConnLab's MVP workflow is Project-first and one selected application form should lead to one Project confirmation path.
- Multiple editable Precheck cases inside one current Intake session make it unclear which application form will become the project.
- Preserving edits is correct only when returning to the same selected application form.
- Switching to a different selected application form should replace the current draft path and clear previous manual overrides so old edits cannot leak into the new form.
- Re-importing a new email package is a new source context and should reset Intake session state.
- The `Review cases` card is not needed for the current New Project workflow and contradicts the "one selected application form creates one project only after confirmation" gate.

The previous multi-case behavior may have been useful for old multi-form package review, but it is not appropriate for the current step-style Intake to Precheck path.

## Goal

Make the current Intake to Precheck workflow support exactly one active review case at a time before Project confirmation.

Expected behavior:

1. Returning from Precheck to Intake and continuing with the same selected application form reopens the same case and preserves saved corrections.
2. Returning from Precheck to Intake and selecting a different application form replaces the active case path with a case/draft based on the new form.
3. Re-importing an email package starts a clean Intake session and does not carry over previous selected asset, selected case, or Precheck edits.
4. The Precheck page does not display the `Review cases` case-switcher card in the New Project workflow.

## Inputs

- Existing intake package ID.
- Selected application-form asset ID.
- Existing review cases and drafts for the package.
- App-level Intake session state from `frontend/src/features/intake/intakeSession`.

## Outputs

- One active Precheck case ID in the current frontend session.
- Backend selection behavior that reuses or replaces the current case consistently.
- Clean session state after new package import.
- Precheck UI without a multi-case selector card.

## Modules

- `backend/application/intake_form_selection_service.py`
- backend intake repositories if an explicit inactive/replaced state is already supported or needs a narrow repository method
- `backend/api/routes_intake.py`
- `frontend/src/App.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/pages/IntakeCaseReviewPage.tsx`
- `frontend/src/features/intake/*`
- `frontend/src/features/precheck/*`
- `tests/unit`
- `tests/integration`

## Required Read Order

Before implementation, read:

1. `AGENTS.md`
2. `docs/task_board.md`
3. `tasks/TASK_095_SINGLE_ACTIVE_PRECHECK_CASE_PER_INTAKE_SESSION.md`
4. `docs/project_management/TASK_EXECUTION_SKILL.md`
5. `docs/project_management/TASK_REVIEW_CHECKLIST.md`
6. `docs/02_ARCHITECTURE_RULES.md`
7. `docs/frontend_architecture_rules.md`
8. `PRODUCT.md`
9. `DESIGN.md`

Use `$impeccable` before frontend/UI or UX-copy changes.

## Design Direction

### Backend Case Selection Rule

`IntakeFormSelectionService.select_form_asset()` should return one active case for the selected asset.

Required rules:

- If an existing unconfirmed case already belongs to the same selected asset, reuse it and preserve manual overrides.
- If the operator selects a different application-form asset before Project confirmation, reuse the current unconfirmed case where possible by rebinding it to the new asset, and clear manual overrides.
- If rebinding is not possible because the old case is already confirmed, create a new case for the new selected asset.
- Do not allow old unconfirmed cases for other selected assets to remain visible as parallel editable cases in the current Precheck review response.

Implementation options:

1. Preferred: add a narrow "active case" concept at the application/API response boundary and filter Precheck review to the selected active case.
2. Acceptable if simpler and safe: rebind the reusable unconfirmed case instead of creating a second case, preserving only confirmed historical cases for traceability.

Do not delete source files, packages, assets, or confirmed projects.

### Draft Preservation Rule

Manual overrides are preserved only when the selected asset is unchanged.

Required behavior:

- Same `selected_form_asset_id`: keep `manual_overrides_json`.
- Different `selected_form_asset_id`: rebuild parsed draft fields from the new form and clear `manual_overrides_json`.
- New imported package: clear previous session selected asset, selected Word asset, selected Precheck case, and any frontend error/success state tied to the previous package.

### Frontend Session Rule

The app-level Intake session must represent one current source package and one current selected form.

Required behavior:

- Importing a new `.msg` package replaces the previous session instead of merging with it.
- Direct Word upload replaces the previous session.
- Supplemental Word upload into the same email package updates the same session.
- Back to Intake preserves selected form and case only for the same package and same selected asset.
- Selecting a different eligible application form clears the previous selected Precheck case until the backend returns the new case ID.

### Precheck UI Rule

Remove the `Review cases` card from the current New Project Precheck page.

Required behavior:

- The page edits only the active case.
- If backend returns multiple cases for historical reasons, the route should select the active case from session or API response and not present a switcher.
- If no active case can be resolved, show an actionable empty/error state that sends the operator back to Intake.

Do not replace the card with a different multi-case control.

## Out Of Scope

- Do not implement a general multi-case management screen.
- Do not implement Matrix, Report Generation, AI review, LAN deployment, permissions, Outlook inbox auto-scan, email sending, or LTR workbook work.
- Do not delete confirmed cases or confirmed projects.
- Do not redesign the entire Intake or Precheck page.
- Do not add a new frontend state management library.
- Do not change deterministic Precheck business rules except where needed to bind the active case.
- Do not introduce destructive cleanup of stored files.

## Acceptance Criteria

- Starting from application form A creates or opens one Precheck case.
- Saving corrections in Precheck for A, returning to Intake, and continuing with A again shows the saved corrections.
- Returning to Intake, selecting application form B, and continuing to Precheck shows B's parsed data, not A's saved corrections.
- After selecting B, the Precheck page does not show A and B as editable case cards.
- Importing a new email package clears prior package selection, selected form, selected Precheck case, and Precheck continuation state.
- Direct Word upload after a previous package also starts a clean session.
- Supplemental Word upload into the same email package keeps the same source package context.
- Backend selection remains authoritative if frontend session state is stale.
- The `Review cases` card is removed from the current Precheck workflow.
- No future-scope features are added.

## Validation

Add or update tests:

- Unit test: selecting the same asset reuses the same case and preserves manual overrides.
- Unit test: selecting a different asset reuses/replaces the active unconfirmed case and clears manual overrides.
- Unit test or integration test: Precheck review for the current workflow exposes only the active case, or the frontend selects only the active case without showing a switcher.
- Integration test: selecting A then B in the same package does not produce two editable active Precheck cases.
- Frontend static test: `IntakeCaseReviewPage` no longer renders `Review cases` / `case-switcher`.
- Frontend static test: new package import resets selected case/session fields.

Recommended validation commands:

```powershell
py -m pytest tests\unit\test_intake_form_selection_service.py -q
py -m pytest tests\integration\test_msg_package_intake_api.py -q
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

If frontend files are changed, also run from `frontend/`:

```powershell
npm run build
```

Manual Windows verification:

1. Import or upload application form A.
2. Continue to Precheck, edit and save a visible field.
3. Back to Intake, continue with A again, and verify the saved field remains.
4. Back to Intake, select application form B, continue to Precheck, and verify B data appears.
5. Verify no `Review cases` card appears.
6. Import a new email package and verify previous selected case/form state is gone.

## Required Markdown Updates After Completion

When this task is implemented and verified, update these Markdown files in the same turn:

1. `docs/task_board.md`
   - Mark `TASK_095_SINGLE_ACTIVE_PRECHECK_CASE_PER_INTAKE_SESSION` done.
   - Update `Last Updated`.
   - Add completion notes.
   - Add validation summary.
   - Set the next recommended task or stop point.

2. `tasks/TASK_095_SINGLE_ACTIVE_PRECHECK_CASE_PER_INTAKE_SESSION.md`
   - Change `Status` from `proposed` or `active` to `done`.
   - Add completion notes.
   - Record exact validation commands and results.
   - Record known limitations.

3. `docs/frontend_architecture_rules.md`
   - Update only if new active-case selector/session conventions become stable frontend rules.

4. `docs/intake_precheck_field_contract.md`
   - Update only if the active-case behavior changes documented Intake/Precheck workflow expectations.

Do not update unrelated future-scope documentation.

## Task Review Checklist

After implementation, run `docs/project_management/TASK_REVIEW_CHECKLIST.md` and explicitly verify:

- API routes still call application services only.
- Frontend session state does not invent persisted business truth.
- Backend remains authoritative when selecting the application form.
- Manual overrides cannot leak from one selected form to another.
- The task did not add Matrix, Report, AI review, LAN, permissions, Outlook inbox auto-scan, email sending, or LTR workbook work.

## Stop Rule

After completing this task:

1. Update the required Markdown files.
2. Report validation results.
3. Stop.
4. Do not start the next task.

## Completion Notes

Completed on 2026-05-04.

- `IntakeFormSelectionService` now reuses any unconfirmed package case when the operator selects a different application form before Project confirmation.
- Manual draft overrides are preserved only when the same selected form is reopened. Rebinding the active case to a different form rebuilds parsed draft fields and clears manual overrides.
- Confirmed cases are not rebound; selecting another form after confirmation creates a new case and leaves the confirmed case intact.
- The New Project Precheck page no longer renders the `Review cases` switcher/card, so the current workflow edits only the resolved active case.
- Intake session behavior remains one current source package plus one selected form: new imports/direct uploads set `selectedPrecheckCaseId` to null, while successful selection stores the backend-returned case ID.
- `docs/intake_precheck_field_contract.md` and `docs/frontend_architecture_rules.md` now record the one-active-case/session convention.

Validation:

```powershell
py -m pytest tests\unit\test_intake_form_selection_service.py -q
```

Result: `13 passed`.

```powershell
py -m pytest tests\integration\test_msg_package_intake_api.py -q
```

Result: `10 passed`.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

Result: `44 passed`.

```powershell
npm run build
```

Result: passed.

Known limitations:

- Historical packages that already contain multiple unconfirmed cases are not destructively cleaned up. The current New Project UI no longer exposes a switcher, and new A-to-B selection no longer creates parallel unconfirmed cases.
- Manual browser smoke with two real application forms is still recommended for operator confidence.
