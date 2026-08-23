"""Additive project-level Point Profile authority persistence models."""

from __future__ import annotations

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.storage.database import Base


class ContactPointProfileRootModel(Base):
    __tablename__ = "contact_point_profile_roots"

    contact_point_profile_root_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False, unique=True, index=True)
    active_confirmed_revision_id: Mapped[str | None] = mapped_column(
        ForeignKey("contact_point_profile_revisions.contact_point_profile_revision_id")
    )
    editable_revision_id: Mapped[str | None] = mapped_column(
        ForeignKey("contact_point_profile_revisions.contact_point_profile_revision_id")
    )
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(64), nullable=False)


class ContactPointProfileRevisionModel(Base):
    __tablename__ = "contact_point_profile_revisions"
    __table_args__ = (
        UniqueConstraint("contact_point_profile_root_id", "revision_sequence", name="uq_contact_point_profile_revision_sequence"),
        CheckConstraint("revision_sequence > 0", name="ck_contact_point_profile_revision_positive"),
        CheckConstraint("state IN ('draft','confirmed','superseded')", name="ck_contact_point_profile_revision_state"),
        Index("uq_contact_point_profile_confirmed_per_root", "contact_point_profile_root_id", unique=True, sqlite_where=text("state = 'confirmed'")),
        Index("uq_contact_point_profile_editable_per_root", "contact_point_profile_root_id", unique=True, sqlite_where=text("state = 'draft'")),
    )

    contact_point_profile_revision_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    contact_point_profile_root_id: Mapped[str] = mapped_column(
        ForeignKey("contact_point_profile_roots.contact_point_profile_root_id"), nullable=False, index=True
    )
    revision_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_revision_id: Mapped[str | None] = mapped_column(
        ForeignKey("contact_point_profile_revisions.contact_point_profile_revision_id")
    )
    state: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    revision_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    delta_r_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("1")
    )
    bootstrap_provenance: Mapped[str | None] = mapped_column(Text, unique=True)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(64), nullable=False)
    confirmed_by: Mapped[str | None] = mapped_column(String(255))
    confirmed_at: Mapped[str | None] = mapped_column(String(64))
    superseded_at: Mapped[str | None] = mapped_column(String(64))
    superseded_reason: Mapped[str | None] = mapped_column(Text)


class ContactPointProfileCategoryModel(Base):
    __tablename__ = "contact_point_profile_categories"
    __table_args__ = (
        UniqueConstraint("contact_point_profile_revision_id", "category_ordinal", name="uq_contact_point_profile_category_order"),
        UniqueConstraint("contact_point_profile_revision_id", "category_id", name="uq_contact_point_profile_category_id"),
        CheckConstraint("category_ordinal >= 0 AND count_per_sample >= 0", name="ck_contact_point_profile_category_numbers"),
        CheckConstraint("included = 0 OR count_per_sample > 0", name="ck_contact_point_profile_included_count"),
        CheckConstraint("point_expression IS NULL OR length(trim(point_expression)) > 0", name="ck_contact_point_profile_point_expression_nonblank"),
        Index("uq_contact_point_profile_included_label", "contact_point_profile_revision_id", "normalized_label_key", unique=True, sqlite_where=text("included = 1")),
        Index("uq_contact_point_profile_included_prefix", "contact_point_profile_revision_id", "normalized_prefix_key", unique=True, sqlite_where=text("included = 1")),
    )

    contact_point_profile_category_snapshot_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    contact_point_profile_revision_id: Mapped[str] = mapped_column(
        ForeignKey("contact_point_profile_revisions.contact_point_profile_revision_id"), nullable=False, index=True
    )
    category_id: Mapped[str] = mapped_column(String(64), nullable=False)
    category_ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_label_key: Mapped[str] = mapped_column(Text, nullable=False)
    count_per_sample: Mapped[int] = mapped_column(Integer, nullable=False)
    record_prefix: Mapped[str] = mapped_column(String(64), nullable=False)
    normalized_prefix_key: Mapped[str] = mapped_column(String(64), nullable=False)
    included: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    point_expression: Mapped[str | None] = mapped_column(Text)


class ContactPointProfileCrCategorySelectionModel(Base):
    """Ordered whole-category CR coverage within one immutable profile revision."""

    __tablename__ = "contact_point_profile_cr_category_selections"
    __table_args__ = (
        ForeignKeyConstraint(
            ["contact_point_profile_revision_id", "category_id"],
            [
                "contact_point_profile_categories.contact_point_profile_revision_id",
                "contact_point_profile_categories.category_id",
            ],
            name="fk_contact_point_profile_cr_selection_category",
        ),
        UniqueConstraint(
            "contact_point_profile_revision_id",
            "category_id",
            name="uq_contact_point_profile_cr_selection_category",
        ),
        UniqueConstraint(
            "contact_point_profile_revision_id",
            "selection_ordinal",
            name="uq_contact_point_profile_cr_selection_order",
        ),
        CheckConstraint(
            "selection_ordinal >= 0",
            name="ck_contact_point_profile_cr_selection_ordinal",
        ),
    )

    contact_point_profile_cr_selection_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    contact_point_profile_revision_id: Mapped[str] = mapped_column(String(64), nullable=False)
    category_id: Mapped[str] = mapped_column(String(64), nullable=False)
    selection_ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
