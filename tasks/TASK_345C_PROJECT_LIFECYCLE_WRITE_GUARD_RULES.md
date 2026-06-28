# TASK_345C Project Lifecycle Write Guard Rules

Status: approved - Developer implementation authorized after Reviewer readiness callback and user approval; implementation pending
Lane: project-lifecycle-write-guard-rules
Owner Role: Developer implementation / Reviewer / QA / Integrator
Evidence: docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_planner.md; docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_developer.md; docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_reconciliation_planner.md
Plan: docs/task_345c_project_lifecycle_write_guard_rules_plan.md
Last Updated: 2026-06-28

## 1. Purpose

Create the downstream planning-first lane after accepted `TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT` and accepted `TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API`.

TASK_345C plans the backend lifecycle write guard/read-only rule update for the new business model:

- stopped and closed projects are not permanent readonly archives;
- business writes remain blocked while stopped or closed;
- activation is the business action that allows work to continue;
- guard errors should point operators and downstream UI toward `Activate project`;
- non-mutating read/preview endpoints remain available when prior inventory classifies them as non-mutating.

This task is now implementation-authorized after Reviewer plan gate pass, Developer planning-first completion, Reviewer implementation-readiness content pass, and explicit user approval. Implementation remains pending and must stay inside the authorized backend write-guard scope below.

## 2. Source Facts

- TASK_345A accepted Activate as the primary direction for stopped/closed projects, including Completed-closed projects.
- TASK_345A rejected `Completed` as a special close path; all close reasons use one unified close form.
- TASK_345A keeps Temporary `Apply/Register LTR` as workflow entrypoint only and defers public-drive LTR workbook authority writing.
- TASK_345B is complete/accepted with backend/API/audit semantics for business close reasons, unified close, activate, close/activate event metadata, and `close_reason_category`.
- TASK_345B deliberately preserved TASK_345C boundary: write guard behavior/copy changes were not implemented.
- Existing `backend/application/project_lifecycle_write_guard.py` still returns legacy stopped `resume/close` allowed actions and closed readonly archive wording.
- Existing TASK_337B/TASK_338 inventory remains useful for write/read classification, but its old closed-permanent/archive language must be updated by this lane before downstream UI relies on it.
- TASK_345B QA was not required because its accepted package was backend/API/migration/audit behavior covered by focused backend tests. Frontend/UX smoke remains deferred to downstream TASK_345C+ UI-facing lanes after their contracts are approved.

## 3. Planned Guard Semantics

TASK_345C should plan and, after later approval, implement backend-only guard semantics unless Reviewer finds a frontend/API-client contract gap.

Expected semantics:

- Active projects: guarded business writes remain allowed by current rules.
- Stopped projects: guarded business writes remain blocked, but `allowed_actions` should include `activate`; legacy `resume` may remain only as internal compatibility if the approved implementation plan requires it.
- Closed projects: guarded business writes remain blocked, but `allowed_actions` should include `activate` when TASK_345B reports activation is recoverable.
- Closed Completed projects: same guard behavior as other business close reasons. Completed is a close reason, not a special permanent archive state.
- Guard messages must avoid user-facing `administrative`, `archive`, permanent readonly, or raw enum language as the product target.
- Lifecycle actions themselves are not generic business writes. `close` and `activate` must remain governed by lifecycle service/API rules, not blocked by the generic write guard.
- Read-only inspection and non-mutating preview endpoints remain available only when TASK_337B/TASK_338 classified them as non-mutating and the implementation confirms no record, file, workbook, output, cache, or authority mutation.

Downstream frontend can rely on backend conflict detail shape with:

- `code = project_lifecycle_readonly`;
- `lifecycle_state`;
- `message`;
- `allowed_actions`, using `activate` as the business action direction;
- close reason fields from TASK_345B lifecycle responses where available.

TASK_345C must not change `frontend/src/api/client.ts`; any frontend client/UI work belongs to later TASK_345D+ lanes.

## 4. May Touch

Planner/reconciliation passes may touch only:

- `tasks/TASK_345C_PROJECT_LIFECYCLE_WRITE_GUARD_RULES.md`
- `docs/task_345c_project_lifecycle_write_guard_rules_plan.md`
- `docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_planner.md`
- `docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_developer.md`
- `docs/lane_evidence/TASK_345C_project-lifecycle-write-guard-rules_reconciliation_planner.md`
- `docs/task_board.md`

Authorized Developer implementation scope after user approval:

- `backend/application/project_lifecycle_write_guard.py`
- `backend/api/lifecycle_errors.py`
- `tests/unit/test_project_lifecycle_write_guard.py`
- `tests/integration/test_project_basic_information_api.py`
- `tests/integration/test_matrix_editor_session_api.py`
- `tests/integration/test_fee_evaluation_pricing_draft_api.py`
- `tests/integration/test_project_folder_required_forms_api.py`
- `tests/integration/test_ltr_workbook_basic_information_sync_api.py`
- route files that already map guard errors only if needed for error shape adjustment:
  - `backend/api/routes_project_basic_information.py`
  - `backend/api/routes_matrix_editor_session.py`
  - `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`
  - `backend/api/routes_project_folder_required_forms.py`
  - `backend/api/routes_ltr_workbook_basic_information_sync.py`

Developer must not expand beyond this list without a separate Planner/Reviewer/user gate.

## 5. Must Not Touch

- No frontend UI, Workbench, Projects registry, CSS, routing, or copy implementation.
- No `frontend/src/api/client.ts` unless a separate approved lane authorizes it.
- No backend close/activate API redesign beyond guard response semantics.
- No public-drive LTR workbook authority write.
- No Temporary Apply/Register LTR implementation beyond references to future lane boundaries.
- No TASK_345D+ future lane implementation.
- No StepInstance, Report generation, execution persistence, AI, permissions, LAN/server, or multi-user scope.
- No unrelated governance/orchestration residual cleanup.

## 6. Locked Paths

Locked outside the authorized Developer implementation list:

- `backend/` except the explicitly authorized guard/error route files above
- `frontend/`
- `tests/` except the explicitly authorized backend tests above
- `frontend/src/api/client.ts`
- Projects registry implementation paths
- Workbench lifecycle UI implementation paths
- public-drive LTR authority and Office workbook write paths
- TASK_345D+ task/plan/evidence files
- `AGENTS.md`
- `.agents/`
- `docs/project_management/`

## 7. Validation Gate

Reviewer implementation gate should verify:

- Guard semantics align with TASK_345A/TASK_345B Activate/unified close model.
- Existing TASK_337B/TASK_338 write/read classification is reused without preserving obsolete permanent archive product meaning.
- Backend-only scope is credible and does not require frontend/API-client changes for this lane.
- May Touch / Must Not Touch / Locked Paths are complete.
- TASK_345B QA-not-required rationale and downstream UI smoke deferral are recorded.

Implementation validation should include:

- focused unit tests for active/stopped/closed guard decisions and allowed actions;
- representative API 409 tests for guarded writes;
- tests proving non-mutating preview/read endpoints remain available;
- tests proving lifecycle `activate` remains available for stopped/closed when TASK_345B allows it;
- forbidden-scope checks for no frontend/API-client/Projects registry/public-drive LTR authority/future-scope files.

## 8. Merge Gate

Developer implementation is authorized but not complete.

Merge remains blocked until:

- Developer evidence reaches ready_for_review after implementation;
- Reviewer implementation gate passes;
- QA is performed only if Reviewer/Integrator requires independent smoke;
- Integrator confirms package boundaries and validation.

## 9. Stop Point

Stop after Developer implementation evidence reaches `ready_for_review`. Do not implement frontend UI, `frontend/src/api/client.ts`, Projects registry, public-drive LTR authority writes, TASK_345D+ future lanes, StepInstance, Report, AI, permissions, LAN/server, or multi-user scope.
