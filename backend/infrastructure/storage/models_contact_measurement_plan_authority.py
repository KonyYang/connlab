"""Additive persistence models for independent contact-measurement plan authority."""

from __future__ import annotations

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.storage.database import Base


class MeasurementPlanRootModel(Base):
    __tablename__ = "measurement_plan_roots"
    measurement_plan_root_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.project_id"),
        unique=True,
        nullable=False,
        index=True,
    )
    active_confirmed_revision_id: Mapped[str | None] = mapped_column(
        ForeignKey("measurement_plan_revisions.measurement_plan_revision_id")
    )
    editable_revision_id: Mapped[str | None] = mapped_column(
        ForeignKey("measurement_plan_revisions.measurement_plan_revision_id")
    )
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(64), nullable=False)


class MeasurementPlanRevisionModel(Base):
    __tablename__ = "measurement_plan_revisions"
    __table_args__ = (
        UniqueConstraint(
            "measurement_plan_root_id",
            "revision_sequence",
            name="uq_measurement_plan_revision_sequence",
        ),
        CheckConstraint(
            "revision_sequence > 0",
            name="ck_measurement_plan_revision_positive",
        ),
        CheckConstraint(
            "state IN ('draft','needs_review','confirmed','superseded')",
            name="ck_measurement_plan_revision_state",
        ),
        Index(
            "uq_measurement_plan_confirmed_per_root",
            "measurement_plan_root_id",
            unique=True,
            sqlite_where=text("state = 'confirmed'"),
        ),
        Index(
            "uq_measurement_plan_editable_per_root",
            "measurement_plan_root_id",
            unique=True,
            sqlite_where=text("state IN ('draft', 'needs_review')"),
        ),
    )
    measurement_plan_revision_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    measurement_plan_root_id: Mapped[str] = mapped_column(
        ForeignKey("measurement_plan_roots.measurement_plan_root_id"),
        nullable=False,
        index=True,
    )
    revision_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_revision_id: Mapped[str | None] = mapped_column(ForeignKey("measurement_plan_revisions.measurement_plan_revision_id"))
    state: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    revision_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    base_confirmed_matrix_id: Mapped[str] = mapped_column(
        ForeignKey("confirmed_matrix_versions.confirmed_matrix_id"),
        nullable=False,
    )
    base_matrix_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    matrix_binding_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    bootstrap_provenance: Mapped[str | None] = mapped_column(Text, unique=True)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(64), nullable=False)
    confirmed_by: Mapped[str | None] = mapped_column(String(255))
    confirmed_at: Mapped[str | None] = mapped_column(String(64))
    superseded_at: Mapped[str | None] = mapped_column(String(64))
    superseded_reason: Mapped[str | None] = mapped_column(Text)


class MeasurementPlanTargetSnapshotModel(Base):
    __tablename__ = "measurement_plan_target_snapshots"
    __table_args__ = (
        UniqueConstraint("measurement_plan_revision_id", "stable_target_key", name="uq_measurement_plan_target_key"),
        CheckConstraint("step_sequence > 0 AND matrix_revision > 0 AND readings_per_sample >= 0", name="ck_measurement_plan_target_numbers"),
        CheckConstraint("contact_kind IN ('llcr','cr_specified_current')", name="ck_measurement_plan_target_kind"),
        CheckConstraint(
            "(source_group_snapshot_id IS NOT NULL "
            "AND length(trim(source_group_snapshot_id)) > 0 "
            "AND manual_group_anchor_id IS NULL) "
            "OR (source_group_snapshot_id IS NULL "
            "AND manual_group_anchor_id IS NOT NULL "
            "AND length(trim(manual_group_anchor_id)) > 0)",
            name="ck_measurement_plan_group_anchor_xor",
        ),
        CheckConstraint(
            "(source_row_snapshot_id IS NOT NULL "
            "AND length(trim(source_row_snapshot_id)) > 0 "
            "AND manual_row_anchor_id IS NULL) "
            "OR (source_row_snapshot_id IS NULL "
            "AND manual_row_anchor_id IS NOT NULL "
            "AND length(trim(manual_row_anchor_id)) > 0)",
            name="ck_measurement_plan_row_anchor_xor",
        ),
        CheckConstraint(
            "stable_target_key LIKE 'cmp-target:v1|%'",
            name="ck_measurement_plan_target_key_shape",
        ),
    )
    measurement_plan_target_snapshot_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    measurement_plan_revision_id: Mapped[str] = mapped_column(ForeignKey("measurement_plan_revisions.measurement_plan_revision_id"), nullable=False, index=True)
    stable_target_key: Mapped[str] = mapped_column(Text, nullable=False)
    source_group_snapshot_id: Mapped[str | None] = mapped_column(String(64))
    manual_group_anchor_id: Mapped[str | None] = mapped_column(String(64))
    source_row_snapshot_id: Mapped[str | None] = mapped_column(String(64))
    manual_row_anchor_id: Mapped[str | None] = mapped_column(String(64))
    confirmed_matrix_id: Mapped[str] = mapped_column(ForeignKey("confirmed_matrix_versions.confirmed_matrix_id"), nullable=False)
    confirmed_group_id: Mapped[str] = mapped_column(String(64), nullable=False)
    confirmed_row_id: Mapped[str] = mapped_column(String(64), nullable=False)
    matrix_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    step_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    step_suffix_note: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    group_label: Mapped[str] = mapped_column(Text, nullable=False)
    test_item: Mapped[str] = mapped_column(Text, nullable=False)
    contact_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    sample_quantity_expression: Mapped[str] = mapped_column(Text, nullable=False)
    eligible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    included: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_override: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    coverage_state: Mapped[str] = mapped_column(String(32), nullable=False, default="included")
    exclusion_reason: Mapped[str | None] = mapped_column(Text)
    impact_status: Mapped[str] = mapped_column(String(48), nullable=False, default="unchanged")
    impact_reason: Mapped[str | None] = mapped_column(Text)
    binding_evidence_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    readings_per_sample: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class MeasurementPlanFamilySnapshotModel(Base):
    __tablename__ = "measurement_plan_family_snapshots"
    __table_args__ = (
        UniqueConstraint("measurement_plan_target_snapshot_id", "family_ordinal", name="uq_measurement_plan_family_order"),
        UniqueConstraint("measurement_plan_target_snapshot_id", "family_id", name="uq_measurement_plan_family_id"),
        CheckConstraint("family_ordinal >= 0 AND count_per_sample >= 0", name="ck_measurement_plan_family_numbers"),
    )
    measurement_plan_family_snapshot_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    measurement_plan_target_snapshot_id: Mapped[str] = mapped_column(ForeignKey("measurement_plan_target_snapshots.measurement_plan_target_snapshot_id"), nullable=False, index=True)
    family_id: Mapped[str] = mapped_column(String(64), nullable=False)
    family_ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    count_per_sample: Mapped[int] = mapped_column(Integer, nullable=False)
    record_label: Mapped[str] = mapped_column(Text, nullable=False)
    record_prefix: Mapped[str] = mapped_column(String(64), nullable=False)
    included: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_custom: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class MeasurementPlanImpactModel(Base):
    __tablename__ = "measurement_plan_impacts"
    __table_args__ = (
        UniqueConstraint(
            "editable_revision_id",
            "impact_identity_key",
            name="uq_measurement_plan_impact_identity",
        ),
        CheckConstraint(
            "impact_subject_key LIKE 'cmp-target:v1|%' "
            "OR impact_subject_key LIKE 'cmp-candidate:v1|%'",
            name="ck_measurement_plan_impact_subject_shape",
        ),
        CheckConstraint(
            "impact_identity_key LIKE 'cmp-impact:v1|%'",
            name="ck_measurement_plan_impact_identity_shape",
        ),
    )
    measurement_plan_impact_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    measurement_plan_root_id: Mapped[str] = mapped_column(ForeignKey("measurement_plan_roots.measurement_plan_root_id"), nullable=False, index=True)
    editable_revision_id: Mapped[str] = mapped_column(ForeignKey("measurement_plan_revisions.measurement_plan_revision_id"), nullable=False, index=True)
    stable_target_key: Mapped[str | None] = mapped_column(Text)
    impact_subject_key: Mapped[str] = mapped_column(Text, nullable=False)
    impact_identity_key: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(48), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    before_evidence_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    after_evidence_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    resolution_state: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)


class MeasurementPlanAuditModel(Base):
    __tablename__ = "measurement_plan_audits"
    measurement_plan_audit_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    measurement_plan_root_id: Mapped[str] = mapped_column(ForeignKey("measurement_plan_roots.measurement_plan_root_id"), nullable=False, index=True)
    measurement_plan_revision_id: Mapped[str | None] = mapped_column(ForeignKey("measurement_plan_revisions.measurement_plan_revision_id"), index=True)
    stable_target_key: Mapped[str | None] = mapped_column(Text)
    action: Mapped[str] = mapped_column(String(48), nullable=False)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    occurred_at: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
