# TASK_314B Fee Evaluation Background Draft Persistence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Fee Evaluation pricing draft autosave and discard so Fee edits persist as non-authority drafts and Confirm Fee only uses the latest saved pricing draft.

**Architecture:** Reuse the existing Fee Evaluation pricing draft persistence service and API as the save/restore authority. Add only the missing discard path in backend service/repository/API, then move the frontend from manual save and implicit confirm-save to debounced autosave plus confirm gating. Confirmed Fee remains the authority version and is still created only through `POST /confirmed-fee/versions`.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy, Pydantic v2, React, TypeScript, Vitest, pytest.

---

## Current Phase And Permission Gate

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Current task status:

```text
TASK_314B_FEE_EVALUATION_BACKGROUND_DRAFT_PERSISTENCE is complete.
```

Implementation was started only after the user explicitly approved TASK_314B. TASK_314B is not required before TASK_315 and completion of TASK_314B does not approve TASK_314C or TASK_315.

## Task Understanding

### Goal

Make Fee Evaluation pricing edits behave like a controlled non-authority draft:

- save in the background,
- restore on re-entry,
- discard explicitly,
- confirm only from a saved draft id,
- remove manual `Save changes` from the normal path.

### Input Data

- Current active Confirmed Matrix-backed Fee Evaluation draft from `GET /confirmed-matrix/fee-draft`.
- Existing pricing draft load state from `GET /confirmed-matrix/fee-evaluation/pricing-draft`.
- Operator edits in `FeeEvaluationReviewExportPage`:
  - row pricing fields,
  - manual trailing row fields,
  - condition confirmation,
  - external cost,
  - external cost note,
  - lab manpower hourly rate,
  - confirmed-by text for authority confirmation.

### Output Data

- Current saved pricing draft row in SQLite, represented by `FeeEvaluationPricingDraftEditModel`.
- Pricing draft load/discard DTOs.
- Confirmed Fee authority version only when the operator clicks `Confirm Fee`.

### Involved Modules

- Backend route: `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`
- Backend application service: `backend/application/fee_evaluation_pricing_draft_persistence_service.py`
- Backend repository: `backend/infrastructure/storage/repositories/fee_evaluation_pricing_draft_edit.py`
- Frontend API client: `frontend/src/api/client.ts`
- Frontend page: `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
- Frontend preview table: `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
- Frontend model/tests: `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`, `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts`
- Backend tests: `tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py`, `tests/integration/test_fee_evaluation_pricing_draft_api.py`, `tests/unit/test_confirmed_fee_version_service.py`, `tests/integration/test_confirmed_fee_version_api.py`

### Not Allowed

- Do not modify Matrix Editor.
- Do not implement TASK_315 Matrix-to-Fee rebase.
- Do not change fee calculation rules.
- Do not change Excel templates or workbook generation.
- Do not change ProjectOutputRecord or Project Folder Required forms behavior.
- Do not add StepInstance/report/AI/permissions/multi-user scope.

## Current Code Reality

Existing save/restore:

```text
GET /api/projects/{project_id}/confirmed-matrix/fee-evaluation/pricing-draft
PUT /api/projects/{project_id}/confirmed-matrix/fee-evaluation/pricing-draft
```

Existing frontend behavior:

- Loads current pricing draft when page opens.
- Hydrates current saved pricing draft payload into preview rows.
- Shows manual `Save changes`.
- Saves immediately inside `handleConfirmFee()` before calling `confirmFeeVersion(...)`.
- Tracks `latestSavedPricingDraftId`, `pricingDraftLoadStatus`, and `pricingDraftDirtySinceConfirm`.

Existing missing behavior:

- No backend discard endpoint.
- No repository delete method.
- Current repository load uses latest-by-project ordering, so a newer stale row can hide an older current-context row if multiple Matrix/Fee-rule contexts exist for one project.
- No debounced autosave.
- Confirm Fee can still save as part of confirm instead of requiring a previously saved autosave token.
- Cancel/back does not discard the pricing draft.

## Design

### Backend Data Structure

No schema migration is required for V1. Use existing `FeeEvaluationPricingDraftEditModel` rows.

Add command/result dataclasses:

```python
@dataclass(frozen=True, slots=True)
class DiscardFeeEvaluationPricingDraftCommand:
    project_id: str
    expected_pricing_draft_edit_id: str | None = None
    expected_confirmed_matrix_id: str | None = None
    expected_confirmed_revision: int | None = None
    expected_fee_rule_version_id: str | None = None


@dataclass(frozen=True, slots=True)
class FeeEvaluationPricingDraftDiscardResult:
    discarded: bool
    current_context: FeeEvaluationPricingDraftContext
```

Extend store protocol:

```python
def get_by_context(
    self,
    *,
    project_id: str,
    confirmed_matrix_id: str,
    confirmed_revision: int,
    fee_rule_version_id: str,
) -> FeeEvaluationPricingDraftSnapshot | None:
    """Return the pricing draft for the exact project/context tuple."""


def delete_current(
    self,
    *,
    project_id: str,
    confirmed_matrix_id: str,
    confirmed_revision: int,
    fee_rule_version_id: str,
) -> bool:
    """Delete one current pricing draft by exact project/context tuple."""
```

Update service load to use `get_by_context(...)` after building current context. If no row exists for the exact current context, return `status="missing"` even when older/newer rows for another context exist. If a future diagnostic wants to show stale draft presence, use a separate boolean/warning path; do not allow latest-by-project to decide the loaded payload.

### Backend API

Add:

```text
DELETE /api/projects/{project_id}/confirmed-matrix/fee-evaluation/pricing-draft
```

Request:

```python
class FeeEvaluationPricingDraftDiscardRequest(BaseModel):
    expected_pricing_draft_edit_id: str | None = None
    expected_confirmed_matrix_id: str | None = None
    expected_confirmed_revision: int | None = None
    expected_fee_rule_version_id: str | None = None
```

Response:

```python
class FeeEvaluationPricingDraftDiscardResponse(BaseModel):
    discarded: bool
    current_confirmed_matrix_id: str
    current_confirmed_revision: int
    current_fee_rule_version_id: str
```

Conflict behavior:

- Missing project/current Matrix remains existing 404/400 behavior from current basic-fill context build.
- Mismatched expected draft id/context returns `409` with code `fee_pricing_draft_conflict`.
- Missing current draft returns `200` with `discarded=false`.

### Frontend State

Replace manual save-centered state with autosave-aware state:

```ts
type FeePricingDraftSaveState =
  | { kind: "loading" }
  | { kind: "idle"; message: string | null }
  | { kind: "dirty" }
  | { kind: "saving" }
  | { kind: "saved"; message: string }
  | { kind: "stale"; message: string }
  | { kind: "error"; message: string };
```

The type already exists. Keep it and refine transitions.

Add refs/state in `FeeEvaluationReviewExportPage.tsx`:

```ts
const autosaveTimeoutRef = useRef<number | null>(null);
const autosaveGenerationRef = useRef(0);
const autosaveInFlightRef = useRef<Promise<FeeEvaluationPricingDraftResponse | null> | null>(null);
const autosaveAbortControllerRef = useRef<AbortController | null>(null);
const latestAutosaveResultRef = useRef<FeeEvaluationPricingDraftResponse | null>(null);
const discardingRef = useRef(false);
const [savedLocalPricingSignature, setSavedLocalPricingSignature] = useState<string | null>(null);
const [baselinePricingSignature, setBaselinePricingSignature] = useState<string | null>(null);
const [hasUserEditedPricingDraft, setHasUserEditedPricingDraft] = useState(false);
const [needsInitialSeedSave, setNeedsInitialSeedSave] = useState(false);
const [isDiscardingPricingDraft, setIsDiscardingPricingDraft] = useState(false);
```

Build a stable local signature from:

```ts
JSON.stringify(buildEditedExportPayload(previewRows, costPreviewValues))
```

Local-change semantics must not use `savedLocalPricingSignature !== currentPricingDraftSignature` alone. Use these signals:

- `baselinePricingSignature`: set after Fee defaults load, after saved draft hydration, and after successful seed save.
- `savedLocalPricingSignature`: set only after successful load/autosave/seed save.
- `hasUserEditedPricingDraft`: set by user edit handlers only; initial load and saved draft hydration must not set it.
- `needsInitialSeedSave`: set when pricing draft load returns `status="missing"` and Fee defaults are ready.

`hasPricingDraftLocalChanges` means:

```ts
const hasPricingDraftLocalChanges =
  hasUserEditedPricingDraft &&
  savedLocalPricingSignature !== currentPricingDraftSignature;
```

The controlled initial seed save path uses `needsInitialSeedSave`, not `hasPricingDraftLocalChanges`, so a missing draft with unchanged defaults can still create the saved draft id required by Confirm Fee.

### Frontend API Client

Add:

```ts
export type FeeEvaluationPricingDraftDiscardRequest = {
  expected_pricing_draft_edit_id?: string | null;
  expected_confirmed_matrix_id?: string | null;
  expected_confirmed_revision?: number | null;
  expected_fee_rule_version_id?: string | null;
};

export type FeeEvaluationPricingDraftDiscardResponse = {
  discarded: boolean;
  current_confirmed_matrix_id: string;
  current_confirmed_revision: number;
  current_fee_rule_version_id: string;
};

export function discardFeeEvaluationPricingDraft(
  projectId: string,
  input: FeeEvaluationPricingDraftDiscardRequest = {}
): Promise<FeeEvaluationPricingDraftDiscardResponse> {
  return requestJson<FeeEvaluationPricingDraftDiscardResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-matrix/fee-evaluation/pricing-draft`,
    {
      method: "DELETE",
      body: JSON.stringify(input),
    }
  );
}
```

### UX Rules

ConnLab product UI is restrained and operational. Do not add a new modal-heavy workflow. Use the existing page header/confirm strip:

- Remove normal-flow `Save changes` button.
- Keep save status visible via `FeePricingDraftSaveStatus`.
- `Confirm Fee` disabled reason must be visible via `title` and existing status text/error area.
- `Back to Workbench` should prompt only when there is a current local/saved draft to discard.
- Discard failure must keep the operator in the page with a business-readable message.

## File Map

### Backend

- Modify `backend/application/fee_evaluation_pricing_draft_persistence_service.py`
  - add discard command/result,
  - add `discard(...)`,
  - update load to query the exact current context,
  - validate expected draft/context tokens.
- Modify `backend/infrastructure/storage/repositories/fee_evaluation_pricing_draft_edit.py`
  - add exact-context `get_by_context(...)`,
  - add exact-context `delete_current(...)`.
- Modify `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`
  - add request/response models,
  - add DELETE route,
  - map conflicts to HTTP 409.
- Modify `tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py`
  - add exact-context restore and discard unit coverage.
- Modify `tests/integration/test_fee_evaluation_pricing_draft_api.py`
  - add exact-context restore and DELETE route coverage.

### Frontend

- Modify `frontend/src/api/client.ts`
  - add discard DTOs and API client function.
- Modify `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
  - add autosave state/refs/effect,
  - remove implicit save from `handleConfirmFee`,
  - add discard/back behavior,
  - update confirm blocker.
- Modify `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
  - remove `onSavePricingDraft`,
  - remove `Save changes` button from normal controls.
- Modify `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`
  - add autosave, confirm gating, discard success/failure tests,
  - update old manual save and confirm-save tests.
- Modify `tests/unit/test_frontend_shell_files.py` only if static guards still assert `Save changes` or old save wiring.

## Implementation Tasks

### Task 1: Backend Discard Service

**Files:**

- Modify: `backend/application/fee_evaluation_pricing_draft_persistence_service.py`
- Test: `tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py`

- [ ] **Step 1: Add failing unit tests for discard**

Add tests:

```python
def test_discard_current_pricing_draft_deletes_matching_context() -> None:
    store = _DraftStore(saved_snapshot=_snapshot())
    service = _service(store=store)

    result = service.discard(
        DiscardFeeEvaluationPricingDraftCommand(
            project_id="P1",
            expected_pricing_draft_edit_id="fed-1",
            expected_confirmed_matrix_id="cmv-1",
            expected_confirmed_revision=1,
            expected_fee_rule_version_id="fee_rules_v2026_06_03",
        )
    )

    assert result.discarded is True
    assert store.deleted_context == (
        "P1",
        "cmv-1",
        1,
        "fee_rules_v2026_06_03",
    )


def test_discard_rejects_mismatched_pricing_draft_id() -> None:
    service = _service(store=_DraftStore(saved_snapshot=_snapshot()))

    with pytest.raises(FeeEvaluationPricingDraftConflictError):
        service.discard(
            DiscardFeeEvaluationPricingDraftCommand(
                project_id="P1",
                expected_pricing_draft_edit_id="fed-other",
            )
        )


def test_load_uses_current_context_when_newer_stale_row_exists() -> None:
    store = _DraftStore(
        saved_snapshot=None,
        context_snapshots={
            ("P1", "cmv-1", 1, "fee_rules_v2026_06_03"): _snapshot(
                updated_at=datetime(2026, 6, 14, 9, 0, 0)
            ),
            ("P1", "old-cmv", 1, "fee_rules_v2026_06_03"): _snapshot(
                draft_edit_id="fed-stale",
                confirmed_matrix_id="old-cmv",
                updated_at=datetime(2026, 6, 14, 10, 0, 0),
            ),
        },
    )
    service = _service(store=store)

    result = service.load(project_id="P1")

    assert result.status == "current"
    assert result.saved_draft_edit_id == "fed-1"


def test_discard_uses_current_context_when_newer_stale_row_exists() -> None:
    store = _DraftStore(
        saved_snapshot=None,
        context_snapshots={
            ("P1", "cmv-1", 1, "fee_rules_v2026_06_03"): _snapshot(
                updated_at=datetime(2026, 6, 14, 9, 0, 0)
            ),
            ("P1", "old-cmv", 1, "fee_rules_v2026_06_03"): _snapshot(
                draft_edit_id="fed-stale",
                confirmed_matrix_id="old-cmv",
                updated_at=datetime(2026, 6, 14, 10, 0, 0),
            ),
        },
    )
    service = _service(store=store)

    result = service.discard(DiscardFeeEvaluationPricingDraftCommand(project_id="P1"))

    assert result.discarded is True
    assert store.deleted_context == ("P1", "cmv-1", 1, "fee_rules_v2026_06_03")
```

- [ ] **Step 2: Run unit tests and verify red**

Run:

```powershell
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py -q
```

Expected: fails because discard command/error/service method do not exist.

- [ ] **Step 3: Implement discard command/result/error**

Add:

```python
class FeeEvaluationPricingDraftConflictError(ValueError):
    """Raised when pricing draft discard tokens do not match current context."""
```

Add dataclasses from the Design section.

- [ ] **Step 4: Extend store protocol and service**

Implement:

```python
def load(self, project_id: str) -> FeeEvaluationPricingDraftLoadResult:
    basic_fill = self._build_basic_fill(project_id)
    context = _context_from_basic_fill(basic_fill)
    snapshot = self._draft_store.get_by_context(
        project_id=context.project_id,
        confirmed_matrix_id=context.confirmed_matrix_id,
        confirmed_revision=context.confirmed_revision,
        fee_rule_version_id=context.fee_rule_version_id,
    )
    if snapshot is None:
        return FeeEvaluationPricingDraftLoadResult(
            status="missing",
            current_context=context,
            saved_draft_edit_id=None,
            payload=None,
        )
    return _load_result_from_snapshot(snapshot, context)


def discard(
    self, command: DiscardFeeEvaluationPricingDraftCommand
) -> FeeEvaluationPricingDraftDiscardResult:
    basic_fill = self._build_basic_fill(command.project_id)
    context = _context_from_basic_fill(basic_fill)
    snapshot = self._draft_store.get_by_context(
        project_id=context.project_id,
        confirmed_matrix_id=context.confirmed_matrix_id,
        confirmed_revision=context.confirmed_revision,
        fee_rule_version_id=context.fee_rule_version_id,
    )
    if snapshot is None:
        return FeeEvaluationPricingDraftDiscardResult(
            discarded=False,
            current_context=context,
        )
    _validate_discard_expectations(command, snapshot, context)
    discarded = self._draft_store.delete_current(
        project_id=context.project_id,
        confirmed_matrix_id=context.confirmed_matrix_id,
        confirmed_revision=context.confirmed_revision,
        fee_rule_version_id=context.fee_rule_version_id,
    )
    return FeeEvaluationPricingDraftDiscardResult(
        discarded=discarded,
        current_context=context,
    )
```

Add helper:

```python
def _validate_discard_expectations(
    command: DiscardFeeEvaluationPricingDraftCommand,
    snapshot: FeeEvaluationPricingDraftSnapshot,
    context: FeeEvaluationPricingDraftContext,
) -> None:
    if command.expected_pricing_draft_edit_id and (
        command.expected_pricing_draft_edit_id != snapshot.draft_edit_id
    ):
        raise FeeEvaluationPricingDraftConflictError(
            "Pricing draft changed before discard. Reload Fee Evaluation."
        )
    if command.expected_confirmed_matrix_id and (
        command.expected_confirmed_matrix_id != context.confirmed_matrix_id
    ):
        raise FeeEvaluationPricingDraftConflictError(
            "Pricing draft Matrix context changed before discard."
        )
    if command.expected_confirmed_revision is not None and (
        command.expected_confirmed_revision != context.confirmed_revision
    ):
        raise FeeEvaluationPricingDraftConflictError(
            "Pricing draft Matrix revision changed before discard."
        )
    if command.expected_fee_rule_version_id and (
        command.expected_fee_rule_version_id != context.fee_rule_version_id
    ):
        raise FeeEvaluationPricingDraftConflictError(
            "Pricing draft fee rule version changed before discard."
        )
```

- [ ] **Step 5: Run unit tests and verify green**

Run:

```powershell
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py -q
```

Expected: all tests pass.

### Task 2: Backend Repository And API Route

**Files:**

- Modify: `backend/infrastructure/storage/repositories/fee_evaluation_pricing_draft_edit.py`
- Modify: `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`
- Test: `tests/integration/test_fee_evaluation_pricing_draft_api.py`

- [ ] **Step 1: Add failing API tests**

Add tests:

```python
def test_pricing_draft_delete_discards_current_payload() -> None:
    service = _Service(_current_result(_payload_values()))
    app.dependency_overrides[get_fee_evaluation_pricing_draft_service] = lambda: service
    try:
        response = TestClient(app).request(
            "DELETE",
            "/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft",
            json={
                "expected_pricing_draft_edit_id": "fed-1",
                "expected_confirmed_matrix_id": "cmv-1",
                "expected_confirmed_revision": 1,
                "expected_fee_rule_version_id": "fee_rules_v2026_06_03",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["discarded"] is True


def test_pricing_draft_delete_maps_conflict_to_409() -> None:
    app.dependency_overrides[get_fee_evaluation_pricing_draft_service] = lambda: _FailingService(
        FeeEvaluationPricingDraftConflictError("Pricing draft changed before discard.")
    )
    try:
        response = TestClient(app).request(
            "DELETE",
            "/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft",
            json={"expected_pricing_draft_edit_id": "fed-other"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "fee_pricing_draft_conflict"


def test_pricing_draft_restore_uses_current_context_when_newer_stale_row_exists() -> None:
    current_row = _pricing_draft_row(
        project_id="P1",
        confirmed_matrix_id="cmv-current",
        confirmed_revision=2,
        fee_rule_version_id="fee_rules_v2026_06_03",
        draft_edit_id="fed-current",
        updated_at=datetime(2026, 6, 14, 9, 0, 0),
    )
    stale_newer_row = _pricing_draft_row(
        project_id="P1",
        confirmed_matrix_id="cmv-old",
        confirmed_revision=1,
        fee_rule_version_id="fee_rules_v2026_06_03",
        draft_edit_id="fed-stale",
        updated_at=datetime(2026, 6, 14, 10, 0, 0),
    )
    _seed_pricing_draft_rows(current_row, stale_newer_row)
    _seed_current_basic_fill_context(
        project_id="P1",
        confirmed_matrix_id="cmv-current",
        confirmed_revision=2,
        fee_rule_version_id="fee_rules_v2026_06_03",
    )

    response = TestClient(app).get(
        "/api/projects/P1/confirmed-matrix/fee-evaluation/pricing-draft"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "current"
    assert response.json()["saved_draft_edit_id"] == "fed-current"
```

- [ ] **Step 2: Run API tests and verify red**

Run:

```powershell
py -m pytest tests/integration/test_fee_evaluation_pricing_draft_api.py -q
```

Expected: fails because DELETE route and service port method do not exist.

- [ ] **Step 3: Implement repository exact-context read and delete**

Add:

```python
def get_by_context(
    self,
    *,
    project_id: str,
    confirmed_matrix_id: str,
    confirmed_revision: int,
    fee_rule_version_id: str,
) -> FeeEvaluationPricingDraftSnapshot | None:
    row = self._session.scalar(
        select(FeeEvaluationPricingDraftEditModel).where(
            FeeEvaluationPricingDraftEditModel.project_id == project_id,
            FeeEvaluationPricingDraftEditModel.confirmed_matrix_id == confirmed_matrix_id,
            FeeEvaluationPricingDraftEditModel.confirmed_revision == confirmed_revision,
            FeeEvaluationPricingDraftEditModel.fee_rule_version_id == fee_rule_version_id,
        )
    )
    return _snapshot_from_model(row) if row is not None else None


def delete_current(
    self,
    *,
    project_id: str,
    confirmed_matrix_id: str,
    confirmed_revision: int,
    fee_rule_version_id: str,
) -> bool:
    row = self._session.scalar(
        select(FeeEvaluationPricingDraftEditModel).where(
            FeeEvaluationPricingDraftEditModel.project_id == project_id,
            FeeEvaluationPricingDraftEditModel.confirmed_matrix_id == confirmed_matrix_id,
            FeeEvaluationPricingDraftEditModel.confirmed_revision == confirmed_revision,
            FeeEvaluationPricingDraftEditModel.fee_rule_version_id == fee_rule_version_id,
        )
    )
    if row is None:
        return False
    self._session.delete(row)
    self._session.flush()
    return True
```

Keep `get_latest_by_project(...)` only if another existing caller still needs it. TASK_314B load/discard must use `get_by_context(...)`.

- [ ] **Step 4: Implement API route**

Add service port method:

```python
def discard(
    self, command: DiscardFeeEvaluationPricingDraftCommand
) -> FeeEvaluationPricingDraftDiscardResult:
    """Discard pricing draft state for one project."""
```

Add DELETE route using request/response DTOs from Design.

Map conflicts:

```python
except FeeEvaluationPricingDraftConflictError as exc:
    raise HTTPException(
        status_code=409,
        detail={"code": "fee_pricing_draft_conflict", "message": str(exc)},
    ) from exc
```

- [ ] **Step 5: Run backend pricing draft tests**

Run:

```powershell
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q
```

Expected: all tests pass.

### Task 3: Frontend API Client And Manual Save Removal

**Files:**

- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
- Modify: `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
- Test: `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`

- [ ] **Step 1: Add failing frontend test that Save changes is absent**

Add:

```ts
it("does not show manual Save changes in the normal Fee Evaluation flow", async () => {
  render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />);
  await screen.findByText("Fee Evaluation");
  expect(screen.queryByRole("button", { name: "Save changes" })).toBeNull();
});
```

- [ ] **Step 2: Run frontend test and verify red**

Run:

```powershell
cd frontend
npm test -- FeeEvaluationReviewExportPage
```

Expected: fails because `Save changes` is still present.

- [ ] **Step 3: Add discard API client**

Implement DTOs and `discardFeeEvaluationPricingDraft(...)` exactly as shown in the Frontend API Client section.

Also extend `saveFeeEvaluationPricingDraft(...)` to accept an optional request option:

```ts
export function saveFeeEvaluationPricingDraft(
  projectId: string,
  input: FeeEvaluationEditedFileExportRequest,
  options?: { signal?: AbortSignal }
): Promise<FeeEvaluationPricingDraftResponse> {
  return apiFetch(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-matrix/fee-evaluation/pricing-draft`,
    {
      method: "PUT",
      body: JSON.stringify(input),
      signal: options?.signal,
    }
  );
}
```

Keep existing call sites source-compatible by making `options` optional.

- [ ] **Step 4: Remove manual save prop/button**

In `FeeEvaluationPreviewTable.tsx`:

- remove `onSavePricingDraft` from props,
- remove the `Save changes` button,
- keep `FeePricingDraftSaveStatus`.

In `FeeEvaluationReviewExportPage.tsx`:

- remove `onSavePricingDraft={handleSavePricingDraft}`,
- keep `handleSavePricingDraft` only if reused internally by autosave, otherwise replace it in later tasks with shared save helper.

- [ ] **Step 5: Run frontend test and verify green**

Run:

```powershell
cd frontend
npm test -- FeeEvaluationReviewExportPage
```

Expected: test passes or only later autosave tests fail because behavior is not implemented yet.

### Task 4: Frontend Autosave

**Files:**

- Modify: `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
- Test: `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`

- [ ] **Step 1: Add failing autosave tests**

Add:

```ts
it("autosaves pricing draft edits after debounce", async () => {
  render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />);
  fireEvent.change(await screen.findByLabelText("External Cost preview"), {
    target: { value: "250" },
  });

  expect(apiMocks.saveFeeEvaluationPricingDraft).not.toHaveBeenCalled();
  await waitFor(
    () => expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledTimes(1),
    { timeout: 1600 }
  );
  expect(apiMocks.saveFeeEvaluationPricingDraft.mock.calls[0][1].summary.external_cost).toBe("250");
});


it("does not autosave immediately during initial saved draft hydration", async () => {
  apiMocks.getFeeEvaluationPricingDraft.mockResolvedValueOnce(savedPricingDraftResponse());
  render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />);

  await screen.findByText("Loaded saved pricing draft.");
  await new Promise((resolve) => setTimeout(resolve, 900));
  expect(apiMocks.saveFeeEvaluationPricingDraft).not.toHaveBeenCalled();
});


it("seeds a missing pricing draft from ready default values without user edits", async () => {
  apiMocks.getFeeEvaluationPricingDraft.mockResolvedValueOnce(missingPricingDraftResponse());
  apiMocks.saveFeeEvaluationPricingDraft.mockResolvedValueOnce({
    ...currentPricingDraftResponse(),
    saved_draft_edit_id: "fed-seeded",
  });

  render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />);

  await waitFor(
    () => expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledTimes(1),
    { timeout: 1600 }
  );
  expect(screen.getByRole("button", { name: "Confirm Fee" })).not.toBeDisabled();
});
```

- [ ] **Step 2: Run frontend tests and verify red**

Run:

```powershell
cd frontend
npm test -- FeeEvaluationReviewExportPage
```

Expected: autosave and seed-save tests fail because saves only happen on manual save/confirm.

- [ ] **Step 3: Build shared save helper**

Inside `FeeEvaluationReviewExportPage.tsx`, add:

```ts
function buildCurrentPricingDraftPayload(): FeeEvaluationEditedFileExportRequest {
  return buildEditedExportPayload(previewRows, costPreviewValues);
}
```

Use this helper for autosave and any remaining explicit save path.

- [ ] **Step 4: Add autosave and seed-save effect**

Implement:

```ts
useEffect(() => {
  if (autosaveTimeoutRef.current !== null) {
    window.clearTimeout(autosaveTimeoutRef.current);
    autosaveTimeoutRef.current = null;
  }
  if (
    draftState.kind !== "ready" ||
    (!hasPricingDraftLocalChanges && !needsInitialSeedSave) ||
    discardingRef.current ||
    isDiscardingPricingDraft
  ) {
    return;
  }
  const generation = autosaveGenerationRef.current + 1;
  autosaveGenerationRef.current = generation;
  const payload = buildCurrentPricingDraftPayload();
  const signature = JSON.stringify(payload);
  const isSeedSave = needsInitialSeedSave && !hasUserEditedPricingDraft;
  if (!isSeedSave) {
    setSaveState({ kind: "dirty" });
  }
  autosaveTimeoutRef.current = window.setTimeout(() => {
    if (discardingRef.current) {
      return;
    }
    setSaveState({ kind: "saving" });
    const abortController = new AbortController();
    autosaveAbortControllerRef.current = abortController;
    const saveRequest = saveFeeEvaluationPricingDraft(projectId, payload, {
      signal: abortController.signal,
    })
      .then((result) => {
        latestAutosaveResultRef.current = result;
        if (autosaveGenerationRef.current === generation && !discardingRef.current) {
          if (result.status === "current") {
            setLatestSavedPricingDraftId(result.saved_draft_edit_id ?? null);
            setPricingDraftLoadStatus("current");
            setSavedLocalPricingSignature(signature);
            setBaselinePricingSignature(signature);
            setHasUserEditedPricingDraft(false);
            setNeedsInitialSeedSave(false);
            setPricingDraftDirtySinceConfirm(false);
            setSaveState({ kind: "saved", message: "Saved pricing draft." });
          } else {
            setLatestSavedPricingDraftId(null);
            setPricingDraftLoadStatus("stale");
            setSaveState({
              kind: "stale",
              message: "Saved draft is not current for this Matrix or fee rule version.",
            });
          }
        }
        return result;
      })
      .catch((error) => {
        if (autosaveGenerationRef.current === generation && !discardingRef.current) {
          if (error instanceof DOMException && error.name === "AbortError") {
            return null;
          }
          setSaveState({
            kind: "error",
            message: error instanceof ApiRequestError ? error.message : "Unable to save pricing draft.",
          });
        }
        return null;
      })
      .finally(() => {
        if (autosaveInFlightRef.current === saveRequest) {
          autosaveInFlightRef.current = null;
        }
        if (autosaveAbortControllerRef.current === abortController) {
          autosaveAbortControllerRef.current = null;
        }
      });
    autosaveInFlightRef.current = saveRequest;
  }, 800);
  return () => {
    if (autosaveTimeoutRef.current !== null) {
      window.clearTimeout(autosaveTimeoutRef.current);
      autosaveTimeoutRef.current = null;
    }
  };
}, [
  currentPricingDraftSignature,
  draftState.kind,
  hasPricingDraftLocalChanges,
  hasUserEditedPricingDraft,
  isDiscardingPricingDraft,
  needsInitialSeedSave,
  projectId,
]);
```

The exact dependency list must include all values used by `buildCurrentPricingDraftPayload()`. Keep it explicit and verify with `npm run build`.

- [ ] **Step 5: Update load hydration signatures**

When a current saved draft is loaded and hydrated:

```ts
const hydratedPayload = buildEditedExportPayload(
  applyFeeEvaluationPreviewEdits(sourcePreviewRows, hydrated.edits),
  hydrated.costPreviewValues
);
setSavedLocalPricingSignature(JSON.stringify(hydratedPayload));
setBaselinePricingSignature(JSON.stringify(hydratedPayload));
setHasUserEditedPricingDraft(false);
setNeedsInitialSeedSave(false);
```

When pricing draft load returns `status="missing"` after Fee defaults are ready:

```ts
const defaultPayload = buildEditedExportPayload(previewRowsFromFeeDraft, defaultCostPreviewValues);
const defaultSignature = JSON.stringify(defaultPayload);
setBaselinePricingSignature(defaultSignature);
setSavedLocalPricingSignature(null);
setHasUserEditedPricingDraft(false);
setNeedsInitialSeedSave(true);
```

User edit handlers must call `setHasUserEditedPricingDraft(true)`.

When missing/stale/error:

```ts
setSavedLocalPricingSignature(null);
```

- [ ] **Step 6: Run frontend tests**

Run:

```powershell
cd frontend
npm test -- FeeEvaluationReviewExportPage
```

Expected: autosave tests pass.

### Task 5: Confirm Fee Gating

**Files:**

- Modify: `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
- Test: `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`

- [ ] **Step 1: Add failing confirm gating tests**

Add:

```ts
it("blocks Confirm Fee until the edited pricing payload autosaves", async () => {
  render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />);
  fireEvent.change(await screen.findByLabelText("External Cost preview"), {
    target: { value: "275" },
  });
  expect(screen.getByRole("button", { name: "Confirm Fee" })).toBeDisabled();

  await waitFor(
    () => expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledTimes(1),
    { timeout: 1600 }
  );
  expect(screen.getByRole("button", { name: "Confirm Fee" })).not.toBeDisabled();
});


it("confirms Fee with the latest autosaved pricing draft id without saving again", async () => {
  apiMocks.saveFeeEvaluationPricingDraft.mockResolvedValueOnce({
    ...currentPricingDraftResponse(),
    saved_draft_edit_id: "fed-autosaved",
  });
  render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />);
  fireEvent.change(await screen.findByLabelText("External Cost preview"), {
    target: { value: "300" },
  });
  await waitFor(
    () => expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledTimes(1),
    { timeout: 1600 }
  );

  fireEvent.click(screen.getByRole("button", { name: "Confirm Fee" }));

  await waitFor(() => expect(apiMocks.confirmFeeVersion).toHaveBeenCalledTimes(1));
  expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledTimes(1);
  expect(apiMocks.confirmFeeVersion).toHaveBeenCalledWith("P1", expect.objectContaining({
    expected_pricing_draft_edit_id: "fed-autosaved",
  }));
});


it("confirms default unchanged Fee after missing draft seed save", async () => {
  apiMocks.getFeeEvaluationPricingDraft.mockResolvedValueOnce(missingPricingDraftResponse());
  apiMocks.saveFeeEvaluationPricingDraft.mockResolvedValueOnce({
    ...currentPricingDraftResponse(),
    saved_draft_edit_id: "fed-seeded",
  });

  render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />);

  await waitFor(
    () => expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledTimes(1),
    { timeout: 1600 }
  );
  fireEvent.change(screen.getByLabelText("Confirmed by"), {
    target: { value: "Operator A" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Confirm Fee" }));

  await waitFor(() => expect(apiMocks.confirmFeeVersion).toHaveBeenCalledTimes(1));
  expect(apiMocks.confirmFeeVersion).toHaveBeenCalledWith("P1", expect.objectContaining({
    expected_pricing_draft_edit_id: "fed-seeded",
  }));
});
```

- [ ] **Step 2: Run tests and verify red**

Run:

```powershell
cd frontend
npm test -- FeeEvaluationReviewExportPage
```

Expected: fails because confirm still saves inside `handleConfirmFee`.

- [ ] **Step 3: Extend confirm blocker**

Change `confirmFeeBlocker` input to include:

```ts
saveState: FeePricingDraftSaveState;
latestSavedPricingDraftId: string | null;
currentPricingDraftSignature: string;
savedLocalPricingSignature: string | null;
isDiscardingPricingDraft: boolean;
```

Add blocker checks:

```ts
if (input.isDiscardingPricingDraft) return "Discarding pricing draft.";
if (input.saveState.kind === "dirty") return "Saving pricing draft before confirm.";
if (input.saveState.kind === "saving") return "Saving pricing draft before confirm.";
if (input.saveState.kind === "error") return "Save pricing draft before confirming Fee.";
if (input.saveState.kind === "stale") return input.saveState.message;
if (!input.latestSavedPricingDraftId) return "Save pricing draft before confirming Fee.";
if (input.savedLocalPricingSignature !== input.currentPricingDraftSignature) {
  return "Saving pricing draft before confirm.";
}
```

- [ ] **Step 4: Remove implicit save from confirm**

Replace the save block in `handleConfirmFee()` with:

```ts
const savedDraftId = latestSavedPricingDraftId;
if (!savedDraftId || savedLocalPricingSignature !== currentPricingDraftSignature) {
  setConfirmFeeActionState({
    kind: "error",
    message: "Save pricing draft before confirming Fee.",
  });
  return;
}

const result = await confirmFeeVersion(projectId, {
  confirmed_by: confirmedBy.trim(),
  expected_pricing_draft_edit_id: savedDraftId,
  summary: {
    testing_fee_total: allPreviewTotal,
    working_hours: allWorkingHoursLabel,
    lab_manpower_cost: allLabManpowerCostLabel,
    external_cost: costPreviewValues.externalCost,
    grand_cost: allGrandCostLabel,
  },
});
```

- [ ] **Step 5: Run frontend tests**

Run:

```powershell
cd frontend
npm test -- FeeEvaluationReviewExportPage
```

Expected: confirm gating tests pass.

### Task 6: Discard / Back To Workbench

**Files:**

- Modify: `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
- Modify: `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
- Test: `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`

- [ ] **Step 1: Add failing discard tests**

Add:

```ts
it("discards the current pricing draft before returning to Workbench", async () => {
  apiMocks.getFeeEvaluationPricingDraft.mockResolvedValueOnce(currentPricingDraftResponse());
  const onBackToWorkbench = vi.fn();
  render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={onBackToWorkbench} />);

  fireEvent.click(await screen.findByRole("button", { name: "Back to Workbench" }));

  await waitFor(() => {
    expect(apiMocks.discardFeeEvaluationPricingDraft).toHaveBeenCalledWith("P1", {
      expected_pricing_draft_edit_id: "fed-1",
      expected_confirmed_matrix_id: "cmv-1",
      expected_confirmed_revision: 1,
      expected_fee_rule_version_id: "fee_rules_v2026_06_03",
    });
    expect(onBackToWorkbench).toHaveBeenCalledTimes(1);
  });
});


it("stays on Fee Evaluation when pricing draft discard fails", async () => {
  apiMocks.getFeeEvaluationPricingDraft.mockResolvedValueOnce(currentPricingDraftResponse());
  apiMocks.discardFeeEvaluationPricingDraft.mockRejectedValueOnce(
    new Error("Pricing draft changed before discard.")
  );
  const onBackToWorkbench = vi.fn();
  render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={onBackToWorkbench} />);

  fireEvent.click(await screen.findByRole("button", { name: "Back to Workbench" }));

  await waitFor(() => expect(apiMocks.discardFeeEvaluationPricingDraft).toHaveBeenCalledTimes(1));
  expect(onBackToWorkbench).not.toHaveBeenCalled();
  expect(screen.getByText("Pricing draft changed before discard.")).toBeTruthy();
});


it("does not hang Back to Workbench when in-flight autosave never settles", async () => {
  vi.useFakeTimers();
  apiMocks.getFeeEvaluationPricingDraft.mockResolvedValueOnce(currentPricingDraftResponse());
  apiMocks.saveFeeEvaluationPricingDraft.mockImplementationOnce(
    () => new Promise(() => undefined)
  );
  const onBackToWorkbench = vi.fn();
  render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={onBackToWorkbench} />);

  fireEvent.change(await screen.findByLabelText("External Cost preview"), {
    target: { value: "325" },
  });
  await vi.advanceTimersByTimeAsync(800);
  fireEvent.click(screen.getByRole("button", { name: "Back to Workbench" }));
  await vi.advanceTimersByTimeAsync(1500);

  await waitFor(() => expect(apiMocks.discardFeeEvaluationPricingDraft).toHaveBeenCalledTimes(1));
  expect(onBackToWorkbench).toHaveBeenCalledTimes(1);
  vi.useRealTimers();
});
```

- [ ] **Step 2: Run frontend tests and verify red**

Run:

```powershell
cd frontend
npm test -- FeeEvaluationReviewExportPage
```

Expected: fails because back currently navigates directly.

- [ ] **Step 3: Add back/discard handler**

In `FeeEvaluationReviewExportPage.tsx`:

```ts
function waitForAutosaveOrTimeout(
  promise: Promise<FeeEvaluationPricingDraftResponse | null> | null,
  timeoutMs = 1500
): Promise<FeeEvaluationPricingDraftResponse | null> {
  if (!promise) {
    return Promise.resolve(null);
  }
  return Promise.race([
    promise.catch(() => null),
    new Promise<null>((resolve) => window.setTimeout(() => resolve(null), timeoutMs)),
  ]);
}


async function handleBackToWorkbench(): Promise<void> {
  const hasDraftToDiscard =
    Boolean(latestSavedPricingDraftId) ||
    savedLocalPricingSignature !== currentPricingDraftSignature ||
    saveState.kind === "dirty" ||
    saveState.kind === "saving" ||
    saveState.kind === "error";
  if (!hasDraftToDiscard) {
    onBackToWorkbench();
    return;
  }
  if (!window.confirm("Discard Fee Evaluation pricing edits and return to Workbench?")) {
    return;
  }
  discardingRef.current = true;
  autosaveGenerationRef.current += 1;
  if (autosaveTimeoutRef.current !== null) {
    window.clearTimeout(autosaveTimeoutRef.current);
    autosaveTimeoutRef.current = null;
  }
  autosaveAbortControllerRef.current?.abort();
  setIsDiscardingPricingDraft(true);
  const inFlightResult = await waitForAutosaveOrTimeout(autosaveInFlightRef.current, 1500);
  const latestResult = inFlightResult ?? latestAutosaveResultRef.current;
  try {
    await discardFeeEvaluationPricingDraft(projectId, {
      expected_pricing_draft_edit_id:
        latestResult?.saved_draft_edit_id ?? latestSavedPricingDraftId,
      expected_confirmed_matrix_id:
        latestResult?.current_confirmed_matrix_id ?? activePricingContext.confirmedMatrixId,
      expected_confirmed_revision:
        latestResult?.current_confirmed_revision ?? activePricingContext.confirmedRevision,
      expected_fee_rule_version_id:
        latestResult?.current_fee_rule_version_id ?? activePricingContext.feeRuleVersionId,
    });
    onBackToWorkbench();
  } catch (error) {
    discardingRef.current = false;
    setIsDiscardingPricingDraft(false);
    setSaveState({
      kind: "error",
      message: error instanceof Error ? error.message : "Unable to discard pricing draft.",
    });
  }
}
```

Define `activePricingContext` from pricing draft load response fields stored in state.

- [ ] **Step 4: Wire preview table back action**

Pass:

```tsx
onBackToWorkbench={() => void handleBackToWorkbench()}
```

In `FeeEvaluationPreviewTable.tsx`, keep the button label `Back to Workbench`.

- [ ] **Step 5: Run frontend tests**

Run:

```powershell
cd frontend
npm test -- FeeEvaluationReviewExportPage
```

Expected: discard tests pass.

### Task 7: Static Guards And Regression Validation

**Files:**

- Modify if needed: `tests/unit/test_frontend_shell_files.py`
- Run backend/frontend validation.
- Modify: `docs/task_board.md` only after implementation is approved and completed.

- [ ] **Step 1: Update static guards if they require old manual save copy**

Search:

```powershell
rg "Save changes|saveFeeEvaluationPricingDraft|Confirm Fee" tests/unit/test_frontend_shell_files.py frontend/src/features/fee-evaluation -n
```

If a static guard intentionally requires `Save changes`, replace it with checks for:

```text
Saving pricing draft
Confirm Fee
discardFeeEvaluationPricingDraft
```

- [ ] **Step 2: Run required backend validation**

Run:

```powershell
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q
```

Expected: all pass.

- [ ] **Step 3: Run Confirmed Fee validation**

Run:

```powershell
py -m pytest tests/unit/test_confirmed_fee_version_service.py tests/integration/test_confirmed_fee_version_api.py -q
```

Expected: all pass.

- [ ] **Step 4: Run frontend validation**

Run:

```powershell
cd frontend
npm test -- FeeEvaluationReviewExportPage
npm run build
```

Expected: tests and build pass.

- [ ] **Step 5: Run shell guard**

Run:

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee"
```

Expected: fee-related shell guards pass.

- [ ] **Step 6: Recommended Project Folder regression**

Run:

```powershell
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/unit/test_official_project_folder_check_service.py -q
```

Expected: Project Folder readiness remains green.

- [ ] **Step 7: Update task board after approved implementation**

Only after implementation and validation, update `docs/task_board.md`:

```text
TASK_314B_FEE_EVALUATION_BACKGROUND_DRAFT_PERSISTENCE is complete.
Validation: <commands and pass counts>.
Scope boundaries held: no TASK_315 rebase, no Fee calculation changes, no ProjectOutputRecord changes.
Next task requires separate approval.
```

## Risk Register

| Risk | Mitigation |
| --- | --- |
| Autosave validates a transient invalid payload and creates noisy errors while operator types | Keep error visible but non-blocking until Confirm; next edit retries after debounce. |
| Missing pricing draft plus unchanged default Fee payload leaves Confirm Fee with no saved draft id | Add one controlled background seed save when `status="missing"` and Fee defaults are ready; test default unchanged confirmation. |
| Back/discard races with in-flight autosave | Clear debounce, abort the autosave request when possible, increment generation, bounded-wait 1.5 seconds, discard latest known draft token, ignore late responses. |
| In-flight autosave never settles | Bounded wait before discard; Back/Discard must not hang indefinitely. |
| Confirm Fee accidentally saves a different payload than the one confirmed | Remove implicit save in confirm path; require `savedLocalPricingSignature === currentPricingDraftSignature` and saved draft id. |
| DELETE body compatibility | Current offline FastAPI path is acceptable; future proxy deployment should consider POST discard route. |
| A newer stale pricing draft hides the current-context draft | Add `get_by_context(...)` and use it for load/discard instead of latest-by-project. |
| Stale pricing draft from old Matrix applied to new preview | Do not return/apply stale payload; stale presence may only be warning metadata. |
| Manual save removal reduces operator confidence | Preserve concise save state text beside actions; show disabled reasons for Confirm Fee. |

## Acceptance Mapping

- Autosave after debounce: Task 4.
- No autosave during initial load: Task 4.
- Controlled seed save for missing default payload: Task 4 and Task 5.
- No repeated save for unchanged payload: Task 4 signature handling.
- Restore current saved draft by exact context: Task 1 and Task 2.
- Stale draft not applied: Task 1, Task 2, Task 4/5 tests.
- Remove `Save changes`: Task 3.
- Confirm disabled while dirty/pending/failed/stale/missing token: Task 5.
- Confirm default unchanged Fee after seed save: Task 4 and Task 5.
- Confirm uses latest autosaved id without implicit save: Task 5.
- Discard current pricing draft: Task 2 and Task 6.
- Discard current-context row when a newer stale row exists: Task 1 and Task 2.
- Discard rejects mismatched tokens: Task 1 and Task 2.
- Discard aborts/bounded-waits in-flight autosave: Task 6.
- Discard failure stays on page: Task 6.
- Confirmed Fee authority untouched: Task 5 and validation suite.
- Project Folder readiness unaffected: Task 7 regression.

## Self-Review

Spec coverage:

- TASK_314B expected scope from umbrella task is covered: pricing draft autosave, discard endpoint, removal of normal-flow `Save changes`, Confirm Fee disabled while dirty/pending/failed/stale.
- TASK_315 rebase is explicitly out of scope.
- TASK_314C regression is not executed here, only a narrow recommended guard is listed.

Marker scan:

- No unresolved markers remain.
- Each implementation task includes exact file paths, commands, and expected outcomes.

Type consistency:

- Backend command/result names use `FeeEvaluationPricingDraft...`.
- Frontend API DTO names use `FeeEvaluationPricingDraftDiscard...`.
- Existing `saved_draft_edit_id` naming is preserved to match current API DTOs.

## Stop Point

TASK_314B implementation is complete after validation and task board update.

Do not proceed to TASK_314C, TASK_315, package execution, StepInstance, reporting, AI, permissions, or multi-user scope without separate explicit approval.
