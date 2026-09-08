import shutil
import uuid
from pathlib import Path

from sqlalchemy import inspect, text

from backend.infrastructure.storage.database import (
    Base,
    build_sqlite_url,
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.shared.config import Settings


def test_build_sqlite_url_uses_configured_path() -> None:
    database_path = Path("tmp") / "connlab-test.sqlite3"

    assert build_sqlite_url(database_path) == "sqlite:///tmp/connlab-test.sqlite3"


def test_create_engine_session_and_init_db_with_temp_file() -> None:
    workspace_tmp = _make_workspace_temp_dir()
    database_path = workspace_tmp / "storage" / "connlab.sqlite3"
    settings = Settings(
        data_dir=workspace_tmp / "data",
        projects_dir=workspace_tmp / "projects",
        templates_dir=workspace_tmp / "templates",
        database_path=database_path,
    )

    try:
        engine = create_database_engine(settings)
        init_db(engine)
        session_factory = create_session_factory(engine)

        with session_factory() as session:
            assert session.execute(text("select 1")).scalar_one() == 1

        assert database_path.is_file()
        assert set(inspect(engine).get_table_names()) == set(Base.metadata.tables.keys())
        assert "project_schedule_revisions" in inspect(engine).get_table_names()
        engine.dispose()
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)


def test_init_db_adds_matrix_schedule_planning_columns_to_existing_schema() -> None:
    workspace_tmp = _make_workspace_temp_dir()
    database_path = workspace_tmp / "storage" / "connlab.sqlite3"
    settings = Settings(
        data_dir=workspace_tmp / "data",
        projects_dir=workspace_tmp / "projects",
        templates_dir=workspace_tmp / "templates",
        database_path=database_path,
    )

    try:
        engine = create_database_engine(settings)
        with engine.begin() as connection:
            connection.execute(
                text("create table project_matrix_draft_records (project_matrix_draft_id text primary key)")
            )
            connection.execute(
                text("create table project_matrix_draft_rows (draft_row_id text primary key)")
            )
            connection.execute(
                text("create table confirmed_matrix_versions (confirmed_matrix_id text primary key)")
            )
            connection.execute(
                text("create table confirmed_matrix_rows (confirmed_row_id text primary key)")
            )

        init_db(engine)

        assert _column_names(engine, "project_matrix_draft_records") >= {
            "pre_test_buffer_days",
            "post_test_buffer_days",
            "sample_received_date",
            "planned_test_start_date",
            "planned_test_complete_date",
            "estimated_completion_date",
        }
        assert "day_expression" in _column_names(engine, "project_matrix_draft_rows")
        assert _column_names(engine, "confirmed_matrix_versions") >= {
            "pre_test_buffer_days",
            "post_test_buffer_days",
            "sample_received_date",
            "planned_test_start_date",
            "planned_test_complete_date",
            "estimated_completion_date",
        }
        assert "day_expression" in _column_names(engine, "confirmed_matrix_rows")
        engine.dispose()
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)


def test_init_db_reconciles_matrix_draft_lifecycle_for_existing_projects() -> None:
    workspace_tmp = _make_workspace_temp_dir()
    database_path = workspace_tmp / "storage" / "connlab.sqlite3"
    settings = Settings(
        data_dir=workspace_tmp / "data",
        projects_dir=workspace_tmp / "projects",
        templates_dir=workspace_tmp / "templates",
        database_path=database_path,
    )

    try:
        engine = create_database_engine(settings)
        init_db(engine)
        with engine.begin() as connection:
            connection.execute(
                text("DROP INDEX IF EXISTS uq_project_matrix_draft_one_working")
            )
            connection.execute(
                text(
                    """
                    INSERT INTO projects (
                        project_id, project_no, product_name, requestor, status,
                        lifecycle_state
                    ) VALUES ('P-LIFE', 'DL-LIFE', 'Connector', 'Alice', 'registered', 'active')
                    """
                )
            )
            for index in range(1, 8):
                connection.execute(
                    text(
                        """
                        INSERT INTO source_matrix_import_records (
                            import_id, project_id, source_document_path,
                            source_document_name, source_format, import_status,
                            parse_time, parser_version, payload_schema_version,
                            warnings_json, blockers_json,
                            selected_group_keys_at_import_json, created_at
                        ) VALUES (
                            :import_id, 'P-LIFE', :path, :name, '.pdf', 'imported',
                            :created_at, 'test', '1', '[]', '[]', '[]', :created_at
                        )
                        """
                    ),
                    {
                        "import_id": f"import-{index}",
                        "path": f"C:/spec-{index}.pdf",
                        "name": f"spec-{index}.pdf",
                        "created_at": f"2026-09-0{index}T08:00:00+00:00",
                    },
                )
                connection.execute(
                    text(
                        """
                        INSERT INTO source_matrix_snapshots (
                            snapshot_id, import_id, project_id, row_count,
                            group_count, cell_count, created_at
                        ) VALUES (
                            :snapshot_id, :import_id, 'P-LIFE', 0, 0, 0, :created_at
                        )
                        """
                    ),
                    {
                        "snapshot_id": f"snapshot-{index}",
                        "import_id": f"import-{index}",
                        "created_at": f"2026-09-0{index}T08:00:00+00:00",
                    },
                )

            draft_rows = (
                ("draft-1", "import-1", "snapshot-1", None, "2026-09-01T08:00:00+00:00"),
                ("draft-2", "import-2", "snapshot-2", None, "2026-09-02T08:00:00+00:00"),
                ("draft-3", None, "snapshot-2", "confirmed-2", "2026-09-07T12:00:00+00:00"),
                ("draft-4", None, "snapshot-1", "confirmed-1", "2026-09-07T13:00:00+00:00"),
                ("draft-5", "import-5", "snapshot-5", None, "2026-09-06T08:00:00+00:00"),
                ("draft-6", "import-6", "snapshot-6", None, "2026-09-01T06:00:00+00:00"),
                ("draft-7", "import-7", "snapshot-7", None, "2026-09-01T07:00:00+00:00"),
            )
            for draft_id, import_id, snapshot_id, base_id, updated_at in draft_rows:
                connection.execute(
                    text(
                        """
                        INSERT INTO project_matrix_draft_records (
                            project_matrix_draft_id, project_id, source_import_id,
                            source_snapshot_id, base_confirmed_matrix_id, status,
                            created_at, updated_at
                        ) VALUES (
                            :draft_id, 'P-LIFE', :import_id, :snapshot_id,
                            :base_id, 'draft', :updated_at, :updated_at
                        )
                        """
                    ),
                    {
                        "draft_id": draft_id,
                        "import_id": import_id,
                        "snapshot_id": snapshot_id,
                        "base_id": base_id,
                        "updated_at": updated_at,
                    },
                )
            for revision, draft_id, import_id, snapshot_id, active, status in (
                (1, "draft-1", "import-1", "snapshot-1", 0, "superseded"),
                (2, "draft-2", "import-2", "snapshot-2", 1, "confirmed"),
            ):
                connection.execute(
                    text(
                        """
                        INSERT INTO confirmed_matrix_versions (
                            confirmed_matrix_id, project_id, project_matrix_draft_id,
                            source_import_id, source_snapshot_id, confirmed_revision,
                            is_active_authority, status, confirmed_by, confirmed_at
                        ) VALUES (
                            :confirmed_id, 'P-LIFE', :draft_id, :import_id,
                            :snapshot_id, :revision, :active, :status, 'operator',
                            '2026-09-02T09:00:00+00:00'
                        )
                        """
                    ),
                    {
                        "confirmed_id": f"confirmed-{revision}",
                        "draft_id": draft_id,
                        "import_id": import_id,
                        "snapshot_id": snapshot_id,
                        "revision": revision,
                        "active": active,
                        "status": status,
                    },
                )
            connection.execute(
                text(
                    """
                    INSERT INTO project_matrix_draft_groups (
                        draft_group_id, project_matrix_draft_id, group_order,
                        group_key, group_label, is_selected
                    ) VALUES ('group-stale', 'draft-5', 1, 'g1', 'Group 1', 1)
                    """
                )
            )
            connection.execute(
                text(
                    """
                    INSERT INTO project_matrix_draft_rows (
                        draft_row_id, project_matrix_draft_id, row_order,
                        test_item, is_sample_row
                    ) VALUES ('row-stale', 'draft-5', 1, 'Visual', 0)
                    """
                )
            )
            connection.execute(
                text(
                    """
                    INSERT INTO project_matrix_draft_cells (
                        draft_cell_id, project_matrix_draft_id, draft_row_id,
                        draft_group_id, cell_value
                    ) VALUES (
                        'cell-stale', 'draft-5', 'row-stale', 'group-stale', '1'
                    )
                    """
                )
            )
            connection.execute(
                text(
                    """
                    INSERT INTO matrix_fee_pending_rebases (
                        pending_rebase_id, project_id, project_matrix_draft_id,
                        base_confirmed_matrix_id, base_confirmed_revision,
                        fee_rule_version_id, matrix_draft_payload_signature,
                        generation, payload_json, created_at, updated_at
                    ) VALUES (
                        'pending-stale', 'P-LIFE', 'draft-5', 'confirmed-2', 2,
                        'fee-rules', 'signature', 1, '{}',
                        '2026-09-06T08:00:00+00:00',
                        '2026-09-06T08:00:00+00:00'
                    )
                    """
                )
            )

        init_db(engine)

        with engine.connect() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT project_matrix_draft_id, status
                    FROM project_matrix_draft_records
                    WHERE project_id = 'P-LIFE'
                    ORDER BY project_matrix_draft_id
                    """
                )
            ).all()
        assert rows == [
            ("draft-1", "superseded"),
            ("draft-2", "superseded"),
            ("draft-3", "draft"),
        ]
        with engine.connect() as connection:
            assert connection.execute(
                text("SELECT COUNT(*) FROM project_matrix_draft_groups WHERE project_matrix_draft_id = 'draft-5'")
            ).scalar_one() == 0
            assert connection.execute(
                text("SELECT COUNT(*) FROM project_matrix_draft_rows WHERE project_matrix_draft_id = 'draft-5'")
            ).scalar_one() == 0
            assert connection.execute(
                text("SELECT COUNT(*) FROM project_matrix_draft_cells WHERE project_matrix_draft_id = 'draft-5'")
            ).scalar_one() == 0
            assert connection.execute(
                text("SELECT COUNT(*) FROM matrix_fee_pending_rebases WHERE project_matrix_draft_id = 'draft-5'")
            ).scalar_one() == 0
            indexes = connection.execute(
                text("PRAGMA index_list(project_matrix_draft_records)")
            ).mappings().all()
            assert any(
                row["name"] == "uq_project_matrix_draft_one_working"
                and row["unique"] == 1
                and row["partial"] == 1
                for row in indexes
            )
        engine.dispose()
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)


def test_settings_load_defaults_database_path_under_data_dir() -> None:
    workspace_tmp = _make_workspace_temp_dir()

    try:
        settings = Settings.load(base_dir=workspace_tmp)

        assert settings.database_path == workspace_tmp / "data" / "connlab.sqlite3"
        assert settings.database_path.parent.is_dir()
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)


def test_settings_load_database_path_override(monkeypatch) -> None:
    workspace_tmp = _make_workspace_temp_dir()
    monkeypatch.setenv("CONNLAB_DATABASE_PATH", "custom-store/custom.sqlite3")

    try:
        settings = Settings.load(base_dir=workspace_tmp)

        assert settings.database_path == (
            workspace_tmp / "custom-store" / "custom.sqlite3"
        ).resolve()
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)


def _make_workspace_temp_dir() -> Path:
    root = Path.cwd() / "tmp"
    root.mkdir(exist_ok=True)
    path = root / f"task003-{uuid.uuid4().hex}"
    path.mkdir()
    return path


def _column_names(engine, table_name: str) -> set[str]:
    with engine.connect() as connection:
        rows = connection.execute(text(f"pragma table_info({table_name})")).all()
    return {str(row[1]) for row in rows}
