"""Temporary SQLite integration coverage for TASK_361H freeform categories."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from backend.application.contact_measurement_plan_bootstrap_service import (
    ContactMeasurementPlanBootstrapService,
)
from backend.application.contact_measurement_plan_lifecycle_service import (
    ContactMeasurementPlanLifecycleError,
    ContactMeasurementPlanLifecycleService,
)
from backend.domain import (
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixStepQuantity,
    ConfirmedMatrixVersion,
    MatrixStepContactFamily,
    MatrixStepContactPlan,
    Project,
    ProjectStatus,
)
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    ConfirmedMatrixAuthorityRepository,
    ContactMeasurementPlanAuthorityRepository,
    ProjectRepository,
)
from backend.shared.config import Settings


def test_repository_reads_historical_freeform_family_high_water_by_kind(
    tmp_path: Path,
) -> None:
    session_factory = _session_factory(tmp_path)
    snapshot = _seed_snapshot(session_factory)

    with session_factory() as session:
        repository = ContactMeasurementPlanAuthorityRepository(session)
        root_id = _bootstrap(repository).bootstrap(snapshot, actor="operator")
        root = repository.get_root("P1")
        assert root is not None and root.active_confirmed_revision_id is not None
        target = repository.targets(root.active_confirmed_revision_id)[0]
        repository.replace_families(
            target.measurement_plan_target_snapshot_id,
            (_family("ff-llcr-2", "HP", 2), _family("ff-llcr-7", "SIG", 1)),
            _ids(),
        )
        session.flush()

        assert repository.family_id_high_water_by_kind(root_id) == {
            "llcr": 7,
            "cr_specified_current": 0,
        }


def test_lifecycle_rejects_duplicate_or_stale_freeform_patches_without_writes(
    tmp_path: Path,
) -> None:
    session_factory = _session_factory(tmp_path)
    _seed_snapshot(session_factory)

    with session_factory() as session:
        repository = ContactMeasurementPlanAuthorityRepository(session)
        lifecycle = _lifecycle(repository, session)
        revision_id = lifecycle.open_draft("P1", actor="operator")
        target = repository.targets(revision_id)[0]
        before = [
            family.family_id
            for family in repository.families(target.measurement_plan_target_snapshot_id)
        ]
        fingerprint = repository.get_revision(revision_id).revision_fingerprint

        with pytest.raises(ContactMeasurementPlanLifecycleError, match="prefixes must be unique"):
            lifecycle.set_target_inclusion(
                "P1", revision_id, target.stable_target_key, True, None,
                (_family("ff-llcr-1", "HP", 1), _family("ff-llcr-2", "hp", 1)),
                fingerprint, "operator",
            )
        with pytest.raises(ContactMeasurementPlanLifecycleError, match="stale"):
            lifecycle.set_target_inclusion(
                "P1", revision_id, target.stable_target_key, True, None,
                (_family("ff-llcr-8", "HP", 1),), "stale-fingerprint", "operator",
            )

        after = repository.families(target.measurement_plan_target_snapshot_id)
        assert [family.family_id for family in after] == before


def test_lifecycle_rejects_cross_target_freeform_identity_or_label_redefinition(
    tmp_path: Path,
) -> None:
    session_factory = _session_factory(tmp_path)
    _seed_snapshot(session_factory)

    with session_factory() as session:
        repository = ContactMeasurementPlanAuthorityRepository(session)
        lifecycle = _lifecycle(repository, session)
        revision_id = lifecycle.open_draft("P1", actor="operator")
        first, second = repository.targets(revision_id)
        fingerprint = repository.get_revision(revision_id).revision_fingerprint
        lifecycle.set_target_inclusion(
            "P1", revision_id, first.stable_target_key, True, None,
            (_family("ff-llcr-1", "HP", 1, "High Power"),), fingerprint, "operator",
        )
        fingerprint = repository.get_revision(revision_id).revision_fingerprint
        lifecycle.set_target_inclusion(
            "P1", revision_id, second.stable_target_key, True, None,
            (_family("ff-llcr-1", "HP", 1, "High Power"),), fingerprint, "operator",
        )
        fingerprint = repository.get_revision(revision_id).revision_fingerprint
        before = [
            (family.family_id, family.label, family.record_prefix)
            for family in repository.families(second.measurement_plan_target_snapshot_id)
        ]

        with pytest.raises(ContactMeasurementPlanLifecycleError, match="issued family id"):
            lifecycle.set_target_inclusion(
                "P1", revision_id, second.stable_target_key, True, None,
                (_family("ff-llcr-1", "HPA", 1, "Different High Power"),), fingerprint, "operator",
            )
        assert [
            (family.family_id, family.label, family.record_prefix)
            for family in repository.families(second.measurement_plan_target_snapshot_id)
        ] == before

        with pytest.raises(ContactMeasurementPlanLifecycleError, match="labels must be unique"):
            lifecycle.set_target_inclusion(
                "P1", revision_id, second.stable_target_key, True, None,
                (_family("ff-llcr-2", "SIG", 1, " high power "),), fingerprint, "operator",
            )
        assert [
            (family.family_id, family.label, family.record_prefix)
            for family in repository.families(second.measurement_plan_target_snapshot_id)
        ] == before


def _lifecycle(repository, session):
    return ContactMeasurementPlanLifecycleService(
        repository=repository,
        confirmed_store=ConfirmedMatrixAuthorityRepository(session),
        bootstrap_service=_bootstrap(repository),
        clock=_clock(),
    )


def _session_factory(tmp_path: Path):
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "authority.sqlite3",
    )
    engine = create_database_engine(settings)
    init_db(engine)
    return create_session_factory(engine)


def _seed_snapshot(session_factory) -> ConfirmedMatrixSnapshot:
    snapshot = _snapshot()
    with session_factory() as session:
        ProjectRepository(session).create(
            Project(
                project_id="P1", project_no="DL-2026-07-P1", product_name="Connector",
                requestor="Operator", status=ProjectStatus.LTR_REGISTERED,
                created_on=date(2026, 7, 12),
            )
        )
        ConfirmedMatrixAuthorityRepository(session).create_snapshot(snapshot)
        session.commit()
    return snapshot


def _snapshot() -> ConfirmedMatrixSnapshot:
    version = ConfirmedMatrixVersion(
        confirmed_matrix_id="cmv-1", project_id="P1", project_matrix_draft_id="pmd-1",
        source_import_id="smi-1", source_snapshot_id="sms-1", confirmed_revision=1,
        is_active_authority=True, status=ConfirmedMatrixStatus.CONFIRMED,
        confirmed_by="operator", confirmed_at="2026-07-12T10:00:00Z",
    )
    group = ConfirmedMatrixGroup(
        confirmed_group_id="cmg-1", confirmed_matrix_id="cmv-1", draft_group_id="pmdg-1",
        source_group_snapshot_id="smg-1", group_order=1, group_key="group-1",
        group_label="Group 1", sample_quantity_expression="2",
    )
    row = ConfirmedMatrixRow(
        confirmed_row_id="cmr-1", confirmed_matrix_id="cmv-1", draft_row_id="pmdr-1",
        source_row_snapshot_id="smr-1", row_order=1, test_item="Low level contact resistance",
    )
    quantity = ConfirmedMatrixStepQuantity(
        confirmed_step_quantity_id="cmsq-1", confirmed_matrix_id="cmv-1",
        confirmed_group_id="cmg-1", confirmed_row_id="cmr-1", draft_group_id="pmdg-1",
        draft_row_id="pmdr-1", step_sequence=1, step_suffix_note=None, raw_token="1",
        test_points_per_sample=None, readings_per_point=None, contact_points_per_sample=None,
        source="matrix_contact_plan", review_required=False, review_reason=None,
        confirmed_at="2026-07-12T10:00:00Z",
        contact_plan=MatrixStepContactPlan(
            contact_kind="llcr", coverage_status="included", included=True,
            exclusion_reason=None, is_override=False, readings_per_sample="4",
            families=(
                MatrixStepContactFamily("hp", "High power", "2", "High power pin", "HP", True, False),
                MatrixStepContactFamily("signal", "Signal", "2", "Signal pin", "SIG", True, False),
            ),
        ),
    )
    second_group = replace(
        group,
        confirmed_group_id="cmg-2",
        draft_group_id="pmdg-2",
        source_group_snapshot_id="smg-2",
        group_order=2,
        group_key="group-2",
        group_label="Group 2",
    )
    second_quantity = replace(
        quantity,
        confirmed_step_quantity_id="cmsq-2",
        confirmed_group_id="cmg-2",
        draft_group_id="pmdg-2",
    )
    return ConfirmedMatrixSnapshot(
        version=version,
        groups=(group, second_group),
        rows=(row,),
        step_quantities=(quantity, second_quantity),
    )


def _bootstrap(repository):
    return ContactMeasurementPlanBootstrapService(
        repository=repository, clock=_clock(), id_factory=_ids()
    )


def _clock():
    return iter([f"2026-07-12T10:00:0{value}Z" for value in range(1, 10)]).__next__


def _ids():
    return iter([f"id-{value}" for value in range(1, 40)]).__next__


def _family(
    family_id: str,
    prefix: str,
    count: int,
    label: str = "Freeform contact",
) -> dict[str, object]:
    return {
        "family_id": family_id, "label": label, "count_per_sample": count,
        "record_label": label, "record_prefix": prefix, "included": True,
        "is_custom": True,
    }
