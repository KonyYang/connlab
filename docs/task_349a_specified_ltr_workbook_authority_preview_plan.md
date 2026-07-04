# TASK_349A Specified LTR Workbook Authority Preview Plan

> Status: complete/accepted / Integrator packaging-readiness accepted
> Task: `TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW`
> Lane: `specified-ltr-workbook-authority-preview`
> Created: 2026-07-04

---

## 1. Discovery Gate

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active task/lane: none after `TASK_348B_LOCAL_LTR_DUPLICATE_CANCEL_STATE_RECOVERY` Integrator acceptance.

Current role: Planner.

Why Planner is allowed: Orchestrator delegated a new formal planning-first lane creation for TASK_349A and explicitly prohibited Developer routing and product code edits.

---

## 2. User Goal Restatement

When an operator uses a full specified DL number in New Project / Intake, ConnLab must treat the public-drive LTR Excel workbook as the first authority. Clicking `Apply LTR Number` should first run a read-only workbook lookup and show the current row for confirmation. If the row is missing, ConnLab must stop and return to Intake without local project creation. If the row is found and confirmed, the existing Apply LTR flow may continue, with TASK_348A local duplicate conflict remaining as the second-layer protection.

---

## 3. Evidence Read

Governance:

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`

UI/architecture:

- `$impeccable` product context
- `PRODUCT.md`
- `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`

Task context:

- `tasks/TASK_347A_NEW_PROJECT_APPLY_LTR_BUSY_LOCK_UX.md`
- `tasks/TASK_348A_LOCAL_LTR_DUPLICATE_OVERRIDE_CONFIRMATION.md`
- `tasks/TASK_348B_LOCAL_LTR_DUPLICATE_CANCEL_STATE_RECOVERY.md`
- `docs/task_board.md` TASK_347A/TASK_348A/TASK_348B closeout rows

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

## 4. Confirmed Facts

Confirmed by user:

- Public-drive LTR Excel is the first authority for specified DL availability.
- Apply LTR must first run a read-only workbook row query for the specified DL.
- ConnLab must not create/confirm local Project or write workbook before this authority preview.
- Found rows must be shown even if blank, partial, or complete.
- Not found must show `LTR workbook 中不存在该编号` and stop local creation.
- Local duplicate conflict is second-layer protection after workbook confirmation.
- Existing workbook preview/read-only capability should be reused.

Confirmed by repository evidence:

- Current New Project Apply calls `completeNewProject` directly from `useNewProjectCompletion`.
- `completeNewProject` currently posts to `/api/intake-cases/{case_id}/complete-new-project`.
- `NewProjectCompletionService.complete` currently confirms or loads the local Project before committing LTR authority.
- Current specified full DL local duplicate checks happen after local project confirmation/loading.
- `ExcelComLTRWorkbookGateway` supports read-only sessions, `find_ltr_number`, and `read_registration_row`.
- `LtrWorkbookTransactionGateway.open_read_only_transaction` opens a read-only workbook without lock, backup, save, or write.
- Workbench Basic Information sync already locates exact LTR rows and maps A:Q row values to business labels.
- `ProjectBasicInformationSummaryCard` already renders a compact LTR workbook preview table for Workbench, but Workbench behavior should remain locked.

Inferred by Planner:

- TASK_349A can be a single lane covering backend preview API plus frontend confirmation flow because both are required for one serialized authority gate.
- The completion API needs a preview acknowledgment or token to prevent bypassing the preview from frontend-only enforcement.
- The first implementation should support full `DL-YYYY-MM-NNN...` specified inputs only. Suffix-only specified input behavior should remain existing behavior or return to Planner if product policy changes.

Not yet confirmed:

- Exact preview-token implementation detail: stateless preview hash vs stored short-lived token.
- Whether full DL rows outside the year sheet should be searched globally or only by parsed year sheet. Safe default: parsed year sheet first, matching workbook year semantics, with duplicate/global mismatch blockers if found during implementation.

These unknowns do not block a planned lane because they can be reviewed as implementation design choices at Reviewer plan gate. They must not be treated as approved implementation details before review.

---

## 5. Current Code Boundary

Specified LTR Apply:

- UI accepts auto or specified mode in `NewProjectCompletionDock`.
- Full DL and suffix-only inputs are valid in the current frontend helper.
- `useNewProjectCompletion.complete` immediately calls `completeNewProject` with setup values.
- `CompleteNewProjectInput` already includes `specified_ltr_number` and `duplicate_resolution`.

Local duplicate location:

- `NewProjectCompletionService._commit_or_load_ltr` resolves the LTR input and calls `ensure_no_conflict_or_valid_confirmation` before commit.
- This occurs after `_confirm_or_load_project`, so it is too late for the new workbook-first authority rule.

Workbook read/write capability:

- `LtrWorkbookWritePreviewService` creates no-write mapping previews from local project/setup data, but it is project-based and not sufficient by itself because TASK_349A must run before local Project confirmation.
- `LtrWorkbookBasicInformationSyncService` reads the current exact workbook row and comparison values, but it is also project/registered-LTR based.
- The infrastructure gateway already has the low-level read-only row lookup/read primitives needed for a new Intake-level preview service.

Workbench preview reuse:

- Reuse the row label order, formatting concept, and read-only gateway primitives.
- Do not change Workbench Basic Information sync UI, routes, semantics, or commit behavior.

---

## 6. Lane Split Decision

Recommended: one planned lane.

Rationale:

- Backend read-only preview, frontend confirmation, and completion ack are one user-visible gate.
- Splitting backend preview and frontend confirmation would leave an unusable half-feature and make bypass prevention harder to review.
- The lane is still narrow because it excludes write semantics, schema changes, Workbench behavior, and suffix-only redesign.

Split fallback:

- Split into backend-only and frontend-only lanes only if Reviewer decides the preview-token enforcement or read-only workbook lookup requires a broader service boundary than expected.

---

## 7. API Contract Draft

Endpoint:

```text
POST /api/intake-cases/{case_id}/specified-ltr-workbook-authority-preview
```

Request:

```json
{
  "specified_ltr_number": "DL-2026-05-011"
}
```

Response states:

- `found`: exact workbook DL row exists and row values are returned.
- `not_found`: workbook opened/read successfully but exact DL row does not exist.
- `blocked`: workbook path/config/open/read issue or duplicate exact rows make authority preview unsafe.

Response fields:

- `status`
- `ltr_number`
- `message`
- `workbook_path`
- `sheet_name`
- `row_number`
- `row_values`: business-labeled values for Project Type, Description P/N, Test Item, Test Type, Requested by, Location, Project Leader, Test Result, Failed item, Sample deposition, Sub-contract, Test Fee, Remarks (PO)
- `preview_token` or `preview_hash` for found state
- `warnings`

Completion request extension:

- Add `specified_ltr_workbook_preview_ack` to `CompleteNewProjectInput` / route request.
- Backend must reject full specified DL completion without a valid ack before confirming or creating local Project.
- The ack should include `acknowledged`, token/hash, sheet, and row.

---

## 8. UX Confirmation Flow Draft

Full specified DL:

1. Operator selects `Use specified LTR number`.
2. Operator enters a complete full DL number.
3. Operator clicks `Apply LTR Number`.
4. UI enters TASK_347A-style busy lock while preview loads.
5. If not found, show `LTR workbook 中不存在该编号`; only Close/Back action is available.
6. If found, show `Confirm LTR workbook row` with workbook path, sheet, row, and business row table.
7. Operator clicks `Use this LTR number`.
8. UI calls existing completion endpoint with preview ack.
9. If local duplicate exists, show TASK_348A local duplicate confirmation.
10. If local duplicate is resolved or absent, existing completion/write flow continues.

Cancel/close:

- Closing found preview returns to Intake with imported application/setup values preserved.
- Closing not-found returns to Intake with no local creation or workbook write.

Copy/design:

- Keep copy compact and operational.
- Avoid technical terms such as API, hash, or backend in the UI.
- Use the existing restrained product style and a table/dense confirmation surface rather than a large status card.

---

## 9. May Touch

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
- `tasks/TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW.md`
- `docs/task_349a_specified_ltr_workbook_authority_preview_plan.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_*.md`
- `docs/task_board.md` through normal lane flow

---

## 10. Must Not Touch / Locked Paths

Must not touch:

- Database schema/migration unless Reviewer explicitly approves a demonstrated need.
- Workbench Basic Information LTR update preview semantics.
- Matrix Editor.
- Fee Evaluation.
- Folder Actions/public folder workflow.
- Projects registry/list.
- Real public-drive workbook mutation during tests.
- Real local/public folders.
- Unrelated Basic Information, Settings/LTR, release/packaging, desktop release, `temp_agents_stash.md`, or board residual cleanup.
- `.agents/**`
- `docs/project_management/**`
- StepInstance, Report, AI, permissions, LAN/server, multi-user.

Locked paths:

- `backend/infrastructure/storage/**`
- migration/database schema files
- `frontend/src/features/project-workbench/**`
- `frontend/src/features/matrix-editor/**`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- real workbook/public-drive data paths
- release/packaging residual paths

---

## 11. Validation Plan

Backend:

- Preview found returns workbook path, sheet, row, row values, and preview token/hash without write.
- Preview not-found returns `not_found` and message `LTR workbook 中不存在该编号`.
- Preview blocked returns actionable blocker for missing path/open/read/duplicate exact rows.
- Full specified DL completion without preview ack is rejected before local project confirmation or workbook write.
- Full specified DL completion with valid ack proceeds to existing local duplicate second-layer conflict if local duplicate exists.
- No real workbook mutation in tests; use fakes/temp fixtures.

Frontend:

- Apply full specified DL calls preview first, not `completeNewProject`.
- Found preview renders row values and metadata.
- Confirm preview calls `completeNewProject` with ack.
- Not-found preview blocks completion and preserves Intake state.
- Cancel/close preserves imported source/form/setup state.
- TASK_347A busy lock remains active during preview/completion.
- TASK_348A local duplicate panel still appears after workbook confirmation if backend returns `LOCAL_LTR_DUPLICATE`.
- Auto LTR and suffix-only specified behavior do not regress unless explicitly scoped.

Build:

- Focused backend tests.
- Focused frontend tests.
- `npm run build`.
- `git diff --check` and trailing whitespace scans.
- Forbidden-scope checks for schema, Workbench behavior, Matrix/Fee/Folder Actions, real workbook mutation, Settings/LTR/release residuals.

---

## 12. Questions

Blocking questions: none for planned lane creation.

Reviewer plan gate should explicitly review:

1. Whether preview ack is better as a stateless hash or stored short-lived token.
2. Whether exact DL lookup should be parsed-year-sheet-only or global with duplicate mismatch blockers.
3. Whether suffix-only specified inputs remain existing behavior or should be routed into a later separate lane.

---

## 13. Definition Of Ready

Satisfied for planned lane creation:

- User goal and operator workflow are clear.
- Board state confirms no active lane after TASK_348B acceptance.
- Existing New Project and workbook preview/read-only code paths were checked.
- May Touch, Must Not Touch, Locked Paths, validation gate, and merge gate are concrete.
- Acceptance path is testable with backend fakes and frontend mocked preview.
- Non-goals prevent schema, Workbench, write semantics, and future-scope creep.

Not approved for implementation.

Recommended next role: ConnLab Reviewer plan gate.

Planner gate: ready_for_reviewer_plan_gate.

---

## 14. Developer Planning-First Refinement

Status: developer planning-first refined after Orchestrator reported Reviewer plan gate pass and user approval for Developer planning-first.

Source-of-truth note:

- Planner source-of-truth reconciliation now records Reviewer plan gate pass, user approval for Developer planning-first, Developer planning-first completion, Reviewer implementation-readiness pass, and user approval for Developer implementation.
- This refinement and reconciliation authorize only the approved TASK_349A implementation scope.
- TASK_349A remains not complete until Developer implementation, Reviewer implementation gate, QA gate if routed, and Integrator packaging/readiness pass.

### 14.1 Future Implementation May Touch

Backend application and API:

- `backend/application/specified_ltr_workbook_authority_preview_service.py` new read-only preview service.
- `backend/application/new_project_completion_service.py` to require and verify preview acknowledgement before local project confirmation for full specified DL inputs.
- `backend/api/routes_new_project_completion.py` to add preview route DTOs and extend completion DTO with preview acknowledgement.
- `backend/api/dependencies.py` to provide the preview service dependency.
- `backend/infrastructure/office/excel_com_ltr_workbook_gateway.py` only if the current read-only row lookup lacks a small helper needed by the preview service.
- `backend/infrastructure/office/ltr_workbook_transaction_gateway.py` only if dependency wiring needs an existing read-only transaction adapter exposed.

Frontend:

- `frontend/src/api/client.ts` for typed preview DTOs, preview helper, and completion acknowledgement payload.
- `frontend/src/features/new-project/useNewProjectCompletion.ts` or a new adjacent hook such as `useSpecifiedLtrWorkbookAuthorityPreview.ts` for preview-first orchestration.
- `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx` new compact confirmation panel.
- `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.test.tsx` new focused tests.
- `frontend/src/features/new-project/NewProjectCompletionDock.tsx` only for disabled/busy state plumbing or helper export, not for new business orchestration.
- `frontend/src/features/new-project/NewProjectCompletionDock.test.tsx` as needed for busy/disabled regression.
- `frontend/src/pages/IntakeInboxPage.tsx` only for page composition, busy-lock source, and panel placement.
- `frontend/src/pages/IntakeInboxPage.test.tsx` for page-level preview lock and state-preservation coverage.
- `frontend/src/intake-inbox.css` only if the new panel needs small restrained styling.

Tests:

- `tests/unit/test_specified_ltr_workbook_authority_preview_service.py` new service tests with fake workbook gateway.
- `tests/integration/test_specified_ltr_workbook_authority_preview_api.py` new API tests.
- `tests/integration/test_new_project_completion_api.py` for missing/stale ack and local duplicate second-layer regressions.

Documentation and evidence:

- `docs/task_349a_specified_ltr_workbook_authority_preview_plan.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_developer.md`

### 14.2 Locked Paths And Non-Goals

Keep locked unless a separate approved reconciliation changes scope:

- database schema and migrations
- local LTR duplicate ownership/audit semantics from TASK_348A
- TASK_347A busy-lock core behavior except adding preview state to the same lock source
- TASK_348B cancel recovery semantics except preserving them during preview cancel
- Workbench Basic Information LTR update preview semantics
- Project Workbench, Matrix Editor, Fee Evaluation, Folder Actions, Projects registry/list
- real public-drive workbook files, real local/public folders, and LTR workbook authority writes during preview
- Settings/LTR helper residuals, Basic Information residuals, release/packaging residuals, desktop release residuals, and `temp_agents_stash.md`
- `.agents/**` and `docs/project_management/**`

### 14.3 Backend Preview API Contract

Endpoint:

```text
POST /api/intake-cases/{case_id}/specified-ltr-workbook-authority-preview
```

Request:

```json
{
  "specified_ltr_number": "DL-2026-05-011"
}
```

Response shape:

```json
{
  "status": "found",
  "ltr_number": "DL-2026-05-011",
  "message": "LTR workbook row found.",
  "workbook": {
    "workbook_path": "D:/PublicProject/LTR.xlsx",
    "sheet_name": "2026",
    "row_number": 42
  },
  "row_values": [
    {
      "field_key": "project_no",
      "label": "Project No.",
      "value": "DL-2026-05-011",
      "is_blank": false
    }
  ],
  "preview_ack": {
    "preview_token": "opaque-or-hash",
    "row_fingerprint": "row-fingerprint"
  },
  "blockers": [],
  "warnings": []
}
```

Status rules:

- `found`: exact full DL row exists in the authority workbook. Return business-labeled row values even when values are blank, partial, or full. Return a preview acknowledgement token/hash.
- `not_found`: exact full DL row is absent. Return message `LTR workbook 中不存在该编号`. Do not return an acknowledgement token. Frontend must allow only close/back to Intake.
- `blocked`: workbook path/config/open/read/sheet/ambiguous-row issue prevents authority preview. Return short actionable blocker copy. Do not return an acknowledgement token.

Preview must be read-only:

- no local `Project` creation or confirmation
- no local `LtrRecord` binding
- no workbook write, save, backup, or lock
- no public-drive authority commit

### 14.4 Preview Ack And Completion Enforcement

Developer planning decision: use a stateless acknowledgement token/hash for the first implementation. Do not add schema or migration.

Completion request extension:

```json
{
  "specified_ltr_workbook_preview_ack": {
    "acknowledged": true,
    "ltr_number": "DL-2026-05-011",
    "sheet_name": "2026",
    "row_number": 42,
    "preview_token": "opaque-or-hash",
    "row_fingerprint": "row-fingerprint"
  }
}
```

Enforcement:

- Required only when `ltr_mode = "specified"` and `specified_ltr_number` parses as a full `DL-YYYY-MM-NNN...` number.
- Suffix-only specified input remains existing behavior in TASK_349A unless Reviewer/User explicitly reopens policy.
- `NewProjectCompletionService.complete` must verify the acknowledgement before `_confirm_or_load_project`.
- Verification reopens the workbook read-only, rechecks exact row location and fingerprint, and rejects missing, stale, or mismatched acknowledgement before any local project confirmation, local LTR binding, or workbook write.
- After valid acknowledgement, existing completion continues and TASK_348A local duplicate remains the second-layer conflict.

### 14.5 Workbook Lookup Policy

Developer planning decision for V1:

- Parse full DL year and use the matching workbook sheet for exact row lookup.
- Do not infer or rewrite DL years.
- Missing workbook, missing expected sheet, unreadable workbook, or duplicate exact rows in a searched sheet are `blocked`.
- Exact row absent in the parsed-year sheet is `not_found`.
- Global cross-sheet search remains a follow-up unless Reviewer requires it before implementation.

### 14.6 Frontend UX Flow

Full specified DL Apply:

1. User enters a full specified DL number and clicks `Apply LTR Number`.
2. Frontend calls the preview endpoint first, not `completeNewProject`.
3. While preview is loading, reuse TASK_347A page-level busy/interaction lock source so Import, drag/drop, editor/setup/sidebar-conflicting actions, and repeat Apply are blocked.
4. `found`: show compact authority preview panel with workbook row summary and actions:
   - primary: `Use this LTR number`
   - secondary: `Cancel`
5. Confirm sends existing `completeNewProject` with `specified_ltr_workbook_preview_ack`.
6. `not_found`: show `LTR workbook 中不存在该编号` and only `Close` or `Back to Intake`.
7. `blocked`: show concise blocker text and only return/cancel actions.
8. Cancel closes only the preview panel and preserves imported Intake source, form/setup values, and readiness state, matching TASK_348B behavior.
9. If completion returns `LOCAL_LTR_DUPLICATE`, show the existing TASK_348A duplicate confirmation panel after workbook acknowledgement.

UX constraints:

- No fake progress phases.
- No long explanation.
- No raw backend enum text.
- No Workbench LTR update preview behavior changes.
- Keep restrained operational UI and dense confirmation layout.

### 14.7 Focused Test Plan

Backend:

- Preview found returns row metadata, labeled row values, acknowledgement token/hash, and performs no writes.
- Preview found covers blank, partial, and full row values.
- Preview not-found returns `not_found` with `LTR workbook 中不存在该编号`, no token, and no writes.
- Preview blocked covers missing workbook config, read failure, missing sheet, and duplicate exact rows.
- Full specified DL completion without ack is rejected before local project confirmation.
- Full specified DL completion with stale or mismatched ack is rejected before local project confirmation.
- Full specified DL completion with valid ack reaches existing local duplicate check and can return `LOCAL_LTR_DUPLICATE`.
- Existing auto and suffix-only specified behavior is unchanged.
- Tests use fakes/temp fixtures only and do not mutate real workbook files.

Frontend/API client:

- API client types include preview status, row values, workbook metadata, and completion ack.
- Full specified DL Apply calls preview helper first and does not call `completeNewProject` until confirmation.
- Found preview renders blank/partial/full row values and `Use this LTR number`.
- Confirm sends `specified_ltr_workbook_preview_ack` and preserves TASK_347A busy lock during completion.
- Not-found disables continuation and preserves Intake state.
- Cancel preserves imported source/form/setup/readiness state.
- Local duplicate panel still appears after preview acknowledgement.
- Auto and suffix-only specified paths do not show the authority preview panel.

Validation:

- focused backend tests
- focused frontend/API client tests
- `npm run build`
- `git diff --check`
- trailing whitespace scan
- static scan proving no real workbook/public-drive path writes
- forbidden-scope status proving no schema, Workbench, Matrix, Folder Actions, Projects registry, Settings/LTR, release/packaging, `.agents`, or `docs/project_management` changes

### 14.8 Schema And Migration Decision

No schema or migration is needed for TASK_349A V1. If implementation discovers a need for persisted preview tokens or workbook preview audit, stop and return to Planner/Reviewer for scope reconciliation before coding that storage change.

Developer planning gate: implementation authorized after Planner source-of-truth reconciliation.

---

## 15. Source-Of-Truth Reconciliation

Reconciliation date: 2026-07-04.

Recorded facts:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed in `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_developer.md`.
- Reviewer implementation-readiness gate passed per Orchestrator routing context.
- User approved TASK_349A reconciliation and Developer implementation.
- Planner reconciliation evidence is recorded in `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_reconciliation_planner.md`.

Current authorization:

- TASK_349A is implementation authorized / pending Developer implementation.
- The next role is Developer implementation pass.
- Developer must stop after updating developer evidence to `ready_for_review`.

Scope remains locked:

- Specified-LTR workbook authority preview only.
- No database schema/migration unless separately reviewed.
- No Workbench LTR update preview semantics changes.
- No real workbook/public-drive mutation during tests or implementation.
- No Matrix Editor, Fee Evaluation, Folder Actions/public-folder workflow, Projects registry/list, Basic Information residual cleanup, Settings/LTR helper residual cleanup, release/packaging residual cleanup, `.agents/**`, `docs/project_management/**`, StepInstance, Report, AI, permissions, LAN/server, or multi-user scope.

---

## 16. QA B1 Package/Scope Reconciliation

Reconciliation date: 2026-07-04.

QA B1 finding:

- Functional validation passed, but actual worktree diff contains adjacent intake/precheck/parser/duplicate-summary/New Project files outside the clearly recorded TASK_349A implementation package.
- Developer triage states those adjacent files are not required for TASK_349A and should not be silently folded into this lane.

Planner decision:

- Exclude the B1 adjacent diffs as external residuals.
- Do not expand TASK_349A May Touch or package scope to include those residuals.
- Do not revert them in Planner, because they may be pre-existing or separately user-requested and Planner is not authorized to roll back product work.
- Require package isolation before acceptance: TASK_349A package must include only workbook-authority-preview files and TASK_349A docs/evidence/board.

Approved TASK_349A product package file list:

- `backend/application/specified_ltr_workbook_authority_preview_service.py`
- `backend/application/new_project_completion_service.py`
- `backend/api/routes_new_project_completion.py`
- `backend/api/dependencies.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/new-project/useNewProjectCompletion.ts`
- `frontend/src/features/new-project/SpecifiedLtrWorkbookAuthorityPreviewPanel.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/intake-inbox.css`
- `tests/unit/test_specified_ltr_workbook_authority_preview_service.py`
- `tests/integration/test_new_project_completion_api.py`
- `frontend/src/pages/IntakeInboxPage.test.tsx`

Allowed TASK_349A docs/evidence:

- `tasks/TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW.md`
- `docs/task_349a_specified_ltr_workbook_authority_preview_plan.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_planner.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_developer.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_qa.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_reconciliation_planner.md`
- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_package_reconciliation_planner.md`
- `docs/task_board.md`

Explicitly excluded residuals:

- `backend/application/intake_form_selection_service.py`
- `backend/modules/intake/application_form_parser.py`
- `tests/unit/test_application_form_parser.py`
- `tests/unit/test_intake_form_selection_service.py`
- `frontend/src/features/precheck/PrecheckFieldGrid.tsx`
- `frontend/src/features/precheck/precheckReviewSelectors.ts`
- `frontend/src/intake-case-review.css`
- `backend/application/ltr_duplicate_resolution_service.py`
- adjacent New Project local-duplicate/setup files omitted from Developer evidence section 2
- Basic Information residuals
- Settings/LTR helper residuals
- release/packaging/desktop residuals
- `.agents/**`
- `docs/project_management/**`
- `temp_agents_stash.md`

Next gate expectation:

- Re-gate should verify package isolation before acceptance.
- If package isolation is not possible without reverting user-requested adjacent work, route to User/Planner for a separate lane/owner decision.

---

## 17. Package-Isolation Decision

Decision date: 2026-07-04.

Integrator packaging blocker:

- `backend/api/dependencies.py` mixes TASK_349A preview dependency injection with duplicate-resolution constructor arguments (`temporary_context_store`, `folder_store`) that depend on excluded `backend/application/ltr_duplicate_resolution_service.py` residuals.
- `frontend/src/pages/IntakeInboxPage.tsx` mixes TASK_349A preview wiring with adjacent dependencies on excluded New Project files: moved `completionError` plumbing and `buildNewProjectRequiredState(projectFields, ...)`.
- A package containing only the reconciled TASK_349A path list would not be self-contained.
- A package including the dependent residual files would violate section 16 and QA B1 reconciliation.

Planner decision:

- Choose Option A: route Developer/package-isolation owner to split mixed hunks so TASK_349A becomes self-contained without adjacent residuals.
- Do not silently merge adjacent residuals into TASK_349A.
- Do not create a separate adjacent lane now; only create one if Developer reports package isolation is impossible without deleting user-requested adjacent behavior.
- Do not expand TASK_349A scope under Option C; there is no strong TASK_349A business authorization to absorb duplicate-resolution summary, precheck/parser/selection, or adjacent New Project setup residuals.

Developer package-isolation fix pass rules:

- May edit only TASK_349A candidate files and Developer evidence.
- Must remove or isolate references that require excluded residual files.
- Must keep specified-LTR workbook authority preview behavior intact.
- Must not revert unknown user work wholesale.
- Must stop and return to Planner/User if a self-contained TASK_349A package cannot be produced without adjacent scope.

Re-gate expectation:

- After Developer package-isolation evidence, Reviewer/QA should verify the candidate package is self-contained and contains no excluded residual dependencies before Integrator packaging/readiness.
