"""Lazy non-destructive bootstrap from active confirmed Matrix contact plans."""

from __future__ import annotations

import json
from hashlib import sha256
from uuid import uuid4

from backend.application.contact_measurement_plan_identity import (
    build_candidate_subject_key,
    build_target_key,
)
from backend.domain import ConfirmedMatrixSnapshot
from backend.infrastructure.storage.models_contact_measurement_plan_authority import (
    MeasurementPlanFamilySnapshotModel,
    MeasurementPlanRevisionModel,
    MeasurementPlanRootModel,
    MeasurementPlanTargetSnapshotModel,
)
from backend.infrastructure.storage.repositories.contact_measurement_plan_authority import ContactMeasurementPlanAuthorityRepository


class ContactMeasurementPlanBootstrapError(ValueError):
    """Raised when legacy bootstrap cannot prove authority consistency."""


class ContactMeasurementPlanBootstrapService:
    """Create or repair one non-destructive authority root from legacy data."""

    def __init__(
        self,
        repository: ContactMeasurementPlanAuthorityRepository,
        clock,
        id_factory=lambda: uuid4().hex,
    ) -> None:
        self._repository = repository
        self._clock = clock
        self._ids = id_factory

    def bootstrap(self, snapshot: ConfirmedMatrixSnapshot, actor: str = "system") -> str | None:
        payload = _bootstrap_payload(snapshot)
        if not payload:
            return None
        fingerprint = _fingerprint(payload)
        provenance = _provenance(snapshot, fingerprint)

        with self._repository.transaction():
            root = self._repository.get_root(snapshot.version.project_id)
            if root is None:
                root, revision = self._create_root(snapshot, actor, fingerprint, provenance)
            else:
                revision = self._existing_bootstrap_revision(root, provenance)

            _recover_or_verify_targets(
                repository=self._repository,
                revision=revision,
                payload=payload,
                id_factory=self._ids,
            )
            self._repository.flush()
            return root.measurement_plan_root_id

    def _create_root(
        self,
        snapshot: ConfirmedMatrixSnapshot,
        actor: str,
        fingerprint: str,
        provenance: str,
    ) -> tuple[MeasurementPlanRootModel, MeasurementPlanRevisionModel]:
        now = self._clock()
        root_id = f"cmpr-{self._ids()}"
        revision_id = f"cmprv-{self._ids()}"
        root = MeasurementPlanRootModel(
            measurement_plan_root_id=root_id,
            project_id=snapshot.version.project_id,
            active_confirmed_revision_id=revision_id,
            editable_revision_id=None,
            created_at=now,
            updated_at=now,
        )
        revision = MeasurementPlanRevisionModel(
            measurement_plan_revision_id=revision_id,
            measurement_plan_root_id=root_id,
            revision_sequence=1,
            parent_revision_id=None,
            state="confirmed",
            revision_fingerprint=fingerprint,
            base_confirmed_matrix_id=snapshot.version.confirmed_matrix_id,
            base_matrix_revision=snapshot.version.confirmed_revision,
            matrix_binding_fingerprint=fingerprint,
            bootstrap_provenance=provenance,
            created_by=actor,
            created_at=now,
            updated_at=now,
            confirmed_by=actor,
            confirmed_at=now,
            superseded_at=None,
            superseded_reason=None,
        )
        self._repository.add(root, revision)
        self._repository.audit(root_id, "bootstrap", actor, now, revision_id)
        return root, revision

    def _existing_bootstrap_revision(
        self,
        root: MeasurementPlanRootModel,
        provenance: str,
    ) -> MeasurementPlanRevisionModel:
        revision = self._repository.get_active_revision(root.project_id)
        if (
            revision is None
            or revision.state != "confirmed"
            or revision.bootstrap_provenance != provenance
        ):
            raise ContactMeasurementPlanBootstrapError(
                "authority_corrupt: existing contact measurement authority "
                "does not match legacy bootstrap provenance."
            )
        return revision


def _bootstrap_payload(snapshot: ConfirmedMatrixSnapshot) -> list[dict[str, object]]:
    groups = {group.confirmed_group_id: group for group in snapshot.groups}
    rows = {row.confirmed_row_id: row for row in snapshot.rows}
    payload: list[dict[str, object]] = []
    for quantity in snapshot.step_quantities:
        plan = quantity.contact_plan
        if plan is None or plan.contact_kind not in {"llcr", "cr_specified_current"}:
            continue
        group = groups.get(quantity.confirmed_group_id)
        row = rows.get(quantity.confirmed_row_id)
        if group is None or row is None:
            raise ContactMeasurementPlanBootstrapError(
                "authority_corrupt: confirmed contact plan target has no Matrix lineage."
            )
        group_anchor = group.source_group_snapshot_id or (
            f"manual-group-{group.confirmed_group_id}"
        )
        row_anchor = row.source_row_snapshot_id or f"manual-row-{row.confirmed_row_id}"
        stable_key = build_target_key(
            group.source_group_snapshot_id,
            None if group.source_group_snapshot_id else group_anchor,
            row.source_row_snapshot_id,
            None if row.source_row_snapshot_id else row_anchor,
            quantity.step_sequence,
            quantity.step_suffix_note,
        )
        try:
            readings = int(plan.readings_per_sample or 0)
            families = [
                {
                    "family_id": family.family_id,
                    "family_ordinal": index,
                    "label": family.family_label,
                    "count_per_sample": int(family.count_per_sample or 0),
                    "record_label": family.record_label,
                    "record_prefix": family.record_prefix,
                    "included": bool(family.included),
                    "is_custom": bool(family.is_custom),
                }
                for index, family in enumerate(plan.families)
            ]
        except ValueError as exc:
            raise ContactMeasurementPlanBootstrapError(
                "authority_corrupt: legacy contact plan contains a non-integer count."
            ) from exc
        payload.append(
            {
                "stable_target_key": stable_key,
                "candidate_subject_key": build_candidate_subject_key(
                    snapshot.version.confirmed_matrix_id,
                    group.confirmed_group_id,
                    row.confirmed_row_id,
                    quantity.step_sequence,
                    quantity.step_suffix_note,
                ),
                "source_group_snapshot_id": group.source_group_snapshot_id,
                "manual_group_anchor_id": (
                    None if group.source_group_snapshot_id else group_anchor
                ),
                "source_row_snapshot_id": row.source_row_snapshot_id,
                "manual_row_anchor_id": (
                    None if row.source_row_snapshot_id else row_anchor
                ),
                "confirmed_matrix_id": snapshot.version.confirmed_matrix_id,
                "confirmed_group_id": group.confirmed_group_id,
                "confirmed_row_id": row.confirmed_row_id,
                "matrix_revision": snapshot.version.confirmed_revision,
                "step_sequence": quantity.step_sequence,
                "step_suffix_note": (quantity.step_suffix_note or "").strip().lower(),
                "group_label": group.group_label,
                "test_item": row.test_item,
                "contact_kind": plan.contact_kind,
                "sample_quantity_expression": group.sample_quantity_expression,
                "eligible": True,
                "included": bool(plan.included),
                "is_override": bool(plan.is_override),
                "coverage_state": plan.coverage_status,
                "exclusion_reason": plan.exclusion_reason,
                "impact_status": "unchanged",
                "impact_reason": None,
                "readings_per_sample": readings,
                "families": families,
            }
        )
    return sorted(payload, key=lambda item: str(item["stable_target_key"]))


def _recover_or_verify_targets(
    *,
    repository: ContactMeasurementPlanAuthorityRepository,
    revision: MeasurementPlanRevisionModel,
    payload: list[dict[str, object]],
    id_factory,
) -> None:
    expected_keys = {str(item["stable_target_key"]) for item in payload}
    existing = {
        target.stable_target_key: target
        for target in repository.targets(revision.measurement_plan_revision_id)
    }
    if set(existing) - expected_keys:
        raise ContactMeasurementPlanBootstrapError(
            "authority_corrupt: bootstrap revision has unexpected target rows."
        )
    for target_payload in payload:
        key = str(target_payload["stable_target_key"])
        target = existing.get(key)
        if target is None:
            target = _new_target(revision, target_payload, id_factory)
            repository.add(target)
        elif not _target_matches(target, target_payload):
            raise ContactMeasurementPlanBootstrapError(
                "authority_corrupt: bootstrap target differs from legacy payload."
            )
        _recover_or_verify_families(repository, target, target_payload, id_factory)


def _new_target(
    revision: MeasurementPlanRevisionModel,
    payload: dict[str, object],
    id_factory,
) -> MeasurementPlanTargetSnapshotModel:
    return MeasurementPlanTargetSnapshotModel(
        measurement_plan_target_snapshot_id=f"cmpt-{id_factory()}",
        measurement_plan_revision_id=revision.measurement_plan_revision_id,
        stable_target_key=str(payload["stable_target_key"]),
        source_group_snapshot_id=_optional(payload, "source_group_snapshot_id"),
        manual_group_anchor_id=_optional(payload, "manual_group_anchor_id"),
        source_row_snapshot_id=_optional(payload, "source_row_snapshot_id"),
        manual_row_anchor_id=_optional(payload, "manual_row_anchor_id"),
        confirmed_matrix_id=str(payload["confirmed_matrix_id"]),
        confirmed_group_id=str(payload["confirmed_group_id"]),
        confirmed_row_id=str(payload["confirmed_row_id"]),
        matrix_revision=int(payload["matrix_revision"]),
        step_sequence=int(payload["step_sequence"]),
        step_suffix_note=str(payload["step_suffix_note"]),
        group_label=str(payload["group_label"]),
        test_item=str(payload["test_item"]),
        contact_kind=str(payload["contact_kind"]),
        sample_quantity_expression=str(payload["sample_quantity_expression"]),
        eligible=bool(payload["eligible"]),
        included=bool(payload["included"]),
        is_override=bool(payload["is_override"]),
        coverage_state=str(payload["coverage_state"]),
        exclusion_reason=_optional(payload, "exclusion_reason"),
        impact_status=str(payload["impact_status"]),
        impact_reason=_optional(payload, "impact_reason"),
        binding_evidence_fingerprint=revision.revision_fingerprint,
        readings_per_sample=int(payload["readings_per_sample"]),
    )


def _target_matches(
    target: MeasurementPlanTargetSnapshotModel,
    payload: dict[str, object],
) -> bool:
    return all(
        getattr(target, field) == expected
        for field, expected in _target_comparison_values(payload).items()
    )


def _target_comparison_values(payload: dict[str, object]) -> dict[str, object]:
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
        "is_override",
        "coverage_state",
        "exclusion_reason",
        "impact_status",
        "impact_reason",
        "readings_per_sample",
    )
    return {field: payload[field] for field in fields}


def _recover_or_verify_families(
    repository: ContactMeasurementPlanAuthorityRepository,
    target: MeasurementPlanTargetSnapshotModel,
    payload: dict[str, object],
    id_factory,
) -> None:
    expected = list(payload["families"])
    existing = {family.family_id: family for family in repository.families(target.measurement_plan_target_snapshot_id)}
    expected_ids = {str(family["family_id"]) for family in expected}
    if set(existing) - expected_ids:
        raise ContactMeasurementPlanBootstrapError(
            "authority_corrupt: bootstrap target has unexpected family rows."
        )
    for family_payload in expected:
        family_id = str(family_payload["family_id"])
        existing_family = existing.get(family_id)
        if existing_family is None:
            repository.add(
                MeasurementPlanFamilySnapshotModel(
                    measurement_plan_family_snapshot_id=f"cmpf-{id_factory()}",
                    measurement_plan_target_snapshot_id=(
                        target.measurement_plan_target_snapshot_id
                    ),
                    family_id=family_id,
                    family_ordinal=int(family_payload["family_ordinal"]),
                    label=str(family_payload["label"]),
                    count_per_sample=int(family_payload["count_per_sample"]),
                    record_label=str(family_payload["record_label"]),
                    record_prefix=str(family_payload["record_prefix"]),
                    included=bool(family_payload["included"]),
                    is_custom=bool(family_payload["is_custom"]),
                )
            )
        elif not _family_matches(existing_family, family_payload):
            raise ContactMeasurementPlanBootstrapError(
                "authority_corrupt: bootstrap family differs from legacy payload."
            )


def _family_matches(
    family: MeasurementPlanFamilySnapshotModel,
    payload: dict[str, object],
) -> bool:
    return all(
        getattr(family, field) == expected
        for field, expected in payload.items()
    )


def _fingerprint(payload: list[dict[str, object]]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8")).hexdigest()


def _provenance(snapshot: ConfirmedMatrixSnapshot, fingerprint: str) -> str:
    return (
        "cmp-bootstrap:v1"
        f"|project:{snapshot.version.project_id}"
        f"|matrix:{snapshot.version.confirmed_matrix_id}"
        f"|legacy:{fingerprint}"
    )


def _optional(payload: dict[str, object], key: str) -> str | None:
    value = payload[key]
    return None if value is None else str(value)
