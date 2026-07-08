"""Build read-only Fee Evaluation drafts from active Confirmed Matrix authority."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from backend.application.confirmed_matrix_fee_draft_models import (
    BuildConfirmedMatrixFeeDraftCommand,
    ConfirmedMatrixAuthorityStore,
    FeeDraftStatus,
    FeeEvaluationDraft,
    FeeEvaluationGroup,
    FeeEvaluationHeader,
    FeeEvaluationLineItem,
    FeeEvaluationWarning,
    FeeLineStatus,
)
from backend.application.confirmed_matrix_fee_manual_defaults import (
    build_report_preparation_line,
    build_sample_preparation_line,
)
from backend.application.confirmed_matrix_fee_step_quantities import (
    StepQuantityLookup,
    build_step_quantity_contexts,
    build_step_quantity_lookup,
)
from backend.domain import (
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
)
from backend.modules.fee_evaluation import (
    FeeDefaultFillContext,
    FeeFieldMetadata,
    FeeRule,
    FeeRuleLibrary,
    FeeRuleMatcher,
    FeeStepQuantityContext,
    build_fee_default_fill,
    load_active_fee_rule_library,
)
from backend.modules.test_plan.matrix_step_sequence_validation import parse_step_tokens

_ZERO = Decimal("0")


class ConfirmedMatrixFeeDraftNotFoundError(LookupError):
    """Raised when no active confirmed Matrix authority exists for a project."""


class ConfirmedMatrixFeeDraftError(ValueError):
    """Raised when confirmed Matrix fee draft data cannot be built."""


@dataclass(frozen=True, slots=True)
class _CalculationResult:
    status: FeeLineStatus
    review_required: bool
    review_reason: str | None
    spend_time: Decimal | None
    unit_label: str
    unit_price: Decimal | None
    units: Decimal | None
    base_fee: Decimal | None
    discount_percent: Decimal | None
    testing_fee: Decimal | None
    field_metadata: tuple[FeeFieldMetadata, ...]


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
        manual_line_items = (
            build_report_preparation_line(
                snapshot=snapshot,
                rule_version_id=library.version.version_id,
            ),
        )
        line_items = tuple(
            item
            for group in groups
            for item in (*group.manual_line_items, *group.line_items)
        ) + manual_line_items
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
            manual_line_items=manual_line_items,
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
    if any(
        item.review_required
        for group in groups
        for item in (*group.manual_line_items, *group.line_items)
    ):
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
    step_quantity_lookup = build_step_quantity_lookup(snapshot)
    matcher = FeeRuleMatcher(library)
    groups: list[FeeEvaluationGroup] = []
    for group in snapshot.groups:
        lines = _build_group_lines(
            group=group,
            snapshot=snapshot,
            cell_lookup=cell_lookup,
            step_quantity_lookup=step_quantity_lookup,
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
                manual_line_items=(
                    build_sample_preparation_line(
                        group=group,
                        snapshot=snapshot,
                        rule_version_id=library.version.version_id,
                    ),
                ),
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
    step_quantity_lookup: StepQuantityLookup,
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
        step_quantities = build_step_quantity_contexts(
            group=group,
            row=row,
            parsed_tokens=parsed_tokens,
            step_quantity_lookup=step_quantity_lookup,
        )
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
                step_quantities=step_quantities,
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
    step_quantities: tuple[FeeStepQuantityContext, ...],
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
            row=row,
            step_tokens=step_tokens,
            step_quantities=step_quantities,
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
        spend_time=_decimal_text(calculation.spend_time) or _text(row.day_expression),
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
        unit_label=calculation.unit_label,
        unit_price=calculation.unit_price,
        units=calculation.units,
        base_fee=calculation.base_fee,
        discount_percent=calculation.discount_percent,
        testing_fee=calculation.testing_fee,
        field_metadata=calculation.field_metadata,
        warnings=warnings,
    )


def _calculate_line(
    *,
    rule: FeeRule,
    group: ConfirmedMatrixGroup,
    row: ConfirmedMatrixRow,
    step_tokens: tuple[str, ...],
    step_quantities: tuple[FeeStepQuantityContext, ...],
    warnings: tuple[FeeEvaluationWarning, ...],
) -> _CalculationResult:
    if warnings:
        return _review("Step token parse warning requires operator review.", rule)
    default_fill = build_fee_default_fill(
        rule=rule,
        context=FeeDefaultFillContext(
            test_item=_text(row.test_item),
            method=_text(row.method),
            condition=_text(row.condition),
            requirement=_text(row.requirement),
            sample_quantity_expression=_text(group.sample_quantity_expression),
            spend_time=_text(row.day_expression),
            step_tokens=step_tokens,
            step_quantities=step_quantities,
        ),
    )
    status: FeeLineStatus = default_fill.status
    return _CalculationResult(
        status=status,
        review_required=default_fill.review_required,
        review_reason=default_fill.review_reason,
        spend_time=default_fill.spend_time,
        unit_label=default_fill.unit_label,
        unit_price=default_fill.unit_price,
        units=default_fill.units,
        base_fee=default_fill.base_fee,
        discount_percent=default_fill.discount_percent,
        testing_fee=default_fill.testing_fee,
        field_metadata=default_fill.field_metadata,
    )


def _review(reason: str, rule: FeeRule) -> _CalculationResult:
    return _CalculationResult(
        status="review_required",
        review_required=True,
        review_reason=reason,
        spend_time=None,
        unit_label=rule.unit_label,
        unit_price=rule.unit_price.amount,
        units=None,
        base_fee=rule.base_fee.amount,
        discount_percent=_ZERO,
        testing_fee=None,
        field_metadata=(),
    )


def _no_rule_match(review_reason: str | None) -> _CalculationResult:
    return _CalculationResult(
        status="no_rule_match",
        review_required=True,
        review_reason=review_reason or "No fee rule match.",
        spend_time=None,
        unit_label="",
        unit_price=None,
        units=None,
        base_fee=None,
        discount_percent=None,
        testing_fee=None,
        field_metadata=(),
    )


def _text(value: str | None) -> str:
    return (value or "").strip()


def _decimal_text(value: Decimal | None) -> str:
    if value is None:
        return ""
    return format(value, "f")
