from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from sqlalchemy.exc import IntegrityError

from backend.domain import (
    Project,
    ProjectStatus,
    SourceMatrixCellSnapshot,
    SourceMatrixGroupSnapshot,
    SourceMatrixImportRecord,
    SourceMatrixImportStatus,
    SourceMatrixRowSnapshot,
    SourceMatrixSnapshot,
)
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


def test_source_matrix_import_repository_rolls_back_on_snapshot_write_failure(
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
            session.commit()

        with session_factory() as session:
            repo = SourceMatrixImportRepository(session)
            import_record = SourceMatrixImportRecord(
                import_id="smi-1",
                project_id="P1",
                draft_id="ptpd-1",
                source_document_path="C:/spec.docx",
                source_document_name="spec.docx",
                source_format=".docx",
                source_asset_id=None,
                source_case_id=None,
                source_draft_id=None,
                import_status=SourceMatrixImportStatus.IMPORTED,
                source_spec_number=None,
                source_spec_revision=None,
                parse_time="2026-05-22T10:00:00+00:00",
                parser_version="parser-v1",
                payload_schema_version="1.0",
                warnings=(),
                blockers=(),
                selected_group_keys_at_import=("g1",),
                created_at="2026-05-22T10:00:00+00:00",
            )
            # Deliberately use duplicate row_order values to trigger unique constraint failure.
            snapshot = SourceMatrixSnapshot(
                snapshot_id="sms-1",
                import_id="smi-1",
                project_id="P1",
                source_table_index=21,
                rows=(
                    SourceMatrixRowSnapshot(
                        row_snapshot_id="smr-1",
                        row_order=1,
                        source_row_index=10,
                        test_item="Visual",
                    ),
                    SourceMatrixRowSnapshot(
                        row_snapshot_id="smr-2",
                        row_order=1,
                        source_row_index=11,
                        test_item="LLCR",
                    ),
                ),
                groups=(
                    SourceMatrixGroupSnapshot(
                        group_snapshot_id="smg-1",
                        group_order=1,
                        group_key="g1",
                        group_label="G1",
                    ),
                ),
                cells=(
                    SourceMatrixCellSnapshot(
                        cell_snapshot_id="smc-1",
                        row_snapshot_id="smr-1",
                        group_snapshot_id="smg-1",
                        cell_value="1",
                    ),
                ),
                created_at="2026-05-22T10:00:00+00:00",
            )

            with pytest.raises(IntegrityError):
                repo.create_import_snapshot(import_record, snapshot)
            session.rollback()

        with session_factory() as session:
            repo = SourceMatrixImportRepository(session)
            assert repo.get_import("smi-1") is None
            assert repo.list_imports_by_project("P1") == []
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
