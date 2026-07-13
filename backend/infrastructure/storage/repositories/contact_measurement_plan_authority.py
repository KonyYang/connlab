"""SQLite repository for independent contact-measurement plan authority."""

from __future__ import annotations

from contextlib import contextmanager
from collections.abc import Iterator
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.infrastructure.storage.models_contact_measurement_plan_authority import (
    MeasurementPlanAuditModel,
    MeasurementPlanFamilySnapshotModel,
    MeasurementPlanImpactModel,
    MeasurementPlanRevisionModel,
    MeasurementPlanRootModel,
    MeasurementPlanTargetSnapshotModel,
)


_FREEFORM_FAMILY_ID = re.compile(r"ff-(?P<kind>llcr|cr)-(?P<number>[1-9][0-9]*)")


class ContactMeasurementPlanAuthorityRepository:
    """Keep independent plan writes transactional and append-only by default."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_root(self, project_id: str) -> MeasurementPlanRootModel | None:
        return self._session.scalar(select(MeasurementPlanRootModel).where(MeasurementPlanRootModel.project_id == project_id))

    def get_revision(self, revision_id: str) -> MeasurementPlanRevisionModel | None:
        return self._session.get(MeasurementPlanRevisionModel, revision_id)

    def get_active_revision(self, project_id: str) -> MeasurementPlanRevisionModel | None:
        root = self.get_root(project_id)
        if root is None or root.active_confirmed_revision_id is None:
            return None
        return self.get_revision(root.active_confirmed_revision_id)

    def get_editable_revision(self, project_id: str) -> MeasurementPlanRevisionModel | None:
        root = self.get_root(project_id)
        if root is None or root.editable_revision_id is None:
            return None
        return self.get_revision(root.editable_revision_id)

    def targets(self, revision_id: str) -> list[MeasurementPlanTargetSnapshotModel]:
        statement = (
            select(MeasurementPlanTargetSnapshotModel)
            .where(
                MeasurementPlanTargetSnapshotModel.measurement_plan_revision_id
                == revision_id
            )
            .order_by(MeasurementPlanTargetSnapshotModel.stable_target_key)
        )
        return list(self._session.scalars(statement).all())

    def target_by_key(
        self,
        revision_id: str,
        stable_target_key: str,
    ) -> MeasurementPlanTargetSnapshotModel | None:
        statement = select(MeasurementPlanTargetSnapshotModel).where(
            MeasurementPlanTargetSnapshotModel.measurement_plan_revision_id == revision_id,
            MeasurementPlanTargetSnapshotModel.stable_target_key == stable_target_key,
        )
        return self._session.scalar(statement)

    def families(self, target_id: str) -> list[MeasurementPlanFamilySnapshotModel]:
        statement = (
            select(MeasurementPlanFamilySnapshotModel)
            .where(
                MeasurementPlanFamilySnapshotModel.measurement_plan_target_snapshot_id
                == target_id
            )
            .order_by(MeasurementPlanFamilySnapshotModel.family_ordinal)
        )
        return list(self._session.scalars(statement).all())

    def family_authorities_for_revision_kind(
        self,
        revision_id: str,
        contact_kind: str,
        excluding_target_id: str,
    ) -> list[tuple[str, str, str]]:
        """Return sibling freeform semantics before one target replacement."""
        statement = (
            select(
                MeasurementPlanFamilySnapshotModel.family_id,
                MeasurementPlanFamilySnapshotModel.label,
                MeasurementPlanFamilySnapshotModel.record_prefix,
            )
            .join(
                MeasurementPlanTargetSnapshotModel,
                MeasurementPlanTargetSnapshotModel.measurement_plan_target_snapshot_id
                == MeasurementPlanFamilySnapshotModel.measurement_plan_target_snapshot_id,
            )
            .where(
                MeasurementPlanTargetSnapshotModel.measurement_plan_revision_id
                == revision_id,
                MeasurementPlanTargetSnapshotModel.contact_kind == contact_kind,
                MeasurementPlanTargetSnapshotModel.measurement_plan_target_snapshot_id
                != excluding_target_id,
            )
        )
        return list(self._session.execute(statement).all())

    def family_id_high_water_by_kind(self, root_id: str) -> dict[str, int]:
        """Read historical freeform issuances without changing any authority rows."""
        statement = (
            select(
                MeasurementPlanTargetSnapshotModel.contact_kind,
                MeasurementPlanFamilySnapshotModel.family_id,
            )
            .join(
                MeasurementPlanFamilySnapshotModel,
                MeasurementPlanFamilySnapshotModel.measurement_plan_target_snapshot_id
                == MeasurementPlanTargetSnapshotModel.measurement_plan_target_snapshot_id,
            )
            .join(
                MeasurementPlanRevisionModel,
                MeasurementPlanRevisionModel.measurement_plan_revision_id
                == MeasurementPlanTargetSnapshotModel.measurement_plan_revision_id,
            )
            .where(MeasurementPlanRevisionModel.measurement_plan_root_id == root_id)
        )
        high_water = {"llcr": 0, "cr_specified_current": 0}
        for contact_kind, family_id in self._session.execute(statement):
            match = _FREEFORM_FAMILY_ID.fullmatch(family_id)
            if match is None:
                continue
            expected_kind = "llcr" if match.group("kind") == "llcr" else "cr_specified_current"
            if contact_kind == expected_kind:
                high_water[expected_kind] = max(high_water[expected_kind], int(match.group("number")))
        return high_water

    def impacts(self, revision_id: str) -> list[MeasurementPlanImpactModel]:
        statement = (
            select(MeasurementPlanImpactModel)
            .where(MeasurementPlanImpactModel.editable_revision_id == revision_id)
            .order_by(MeasurementPlanImpactModel.impact_identity_key)
        )
        return list(self._session.scalars(statement).all())

    def add_or_verify_impact(self, impact: MeasurementPlanImpactModel) -> None:
        """Idempotently add one classifier impact or reject divergent duplicate data."""
        statement = select(MeasurementPlanImpactModel).where(
            MeasurementPlanImpactModel.editable_revision_id
            == impact.editable_revision_id,
            MeasurementPlanImpactModel.impact_identity_key
            == impact.impact_identity_key,
        )
        existing = self._session.scalar(statement)
        if existing is None:
            self._session.add(impact)
            return
        fields = (
            "measurement_plan_root_id",
            "stable_target_key",
            "impact_subject_key",
            "category",
            "severity",
            "before_evidence_fingerprint",
            "after_evidence_fingerprint",
            "reason",
        )
        if any(getattr(existing, field) != getattr(impact, field) for field in fields):
            raise ValueError("authority_corrupt: impact identity has divergent payload.")

    def replace_families(
        self,
        target_id: str,
        families: tuple[dict[str, object], ...],
        id_factory,
    ) -> None:
        """Replace one editable target's family snapshot in the current transaction."""
        for family in self.families(target_id):
            self._session.delete(family)
        self._session.flush()
        for ordinal, family in enumerate(families):
            self._session.add(
                MeasurementPlanFamilySnapshotModel(
                    measurement_plan_family_snapshot_id=f"cmpf-{id_factory()}",
                    measurement_plan_target_snapshot_id=target_id,
                    family_id=str(family["family_id"]),
                    family_ordinal=ordinal,
                    label=str(family["label"]),
                    count_per_sample=int(family["count_per_sample"]),
                    record_label=str(family["record_label"]),
                    record_prefix=str(family["record_prefix"]),
                    included=bool(family["included"]),
                    is_custom=bool(family["is_custom"]),
                )
            )

    def unresolved_review_impacts(
        self,
        revision_id: str,
    ) -> list[MeasurementPlanImpactModel]:
        statement = select(MeasurementPlanImpactModel).where(
            MeasurementPlanImpactModel.editable_revision_id == revision_id,
            MeasurementPlanImpactModel.severity == "review_required",
            MeasurementPlanImpactModel.resolution_state == "open",
        )
        return list(self._session.scalars(statement).all())

    def resolve_candidate_rebind(
        self,
        revision_id: str,
        candidate_subject_key: str,
    ) -> bool:
        """Resolve the one candidate diagnostic consumed by an explicit rebind."""
        statement = select(MeasurementPlanImpactModel).where(
            MeasurementPlanImpactModel.editable_revision_id == revision_id,
            MeasurementPlanImpactModel.impact_subject_key == candidate_subject_key,
            MeasurementPlanImpactModel.severity == "review_required",
        )
        impact = self._session.scalar(statement)
        if impact is None:
            raise ValueError("authority_corrupt: candidate impact was not found.")
        if impact.resolution_state == "open":
            impact.resolution_state = "rebound"
            return True
        if impact.resolution_state == "rebound":
            return False
        raise ValueError("authority_corrupt: candidate impact has incompatible resolution.")

    def accept_compatible_impacts(self, revision_id: str) -> None:
        for impact in self.impacts(revision_id):
            if impact.severity == "info" and impact.resolution_state == "open":
                impact.resolution_state = "accepted"

    def add(self, *rows: object) -> None:
        self._session.add_all(rows)

    def audit(
        self,
        root_id: str,
        action: str,
        actor: str,
        occurred_at: str,
        revision_id: str | None = None,
        reason: str | None = None,
    ) -> None:
        audit_id = f"cmpa-{root_id}-{action}-{occurred_at}"
        self._session.add(
            MeasurementPlanAuditModel(
                measurement_plan_audit_id=audit_id,
                measurement_plan_root_id=root_id,
                measurement_plan_revision_id=revision_id,
                stable_target_key=None,
                action=action,
                actor=actor,
                occurred_at=occurred_at,
                reason=reason,
            )
        )

    def flush(self) -> None:
        self._session.flush()

    @contextmanager
    def transaction(self) -> Iterator[None]:
        """Provide savepoint rollback without taking ownership of request commits."""
        with self._session.begin_nested():
            yield
