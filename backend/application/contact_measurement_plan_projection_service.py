"""Read-only independent contact-measurement plan projection boundary."""

from __future__ import annotations

from dataclasses import dataclass

from backend.application.contact_measurement_plan_impact_classifier import (
    classify_revision_targets,
)
from backend.infrastructure.storage.repositories.contact_measurement_plan_authority import (
    ContactMeasurementPlanAuthorityRepository,
)


@dataclass(frozen=True, slots=True)
class ContactMeasurementPlanProjection:
    status: str
    project_id: str
    revision_id: str | None
    revision_sequence: int | None
    targets: tuple[dict[str, object], ...]
    diagnostics: tuple[str, ...] = ()


class ContactMeasurementPlanProjectionService:
    """Return only confirmed, compatible authority; drafts never enter projection."""

    def __init__(
        self,
        repository: ContactMeasurementPlanAuthorityRepository,
        enabled: bool,
        confirmed_store=None,
    ) -> None:
        self._repository = repository
        self._enabled = enabled
        self._confirmed_store = confirmed_store

    def get_effective(self, project_id: str) -> ContactMeasurementPlanProjection:
        if not self._enabled:
            return ContactMeasurementPlanProjection(
                "disabled",
                project_id,
                None,
                None,
                (),
                ("Independent contact measurement authority is disabled.",),
            )
        root = self._repository.get_root(project_id)
        if root is None:
            return ContactMeasurementPlanProjection(
                "not_started",
                project_id,
                None,
                None,
                (),
            )
        revision = self._repository.get_active_revision(project_id)
        if revision is None:
            return ContactMeasurementPlanProjection(
                "authority_corrupt",
                project_id,
                None,
                None,
                (),
                (
                    "Contact measurement authority requires maintenance before "
                    "it can be projected.",
                ),
            )
        stored_targets = self._repository.targets(revision.measurement_plan_revision_id)
        categories_by_target: dict[str, str] = {}
        new_target_count = 0
        current_matrix = (
            self._confirmed_store.get_active_by_project(project_id)
            if self._confirmed_store is not None
            else None
        )
        if current_matrix is not None:
            impact_result = classify_revision_targets(
                tuple(stored_targets),
                current_matrix,
            )
            categories_by_target = impact_result.categories_by_target
            new_target_count = len(impact_result.new_target_keys)
        targets: list[dict[str, object]] = []
        omitted_count = 0
        for target in stored_targets:
            category = categories_by_target.get(
                target.stable_target_key,
                target.impact_status,
            )
            if category in {
                "structural_review_required",
                "projection_review_required",
            }:
                omitted_count += 1
                continue
            families = tuple(
                {
                    "family_id": family.family_id,
                    "family_ordinal": family.family_ordinal,
                    "label": family.label,
                    "count_per_sample": family.count_per_sample,
                    "record_label": family.record_label,
                    "record_prefix": family.record_prefix,
                    "included": family.included,
                    "is_custom": family.is_custom,
                }
                for family in self._repository.families(
                    target.measurement_plan_target_snapshot_id
                )
            )
            targets.append(
                {
                    "stable_target_key": target.stable_target_key,
                    "confirmed_group_id": getattr(target, "confirmed_group_id", ""),
                    "confirmed_row_id": getattr(target, "confirmed_row_id", ""),
                    "step_sequence": getattr(target, "step_sequence", 0),
                    "step_suffix_note": getattr(target, "step_suffix_note", ""),
                    "contact_kind": target.contact_kind,
                    "included": target.included,
                    "readings_per_sample": target.readings_per_sample,
                    "families": families,
                }
            )
        diagnostics: tuple[str, ...] = ()
        if new_target_count:
            diagnostics += (
                f"{new_target_count} current Matrix target requires review and is not projected.",
            )
        if omitted_count:
            diagnostics += (
                f"{omitted_count} target requires review and is not projected.",
            )
        status = "complete"
        if new_target_count:
            status = "needs_review"
        elif omitted_count:
            status = "partial_compatible"
        return ContactMeasurementPlanProjection(
            status,
            project_id,
            revision.measurement_plan_revision_id,
            revision.revision_sequence,
            tuple(targets),
            diagnostics,
        )

    def get_workspace(self, project_id: str) -> dict[str, object]:
        """Return the editable revision when present, otherwise confirmed authority."""
        root = self._repository.get_root(project_id)
        if root is None:
            return {
                "status": "not_started",
                "project_id": project_id,
                "active_confirmed_revision_id": None,
                "editable_revision_id": None,
                "editable_revision_state": None,
                "editable_revision_fingerprint": None,
                "targets": [],
            }
        editable = self._repository.get_editable_revision(project_id)
        active = self._repository.get_active_revision(project_id)
        revision = editable or active
        if revision is None:
            return {
                "status": "authority_corrupt",
                "project_id": project_id,
                "active_confirmed_revision_id": root.active_confirmed_revision_id,
                "editable_revision_id": root.editable_revision_id,
                "editable_revision_state": None,
                "editable_revision_fingerprint": None,
                "targets": [],
            }
        targets = [
            {
                "stable_target_key": target.stable_target_key,
                "contact_kind": target.contact_kind,
                "included": target.included,
                "readings_per_sample": target.readings_per_sample,
                "families": [
                    {
                        "family_id": family.family_id,
                        "family_ordinal": family.family_ordinal,
                        "label": family.label,
                        "count_per_sample": family.count_per_sample,
                        "record_label": family.record_label,
                        "record_prefix": family.record_prefix,
                        "included": family.included,
                        "is_custom": family.is_custom,
                    }
                    for family in self._repository.families(
                        target.measurement_plan_target_snapshot_id
                    )
                ],
            }
            for target in self._repository.targets(
                revision.measurement_plan_revision_id
            )
        ]
        return {
            "status": "ready",
            "project_id": project_id,
            "active_confirmed_revision_id": root.active_confirmed_revision_id,
            "editable_revision_id": root.editable_revision_id,
            "editable_revision_state": editable.state if editable else None,
            "editable_revision_fingerprint": (
                editable.revision_fingerprint if editable else None
            ),
            "targets": targets,
        }
