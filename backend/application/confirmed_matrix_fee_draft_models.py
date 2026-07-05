"""DTOs for read-only confirmed Matrix Fee Evaluation drafts."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, Protocol

from backend.domain import ConfirmedMatrixSnapshot
from backend.modules.fee_evaluation import FeeFieldMetadata

FeeDraftStatus = Literal["ready", "empty", "needs_review"]
FeeLineStatus = Literal["calculated", "review_required", "no_rule_match"]


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
    spend_time: str
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
    field_metadata: tuple[FeeFieldMetadata, ...]
    warnings: tuple[FeeEvaluationWarning, ...]


@dataclass(frozen=True, slots=True)
class FeeEvaluationGroup:
    """One selected Confirmed Matrix group with fee draft line items."""

    group_key: str
    group_label: str
    sample_quantity_expression: str
    manual_line_items: tuple[FeeEvaluationLineItem, ...]
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
    manual_line_items: tuple[FeeEvaluationLineItem, ...]
    warnings: tuple[FeeEvaluationWarning, ...]
