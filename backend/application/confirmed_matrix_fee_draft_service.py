"""Build read-only Fee Evaluation drafts from active Confirmed Matrix authority."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
import re
from typing import Literal, Protocol

from backend.domain import ConfirmedMatrixGroup, ConfirmedMatrixRow, ConfirmedMatrixSnapshot
from backend.modules.fee_evaluation import (
    FeeRule,
    FeeRuleLibrary,
    FeeRuleMatcher,
    load_active_fee_rule_library,
)
from backend.modules.test_plan.matrix_step_sequence_validation import parse_step_tokens

FeeDraftStatus = Literal["ready", "empty", "needs_review"]
FeeLineStatus = Literal["calculated", "review_required", "no_rule_match"]
_PLAIN_NON_NEGATIVE_DECIMAL = re.compile(r"^\d+(?:\.\d+)?$")
_ZERO = Decimal("0")


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


@dataclass(frozen=True, slots=True)
class _CalculationResult:
    status: FeeLineStatus
    review_required: bool
    review_reason: str | None
    units: Decimal | None
    base_fee: Decimal | None
    discount_percent: Decimal | None
    testing_fee: Decimal | None


class ConfirmedMatrixFeeDraftService:
    """Build read-only Fee Evaluation drafts from active Confirmed Matrix authority."""

    def __init__(
        self,
        *,
        confirmed_store: ConfirmedMatrixAuthorityStore,
        rule_library: FeeRuleLibrary | None = None,
    ) -> None:
        self._confirmed = confirmed_store
        self._rule_library = rule_library

    def build_draft(self, command: BuildConfirmedMatrixFeeDraftCommand) -> FeeEvaluationDraft:
        """Return one Fee Evaluation draft preview for a project."""
        snapshot = self._confirmed.get_active_by_project(command.project_id)
        if snapshot is None:
            raise ConfirmedMatrixFeeDraftNotFoundError("Active confirmed matrix not found.")
        library = self._rule_library or load_active_fee_rule_library()
        warnings = _root_warnings(snapshot)
        groups = _build_groups(snapshot=snapshot, library=library)
        line_items = tuple(item for group in groups for item in group.line_items)
        review_required_count = sum(1 for item in line_items if item.review_required)
        calculated_values = [item.testing_fee for item in line_items if item.testing_fee is not None]
        total_fee = (
            sum(calculated_values, Decimal("0"))
            if calculated_values and review_required_count == 0 and not warnings
            else None
        )
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


def _draft_status(
    groups: tuple[FeeEvaluationGroup, ...],
    warnings: list[FeeEvaluationWarning],
) -> FeeDraftStatus:
    if warnings:
        return "needs_review"
    if not groups:
        return "empty"
    if any(item.review_required for group in groups for item in group.line_items):
        return "needs_review"
    return "ready"


def _build_groups(
    *,
    snapshot: ConfirmedMatrixSnapshot,
    library: FeeRuleLibrary,
) -> tuple[FeeEvaluationGroup, ...]:
    groups_by_id = {group.confirmed_group_id: group for group in snapshot.groups}
    rows_by_id = {row.confirmed_row_id: row for row in snapshot.rows}
    cell_lookup = _build_cell_lookup(
        snapshot=snapshot,
        groups_by_id=groups_by_id,
        rows_by_id=rows_by_id,
    )
    matcher = FeeRuleMatcher(library)
    groups: list[FeeEvaluationGroup] = []
    for group in snapshot.groups:
        lines = _build_group_lines(
            group=group,
            snapshot=snapshot,
            cell_lookup=cell_lookup,
            matcher=matcher,
            library=library,
        )
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


def _build_cell_lookup(
    *,
    snapshot: ConfirmedMatrixSnapshot,
    groups_by_id: dict[str, ConfirmedMatrixGroup],
    rows_by_id: dict[str, ConfirmedMatrixRow],
) -> dict[tuple[str, str], str]:
    lookup: dict[tuple[str, str], str] = {}
    for cell in snapshot.cells:
        if cell.confirmed_group_id not in groups_by_id or cell.confirmed_row_id not in rows_by_id:
            raise ConfirmedMatrixFeeDraftError("Confirmed matrix cell lineage is invalid.")
        lookup[(cell.confirmed_group_id, cell.confirmed_row_id)] = cell.cell_value
    return lookup


def _build_group_lines(
    *,
    group: ConfirmedMatrixGroup,
    snapshot: ConfirmedMatrixSnapshot,
    cell_lookup: dict[tuple[str, str], str],
    matcher: FeeRuleMatcher,
    library: FeeRuleLibrary,
) -> list[FeeEvaluationLineItem]:
    lines: list[FeeEvaluationLineItem] = []
    for row in snapshot.rows:
        cell_value = _text(cell_lookup.get((group.confirmed_group_id, row.confirmed_row_id)))
        if not cell_value:
            continue
        parsed_tokens, token_warnings = parse_step_tokens(cell_value)
        step_tokens = tuple(token.raw_token for token in parsed_tokens)
        if not step_tokens:
            continue
        match = matcher.match_test_item(row.test_item)
        rule = match.rule
        warnings = tuple(
            FeeEvaluationWarning(
                code="step_token_parse_warning",
                message=message,
                scope=f"group:{group.group_key}:row:{row.confirmed_row_id}",
            )
            for message in token_warnings
        )
        lines.append(
            _build_line_item(
                group=group,
                row=row,
                snapshot=snapshot,
                step_tokens=step_tokens,
                rule=rule,
                rule_version_id=library.version.version_id if rule is not None else None,
                match_reason=match.match_reason,
                unmatched_review_reason=match.review_reason,
                warnings=warnings,
            )
        )
    return lines


def _build_line_item(
    *,
    group: ConfirmedMatrixGroup,
    row: ConfirmedMatrixRow,
    snapshot: ConfirmedMatrixSnapshot,
    step_tokens: tuple[str, ...],
    rule: FeeRule | None,
    rule_version_id: str | None,
    match_reason: str,
    unmatched_review_reason: str | None,
    warnings: tuple[FeeEvaluationWarning, ...],
) -> FeeEvaluationLineItem:
    calculation = (
        _no_rule_match(unmatched_review_reason)
        if rule is None
        else _calculate_line(
            rule=rule,
            group=group,
            step_tokens=step_tokens,
            warnings=warnings,
        )
    )
    return FeeEvaluationLineItem(
        line_id=f"{snapshot.version.confirmed_matrix_id}:{group.group_key}:{row.confirmed_row_id}",
        status=calculation.status,
        review_required=calculation.review_required,
        review_reason=calculation.review_reason,
        confirmed_matrix_id=snapshot.version.confirmed_matrix_id,
        confirmed_revision=snapshot.version.confirmed_revision,
        group_key=group.group_key.strip(),
        group_label=group.group_label.strip(),
        confirmed_group_id=group.confirmed_group_id,
        sample_quantity_expression=_text(group.sample_quantity_expression),
        confirmed_row_id=row.confirmed_row_id,
        source_row_id=row.source_row_snapshot_id,
        row_order=row.row_order,
        test_item=_text(row.test_item),
        section=_text(row.source_section),
        method=_text(row.method),
        condition=_text(row.condition),
        requirement=_text(row.requirement),
        step_tokens=step_tokens,
        matched_rule_id=rule.rule_id if rule is not None else None,
        matched_rule_version_id=rule_version_id,
        matched_rule_name=rule.display_name if rule is not None else None,
        match_reason=match_reason,
        calculation_strategy=rule.calculation_strategy if rule is not None else None,
        unit_label=rule.unit_label if rule is not None else "",
        unit_price=rule.unit_price.amount if rule is not None else None,
        units=calculation.units,
        base_fee=calculation.base_fee,
        discount_percent=calculation.discount_percent,
        testing_fee=calculation.testing_fee,
        warnings=warnings,
    )


def _calculate_line(
    *,
    rule: FeeRule,
    group: ConfirmedMatrixGroup,
    step_tokens: tuple[str, ...],
    warnings: tuple[FeeEvaluationWarning, ...],
) -> _CalculationResult:
    if warnings:
        return _review("Step token parse warning requires operator review.", rule)
    if rule.review_required:
        return _review(_review_reason_for_rule(rule), rule)
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
    return _review(_review_reason_for_rule(rule), rule)


def _calculated(rule: FeeRule, units: Decimal) -> _CalculationResult:
    discount_percent = _ZERO
    unit_price = rule.unit_price.amount or _ZERO
    base_fee = rule.base_fee.amount or _ZERO
    testing_fee = unit_price * units * (Decimal("1") - discount_percent / Decimal("100")) + base_fee
    return _CalculationResult(
        status="calculated",
        review_required=False,
        review_reason=None,
        units=units,
        base_fee=base_fee,
        discount_percent=discount_percent,
        testing_fee=testing_fee,
    )


def _review(reason: str, rule: FeeRule) -> _CalculationResult:
    return _CalculationResult(
        status="review_required",
        review_required=True,
        review_reason=reason,
        units=None,
        base_fee=rule.base_fee.amount,
        discount_percent=_ZERO,
        testing_fee=None,
    )


def _no_rule_match(review_reason: str | None) -> _CalculationResult:
    return _CalculationResult(
        status="no_rule_match",
        review_required=True,
        review_reason=review_reason or "No fee rule match.",
        units=None,
        base_fee=None,
        discount_percent=None,
        testing_fee=None,
    )


def _review_reason_for_rule(rule: FeeRule) -> str:
    if rule.calculation_strategy == "per_photo":
        return "Photo count is not available from Matrix authority."
    if rule.calculation_strategy == "per_reading":
        return "Reading count derivation is not defined in TASK_286."
    if rule.calculation_strategy == "per_cycle":
        return "Cycle count derivation is not defined in TASK_286."
    if rule.calculation_strategy == "per_hour":
        return "Day-to-hour fee conversion is not defined in TASK_286."
    if rule.calculation_strategy in {"manual_required", "unknown"}:
        return rule.review_reason or "Matched fee rule requires operator review."
    if rule.review_required:
        return rule.review_reason or "Matched fee rule requires operator review."
    return "Fee line requires operator review."


def _plain_decimal_quantity(value: str) -> Decimal | None:
    text = value.strip()
    if not _PLAIN_NON_NEGATIVE_DECIMAL.fullmatch(text):
        return None
    return Decimal(text)


def _text(value: str | None) -> str:
    return (value or "").strip()
