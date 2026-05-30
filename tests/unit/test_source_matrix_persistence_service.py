from __future__ import annotations

from datetime import date
from pathlib import Path

from backend.application.source_matrix_import_persistence_service import (
    PersistSourceMatrixImportCommand,
    SourceMatrixImportPersistenceService,
)
from backend.domain import Project, ProjectStatus
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    ProjectRepository,
    SourceMatrixImportRepository,
)
from backend.shared.config import Settings


def test_source_matrix_persistence_service_persists_sparse_cells_and_metadata(
    tmp_path: Path,
) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)
    try:
        with session_factory() as session:
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
            service = SourceMatrixImportPersistenceService(
                store=SourceMatrixImportRepository(session)
            )
            import_id = service.persist_from_draft(
                PersistSourceMatrixImportCommand(
                    project_id="P1",
                    draft_id="ptpd-1",
                    source_document_path="C:/specs/spec.docx",
                    source_document_name="spec.docx",
                    source_format=".docx",
                    source_asset_id="asset-1",
                    source_case_id="case-1",
                    source_draft_id="draft-1",
                    payload={
                        "groups": [
                            {"group_key": "g1", "group_label": "G1", "sample_size": 5},
                            {"group_key": "g2", "group_label": "G2", "sample_size": 6},
                        ],
                        "rows": [
                            {
                                "source_row_index": 3,
                                "test_item": "Visual Examination",
                                "source_section": "6.1",
                                "method": "EIA-364-18B",
                                "condition": "10x min magnification",
                                "requirement": "No detrimental condition",
                                "group_tokens": {"G1": "1", "G2": ""},
                                "is_sample_row": False,
                            },
                            {
                                "source_row_index": 4,
                                "test_item": "LLCR",
                                "source_section": "6.2",
                                "group_tokens": {"G1": "2,3", "G2": "4"},
                                "is_sample_row": False,
                            },
                        ],
                        "warnings": ["matrix warning"],
                        "blockers": [],
                        "source_metadata": {
                            "source_spec_number": "GS-12-1507",
                            "source_spec_revision": "Rev7",
                            "parse_time": "2026-05-22T08:00:00+00:00",
                            "parser_version": "parser-v2",
                            "payload_schema_version": "2.1",
                        },
                        "selected_group_keys_at_import": ["g2"],
                    },
                    created_at="2026-05-22T08:00:01+00:00",
                    task261_commit_fingerprint="fp-task261-001",
                )
            )
            session.commit()

            repo = SourceMatrixImportRepository(session)
            import_record = repo.get_import(import_id)
            snapshot = repo.get_snapshot_by_import(import_id)

            assert import_record is not None
            assert snapshot is not None
            assert import_record.parser_version == "parser-v2"
            assert import_record.payload_schema_version == "2.1"
            assert import_record.source_spec_number == "GS-12-1507"
            assert import_record.source_spec_revision == "Rev7"
            assert list(import_record.selected_group_keys_at_import) == ["g2"]
            assert import_record.task261_commit_fingerprint == "fp-task261-001"
            assert import_record.source_preview_payload is not None
            assert import_record.source_preview_payload["groups"][0]["group_key"] == "g1"
            lookup = repo.get_import_by_project_and_fingerprint(
                project_id="P1",
                task261_commit_fingerprint="fp-task261-001",
            )
            assert lookup is not None
            assert lookup.import_id == import_id
            assert len(snapshot.groups) == 2
            assert len(snapshot.rows) == 2
            assert len(snapshot.cells) == 3
            assert snapshot.rows[0].method == "EIA-364-18B"
            assert snapshot.rows[0].condition == "10x min magnification"
            assert snapshot.rows[0].requirement == "No detrimental condition"
    finally:
        engine.dispose()


def test_source_matrix_persistence_service_derives_rows_from_steps_when_rows_missing(
    tmp_path: Path,
) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)
    try:
        with session_factory() as session:
            ProjectRepository(session).create(
                Project(
                    project_id="P1",
                    project_no="DL-2026-05-001",
                    product_name="Connector",
                    requestor="Alice",
                    status=ProjectStatus.LTR_REGISTERED,
                )
            )
            service = SourceMatrixImportPersistenceService(
                store=SourceMatrixImportRepository(session)
            )
            import_id = service.persist_from_draft(
                PersistSourceMatrixImportCommand(
                    project_id="P1",
                    draft_id="ptpd-2",
                    source_document_path="C:/specs/spec.docx",
                    source_document_name="spec.docx",
                    source_format=".docx",
                    source_asset_id=None,
                    source_case_id=None,
                    source_draft_id=None,
                    payload={
                        "groups": [
                            {
                                "group_key": "g1",
                                "group_label": "G1",
                                "source_table_index": 21,
                                "steps": [
                                    {
                                        "raw_token": "1",
                                        "test_item": "Visual",
                                        "source_section": "6.1",
                                        "source_row_index": 10,
                                    },
                                    {
                                        "raw_token": "2",
                                        "test_item": "Visual",
                                        "source_section": "6.1",
                                        "source_row_index": 10,
                                    },
                                ],
                            },
                            {
                                "group_key": "g2",
                                "group_label": "G2",
                                "source_table_index": 21,
                                "steps": [
                                    {
                                        "raw_token": "3",
                                        "test_item": "Visual",
                                        "source_section": "6.1",
                                        "source_row_index": 10,
                                    }
                                ],
                            },
                        ],
                        "warnings": [],
                        "blockers": ["missing sample row"],
                    },
                    created_at="2026-05-22T09:00:00+00:00",
                )
            )
            session.commit()

            repo = SourceMatrixImportRepository(session)
            import_record = repo.get_import(import_id)
            snapshot = repo.get_snapshot_by_import(import_id)
            assert import_record is not None
            assert snapshot is not None
            assert import_record.import_status.value == "blocked"
            assert snapshot.source_table_index == 21
            assert len(snapshot.rows) == 1
            assert len(snapshot.cells) == 2
            values = sorted(cell.cell_value for cell in snapshot.cells)
            assert values == ["1, 2", "3"]
    finally:
        engine.dispose()


def test_source_matrix_persistence_service_normalizes_group_prefix_labels(
    tmp_path: Path,
) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)
    try:
        with session_factory() as session:
            ProjectRepository(session).create(
                Project(
                    project_id="P1",
                    project_no="DL-2026-05-001",
                    product_name="Connector",
                    requestor="Alice",
                    status=ProjectStatus.LTR_REGISTERED,
                )
            )
            service = SourceMatrixImportPersistenceService(
                store=SourceMatrixImportRepository(session)
            )
            import_id = service.persist_from_draft(
                PersistSourceMatrixImportCommand(
                    project_id="P1",
                    draft_id="ptpd-3",
                    source_document_path="C:/specs/spec.docx",
                    source_document_name="spec.docx",
                    source_format=".docx",
                    source_asset_id=None,
                    source_case_id=None,
                    source_draft_id=None,
                    payload={
                        "groups": [
                            {"group_key": "g1", "group_label": "Group 8a", "sample_size": 5},
                            {"group_key": "g2", "group_label": "group-2", "sample_size": 6},
                        ],
                        "rows": [
                            {
                                "source_row_index": 1,
                                "test_item": "Visual",
                                "source_section": "6.1",
                                "group_tokens": {"g1": "1", "g2": "2"},
                                "is_sample_row": False,
                            }
                        ],
                    },
                    created_at="2026-05-22T10:00:00+00:00",
                )
            )
            session.commit()

            snapshot = SourceMatrixImportRepository(session).get_snapshot_by_import(import_id)
            assert snapshot is not None
            assert [group.group_label for group in snapshot.groups] == ["8a", "2"]
    finally:
        engine.dispose()


def _create_temp_engine(tmp_path: Path):
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    return create_database_engine(settings)
