# TASK_349A Specified LTR Workbook Authority Preview Planner Evidence

> Task: `TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW`
> Lane: `specified-ltr-workbook-authority-preview`
> Role: Planner
> Status: ready_for_reviewer_plan_gate
> Created: 2026-07-04

---

## Planner Discovery Result

Decision: create a formal planned lane for TASK_349A.

Status: planned for Reviewer plan gate only.

Implementation authorization: not granted.

Recommended next role: ConnLab Reviewer plan gate.

---

## Current Phase / Task / Lane

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active task/lane: none after `TASK_348B_LOCAL_LTR_DUPLICATE_CANCEL_STATE_RECOVERY` Integrator acceptance.

Planner lane created:

```text
TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW
specified-ltr-workbook-authority-preview
```

---

## Sources Read

Governance:

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`

UI/architecture:

- `$impeccable` context
- `PRODUCT.md`
- `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`

Task context:

- `tasks/TASK_347A_NEW_PROJECT_APPLY_LTR_BUSY_LOCK_UX.md`
- `tasks/TASK_348A_LOCAL_LTR_DUPLICATE_OVERRIDE_CONFIRMATION.md`
- `tasks/TASK_348B_LOCAL_LTR_DUPLICATE_CANCEL_STATE_RECOVERY.md`
- `docs/task_board.md` closeout context for TASK_347A/TASK_348A/TASK_348B

Code:

- `frontend/src/features/new-project/useNewProjectCompletion.ts`
- `frontend/src/features/new-project/NewProjectCompletionDock.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/api/client.ts`
- `backend/api/routes_new_project_completion.py`
- `backend/application/new_project_completion_service.py`
- `backend/application/ltr_workbook_write_preview_service.py`
- `backend/application/ltr_workbook_basic_information_sync_service.py`
- `backend/api/routes_ltr.py`
- `backend/api/dependencies.py`
- `backend/infrastructure/office/excel_com_ltr_workbook_gateway.py`
- `backend/infrastructure/office/ltr_workbook_transaction_gateway.py`
- focused LTR workbook preview/sync tests

---

## Confirmed By User

- Public-drive LTR Excel is the first authority for specified DL availability.
- Apply LTR Number must first run a read-only workbook row lookup for the specified DL.
- ConnLab must not create/confirm local Project, register local LTR ownership, or write workbook before the preview.
- Found workbook rows must be shown to the operator regardless of blank/partial/complete row content.
- Not found must show `LTR workbook 中不存在该编号` and stop local creation.
- Local duplicate conflict remains second-layer after workbook confirmation.
- Existing workbook preview/read-only capabilities should be reused.

---

## Confirmed By Repository Evidence

- Current New Project Apply calls `completeNewProject` directly.
- Current backend completion confirms or loads a local Project before LTR authority commit.
- Current local duplicate protection runs after project confirmation/loading.
- Existing gateway/session code can open the LTR workbook read-only and locate/read workbook rows.
- Existing Workbench Basic Information LTR sync already maps current workbook row values to business labels and reads exact DL rows.
- Existing frontend Workbench preview panel gives a reusable UX pattern, but Workbench behavior itself is locked.

---

## Planner Inference

- TASK_349A should add a new Intake-level read-only preview service/API rather than reuse project-scoped Workbench routes directly.
- Backend completion should require a preview ack/token for full specified DL numbers to prevent frontend-only bypass.
- One lane is sufficient because backend preview API, frontend confirmation, and completion ack are one authority gate.
- Suffix-only specified input should remain out of scope unless Reviewer/User explicitly expands the policy.

---

## Not Yet Confirmed

- Stateless preview hash vs stored short-lived preview token.
- Parsed-year-sheet-only lookup vs global lookup with blockers for cross-sheet duplicates.
- Long-term suffix-only specified number policy.

These are reviewable implementation-design choices and do not block planned lane creation.

---

## Planning Risk

If this lane is skipped or treated as a quick fix:

- New Project may continue to create/confirm local projects before verifying public workbook authority.
- Public workbook not-found cases may still fall through to local duplicate checks or local creation.
- Local SQLite may incorrectly act as first authority for specified DL availability.
- Frontend-only confirmation could be bypassed without backend ack enforcement.

---

## Files Created / Updated

- `tasks/TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW.md`
- `docs/task_349a_specified_ltr_workbook_authority_preview_plan.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_planner.md`
- `docs/task_board.md`

---

## Lane State

Formal task file: created.

Plan file: created.

Board row: created.

Status: `planned`, ready for Reviewer plan gate only.

Not approved for Developer implementation.

---

## May Touch Draft

- `backend/application/*specified*ltr*preview*` or a new focused `specified_ltr_workbook_authority_preview_service.py`
- `backend/application/ltr_workbook_basic_information_sync_service.py` only for extracting/reusing read-only row label mapping if Reviewer accepts that boundary
- `backend/infrastructure/office/excel_com_ltr_workbook_gateway.py` only for narrow read-only helper support if needed
- `backend/infrastructure/office/ltr_workbook_transaction_gateway.py` only for read-only adapter support if needed
- `backend/api/routes_new_project_completion.py` or a new focused route module
- `backend/api/dependencies.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/new-project/**`
- `frontend/src/pages/IntakeInboxPage.tsx`
- focused backend/frontend tests
- TASK_349A task/plan/evidence/board docs through normal lane flow

---

## Must Not Touch / Locked Paths

- Database schema/migration unless Reviewer explicitly approves a demonstrated need
- Workbench Basic Information LTR update preview semantics and user flow
- Matrix Editor
- Fee Evaluation
- Folder Actions/public folder workflow
- Projects registry/list
- Real public-drive workbook mutation during tests
- Real local/public folders
- Unrelated Basic Information, Settings/LTR, release/packaging, desktop release, `temp_agents_stash.md`, or board residual cleanup
- `.agents/**`
- `docs/project_management/**`
- StepInstance, Report, AI, permissions, LAN/server, multi-user

---

## Validation Gate Draft

- Backend read-only preview found/not-found/blocked tests.
- Backend no-write proof for preview.
- Backend completion rejects full specified DL without preview ack before local project confirmation.
- Backend completion with ack still reaches TASK_348A local duplicate conflict when local duplicate exists.
- Frontend Apply full specified DL calls preview before completion.
- Frontend found preview displays workbook row values and metadata.
- Frontend not-found preview blocks completion and preserves Intake state.
- Frontend confirm sends completion ack.
- TASK_347A busy lock and TASK_348A/TASK_348B duplicate/cancel behavior remain intact.
- `npm run build`, focused tests, `git diff --check`, trailing whitespace, and forbidden-scope checks.

---

## Planner Validation

Executed after TASK_349A task/plan/evidence/board writes:

- `git diff --check -- docs/task_board.md tasks/TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW.md docs/task_349a_specified_ltr_workbook_authority_preview_plan.md docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_planner.md`: passed with existing LF/CRLF warning on `docs/task_board.md` only.
- `rg -n "[ \t]$" docs/task_board.md tasks/TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW.md docs/task_349a_specified_ltr_workbook_authority_preview_plan.md docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_planner.md`: no matches.
- Targeted `git status --short -- docs/task_board.md tasks/TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW.md docs/task_349a_specified_ltr_workbook_authority_preview_plan.md docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_planner.md frontend backend tests` confirms this Planner pass created/updated TASK_349A docs and `docs/task_board.md` only; existing backend/frontend/tests dirty residuals remain external to TASK_349A and were not modified by this Planner pass.
- External Basic Information, Settings/LTR helper, release/packaging, desktop release, `temp_agents_stash.md`, and unrelated board/product residuals remain excluded from TASK_349A.

Planner gate: ready_for_reviewer_plan_gate.
