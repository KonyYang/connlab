"""Pure source-context and provenance policy for Fee pricing-draft V2."""

from __future__ import annotations

from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportValues,
)
from backend.application.fee_evaluation_pricing_draft_serialization import (
    edited_values_to_payload,
)
from backend.application.fee_evaluation_pricing_draft_v2_contract import (
    FeePricingDraftSourceContext,
    canonical_fingerprint,
)


def source_context_for_values(
    *,
    confirmed_matrix_id: str,
    confirmed_revision: int,
    fee_rule_version_id: str,
    values: FeeEvaluationEditedExportValues,
) -> FeePricingDraftSourceContext:
    """Bind a V2 save to the authority values that seeded its defaults."""
    return FeePricingDraftSourceContext(
        confirmed_matrix_id=confirmed_matrix_id,
        confirmed_revision=confirmed_revision,
        fee_rule_version_id=fee_rule_version_id,
        point_profile_status="not_started",
        point_profile_revision_id=None,
        point_profile_revision_sequence=None,
        point_profile_fingerprint=None,
        automatic_defaults_fingerprint=canonical_fingerprint(
            edited_values_to_payload(values)
        ),
    )


def infer_operator_provenance(
    values: FeeEvaluationEditedExportValues,
    *,
    automatic_defaults: FeeEvaluationEditedExportValues | None = None,
) -> dict[str, tuple[str, ...]]:
    """Persist fields that differ from the server's current automatic defaults."""
    fields = (
        "spend_time",
        "unit_price",
        "unit_type",
        "base_fee",
        "discount",
        "notes",
    )
    if automatic_defaults is None:
        return {row.source_line_id: fields for row in values.rows}
    defaults = {row.source_line_id: row for row in automatic_defaults.rows}
    return {
        row.source_line_id: tuple(
            field
            for field in fields
            if (default := defaults.get(row.source_line_id)) is None
            or getattr(row, field) != getattr(default, field)
        )
        for row in values.rows
    }
