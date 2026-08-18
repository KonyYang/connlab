# TASK_349A Specified LTR Workbook Authority Preview

> Status: complete/accepted - Integrator packaging/readiness accepted
> Created: 2026-07-04
> Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
> Lane: specified-ltr-workbook-authority-preview

---

## 1. Purpose

Plan a controlled New Project / Intake authority preview gate for full specified DL/LTR numbers.

When an operator selects `Use specified LTR number`, enters a complete `DL-YYYY-MM-NNN...` value, and clicks `Apply LTR Number`, ConnLab must first perform a read-only lookup in the public-drive LTR Excel workbook. The workbook row is the first authority for whether the specified DL number exists and may be used. ConnLab must not create or confirm the local Project, must not register local LTR ownership, and must not write the workbook before the operator reviews and confirms the workbook row.

This task is implementation-authorized after Reviewer plan gate, Developer planning-first, Reviewer implementation-readiness, explicit user approval, and Planner source-of-truth reconciliation. It is not complete.

---

## 2. User-Confirmed Business Rules

- Public-drive LTR Excel is the first authority for specified DL availability.
- Applying a full specified DL must first read the workbook row in read-only mode.
- No local Project confirmation, local LTR binding, or workbook write may happen before this workbook authority preview.
- If the workbook row is found, show key row values and workbook metadata for operator confirmation.
- The row must be shown whether it is blank, partially filled, or fully filled.
- Only after operator confirmation may the existing Apply LTR flow continue.
- Local duplicate conflict remains a second-layer protection after workbook confirmation.
- If the workbook row is not found, show `LTR workbook 中不存在该编号` and return to the Intake page without local creation.
- Reuse existing workbook preview/read-only capabilities where possible.

---

## 3. Repository Facts

Current New Project flow:

- `frontend/src/features/new-project/NewProjectCompletionDock.tsx` supports `Use specified LTR number` and validates full `DL-YYYY-MM-NNN...` values as well as suffix-only tokens.
- `frontend/src/features/new-project/useNewProjectCompletion.ts` calls `completeNewProject(activeCase.case_id, input)` directly when `Apply LTR Number` is clicked.
- `frontend/src/api/client.ts` maps that call to `POST /api/intake-cases/{case_id}/complete-new-project`.
- `backend/api/routes_new_project_completion.py` passes `specified_ltr_number` into `NewProjectCompletionService.complete`.
- `backend/application/new_project_completion_service.py` currently validates setup, confirms or loads the local Project, promotes setup values, then resolves and commits LTR authority.
- For specified full DL input, `_resolve_ltr_input` normalizes the number; local duplicate conflict checks currently happen before `ltr_commit.commit_project`, but after local project confirmation/loading.

Existing workbook capabilities:

- `backend/infrastructure/office/excel_com_ltr_workbook_gateway.py` supports read-only sessions, `find_ltr_number`, `read_ltr_number_cells`, and `read_registration_row`.
- `backend/infrastructure/office/ltr_workbook_transaction_gateway.py` supports read-only transactions without lock, backup, save, or write.
- `backend/application/ltr_workbook_basic_information_sync_service.py` already locates an exact registered DL row and reads current A:Q values for Workbench Basic Information sync.
- The accepted Workbench LTR update preview uses business labels in the required order: Project Type, Description P/N, Test Item, Test Type, Requested by, Location, Project Leader, Test Result, Failed item, Sample deposition, Sub-contract, Test Fee, Remarks (PO).
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx` already renders a compact workbook preview table and read-only workbook action for Workbench context.

---

## 4. Planner Decision

Create one planned lane:

```text
TASK_349A_SPECIFIED_LTR_WORKBOOK_AUTHORITY_PREVIEW
lane: specified-ltr-workbook-authority-preview
```

One lane can cover backend read-only preview API, frontend confirmation flow, and completion payload acknowledgment because the feature is one serialized gate in a single user action. It should split only if implementation discovery finds that existing workbook read helpers need a broader reusable service refactor or if suffix-only specified LTR behavior must be redesigned.

---

## 5. Scope

In scope for future implementation after approval:

- Add a backend read-only specified LTR workbook authority preview for full DL numbers.
- Add a typed API response for found/not-found/blocked preview states.
- Return workbook path, sheet, row, and business-labeled current row values.
- Add frontend API client types/helpers for the preview.
- Add a New Project confirmation surface before existing `completeNewProject` is called for full specified DL numbers.
- Extend the completion request with a preview acknowledgment or token so the backend can reject bypassed specified-DL completion.
- Preserve TASK_347A busy/interaction lock and TASK_348A/TASK_348B local duplicate behavior.
- Add focused backend/frontend tests.

Out of scope:

- No workbook write during preview.
- No database schema/migration unless Reviewer later approves a specific need.
- No change to Workbench LTR update preview semantics.
- No broad LTR authority rewrite.
- No suffix-only specified LTR redesign in this lane.
- No Matrix Editor, Fee Evaluation, Folder Actions/public folder workflow, Project Workbench unrelated behavior, StepInstance, Report, AI, permissions, LAN/server, or multi-user scope.

---

## 6. API Contract Draft

Preview endpoint draft:

```text
POST /api/intake-cases/{case_id}/specified-ltr-workbook-authority-preview
```

Request:

```json
{
  "specified_ltr_number": "DL-2026-05-011"
}
```

Response:

```json
{
  "status": "found",
  "ltr_number": "DL-2026-05-011",
  "workbook_path": "D:\\Public...\\LTR.xls",
  "sheet_name": "2026",
  "row_number": 42,
  "row_values": [
    { "field_name": "project_type", "label": "Project Type", "value": "NPD" },
    { "field_name": "description_pn", "label": "Description P/N", "value": "..." },
    { "field_name": "test_item", "label": "Test Item", "value": "..." },
    { "field_name": "test_type", "label": "Test Type", "value": "..." },
    { "field_name": "requested_by", "label": "Requested by", "value": "..." },
    { "field_name": "location", "label": "Location", "value": "..." },
    { "field_name": "project_leader", "label": "Project Leader", "value": "..." },
    { "field_name": "test_result", "label": "Test Result", "value": "..." },
    { "field_name": "failed_item", "label": "Failed item", "value": "..." },
    { "field_name": "sample_deposition", "label": "Sample deposition", "value": "..." },
    { "field_name": "sub_contract", "label": "Sub-contract", "value": "..." },
    { "field_name": "test_fee", "label": "Test Fee", "value": "..." },
    { "field_name": "remarks_po", "label": "Remarks (PO)", "value": "..." }
  ],
  "preview_token": "opaque-short-lived-token-or-hash",
  "warnings": []
}
```

Not found:

```json
{
  "status": "not_found",
  "ltr_number": "DL-2026-05-011",
  "message": "LTR workbook 中不存在该编号",
  "workbook_path": "D:\\Public...\\LTR.xls",
  "sheet_name": "2026",
  "row_number": null,
  "row_values": [],
  "preview_token": null,
  "warnings": []
}
```

Blocked:

```json
{
  "status": "blocked",
  "ltr_number": "DL-2026-05-011",
  "message": "Unable to read LTR workbook for preview.",
  "workbook_path": null,
  "sheet_name": null,
  "row_number": null,
  "row_values": [],
  "preview_token": null,
  "warnings": []
}
```

Completion extension draft:

```json
{
  "specified_ltr_number": "DL-2026-05-011",
  "specified_ltr_workbook_preview_ack": {
    "acknowledged": true,
    "preview_token": "opaque-short-lived-token-or-hash",
    "sheet_name": "2026",
    "row_number": 42
  }
}
```

The exact token mechanism can be a deterministic server-verifiable preview hash if no storage is needed. It must prove that the operator confirmed the workbook preview before specified-DL completion continues.

---

## 7. Data Flow Draft

```text
Use specified LTR number + full DL input
  -> Apply LTR Number
  -> read-only workbook authority preview
  -> if not found: show message and return to Intake without local creation
  -> if found: show row confirmation table
  -> user confirms workbook row
  -> existing complete-new-project with preview ack
  -> backend verifies preview ack before local project confirmation/commit proceeds
  -> local duplicate second-layer conflict may appear
  -> if local duplicate confirmed, existing TASK_348A replacement flow continues
  -> workbook write/replace proceeds through existing commit service
```

---

## 8. UX Flow Draft

Found preview:

- Show a compact confirmation layer near the New Project completion area or as a focused dialog consistent with the existing local duplicate conflict surface.
- Title: `Confirm LTR workbook row`.
- Metadata: LTR number, workbook path, sheet, row.
- Table: business labels and current workbook values in the accepted Workbench order.
- Primary action: `Use this LTR number`.
- Secondary action: `Cancel`.
- Confirming the preview continues to the existing Apply LTR flow.

Not found:

- Show `LTR workbook 中不存在该编号`.
- No continue action.
- Only `Close` / `Back to Intake`.
- Preserve the imported application and setup values.

Busy/interaction lock:

- Reuse TASK_347A busy/locked state for the preview request and later completion request.
- Do not display fake workbook phases unless backend exposes them.
- Preserve TASK_348B Cancel state recovery expectations.

---

## 9. May Touch

Future Developer implementation may touch:

- `backend/application/*ltr*workbook*preview*` services or a new focused application service for specified LTR workbook authority preview.
- `backend/infrastructure/office/excel_com_ltr_workbook_gateway.py` only for narrow read-only helper reuse if needed.
- `backend/infrastructure/office/ltr_workbook_transaction_gateway.py` only if the read-only transaction interface needs a narrow reusable adapter.
- `backend/api/routes_new_project_completion.py` or a new focused route module for the Intake specified LTR preview API.
- `backend/api/dependencies.py` for service wiring.
- `frontend/src/api/client.ts` for typed preview DTO/helper and completion ack payload.
- `frontend/src/features/new-project/**`
- `frontend/src/pages/IntakeInboxPage.tsx`
- focused backend/frontend tests.
- TASK_349A task/plan/evidence/board docs through normal lane flow.

---

## 10. Must Not Touch

- Database schema/migration unless Reviewer explicitly approves a demonstrated need.
- Workbench Basic Information LTR update preview semantics and user flow.
- Workbench lifecycle, Matrix Editor, Fee Evaluation, Folder Actions/public folder workflow, Projects registry/list.
- Real public-drive workbook mutation during tests.
- Real local/public folders.
- Unrelated Basic Information, Settings/LTR, release/packaging, desktop release, `temp_agents_stash.md`, or board residual cleanup.
- `.agents/**`
- `docs/project_management/**`
- StepInstance, Report, AI, permissions, LAN/server, multi-user.

---

## 11. Locked Paths

Locked unless a separate approved lane exists:

- `backend/infrastructure/storage/**`
- migration/database schema files
- Workbench Project Basic Information UI behavior outside read-only reuse references
- `frontend/src/features/project-workbench/**`
- `frontend/src/features/matrix-editor/**`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- real workbook files and public-drive data
- real `D:\Test Project/**`
- real `D:\PublicProject/**`
- `.agents/**`
- `docs/project_management/**`
- release/packaging residuals

---

## 12. Validation Gate

Reviewer plan gate should verify:

- The lane enforces workbook-first authority for full specified DL Apply.
- The preview endpoint is read-only and does not confirm Project, register local LTR, or write workbook.
- The not-found branch blocks local creation.
- Local duplicate remains second-layer after workbook confirmation.
- May Touch is sufficient and locked paths prevent scope creep.

Future implementation validation should include:

- Backend unit tests for found, not-found, duplicate exact workbook rows, workbook read error, and no-write behavior.
- Backend/API tests proving full specified DL completion without preview ack is rejected before local project confirmation or workbook write.
- Backend/API tests proving preview-found plus ack allows existing completion to proceed to local duplicate conflict when local duplicate exists.
- Frontend tests for found preview confirmation, not-found message, cancel/close preserving Intake state, busy lock, and no `completeNewProject` call before preview confirmation.
- Regression that auto LTR and suffix-only specified behavior are not broadened by this lane unless explicitly scoped.
- `npm run build` and focused `npm test`.
- No real workbook mutation in tests; use fakes/temp fixtures.

---

## 13. Merge Gate

Do not merge or package until:

1. Reviewer plan gate passes.
2. User explicitly approves Developer planning-first and later implementation according to protocol.
3. Developer evidence records implementation details and validation.
4. Reviewer implementation gate passes.
5. QA gate runs the agreed frontend/browser and backend no-write smoke, or records a justified blocker.
6. Integrator confirms package scope excludes real workbook mutation, schema migration unless approved, Workbench behavior changes, Matrix/Fee/Folder Actions, Settings/LTR residuals, release residuals, `.agents/**`, and `docs/project_management/**`.

---

## 14. Next Role

Recommended next role: ConnLab Developer implementation pass.

Current stop point: complete/accepted by Integrator after package-isolation fix, Reviewer re-gate pass, and QA re-gate pass.

---

## 15. Implementation Authorization Reconciliation

Source-of-truth reconciliation recorded:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed in `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_developer.md`.
- Reviewer implementation-readiness gate passed per Orchestrator callback context.
- User explicitly approved TASK_349A reconciliation and Developer implementation.
- Planner reconciliation evidence is recorded in `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_reconciliation_planner.md`.

This authorization does not broaden scope beyond the TASK_349A specified-LTR workbook authority preview plan. Database schema/migration remains locked unless separately reviewed; Workbench LTR update preview semantics remain locked; preview must not mutate real public-drive workbook/data; Matrix, Fee Evaluation, Folder Actions/public-folder workflow, Projects registry/list, Basic Information residuals, Settings/LTR helper residuals, release/packaging residuals, `.agents/**`, `docs/project_management/**`, `temp_agents_stash.md`, StepInstance, Report, AI, permissions, LAN/server, and multi-user scope remain locked.

---

## 16. QA B1 Package/Scope Reconciliation

Planner decision after QA B1:

- The QA B1 adjacent diffs are excluded external residuals, not TASK_349A implementation scope.
- Developer triage records that these adjacent files are not required for workbook-first preview, read-only workbook access, preview acknowledgement verification, not-found blocking, or preview-confirm-to-completion handoff.
- There is no clear TASK_349A business authorization to silently merge those adjacent diffs into this lane.
- If the adjacent behavior is wanted, it needs a separate lane/owner or a separate explicit scope reconciliation; it must not be packaged with TASK_349A by default.

TASK_349A package may include only:

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
- TASK_349A task/plan/evidence/board docs

Explicitly excluded from TASK_349A package:

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

Current stop point:

- TASK_349A is complete/accepted by Integrator.
- Merge/package readiness accepted after Developer package-isolation fix, Reviewer/QA re-gate, and Integrator validation.
- QA/Integrator must not package the excluded residuals with TASK_349A.

Package reconciliation evidence:

- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_package_reconciliation_planner.md`

---

## 17. Package-Isolation Decision

Integrator packaging blocker:

- `backend/api/dependencies.py` contains TASK_349A preview dependency injection plus duplicate-resolution constructor arguments that depend on excluded `backend/application/ltr_duplicate_resolution_service.py` residuals.
- `frontend/src/pages/IntakeInboxPage.tsx` contains TASK_349A preview wiring plus adjacent dependencies on excluded New Project files, including moved completion error plumbing and `buildNewProjectRequiredState(projectFields, ...)`.
- Staging only the TASK_349A path list would create a non-self-contained package; staging the dependent residual files would violate the QA B1 package reconciliation.

Planner decision:

- Choose Option A: route Developer/package-isolation owner to split mixed hunks so TASK_349A becomes self-contained without adjacent residuals.
- Do not silently merge adjacent residuals into TASK_349A.
- Do not create a separate adjacent lane unless Developer reports isolation is not possible without deleting user-requested adjacent behavior.
- Do not choose Option C / scope expansion; there is no strong TASK_349A business authorization to absorb the adjacent residuals.

Allowed package-isolation work:

- Developer may edit only TASK_349A candidate files and Developer evidence to remove dependencies on excluded residuals.
- Developer must keep specified-LTR workbook authority preview behavior intact.
- Developer must preserve scope locks from sections 15 and 16.

Next role:

- Developer package-isolation fix pass.

Package-isolation decision evidence:

- `docs/lane_evidence/TASK_349A_specified-ltr-workbook-authority-preview_package_isolation_decision_planner.md`
