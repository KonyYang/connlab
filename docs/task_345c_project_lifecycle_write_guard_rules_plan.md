# TASK_345C Project Lifecycle Write Guard Rules Plan

Status: implementation authorized - pending Developer implementation
Lane: project-lifecycle-write-guard-rules
Task: TASK_345C_PROJECT_LIFECYCLE_WRITE_GUARD_RULES
Evidence: docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_planner.md; docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_developer.md; docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_reconciliation_planner.md
Last Updated: 2026-06-28

## 1. Planner Objective

Create the formal planning-first lane for lifecycle write guard/read-only rule updates after TASK_345B acceptance.

This plan does not implement product code. Reviewer plan gate passed, Developer planning-first completed, Reviewer implementation-readiness content review found the plan sufficient, and the user explicitly approved Developer implementation. This plan is now the source-of-truth contract for the pending Developer implementation pass.

## 2. Discovery Gate

### User-Confirmed Facts

- TASK_345B is accepted by Integrator with local commit `f8f5d1ebe3719c65a36269995166ab142005d0f`.
- The next recommended lane is TASK_345C / `project-lifecycle-write-guard-rules`.
- The new business model keeps business writes blocked while stopped/closed, but stopped/closed are no longer permanent readonly archives.
- `Close project` is a business phase transition and can be followed by Activate.
- Unified close/activate backend/API semantics are provided by TASK_345B.
- Temporary Apply/Register LTR is a later entrypoint lane; public-drive LTR authority writing remains locked.

### Repository-Proven Facts

- `docs/task_board.md` records TASK_345A complete/accepted and TASK_345B complete/accepted.
- TASK_345A defines Activate as primary direction for stopped/closed, treats Completed as one close reason, requires audit history, and defers public-drive LTR authority writes.
- TASK_345B implemented backend/API/audit lifecycle activation model and explicitly deferred TASK_345C write guard behavior.
- Existing `backend/application/project_lifecycle_write_guard.py` still uses legacy guard messages:
  - stopped: `Resume it before making changes.` with allowed actions `resume`, `close`;
  - closed completed/admin: readonly archive-style messages with no allowed actions.
- Existing `backend/api/lifecycle_errors.py` maps guard errors to structured `409` details with `code`, `lifecycle_state`, `closure_type`, `message`, and `allowed_actions`.
- TASK_337B/TASK_338 inventory documents which operations are writes and which preview/read endpoints should remain available if non-mutating.
- TASK_345B acceptance evidence records QA not required because backend/API/migration/audit behavior was covered by focused backend regression, and frontend/UX smoke belongs to downstream TASK_345C+ lanes.

### Planner Inference

TASK_345C can be handled as a backend-only guard semantics lane if it updates the backend guard helper/error details and focused backend tests while preserving existing API detail shape. Downstream frontend UI can rely on `allowed_actions` containing `activate` and business-readable messages, but UI copy/routing changes belong to later TASK_345D+ lanes.

### Definition Of Ready

Ready for Reviewer plan gate:

- Upstream TASK_345A and TASK_345B are accepted.
- The target guard gap is visible in current code.
- May Touch / Must Not Touch / Locked Paths are defined.
- Validation and merge gates are defined.
- No blocking clarification is required for plan review.

Ready for Developer implementation after reconciliation:

- Reviewer plan gate passed per current Orchestrator/User delegation.
- Developer planning-first completed and updated only TASK_345C plan/evidence.
- Reviewer implementation-readiness content review found the plan sufficient but blocked on source-of-truth alignment.
- User explicitly approved later Developer implementation.
- This reconciliation aligns board/task/plan/evidence without marking implementation complete.

## 3. Scope

TASK_345C plans backend lifecycle write guard/read-only rules for the new business model.

Primary question:

How should backend guard errors behave when stopped/closed projects reject business writes after TASK_345B introduced `activate`?

Approved target direction for the plan:

- Active project writes continue as today.
- Stopped/closed business writes remain blocked until activation.
- Guard allowed actions point to `activate`, not permanent archive or Reopen-only language.
- Completed-closed is not special; it follows the same closed write-blocking and activation direction as other close reasons.
- Lifecycle `close` and `activate` actions are not blocked by generic business write guard logic.
- Non-mutating preview/read endpoints stay available if the implementation verifies they are truly non-mutating.

## 4. Candidate Implementation Shape For Later Approval

This section is planning guidance only.

Likely files:

- `backend/application/project_lifecycle_write_guard.py`
- `backend/api/lifecycle_errors.py`
- selected backend route/service tests that already exercise guard error details
- `tests/unit/test_project_lifecycle_write_guard.py`
- representative integration tests for guarded writes and readonly previews

Likely changes:

- update stopped guard allowed actions from `resume`/`close` to `activate` as the product-facing action direction;
- update closed guard allowed actions from empty to `activate` where activation is allowed by TASK_345B semantics;
- replace permanent readonly/archive/admin wording with business-readable Activate guidance;
- preserve stable error code `project_lifecycle_readonly`;
- decide whether to include legacy fields like `closure_type` for compatibility while adding `close_reason_category` only if already available without expanding API contract;
- update tests to lock business model wording and allowed actions;
- keep non-mutating previews/read endpoints available.

Backend-only assessment:

TASK_345C should be backend-only because TASK_345B already created the lifecycle response semantics and existing guard errors already return structured API detail. Frontend UI can rely on backend `409` detail and later TASK_345D+ lanes can update UI actions/copy without requiring `frontend/src/api/client.ts` changes in TASK_345C. If Reviewer finds an API-client gap, TASK_345C must remain blocked or split a separate client contract lane.

## 5. Downstream Frontend Reliance

Later frontend lanes may rely on these backend semantics after TASK_345C implementation is accepted:

- business writes rejected by lifecycle guard use `code = project_lifecycle_readonly`;
- stopped/closed guard details identify `activate` as the recovery action when available;
- guard messages do not expose `administrative`, permanent archive semantics, or raw enum labels as business copy;
- read-only/previews remain available only where non-mutating classification is preserved;
- lifecycle action endpoints remain the authority for `close` and `activate`.

No frontend UI implementation is part of TASK_345C.

## 6. May Touch

Planner lane creation may touch:

- `tasks/TASK_345C_PROJECT_LIFECYCLE_WRITE_GUARD_RULES.md`
- `docs/task_345c_project_lifecycle_write_guard_rules_plan.md`
- `docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_planner.md`
- `docs/task_board.md`

Developer implementation is authorized after Reviewer readiness callback and user approval, and is limited to the reviewed backend guard files and focused backend tests listed in section 11.4.

## 7. Must Not Touch

- Frontend UI, Workbench, Projects registry, CSS, routing, and copy implementation.
- `frontend/src/api/client.ts` unless a separate approved lane authorizes it.
- Backend lifecycle model/API redesign beyond write guard response semantics.
- Public-drive LTR workbook authority writing.
- Temporary Apply/Register LTR workflow implementation.
- TASK_345D+ future lane files or implementation.
- StepInstance, Report generation, execution persistence, AI, permissions, LAN/server, multi-user.
- Unrelated governance/orchestration residuals.

## 8. Locked Paths

Locked outside the authorized Developer implementation list:

- `backend/` except the explicitly authorized guard/error route files in section 11.4
- `frontend/`
- `tests/` except the explicitly authorized backend tests in section 11.4
- `frontend/src/api/client.ts`
- Projects registry implementation paths
- Workbench UI implementation paths
- public-drive LTR authority/Office workbook write paths
- TASK_345D+ files
- `AGENTS.md`
- `.agents/`
- `docs/project_management/`

## 9. Validation Gate

Planner/reconciliation validation:

- `git diff --check` on touched planning files.
- trailing-whitespace scan on touched planning files.
- targeted `git status --short` proving no backend/frontend/tests product files changed.

Reviewer implementation gate:

- Check that this lane updates guard semantics without reviving old permanent archive meaning.
- Check that backend-only scope is sufficient.
- Check that future validation protects writes and preserves non-mutating previews.
- Check that frontend/API-client/Projects registry/public-drive/future scopes remain locked.

Implementation validation:

- `py -m pytest tests/unit/test_project_lifecycle_write_guard.py -q`
- focused lifecycle gating API tests for representative business writes;
- focused preview/read availability tests for non-mutating endpoints;
- lifecycle API regression proving `activate` remains available for stopped/closed where TASK_345B supports it;
- forbidden-scope checks for frontend/API-client/Projects registry/public-drive LTR authority/TASK_345D+ files.

## 10. Merge Gate

No merge is authorized now. Developer implementation is authorized but not complete.

Future merge requires:

- Developer implementation evidence `ready_for_review`;
- Reviewer implementation gate pass;
- QA only if requested by Reviewer or Integrator;
- Integrator package validation and board closeout.

## 11. Developer Planning-First Refinement

Developer planning-first re-read the TASK_345A/TASK_345B contract, TASK_337B/TASK_338 write guard inventory, and current write guard code. This section refines the future implementation scope; it still does not authorize product code changes.

Repository status note: the original Developer planning-first pass recorded that `docs/task_board.md` lagged behind the Orchestrator delegation and still showed TASK_345C as planned for Reviewer plan gate. The Planner reconciliation checkpoint in section 13 supersedes that lag note by aligning the board/task/plan/evidence to implementation authorized after user approval. Product code is still unchanged at reconciliation time.

### 11.1 Guard Behavior Matrix

| Project state | Business writes | Non-mutating reads/previews | Lifecycle transitions | Guard recovery direction |
|---|---|---|---|---|
| Active formal/registered | Allow by existing business rules. | Allow. | `stop` and unified `close` remain governed by lifecycle service/API rules, not generic write guard. | None. |
| Active temporary/no-LTR | Allow only for existing temporary-safe/local writes already allowed by business services. Public-drive LTR workbook authority write remains locked to a later lane. | Allow. | `stop` and unified `close` remain lifecycle transitions. Temporary Apply/Register LTR authority write is not implemented by this lane. | None. |
| Stopped | Block selected project/business/authority/file/Office/external writes until activation. | Allow only where TASK_337B/TASK_338 classify the endpoint as truly non-mutating. | `activate`, compatibility `resume`, and unified `close` must not be blocked by generic write guard. | Product-facing `activate`. |
| Closed with reason Completed | Block selected writes until activation. Completed is one business close reason, not a permanent archive class. | Allow only where non-mutating. | `activate` must not be blocked by generic write guard when TASK_345B lifecycle service allows it. | Product-facing `activate`. |
| Closed with other business reason | Block selected writes until activation. Do not expose `administrative` as business copy. | Allow only where non-mutating. | `activate` must not be blocked by generic write guard when TASK_345B lifecycle service allows it. | Product-facing `activate`. |
| Legacy closed without recoverable prior status | Guard may still point to activation as the business recovery direction, but activation service/API owns the final conflict if it cannot safely restore status. | Allow only where non-mutating. | Generic write guard must not invent prior status. | Product-facing `activate`; activation endpoint may return conflict. |

### 11.2 Operation Classification

TASK_345C applies to the write guard first slice already implemented by TASK_338:

- `BASIC_INFORMATION_DRAFT`
- `BASIC_INFORMATION_CONFIRM`
- `MATRIX_EDITOR_DRAFT_SAVE`
- `MATRIX_EDITOR_DRAFT_DISCARD`
- `MATRIX_EDITOR_CONFIRM`
- `FEE_PRICING_DRAFT_SAVE`
- `FEE_PRICING_DRAFT_DISCARD`
- `REQUIRED_FORMS_GENERATE`
- `LTR_WORKBOOK_BASIC_INFORMATION_SYNC_COMMIT`

These are business/authority/file/Office/external writes for guard purposes, so stopped/closed states must return lifecycle readonly conflicts until activation.

TASK_345C must not guard or rewrite lifecycle transition operations themselves:

- `stop`
- unified `close`
- `activate`
- compatibility `resume`
- compatibility `close-completed`
- compatibility `close-administrative`

Read-only registry, project detail, lifecycle detail, output status summary, Basic Information reads, Matrix reads, Fee reads/previews, folder/status checks, and other previews remain available only when the endpoint does not mutate records, files, workbooks, caches, output rows, authority data, or public-drive state.

### 11.3 Error And Recovery Contract

The implementation should preserve the stable error code:

```text
project_lifecycle_readonly
```

Future guard 409 details should include:

- `code`
- `project_id`
- `lifecycle_state`
- `message`
- `allowed_actions`
- compatibility `closure_type` only if needed by existing tests/clients
- `close_reason_category` and `close_reason_label` only if they are available without expanding this lane into lifecycle API redesign

Product-facing behavior:

- stopped message should point to Activate, for example: `This project is stopped. Activate it before making changes.`
- closed message should point to Activate, for example: `This project is closed. Activate it before making changes.`
- `allowed_actions` for stopped/closed guard conflicts should use `["activate"]` as the product recovery direction.
- Do not expose `administrative`, `closed_administrative`, `archive`, permanent readonly, or raw enum wording in guard messages.
- Keep guard not-found mapping as API `404`.

Compatibility note: TASK_345B lifecycle responses may still retain `resume` compatibility for stopped projects. TASK_345C guard errors should prefer `activate`; if compatibility is required, it should be internal or explicitly documented without making `resume` the product-facing recovery action.

### 11.4 Future Implementation File List

Allowed future implementation files, after Reviewer implementation-readiness and explicit implementation routing:

- `backend/application/project_lifecycle_write_guard.py`
- `backend/api/lifecycle_errors.py`
- `tests/unit/test_project_lifecycle_write_guard.py`
- `tests/integration/test_project_basic_information_api.py`
- `tests/integration/test_matrix_editor_session_api.py`
- `tests/integration/test_fee_evaluation_pricing_draft_api.py`
- `tests/integration/test_project_folder_required_forms_api.py`
- `tests/integration/test_ltr_workbook_basic_information_sync_api.py`

Route files that already map lifecycle guard errors may be touched only if the API error detail shape requires route-local adjustment:

- `backend/api/routes_project_basic_information.py`
- `backend/api/routes_matrix_editor_session.py`
- `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`
- `backend/api/routes_project_folder_required_forms.py`
- `backend/api/routes_ltr_workbook_basic_information_sync.py`

No frontend, frontend API client, Projects registry, Workbench UI, public-drive LTR authority write, TASK_345D+ lane, StepInstance, Report, AI, permissions, LAN/server, or multi-user file is part of this implementation list.

### 11.5 Focused Test Plan

Future implementation should update or add tests for:

- active project writes remain allowed;
- stopped write conflicts return `allowed_actions=["activate"]` and Activate-oriented message;
- closed Completed write conflicts return `allowed_actions=["activate"]` and no permanent archive wording;
- closed non-completed/legacy administrative write conflicts return `allowed_actions=["activate"]` and no `administrative` user-facing message;
- API error mapping includes stable `project_lifecycle_readonly` detail and preserves 404 mapping for missing projects;
- Basic Information, Matrix editor, Fee pricing draft, Required Forms, and LTR workbook Basic Information sync representative writes return the new guard recovery details for stopped/closed states;
- non-mutating reads/previews covered by TASK_338 remain available;
- lifecycle `activate` and unified `close` endpoints are not blocked by the generic write guard;
- forbidden-scope checks prove no frontend/API-client/Projects registry/public-drive authority/future-scope changes.

### 11.6 Risks And Follow-Ups

- Existing unit tests intentionally lock old stopped `resume/close` and closed readonly archive behavior; TASK_345C implementation must update those expectations.
- Integration tests may use fake `ProjectLifecycleReadonlyError` instances with old actions/messages; update only tests in the future May Touch list.
- `ProjectLifecycleReadonlyError` currently does not carry `close_reason_category`; adding it is optional and should happen only if it can be done without expanding API scope.
- TASK_345C should not change the lifecycle API's activate conflict behavior for legacy rows without recoverable previous status.
- Temporary Apply/Register LTR remains a later entrypoint/authority lane and must not be smuggled into write guard semantics.

## 12. Stop Point

Stop after Developer implementation evidence reaches `ready_for_review`. Recommended next role after reconciliation: Developer implementation pass.

Developer implementation stop point: stop after implementing the authorized backend write-guard scope, running validation, and updating Developer evidence to `ready_for_review`. Recommended next role after Developer implementation: Reviewer implementation gate.

## 13. Planner Reconciliation Checkpoint

This reconciliation aligns repository source-of-truth after the Reviewer implementation-readiness callback and explicit user approval.

Fact chain:

1. TASK_345C Reviewer plan gate passed.
2. User approved Developer planning-first.
3. Developer planning-first completed and updated only TASK_345C plan/evidence.
4. Reviewer implementation-readiness content review found the plan sufficient, but blocked because `docs/task_board.md` and `tasks/TASK_345C_PROJECT_LIFECYCLE_WRITE_GUARD_RULES.md` still said planned / ready for Reviewer plan gate only.
5. User explicitly approved later Developer implementation.

Result:

- TASK_345C is now implementation authorized, pending Developer implementation.
- This checkpoint does not mark implementation complete.
- This checkpoint does not change backend/frontend/tests/API client product code.
- Scope locks remain: backend write guard implementation only; no frontend UI, no `frontend/src/api/client.ts`, no Projects registry, no public-drive LTR authority write, no TASK_345D+ future lanes, no StepInstance, Report, AI, permissions, LAN/server, or multi-user scope.
