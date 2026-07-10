# TASK_360C Matrix Contact Plan Revision-Draft Enablement Plan

## Discovery Summary

This is a small post-acceptance corrective lane for the gap between active confirmed Matrix authority and the draft-only Contact Measurement Plan editor. It reuses the existing Matrix revision-draft primitive rather than changing authority, persistence, Fee, or workbook logic.

## Current Phase / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current task: `TASK_360C_MATRIX_CONTACT_PLAN_REVISION_DRAFT_ENABLEMENT`.
- Role: Integrator packaging/readiness.
- Why allowed: TASK_360A and TASK_360B are accepted; Developer implementation completed; Reviewer implementation re-gate passed; QA gate passed; Integrator package isolation is the next legal gate.

## Evidence Classification

### Confirmed By User

- The actual project smoke produced HP `4` + LP `5` + Signal `24` and displayed derived `33` readings per sample.
- In that post-confirm state, the Contact Measurement Plan had `0 targets`, disabled blank apply, draft-required save error, and correctly blocked specialized workbook preview with no generated artifact.
- The desired repair is the smallest safe draft bridge.

### Confirmed By Repository

- No revision draft means session seed contains an authority projection but no `editor_draft_id`.
- The frontend clears draft Step quantities without that id, so the plan has no eligible target rows.
- The revision endpoint, typed frontend helper, draft load path, and confirmed contact-plan carry-forward are already implemented and covered by existing Matrix revision flow.
- Current UI intentionally hides prior revision actions, leaving no operator entry to create the safe draft.

### Inferred By Planner

- One compact inline `Open editable Matrix draft` action in Matrix Editor is enough. It should not be a modal, second workflow panel, or automatic draft creation.
- The existing Contact Measurement Plan card should state its draft requirement and keep mutation controls disabled until the session has a current draft. Its existing confirmed-only workbook controls stay separate.

### Not Yet Confirmed

None material to this lane. Exact final action placement may follow existing Matrix Editor header/completion-dock spacing during implementation, but must remain one compact inline operational control.

## Implementation Contract

```text
Active confirmed Matrix, no revision draft
  -> Matrix Editor authority view
  -> operator selects Open editable Matrix draft
  -> existing POST /matrix-revisions creates a draft from active confirmed snapshot
  -> frontend reloads existing session seed and draft Step quantities
  -> Contact Measurement Plan finds eligible Group-Step targets
  -> apply blank-only plan and save draft quantities
  -> existing Confirm Matrix promotes the new snapshot
  -> Fee and TASK_360B consume only the newly confirmed snapshot
```

The action must never modify active confirmed authority itself. A `409` existing-draft result is recovery, not overwrite: reload the session and use the current draft. A lifecycle readonly view makes no request.

## Developer Planning-First Refinement

### Existing Primitive Reuse

Implementation must reuse the current typed primitive without a client, route, or schema change:

- `createMatrixRevisionDraft(projectId)` already calls `POST /api/projects/{project_id}/matrix-revisions`.
- The route returns `201` for a new revision draft and `409` when a revision draft already exists for the active confirmed Matrix lineage.
- `fetchMatrixEditorSession(projectId)` is the current session authority. Its existing load path applies `editor_draft`, updates `savedEditorDraftId`, then lets the existing `savedEditorDraftId` effect fetch draft Step quantities.
- `carry_forward_step_quantities()` already copies the confirmed Step `contact_plan` into the revision draft. The frontend must wait for the reloaded session and use those returned draft items; it must not reconstruct contact-plan data locally.

The create response is only a successful operation signal. The UI must not merge that response into Matrix editor state. It always reloads the session source of truth after creation or conflict recovery.

### Session And Conflict State Machine

| Session state | Inline action | Handler outcome | Contact-plan state |
|---|---|---|---|
| Active confirmed Matrix, no `editor_draft_id` | Show enabled `Open editable Matrix draft` | Call the existing helper once, then reload the session seed | Read-only explanation; target mutation and save remain unavailable |
| Create request pending | Disable the same action | Suppress a second request | Preserve authority view and existing contact-plan values |
| `201` create result | Hide action after reload exposes a draft | Reuse existing draft-load and Step-quantity fetch effects | Draft targets, including carried-forward contact plan, become available |
| `409` existing draft | Do not surface a duplicate-create failure | Reload the session once; if it now exposes a draft, show the same successful editable state | No overwrite, no second draft, no confirmed-authority change |
| Reload fails or still has no draft after `409` | Keep one concise error and allow retry | Do not guess a draft id or clear authority state | Remains draft-required and non-mutating |
| Lifecycle readonly | Disabled with existing lifecycle reason | Handler exits before any request | Existing readonly contact-plan behavior remains unchanged |

The implementation should extract the existing session-seed loading body into a local reusable callback only when that reduces duplicate state assignment. It must preserve the current project-id reload lifecycle and cancellation protection. No new global store, route state, or parallel session channel is authorized.

### UI Structure And Copy

- Put a single compact inline action immediately before the existing `MatrixContactMeasurementPlanCard` in the Matrix functional area, adjacent to the existing Project Schedule surface but not inside it and not as a new card.
- In the draftless confirmed authority state, show the short helper `Open an editable Matrix draft to update contact targets.` The action is the one primary command for that state.
- Once `savedEditorDraftId` is present, remove the create action rather than retaining a duplicate-draft command. Existing Contact Measurement Plan controls remain the editing surface.
- Keep the existing card's mutation controls disabled while draft quantities load, save, or the lifecycle is readonly. A card prop/copy change is allowed only if the current disabled state does not clearly convey the draft requirement.
- Use a short success/recovery message such as `Editable Matrix draft opened.` Do not expose HTTP status, route names, draft ids, or raw conflict text.
- Do not add a modal, confirmation dialog, second workflow panel, dashboard card, or automatic draft creation.

### Contact-Plan Authority Boundary

- Only the existing Confirm Matrix operation promotes revision draft quantities and `contact_plan` records to a new confirmed authority snapshot.
- Blank-only apply continues to leave explicit Group-Step overrides intact. No draft opening operation may apply a profile, change included/excluded targets, or save quantities by itself.
- TASK_360B preview/generate, Fee, and generic Test Record remain confirmed-snapshot consumers. They must not see revision-draft contact-plan changes before reconfirmation.

## Exact Future May Touch

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`: import/call existing typed helper, reuse the session-seed reload path, expose the draft action, and coordinate draft-required controls.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`: focused behavior coverage.
- `frontend/src/features/matrix-editor/MatrixContactMeasurementPlanCard.tsx` and its focused test only if required for disabled-state copy/props.
- `frontend/src/workbench.css` only for the scoped inline action/status treatment.
- TASK_360C governance docs/evidence/board.

## Must Not Touch / Locked Paths

- `backend/**`, `frontend/src/api/client.ts`, schema, Matrix revision API/service/repository/domain, and existing Matrix confirm behavior.
- Fee rules/default-fill, generic Test Record, TASK_360B specialized workbook files, Matrix parser/import, Basic Information, StepInstance/execution, Report, LTR/public-drive, real workbook/folder data, release/settings.
- `.agents/**`, `docs/project_management/**`, external Fee residuals, and remote push.

## UX Acceptance

- The Matrix stays visually primary. The new action is concise and inline, not modal-first and not a new card/dashboard.
- In authority-only state, the Contact Measurement Plan communicates that an editable Matrix draft is required for changing contact targets.
- Existing draft opens automatically and does not show duplicate-create controls.
- The action preserves existing lifecycle readonly message and never gives a misleading editable state.

## Validation And Merge Gates

- Frontend behavior tests for draftless confirmed state, one explicit action request, successful create plus session reload, and current-draft action absence.
- Focused conflict test: a `409` from `createMatrixRevisionDraft()` reloads the session; a reloaded `editor_draft_id` enters the editable state without an error, while a failed/missing reload leaves a concise retryable error and does not invent state.
- Readonly and in-flight tests: lifecycle readonly makes no create request; pending creation suppresses double-clicks; existing current draft never creates another request.
- Contact-plan regression: reloaded draft Step quantities expose carried-forward `contact_plan`, target coverage returns after the draft is available, blank-only apply and save remain draft-only, and explicit overrides remain unchanged.
- Backend regression only: existing matrix revision service/API tests continue to prove `409` duplicate protection and confirmed `contact_plan` carry-forward. This lane adds no backend test because it does not change backend code.
- Regression: TASK_360A contact-plan/Fee passive consumption, generic Test Record, and TASK_360B preview/generate remain confirmed-only.
- `npm test -- MatrixEditorWorkspace MatrixContactMeasurementPlanCard --run`, `npm run build`, diff/trailing/forbidden-scope scans.
- Real smoke: confirm -> Workbench -> Matrix Editor -> open draft -> targets -> set `4/5/24` -> apply/save -> reconfirm -> preview/generate. Generated output must remain app-managed, macro-free, and outside public-drive/LTR paths.
- Merge only after the normal Reviewer, QA, and Integrator gates and a self-contained frontend package. Completed: Reviewer re-gate passed, QA gate passed, and Integrator package isolation accepted.

## Definition Of Ready

Reviewer plan gate and implementation-readiness passed after docs-only Developer planning-first. The user approved reconciliation plus Developer implementation; Developer implementation completed; Reviewer re-gate passed; QA gate passed; Integrator package isolation accepted. TASK_360C is complete / accepted.

## Integrator Closeout

- Integrator gate: accepted.
- Accepted package: Matrix Editor inline editable-draft bridge, Contact Measurement Plan workbook-lock split, focused frontend tests, scoped revision-draft bridge CSS, TASK_360C task/plan/evidence, and TASK_360C board closeout.
- Excluded residuals: Fee seed/rule/test work, unrelated `workbench.css` responsive/overflow hunks, TASK_360D/E task files, `docs/superpowers/`, backend/API-client/schema changes, TASK_360B workbook implementation changes, generic Test Record, parser/import, StepInstance, Report, LTR/public-drive, real workbook/folder paths, `.agents/**`, and `docs/project_management/**`.
- Remote push intentionally not performed.

## Dependency Assessment

TASK_360C is serial after TASK_360A/360B acceptance but has no backend dependency work. It can proceed as a focused frontend corrective lane; no parallel child lane is needed.
