"""Independent contact-measurement plan authority read models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class MeasurementPlanFamilySnapshot:
    family_id: str
    family_ordinal: int
    label: str
    count_per_sample: int
    record_label: str
    record_prefix: str
    included: bool
    is_custom: bool


@dataclass(frozen=True, slots=True)
class MeasurementPlanTargetSnapshot:
    stable_target_key: str
    source_group_snapshot_id: str | None
    manual_group_anchor_id: str | None
    source_row_snapshot_id: str | None
    manual_row_anchor_id: str | None
    confirmed_matrix_id: str
    confirmed_group_id: str
    confirmed_row_id: str
    matrix_revision: int
    step_sequence: int
    step_suffix_note: str
    group_label: str
    test_item: str
    contact_kind: str
    sample_quantity_expression: str
    included: bool
    is_override: bool
    readings_per_sample: int
    families: tuple[MeasurementPlanFamilySnapshot, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class MeasurementPlanRevisionSnapshot:
    revision_id: str
    root_id: str
    revision_sequence: int
    state: str
    revision_fingerprint: str
    base_confirmed_matrix_id: str
    base_matrix_revision: int
    matrix_binding_fingerprint: str
    targets: tuple[MeasurementPlanTargetSnapshot, ...] = field(default_factory=tuple)
