"""Build V2 Fee pricing-draft source context from confirmed authorities."""

from __future__ import annotations

from dataclasses import asdict

from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    MatrixBasicFillWorkbook,
)
from backend.application.fee_evaluation_edited_export_values import (
    FeeEvaluationEditedExportValues,
)
from backend.application.fee_evaluation_pricing_draft_v2_policy import (
    source_context_for_values,
)
from backend.application.fee_evaluation_pricing_draft_v2_contract import canonical_fingerprint
from backend.domain import ConfirmedMatrixSnapshot
from backend.modules.fee_evaluation import load_active_fee_rule_library


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


def build_legacy_source_context(
    *,
    context: object,
    fallback_values: FeeEvaluationEditedExportValues,
    automatic_defaults_provider: object | None,
    point_profile_provider: object | None,
    measurement_plan_provider: object | None,
):
    """Retain the pre-attestation provider path for compatibility callers."""
    return build_authority_source_context(
        project_id=str(getattr(context, "project_id")),
        confirmed_matrix_id=str(getattr(context, "confirmed_matrix_id")),
        confirmed_revision=int(getattr(context, "confirmed_revision")),
        fee_rule_version_id=str(getattr(context, "fee_rule_version_id")),
        fallback_values=fallback_values,
        automatic_defaults_provider=automatic_defaults_provider,
        point_profile_provider=point_profile_provider,
        measurement_plan_provider=measurement_plan_provider,
    )


def basic_fill_context_values(basic_fill: MatrixBasicFillWorkbook) -> dict[str, object]:
    """Return current context constructor values from one basic-fill snapshot."""
    library = load_active_fee_rule_library()
    return {
        "project_id": basic_fill.header.project_id,
        "confirmed_matrix_id": basic_fill.header.confirmed_matrix_id,
        "confirmed_revision": basic_fill.header.confirmed_revision,
        "fee_rule_version_id": library.version.version_id,
    }


def build_authority_source_context_from_facts(
    *,
    confirmed_matrix: ConfirmedMatrixSnapshot,
    fee_rule_version_id: str,
    automatic_defaults: FeeEvaluationEditedExportValues,
    point_profile: object | None,
    measurement_plan: object | None,
):
    """Build source context without rereading any authority provider."""
    context = source_context_for_values(
        confirmed_matrix_id=confirmed_matrix.version.confirmed_matrix_id,
        confirmed_revision=confirmed_matrix.version.confirmed_revision,
        fee_rule_version_id=fee_rule_version_id,
        values=automatic_defaults,
    )
    profile = point_profile or type("MissingProfile", (), {"status": "not_started"})()
    plan = measurement_plan or type("MissingPlan", (), {"status": "not_started"})()
    return type(context)(
        confirmed_matrix_id=context.confirmed_matrix_id,
        confirmed_revision=context.confirmed_revision,
        fee_rule_version_id=context.fee_rule_version_id,
        point_profile_status=str(getattr(profile, "status", "authority_corrupt")),
        point_profile_revision_id=getattr(profile, "revision_id", None),
        point_profile_revision_sequence=getattr(profile, "revision_sequence", None),
        point_profile_fingerprint=getattr(profile, "fingerprint", None),
        automatic_defaults_fingerprint=context.automatic_defaults_fingerprint,
        measurement_plan_status=str(getattr(plan, "status", "authority_corrupt")),
        measurement_plan_revision_id=getattr(plan, "revision_id", None),
        measurement_plan_revision_sequence=getattr(plan, "revision_sequence", None),
        measurement_plan_fingerprint=_measurement_plan_fingerprint(plan),
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
