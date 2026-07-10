# TASK_360C Matrix Contact Plan Revision-Draft Enablement Reviewer Evidence

Status: reviewer_pass
Task: `TASK_360C_MATRIX_CONTACT_PLAN_REVISION_DRAFT_ENABLEMENT`
Lane: `matrix-contact-plan-revision-draft-enablement`
Date: 2026-07-11
Role: Reviewer

## Gate

Reviewer plan gate only. No product code was changed, Developer was not started, and implementation remains unauthorized.

Current phase: Phase 11, Project Workbench / Matrix / Approval Package controlled foundation.
Current active task: `TASK_360C_MATRIX_CONTACT_PLAN_REVISION_DRAFT_ENABLEMENT`.
Why allowed now: the board marks TASK_360C as the current planned corrective lane after accepted TASK_360A and TASK_360B, with Reviewer plan gate as the next legal action.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `PRODUCT.md`, `DESIGN.md`, and `$impeccable` product guidance already loaded for the Matrix UI surface
- `docs/02_ARCHITECTURE_RULES.md` and `docs/frontend_architecture_rules.md`
- TASK_360A/B accepted board/evidence context
- `tasks/TASK_360C_MATRIX_CONTACT_PLAN_REVISION_DRAFT_ENABLEMENT.md`
- `docs/task_360c_matrix_contact_plan_revision_draft_enablement_plan.md`
- `docs/lane_evidence/TASK_360C_matrix-contact-plan-revision-draft-enablement_planner.md`
- Current Matrix Editor session/Step quantity code, typed `createMatrixRevisionDraft()` client helper, Matrix revision route/service, confirmed contact-plan carry-forward, and focused revision-flow tests.

## Findings

No blocking findings.

The root cause is supported by current code rather than inferred from the smoke alone. `MatrixEditorSessionService.get_seed()` produces an authority projection with `editor_draft_id = null` and `draft_status = missing` when a confirmed Matrix has no current revision draft. `MatrixEditorWorkspace` then clears its `stepQuantityItems` whenever `savedEditorDraftId` is absent. Contact Measurement Plan derives targets from those draft-only items, so its observed zero-target and save-blocked state follows directly.

TASK_360C chooses the narrowest safe correction. It reuses the existing typed `createMatrixRevisionDraft(projectId)` helper and existing `POST /api/projects/{project_id}/matrix-revisions` service, then reloads the existing session seed and Step quantities. The revision service already rejects duplicate current-base drafts and `carry_forward_step_quantities()` copies confirmed `contact_plan` records into the draft. This is a frontend bridge, not a new authority, API, schema, or persistence feature.

The authority and consumer boundary is correct:

- Active confirmed Matrix remains immutable until the existing Confirm Matrix action reconfirms the revision draft.
- In a draftless confirmed view, one compact inline `Open editable Matrix draft` action is appropriate. It is not automatic, modal-first, or a second workflow surface.
- A lifecycle-readonly state disables the action and handler before a request.
- A `409` existing-draft outcome reloads the session rather than overwriting or creating a second draft.
- Existing blank-only contact-plan apply/save remains draft-only.
- TASK_360B preview/generate remains confirmed-snapshot-only and must not read the new draft; Fee and generic Test Record likewise remain downstream consumers of the next confirmed snapshot only.

The future May Touch list is sufficiently narrow: Matrix Editor workspace and focused tests, Contact Measurement Plan card/test only for a necessary draft-required affordance, scoped CSS, and lane documentation. The existing client helper is reused with no `frontend/src/api/client.ts` change. Backend, revision route/service/repository/domain/schema, confirmed Matrix construction, Fee/default-fill, TASK_360B files, generic Test Record, Matrix parser/import, StepInstance, Report, Basic Information, LTR/public-drive, real files, release/settings, `.agents/**`, and `docs/project_management/**` remain locked.

The UI acceptance follows ConnLab product guidance: Matrix stays primary, the action is compact and inline, blocked state has a business-readable reason, mutation controls remain unavailable without a draft, and no dashboard/card stack or long explanatory copy is introduced.

## Validation

- Reviewed `git status --short` and targeted board/docs diff. TASK_360C changes are task/plan/Planner evidence/board docs only; no TASK_360C product implementation file is present.
- Existing visible Fee rule/seed/test changes remain external residuals and are excluded.
- Read-only inspection confirmed the revision route returns `409` for an existing draft, session reload exposes `editor_draft_id`, and confirmed `contact_plan` is copied by the existing carry-forward helper.
- `git diff --check` for TASK_360C planning docs and board passed with only the existing `docs/task_board.md` LF/CRLF warning.
- Trailing-whitespace scan on TASK_360C task, plan, Planner evidence, and this Reviewer evidence returned no matches.

## Decision

`reviewer_pass`

Recommended next role/action: User approval / Developer planning-first. Do not route Developer implementation until user approval, Developer planning-first, Reviewer implementation-readiness, source-of-truth reconciliation, and later implementation authorization are complete.

Blocking summary: none.

---

# TASK_360C Reviewer Implementation-Readiness Gate

Status: reviewer_implementation_readiness_pass
Date: 2026-07-11
Role: Reviewer

## Gate

Reviewer implementation-readiness gate only. No product code was changed, no Developer implementation was started, and this decision does not authorize implementation.

## Findings

No blocking findings. Developer planning-first is docs-only and the future implementation strategy is concrete enough for a later authorized pass.

- The exact frontend control point is a draftless, active-confirmed Matrix Editor session. The action is explicit, inline, and absent once `savedEditorDraftId` is present.
- It reuses the existing typed `createMatrixRevisionDraft(projectId)` helper without API-client or backend contract changes. A `201` reloads the existing session source of truth; the current id-based quantity effect then loads the revision-draft items.
- A `409` is specified as recovery: reload once, accept the existing current draft only if that reload returns an `editor_draft_id`, otherwise show concise retryable feedback. No draft id is invented and no confirmed authority is changed.
- Lifecycle readonly and in-flight create both suppress the request. Contact-plan apply/save remains draft-only, blank-only behavior and manual overrides remain unchanged, and Confirm Matrix remains the only promotion action.
- Confirmed `contact_plan` carry-forward is already implemented. TASK_360B, Fee, and generic Test Record remain confirmed-snapshot consumers until reconfirmation.

Future May Touch is sufficiently narrow: Matrix Editor workspace/tests, optionally the existing Contact Measurement Plan card/test for a focused draft-required message, scoped CSS, and lane evidence/docs. `backend/**`, `frontend/src/api/client.ts`, revision flow implementation, confirmed authority, Fee, generic Test Record, TASK_360B, parser/import, StepInstance, Report, LTR/public-drive, real files, release/settings, `.agents/**`, and `docs/project_management/**` remain locked.

## Docs-Only And Source-Of-Truth Check

Developer planning-first changed only `docs/task_360c_matrix_contact_plan_revision_draft_enablement_plan.md` and its Developer evidence. No TASK_360C product-code file is present in current status. Visible Fee rule/seed/test changes remain external residuals and are excluded.

The task board still records TASK_360C as planned and pending Reviewer plan gate, rather than recording the completed plan and planning-first gates. This is source-of-truth lag, so it prevents direct implementation authorization even though readiness passes.

## Validation

- Re-read TASK_360C task, updated plan, Planner/Reviewer/Developer evidence, board state, worktree status, current Matrix Editor session/quantity behavior, existing typed revision client helper, revision route/service, and confirmed contact-plan carry-forward.
- Confirmed the planning-first pass is docs-only by targeted status/diff review.
- `git diff --check` for TASK_360C plan/Developer evidence passed with no output; trailing-whitespace scan was clean.

## Decision

`reviewer_implementation_readiness_pass`

Recommended next role/action: User approval plus Planner/Integrator source-of-truth reconciliation before any Developer implementation. Do not route implementation directly from this readiness pass.

Blocking summary: none for readiness. Board reconciliation is an authorization prerequisite, not an implementation defect.

---

# TASK_360C Reviewer Implementation Gate

Status: reviewer_implementation_blocked
Date: 2026-07-11
Role: Reviewer

## Gate

Reviewer implementation gate only. No product code was changed and QA was not routed.

## Findings

### B1 - Confirmed-snapshot specialized workbook actions are disabled with the draft editor

`MatrixEditorWorkspace` now passes `!savedEditorDraftId` as part of the single `disabled` prop for `MatrixContactMeasurementPlanCard` ([MatrixEditorWorkspace.tsx](D:/PythonProject/connlab/frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx:3809)). That prop disables not only the draft-only contact family, target, blank-apply, and save controls, but also `Preview specialized record`, `Generate workbook`, and `Download workbook` in the card.

This regresses accepted TASK_360B behavior. The specialized workbook model calls the existing project-level preview endpoint ([useLlcrCrSpecializedRecordWorkbookModel.ts](D:/PythonProject/connlab/frontend/src/features/matrix-editor/useLlcrCrSpecializedRecordWorkbookModel.ts:16)); its backend preview service reads the active **confirmed** Matrix snapshot ([confirmed_matrix_llcr_cr_record_preview_service.py](D:/PythonProject/connlab/backend/application/confirmed_matrix_llcr_cr_record_preview_service.py:31)). It is deliberately independent of an editor draft. A draftless confirmed Matrix with included confirmed targets must still be able to preview and generate its specialized record; only Contact Plan mutation must require a current draft.

Smallest fix: separate the draft-editor disabled state from the confirmed-workbook action disabled state. Keep profile/target inputs plus blank-only apply/save disabled when no `savedEditorDraftId`; leave workbook preview/generate/download available whenever lifecycle and the workbook model's own busy/fingerprint guards permit it. Add a workspace regression proving a draftless confirmed session can invoke workbook preview while `Save contact plan` remains disabled.

## Validation

- Re-ran `npm test -- MatrixEditorWorkspace MatrixContactMeasurementPlanCard --run`: 2 files / 46 tests passed.
- Re-ran matrix revision and Step-quantity regression tests: 20 passed.
- Re-ran `npm run build`: passed with the existing Vite chunk-size warning.
- `git diff --check` passed for the candidate files, trailing-whitespace scan was clean, and targeted diff/status review confirmed no TASK_360C backend, API-client, schema, or locked-scope change.
- Inspected the candidate's 201/409 session reload path. It correctly reuses the typed helper and reloads the session rather than merging a response into confirmed authority. B1 is the remaining blocking regression.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer fix pass for B1 only. Do not route QA until the confirmed-snapshot workbook actions are decoupled from the draft-only Contact Plan editor lock.

Blocking summary: B1 as above.

---

# TASK_360C Reviewer Implementation Re-Gate - B1

Status: reviewer_pass
Date: 2026-07-11
Role: Reviewer

## Finding Closure

B1 is closed. `MatrixContactMeasurementPlanCard` now separates its draft-editor `disabled` state from an optional `workbookDisabled` state that retains the previous default for every other caller. `MatrixEditorWorkspace` keeps profile, target, blank-only apply, and save controls disabled with no `savedEditorDraftId`, while passing `workbookDisabled={isLifecycleReadonly}` for TASK_360B's confirmed-snapshot actions.

The new focused Workspace regression proves the intended boundary: a draftless confirmed Matrix keeps `Save contact plan` disabled, but enables `Preview specialized record` and invokes the existing project-level confirmed-snapshot preview helper. Existing busy and preview-fingerprint checks continue to guard generate/download. No draft data is passed to the specialized workbook model.

## Scope

The B1 fix changes only the allowed Matrix Editor component, its focused test, and the existing Workspace/test/style/evidence candidate. There is no backend, API-client, schema, confirmation-flow, Fee, generic Test Record, TASK_360B service, parser/import, StepInstance, Report, LTR/public-drive, or governance-path change. The unrelated Fee and Matrix CSS responsive residuals remain excluded from the TASK_360C candidate package.

## Validation

- Re-ran `npm test -- MatrixEditorWorkspace MatrixContactMeasurementPlanCard --run`: 2 files / 47 tests passed.
- Re-ran matrix revision and Step-quantity regression suite: 20 passed.
- Re-ran `npm run build`: passed with the existing Vite chunk-size warning.
- Candidate `git diff --check`, trailing-whitespace, and forbidden-content scans passed. Existing Fee/test residuals are outside the candidate package.

## Decision

`reviewer_pass`

Recommended next role/action: QA gate. QA should perform the controlled fixture smoke because opening a revision draft writes state: confirm Matrix, reopen Matrix Editor, preview the confirmed specialized record before opening a draft, open the draft, save Contact Plan changes, reconfirm, then confirm TASK_360B preview/generate sees only the new confirmed snapshot.

Blocking summary: none.
