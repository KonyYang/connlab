# TASK_301 Fee Pricing Draft Persistence - Executable Plan

## Summary

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_301_FEE_PRICING_DRAFT_PERSISTENCE`, planned and awaiting explicit approval.

This plan is for review only. It does not approve implementation.

TASK_301 persists the Fee Evaluation page's local editable pricing draft and reloads it when the operator returns to the page. It builds directly on TASK_299 local edit state and TASK_300 export payload identity. The saved draft is tied to the current active Confirmed Matrix authority version and active fee rule version, so stale edits are not silently applied to a changed Matrix or changed pricing-rule baseline.

## Step 1 - Task Understanding

Goal:

- Save and reload operator-edited Fee Evaluation pricing values for the current project, active Confirmed Matrix, and active fee rule version.

Inputs:

- Current Fee Evaluation preview rows and summary values from the frontend.
- Current backend Matrix basic-fill row identities.
- Current active Confirmed Matrix id/revision.
- Active fee rule version id.

Outputs:

- Persisted pricing draft payload.
- Load API response for the current active Matrix and fee rule version.
- Frontend restored edit state and save status.

Modules involved:

- `backend/application`
- `backend/infrastructure/storage`
- `backend/api`
- `frontend/src/api/client.ts`
- `frontend/src/features/fee-evaluation`
- tests under `tests/unit`, `tests/integration`, and frontend Vitest files.

Not allowed:

- No TASK_302 rule-reference maintenance.
- No new Excel behavior beyond existing TASK_300 export consuming current page state.
- No project-output record changes.
- No StepInstance/execution/report/AI/multi-user scope.
- No stale edit merge across Matrix authority versions or fee rule versions.

## Design Decisions

### Persistence Shape

Use one persisted draft record per project, active Confirmed Matrix identity, and fee rule version.

Recommended table:

```text
fee_evaluation_pricing_draft_edits
  draft_edit_id TEXT PRIMARY KEY
  project_id TEXT NOT NULL
  confirmed_matrix_id TEXT NOT NULL
  confirmed_revision INTEGER NOT NULL
  fee_rule_version_id TEXT NOT NULL
  payload_json TEXT NOT NULL
  created_at TEXT NOT NULL
  updated_at TEXT NOT NULL
  UNIQUE(project_id, confirmed_matrix_id, confirmed_revision, fee_rule_version_id)
```

The payload JSON should store the same normalized application DTO shape already used by TASK_300:

- `rows`
- `manual_rows`
- `summary`

Rationale:

- TASK_301 is draft persistence, not analytical fee accounting.
- Row identity validation still happens before save.
- A JSON payload keeps V1 small and avoids premature row-level schema churn.
- A future TASK can normalize rows if search/reporting of fee edits becomes required.
- V1 save behavior overwrites the existing draft for the same `(project_id, confirmed_matrix_id, confirmed_revision, fee_rule_version_id)` tuple. It does not preserve historical draft edit versions.

### Stale Behavior

Load API V1 should return one of:

- `missing`: no saved draft for this project.
- `current`: saved draft matches current active Confirmed Matrix id/revision and active fee rule version id.
- `stale`: saved draft exists but does not match current active Confirmed Matrix id/revision or active fee rule version id.

The frontend applies only `current`.

Stale response should include enough metadata for operator copy:

- saved `confirmed_matrix_id`
- saved `confirmed_revision`
- saved `fee_rule_version_id`
- current `confirmed_matrix_id`
- current `confirmed_revision`
- current `fee_rule_version_id`

No merge or migration in TASK_301.

### Save Validation

Before persistence:

1. Resolve active Confirmed Matrix and build Matrix basic-fill rows using existing TASK_290/TASK_300 service path.
2. Validate edited row identities with existing `edited_row_lookup(...)`.
3. Validate manual row kinds with existing `validate_supported_manual_rows(...)`.
4. Reject duplicate row identities and duplicate manual rows.
5. Persist only after validation passes.

### Frontend Saved Payload Mapping

Saved payload rows use backend Matrix basic-fill identity. The frontend edit state uses local preview row ids as keys. TASK_301 implementation must add a dedicated frontend helper to bridge those shapes.

Recommended helper:

```text
hydrateFeeEvaluationPreviewEditsFromSavedDraft(previewRows, savedDraft)
```

Required behavior:

1. Build an index from current `previewRows` using the stable tuple:
   - `sourceLineId`
   - `confirmedGroupId`
   - `confirmedRowId`
   - `stepToken`
   - `stepIndex`
2. For each saved backend row, find the matching current preview row identity.
3. Convert matched saved rows into `FeeEvaluationPreviewEditState` keyed by the current frontend preview row `lineId`.
4. Convert saved manual rows, especially `report_preparation`, through the same current preview-row identity where available.
5. Convert saved summary values into `costPreviewValues`.
6. Do not apply unmatched saved rows.
7. If any saved rows are unmatched, surface stale/validation copy and keep unmatched values out of the page state.

Do not hydrate saved rows by `lineId` alone. `lineId` is a frontend working key and can diverge from backend basic-fill identity after step expansion or model changes.

### Frontend Save UX

Use an explicit `Save changes` button in the Fee Evaluation preview header or near the Fee Form action.

V1 state:

- `Unsaved changes`
- `Saved`
- `Saving`
- `Save failed`
- `Loaded saved draft`
- `Saved draft is stale for the current Matrix or fee rule version`

Do not autosave every cell edit in V1. The page is a dense pricing worksheet and explicit save avoids noisy API calls while users are still editing.

### Export Relationship

`Fee Form` export remains TASK_300 behavior:

- It exports the current page state.
- After TASK_301 load, saved values become the current page state.
- TASK_301 does not add server-side "export persisted draft without page payload" behavior.

No-body direct download compatibility remains unchanged.

## File-Level Design

### Backend Application

Add:

- `backend/application/fee_evaluation_pricing_draft_persistence_service.py`

Responsibilities:

- Define command/result dataclasses.
- Convert current API payload into `FeeEvaluationEditedExportValues`.
- Resolve current active Matrix basic-fill identity.
- Validate row/manual identities.
- Save/load current/stale edit payloads through a repository port.

Possible dataclasses:

```python
@dataclass(frozen=True, slots=True)
class SaveFeeEvaluationPricingDraftCommand:
    project_id: str
    edited_values: FeeEvaluationEditedExportValues

@dataclass(frozen=True, slots=True)
class FeeEvaluationPricingDraftSnapshot:
    project_id: str
    confirmed_matrix_id: str
    confirmed_revision: int
    fee_rule_version_id: str
    edited_values: FeeEvaluationEditedExportValues
    updated_at: datetime
```

Status result:

```python
Literal["missing", "current", "stale"]
```

No change to `FeeRuleMatchStatus`.

### Backend Storage

Update:

- `backend/infrastructure/storage/models.py`
- `backend/infrastructure/storage/database.py`

Add:

- `backend/infrastructure/storage/repositories/fee_evaluation_pricing_draft_edit.py`

Repository operations:

- `upsert_current(snapshot)`
- `get_latest_by_project(project_id)`
- optional `get_current(project_id, confirmed_matrix_id, confirmed_revision, fee_rule_version_id)` if simpler for implementation

Implementation details:

- New table creation through existing SQLAlchemy metadata/create-all path.
- Add a uniqueness constraint on `(project_id, confirmed_matrix_id, confirmed_revision, fee_rule_version_id)`.
- `upsert_current(snapshot)` should replace/overwrite the payload and `updated_at` for that same tuple.
- It should not create multiple current drafts for the same authority/rule context.
- If this repo uses explicit ensure helpers for schema evolution, add a minimal table-exists ensure path for existing local SQLite databases.
- Do not add unrelated migrations.

### Backend API

Add:

- `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`

Routes:

```text
GET /api/projects/{project_id}/confirmed-matrix/fee-evaluation/pricing-draft
PUT /api/projects/{project_id}/confirmed-matrix/fee-evaluation/pricing-draft
```

DTOs:

- Reuse or mirror TASK_300 edited row/manual/summary DTOs.
- If duplication is unavoidable, extract shared DTOs inside `backend/api` before wiring.
- Avoid circular imports between route modules.

Route responsibilities:

- Parse request.
- Call application service.
- Map domain/service errors to typed `404` / `400` / `409` where appropriate.
- Return business-readable details.

### Dependency Wiring

Update:

- `backend/api/dependencies.py`
- `backend/api/main.py`

Register repository/service route dependencies following existing patterns.

### Frontend API Client

Update:

- `frontend/src/api/client.ts`

Add:

- `getFeeEvaluationPricingDraft(projectId)`
- `saveFeeEvaluationPricingDraft(projectId, payload)`

Use existing TASK_300 request DTO type for payload shape when possible.

### Frontend Fee Evaluation Feature

Update:

- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
- tests for the page/model as needed.

Add helper in `feeEvaluationPreviewModel.ts` or a small sibling module:

- `hydrateFeeEvaluationPreviewEditsFromSavedDraft(...)`
- `buildFeeEvaluationPreviewStableIdentity(...)`

Behavior:

1. Load normal fee draft as today.
2. Load saved pricing draft for project/current Matrix/current fee rule version.
3. If response is `current`, apply saved row edits, manual row edits, and summary values.
4. If `missing`, keep defaults.
5. If `stale`, keep defaults and display concise stale copy.
6. On cell/summary edits, mark page `Unsaved changes`.
7. On `Save changes`, send `buildEditedExportPayload(previewRows, costPreviewValues)`.
8. On success, mark `Saved`.

Do not turn `Fee Form` into save+export automatically in TASK_301.

## Data Contract

The saved payload must include:

- Row identities:
  - `source_line_id`
  - `confirmed_group_id`
  - `confirmed_row_id`
  - `step_token`
  - `step_index`
- Editable row values:
  - `spend_time`
  - `unit_price`
  - `unit_type`
  - `units`
  - `base_fee`
  - `discount`
  - `testing_fee`
  - `notes`
- Manual rows:
  - `report_preparation`
- Summary:
  - `condition_confirmation_spend_time`
  - `external_cost`
  - `external_cost_note`
  - `lab_manpower_hourly_rate`

Testing Fee can be persisted as the frontend-calculated display value, but backend should continue to treat row formula behavior as TASK_300 export responsibility.

## Risks

- Row identity drift:
  - Mitigation: use existing TASK_300 identity helper and validation before saving.
- Stale edits after Matrix revision or fee rule version switch:
  - Mitigation: bind to active Confirmed Matrix id/revision and active fee rule version id, then never apply stale payload automatically.
- Frontend hydration mismatch:
  - Mitigation: hydrate saved rows through current preview-row stable identity tuple, reject unmatched saved rows from page state, and test unmatched-row copy.
- JSON payload hides queryable fields:
  - Accepted for V1 draft persistence. Future normalization can be a separate task if needed.
- Frontend duplicate source of truth:
  - Mitigation: saved payload only initializes current page state; active in-page state remains the source for export.

## Test Plan

Backend unit:

- save/load current Matrix and fee rule version draft
- missing draft returns `missing`
- stale saved Matrix returns `stale`
- stale saved fee rule version returns `stale`
- duplicate row identity rejected
- unknown row identity rejected
- row Notes and External Cost note round-trip

Backend integration/API:

- GET missing
- PUT save then GET current
- GET stale when active Matrix revision changes or repository has older metadata
- GET stale when saved fee rule version differs from current active fee rule version
- invalid payload returns actionable 400/409

Frontend:

- current saved draft hydrates editable row cells and summary controls
- saved backend row identities map to current frontend `lineId` keys through the stable identity tuple
- unmatched saved rows are not applied and show stale/validation copy
- stale saved draft shows stale copy and keeps current defaults
- save button sends TASK_300 edited payload
- save success and error states render
- Fee Form export after hydration still calls TASK_300 download path with current state

Regression:

```text
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py -q
py -m pytest tests/integration/test_fee_evaluation_pricing_draft_api.py -q
py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_fee_evaluation_workbook_gateway.py tests/integration/test_confirmed_matrix_fee_file_download_api.py -q
cd frontend; npm test -- --run FeeEvaluation ProjectWorkbench --watch=false
cd frontend; npm run build
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or project_workbench"
git diff --check
```

## Self-Check Before Implementation

- No TASK_302 reference-update workflow.
- No new Excel gateway behavior.
- No output-record freshness change.
- No stale edit merge.
- No StepInstance or execution persistence.
- No hardcoded absolute template/reference path.
- No broad frontend page growth without feature helpers.
