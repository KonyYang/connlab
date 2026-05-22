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
