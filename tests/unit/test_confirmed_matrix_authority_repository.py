from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from sqlalchemy.exc import IntegrityError

from backend.application.source_matrix_import_persistence_service import (
    PersistSourceMatrixImportCommand,
    SourceMatrixImportPersistenceService,
)
from backend.domain import (
    ConfirmedMatrixCell,
    ConfirmedMatrixGroup,
    ConfirmedMatrixRow,
    ConfirmedMatrixSnapshot,
    ConfirmedMatrixStatus,
    ConfirmedMatrixStepQuantity,
    ConfirmedMatrixVersion,
    MatrixStepContactFamily,
    MatrixStepContactPlan,
    Project,
    ProjectMatrixDraftCell,
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
    ProjectStatus,
)
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    ConfirmedMatrixAuthorityRepository,
    ProjectMatrixDraftRepository,
    ProjectRepository,
    SourceMatrixImportRepository,
)
from backend.shared.config import Settings


def test_confirmed_matrix_authority_repository_create_and_get_active_roundtrip(
    tmp_path: Path,
) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)
    try:
        with session_factory() as session:
            _seed_project(session)
            source_import_id, source_snapshot = _seed_source_snapshot(session)
            draft_snapshot = _seed_project_matrix_draft(session, source_import_id, source_snapshot)
            snapshot = _build_confirmed_snapshot(
                confirmed_matrix_id="cmv-1",
                draft=draft_snapshot,
                status=ConfirmedMatrixStatus.CONFIRMED,
            )
            repo = ConfirmedMatrixAuthorityRepository(session)
            repo.create_snapshot(snapshot)
            session.commit()

            loaded = repo.get("cmv-1")
            assert loaded is not None
            assert loaded.version.project_id == "P1"
            assert loaded.version.project_matrix_draft_id == draft_snapshot.record.project_matrix_draft_id
            assert len(loaded.groups) == 2
            assert len(loaded.rows) == 2
            assert len(loaded.cells) == 2

            active = repo.get_active_by_project("P1")
            assert active is not None
            assert active.version.confirmed_matrix_id == "cmv-1"
    finally:
        engine.dispose()


def test_confirmed_matrix_authority_repository_roundtrips_step_quantities(
    tmp_path: Path,
) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)
    try:
        with session_factory() as session:
            _seed_project(session)
            source_import_id, source_snapshot = _seed_source_snapshot(session)
            draft_snapshot = _seed_project_matrix_draft(session, source_import_id, source_snapshot)
            snapshot = _build_confirmed_snapshot(
                confirmed_matrix_id="cmv-qty",
                draft=draft_snapshot,
                status=ConfirmedMatrixStatus.CONFIRMED,
            )
            snapshot = ConfirmedMatrixSnapshot(
                version=snapshot.version,
                groups=snapshot.groups,
                rows=snapshot.rows,
                cells=snapshot.cells,
                step_quantities=(
                    ConfirmedMatrixStepQuantity(
                        confirmed_step_quantity_id="cmsq-1",
                        confirmed_matrix_id="cmv-qty",
                        confirmed_group_id=snapshot.groups[0].confirmed_group_id,
                        confirmed_row_id=snapshot.rows[0].confirmed_row_id,
                        draft_group_id=draft_snapshot.groups[0].draft_group_id,
                        draft_row_id=draft_snapshot.rows[0].draft_row_id,
                        step_sequence=1,
                        step_suffix_note=None,
                        raw_token="1",
                        test_points_per_sample="3",
                        readings_per_point="2",
                        contact_points_per_sample="4",
                        source="matrix_step_override",
                        review_required=False,
                        review_reason=None,
                        confirmed_at="2026-07-08T09:00:00+00:00",
                        contact_plan=MatrixStepContactPlan(
                            contact_kind="llcr",
                            coverage_status="eligible",
                            included=True,
                            exclusion_reason=None,
                            is_override=False,
                            readings_per_sample="6",
                            families=(
                                MatrixStepContactFamily(
                                    family_id="signal_pin",
                                    family_label="Signal Pin",
                                    count_per_sample="6",
                                    record_label="Signal Pin contact",
                                    record_prefix="SIG",
                                    included=True,
                                    is_custom=False,
                                ),
                            ),
                        ),
                    ),
                ),
            )
            repo = ConfirmedMatrixAuthorityRepository(session)
            repo.create_snapshot(snapshot)
            session.commit()

            loaded = repo.get("cmv-qty")
            assert loaded is not None
            assert len(loaded.step_quantities) == 1
            assert loaded.step_quantities[0].test_points_per_sample == "3"
            assert loaded.step_quantities[0].source == "matrix_step_override"
            assert loaded.step_quantities[0].contact_plan is not None
            assert loaded.step_quantities[0].contact_plan.families[0].record_prefix == "SIG"
    finally:
        engine.dispose()


def test_confirmed_matrix_authority_repository_rejects_duplicate_no_suffix_step_quantity(
    tmp_path: Path,
) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)
    try:
        with session_factory() as session:
            _seed_project(session)
            source_import_id, source_snapshot = _seed_source_snapshot(session)
            draft_snapshot = _seed_project_matrix_draft(session, source_import_id, source_snapshot)
            snapshot = _build_confirmed_snapshot(
                confirmed_matrix_id="cmv-qty-uq",
                draft=draft_snapshot,
                status=ConfirmedMatrixStatus.CONFIRMED,
            )
            snapshot = ConfirmedMatrixSnapshot(
                version=snapshot.version,
                groups=snapshot.groups,
                rows=snapshot.rows,
                cells=snapshot.cells,
                step_quantities=(
                    ConfirmedMatrixStepQuantity(
                        confirmed_step_quantity_id="cmsq-uq-1",
                        confirmed_matrix_id="cmv-qty-uq",
                        confirmed_group_id=snapshot.groups[0].confirmed_group_id,
                        confirmed_row_id=snapshot.rows[0].confirmed_row_id,
                        draft_group_id=draft_snapshot.groups[0].draft_group_id,
                        draft_row_id=draft_snapshot.rows[0].draft_row_id,
                        step_sequence=1,
                        step_suffix_note=None,
                        raw_token="1",
                        test_points_per_sample="3",
                        readings_per_point="2",
                        contact_points_per_sample="4",
                        source="matrix_step_override",
                        review_required=False,
                        review_reason=None,
                        confirmed_at="2026-07-08T09:00:00+00:00",
                    ),
                    ConfirmedMatrixStepQuantity(
                        confirmed_step_quantity_id="cmsq-uq-2",
                        confirmed_matrix_id="cmv-qty-uq",
                        confirmed_group_id=snapshot.groups[0].confirmed_group_id,
                        confirmed_row_id=snapshot.rows[0].confirmed_row_id,
                        draft_group_id=draft_snapshot.groups[0].draft_group_id,
                        draft_row_id=draft_snapshot.rows[0].draft_row_id,
                        step_sequence=1,
                        step_suffix_note=None,
                        raw_token="1",
                        test_points_per_sample="3",
                        readings_per_point="2",
                        contact_points_per_sample="4",
                        source="matrix_step_override",
                        review_required=False,
                        review_reason=None,
                        confirmed_at="2026-07-08T09:00:00+00:00",
                    ),
                ),
            )
            repo = ConfirmedMatrixAuthorityRepository(session)

            with pytest.raises(IntegrityError):
                repo.create_snapshot(snapshot)
            session.rollback()
    finally:
        engine.dispose()


def test_confirmed_matrix_authority_repository_enforces_one_active_authority_per_project(
    tmp_path: Path,
) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)
    try:
        with session_factory() as session:
            _seed_project(session)
            source_import_id, source_snapshot = _seed_source_snapshot(session)
            draft_snapshot = _seed_project_matrix_draft(session, source_import_id, source_snapshot)
            repo = ConfirmedMatrixAuthorityRepository(session)
            first = _build_confirmed_snapshot(
                confirmed_matrix_id="cmv-a",
                draft=draft_snapshot,
                status=ConfirmedMatrixStatus.CONFIRMED,
            )
            repo.create_snapshot(first)
            session.commit()

            second = _build_confirmed_snapshot(
                confirmed_matrix_id="cmv-b",
                draft=draft_snapshot,
                status=ConfirmedMatrixStatus.CONFIRMED,
            )
            with pytest.raises(IntegrityError):
                repo.create_snapshot(second)
            session.rollback()

            active = repo.get_active_by_project("P1")
            assert active is not None
            assert active.version.confirmed_matrix_id == "cmv-a"
    finally:
        engine.dispose()


def test_confirmed_matrix_authority_repository_rolls_back_on_child_unique_failure(
    tmp_path: Path,
) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)
    try:
        with session_factory() as session:
            _seed_project(session)
            source_import_id, source_snapshot = _seed_source_snapshot(session)
            draft_snapshot = _seed_project_matrix_draft(session, source_import_id, source_snapshot)
            invalid = ConfirmedMatrixSnapshot(
                version=ConfirmedMatrixVersion(
                    confirmed_matrix_id="cmv-rb",
                    project_id="P1",
                    project_matrix_draft_id=draft_snapshot.record.project_matrix_draft_id,
                    source_import_id=draft_snapshot.record.source_import_id,
                    source_snapshot_id=draft_snapshot.record.source_snapshot_id,
                    confirmed_revision=1,
                    is_active_authority=True,
                    status=ConfirmedMatrixStatus.CONFIRMED,
                    confirmed_by="operator",
                    confirmed_at="2026-05-23T10:00:00+00:00",
                ),
                groups=(
                    ConfirmedMatrixGroup(
                        confirmed_group_id="cmg-rb-1",
                        confirmed_matrix_id="cmv-rb",
                        draft_group_id=draft_snapshot.groups[0].draft_group_id,
                        source_group_snapshot_id=draft_snapshot.groups[0].source_group_snapshot_id,
                        group_order=1,
                        group_key="g1",
                        group_label="G1",
                        sample_quantity_expression="5",
                    ),
                ),
                rows=(
                    ConfirmedMatrixRow(
                        confirmed_row_id="cmr-rb-1",
                        confirmed_matrix_id="cmv-rb",
                        draft_row_id=draft_snapshot.rows[0].draft_row_id,
                        source_row_snapshot_id=draft_snapshot.rows[0].source_row_snapshot_id,
                        row_order=1,
                        test_item="Visual",
                    ),
                    ConfirmedMatrixRow(
                        confirmed_row_id="cmr-rb-2",
                        confirmed_matrix_id="cmv-rb",
                        draft_row_id=draft_snapshot.rows[1].draft_row_id,
                        source_row_snapshot_id=draft_snapshot.rows[1].source_row_snapshot_id,
                        row_order=1,
                        test_item="LLCR",
                    ),
                ),
                cells=(),
            )
            repo = ConfirmedMatrixAuthorityRepository(session)
            with pytest.raises(IntegrityError):
                repo.create_snapshot(invalid)
            session.rollback()
            assert repo.get("cmv-rb") is None
    finally:
        engine.dispose()


def test_confirmed_matrix_authority_repository_supersede_active_and_create_snapshot(
    tmp_path: Path,
) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)
    try:
        with session_factory() as session:
            _seed_project(session)
            source_import_id, source_snapshot = _seed_source_snapshot(session)
            draft_snapshot = _seed_project_matrix_draft(session, source_import_id, source_snapshot)
            repo = ConfirmedMatrixAuthorityRepository(session)
            first = _build_confirmed_snapshot(
                confirmed_matrix_id="cmv-s1",
                draft=draft_snapshot,
                status=ConfirmedMatrixStatus.CONFIRMED,
            )
            repo.create_snapshot(first)
            session.commit()

            second = _build_confirmed_snapshot(
                confirmed_matrix_id="cmv-s2",
                draft=draft_snapshot,
                status=ConfirmedMatrixStatus.CONFIRMED,
            )
            second = ConfirmedMatrixSnapshot(
                version=ConfirmedMatrixVersion(
                    confirmed_matrix_id=second.version.confirmed_matrix_id,
                    project_id=second.version.project_id,
                    project_matrix_draft_id=second.version.project_matrix_draft_id,
                    source_import_id=second.version.source_import_id,
                    source_snapshot_id=second.version.source_snapshot_id,
                    confirmed_revision=2,
                    is_active_authority=True,
                    status=ConfirmedMatrixStatus.CONFIRMED,
                    confirmed_by=second.version.confirmed_by,
                    confirmed_at="2026-05-23T11:00:00+00:00",
                ),
                groups=second.groups,
                rows=second.rows,
                cells=second.cells,
            )
            repo.supersede_active_and_create_snapshot(
                previous_active_confirmed_matrix_id="cmv-s1",
                snapshot=second,
                superseded_reason="Revision confirmed",
            )
            session.commit()

            previous = repo.get("cmv-s1")
            assert previous is not None
            assert previous.version.is_active_authority is False
            assert previous.version.status == ConfirmedMatrixStatus.SUPERSEDED
            assert previous.version.superseded_by_confirmed_matrix_id == "cmv-s2"
            assert previous.version.superseded_reason == "Revision confirmed"
            active = repo.get_active_by_project("P1")
            assert active is not None
            assert active.version.confirmed_matrix_id == "cmv-s2"
            assert active.version.confirmed_revision == 2
    finally:
        engine.dispose()


def test_confirmed_matrix_authority_repository_list_by_project_orders_by_revision(
    tmp_path: Path,
) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)
    try:
        with session_factory() as session:
            _seed_project(session)
            source_import_id, source_snapshot = _seed_source_snapshot(session)
            draft_snapshot = _seed_project_matrix_draft(session, source_import_id, source_snapshot)
            repo = ConfirmedMatrixAuthorityRepository(session)

            first = _build_confirmed_snapshot(
                confirmed_matrix_id="cmv-l1",
                draft=draft_snapshot,
                status=ConfirmedMatrixStatus.CONFIRMED,
            )
            repo.create_snapshot(first)
            session.commit()

            second = _build_confirmed_snapshot(
                confirmed_matrix_id="cmv-l2",
                draft=draft_snapshot,
                status=ConfirmedMatrixStatus.CONFIRMED,
            )
            second = ConfirmedMatrixSnapshot(
                version=ConfirmedMatrixVersion(
                    confirmed_matrix_id=second.version.confirmed_matrix_id,
                    project_id=second.version.project_id,
                    project_matrix_draft_id=second.version.project_matrix_draft_id,
                    source_import_id=second.version.source_import_id,
                    source_snapshot_id=second.version.source_snapshot_id,
                    confirmed_revision=2,
                    is_active_authority=True,
                    status=ConfirmedMatrixStatus.CONFIRMED,
                    confirmed_by=second.version.confirmed_by,
                    confirmed_at="2026-05-23T11:00:00+00:00",
                ),
                groups=second.groups,
                rows=second.rows,
                cells=second.cells,
            )
            repo.supersede_active_and_create_snapshot(
                previous_active_confirmed_matrix_id="cmv-l1",
                snapshot=second,
                superseded_reason="Revision confirmed",
            )
            session.commit()

            snapshots = repo.list_by_project("P1")
            assert [snapshot.version.confirmed_revision for snapshot in snapshots] == [1, 2]
            assert snapshots[0].version.confirmed_matrix_id == "cmv-l1"
            assert snapshots[1].version.confirmed_matrix_id == "cmv-l2"
            assert snapshots[0].version.is_active_authority is False
            assert snapshots[1].version.is_active_authority is True
            assert len(snapshots[0].groups) > 0
            assert len(snapshots[0].rows) > 0
            assert len(snapshots[0].cells) > 0
    finally:
        engine.dispose()


def test_supersede_active_and_create_snapshot_rolls_back_when_new_insert_fails(
    tmp_path: Path,
) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)
    try:
        with session_factory() as session:
            _seed_project(session)
            source_import_id, source_snapshot = _seed_source_snapshot(session)
            draft_snapshot = _seed_project_matrix_draft(session, source_import_id, source_snapshot)
            repo = ConfirmedMatrixAuthorityRepository(session)
            first = _build_confirmed_snapshot(
                confirmed_matrix_id="cmv-rs1",
                draft=draft_snapshot,
                status=ConfirmedMatrixStatus.CONFIRMED,
            )
            repo.create_snapshot(first)
            session.commit()

            invalid_second = _build_confirmed_snapshot(
                confirmed_matrix_id="cmv-rs2",
                draft=draft_snapshot,
                status=ConfirmedMatrixStatus.CONFIRMED,
            )
            invalid_second = ConfirmedMatrixSnapshot(
                version=ConfirmedMatrixVersion(
                    confirmed_matrix_id=invalid_second.version.confirmed_matrix_id,
                    project_id=invalid_second.version.project_id,
                    project_matrix_draft_id=invalid_second.version.project_matrix_draft_id,
                    source_import_id=invalid_second.version.source_import_id,
                    source_snapshot_id=invalid_second.version.source_snapshot_id,
                    confirmed_revision=2,
                    is_active_authority=True,
                    status=ConfirmedMatrixStatus.CONFIRMED,
                    confirmed_by=invalid_second.version.confirmed_by,
                    confirmed_at="2026-05-23T11:00:00+00:00",
                ),
                groups=invalid_second.groups,
                rows=(
                    invalid_second.rows[0],
                    ConfirmedMatrixRow(
                        confirmed_row_id="cmr-rs-dup",
                        confirmed_matrix_id="cmv-rs2",
                        draft_row_id=invalid_second.rows[1].draft_row_id,
                        source_row_snapshot_id=invalid_second.rows[1].source_row_snapshot_id,
                        row_order=invalid_second.rows[0].row_order,
                        test_item=invalid_second.rows[1].test_item,
                    ),
                ),
                cells=invalid_second.cells,
            )
            with pytest.raises(IntegrityError):
                repo.supersede_active_and_create_snapshot(
                    previous_active_confirmed_matrix_id="cmv-rs1",
                    snapshot=invalid_second,
                    superseded_reason="bad",
                )
            session.rollback()
            previous = repo.get("cmv-rs1")
            assert previous is not None
            assert previous.version.is_active_authority is True
            assert previous.version.status == ConfirmedMatrixStatus.CONFIRMED
            assert previous.version.superseded_by_confirmed_matrix_id is None
    finally:
        engine.dispose()


def _seed_project(session) -> None:
    ProjectRepository(session).create(
        Project(
            project_id="P1",
            project_no="DL-2026-05-001",
            product_name="Connector",
            requestor="Alice",
            status=ProjectStatus.LTR_REGISTERED,
            created_on=date(2026, 5, 22),
        )
    )
    session.flush()


def _seed_source_snapshot(session) -> tuple[str, object]:
    source_service = SourceMatrixImportPersistenceService(
        store=SourceMatrixImportRepository(session)
    )
    source_import_id = source_service.persist_from_draft(
        PersistSourceMatrixImportCommand(
            project_id="P1",
            draft_id="ptpd-seed",
            source_document_path="C:/spec.docx",
            source_document_name="spec.docx",
            source_format=".docx",
            source_asset_id="asset-1",
            source_case_id="case-1",
            source_draft_id="draft-1",
            payload={
                "groups": [
                    {"group_key": "g1", "group_label": "G1", "sample_quantity_expression": "5"},
                    {"group_key": "g2", "group_label": "G2", "sample_quantity_expression": "6"},
                ],
                "rows": [
                    {
                        "source_row_index": 3,
                        "test_item": "Visual",
                        "source_section": "6.1",
                        "group_tokens": {"G1": "1", "G2": ""},
                        "is_sample_row": False,
                    },
                    {
                        "source_row_index": 4,
                        "test_item": "LLCR",
                        "source_section": "6.2",
                        "group_tokens": {"G1": "", "G2": "2"},
                        "is_sample_row": False,
                    },
                    {
                        "source_row_index": 5,
                        "test_item": "Samples Quantity (PCS)",
                        "source_section": None,
                        "group_tokens": {"G1": "5", "G2": "6"},
                        "is_sample_row": True,
                    },
                ],
                "warnings": [],
                "blockers": [],
            },
            created_at="2026-05-22T09:00:00+00:00",
        )
    )
    snapshot = SourceMatrixImportRepository(session).get_snapshot_by_import(source_import_id)
    assert snapshot is not None
    return source_import_id, snapshot


def _seed_project_matrix_draft(session, source_import_id: str, source_snapshot) -> ProjectMatrixDraftSnapshot:
    draft = ProjectMatrixDraftSnapshot(
        record=ProjectMatrixDraftRecord(
            project_matrix_draft_id="pmd-1",
            project_id="P1",
            source_import_id=source_import_id,
            source_snapshot_id=source_snapshot.snapshot_id,
            status=ProjectMatrixDraftStatus.DRAFT,
            created_at="2026-05-23T08:00:00+00:00",
            updated_at="2026-05-23T08:00:00+00:00",
        ),
        groups=(
            ProjectMatrixDraftGroup(
                draft_group_id="pmdg-1",
                project_matrix_draft_id="pmd-1",
                source_group_snapshot_id=source_snapshot.groups[0].group_snapshot_id,
                group_order=1,
                group_key="g1",
                group_label="G1",
                is_selected=True,
                sample_quantity_expression="5",
            ),
            ProjectMatrixDraftGroup(
                draft_group_id="pmdg-2",
                project_matrix_draft_id="pmd-1",
                source_group_snapshot_id=source_snapshot.groups[1].group_snapshot_id,
                group_order=2,
                group_key="g2",
                group_label="G2",
                is_selected=True,
                sample_quantity_expression="6",
            ),
        ),
        rows=(
            ProjectMatrixDraftRow(
                draft_row_id="pmdr-1",
                project_matrix_draft_id="pmd-1",
                source_row_snapshot_id=source_snapshot.rows[0].row_snapshot_id,
                row_order=1,
                test_item="Visual",
                source_section="6.1",
                method="M1",
                condition="C1",
                requirement="R1",
                is_sample_row=False,
            ),
            ProjectMatrixDraftRow(
                draft_row_id="pmdr-2",
                project_matrix_draft_id="pmd-1",
                source_row_snapshot_id=source_snapshot.rows[1].row_snapshot_id,
                row_order=2,
                test_item="LLCR",
                source_section="6.2",
                method="M2",
                condition="C2",
                requirement="R2",
                is_sample_row=False,
            ),
            ProjectMatrixDraftRow(
                draft_row_id="pmdr-3",
                project_matrix_draft_id="pmd-1",
                source_row_snapshot_id=source_snapshot.rows[2].row_snapshot_id,
                row_order=3,
                test_item="Samples Quantity (PCS)",
                is_sample_row=True,
            ),
        ),
        cells=(
            ProjectMatrixDraftCell(
                draft_cell_id="pmdc-1",
                project_matrix_draft_id="pmd-1",
                draft_row_id="pmdr-1",
                draft_group_id="pmdg-1",
                cell_value="1",
            ),
            ProjectMatrixDraftCell(
                draft_cell_id="pmdc-2",
                project_matrix_draft_id="pmd-1",
                draft_row_id="pmdr-2",
                draft_group_id="pmdg-2",
                cell_value="2",
            ),
        ),
    )
    ProjectMatrixDraftRepository(session).create_snapshot(draft)
    session.flush()
    return draft


def _build_confirmed_snapshot(
    *,
    confirmed_matrix_id: str,
    draft: ProjectMatrixDraftSnapshot,
    status: ConfirmedMatrixStatus,
) -> ConfirmedMatrixSnapshot:
    return ConfirmedMatrixSnapshot(
        version=ConfirmedMatrixVersion(
            confirmed_matrix_id=confirmed_matrix_id,
            project_id=draft.record.project_id,
            project_matrix_draft_id=draft.record.project_matrix_draft_id,
            source_import_id=draft.record.source_import_id,
            source_snapshot_id=draft.record.source_snapshot_id,
            confirmed_revision=1,
            is_active_authority=True,
            status=status,
            confirmed_by="operator",
            confirmed_at="2026-05-23T10:00:00+00:00",
        ),
        groups=(
            ConfirmedMatrixGroup(
                confirmed_group_id=f"cmg-{confirmed_matrix_id}-1",
                confirmed_matrix_id=confirmed_matrix_id,
                draft_group_id=draft.groups[0].draft_group_id,
                source_group_snapshot_id=draft.groups[0].source_group_snapshot_id,
                group_order=1,
                group_key="g1",
                group_label="G1",
                sample_quantity_expression="5",
            ),
            ConfirmedMatrixGroup(
                confirmed_group_id=f"cmg-{confirmed_matrix_id}-2",
                confirmed_matrix_id=confirmed_matrix_id,
                draft_group_id=draft.groups[1].draft_group_id,
                source_group_snapshot_id=draft.groups[1].source_group_snapshot_id,
                group_order=2,
                group_key="g2",
                group_label="G2",
                sample_quantity_expression="6",
            ),
        ),
        rows=(
            ConfirmedMatrixRow(
                confirmed_row_id=f"cmr-{confirmed_matrix_id}-1",
                confirmed_matrix_id=confirmed_matrix_id,
                draft_row_id=draft.rows[0].draft_row_id,
                source_row_snapshot_id=draft.rows[0].source_row_snapshot_id,
                row_order=1,
                test_item="Visual",
                source_section="6.1",
                method="M1",
                condition="C1",
                requirement="R1",
            ),
            ConfirmedMatrixRow(
                confirmed_row_id=f"cmr-{confirmed_matrix_id}-2",
                confirmed_matrix_id=confirmed_matrix_id,
                draft_row_id=draft.rows[1].draft_row_id,
                source_row_snapshot_id=draft.rows[1].source_row_snapshot_id,
                row_order=2,
                test_item="LLCR",
                source_section="6.2",
                method="M2",
                condition="C2",
                requirement="R2",
            ),
        ),
        cells=(
            ConfirmedMatrixCell(
                confirmed_cell_id=f"cmc-{confirmed_matrix_id}-1",
                confirmed_matrix_id=confirmed_matrix_id,
                confirmed_row_id=f"cmr-{confirmed_matrix_id}-1",
                confirmed_group_id=f"cmg-{confirmed_matrix_id}-1",
                draft_row_id=draft.rows[0].draft_row_id,
                draft_group_id=draft.groups[0].draft_group_id,
                cell_value="1",
            ),
            ConfirmedMatrixCell(
                confirmed_cell_id=f"cmc-{confirmed_matrix_id}-2",
                confirmed_matrix_id=confirmed_matrix_id,
                confirmed_row_id=f"cmr-{confirmed_matrix_id}-2",
                confirmed_group_id=f"cmg-{confirmed_matrix_id}-2",
                draft_row_id=draft.rows[1].draft_row_id,
                draft_group_id=draft.groups[1].draft_group_id,
                cell_value="2",
            ),
        ),
    )


def _create_temp_engine(tmp_path: Path):
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    return create_database_engine(settings)
