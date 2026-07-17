"""Build V2 Fee pricing-draft source context from confirmed authorities."""

from __future__ import annotations

from dataclasses import asdict

from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportValues,
)
from backend.application.fee_evaluation_pricing_draft_v2_policy import (
    source_context_for_values,
)
from backend.application.fee_evaluation_pricing_draft_v2_contract import canonical_fingerprint


def build_authority_source_context(
    *,
    project_id: str,
    confirmed_matrix_id: str,
    confirmed_revision: int,
    fee_rule_version_id: str,
    fallback_values: FeeEvaluationEditedExportValues,
    automatic_defaults_provider: object | None,
    point_profile_provider: object | None,
    measurement_plan_provider: object | None = None,
):
    """Return one deterministic V2 source context, using only read-only authority ports."""
    defaults = current_automatic_values(
        project_id, automatic_defaults_provider, fallback_values
    )
    context = source_context_for_values(
        confirmed_matrix_id=confirmed_matrix_id,
        confirmed_revision=confirmed_revision,
        fee_rule_version_id=fee_rule_version_id,
        values=defaults,
    )
    profile = (
        getattr(point_profile_provider, "get_effective")(project_id)
        if point_profile_provider is not None
        else None
    )
    if profile is None:
        profile = type("MissingProfile", (), {"status": "not_started"})()
    measurement_plan = (
        getattr(measurement_plan_provider, "get_effective")(project_id)
        if measurement_plan_provider is not None
        else None
    )
    if measurement_plan is None:
        measurement_plan = type("MissingMeasurementPlan", (), {"status": "not_started"})()
    return type(context)(
        confirmed_matrix_id=context.confirmed_matrix_id,
        confirmed_revision=context.confirmed_revision,
        fee_rule_version_id=context.fee_rule_version_id,
        point_profile_status=str(getattr(profile, "status", "authority_corrupt")),
        point_profile_revision_id=getattr(profile, "revision_id", None),
        point_profile_revision_sequence=getattr(profile, "revision_sequence", None),
        point_profile_fingerprint=getattr(profile, "fingerprint", None),
        automatic_defaults_fingerprint=context.automatic_defaults_fingerprint,
        measurement_plan_status=str(getattr(measurement_plan, "status", "authority_corrupt")),
        measurement_plan_revision_id=getattr(measurement_plan, "revision_id", None),
        measurement_plan_revision_sequence=getattr(measurement_plan, "revision_sequence", None),
        measurement_plan_fingerprint=_measurement_plan_fingerprint(measurement_plan),
    )


def _measurement_plan_fingerprint(plan: object) -> str | None:
    existing = getattr(plan, "fingerprint", None)
    if existing:
        return str(existing)
    status = str(getattr(plan, "status", "not_started"))
    revision_id = getattr(plan, "revision_id", None)
    if status == "not_started" and revision_id is None:
        return None
    targets = getattr(plan, "targets", ())
    return canonical_fingerprint(
        {
            "status": status,
            "revision_id": revision_id,
            "revision_sequence": getattr(plan, "revision_sequence", None),
            "targets": [asdict(target) for target in targets],
            "diagnostics": list(getattr(plan, "diagnostics", ())),
        }
    )


def current_automatic_values(
    project_id: str,
    provider: object | None,
    fallback: FeeEvaluationEditedExportValues,
) -> FeeEvaluationEditedExportValues:
    """Return current backend defaults without applying a saved pricing draft."""
    if provider is None:
        return fallback
    build = getattr(provider, "build_draft", None)
    if build is None:
        return fallback
    from backend.application.confirmed_matrix_fee_draft_models import (
        BuildConfirmedMatrixFeeDraftCommand,
    )
    from backend.application.matrix_fee_rebase_promotion_values import (
        edited_values_from_fee_draft,
    )

    return edited_values_from_fee_draft(
        build(BuildConfirmedMatrixFeeDraftCommand(project_id=project_id))
    )
