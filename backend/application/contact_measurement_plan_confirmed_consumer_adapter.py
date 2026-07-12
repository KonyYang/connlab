"""Typed confirmed Measurement Plan facts for formal downstream consumers."""

from __future__ import annotations

from dataclasses import dataclass

from backend.application.contact_measurement_plan_projection_service import (
    ContactMeasurementPlanProjectionService,
)
from backend.domain import (
    ConfirmedMatrixSnapshot,
    MatrixStepContactFamily,
    MatrixStepContactPlan,
)


@dataclass(frozen=True, slots=True)
class EffectiveContactMeasurementTarget:
    """One confirmed target matched by explicit Matrix lineage only."""

    confirmed_group_id: str
    confirmed_row_id: str
    step_sequence: int
    step_suffix_note: str
    contact_plan: MatrixStepContactPlan


@dataclass(frozen=True, slots=True)
class EffectiveContactMeasurementPlan:
    """Read-only formal-consumer projection with explicit rollback policy."""

    status: str
    snapshot: ConfirmedMatrixSnapshot
    revision_id: str | None
    revision_sequence: int | None
    targets: tuple[EffectiveContactMeasurementTarget, ...]
    diagnostics: tuple[str, ...]

    @property
    def legacy_fallback_allowed(self) -> bool:
        return self.status in {"not_started", "disabled"}

    @property
    def lookup(self) -> dict[tuple[str, str, int, str], EffectiveContactMeasurementTarget]:
        return {
            (
                target.confirmed_group_id,
                target.confirmed_row_id,
                target.step_sequence,
                target.step_suffix_note,
            ): target
            for target in self.targets
        }


class ContactMeasurementPlanConfirmedConsumerAdapter:
    """Join effective independent authority to active Matrix lineage for consumers."""

    def __init__(self, *, projection_service, confirmed_store) -> None:
        self._projection_service: ContactMeasurementPlanProjectionService = projection_service
        self._confirmed_store = confirmed_store

    def get_effective(self, project_id: str) -> EffectiveContactMeasurementPlan | None:
        snapshot = self._confirmed_store.get_active_by_project(project_id)
        if snapshot is None:
            return None
        projected = self._projection_service.get_effective(project_id)
        targets = tuple(_target_from_payload(item) for item in projected.targets)
        status = projected.status
        if status == "complete" and not targets:
            status = "empty"
        return EffectiveContactMeasurementPlan(
            status=status,
            snapshot=snapshot,
            revision_id=projected.revision_id,
            revision_sequence=projected.revision_sequence,
            targets=targets,
            diagnostics=projected.diagnostics,
        )


def _target_from_payload(payload: dict[str, object]) -> EffectiveContactMeasurementTarget:
    families = tuple(
        MatrixStepContactFamily(
            family_id=str(family["family_id"]),
            family_label=str(family["label"]),
            count_per_sample=str(family["count_per_sample"]),
            record_label=str(family["record_label"]),
            record_prefix=str(family["record_prefix"]),
            included=bool(family["included"]),
            is_custom=bool(family["is_custom"]),
        )
        for family in payload.get("families", ())
        if isinstance(family, dict)
    )
    plan = MatrixStepContactPlan(
        contact_kind=str(payload["contact_kind"]),
        coverage_status="included" if bool(payload["included"]) else "excluded",
        included=bool(payload["included"]),
        exclusion_reason=None,
        is_override=False,
        readings_per_sample=str(payload["readings_per_sample"]),
        families=families,
    )
    return EffectiveContactMeasurementTarget(
        confirmed_group_id=str(payload["confirmed_group_id"]),
        confirmed_row_id=str(payload["confirmed_row_id"]),
        step_sequence=int(payload["step_sequence"]),
        step_suffix_note=str(payload.get("step_suffix_note") or "").strip(),
        contact_plan=plan,
    )
