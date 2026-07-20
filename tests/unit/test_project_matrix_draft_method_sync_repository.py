from __future__ import annotations

from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.models_project_matrix_draft import (
    ProjectMatrixDraftRecordModel,
    ProjectMatrixDraftRowModel,
)
from backend.infrastructure.storage.repositories.project_matrix_draft import (
    ProjectMatrixDraftRepository,
)
from backend.shared.config import Settings


def test_method_sync_cas_updates_only_selected_method_and_root_context(tmp_path) -> None:
    settings = Settings(
        data_dir=tmp_path,
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "db.sqlite3",
    )
    engine = create_database_engine(settings)
    init_db(engine)
    factory = create_session_factory(engine)
    with factory() as session:
        session.add(
            ProjectMatrixDraftRecordModel(
                project_matrix_draft_id="D1",
                project_id="P1",
                source_import_id=None,
                source_snapshot_id="S1",
                base_confirmed_matrix_id="CM1",
                status="draft",
                created_at="old",
                updated_at="old",
            )
        )
        session.add_all(
            [
                ProjectMatrixDraftRowModel(
                    draft_row_id="R1",
                    project_matrix_draft_id="D1",
                    source_row_snapshot_id=None,
                    row_order=1,
                    test_item="CR",
                    method="EIA-364-04A",
                    requirement="Keep",
                    is_sample_row=False,
                ),
                ProjectMatrixDraftRowModel(
                    draft_row_id="R2",
                    project_matrix_draft_id="D1",
                    source_row_snapshot_id=None,
                    row_order=2,
                    test_item="Other",
                    method="EIA-364-18C",
                    is_sample_row=False,
                ),
            ]
        )
        session.commit()

        changed = ProjectMatrixDraftRepository(session).apply_method_sync(
            project_matrix_draft_id="D1",
            expected_updated_at="old",
            expected_status="draft",
            expected_base_confirmed_matrix_id="CM1",
            updated_at="new",
            method_sync_context_json='{"schema":"matrix-method-sync:v1"}',
            updates=(("R1", "EIA-364-04A", "EIA-364-04B"),),
        )
        session.commit()

        assert changed is True
        assert session.get(ProjectMatrixDraftRowModel, "R1").method == "EIA-364-04B"
        assert session.get(ProjectMatrixDraftRowModel, "R1").requirement == "Keep"
        assert session.get(ProjectMatrixDraftRowModel, "R2").method == "EIA-364-18C"
        root = session.get(ProjectMatrixDraftRecordModel, "D1")
        assert root.updated_at == "new"
        assert root.method_sync_context_json == '{"schema":"matrix-method-sync:v1"}'
    engine.dispose()


def test_method_sync_row_conflict_rolls_back_root_and_other_rows(tmp_path) -> None:
    settings = Settings(
        data_dir=tmp_path,
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "conflict.sqlite3",
    )
    engine = create_database_engine(settings)
    init_db(engine)
    factory = create_session_factory(engine)
    with factory() as session:
        session.add(
            ProjectMatrixDraftRecordModel(
                project_matrix_draft_id="D1",
                project_id="P1",
                source_import_id=None,
                source_snapshot_id="S1",
                base_confirmed_matrix_id="CM1",
                status="draft",
                created_at="old",
                updated_at="old",
            )
        )
        session.add_all(
            [
                ProjectMatrixDraftRowModel(
                    draft_row_id="R1",
                    project_matrix_draft_id="D1",
                    source_row_snapshot_id=None,
                    row_order=1,
                    test_item="CR",
                    method="EIA-364-04A",
                    is_sample_row=False,
                ),
                ProjectMatrixDraftRowModel(
                    draft_row_id="R2",
                    project_matrix_draft_id="D1",
                    source_row_snapshot_id=None,
                    row_order=2,
                    test_item="Other",
                    method="changed",
                    is_sample_row=False,
                ),
            ]
        )
        session.commit()

        changed = ProjectMatrixDraftRepository(session).apply_method_sync(
            project_matrix_draft_id="D1",
            expected_updated_at="old",
            expected_status="draft",
            expected_base_confirmed_matrix_id="CM1",
            updated_at="new",
            method_sync_context_json='{"schema":"matrix-method-sync:v1"}',
            updates=(
                ("R1", "EIA-364-04A", "EIA-364-04B"),
                ("R2", "expected", "replacement"),
            ),
        )

        assert changed is False
        assert session.get(ProjectMatrixDraftRowModel, "R1").method == "EIA-364-04A"
        assert session.get(ProjectMatrixDraftRecordModel, "D1").updated_at == "old"
    engine.dispose()
