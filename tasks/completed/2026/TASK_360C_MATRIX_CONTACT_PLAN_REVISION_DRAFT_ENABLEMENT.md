# TASK_360C Matrix Contact Plan Revision-Draft Enablement

## Status

Complete / Integrator accepted.

## Current Phase / Active Task / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Active task: `TASK_360C_MATRIX_CONTACT_PLAN_REVISION_DRAFT_ENABLEMENT`.
- Role: Integrator packaging/readiness.
- Why allowed: `TASK_360A` and `TASK_360B` are accepted; Developer implementation completed; Reviewer implementation re-gate passed; QA gate passed; Integrator package isolation is the next legal gate.

## User Goal

After confirming a Matrix, an operator must be able to explicitly open an editable revision draft, use Contact Measurement Plan against eligible LLCR/CR Group-Step targets, save quantities, and reconfirm. The existing confirmed authority and all derived consumers must remain intact until reconfirmation.

## Confirmed By User

- On project `72fbbfa290294da9a507344b68ff900f`, the operator confirmed a Matrix, returned to Workbench, re-entered Matrix Editor, and entered LLCR families HP `4`, LP `5`, Signal `24`.
- The card correctly derived `Readings / sample: 33`, but rendered `0 targets`; `Apply to blank contact targets` was disabled and Save reported `Save the Matrix draft before setting Step quantities.`
- Specialized workbook preview correctly blocked with `No included LLCR/CR targets` and generated no workbook.
- The requested correction is the Matrix draft bridge, not a change to confirmed authority, Fee, specialized workbook generation, generic Test Record, parser/import, LTR/public-drive, or lifecycle semantics.

## Confirmed By Repository Evidence

- `MatrixEditorSessionService.get_seed()` reconstructs the editor from active confirmed authority when no current revision draft exists, returning `editor_draft_id = null` and `draft_status = missing`.
- `MatrixEditorWorkspace` clears `stepQuantityItems` when `savedEditorDraftId` is absent. Contact target coverage is derived from those items, producing `0 targets`; its save handler emits the observed draft-required message.
- `POST /api/projects/{project_id}/matrix-revisions` and the existing typed `createMatrixRevisionDraft()` client helper create one revision draft from active confirmed authority.
- Revision construction carries confirmed Step quantities and `contact_plan` into the draft through `carry_forward_step_quantities()`.
- The current Matrix Editor intentionally exposes no `Create Revision Draft` action. Existing focused UI tests assert that historical revision actions are absent.

## Corrective Contract

1. A confirmed Matrix remains immutable authority. Entering Matrix Editor without an open revision draft is an authority view, not a writable Contact Measurement Plan surface.
2. When the project has active confirmed authority and no current draft, Matrix Editor provides one compact inline action: `Open editable Matrix draft`.
3. The action calls only the existing revision-draft endpoint. It creates no confirmed revision and changes no Fee/Test Record/workbook output by itself.
4. On success, the editor reloads its existing session seed and draft Step quantities. Eligible LLCR/CR targets then derive from that draft and can accept blank-only common plan application and save.
5. An already-open current revision draft is loaded directly; no duplicate creation action or duplicate write is issued.
6. The Contact Measurement Plan edit/apply/save controls are unavailable until a writable draft exists. Its specialized workbook preview/generate path remains a separate confirmed-snapshot-only consumer and must not read the draft.
7. Existing `Confirm Matrix` remains the only authority-promotion action. After reconfirmation, existing Fee and TASK_360B consumers read the resulting active confirmed snapshot as before.

## May Touch

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/features/matrix-editor/MatrixContactMeasurementPlanCard.tsx` and its focused test only if needed to present the compact draft-required affordance
- `frontend/src/workbench.css` only for scoped inline action/status styling
- TASK_360C task, plan, Planner evidence, and board through normal lane flow

## Must Not Touch / Locked Paths

- `backend/**`, database/schema/repository/domain/API route changes, and `frontend/src/api/client.ts`: the existing revision endpoint and typed helper are sufficient.
- Confirmed Matrix snapshot construction, Fee/default-fill behavior, TASK_360B projection/preview/generation/artifact behavior, generic top `Test record`, Matrix parser/import, StepInstance/execution, Report, Basic Information, LTR/public-drive, and real files/folders.
- External Fee residuals: `backend/modules/fee_evaluation/fee_default_fill.py`, `backend/modules/fee_evaluation/seeds/fee_rules_v2026_06_03.json`, and their visible focused tests.
- `.agents/**`, `docs/project_management/**`, release/packaging paths, and remote push.

## Acceptance Criteria

1. A confirmed Matrix with no current revision draft shows a clear inline `Open editable Matrix draft` action and explains that Contact Measurement Plan needs a draft for changes.
2. The action is lifecycle-readonly safe, prevents duplicate requests, and handles an existing-draft conflict by reloading the current session rather than overwriting anything.
3. After the draft opens, the existing step-quantity load returns eligible LLCR/CR Group-Step targets; Contact Measurement Plan can apply to blank targets and save.
4. Existing confirmed contact data is carried into the revision draft where it exists; no draft action changes active confirmed revision, Fee output, generic Test Record, or specialized workbook state.
5. `Confirm Matrix` remains the only promotion step. Reconfirmation makes the saved plan available to existing TASK_360B preview/generate through confirmed snapshot authority.
6. The existing workbook preview remains blocked before confirmed included targets exist and creates no file in that blocked state.

## Validation Gate

- Focused frontend tests for no-draft authority view, explicit create/reload, existing-draft recovery, lifecycle readonly block, duplicate-request protection, contact target coverage, apply/save after draft creation, and no direct confirmed mutation.
- Existing Matrix revision API/carry-forward tests, TASK_360A Fee passive-consumption regression, generic Test Record regression, and TASK_360B preview/generate regression.
- `npm test -- MatrixEditorWorkspace MatrixContactMeasurementPlanCard --run`; `npm run build`; `git diff --check`; trailing-whitespace and forbidden-scope scans.
- Authorized real UI smoke: confirm Matrix, return to Workbench, reopen Matrix Editor, open editable draft, set HP `4` / LP `5` / Signal `24`, verify `33`, apply blank targets, save quantities, reconfirm, then use TASK_360B preview/generate against the confirmed result. Use only the managed artifact directory or controlled local test data, never public-drive/LTR files.

## Merge Gate

Authorization history: Reviewer plan gate passed; user approved Developer planning-first; Developer planning-first completed as docs-only; Reviewer implementation-readiness passed; user approved reconciliation plus Developer implementation; Developer implementation completed; Reviewer B1 re-gate passed; QA gate passed; Integrator package isolation accepted.

## Definition of Ready

Definition of Ready, implementation readiness, Reviewer gate, QA gate, and Integrator package isolation are satisfied. TASK_360C is complete / accepted.

## Integrator Closeout

- Integrator gate: accepted.
- Package includes the inline editable Matrix draft bridge, focused Matrix Editor/contact-plan tests, scoped revision-draft bridge styling, TASK_360C task/plan/evidence, and TASK_360C board closeout.
- Package excludes external Fee residuals, unrelated `workbench.css` responsive/overflow hunks, TASK_360D/E files, `docs/superpowers/`, backend/API-client/schema changes, TASK_360B workbook implementation changes, generic Test Record, parser/import, StepInstance, Report, LTR/public-drive, real workbook/folder paths, `.agents/**`, and `docs/project_management/**`.
- Remote push intentionally not performed.

## Blocking Questions

None. The action uses existing revision semantics and does not introduce a new business decision.
