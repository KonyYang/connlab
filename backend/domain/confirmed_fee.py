"""Domain objects for Confirmed Fee authority snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


ConfirmedFeeStatus = Literal["missing", "current", "stale"]


@dataclass(frozen=True, slots=True)
class ConfirmedFeeSummary:
    """Operator-confirmed Fee Evaluation totals snapshot."""

    testing_fee_total: str
    working_hours: str
    lab_manpower_cost: str
    external_cost: str
    grand_cost: str


@dataclass(frozen=True, slots=True)
class ConfirmedFeeVersion:
    """Immutable Confirmed Fee authority version for one project."""

    confirmed_fee_id: str
    project_id: str
    confirmed_fee_revision: int
    confirmed_matrix_id: str
    confirmed_revision: int
    fee_rule_version_id: str
    pricing_draft_edit_id: str
    pricing_effective_from: str | None
    summary: ConfirmedFeeSummary
    pricing_snapshot_json: str
    confirmed_by: str
    confirmed_at: str
    confirmation_note: str | None = None
