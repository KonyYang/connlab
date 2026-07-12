"""Snapshot-copy and impact-persistence helpers for plan revision lifecycle."""

from __future__ import annotations

from backend.application.contact_measurement_plan_identity import (
    build_impact_identity_key,
)
from backend.infrastructure.storage.models_contact_measurement_plan_authority import (
    MeasurementPlanFamilySnapshotModel,
    MeasurementPlanImpactModel,
    MeasurementPlanTargetSnapshotModel,
)
from backend.infrastructure.storage.repositories.contact_measurement_plan_authority import (
    ContactMeasurementPlanAuthorityRepository,
)


def copy_targets(
    *,
    repository: ContactMeasurementPlanAuthorityRepository,
    source_revision_id: str,
    target_revision_id: str,
    id_factory,
) -> None:
    """Copy immutable target/family snapshots into a new editable revision."""
    for source_target in repository.targets(source_revision_id):
        target = MeasurementPlanTargetSnapshotModel(
            measurement_plan_target_snapshot_id=f"cmpt-{id_factory()}",
            measurement_plan_revision_id=target_revision_id,
            stable_target_key=source_target.stable_target_key,
            source_group_snapshot_id=source_target.source_group_snapshot_id,
            manual_group_anchor_id=source_target.manual_group_anchor_id,
            source_row_snapshot_id=source_target.source_row_snapshot_id,
            manual_row_anchor_id=source_target.manual_row_anchor_id,
            confirmed_matrix_id=source_target.confirmed_matrix_id,
            confirmed_group_id=source_target.confirmed_group_id,
            confirmed_row_id=source_target.confirmed_row_id,
            matrix_revision=source_target.matrix_revision,
            step_sequence=source_target.step_sequence,
            step_suffix_note=source_target.step_suffix_note,
            group_label=source_target.group_label,
            test_item=source_target.test_item,
            contact_kind=source_target.contact_kind,
            sample_quantity_expression=source_target.sample_quantity_expression,
            eligible=source_target.eligible,
            included=source_target.included,
            is_override=source_target.is_override,
            coverage_state=source_target.coverage_state,
            exclusion_reason=source_target.exclusion_reason,
            impact_status=source_target.impact_status,
            impact_reason=source_target.impact_reason,
            binding_evidence_fingerprint=source_target.binding_evidence_fingerprint,
            readings_per_sample=source_target.readings_per_sample,
        )
        repository.add(target)
        for source_family in repository.families(
            source_target.measurement_plan_target_snapshot_id
        ):
            repository.add(
                MeasurementPlanFamilySnapshotModel(
                    measurement_plan_family_snapshot_id=f"cmpf-{id_factory()}",
                    measurement_plan_target_snapshot_id=(
                        target.measurement_plan_target_snapshot_id
                    ),
                    family_id=source_family.family_id,
                    family_ordinal=source_family.family_ordinal,
                    label=source_family.label,
                    count_per_sample=source_family.count_per_sample,
                    record_label=source_family.record_label,
                    record_prefix=source_family.record_prefix,
                    included=source_family.included,
                    is_custom=source_family.is_custom,
                )
            )


def apply_target_replacement(
    target,
    replacement: dict[str, object],
    fingerprint: str,
) -> None:
    """Apply a fully resolved canonical Matrix target to a draft target row."""
    fields = (
        "stable_target_key",
        "source_group_snapshot_id",
        "manual_group_anchor_id",
        "source_row_snapshot_id",
        "manual_row_anchor_id",
        "confirmed_matrix_id",
        "confirmed_group_id",
        "confirmed_row_id",
        "matrix_revision",
        "step_sequence",
        "step_suffix_note",
        "group_label",
        "test_item",
        "contact_kind",
        "sample_quantity_expression",
        "eligible",
        "included",
        "coverage_state",
        "exclusion_reason",
        "impact_status",
        "impact_reason",
        "readings_per_sample",
    )
    for field in fields:
        setattr(target, field, replacement[field])
    target.binding_evidence_fingerprint = fingerprint


def persist_impacts(
    *,
    repository: ContactMeasurementPlanAuthorityRepository,
    root_id: str,
    revision_id: str,
    targets,
    result,
    after_fingerprint: str,
    created_at: str,
    id_factory,
) -> None:
    """Store idempotent classifier results with non-null dedupe identities."""
    targets_by_key = {target.stable_target_key: target for target in targets}
    for stable_target_key, category in result.categories_by_target.items():
        if category != "unchanged":
            target = targets_by_key[stable_target_key]
            _persist_impact(
                repository=repository,
                root_id=root_id,
                revision_id=revision_id,
                stable_target_key=stable_target_key,
                category=category,
                before_fingerprint=target.binding_evidence_fingerprint,
                after_fingerprint=after_fingerprint,
                created_at=created_at,
                id_factory=id_factory,
            )
    for stable_target_key in result.new_target_keys:
        _persist_impact(
            repository=repository,
            root_id=root_id,
            revision_id=revision_id,
            stable_target_key=None,
            impact_subject_key=result.candidate_subjects_by_target[stable_target_key],
            category="structural_review_required",
            before_fingerprint="none",
            after_fingerprint=after_fingerprint,
            created_at=created_at,
            id_factory=id_factory,
        )


def _persist_impact(
    *,
    repository: ContactMeasurementPlanAuthorityRepository,
    root_id: str,
    revision_id: str,
    stable_target_key: str,
    impact_subject_key: str | None = None,
    category: str,
    before_fingerprint: str,
    after_fingerprint: str,
    created_at: str,
    id_factory,
) -> None:
    severity = (
        "review_required"
        if category in {"structural_review_required", "projection_review_required"}
        else "info"
    )
    repository.add_or_verify_impact(
        MeasurementPlanImpactModel(
            measurement_plan_impact_id=f"cmpi-{id_factory()}",
            measurement_plan_root_id=root_id,
            editable_revision_id=revision_id,
            stable_target_key=stable_target_key,
            impact_subject_key=impact_subject_key or stable_target_key,
            impact_identity_key=build_impact_identity_key(
                category,
                impact_subject_key or stable_target_key,
                before_fingerprint,
                after_fingerprint,
            ),
            category=category,
            severity=severity,
            before_evidence_fingerprint=before_fingerprint,
            after_evidence_fingerprint=after_fingerprint,
            resolution_state="open",
            reason=category.replace("_", " "),
            created_at=created_at,
        )
    )
