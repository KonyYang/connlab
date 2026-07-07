# TASK_353B Registered LTR Workbook Row Preview Plan

> Status: complete/accepted - Integrator packaging/readiness accepted
> Task: `TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW`
> Lane: `registered-ltr-workbook-row-preview`
> Created: 2026-07-07

## 1. Discovery Gate

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active task/lane: `TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW` is complete/accepted after controlled Developer, Reviewer, QA, and Integrator gates.

Current role: Planner reconciliation.

Why allowed: user/orchestrator requested a single legal Planner source-of-truth reconciliation after Reviewer plan gate pass, Developer planning-first completion, Reviewer implementation-readiness pass, and explicit user approval for reconciliation plus Developer implementation. This pass updates documentation only and does not implement product code.

## 1.1 Implementation Authorization Checkpoint

Repository source-of-truth is reconciled for Developer implementation:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed in `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_developer.md`.
- Reviewer implementation-readiness passed in `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_reviewer.md`.
- User approved reconciliation and Developer implementation.

Authorized implementation remains limited to the read-only registered LTR workbook row preview action/API, the copy separation between `LTR workbook row preview` and `Update LTR from Basic Information`, and the focused tests/evidence listed in this plan. This does not mark implementation complete.

## 2. User Goal Restatement

ConnLab needs a new read-only way to verify that a registered project's DL/LTR number exists in the public-drive LTR workbook and that the row information looks correct. The existing `LTR update preview` is not this feature because it previews a write-capable Basic Information to workbook sync and requires confirmed Basic Information. The new action should be enabled by registered LTR presence alone, show a field table like the Intake specified-LTR workbook authority preview, and provide no Commit/write path. The existing Basic Information sync/update feature should remain, but its copy should be clearer, for example `Update LTR from Basic Information`.

## 3. Evidence Read

Governance and board:

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`

UI/product context:

- `$impeccable` product context
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`

Task/evidence context:

- `docs/task_349a_specified_ltr_workbook_authority_preview_plan.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_planner.md`
- `docs/lane_evidence/TASK_353A_basic-information-confirmed-identity-authority_planner.md`
- `docs/task_board.md` accepted rows for TASK_349A and TASK_353A

Code and tests:

- `backend/application/specified_ltr_workbook_authority_preview_service.py`
- `backend/application/ltr_workbook_basic_information_sync_service.py`
- `backend/api/routes_ltr_workbook_basic_information_sync.py`
- `backend/api/routes_new_project_completion.py`
- `backend/api/dependencies.py`
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx`
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.test.tsx`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx`
- `frontend/src/features/project-basic-information/useProjectBasicInformationModel.ts`
- `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx`
- `frontend/src/api/client.ts`
- `tests/unit/test_specified_ltr_workbook_authority_preview_service.py`
- `tests/unit/test_ltr_workbook_basic_information_sync_service.py`
- `tests/integration/test_ltr_workbook_basic_information_sync_api.py`

## 4. Confirmed By User

- A read-only action should exist for registered projects: `LTR workbook preview` / `LTR row preview`.
- The read-only action is enabled by registered LTR/DL presence, not by Basic Information confirmed state.
- The read-only action should query the public-drive LTR workbook row and show a business-readable field table.
- It must not require Basic Information Confirm.
- It must not write, commit, or alter local/project/workbook data.
- The current Basic Information-to-LTR workbook update/sync should remain but should be named more explicitly, such as `Update LTR from Basic Information`.

## 5. Confirmed By Repository Evidence

- `SpecifiedLtrWorkbookAuthorityPreviewService` already performs read-only workbook row lookup by DL and maps workbook columns E:Q to the requested business fields.
- `LtrWorkbookBasicInformationSyncService` already resolves the latest registered local LTR, locates the exact DL row in the workbook, reads the row, and provides an open-readonly action.
- The Basic Information sync service currently requires a latest confirmed Basic Information snapshot for preview/commit and returns blocker `Confirm Basic Information before synchronizing LTR workbook.`
- `ProjectBasicInformationSummaryCard` currently exposes a button labeled `LTR update preview`, enables it only for confirmed Basic Information, calls `previewLtrWorkbookBasicInformationSync`, and can then show `Confirm update`.
- The current side panel has no separate registered-LTR-only read preview.
- The existing Intake specified-LTR preview modal/table can be reused as a visual/field-label reference without changing Intake semantics.

## 6. Inferred By Planner

- The cleanest backend path is a new read-only project-scoped application service and route that reuses row-label and exact-DL lookup concepts without coupling to confirmed Basic Information or commit DTOs.
- No database schema change is needed because the project already has registered LTR records and workbook row data is read live from the configured workbook.
- `frontend/src/api/client.ts` must be touched for a typed read-only preview helper unless the frontend calls an already existing API, which it does not.
- `ProjectBasicInformationSummaryCard` is the likely UI surface because it already owns the Workbench side Basic Information/LTR actions.
- If the Basic Information standalone page also needs the action, it should share the same component/helper rather than creating a second implementation.

## 7. Not Yet Confirmed

- Exact visual placement: inline panel under the side action versus modal/dialog. Safe default for planning: read-only side panel/table, with Reviewer free to require modal if the side column becomes cramped.
- Whether the read-only preview should also offer the existing Excel read-only open-at-cell action. Safe default: optional if it reuses the existing read-only opener and remains no-write; not required for V1 acceptance.
- Whether closed/stopped lifecycle readonly should hide or keep the read-only preview. Safe default: keep read-only preview available because it does not mutate project/workbook state.

These do not block a planned lane because they are bounded UI/review details and do not change data ownership or write behavior.

## 8. Proposed UX / API / Service Boundary

Backend API draft:

```text
GET /api/projects/{project_id}/ltr-workbook/registered-row-preview
```

Response draft:

```json
{
  "status": "found",
  "project_id": "P1",
  "ltr_number": "DL-2026-05-011",
  "message": "LTR workbook row found.",
  "workbook_path": "P:/LTR/LTR.xlsx",
  "sheet_name": "2026",
  "row_number": 42,
  "row_values": [
    { "field_name": "project_type", "label": "Project Type", "value": "NPD", "is_blank": false }
  ],
  "blockers": [],
  "warnings": []
}
```

Service behavior:

- Resolve latest registered LTR for the project.
- Parse the year/sheet from the registered DL and locate the exact row in the configured workbook.
- Read the row in a read-only workbook transaction.
- Return the same business field labels used by TASK_349A.
- Return readable `not_found` / `blocked` states.
- Do not create preview ack, backup, save, commit, or write transaction.

Frontend behavior:

- Show `LTR workbook row preview` as a separate read-only action.
- Show `Update LTR from Basic Information` for the existing write-capable sync action.
- Only the update action can show comparison against Basic Information and `Confirm update`.
- The row preview action shows a read-only workbook table and no Commit/Confirm update button.

## 9. May Touch

See `tasks/TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW.md`.

Key planned scope:

- New backend read-only preview service/API/client helper.
- Basic Information side-card UI/copy.
- Focused backend/frontend tests.

## 10. Must Not Touch / Locked Paths

See `tasks/TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW.md`.

Key locks:

- No LTR workbook write or commit in the new action.
- No schema/migration.
- No Intake specified LTR flow behavior changes.
- No Matrix/Fee/Folder Actions/Report/StepInstance/AI/permissions/LAN/server/multi-user.
- No real workbook/folder mutation and no unrelated dirty cleanup.

## 11. Validation Gate Draft

Backend:

- Project with registered LTR can read the row without confirmed Basic Information.
- Project without registered LTR is blocked/readable.
- Missing workbook row is readable `not_found`.
- New service does not call write transaction/commit/backup/save.
- Existing Basic Information sync preview/commit behavior still requires confirmed Basic Information.
- TASK_349A specified-LTR preview behavior remains unchanged.

Frontend:

- Registered-LTR row preview action is separate from Basic Information sync/update.
- Preview table has no Commit action.
- Existing update action is copy-clarified and still confirmed-Basic-Information gated.
- Error/blocked/not-found states are concise and visible.

Commands:

- `py -m pytest tests/unit/test_registered_ltr_workbook_row_preview_service.py tests/integration/test_registered_ltr_workbook_row_preview_api.py -q`
- `py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py tests/unit/test_specified_ltr_workbook_authority_preview_service.py -q`
- `npm test -- ProjectBasicInformationSummaryCard --run`
- `npm run build`
- `git diff --check`
- trailing whitespace scan
- forbidden-scope/status scan

## 12. Merge Gate Draft

- Reviewer plan gate required before Developer planning/implementation.
- Developer evidence required before implementation review.
- Reviewer must confirm no write path exists in the new row preview and the old update/commit flow remains separated.
- QA must smoke a registered project with unconfirmed Basic Information and verify row preview is available while update remains gated.
- Integrator must package only TASK_353B files and exclude current release/settings/template residuals.
- Remote push is not authorized.

## 13. Definition Of Ready

Definition of Ready for a planned lane is satisfied:

- The operator scenario is clear.
- Existing conflicting behavior is identified.
- Backend/UI boundaries are clear.
- May Touch / Must Not Touch / Locked Paths are concrete.
- Validation and merge gates are testable.
- Non-goals prevent LTR workbook write/schema/Intake/Fee/Matrix/Folder scope creep.

Reviewer plan gate passed. Developer planning-first completed. Reviewer implementation-readiness passed. User approved reconciliation and Developer implementation.

TASK_353B is complete/accepted locally. The accepted package is limited to the registered-LTR read-only workbook row preview service/API/client/UI wiring, focused tests, TASK_353B task/plan/evidence, and board closeout. External TASK_352/PDF, Settings/LTR/template, TASK_355/release/desktop/packaging, `workbench.css`, temp stash, `.agents/**`, and `docs/project_management/**` residuals remain excluded. Remote push is not authorized.

## 14. Developer Planning-First Refinement

Status after Developer planning-first and Planner reconciliation: `implementation authorized - pending Developer implementation`.

This refinement is docs-only. It confirms the future implementation should keep the read-only registered-row preview separate from the existing Basic Information sync/update flow.

### 14.1 Implementation Strategy

Backend:

- Add a thin project-scoped read-only application service, tentatively `RegisteredLtrWorkbookRowPreviewService`.
- Service input should be `project_id` only.
- Service resolves the latest local registered `LtrRecord` for the project through `LtrRecordRepository`.
- Service opens the configured LTR workbook through `open_read_only_transaction()` only.
- Service locates the exact DL/LTR row in the target year sheet using the same normalization and exact-match behavior already proven in `LtrWorkbookBasicInformationSyncService`.
- Service returns TASK_349A-style business row values: Project Type, Description P/N, Test Item, Test Type, Requested by, Location, Project Leader, Test Result, Failed item, Sample deposition, Sub-contract, Test Fee, Remarks (PO).
- Service must not require confirmed Basic Information and must not depend on `ConfirmedBasicInformationReader`.
- Service must not create preview ack, call write transaction, run short transaction, backup, save, commit, or mutate local project data.

Recommended reuse:

- Extract only safe row-label mapping / row-value formatting from `SpecifiedLtrWorkbookAuthorityPreviewService` if duplication would be meaningful. Do not change TASK_349A Intake preview semantics.
- Extract only safe exact-DL row lookup helper from `LtrWorkbookBasicInformationSyncService` if it avoids duplicating subtle matching/cache behavior. Do not weaken its confirmed Basic Information gate or commit path.
- If extraction creates too much same-file churn, implement the new service with narrow local helpers and add regression tests proving behavior matches the existing exact-DL lookup rules.

API:

- Add `GET /api/projects/{project_id}/ltr-workbook/registered-row-preview`.
- Response should be read-only and not include commit fields:
  - `status`: `found | not_found | blocked`
  - `project_id`
  - `ltr_number`
  - `message`
  - `workbook_path`
  - `sheet_name`
  - `row_number`
  - `row_values`
  - `blockers`
  - `warnings`
- Route should return a typed response and map workbook lock/read errors to business-readable `blocked` or HTTP conflict where consistent with existing workbook routes.
- Register the route in `backend/api/main.py` and dependency in `backend/api/dependencies.py`.

Frontend:

- Add a typed API client helper and DTO for the registered row preview.
- Update `ProjectBasicInformationSummaryCard` to render two clearly separated actions:
  - `LTR workbook row preview`: read-only, enabled by registered LTR availability, does not require Basic Information confirmed state, never renders `Confirm update`.
  - `Update LTR from Basic Information`: existing write-capable preview/commit flow, still gated by confirmed Basic Information.
- The read-only preview should render a compact table using the TASK_349A field labels. Prefer inline side-panel disclosure inside the existing Basic Information side card for V1 to avoid adding another modal unless Reviewer requests it.
- Disabled/no-LTR copy should be short, for example `Registered LTR required`.
- `not_found` should tell the operator the registered DL was not found in the configured workbook.
- Closed/stopped lifecycle states should not suppress read-only preview because the new action is non-mutating.

### 14.2 Exact Future May Touch

Backend:

- `backend/application/registered_ltr_workbook_row_preview_service.py`
- `backend/application/ltr_workbook_basic_information_sync_service.py` only for safe helper extraction or import reuse, with existing sync behavior preserved.
- `backend/application/specified_ltr_workbook_authority_preview_service.py` only for safe row-value helper extraction or import reuse, with TASK_349A behavior preserved.
- `backend/api/routes_ltr_workbook_registered_row_preview.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`

Frontend:

- `frontend/src/api/client.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx`
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.test.tsx`
- `frontend/src/features/project-basic-information/useProjectBasicInformationModel.ts` only if registered-LTR availability cannot be derived from existing Basic Information/Project context.
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx` only if the SummaryCard needs a typed registered-LTR prop.
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx` and `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts` only if Workbench-side wiring needs to pass registered-LTR state into the existing side surface.

Tests/docs:

- `tests/unit/test_registered_ltr_workbook_row_preview_service.py`
- `tests/integration/test_registered_ltr_workbook_row_preview_api.py`
- Existing regression tests for Basic Information sync and TASK_349A specified preview if helpers are extracted.
- `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_developer.md`

### 14.3 Locked Scope Confirmation

- No LTR workbook write, commit, backup, save, or authority writeback in the new preview.
- No weakening of existing Basic Information sync/update confirmed-state gate.
- No Intake specified-LTR workbook authority preview or local duplicate flow changes.
- No schema/migration.
- No Matrix parser/import, Fee calculation/export, Folder Actions/public folder workflow, Report, StepInstance, AI, permissions, LAN/server, or multi-user changes.
- No real workbook/folder mutation in tests.
- No release/settings/template residual cleanup, `.agents/**`, `docs/project_management/**`, or remote push.

### 14.4 Focused Test Plan

Backend unit tests:

- Registered LTR project returns `found` row values without confirmed Basic Information.
- Project with no registered LTR returns a readable blocked state.
- Exact DL row not found returns `not_found`.
- Duplicate exact DL rows are blocked.
- Preview uses read-only transaction only and never calls write transaction / run short transaction / commit / backup / save.

Backend integration/API tests:

- `GET /api/projects/{project_id}/ltr-workbook/registered-row-preview` returns typed row values for a fake service.
- Missing registered LTR maps to the planned readable response/status.
- Existing Basic Information sync preview still returns blocked when Basic Information is unconfirmed.
- Existing Basic Information sync commit still requires confirmed Basic Information and lifecycle write permission.
- TASK_349A specified-LTR authority preview tests still pass if row label helpers are shared.

Frontend tests:

- `ProjectBasicInformationSummaryCard` shows separate `LTR workbook row preview` and `Update LTR from Basic Information` actions.
- Read-only preview action can be enabled while Basic Information is not confirmed when registered LTR availability is true.
- Read-only preview renders workbook row fields and does not render `Confirm update`.
- Existing update action is disabled until Basic Information confirmed.
- Existing update action still previews/commits only through the Basic Information sync helper.
- `not_found` and blocked copy are visible and concise.

Validation commands:

- `py -m pytest tests/unit/test_registered_ltr_workbook_row_preview_service.py tests/integration/test_registered_ltr_workbook_row_preview_api.py -q`
- `py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py tests/unit/test_specified_ltr_workbook_authority_preview_service.py -q`
- `npm test -- ProjectBasicInformationSummaryCard --run`
- `npm run build`
- `git diff --check`
- trailing whitespace scan on touched files
- forbidden-scope/status scan

Browser smoke:

- Use a registered project with no confirmed Basic Information. Verify `LTR workbook row preview` is enabled and opens read-only row fields.
- Verify `Update LTR from Basic Information` remains disabled until Basic Information is confirmed.
- Verify the row preview has no Commit/Confirm update control.
