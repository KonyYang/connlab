"""Build Fee Evaluation line items from one confirmed Matrix group."""

from __future__ import annotations

from decimal import Decimal

from backend.application.confirmed_matrix_fee_base_fee_policy import (
    FeeCalculationResult as _CalculationResult,
    apply_matrix_fee_line_policies as _apply_matrix_fee_line_policies,
)
from backend.application.confirmed_matrix_fee_cr_specified_current import (
    resolve_cr_specified_current_readings,
)
from backend.application.confirmed_matrix_fee_draft_models import (
    FeeEvaluationGroup,
    FeeEvaluationLineItem,
    FeeEvaluationWarning,
)
from backend.application.confirmed_matrix_fee_duration_authority import (
    resolve_confirmed_duration_authority,
)
from backend.application.confirmed_matrix_fee_manual_defaults import (
    _decimal_text,
    _text,
    build_sample_preparation_line,
)
from backend.application.confirmed_matrix_fee_step_quantities import (
    StepQuantityLookup,
    build_profile_reading_contexts,
    build_step_quantity_contexts,
    build_step_quantity_lookup,
)
from backend.application import confirmed_matrix_fee_rule_resolution
from backend.application.contact_measurement_plan_confirmed_consumer_adapter import (
    EffectiveContactMeasurementPlan,
)
from backend.application.contact_point_profile_confirmed_consumer_adapter import (
    EffectiveConfirmedPointProfile,
)
from backend.domain import ConfirmedMatrixGroup, ConfirmedMatrixRow, ConfirmedMatrixSnapshot
from backend.modules.fee_evaluation import (
    CrSpecifiedCurrentAuthority,
    FeeDefaultFillContext,
    FeeRule,
    FeeRuleLibrary,
    FeeRuleMatchResult,
    FeeRuleMatcher,
    FeeStepQuantityContext,
    build_fee_default_fill,
)
from backend.modules.fee_evaluation.fee_default_fill_models import FeeDurationAuthority
from backend.modules.test_plan.matrix_step_sequence_validation import parse_step_tokens

_ZERO = Decimal("0")


class ConfirmedMatrixFeeDraftError(ValueError):
    """Raised when confirmed Matrix Fee draft data cannot be built."""


def build_groups(
    *,
    snapshot: ConfirmedMatrixSnapshot,
    library: FeeRuleLibrary,
    effective_contact_plan: EffectiveContactMeasurementPlan | None,
    effective_point_profile: EffectiveConfirmedPointProfile | None,
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
    rule_matches = confirmed_matrix_fee_rule_resolution.build_matrix_fee_rule_matches(
        rows=snapshot.rows,
        matcher=matcher,
        library=library,
    )
    groups: list[FeeEvaluationGroup] = []
    for group in snapshot.groups:
        lines = build_group_lines(
            group=group,
            snapshot=snapshot,
            cell_lookup=cell_lookup,
            step_quantity_lookup=step_quantity_lookup,
            rule_matches=rule_matches,
            library=library,
            effective_contact_plan=effective_contact_plan,
            effective_point_profile=effective_point_profile,
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


def build_group_lines(
    *,
    group: ConfirmedMatrixGroup,
    snapshot: ConfirmedMatrixSnapshot,
    cell_lookup: dict[tuple[str, str], str],
    step_quantity_lookup: StepQuantityLookup,
    rule_matches: dict[str, FeeRuleMatchResult],
    library: FeeRuleLibrary,
    effective_contact_plan: EffectiveContactMeasurementPlan | None,
    effective_point_profile: EffectiveConfirmedPointProfile | None,
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
        match = rule_matches[row.confirmed_row_id]
        rule = match.rule
        is_llcr = rule is not None and rule.rule_id == "fee_rule_llcr"
        uses_profile_default = (
            is_llcr
            and effective_point_profile is not None
            and effective_point_profile.is_usable
            and (
                effective_contact_plan is None
                or effective_contact_plan.legacy_fallback_allowed
            )
        )
        active_lookup = (
            {key: target.contact_plan for key, target in effective_contact_plan.lookup.items()}
            if effective_contact_plan is not None
            and not effective_contact_plan.legacy_fallback_allowed
            else None
        )
        if uses_profile_default:
            step_quantities = build_profile_reading_contexts(
                parsed_tokens=parsed_tokens,
                profile=effective_point_profile or _missing_point_profile(),
            )
        elif rule is not None and rule.rule_id == "fee_rule_contact_resistance_specified_current":
            step_quantities = resolve_cr_specified_current_readings(
                group=group,
                row=row,
                parsed_tokens=parsed_tokens,
                effective_plan=effective_contact_plan,
                effective_point_profile=effective_point_profile,
            )
        else:
            step_quantities = build_step_quantity_contexts(
                group=group,
                row=row,
                parsed_tokens=parsed_tokens,
                step_quantity_lookup=step_quantity_lookup,
                effective_contact_targets=active_lookup,
                effective_contact_status=(
                    effective_contact_plan.status if effective_contact_plan is not None else None
                ),
                is_llcr_or_specified_current=(
                    rule is not None
                    and rule.rule_id
                    in {"fee_rule_llcr", "fee_rule_contact_resistance_specified_current"}
                ),
            )
        warnings = tuple(
            FeeEvaluationWarning(
                code="step_token_parse_warning",
                message=message,
                scope=f"group:{group.group_key}:row:{row.confirmed_row_id}",
            )
            for message in token_warnings
        )
        duration_authority = (
            resolve_confirmed_duration_authority(
                group=group,
                row=row,
                step_sequence=parsed_tokens[0].sequence,
                step_suffix_note=parsed_tokens[0].suffix_note,
                authorities=snapshot.duration_authorities,
                expected_confirmed_matrix_id=snapshot.version.confirmed_matrix_id,
            )
            if len(parsed_tokens) == 1
            else None
        )
        lines.append(
            _build_line_item(
                group=group,
                row=row,
                snapshot=snapshot,
                step_tokens=step_tokens,
                step_quantities=step_quantities,
                duration_authority=duration_authority,
                rule=rule,
                rule_version_id=library.version.version_id if rule is not None else None,
                match_reason=match.match_reason,
                unmatched_review_reason=match.review_reason,
                warnings=warnings,
            )
        )
    return lines


def _missing_point_profile() -> EffectiveConfirmedPointProfile:
    return EffectiveConfirmedPointProfile(
        status="missing",
        readings_per_sample=None,
        revision_id=None,
        revision_sequence=None,
        fingerprint=None,
        lineage=None,
        message="Confirm Point Profile before calculating LLCR units.",
    )


def _build_line_item(
    *,
    group: ConfirmedMatrixGroup,
    row: ConfirmedMatrixRow,
    snapshot: ConfirmedMatrixSnapshot,
    step_tokens: tuple[str, ...],
    step_quantities: tuple[FeeStepQuantityContext, ...],
    duration_authority: FeeDurationAuthority | None,
    rule: FeeRule | None,
    rule_version_id: str | None,
    match_reason: str,
    unmatched_review_reason: str | None,
    warnings: tuple[FeeEvaluationWarning, ...],
) -> FeeEvaluationLineItem:
    cr_authority = step_quantities[0].cr_authority if step_quantities else None
    calculation = (
        _no_rule_match(unmatched_review_reason)
        if rule is None
        else _calculate_line(
            rule=rule,
            group=group,
            row=row,
            step_tokens=step_tokens,
            step_quantities=step_quantities,
            cr_authority=cr_authority,
            duration_authority=duration_authority,
            warnings=warnings,
        )
    )
    calculation = _apply_matrix_fee_line_policies(
        calculation=calculation,
        rule=rule,
        testing_fee_source=(
            cr_authority.source
            if rule is not None
            and rule.rule_id == "fee_rule_contact_resistance_specified_current"
            and cr_authority is not None
            and cr_authority.is_valid
            else rule.display_name if rule is not None else "No fee rule match"
        ),
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
    cr_authority: CrSpecifiedCurrentAuthority | None,
    duration_authority: FeeDurationAuthority | None,
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
            cr_authority=cr_authority,
            duration_authority=duration_authority,
        ),
    )
    return _CalculationResult(
        status=default_fill.status,
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
