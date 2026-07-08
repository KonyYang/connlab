from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from backend.application.source_matrix_import_persistence_service import (
    PersistSourceMatrixImportCommand,
    SourceMatrixImportPersistenceService,
)
from backend.domain import (
    Project,
    ProjectMatrixDraftCell,
    ProjectMatrixDraftGroup,
    ProjectMatrixDraftRecord,
    ProjectMatrixDraftRow,
    ProjectMatrixDraftSnapshot,
    ProjectMatrixDraftStatus,
    ProjectMatrixDraftStepQuantity,
    ProjectStatus,
)
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    ProjectMatrixDraftRepository,
    ProjectRepository,
    SourceMatrixImportRepository,
)
from backend.shared.config import Settings


def test_project_matrix_draft_repository_create_and_get_roundtrip(tmp_path: Path) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)
    try:
        with session_factory() as session:
            _seed_project(session)
            source_import_id, source_snapshot = _seed_source_snapshot(session)
            source_groups = source_snapshot.groups
            source_rows = source_snapshot.rows
            record = ProjectMatrixDraftRecord(
                project_matrix_draft_id="pmd-1",
                project_id="P1",
                source_import_id=source_import_id,
                source_snapshot_id=source_snapshot.snapshot_id,
                status=ProjectMatrixDraftStatus.DRAFT,
                created_at="2026-05-22T10:00:00+00:00",
                updated_at="2026-05-22T10:00:00+00:00",
                base_confirmed_matrix_id=None,
            )
            groups = (
                ProjectMatrixDraftGroup(
                    draft_group_id="pmdg-1",
                    project_matrix_draft_id="pmd-1",
                    source_group_snapshot_id=source_groups[0].group_snapshot_id,
                    group_order=1,
                    group_key=source_groups[0].group_key,
                    group_label=source_groups[0].group_label,
                    is_selected=True,
                    sample_quantity_expression="5",
                    sample_note=None,
                ),
                ProjectMatrixDraftGroup(
                    draft_group_id="pmdg-2",
                    project_matrix_draft_id="pmd-1",
                    source_group_snapshot_id=source_groups[1].group_snapshot_id,
                    group_order=2,
                    group_key=source_groups[1].group_key,
                    group_label=source_groups[1].group_label,
                    is_selected=False,
                    sample_quantity_expression="5",
                    sample_note=None,
                ),
            )
            rows = (
                ProjectMatrixDraftRow(
                    draft_row_id="pmdr-1",
                    project_matrix_draft_id="pmd-1",
                    source_row_snapshot_id=source_rows[0].row_snapshot_id,
                    row_order=1,
                    test_item=source_rows[0].test_item,
                    source_section=source_rows[0].source_section,
                    is_sample_row=False,
                ),
                ProjectMatrixDraftRow(
                    draft_row_id="pmdr-2",
                    project_matrix_draft_id="pmd-1",
                    source_row_snapshot_id=source_rows[1].row_snapshot_id,
                    row_order=2,
                    test_item=source_rows[1].test_item,
                    source_section=source_rows[1].source_section,
                    is_sample_row=False,
                ),
            )
            cells = (
                ProjectMatrixDraftCell(
                    draft_cell_id="pmdc-1",
                    project_matrix_draft_id="pmd-1",
                    draft_row_id="pmdr-1",
                    draft_group_id="pmdg-1",
                    cell_value="1",
                ),
            )
            snapshot = ProjectMatrixDraftSnapshot(
                record=record,
                groups=groups,
                rows=rows,
                cells=cells,
            )
            repo = ProjectMatrixDraftRepository(session)
            repo.create_snapshot(snapshot)
            session.commit()

            loaded = repo.get("pmd-1")
            assert loaded is not None
            assert loaded.record.source_import_id == source_import_id
            assert len(loaded.groups) == 2
            assert len(loaded.rows) == 2
            assert len(loaded.cells) == 1
            assert loaded.cells[0].cell_value == "1"
            assert repo.get_by_project_and_source_import("P1", source_import_id) is not None
            assert loaded.record.base_confirmed_matrix_id is None
    finally:
        engine.dispose()


def test_project_matrix_draft_repository_replaces_step_quantities(
    tmp_path: Path,
) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)
    try:
        with session_factory() as session:
            _seed_project(session)
            source_import_id, source_snapshot = _seed_source_snapshot(session)
            source_groups = source_snapshot.groups
            source_rows = source_snapshot.rows
            snapshot = ProjectMatrixDraftSnapshot(
                record=ProjectMatrixDraftRecord(
                    project_matrix_draft_id="pmd-qty",
                    project_id="P1",
                    source_import_id=source_import_id,
                    source_snapshot_id=source_snapshot.snapshot_id,
                    status=ProjectMatrixDraftStatus.DRAFT,
                    created_at="2026-07-08T08:00:00+00:00",
                    updated_at="2026-07-08T08:00:00+00:00",
                ),
                groups=(
                    ProjectMatrixDraftGroup(
                        draft_group_id="pmdg-qty",
                        project_matrix_draft_id="pmd-qty",
                        source_group_snapshot_id=source_groups[0].group_snapshot_id,
                        group_order=1,
                        group_key="g1",
                        group_label="G1",
                        is_selected=True,
                        sample_quantity_expression="5",
                    ),
                ),
                rows=(
                    ProjectMatrixDraftRow(
                        draft_row_id="pmdr-qty",
                        project_matrix_draft_id="pmd-qty",
                        source_row_snapshot_id=source_rows[0].row_snapshot_id,
                        row_order=1,
                        test_item="LLCR",
                        is_sample_row=False,
                    ),
                ),
                cells=(
                    ProjectMatrixDraftCell(
                        draft_cell_id="pmdc-qty",
                        project_matrix_draft_id="pmd-qty",
                        draft_row_id="pmdr-qty",
                        draft_group_id="pmdg-qty",
                        cell_value="1",
                    ),
                ),
            )
            repo = ProjectMatrixDraftRepository(session)
            repo.create_snapshot(snapshot)
            repo.replace_step_quantities(
                "pmd-qty",
                (
                    ProjectMatrixDraftStepQuantity(
                        draft_step_quantity_id="pmdsq-1",
                        project_matrix_draft_id="pmd-qty",
                        draft_group_id="pmdg-qty",
                        draft_row_id="pmdr-qty",
                        step_sequence=1,
                        step_suffix_note=None,
                        raw_token="1",
                        test_points_per_sample="3",
                        readings_per_point="2",
                        contact_points_per_sample="4",
                        source="matrix_step_override",
                        review_required=False,
                        review_reason=None,
                        updated_at="2026-07-08T09:00:00+00:00",
                    ),
                ),
            )
            session.commit()

            loaded = repo.get("pmd-qty")
            assert loaded is not None
            assert len(loaded.step_quantities) == 1
            assert loaded.step_quantities[0].test_points_per_sample == "3"
            assert loaded.step_quantities[0].readings_per_point == "2"
    finally:
        engine.dispose()


def test_project_matrix_draft_repository_rejects_duplicate_no_suffix_step_quantity(
    tmp_path: Path,
) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)
    try:
        with session_factory() as session:
            _seed_project(session)
            source_import_id, source_snapshot = _seed_source_snapshot(session)
            source_groups = source_snapshot.groups
            source_rows = source_snapshot.rows
            snapshot = ProjectMatrixDraftSnapshot(
                record=ProjectMatrixDraftRecord(
                    project_matrix_draft_id="pmd-qty-uq",
                    project_id="P1",
                    source_import_id=source_import_id,
                    source_snapshot_id=source_snapshot.snapshot_id,
                    status=ProjectMatrixDraftStatus.DRAFT,
                    created_at="2026-07-08T08:00:00+00:00",
                    updated_at="2026-07-08T08:00:00+00:00",
                ),
                groups=(
                    ProjectMatrixDraftGroup(
                        draft_group_id="pmdg-qty-uq",
                        project_matrix_draft_id="pmd-qty-uq",
                        source_group_snapshot_id=source_groups[0].group_snapshot_id,
                        group_order=1,
                        group_key="g1",
                        group_label="G1",
                        is_selected=True,
                        sample_quantity_expression="5",
                    ),
                ),
                rows=(
                    ProjectMatrixDraftRow(
                        draft_row_id="pmdr-qty-uq",
                        project_matrix_draft_id="pmd-qty-uq",
                        source_row_snapshot_id=source_rows[0].row_snapshot_id,
                        row_order=1,
                        test_item="LLCR",
                        is_sample_row=False,
                    ),
                ),
                cells=(
                    ProjectMatrixDraftCell(
                        draft_cell_id="pmdc-qty-uq",
                        project_matrix_draft_id="pmd-qty-uq",
                        draft_row_id="pmdr-qty-uq",
                        draft_group_id="pmdg-qty-uq",
                        cell_value="1",
                    ),
                ),
            )
            repo = ProjectMatrixDraftRepository(session)
            repo.create_snapshot(snapshot)
            duplicate = ProjectMatrixDraftStepQuantity(
                draft_step_quantity_id="pmdsq-uq-1",
                project_matrix_draft_id="pmd-qty-uq",
                draft_group_id="pmdg-qty-uq",
                draft_row_id="pmdr-qty-uq",
                step_sequence=1,
                step_suffix_note=None,
                raw_token="1",
                test_points_per_sample="3",
                readings_per_point="2",
                contact_points_per_sample="4",
                source="matrix_step_override",
                review_required=False,
                review_reason=None,
                updated_at="2026-07-08T09:00:00+00:00",
            )

            with pytest.raises(IntegrityError):
                repo.replace_step_quantities(
                    "pmd-qty-uq",
                    (
                        duplicate,
                        ProjectMatrixDraftStepQuantity(
                            draft_step_quantity_id="pmdsq-uq-2",
                            project_matrix_draft_id="pmd-qty-uq",
                            draft_group_id="pmdg-qty-uq",
                            draft_row_id="pmdr-qty-uq",
                            step_sequence=1,
                            step_suffix_note=None,
                            raw_token="1",
                            test_points_per_sample="3",
                            readings_per_point="2",
                            contact_points_per_sample="4",
                            source="matrix_step_override",
                            review_required=False,
                            review_reason=None,
                            updated_at="2026-07-08T09:00:00+00:00",
                        ),
                    ),
                )
            session.rollback()
    finally:
        engine.dispose()


def test_project_matrix_draft_repository_rolls_back_on_child_unique_failure(
    tmp_path: Path,
) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)
    try:
        with session_factory() as session:
            _seed_project(session)
            source_import_id, source_snapshot = _seed_source_snapshot(session)
            source_groups = source_snapshot.groups
            source_rows = source_snapshot.rows
            snapshot = ProjectMatrixDraftSnapshot(
                record=ProjectMatrixDraftRecord(
                    project_matrix_draft_id="pmd-2",
                    project_id="P1",
                    source_import_id=source_import_id,
                    source_snapshot_id=source_snapshot.snapshot_id,
                    status=ProjectMatrixDraftStatus.DRAFT,
                    created_at="2026-05-22T10:10:00+00:00",
                    updated_at="2026-05-22T10:10:00+00:00",
                    base_confirmed_matrix_id=None,
                ),
                groups=(
                    ProjectMatrixDraftGroup(
                        draft_group_id="pmdg-21",
                        project_matrix_draft_id="pmd-2",
                        source_group_snapshot_id=source_groups[0].group_snapshot_id,
                        group_order=1,
                        group_key=source_groups[0].group_key,
                        group_label=source_groups[0].group_label,
                        is_selected=True,
                    ),
                ),
                rows=(
                    ProjectMatrixDraftRow(
                        draft_row_id="pmdr-21",
                        project_matrix_draft_id="pmd-2",
                        source_row_snapshot_id=source_rows[0].row_snapshot_id,
                        row_order=1,
                        test_item=source_rows[0].test_item,
                    ),
                    ProjectMatrixDraftRow(
                        draft_row_id="pmdr-22",
                        project_matrix_draft_id="pmd-2",
                        source_row_snapshot_id=source_rows[1].row_snapshot_id,
                        row_order=1,
                        test_item=source_rows[1].test_item,
                    ),
                ),
            )
            repo = ProjectMatrixDraftRepository(session)
            with pytest.raises(IntegrityError):
                repo.create_snapshot(snapshot)
            session.rollback()
            assert repo.get("pmd-2") is None
            assert repo.get_by_project_and_source_import("P1", source_import_id) is None
    finally:
        engine.dispose()


def test_project_matrix_draft_repository_replace_snapshot_roundtrip(tmp_path: Path) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)
    try:
        with session_factory() as session:
            _seed_project(session)
            source_import_id, source_snapshot = _seed_source_snapshot(session)
            initial = ProjectMatrixDraftSnapshot(
                record=ProjectMatrixDraftRecord(
                    project_matrix_draft_id="pmd-r1",
                    project_id="P1",
                    source_import_id=source_import_id,
                    source_snapshot_id=source_snapshot.snapshot_id,
                    status=ProjectMatrixDraftStatus.DRAFT,
                    created_at="2026-05-22T10:00:00+00:00",
                    updated_at="2026-05-22T10:00:00+00:00",
                    base_confirmed_matrix_id=None,
                ),
                groups=(
                    ProjectMatrixDraftGroup(
                        draft_group_id="pmdg-r1",
                        project_matrix_draft_id="pmd-r1",
                        source_group_snapshot_id=source_snapshot.groups[0].group_snapshot_id,
                        group_order=1,
                        group_key="g1",
                        group_label="G1",
                        is_selected=True,
                    ),
                ),
                rows=(
                    ProjectMatrixDraftRow(
                        draft_row_id="pmdr-r1",
                        project_matrix_draft_id="pmd-r1",
                        source_row_snapshot_id=source_snapshot.rows[0].row_snapshot_id,
                        row_order=1,
                        test_item="Visual",
                    ),
                ),
                cells=(
                    ProjectMatrixDraftCell(
                        draft_cell_id="pmdc-r1",
                        project_matrix_draft_id="pmd-r1",
                        draft_row_id="pmdr-r1",
                        draft_group_id="pmdg-r1",
                        cell_value="1",
                    ),
                ),
            )
            repo = ProjectMatrixDraftRepository(session)
            repo.create_snapshot(initial)
            replacement = ProjectMatrixDraftSnapshot(
                record=ProjectMatrixDraftRecord(
                    project_matrix_draft_id="pmd-r1",
                    project_id="P1",
                    source_import_id=source_import_id,
                    source_snapshot_id=source_snapshot.snapshot_id,
                    status=ProjectMatrixDraftStatus.DRAFT,
                    created_at="2026-05-22T10:00:00+00:00",
                    updated_at="2026-05-22T10:30:00+00:00",
                    base_confirmed_matrix_id=None,
                ),
                groups=(
                    ProjectMatrixDraftGroup(
                        draft_group_id="pmdg-r2",
                        project_matrix_draft_id="pmd-r1",
                        source_group_snapshot_id=source_snapshot.groups[0].group_snapshot_id,
                        group_order=1,
                        group_key="g1",
                        group_label="Group A",
                        is_selected=True,
                    ),
                    ProjectMatrixDraftGroup(
                        draft_group_id="pmdg-r3",
                        project_matrix_draft_id="pmd-r1",
                        source_group_snapshot_id=source_snapshot.groups[1].group_snapshot_id,
                        group_order=2,
                        group_key="g2",
                        group_label="Group B",
                        is_selected=False,
                    ),
                ),
                rows=(
                    ProjectMatrixDraftRow(
                        draft_row_id="pmdr-r2",
                        project_matrix_draft_id="pmd-r1",
                        source_row_snapshot_id=source_snapshot.rows[0].row_snapshot_id,
                        row_order=1,
                        test_item="Visual Updated",
                    ),
                ),
                cells=(
                    ProjectMatrixDraftCell(
                        draft_cell_id="pmdc-r2",
                        project_matrix_draft_id="pmd-r1",
                        draft_row_id="pmdr-r2",
                        draft_group_id="pmdg-r3",
                        cell_value="9",
                    ),
                ),
            )
            repo.replace_snapshot(replacement)
            session.commit()
            loaded = repo.get("pmd-r1")
            assert loaded is not None
            assert loaded.record.updated_at == "2026-05-22T10:30:00+00:00"
            assert len(loaded.groups) == 2
            assert len(loaded.rows) == 1
            assert len(loaded.cells) == 1
            assert loaded.cells[0].cell_value == "9"
    finally:
        engine.dispose()


def test_project_matrix_draft_repository_replace_snapshot_rolls_back_on_unique_failure(
    tmp_path: Path,
) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)
    try:
        with session_factory() as session:
            _seed_project(session)
            source_import_id, source_snapshot = _seed_source_snapshot(session)
            repo = ProjectMatrixDraftRepository(session)
            baseline = ProjectMatrixDraftSnapshot(
                record=ProjectMatrixDraftRecord(
                    project_matrix_draft_id="pmd-rb",
                    project_id="P1",
                    source_import_id=source_import_id,
                    source_snapshot_id=source_snapshot.snapshot_id,
                    status=ProjectMatrixDraftStatus.DRAFT,
                    created_at="2026-05-22T10:00:00+00:00",
                    updated_at="2026-05-22T10:00:00+00:00",
                    base_confirmed_matrix_id=None,
                ),
                groups=(
                    ProjectMatrixDraftGroup(
                        draft_group_id="pmdg-rb1",
                        project_matrix_draft_id="pmd-rb",
                        source_group_snapshot_id=source_snapshot.groups[0].group_snapshot_id,
                        group_order=1,
                        group_key="g1",
                        group_label="G1",
                        is_selected=True,
                    ),
                ),
                rows=(
                    ProjectMatrixDraftRow(
                        draft_row_id="pmdr-rb1",
                        project_matrix_draft_id="pmd-rb",
                        source_row_snapshot_id=source_snapshot.rows[0].row_snapshot_id,
                        row_order=1,
                        test_item="Visual",
                    ),
                ),
                cells=(),
            )
            repo.create_snapshot(baseline)
            session.commit()
            invalid = ProjectMatrixDraftSnapshot(
                record=ProjectMatrixDraftRecord(
                    project_matrix_draft_id="pmd-rb",
                    project_id="P1",
                    source_import_id=source_import_id,
                    source_snapshot_id=source_snapshot.snapshot_id,
                    status=ProjectMatrixDraftStatus.DRAFT,
                    created_at="2026-05-22T10:00:00+00:00",
                    updated_at="2026-05-22T10:05:00+00:00",
                    base_confirmed_matrix_id=None,
                ),
                groups=(
                    ProjectMatrixDraftGroup(
                        draft_group_id="pmdg-rb2",
                        project_matrix_draft_id="pmd-rb",
                        source_group_snapshot_id=source_snapshot.groups[0].group_snapshot_id,
                        group_order=1,
                        group_key="g1",
                        group_label="G1",
                        is_selected=True,
                    ),
                ),
                rows=(
                    ProjectMatrixDraftRow(
                        draft_row_id="pmdr-rb2",
                        project_matrix_draft_id="pmd-rb",
                        source_row_snapshot_id=source_snapshot.rows[0].row_snapshot_id,
                        row_order=1,
                        test_item="Visual",
                    ),
                    ProjectMatrixDraftRow(
                        draft_row_id="pmdr-rb3",
                        project_matrix_draft_id="pmd-rb",
                        source_row_snapshot_id=source_snapshot.rows[1].row_snapshot_id,
                        row_order=1,
                        test_item="LLCR",
                    ),
                ),
                cells=(),
            )
            with pytest.raises(IntegrityError):
                repo.replace_snapshot(invalid)
            session.rollback()
            reloaded = repo.get("pmd-rb")
            assert reloaded is not None
            assert len(reloaded.rows) == 1
            assert reloaded.rows[0].draft_row_id == "pmdr-rb1"
    finally:
        engine.dispose()


def test_project_matrix_draft_repository_supports_revision_draft_nullable_source_import(
    tmp_path: Path,
) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)
    try:
        with session_factory() as session:
            _seed_project(session)
            source_import_id, source_snapshot = _seed_source_snapshot(session)
            base_confirmed_id = "cmv-base"
            session.execute(
                text(
                    """
                INSERT INTO confirmed_matrix_versions (
                    confirmed_matrix_id, project_id, project_matrix_draft_id, source_import_id,
                    source_snapshot_id, confirmed_revision, is_active_authority, status,
                    confirmed_by, confirmed_at
                ) VALUES (:id, 'P1', 'pmd-base', :smi, :sms, 1, 1, 'confirmed', 'operator', '2026-05-23T09:00:00+00:00')
                """
                ),
                {"id": base_confirmed_id, "smi": source_import_id, "sms": source_snapshot.snapshot_id},
            )
            revision = ProjectMatrixDraftSnapshot(
                record=ProjectMatrixDraftRecord(
                    project_matrix_draft_id="pmd-rev",
                    project_id="P1",
                    source_import_id=None,
                    source_snapshot_id=source_snapshot.snapshot_id,
                    status=ProjectMatrixDraftStatus.DRAFT,
                    created_at="2026-05-23T10:00:00+00:00",
                    updated_at="2026-05-23T10:00:00+00:00",
                    base_confirmed_matrix_id=base_confirmed_id,
                ),
                groups=(),
                rows=(),
                cells=(),
            )
            repo = ProjectMatrixDraftRepository(session)
            repo.create_snapshot(revision)
            session.commit()

            loaded = repo.get("pmd-rev")
            assert loaded is not None
            assert loaded.record.source_import_id is None
            assert loaded.record.base_confirmed_matrix_id == base_confirmed_id
            assert (
                repo.get_by_project_and_base_confirmed_matrix("P1", base_confirmed_id)
                is not None
            )
    finally:
        engine.dispose()


def test_project_matrix_draft_repository_enforces_revision_base_uniqueness(
    tmp_path: Path,
) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)
    try:
        with session_factory() as session:
            _seed_project(session)
            source_import_id, source_snapshot = _seed_source_snapshot(session)
            base_confirmed_id = "cmv-base-uq"
            session.execute(
                text(
                    """
                INSERT INTO confirmed_matrix_versions (
                    confirmed_matrix_id, project_id, project_matrix_draft_id, source_import_id,
                    source_snapshot_id, confirmed_revision, is_active_authority, status,
                    confirmed_by, confirmed_at
                ) VALUES (:id, 'P1', 'pmd-base', :smi, :sms, 1, 1, 'confirmed', 'operator', '2026-05-23T09:00:00+00:00')
                """
                ),
                {"id": base_confirmed_id, "smi": source_import_id, "sms": source_snapshot.snapshot_id},
            )
            repo = ProjectMatrixDraftRepository(session)
            first = ProjectMatrixDraftSnapshot(
                record=ProjectMatrixDraftRecord(
                    project_matrix_draft_id="pmd-rev-1",
                    project_id="P1",
                    source_import_id=None,
                    source_snapshot_id=source_snapshot.snapshot_id,
                    status=ProjectMatrixDraftStatus.DRAFT,
                    created_at="2026-05-23T10:00:00+00:00",
                    updated_at="2026-05-23T10:00:00+00:00",
                    base_confirmed_matrix_id=base_confirmed_id,
                ),
                groups=(),
                rows=(),
                cells=(),
            )
            repo.create_snapshot(first)
            session.commit()

            second = ProjectMatrixDraftSnapshot(
                record=ProjectMatrixDraftRecord(
                    project_matrix_draft_id="pmd-rev-2",
                    project_id="P1",
                    source_import_id=None,
                    source_snapshot_id=source_snapshot.snapshot_id,
                    status=ProjectMatrixDraftStatus.DRAFT,
                    created_at="2026-05-23T10:01:00+00:00",
                    updated_at="2026-05-23T10:01:00+00:00",
                    base_confirmed_matrix_id=base_confirmed_id,
                ),
                groups=(),
                rows=(),
                cells=(),
            )
            with pytest.raises(IntegrityError):
                repo.create_snapshot(second)
            session.rollback()
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
                    {"group_key": "g1", "group_label": "G1"},
                    {"group_key": "g2", "group_label": "G2"},
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


def _create_temp_engine(tmp_path: Path):
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    return create_database_engine(settings)
