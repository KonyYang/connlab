"""Build automatic Fee defaults and safety from one authority snapshot."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Protocol

from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    MatrixBasicFillWorkbook,
)
from backend.application.confirmed_matrix_fee_draft_build_result import (
    ConfirmedMatrixFeeAuthorityBuildResult,
)
from backend.application.confirmed_matrix_fee_draft_models import (
    BuildConfirmedMatrixFeeDraftCommand,
    FeeEvaluationDraft,
    FeeEvaluationLineItem,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportValues,
    FeeEvaluationEditedRowIdentity,
    FeeEvaluationManualRowIdentity,
    edited_row_identity,
    edited_row_lookup,
    manual_row_identity,
    validate_supported_manual_rows,
)
from backend.application.fee_evaluation_pricing_draft_prior_defaults_attestation import (
    FeePricingDraftAutomaticFieldSafety,
    FeePricingDraftAutomaticRowSafety,
)
from backend.application.fee_evaluation_pricing_draft_v2_authority_context import (
    build_authority_source_context_from_facts,
)
from backend.application.fee_evaluation_pricing_draft_v2_contract import (
    FeePricingDraftSourceContext,
)
from backend.domain import ConfirmedMatrixSnapshot

_CR_RULE_ID = "fee_rule_contact_resistance_specified_current"
_CR_REQUIRED_FIELDS = {"unit_price", "unit_label", "units", "testing_fee"}


class ConfirmedMatrixFeeAuthorityBuildProvider(Protocol):
    """Private single-build port required by pricing-draft persistence."""

    def build_authority_result(
        self,
        command: BuildConfirmedMatrixFeeDraftCommand,
    ) -> ConfirmedMatrixFeeAuthorityBuildResult:
        """Return one immutable authority build."""


@dataclass(frozen=True, slots=True)
class FeePricingDraftAutomaticBuildResult:
    """Canonical automatic values, safety, and lineage from one build."""

    fee_draft: FeeEvaluationDraft
    confirmed_matrix: ConfirmedMatrixSnapshot
    automatic_values: FeeEvaluationEditedExportValues
    ordered_row_identities: tuple[
        FeeEvaluationEditedRowIdentity | FeeEvaluationManualRowIdentity, ...
    ]
    row_safety: tuple[FeePricingDraftAutomaticRowSafety, ...]
    source_context: FeePricingDraftSourceContext


def build_current_pricing_defaults(
    project_id: str,
    provider: ConfirmedMatrixFeeAuthorityBuildProvider,
) -> FeePricingDraftAutomaticBuildResult:
    """Derive every pricing-default fact from exactly one provider call."""
    authority = provider.build_authority_result(
        BuildConfirmedMatrixFeeDraftCommand(project_id=project_id)
    )
    from backend.application.matrix_fee_rebase_promotion_values import (
        edited_values_from_fee_draft,
    )

    values = edited_values_from_fee_draft(authority.draft)
    identities = tuple(edited_row_identity(row) for row in values.rows) + tuple(
        manual_row_identity(row) for row in values.manual_rows
    )
    safety = _row_safety(authority.draft, values)
    context = build_authority_source_context_from_facts(
        confirmed_matrix=authority.confirmed_matrix,
        fee_rule_version_id=authority.rule_library.version.version_id,
        automatic_defaults=values,
        point_profile=authority.effective_point_profile,
        measurement_plan=authority.effective_measurement_plan,
    )
    return FeePricingDraftAutomaticBuildResult(
        fee_draft=authority.draft,
        confirmed_matrix=authority.confirmed_matrix,
        automatic_values=values,
        ordered_row_identities=identities,
        row_safety=safety,
        source_context=context,
    )


def build_current_pricing_defaults_if_supported(
    project_id: str,
    provider: object | None,
) -> FeePricingDraftAutomaticBuildResult | None:
    """Use the single-build path when a compatibility provider supports it."""
    if provider is None or getattr(provider, "build_authority_result", None) is None:
        return None
    return build_current_pricing_defaults(project_id, provider)  # type: ignore[arg-type]


def validate_edited_values_against_captured_matrix(
    values: FeeEvaluationEditedExportValues,
    basic_fill: MatrixBasicFillWorkbook,
) -> None:
    """Validate edited rows against the Matrix captured by the authority build."""
    edited_row_lookup(values, basic_fill)
    validate_supported_manual_rows(values.manual_rows, basic_fill)


def merge_existing_inactive_rows(
    *,
    incoming: FeeEvaluationEditedExportValues,
    existing: FeeEvaluationEditedExportValues | None,
) -> FeeEvaluationEditedExportValues:
    """Preserve server-side hidden rows when clients save active rows only."""
    if incoming.inactive_rows or existing is None or not existing.inactive_rows:
        return incoming
    return replace(incoming, inactive_rows=existing.inactive_rows)


def _row_safety(
    draft: FeeEvaluationDraft,
    values: FeeEvaluationEditedExportValues,
) -> tuple[FeePricingDraftAutomaticRowSafety, ...]:
    lines = {
        (line.confirmed_group_id, line.confirmed_row_id, token, index): line
        for group in draft.groups
        for line in group.line_items
        for index, token in enumerate(line.step_tokens)
    }
    result: list[FeePricingDraftAutomaticRowSafety] = []
    for row in values.rows:
        line = lines.get(
            (row.confirmed_group_id, row.confirmed_row_id, row.step_token, row.step_index)
        )
        if line is None:
            result.append(_missing_line_safety(edited_row_identity(row)))
            continue
        result.append(_line_safety(edited_row_identity(row), line))
    return tuple(result)


def _line_safety(
    identity: FeeEvaluationEditedRowIdentity,
    line: FeeEvaluationLineItem,
) -> FeePricingDraftAutomaticRowSafety:
    is_cr = line.matched_rule_id == _CR_RULE_ID
    metadata_by_field = {item.field: item for item in line.field_metadata}
    required_fields = (
        _CR_REQUIRED_FIELDS
        if is_cr
        else {
            item.field
            for item in line.field_metadata
            if item.state == "auto_filled"
        }
    )
    field_safety = tuple(
        FeePricingDraftAutomaticFieldSafety(
            field=item.field,
            state=item.state,
            source=item.source,
            required_for_rebase=item.field in required_fields,
        )
        for item in line.field_metadata
    )
    required_are_safe = all(
        field in metadata_by_field
        and metadata_by_field[field].state == "auto_filled"
        and (not is_cr or _is_confirmed_cr_source(metadata_by_field[field].source))
        for field in required_fields
    )
    safe = bool(required_fields) and required_are_safe
    return FeePricingDraftAutomaticRowSafety(
        identity=identity,
        row_kind="matrix",
        matched_rule_id=line.matched_rule_id,
        automatic_fields=field_safety,
        safe_for_rebase=safe,
        diagnostic_code="safe" if safe else "automatic_authority_review_required",
        diagnostic_text=None if safe else line.review_reason or "Automatic authority is unavailable.",
    )


def _missing_line_safety(
    identity: FeeEvaluationEditedRowIdentity,
) -> FeePricingDraftAutomaticRowSafety:
    return FeePricingDraftAutomaticRowSafety(
        identity=identity,
        row_kind="matrix",
        matched_rule_id=None,
        automatic_fields=(),
        safe_for_rebase=False,
        diagnostic_code="automatic_row_unmatched",
        diagnostic_text="Automatic Fee row could not be matched before flattening.",
    )


def _is_confirmed_cr_source(value: str | None) -> bool:
    return bool(
        value
        and value.startswith(
            ("Confirmed CR Measurement Plan", "Confirmed Project Point Profile")
        )
    )
