# TASK_286 Confirmed Matrix To Fee Draft Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a backend-only, read-only Fee Evaluation draft preview from active Confirmed Matrix authority and the active TASK_285 fee-rule seed library.

**Architecture:** Add an application-layer service that consumes the existing Confirmed Matrix repository port and `backend.modules.fee_evaluation` matcher. Keep fee draft output as typed application dataclasses plus a thin FastAPI response mapper. Do not persist edited fee drafts, export Excel, add UI, or expand Matrix authority semantics.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic v2, pytest, existing SQLAlchemy repository wiring, existing `backend.modules.fee_evaluation` rule seed library.

---

## Current Task Context

- Current Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current Active Task: `TASK_286_CONFIRMED_MATRIX_TO_FEE_DRAFT`
- Why allowed now: `docs/task_board.md` marks TASK_285 complete and TASK_286 as planned awaiting explicit approval.
- Implementation gate: this plan must be reviewed and explicitly approved before code changes begin.

## Scope Summary

### In Scope

- Backend application dataclasses for fee draft preview.
- Backend application service reading active Confirmed Matrix authority.
- Active fee rule version from TASK_285 via `load_active_fee_rule_library()`.
- Typed FastAPI route returning a read-only fee draft preview.
- Unit tests for service behavior.
- Integration tests for the API route.

### Out Of Scope

- No frontend review UI.
- No Excel export.
- No persisted edited fee draft.
- No new database tables or migrations.
- No Project model date field expansion.
- No application-form lookup for sample received date.
- No StepInstance, execution persistence, report generation, or legacy `test_record_fee_*` expansion.

## Required Semantics

### Pricing Effective Date

TASK_285 seed uses:

```text
effective_from_basis = "project.sample_received_date"
```

TASK_286 resolves that basis from:

```python
snapshot.version.sample_received_date
```

Output field:

```python
pricing_effective_from: str | None
```

If `sample_received_date` is missing, still return a draft but add a warning and mark the draft as needing review. Do not query Project or application-form records.

### V1 Calculation Policy

Calculate `testing_fee` only when all of these are true:

- matched fee rule exists;
- `rule.review_required` is `False`;
- `rule.unit_price.amount` is numeric;
- `rule.base_fee.amount` is numeric or deterministic zero;
- discount is deterministic, V1 default `0`;
- units are deterministic from Confirmed Matrix authority.

V1 deterministic units:

- `per_sample` / `per_specimen`: group `sample_quantity_expression` is a plain non-negative number such as `5` or `3`.
- `fixed_per_group`: unit count is `1` for each selected group/row where that group cell has at least one parsed step token.

V1 review-required units:

- `per_photo`: no photo count in Matrix authority.
- `per_reading`: no reading-count derivation in this task.
- `per_cycle`: review-required unless a later task defines cycle parsing.
- `per_hour`: no Day-to-hour fee conversion in this task.
- `manual_required` / `unknown`: always review-required.
- sample expressions such as `5+(5e)`, `3 pcs`, ranges, notes, or marker-bearing values.

## File Structure

### Create

- `backend/application/confirmed_matrix_fee_draft_service.py`
  - Application dataclasses.
  - Confirmed Matrix authority store protocol.
  - Fee draft build service.
  - V1 calculation helper functions.

- `backend/api/routes_confirmed_matrix_fee_draft.py`
  - Pydantic response models.
  - `GET /api/projects/{project_id}/confirmed-matrix/fee-draft`
  - Thin mapping from application dataclasses to response DTOs.

- `tests/unit/test_confirmed_matrix_fee_draft_service.py`
  - Service tests with in-memory fake confirmed store.

- `tests/integration/test_confirmed_matrix_fee_draft_api.py`
  - Route tests using temporary SQLite database and existing Matrix draft/confirm flow where possible.

### Modify

- `backend/api/dependencies.py`
  - Add `get_confirmed_matrix_fee_draft_service()`.

- `backend/api/main.py`
  - Include the new router.

- `tasks/TASK_286_CONFIRMED_MATRIX_TO_FEE_DRAFT.md`
  - Mark complete only after implementation and validation.

- `docs/task_board.md`
  - Mark TASK_286 complete and keep TASK_287 planned after successful validation.

## Data Model Design

Use application-layer dataclasses in `backend/application/confirmed_matrix_fee_draft_service.py`.

```python
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, Protocol

from backend.domain import ConfirmedMatrixSnapshot

FeeDraftStatus = Literal["ready", "empty", "needs_review"]
FeeLineStatus = Literal["calculated", "review_required", "no_rule_match"]


class ConfirmedMatrixFeeDraftNotFoundError(LookupError):
    """Raised when no active confirmed Matrix authority exists for a project."""


class ConfirmedMatrixFeeDraftError(ValueError):
    """Raised when confirmed Matrix fee draft data cannot be built."""


class ConfirmedMatrixAuthorityStore(Protocol):
    """Confirmed Matrix authority read operations required by fee draft service."""

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        """Return one active confirmed authority aggregate in one project."""


@dataclass(frozen=True, slots=True)
class BuildConfirmedMatrixFeeDraftCommand:
    """Input payload for confirmed-authority fee draft building."""

    project_id: str


@dataclass(frozen=True, slots=True)
class FeeEvaluationWarning:
    """One warning emitted while building the fee draft."""

    code: str
    message: str
    scope: str


@dataclass(frozen=True, slots=True)
class FeeEvaluationLineItem:
    """One Matrix-derived fee candidate line for operator review."""

    line_id: str
    status: FeeLineStatus
    review_required: bool
    review_reason: str | None
    confirmed_matrix_id: str
    confirmed_revision: int
    group_key: str
    group_label: str
    confirmed_group_id: str
    sample_quantity_expression: str
    confirmed_row_id: str
    source_row_id: str | None
    row_order: int
    test_item: str
    section: str
    method: str
    condition: str
    requirement: str
    step_tokens: tuple[str, ...]
    matched_rule_id: str | None
    matched_rule_version_id: str | None
    matched_rule_name: str | None
    match_reason: str
    calculation_strategy: str | None
    unit_label: str
    unit_price: Decimal | None
    units: Decimal | None
    base_fee: Decimal | None
    discount_percent: Decimal | None
    testing_fee: Decimal | None
    warnings: tuple[FeeEvaluationWarning, ...]


@dataclass(frozen=True, slots=True)
class FeeEvaluationGroup:
    """One selected Confirmed Matrix group with fee draft line items."""

    group_key: str
    group_label: str
    sample_quantity_expression: str
    line_items: tuple[FeeEvaluationLineItem, ...]


@dataclass(frozen=True, slots=True)
class FeeEvaluationHeader:
    """Top-level fee draft metadata and pricing source traceability."""

    project_id: str
    confirmed_matrix_id: str
    confirmed_revision: int
    pricing_rule_version_id: str
    pricing_source_file_name: str
    pricing_source_hash: str
    pricing_effective_from: str | None
    generated_at: str


@dataclass(frozen=True, slots=True)
class FeeEvaluationDraft:
    """Read-only fee evaluation draft preview derived from Confirmed Matrix."""

    header: FeeEvaluationHeader
    draft_status: FeeDraftStatus
    total_fee: Decimal | None
    review_required_count: int
    groups: tuple[FeeEvaluationGroup, ...]
    warnings: tuple[FeeEvaluationWarning, ...]
```

## API Design

Endpoint:

```text
GET /api/projects/{project_id}/confirmed-matrix/fee-draft
```

Status mapping:

- `200`: returns fee draft, including `empty` and `needs_review`.
- `404`: no active confirmed Matrix authority.
- `422`: confirmed Matrix lineage is internally invalid.

Representative response:

```json
{
  "header": {
    "project_id": "P1",
    "confirmed_matrix_id": "cmv-1",
    "confirmed_revision": 1,
    "pricing_rule_version_id": "fee_rules_v2026_06_03",
    "pricing_source_file_name": "Testing Fee Evaluation-Even.xls",
    "pricing_source_hash": "sha256:b19cce35f774ad3a83260805f7b717d5446f23ca1a90c209a08d8cb7f91fe226",
    "pricing_effective_from": "2026-06-03",
    "generated_at": "2026-06-04T10:00:00+08:00"
  },
  "draft_status": "needs_review",
  "total_fee": null,
  "review_required_count": 2,
  "groups": [
    {
      "group_key": "g1",
      "group_label": "1",
      "sample_quantity_expression": "5",
      "line_items": [
        {
          "line_id": "cmv-1:g1:cmr-visual",
          "status": "review_required",
          "review_required": true,
          "review_reason": "Photo count is not available from Matrix authority.",
          "test_item": "Visual Examination",
          "step_tokens": ["1"],
          "matched_rule_id": "fee_rule_visual_exam",
          "matched_rule_version_id": "fee_rules_v2026_06_03",
          "calculation_strategy": "per_photo",
          "unit_price": 10,
          "units": null,
          "base_fee": 0,
          "discount_percent": 0,
          "testing_fee": null
        }
      ]
    }
  ],
  "warnings": []
}
```

Use JSON numbers for Decimal response fields through Pydantic serialization. If existing response style prefers strings for Decimal, use strings consistently and document it in the route mapper. The implementation plan recommends `Decimal | None` in service dataclasses and `float | None` or `str | None` in response models only after checking existing API response conventions. Do not introduce a custom global encoder.

## Implementation Tasks

### Task 1: Service Tests For Metadata And Not Found

**Files:**
- Create test: `tests/unit/test_confirmed_matrix_fee_draft_service.py`
- Later create implementation: `backend/application/confirmed_matrix_fee_draft_service.py`

- [ ] **Step 1: Write failing tests for active snapshot metadata and not-found behavior**

Add this test skeleton:

```python
from __future__ import annotations

from decimal import Decimal

import pytest

from backend.application.confirmed_matrix_fee_draft_service import (
    BuildConfirmedMatrixFeeDraftCommand,
    ConfirmedMatrixFeeDraftNotFoundError,
    ConfirmedMatrixFeeDraftService,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixVersion,
)


def test_fee_draft_header_uses_confirmed_matrix_version_sample_received_date() -> None:
    service = ConfirmedMatrixFeeDraftService(confirmed_store=_ConfirmedStore(active=_snapshot()))

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    assert draft.header.project_id == "P1"
    assert draft.header.confirmed_matrix_id == "cmv-1"
    assert draft.header.confirmed_revision == 1
    assert draft.header.pricing_rule_version_id == "fee_rules_v2026_06_03"
    assert draft.header.pricing_source_file_name == "Testing Fee Evaluation-Even.xls"
    assert draft.header.pricing_effective_from == "2026-06-03"
    assert draft.draft_status in {"empty", "needs_review"}


def test_fee_draft_not_found_when_no_active_authority() -> None:
    service = ConfirmedMatrixFeeDraftService(confirmed_store=_ConfirmedStore(active=None))

    with pytest.raises(ConfirmedMatrixFeeDraftNotFoundError, match="Active confirmed matrix not found"):
        service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))


class _ConfirmedStore:
    def __init__(self, active: ConfirmedMatrixSnapshot | None) -> None:
        self.active = active

    def get_active_by_project(self, project_id: str) -> ConfirmedMatrixSnapshot | None:
        if self.active and self.active.version.project_id == project_id:
            return self.active
        return None


def _snapshot(
    *,
    sample_quantity_expression: str = "5",
    row: ConfirmedMatrixRow | None = None,
    cell_value: str = "1",
    sample_received_date: str | None = "2026-06-03",
) -> ConfirmedMatrixSnapshot:
    row = row or ConfirmedMatrixRow(
        confirmed_row_id="cmr-visual",
        confirmed_matrix_id="cmv-1",
        draft_row_id="pmdr-visual",
        source_row_snapshot_id="smr-visual",
        row_order=1,
        test_item="Visual Examination",
        source_section="6.1",
        method="EIA-364-18",
        condition="Visual Inspection",
        requirement="No damage",
    )
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id="cmv-1",
            project_id="P1",
            project_matrix_draft_id="pmd-1",
            source_import_id="smi-1",
            source_snapshot_id="sms-1",
            confirmed_revision=1,
            is_active_authority=True,
            status=ConfirmedMatrixStatus.CONFIRMED,
            confirmed_by="operator",
            confirmed_at="2026-06-03T09:00:00+08:00",
            sample_received_date=sample_received_date,
        ),
        groups=(
            ConfirmedMatrixGroup(
                confirmed_group_id="cmg-1",
                confirmed_matrix_id="cmv-1",
                draft_group_id="pmdg-1",
                source_group_snapshot_id="smg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                sample_quantity_expression=sample_quantity_expression,
            ),
        ),
        rows=(row,),
        cells=(
            ConfirmedMatrixCell(
                confirmed_cell_id="cmc-1",
                confirmed_matrix_id="cmv-1",
                confirmed_row_id=row.confirmed_row_id,
                confirmed_group_id="cmg-1",
                draft_row_id=row.draft_row_id,
                draft_group_id="pmdg-1",
                cell_value=cell_value,
            ),
        ),
    )
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_fee_draft_service.py -q
```

Expected: import failure because `backend.application.confirmed_matrix_fee_draft_service` does not exist.

### Task 2: Implement Service Skeleton And Header

**Files:**
- Create: `backend/application/confirmed_matrix_fee_draft_service.py`
- Modify test: `tests/unit/test_confirmed_matrix_fee_draft_service.py`

- [ ] **Step 1: Add application dataclasses and header-building service**

Create `backend/application/confirmed_matrix_fee_draft_service.py` with the dataclasses from the Data Model section and this service skeleton:

```python
class ConfirmedMatrixFeeDraftService:
    """Build read-only Fee Evaluation drafts from active Confirmed Matrix authority."""

    def __init__(self, *, confirmed_store: ConfirmedMatrixAuthorityStore) -> None:
        self._confirmed = confirmed_store

    def build_draft(self, command: BuildConfirmedMatrixFeeDraftCommand) -> FeeEvaluationDraft:
        """Return one Fee Evaluation draft preview for a project."""
        snapshot = self._confirmed.get_active_by_project(command.project_id)
        if snapshot is None:
            raise ConfirmedMatrixFeeDraftNotFoundError("Active confirmed matrix not found.")
        library = load_active_fee_rule_library()
        warnings = _root_warnings(snapshot)
        groups = _build_groups(snapshot=snapshot, library=library)
        line_items = tuple(item for group in groups for item in group.line_items)
        review_required_count = sum(1 for item in line_items if item.review_required)
        calculated_values = [item.testing_fee for item in line_items if item.testing_fee is not None]
        total_fee = sum(calculated_values, Decimal("0")) if calculated_values and review_required_count == 0 else None
        return FeeEvaluationDraft(
            header=FeeEvaluationHeader(
                project_id=snapshot.version.project_id,
                confirmed_matrix_id=snapshot.version.confirmed_matrix_id,
                confirmed_revision=snapshot.version.confirmed_revision,
                pricing_rule_version_id=library.version.version_id,
                pricing_source_file_name=library.version.source_file_name,
                pricing_source_hash=library.version.source_hash,
                pricing_effective_from=snapshot.version.sample_received_date,
                generated_at=_now_iso(),
            ),
            draft_status=_draft_status(groups, warnings),
            total_fee=total_fee,
            review_required_count=review_required_count + len(warnings),
            groups=groups,
            warnings=tuple(warnings),
        )
```

Helper behavior:

```python
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _root_warnings(snapshot: ConfirmedMatrixSnapshot) -> list[FeeEvaluationWarning]:
    if snapshot.version.sample_received_date:
        return []
    return [
        FeeEvaluationWarning(
            code="missing_pricing_effective_from",
            message="Sample received date is missing from active Confirmed Matrix authority.",
            scope="confirmed_matrix",
        )
    ]
```

For the first pass, `_build_groups()` may return empty groups. Later tasks fill line items. Do not assert `needs_review` until line-item construction or missing-root-warning behavior exists.

- [ ] **Step 2: Run the metadata tests**

Run:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_fee_draft_service.py -q
```

Expected: metadata/not-found tests pass after filling minimal `_build_groups` and `_draft_status`.

### Task 3: Add Line Item Construction And Review-Required Matching

**Files:**
- Modify: `backend/application/confirmed_matrix_fee_draft_service.py`
- Modify: `tests/unit/test_confirmed_matrix_fee_draft_service.py`

- [ ] **Step 1: Add failing tests for Visual and unmatched line items**

Append:

```python
def test_fee_draft_marks_visual_exam_review_required_because_photo_count_is_unknown() -> None:
    service = ConfirmedMatrixFeeDraftService(confirmed_store=_ConfirmedStore(active=_snapshot()))

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.status == "review_required"
    assert line.review_required is True
    assert line.matched_rule_id == "fee_rule_visual_exam"
    assert line.matched_rule_version_id == "fee_rules_v2026_06_03"
    assert line.calculation_strategy == "per_photo"
    assert line.unit_price == Decimal("10")
    assert line.units is None
    assert line.testing_fee is None
    assert line.step_tokens == ("1",)


def test_fee_draft_marks_unmatched_row_as_no_rule_match() -> None:
    row = ConfirmedMatrixRow(
        confirmed_row_id="cmr-unknown",
        confirmed_matrix_id="cmv-1",
        draft_row_id="pmdr-unknown",
        source_row_snapshot_id="smr-unknown",
        row_order=1,
        test_item="Laser welding simulation",
        source_section="9.9",
        method="",
        condition="",
        requirement="",
    )
    service = ConfirmedMatrixFeeDraftService(confirmed_store=_ConfirmedStore(active=_snapshot(row=row)))

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.status == "no_rule_match"
    assert line.review_required is True
    assert line.matched_rule_id is None
    assert line.matched_rule_version_id is None
    assert line.review_reason == "No fee rule match."
```

- [ ] **Step 2: Implement line item building**

Implement helpers:

```python
def _build_groups(*, snapshot: ConfirmedMatrixSnapshot, library: FeeRuleLibrary) -> tuple[FeeEvaluationGroup, ...]:
    groups_by_id = {group.confirmed_group_id: group for group in snapshot.groups}
    rows_by_id = {row.confirmed_row_id: row for row in snapshot.rows}
    cell_lookup = _build_cell_lookup(snapshot=snapshot, groups_by_id=groups_by_id, rows_by_id=rows_by_id)
    matcher = FeeRuleMatcher(library)
    groups: list[FeeEvaluationGroup] = []
    for group in snapshot.groups:
        lines = _build_group_lines(group=group, snapshot=snapshot, cell_lookup=cell_lookup, matcher=matcher)
        if not lines:
            continue
        groups.append(
            FeeEvaluationGroup(
                group_key=group.group_key.strip(),
                group_label=group.group_label.strip(),
                sample_quantity_expression=_text(group.sample_quantity_expression),
                line_items=tuple(lines),
            )
        )
    return tuple(groups)
```

Use existing `parse_step_tokens` from `backend.modules.test_plan.matrix_step_sequence_validation`. If parsing returns no tokens, skip the row/group line because selected group contribution requires step tokens.

Line id:

```python
line_id = f"{snapshot.version.confirmed_matrix_id}:{group.group_key}:{row.confirmed_row_id}"
```

Warnings:

- Invalid cell lineage raises `ConfirmedMatrixFeeDraftError("Confirmed matrix cell lineage is invalid.")`.
- Unmatched rows return `status="no_rule_match"` with `matched_rule_id=None` and `matched_rule_version_id=None`.
- Matched rows always copy `library.version.version_id` into `matched_rule_version_id`, including review-required rows.
- Matched but non-calculable rows return `status="review_required"`.

- [ ] **Step 3: Run service tests**

Run:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_fee_draft_service.py -q
```

Expected: all current service tests pass.

### Task 4: Add V1 Calculation Tests And Minimal Calculation

**Files:**
- Modify: `backend/application/confirmed_matrix_fee_draft_service.py`
- Modify: `tests/unit/test_confirmed_matrix_fee_draft_service.py`

- [ ] **Step 1: Add tests for deterministic and ambiguous unit policy**

Because active TASK_285 seed may not include a non-review `per_sample` rule, use an injected library hook only if necessary. Preferred approach: allow service constructor optional `rule_library: FeeRuleLibrary | None = None` for tests, defaulting to `load_active_fee_rule_library()` in production.

Test cases:

```python
def test_fee_draft_calculates_fixed_per_group_when_rule_is_deterministic() -> None:
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(active=_snapshot(row=_fixture_row("Fixture setup"))),
        rule_library=_single_rule_library(
            rule_id="fee_rule_fixture",
            display_name="Fixture setup",
            aliases=("Fixture setup",),
            unit_price=Decimal("100"),
            base_fee=Decimal("0"),
            strategy="fixed_per_group",
            review_required=False,
        ),
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.status == "calculated"
    assert line.units == Decimal("1")
    assert line.testing_fee == Decimal("100")
    assert draft.total_fee == Decimal("100")


def test_fee_draft_marks_marker_sample_quantity_review_required_for_per_sample() -> None:
    service = ConfirmedMatrixFeeDraftService(
        confirmed_store=_ConfirmedStore(
            active=_snapshot(
                sample_quantity_expression="5+(5e)",
                row=_fixture_row("Sample preparation"),
            )
        ),
        rule_library=_single_rule_library(
            rule_id="fee_rule_sample_prep",
            display_name="Sample preparation",
            aliases=("Sample preparation",),
            unit_price=Decimal("50"),
            base_fee=Decimal("0"),
            strategy="per_sample",
            review_required=False,
        ),
    )

    draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id="P1"))

    line = draft.groups[0].line_items[0]
    assert line.status == "review_required"
    assert line.units is None
    assert line.testing_fee is None
    assert "sample quantity" in (line.review_reason or "").lower()
```

- [ ] **Step 2: Implement calculation helper**

Core helper:

```python
def _calculate_line(rule: FeeRule, group: ConfirmedMatrixGroup, step_tokens: tuple[str, ...]) -> _CalculationResult:
    if rule.review_required:
        return _review("Matched fee rule requires operator review.", rule)
    if rule.unit_price.amount is None:
        return _review("Unit price is not numeric in the active fee rule.", rule)
    if rule.base_fee.amount is None:
        return _review("Base fee is not deterministic in the active fee rule.", rule)
    if rule.calculation_strategy in {"per_sample", "per_specimen"}:
        units = _plain_decimal_quantity(group.sample_quantity_expression)
        if units is None:
            return _review("Group sample quantity is not a plain numeric unit basis.", rule)
        return _calculated(rule, units)
    if rule.calculation_strategy == "fixed_per_group":
        if not step_tokens:
            return _review("No selected step tokens are available for this group.", rule)
        return _calculated(rule, Decimal("1"))
    return _review(f"{rule.calculation_strategy} requires operator review in V1.", rule)
```

Quantity parser:

```python
_PLAIN_NON_NEGATIVE_DECIMAL = re.compile(r"^\d+(?:\.\d+)?$")

def _plain_decimal_quantity(value: str) -> Decimal | None:
    text = value.strip()
    if not _PLAIN_NON_NEGATIVE_DECIMAL.fullmatch(text):
        return None
    return Decimal(text)
```

Calculated fee:

```python
testing_fee = rule.unit_price.amount * units * (Decimal("1") - discount_percent / Decimal("100")) + rule.base_fee.amount
```

V1 discount percent is always `Decimal("0")`.

- [ ] **Step 3: Run service tests**

Run:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_fee_draft_service.py -q
```

Expected: pass.

### Task 5: Add API Route And Dependency Wiring

**Files:**
- Create: `backend/api/routes_confirmed_matrix_fee_draft.py`
- Modify: `backend/api/dependencies.py`
- Modify: `backend/api/main.py`
- Test: `tests/integration/test_confirmed_matrix_fee_draft_api.py`

- [ ] **Step 1: Write failing integration tests**

Create route tests modeled after `tests/integration/test_confirmed_matrix_test_record_preview_api.py`:

```python
def test_confirmed_matrix_fee_draft_api_happy_path(tmp_path: Path) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        source_import_id = _seed_source_import("P1", tmp_path)
        create_draft = client.post(
            "/api/projects/P1/matrix-drafts",
            json={"source_import_id": source_import_id, "selected_group_keys": ["g1"]},
        )
        assert create_draft.status_code == 201
        draft_id = create_draft.json()["record"]["project_matrix_draft_id"]
        save = client.put(
            f"/api/projects/P1/matrix-drafts/{draft_id}",
            json={
                "groups": create_draft.json()["snapshot"]["groups"],
                "rows": create_draft.json()["snapshot"]["rows"],
                "cells": create_draft.json()["snapshot"]["cells"],
                "sample_received_date": "2026-06-03",
            },
        )
        assert save.status_code in {200, 204}
        confirm = client.post(
            f"/api/projects/P1/matrix-drafts/{draft_id}/confirm",
            json={"confirmed_by": "operator"},
        )
        assert confirm.status_code == 201

        response = client.get("/api/projects/P1/confirmed-matrix/fee-draft")

        assert response.status_code == 200
        payload = response.json()
        assert payload["header"]["project_id"] == "P1"
        assert payload["header"]["pricing_rule_version_id"] == "fee_rules_v2026_06_03"
        assert payload["header"]["pricing_effective_from"] == "2026-06-03"
        assert payload["draft_status"] in {"ready", "needs_review"}
        assert payload["groups"][0]["group_key"] == "g1"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
```

If draft update API shape differs, adjust test setup by directly seeding `ConfirmedMatrixAuthorityRepository` with a snapshot that includes `sample_received_date`. Keep the endpoint assertion unchanged.

Also add:

```python
def test_confirmed_matrix_fee_draft_api_returns_404_when_no_active_confirmed(tmp_path: Path) -> None:
    client, engine, _ = _client(tmp_path)
    try:
        _seed_project("P1", tmp_path)
        response = client.get("/api/projects/P1/confirmed-matrix/fee-draft")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
```

- [ ] **Step 2: Implement API route**

Response models should mirror service dataclasses:

```python
class FeeEvaluationWarningResponse(BaseModel):
    code: str
    message: str
    scope: str
```

Line response must include both rule id and rule version traceability:

```python
matched_rule_id: str | None
matched_rule_version_id: str | None
matched_rule_name: str | None
```

For Decimal fields, choose one representation and keep it local to the route:

```python
def _decimal_or_none(value: Decimal | None) -> str | None:
    return format(value, "f") if value is not None else None
```

Use strings for Decimal values in API response to avoid float precision drift:

```python
unit_price: str | None
units: str | None
base_fee: str | None
discount_percent: str | None
testing_fee: str | None
total_fee: str | None
```

Route:

```python
@router.get(
    "/api/projects/{project_id}/confirmed-matrix/fee-draft",
    response_model=FeeEvaluationDraftResponse,
)
def get_confirmed_matrix_fee_draft(
    project_id: str,
    service: ConfirmedMatrixFeeDraftService = Depends(get_confirmed_matrix_fee_draft_service),
) -> FeeEvaluationDraftResponse:
    try:
        draft = service.build_draft(BuildConfirmedMatrixFeeDraftCommand(project_id=project_id))
    except ConfirmedMatrixFeeDraftNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ConfirmedMatrixFeeDraftError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _to_response(draft)
```

- [ ] **Step 3: Wire dependencies and router**

In `backend/api/dependencies.py`:

```python
from backend.application.confirmed_matrix_fee_draft_service import ConfirmedMatrixFeeDraftService
```

Add:

```python
def get_confirmed_matrix_fee_draft_service(
    session: Session = Depends(get_session),
) -> ConfirmedMatrixFeeDraftService:
    """Return Confirmed-Matrix-backed fee draft service."""
    return ConfirmedMatrixFeeDraftService(
        confirmed_store=ConfirmedMatrixAuthorityRepository(session)
    )
```

In `backend/api/main.py`, import and include router:

```python
from backend.api.routes_confirmed_matrix_fee_draft import (
    router as confirmed_matrix_fee_draft_router,
)

app.include_router(confirmed_matrix_fee_draft_router)
```

- [ ] **Step 4: Run integration tests**

Run:

```powershell
py -m pytest tests/integration/test_confirmed_matrix_fee_draft_api.py -q
```

Expected: pass.

### Task 6: Validation And Documentation Closure

**Files:**
- Modify: `tasks/TASK_286_CONFIRMED_MATRIX_TO_FEE_DRAFT.md`
- Modify: `docs/task_board.md`

- [ ] **Step 1: Run targeted tests**

Run:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_fee_draft_service.py tests/integration/test_confirmed_matrix_fee_draft_api.py -q
```

Expected: all pass.

- [ ] **Step 2: Run regression tests**

Run:

```powershell
py -m pytest tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_matcher.py tests/unit/test_confirmed_matrix_test_record_preview_service.py tests/integration/test_confirmed_matrix_test_record_preview_api.py -q
```

Expected: all pass.

- [ ] **Step 3: Run API dependency smoke**

Run:

```powershell
py -m pytest tests/integration/test_api_default_dependencies.py -q
```

Expected: pass.

- [ ] **Step 4: Run diff check**

Run:

```powershell
git diff --check
```

Expected: no whitespace errors. CRLF warnings are acceptable if consistent with existing repository behavior.

- [ ] **Step 5: Update task docs only after tests pass**

Update `tasks/TASK_286_CONFIRMED_MATRIX_TO_FEE_DRAFT.md`:

```markdown
## Status

Complete. Implemented and validated on 2026-06-04.
```

Update `docs/task_board.md`:

- Mark TASK_286 complete.
- Record validation commands and pass counts.
- Set next recommended/current task to `TASK_287_FEE_EVALUATION_REVIEW_UI (planned; awaiting explicit approval)`.
- Preserve scope boundary: no UI, no Excel export, no edited draft persistence.

## Self-Review Checklist

- [ ] Every TASK_286 acceptance criterion maps to at least one implementation task.
- [ ] Plan does not add UI, Excel export, persistence for edited fee drafts, Project date fields, or application-form date lookup.
- [ ] `pricing_effective_from` comes from active `ConfirmedMatrixVersion.sample_received_date`.
- [ ] Every matched line item carries `matched_rule_version_id`; unmatched lines use `None`.
- [ ] V1 calculation policy blocks ambiguous units and emits `review_required`.
- [ ] Existing `test_record_fee_*` services are not modified.
- [ ] API route is thin and calls application service only.
- [ ] Tests cover no authority, pricing metadata, selected group behavior, unmatched rows, manual-required rows, and ambiguous unit bases.

## Execution Stop

After this plan is reviewed, implementation must wait for explicit approval such as:

```text
批准执行 TASK_286
```

Do not start TASK_287 after implementing TASK_286 unless the user explicitly approves TASK_287 separately.
