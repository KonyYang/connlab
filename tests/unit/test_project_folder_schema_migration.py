import pytest
from sqlalchemy import create_engine, event
from backend.infrastructure.storage.project_folder_schema_migration import migrate_project_folder_schema


def legacy_engine(tmp_path):
    engine = create_engine(f"sqlite:///{(tmp_path / 'migration.sqlite').as_posix()}")
    with engine.begin() as connection:
        connection.exec_driver_sql("CREATE TABLE project_official_workspace_records (workspace_id VARCHAR(64) PRIMARY KEY, project_id VARCHAR(64) NOT NULL UNIQUE, template_source_path VARCHAR(1024) NOT NULL)")
        connection.exec_driver_sql("CREATE INDEX ix_workspace_project ON project_official_workspace_records(project_id)")
        connection.exec_driver_sql("INSERT INTO project_official_workspace_records VALUES ('W1','P1','retained-template')")
        connection.exec_driver_sql("CREATE TABLE project_public_folder_workflow_states (project_id VARCHAR(64) PRIMARY KEY, auto_sync_enabled BOOLEAN)")
        connection.exec_driver_sql("INSERT INTO project_public_folder_workflow_states VALUES ('P1',1)")
    return engine


def test_nullable_template_migration_preserves_rows_keys_and_is_idempotent(tmp_path):
    engine = legacy_engine(tmp_path)
    migrate_project_folder_schema(engine)
    migrate_project_folder_schema(engine)
    with engine.begin() as connection:
        assert connection.exec_driver_sql("SELECT template_source_path,creation_kind FROM project_official_workspace_records WHERE project_id='P1'").one() == ('retained-template','template')
        connection.exec_driver_sql("INSERT INTO project_official_workspace_records VALUES ('W2','P2',NULL,'basic')")
        assert connection.exec_driver_sql("SELECT auto_sync_enabled,binding_json FROM project_public_folder_workflow_states").one() == (1,None)
        assert 'ix_workspace_project' in {row[1] for row in connection.exec_driver_sql("PRAGMA index_list(project_official_workspace_records)")}
        assert connection.exec_driver_sql("PRAGMA foreign_key_check").all() == []
    engine.dispose()


def test_interrupted_migration_rolls_back_ddl_and_retries_without_deleting_data(tmp_path):
    engine = legacy_engine(tmp_path)
    def fail(_conn, _cursor, statement, _params, _context, _many):
        if statement.startswith('INSERT INTO _workspace_phase1_migration'):
            raise RuntimeError('injected migration interruption')
    event.listen(engine, 'before_cursor_execute', fail)
    with pytest.raises(RuntimeError):
        migrate_project_folder_schema(engine)
    event.remove(engine, 'before_cursor_execute', fail)
    with engine.connect() as connection:
        assert connection.exec_driver_sql("SELECT template_source_path FROM project_official_workspace_records").scalar_one() == 'retained-template'
        assert '_workspace_phase1_migration' not in connection.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table'").scalars().all()
    migrate_project_folder_schema(engine)
    engine.dispose()
