# TASK_348A Local LTR Duplicate Override Confirmation Plan

Status: complete/accepted by Integrator

Last updated: 2026-07-02

Lane: `local-ltr-duplicate-override-confirmation`

---

## 1. Current Phase, Task, And Role

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

Current active task/lane: `TASK_348A_LOCAL_LTR_DUPLICATE_OVERRIDE_CONFIRMATION` / `local-ltr-duplicate-override-confirmation`.

Current role: ConnLab Integrator packaging/readiness closeout.

Why allowed: Orchestrator delegated Integrator packaging/readiness after Reviewer re-gate and QA gate passed. This closeout updates source-of-truth docs and packages only the accepted TASK_348A duplicate override files plus the exact Planner-reconciled adjacent New Project setup/defaulting files.

---

## 2. User Goal Restatement

The user wants ConnLab to support a rare but real business case: local SQLite may already contain a DL/LTR number for an old project, but the operator may need to use that number for the current project after confirming the old local association is no longer needed. ConnLab must not treat `project_no` display identity as hard authority, and must not silently overwrite, delete, or reuse old local records. Public-drive LTR Excel remains the business authority and cannot be bypassed by local override. The user expects a structured backend conflict, a frontend confirmation flow, explicit second action, and durable audit history.

---

## 3. Evidence Read

Governance and planning:

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`

UI and architecture context:

- `$impeccable` context via `node .agents/skills/impeccable/scripts/load-context.mjs`
- `PRODUCT.md`
- `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`

Code and test evidence:

- `backend/application/new_project_completion_service.py`
- `backend/application/ltr_service.py`
- `backend/application/ltr_local_commit_service.py`
- `backend/application/ltr_authority.py`
- `backend/application/ltr_workbook_write_commit_service.py`
- `backend/application/ltr_registration_preview_service.py`
- `backend/api/routes_new_project_completion.py`
- `backend/api/routes_ltr.py`
- `backend/api/routes_ltr_workbook.py`
- `backend/infrastructure/storage/models.py`
- `backend/infrastructure/storage/repositories/records.py`
- `backend/infrastructure/storage/database.py`
- `backend/domain/enums.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/new-project/useNewProjectCompletion.ts`
- `frontend/src/features/new-project/NewProjectCompletionDock.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `tests/integration/test_new_project_completion_api.py`
- `tests/unit/test_ltr_workbook_write_commit_service.py`
- `tests/unit/test_ltr_local_commit_service.py`

Related historical LTR evidence:

- `tasks/completed/2026/TASK_156_REAL_LTR_APPLICATION_SMOKE_AND_FAILURE_HANDLING.md`
- `tasks/completed/2026/TASK_157_LTR_WORKBOOK_SQLITE_RECONCILIATION_AND_AUDIT_CHECK.md`

---

## 4. Confirmed Facts

Confirmed by user:

- Public-drive LTR Excel plus local `ltr_records.ltr_number` are the core uniqueness authority inputs.
- `project_no` or local project identity display must not be the hard uniqueness authority.
- Local SQLite may contain an old record for a DL/LTR number that the user still needs to use for the current project.
- ConnLab must never silently overwrite, delete, or reuse old records.
- UI must display key conflict information and require explicit confirmation.
- Public workbook duplicates must not be silently bypassed by a local override.
- Old local history must be retained and auditable.

Confirmed by repository evidence:

- `ltr_records.ltr_number` currently has a global SQLite unique constraint.
- `LtrRecord` status values are `draft`, `registered`, and `cancelled`.
- New Project completion calls an LTR authority port and then returns only success or generic errors.
- Local duplicate during New Project completion can become an `IntegrityError` and currently maps to a generic `409` string.
- LTR preview already reports local and workbook conflicts as strings, but not as a structured duplicate-resolution contract.
- Workbook commit can reject exact duplicates for append paths and can replace existing rows for some specified-number paths.
- Frontend `ApiRequestError.detail` can carry structured objects, but New Project completion currently renders only plain error text.

Inferred by Planner:

- The safest implementation should preflight local duplicate records before any irreversible workbook write or local registration commit.
- A robust solution likely needs schema/migration work because keeping `ltr_number` globally unique conflicts with retaining superseded local history under the same LTR number.
- `ProjectCleanupAuditRecordModel` or a new dedicated LTR association audit table could carry the audit trail; a dedicated table is cleaner if schema work is already required.
- This work is too broad for Quick Fix and should not be merged into TASK_347A or older LTR workbook tasks.

Not yet confirmed:

- The exact operator identity source for audit can follow current local default conventions at implementation time; this does not block planning.
- Whether public workbook existing-row replacement should gain a new explicit workbook-row acknowledgement in the same lane. The planned contract keeps public workbook semantics authority-controlled and prevents local override from bypassing workbook blockers.

---

## 5. Current Code Boundary And Real Conflict Path

Current local duplicate path:

1. New Project frontend calls `completeNewProject(caseId, input)`.
2. `routes_new_project_completion.complete_new_project(...)` calls `NewProjectCompletionService.complete(...)`.
3. The completion service confirms or loads the project, promotes setup fields, then calls the LTR authority port.
4. The active workbook authority eventually calls local LTR registration.
5. `LtrRecordRepository.create(...)` flushes a row into `ltr_records`.
6. Because `ltr_records.ltr_number` is globally unique, a duplicate LTR number can raise `IntegrityError`.
7. New Project API currently maps that to a generic `409` string.
8. Frontend renders the string through `completionError`.

Risk in current path:

- A local duplicate can be discovered too late.
- The response lacks a structured conflict summary.
- The operator cannot choose an audited override path.
- The existing project is not surfaced as the default safe path.
- Tests cover generic rejection, not recoverable confirmation.

---

## 6. Lane Split Decision

Recommended as one formal planning-first lane: `TASK_348A_LOCAL_LTR_DUPLICATE_OVERRIDE_CONFIRMATION`.

Reason:

- The API conflict shape, local storage strategy, and frontend confirmation flow must agree before implementation.
- Splitting backend and frontend before the conflict contract is reviewed would make the UI guess at data fields and resolution semantics.
- The lane can still use internal implementation checkpoints:
  1. backend duplicate preview/error contract and audit model,
  2. migration/current-owner or supersession storage behavior,
  3. New Project UI confirmation flow,
  4. integration/QA.

Split fallback:

- If Reviewer considers migration risk too large, split into `TASK_348A_BACKEND_LOCAL_LTR_DUPLICATE_CONTRACT` and `TASK_348B_NEW_PROJECT_LTR_DUPLICATE_CONFIRMATION_UI`. Until then, keep this as one planned contract lane with Reviewer gate.

---

## 7. API Contract Draft

Conflict response:

HTTP status: `409`

Detail shape:

```json
{
  "code": "LOCAL_LTR_DUPLICATE",
  "message": "This LTR number already has a local ConnLab record.",
  "ltr_number": "DL-2026-05-011",
  "existing": {
    "ltr_id": "LTR-...",
    "project_id": "P-...",
    "display_project_id": "DL-2026-05-011",
    "project_name": "Coolpower HDF 3.40mm pin Qualification Testing",
    "product_name": "Coolpower HDF",
    "sample_description": "3.40mm pin samples",
    "test_item": "Qualification Testing",
    "requester": "Alice",
    "requested_by": "Alice",
    "registered_on": "2026-05-07",
    "created_on": "2026-05-07",
    "lifecycle_state": "active",
    "project_status": "ltr_registered",
    "has_local_folder": true,
    "has_matrix": true,
    "has_basic_information": true,
    "has_outputs": false
  },
  "current": {
    "case_id": "case-...",
    "project_id": "P-new",
    "project_name": "Current New Project",
    "requester": "Bob"
  },
  "resolution": {
    "token": "opaque-short-lived-token",
    "allowed_actions": ["open_existing", "cancel", "replace_local_association"],
    "requires_second_confirmation": true
  }
}
```

Confirmed continue request draft:

```json
{
  "ltr_mode": "specified",
  "specified_ltr_number": "DL-2026-05-011",
  "operator_confirmed": true,
  "duplicate_resolution": {
    "action": "replace_local_association",
    "token": "opaque-short-lived-token",
    "reason": "Operator confirmed old local association is no longer current."
  }
}
```

Contract rules:

- `LOCAL_LTR_DUPLICATE` is only for local SQLite duplicate association conflicts.
- Public workbook duplicate or existing-row blockers must use a distinct public authority error and cannot be cleared by `duplicate_resolution`.
- Confirmation token must bind at least `ltr_number`, existing `ltr_id`, existing `project_id`, current `case_id` or project id, and conflict fingerprint.
- Missing, stale, or mismatched token must fail without mutation.
- `open_existing` is a frontend route action, not a backend mutation.

---

## 8. Data Ownership And Schema Strategy Draft

Authority rule:

- Public-drive LTR Excel remains business authority.
- SQLite is a local structured record, audit surface, and current local association index.

Recommended storage strategy:

- Do not simply remove uniqueness from `ltr_records.ltr_number`.
- Introduce an explicit current-owner concept so one LTR can retain historical local records while only one record is current.
- Prefer adding fields such as:
  - `is_current_owner` boolean, default true for legacy registered rows.
  - `superseded_at` string timestamp.
  - `superseded_by_ltr_id` nullable string.
  - `superseded_reason` text.
  - optional `source_action` or `association_version`.
- Migrate away from the single-column unique constraint on `ltr_number` and replace it with a current-owner uniqueness rule.
- SQLite partial unique index is acceptable if tested:
  - unique current owner per `ltr_number` where `status = 'registered'` and `is_current_owner = 1`.
- If partial unique migration is too risky for the first implementation, Reviewer may require a smaller rebind strategy, but that fallback must still preserve audit history and must not physically delete the old row.

Audit strategy:

- Add a dedicated audit record or reuse an existing audit pattern only if it can clearly record:
  - operator,
  - timestamp,
  - reason,
  - LTR number,
  - old `ltr_id` and project id,
  - new `ltr_id` and project id,
  - previous local owner status,
  - source action `local_ltr_duplicate_override`.

---

## 9. UX Confirmation Flow Draft

Register: product. The UI should be restrained, dense, operational, and business-readable.

Flow:

1. User clicks `Apply LTR Number`.
2. If backend returns `LOCAL_LTR_DUPLICATE`, keep the current form state intact.
3. Show a compact conflict panel in the New Project completion area or a focused confirmation dialog if the existing page layout cannot hold the summary.
4. Show only key facts:
   - LTR number,
   - existing project display id/name,
   - existing requester/registered date/status if available,
   - lightweight trace signals,
   - risk note: continuing keeps old history and makes the current project the current local association.
5. Actions:
   - `Open existing project` as the default safe action.
   - `Cancel`.
   - `Continue with this LTR number` as a guarded secondary/destructive-risk action.
6. The continue action requires a second explicit confirmation, for example a confirm checkbox plus final button, or a two-step confirmation state.
7. On success, clear the conflict panel, store the usual LTR result banner, and route normally.
8. On stale token or changed conflict, show a short retry message and require re-running Apply LTR Number.

Copy constraints:

- Do not expose SQL, unique index, API names, or stack traces.
- Do not use long explanatory paragraphs.
- Do not use user-facing `override` as the primary label if safer business copy is possible; prefer `Continue with this LTR number`.
- Pair warning color with text.

---

## 10. May Touch

Planner current pass may touch only:

- `tasks/TASK_348A_LOCAL_LTR_DUPLICATE_OVERRIDE_CONFIRMATION.md`
- `docs/task_348a_local_ltr_duplicate_override_confirmation_plan.md`
- `docs/lane_evidence/TASK_348A_local-ltr-duplicate-override-confirmation_planner.md`
- `docs/task_board.md`

Future Developer May Touch, only after Reviewer and user approval:

- `backend/application/new_project_completion_service.py`
- `backend/application/ltr_service.py`
- `backend/application/ltr_local_commit_service.py`
- `backend/application/ltr_workbook_write_commit_service.py`
- `backend/application/ltr_registration_preview_service.py` only if conflict preview reuse is needed
- new backend application service for local LTR duplicate conflict/resolution if needed
- `backend/api/routes_new_project_completion.py`
- `backend/api/routes_ltr.py` only if shared direct LTR commit behavior is included by Reviewer
- `backend/api/routes_ltr_workbook.py` only for local duplicate contract mapping, not workbook authority rewrite
- `backend/api/dependencies.py`
- `backend/domain/enums.py`
- `backend/domain/models.py`
- `backend/domain/__init__.py`
- `backend/infrastructure/storage/models.py`
- `backend/infrastructure/storage/database.py`
- `backend/infrastructure/storage/repositories/records.py`
- new focused repository/audit files under `backend/infrastructure/storage/repositories/`
- `frontend/src/api/client.ts`
- `frontend/src/features/new-project/useNewProjectCompletion.ts`
- `frontend/src/features/new-project/NewProjectCompletionDock.tsx`
- `frontend/src/features/new-project/NewProjectApplicationEditor.tsx` only if conflict placement requires passing a typed summary
- `frontend/src/pages/IntakeInboxPage.tsx` only for route/open-existing orchestration
- `frontend/src/intake-inbox.css`
- focused backend tests under `tests/unit/` and `tests/integration/`
- focused frontend tests for New Project duplicate confirmation
- `tests/unit/test_frontend_shell_files.py` only for narrow static guard coverage
- TASK_348A evidence files through normal lane flow

---

## 11. Must Not Touch

- Real public-drive LTR Excel files.
- Real public-drive data or real operator workbooks.
- Public-drive authority row write policy beyond distinguishing local duplicate resolution from workbook blockers.
- Matrix Editor behavior.
- Workbench Folder Actions, Sync, Submit, Pull, public folder workflow, or local folder open behavior.
- Project Registry behavior except opening an existing project route from the conflict UI, if approved.
- StepInstance, Report, AI, permissions, LAN/server, multi-user.
- Broad frontend architecture refactors.
- Broad backend service refactors.
- Release/packaging residuals.
- Settings/LTR helper residual cleanup.
- `.agents/**`
- `docs/project_management/**`
- `temp_agents_stash.md`
- Remote push.

---

## 12. Locked Paths

- real LTR workbook files and public-drive folders
- real `D:\Test Project/**`
- real `D:\PublicProject/**`
- `frontend/src/features/project-workbench/**`
- `frontend/src/features/matrix-editor/**`
- `frontend/src/pages/ProjectListPage.tsx`, except route navigation may be discussed but not implemented unless Reviewer explicitly approves
- `backend/application/public_folder_workflow_service.py`
- `backend/application/public_folder_year_resolver.py`
- `backend/application/public_folder_path_resolver.py`
- `backend/infrastructure/files/public_folder_workflow_gateway.py`
- `backend/desktop/**`
- `dist_release/**`
- `packaging/**`
- `scripts/build_windows_*`
- `scripts/smoke_windows_*`
- `docs/packaging_notes.md`
- `pyproject.toml`
- `.agents/**`
- `docs/project_management/**`

---

## 13. Validation Gate Draft

Backend tests:

- Local duplicate returns `409` with structured `LOCAL_LTR_DUPLICATE` detail and existing record summary.
- No confirmation means no local LTR ownership change.
- Stale or mismatched confirmation token fails without mutation.
- Confirmed continue supersedes/retires old current local association and creates or marks the new current association.
- Old local history and audit are retained.
- Public workbook duplicate/blocker cannot be cleared by local duplicate confirmation.
- Existing same-case idempotent retry still returns the same project/LTR.
- Migration preserves existing registered LTR rows as current owners.
- Current-owner uniqueness rejects two current local owners for one LTR.

Frontend tests:

- New Project Apply LTR renders local duplicate conflict summary.
- `Open existing project`, `Cancel`, and confirmed continue paths behave as planned.
- Confirm continue requires a second explicit action.
- User input remains intact after local duplicate conflict.
- Generic workbook/public authority errors do not render the local override panel.

Integration/API tests:

- `complete-new-project` typed conflict response.
- confirm-resolution request success/failure.
- direct local commit route coverage if included by Reviewer.

Commands expected after implementation:

- focused `py -m pytest` backend unit/integration suite for LTR duplicate behavior.
- focused frontend tests for New Project duplicate confirmation.
- `npm run build`.
- `git diff --check`.
- forbidden-scope scans proving no real workbook/folder mutation paths and no locked feature areas changed.

---

## 14. Merge Gate Draft

Merge may proceed only after:

- Reviewer plan gate passes.
- User explicitly approves Developer implementation.
- Developer evidence records implementation and focused validation.
- Reviewer implementation gate passes with no blocking findings.
- QA gate passes because this is a cross-backend/frontend authority workflow.
- Integrator confirms package scope excludes real workbook/public-drive mutation and unrelated residuals.
- Board and evidence are updated without marking future lanes complete.

---

## 15. Blocking Clarification Questions

None for planned lane creation.

Planner defaults are safe and reviewable:

- Public workbook duplicate cannot be bypassed by local override.
- Local duplicate confirmation must be second-action and audited.
- Schema/migration strategy is proposed for Reviewer gate before implementation approval.

---

## 16. Definition Of Ready

Definition of Ready for a planned lane is satisfied:

- User scenario is clear.
- Repository evidence confirms the current conflict path.
- Dependencies are complete enough for Reviewer plan gate.
- May Touch, Must Not Touch, Locked Paths, Evidence, Validation Gate, and Merge Gate are concrete.
- Non-goals prevent scope creep.

Definition of Ready for approved implementation is now satisfied at source-of-truth level:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed and refined this plan.
- Reviewer implementation-readiness gate passed.
- User explicitly approved TASK_348A reconciliation and Developer implementation.
- `docs/task_board.md`, the TASK file, this plan, and reconciliation evidence record implementation authorization.

Implementation authorization reconciliation outcome: Developer implementation was authorized and has since completed. Current recommendation after B1 scope reconciliation is Reviewer implementation re-gate.

---

## 17. Developer Planning-First Refinement

### 17.1 Current Implementation Facts Rechecked

Developer re-read the New Project, local LTR, workbook authority, storage, API client, and frontend New Project code. The important implementation facts are:

- `backend/application/new_project_completion_service.py` coordinates intake confirmation, setup promotion, and an `LtrAuthorityPort` commit, but does not have local duplicate preflight or duplicate resolution payloads.
- `backend/api/routes_new_project_completion.py` catches SQLAlchemy `IntegrityError` and returns a generic `409` string. This is the concrete place where `LOCAL_LTR_DUPLICATE` must replace the current generic conflict for known local duplicate cases.
- `backend/application/ltr_service.py` creates one registered LTR per project and delegates LTR number uniqueness to repository/database constraints.
- `backend/application/ltr_local_commit_service.py` already has preview-first behavior but delegates the final insert to `LtrService.register_ltr`.
- `backend/application/ltr_workbook_write_commit_service.py` resolves workbook number decisions inside a locked transaction, then writes the workbook row, then registers the local LTR. TASK_348A implementation must detect local duplicate conflicts after a final number is known and before workbook row write when the number is resolved inside that transaction.
- `backend/infrastructure/storage/models.py` currently declares `LtrRecordModel.ltr_number` as `unique=True`, so retaining old local history for the same LTR number requires a migration away from the single-column unique constraint.
- `backend/infrastructure/storage/database.py` uses explicit SQLite compatibility migrations in `init_db`, including table rebuilds where constraints change.
- `frontend/src/api/client.ts` preserves structured API error `detail` objects and can add typed `LOCAL_LTR_DUPLICATE` guards without replacing the fetch boundary.
- `frontend/src/features/new-project/useNewProjectCompletion.ts` currently collapses all completion failures to a plain `completionError` string.
- `frontend/src/features/new-project/NewProjectCompletionDock.tsx` and `frontend/src/pages/IntakeInboxPage.tsx` are the correct surface for a compact conflict confirmation panel that preserves the current setup values.

### 17.2 Exact Future May Touch List

Future implementation May Touch after Reviewer and user authorization:

Backend contract and service:

- `backend/application/new_project_completion_service.py`
- `backend/application/ltr_service.py`
- `backend/application/ltr_local_commit_service.py`
- `backend/application/ltr_workbook_write_commit_service.py`
- `backend/application/ltr_registration_preview_service.py` only for read-only conflict summary reuse
- new `backend/application/ltr_duplicate_resolution_service.py`
- new `backend/application/ltr_duplicate_resolution_token_service.py` if token persistence is separated

Backend API and dependencies:

- `backend/api/routes_new_project_completion.py`
- `backend/api/routes_ltr.py` only if direct local LTR commit must share the same conflict contract
- `backend/api/routes_ltr_workbook.py` only for shared structured conflict mapping, not workbook authority rewrite
- `backend/api/dependencies.py`

Domain and storage:

- `backend/domain/enums.py`
- `backend/domain/models.py`
- `backend/domain/__init__.py`
- `backend/infrastructure/storage/models.py`
- `backend/infrastructure/storage/database.py`
- `backend/infrastructure/storage/repositories/records.py`
- `backend/infrastructure/storage/repositories/__init__.py`
- new `backend/infrastructure/storage/repositories/ltr_duplicate_resolution.py`
- new `backend/infrastructure/storage/repositories/ltr_association_event.py` if audit is not folded into one repository file

Frontend API client and New Project UI:

- `frontend/src/api/client.ts`
- `frontend/src/features/new-project/useNewProjectCompletion.ts`
- `frontend/src/features/new-project/NewProjectCompletionDock.tsx`
- new `frontend/src/features/new-project/LocalLtrDuplicateConflictPanel.tsx`
- `frontend/src/features/new-project/NewProjectApplicationEditor.tsx` only if the conflict panel must be placed above the dock
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/intake-inbox.css`

Tests:

- `tests/unit/test_ltr_duplicate_resolution_service.py`
- `tests/unit/test_ltr_local_commit_service.py`
- `tests/unit/test_ltr_workbook_write_commit_service.py`
- `tests/integration/test_new_project_completion_api.py`
- `tests/integration/test_ltr_duplicate_resolution_migration.py`
- `frontend/src/api/client.test.ts` or the existing API-client test file if present
- `frontend/src/features/new-project/useNewProjectCompletion.test.tsx` if hook tests are already used in the suite, otherwise component/page tests
- `frontend/src/features/new-project/NewProjectCompletionDock.test.tsx`
- `frontend/src/features/new-project/LocalLtrDuplicateConflictPanel.test.tsx`
- `frontend/src/pages/IntakeInboxPage.test.tsx` only if route/open-existing orchestration requires page-level coverage
- `tests/unit/test_frontend_shell_files.py` only for narrow static guard coverage

Documentation and evidence:

- `docs/task_348a_local_ltr_duplicate_override_confirmation_plan.md`
- `docs/lane_evidence/TASK_348A_local-ltr-duplicate-override-confirmation_developer.md`
- later Reviewer/QA/Integrator evidence through normal lane flow

### 17.3 Local Duplicate Flow

Unconfirmed flow:

1. Completion resolves or predicts the final LTR number without mutating local ownership.
2. The backend checks for a current local owner for the normalized LTR number that is not the same current project/case.
3. If found, the backend returns HTTP `409` with `detail.code = "LOCAL_LTR_DUPLICATE"`.
4. The response includes an existing local record/project summary, the current case/project summary, and a persisted duplicate-resolution token.
5. No local LTR owner changes, no old row retirement, and no audit event are written during this unconfirmed conflict path.

Safe defaults:

- `open_existing` is the preferred safe action and only routes to an existing project view.
- `cancel` closes the conflict panel and preserves the current setup values.
- `replace_local_association` is never the default and must require a second explicit action.

Confirmed continue:

1. The operator clicks `Continue with this LTR number`.
2. The UI reveals a second confirmation step, for example an acknowledgement checkbox plus a final `Confirm current local owner` button.
3. The second request includes `duplicate_resolution.action`, `token`, `acknowledged = true`, and an operator reason/note.
4. Backend validates that the token is unused, unexpired, and still matches `ltr_number`, existing `ltr_id`, existing project id, current case/project id, current owner fingerprint, and workbook decision fingerprint where available.
5. Backend retires only the old current local ownership flag and creates or marks the new LTR row as the current local owner.
6. Old local rows remain queryable as history. The implementation must not delete or overwrite the old local record.
7. An LTR association audit event records timestamp, operator, reason, old owner, new owner, token id or fingerprint, and source action `local_ltr_duplicate_override`.

Same-case idempotency:

- If the current case/project already owns the registered LTR and the retry is an idempotent completion retry, return success and do not show the duplicate panel.
- If the same LTR number exists on another project, always require the structured conflict unless a valid duplicate-resolution token is supplied.

### 17.4 Public Workbook Authority V1 Strategy

Public workbook authority must remain separate from local duplicate resolution.

V1 rules:

- `duplicate_resolution` only authorizes local SQLite current-owner replacement. It must not clear workbook blockers.
- If the workbook path would reject the number today, TASK_348A must keep returning the workbook authority error, not `LOCAL_LTR_DUPLICATE`.
- If the workbook commit decision is an existing supported same-row replacement, such as current `replace_existing` behavior for a specified base or full associated DL number, the local duplicate token may bind that workbook row pointer/fingerprint but does not introduce a new silent workbook override.
- If the workbook detects a different exact duplicate, missing base, missing sheet, locked workbook, unsupported append conflict, or stale row fingerprint, the request must fail before local owner replacement.
- Tests must prove that a local duplicate confirmation cannot bypass public workbook duplicate or row ownership blockers.

This keeps the first implementation narrow: local SQLite can change current owner only after the existing workbook authority path still permits the operation.

### 17.5 Schema And Migration Strategy

Recommended storage change:

- Replace the current global `ltr_records.ltr_number` uniqueness with one current-owner uniqueness rule.
- Add nullable/history columns to `ltr_records`:
  - `is_current_owner BOOLEAN NOT NULL DEFAULT 1`
  - `superseded_at VARCHAR(64)`
  - `superseded_by_ltr_id VARCHAR(64)`
  - `superseded_reason TEXT`
  - `owner_version INTEGER NOT NULL DEFAULT 1`
- Rebuild the `ltr_records` table in SQLite to remove the inline `unique=True` single-column constraint.
- Add a partial unique index:
  - `CREATE UNIQUE INDEX ux_ltr_records_current_owner_ltr_number ON ltr_records(ltr_number) WHERE status = 'registered' AND is_current_owner = 1`
- Add indexes on `project_id`, `ltr_number`, and `is_current_owner` if the rebuild drops useful implicit indexes.

Token persistence:

- Add `ltr_duplicate_resolution_tokens`:
  - `token_id`
  - `ltr_number`
  - `existing_ltr_id`
  - `existing_project_id`
  - `current_case_id`
  - `current_project_id`
  - `conflict_fingerprint`
  - `workbook_fingerprint`
  - `expires_at`
  - `used_at`
  - `created_at`
  - `created_by`
  - `metadata_json`

Audit persistence:

- Add `ltr_association_events`:
  - `event_id`
  - `ltr_number`
  - `event_type`
  - `old_ltr_id`
  - `old_project_id`
  - `new_ltr_id`
  - `new_project_id`
  - `operator`
  - `reason`
  - `token_id`
  - `created_at`
  - `metadata_json`

Migration compatibility:

- Existing registered rows are backfilled with `is_current_owner = 1` and `owner_version = 1`.
- Existing draft/cancelled rows may be backfilled with `is_current_owner = 0` unless the Reviewer requires legacy draft visibility as owner candidates.
- If a legacy database already has impossible duplicate registered LTR rows, migration must not guess a current owner silently. It should mark the newest by registered date only if a deterministic safe rule is approved, otherwise fail with a clear local cleanup blocker.
- Rollback risk is non-trivial because removing an inline SQLite unique constraint requires table rebuild. The implementation plan must include a migration test that starts from the old schema with `ltr_number` unique.

### 17.6 API Contract Refinement

Complete request additions:

```json
{
  "duplicate_resolution": {
    "action": "replace_local_association",
    "token": "opaque-token-id",
    "acknowledged": true,
    "reason": "Operator confirmed this project should be the current local owner."
  }
}
```

Conflict detail shape:

```json
{
  "code": "LOCAL_LTR_DUPLICATE",
  "message": "This LTR number already has a local ConnLab owner.",
  "ltr_number": "DL-2026-05-011",
  "existing": {
    "ltr_id": "old-ltr-id",
    "project_id": "old-project-id",
    "display_project_id": "DL-2026-05-011",
    "project_name": "Existing project",
    "product_name": "Connector",
    "sample_description": "3.40mm pin samples",
    "test_item": "Qualification Testing",
    "requester": "Alice",
    "registered_on": "2026-05-07",
    "project_status": "ltr_registered",
    "lifecycle_state": "active",
    "has_local_folder": true,
    "has_matrix": true,
    "has_outputs": false
  },
  "current": {
    "case_id": "case-id",
    "project_id": "new-project-id",
    "project_name": "Current project",
    "requester": "Bob"
  },
  "resolution": {
    "token": "opaque-token-id",
    "expires_at": "2026-07-02T12:00:00Z",
    "allowed_actions": [
      "open_existing",
      "cancel",
      "replace_local_association"
    ],
    "requires_second_confirmation": true
  }
}
```

Error code boundaries:

- `LOCAL_LTR_DUPLICATE`: local SQLite current owner conflict only.
- `LOCAL_LTR_DUPLICATE_TOKEN_STALE`: token missing, used, expired, or fingerprint mismatch.
- `PUBLIC_LTR_DUPLICATE`: public workbook duplicate or row blocker, not clearable by local duplicate confirmation.
- `LTR_AUTHORITY_BLOCKED`: workbook lock, missing sheet, invalid specified number, missing base, or unsupported authority state.

Frontend client:

- Add `LocalLtrDuplicateConflictDetail`, `CompleteNewProjectDuplicateResolutionInput`, and `isLocalLtrDuplicateConflictDetail`.
- Keep `ApiRequestError.detail` as the transport boundary.
- `useNewProjectCompletion` should expose `localDuplicateConflict`, `confirmDuplicateResolution`, and `clearLocalDuplicateConflict` rather than forcing the page to parse raw API errors.

### 17.7 UX Confirmation Refinement

The New Project UI should stay within the product register: restrained, dense, operational, and business-readable.

Recommended placement:

- Render a compact `LocalLtrDuplicateConflictPanel` in the New Project completion area, directly above or inside the completion dock.
- Keep the current form/session values intact.
- Do not navigate away unless the operator chooses `Open existing project`.

Panel content:

- Title: `LTR number already exists locally`
- Summary fields:
  - LTR number
  - Existing project display id/name
  - Existing requester
  - Registered date
  - Status
  - Trace signals such as local folder or Matrix only when backend supplies true values
- Short risk copy: `Continuing keeps the old history and makes this project the current local owner.`

Actions:

- Primary safe action: `Open existing project`
- Secondary action: `Cancel`
- Guarded action: `Continue with this LTR number`
- Final confirmation button after acknowledgement: `Confirm current local owner`

Anti-misclick:

- The guarded action must not be the only prominent blue button.
- Continue requires a second explicit acknowledgement.
- The confirmation request must disable while in flight and must preserve the same busy-lock behavior introduced by TASK_347A.

Copy constraints:

- Do not show SQL, unique indexes, API paths, stack traces, or raw backend enum tokens.
- Do not use `override` as the primary operator-facing verb.
- Do not use long paragraphs or fake workbook progress.

### 17.8 Test Plan Refinement

Backend unit tests:

- Duplicate service builds `LOCAL_LTR_DUPLICATE` detail with existing/current summaries.
- Token service creates token rows, validates fingerprints, rejects stale/used/mismatched tokens, and marks tokens used on success.
- Repository supports one current owner per LTR number and retains superseded rows.
- Audit event records old owner, new owner, operator, reason, and token id.
- Workbook commit resolves final number and checks local duplicate before workbook row write when final number is known inside the transaction.
- Local commit rejects duplicate without token and succeeds with valid duplicate resolution.

Backend integration/API tests:

- `complete-new-project` returns structured `409` with `LOCAL_LTR_DUPLICATE` and no local owner change.
- Confirmed continue retires old current owner, creates or marks new current owner, and persists audit.
- Same-case retry remains idempotent and does not create duplicate audit.
- Public workbook duplicate/blocker still fails even with local duplicate token.
- Migration from old unique `ltr_records` schema backfills current-owner fields and creates the partial unique index.
- Migration test covers old schema without the new token/audit tables.

Frontend/API-client tests:

- `isLocalLtrDuplicateConflictDetail` accepts only the structured conflict shape.
- `completeNewProject` accepts `duplicate_resolution` payload.
- Hook exposes duplicate state when `ApiRequestError.detail.code` is `LOCAL_LTR_DUPLICATE`.
- Hook leaves generic workbook errors as ordinary completion errors.
- Hook preserves setup values across conflict, cancel, stale-token retry, and success.

Frontend UI tests:

- Conflict panel shows existing/current summary fields.
- `Open existing project` routes to the existing project without committing the current project.
- `Cancel` clears the panel.
- `Continue with this LTR number` requires the second acknowledgement before final submit.
- Confirm submit sends token/action/reason and disables controls while pending.
- Success clears conflict and follows the normal completion handoff.

Static/forbidden-scope tests:

- No real public workbook files are opened in tests.
- No Matrix Editor, Workbench Folder Actions, Project Registry behavior, release packaging, Settings/LTR residual cleanup, or future scope files are changed by implementation.

### 17.9 Implementation Checkpoints For Later Pass

Recommended implementation order after approval:

1. Add migration tests for old `ltr_records` schema and token/audit tables.
2. Implement storage/domain/repositories for current-owner rows, tokens, and audit events.
3. Implement duplicate resolution service and token validation.
4. Integrate preflight into New Project completion and workbook/local commit paths before unsafe writes.
5. Add structured route error mapping.
6. Add frontend API types and hook conflict state.
7. Add compact confirmation panel and page routing for `Open existing project`.
8. Run backend, frontend, build, diff, and forbidden-scope validation.

Stop condition for implementation:

- If the workbook authority path cannot safely know or bind the final number before workbook write, stop and route Planner/User for a split lane. Do not implement a local override that writes the workbook first and discovers local duplicate afterward.

---

## 18. Planner Source-Of-Truth Reconciliation

Reconciliation facts:

- Planner Discovery / planned lane creation completed in `docs/lane_evidence/TASK_348A_local-ltr-duplicate-override-confirmation_planner.md`.
- Reviewer plan gate passed.
- User approved TASK_348A Developer planning-first.
- Developer planning-first completed in `docs/lane_evidence/TASK_348A_local-ltr-duplicate-override-confirmation_developer.md`.
- Reviewer implementation-readiness gate passed.
- User explicitly approved TASK_348A reconciliation and Developer implementation.

Reconciled authorization:

- TASK_348A is implementation authorized and pending Developer implementation.
- This does not mark the task complete.
- Developer May Touch remains the exact implementation scope described in this plan.
- Scope locks remain active: no real public-drive LTR workbook or public-drive data mutation; no real local/public folder mutation; no Matrix Editor, Folder Actions, unrelated Project Workbench behavior, StepInstance, Report, AI, permissions, LAN/server, multi-user, release/packaging residuals, Settings/LTR helper residual cleanup, `.agents/**`, or `docs/project_management/**`.

Next role: Reviewer implementation re-gate.

---

## 19. B1 Adjacent New Project Setup Scope Reconciliation

Reviewer B1 finding:

- The implementation diff includes adjacent New Project setup/defaulting behavior not covered by the original TASK_348A May Touch.
- The exact files are:
  - `backend/application/intake_case_review_service.py`
  - `frontend/src/features/new-project/NewProjectSetupConfirmationPanel.tsx`
  - `tests/unit/test_intake_case_review_service.py`

Planner decision:

- Reconcile the exact adjacent behavior into the TASK_348A package scope.
- Do not split a new lane for these three already-implemented, user-requested, validated hunks.
- Do not broaden TASK_348A beyond the exact accepted adjacent behavior.

Facts supporting this decision:

- Thread `019f2347-8027-7980-9f27-46c19284f7d9` was accessible from this Planner thread.
- That thread records a user-requested New Project setup adjustment:
  - field order: `Sample Description*` before `Test Item*`;
  - default `Test Type in sheet` should be `Analysis` for the failure-analysis application context, otherwise infer from words in `Test Item` where possible.
- Developer evidence records that the adjacent changes are not technically required for TASK_348A duplicate override, but are user-requested and validated.
- Current repo diff confirms the adjacent changes are limited to parsed-intake defaults, field order, and focused tests.

Accepted adjacent behavior:

- `backend/application/intake_case_review_service.py` may derive default `project_setup.sample_description` from the first parsed sample table data cell when no saved setup override exists.
- `backend/application/intake_case_review_service.py` may derive default `project_setup.test_item` from the first `requested_testing_rows[].test_to_be_performed` value when no saved setup override exists.
- `backend/application/intake_case_review_service.py` may derive default `project_setup.test_type_in_sheet` from `Lab/Failure Analysis`, matching words in `test_item`, or fallback `Partial Qualification`.
- Saved/manual `project_setup` values remain authoritative and must not be overwritten by parsed defaults.
- `frontend/src/features/new-project/NewProjectSetupConfirmationPanel.tsx` may display `Sample Description*` before `Test Item*`.
- `tests/unit/test_intake_case_review_service.py` may include focused coverage for the adjacent defaulting behavior.

Still locked:

- No broad New Project setup refactor.
- No additional intake parser or precheck behavior changes beyond the exact defaults above.
- No public-drive workbook authority changes outside TASK_348A duplicate override semantics.
- No real workbook/public-drive/local-folder mutation.
- No Matrix Editor, Folder Actions, Project Workbench unrelated behavior, Project Registry redesign, StepInstance, Report, AI, permissions, LAN/server, or multi-user.
- No Basic Information, Settings/LTR, release/packaging residual cleanup.
- No `.agents/**` or `docs/project_management/**`.

Reviewer re-gate expectation:

- Treat B1 as scope-reconciled by Planner.
- Re-review the actual diff to confirm the adjacent behavior does not exceed the accepted files/behavior above.
- If the diff stays within this exact boundary, proceed with normal TASK_348A Reviewer implementation gate.

Next role after this reconciliation: Reviewer implementation re-gate. Do not route QA or Integrator until Reviewer passes.
