"""Legacy migration preserves records and is safe to rerun."""

import pytest
from sqlalchemy import create_engine, text, inspect

from backend.infrastructure.storage.project_registry_schema_migration import migrate_project_registry_schema
from backend.infrastructure.storage.database import init_db


def test_legacy_projects_receive_active_location_without_touching_business_values():
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.exec_driver_sql("CREATE TABLE projects (project_id TEXT PRIMARY KEY, status TEXT, project_no TEXT)")
        connection.exec_driver_sql("INSERT INTO projects VALUES ('old','closed','DL-2026-01-002')")
    migrate_project_registry_schema(engine)
    migrate_project_registry_schema(engine)
    with engine.connect() as connection:
        row = connection.execute(text("SELECT status,project_no,registry_state,registry_revision FROM projects")).one()
    assert tuple(row) == ("closed", "DL-2026-01-002", "active", 0)
    engine.dispose()


def test_new_schema_and_repeat_startup_preserve_registry_history():
    engine = create_engine("sqlite:///:memory:")
    init_db(engine)
    with engine.begin() as connection:
        connection.exec_driver_sql("INSERT INTO projects(project_id,product_name,requestor,status,lifecycle_state,registry_state,registry_revision) VALUES('old','Sample','User','draft','active','trash',2)")
    init_db(engine)
    with engine.connect() as connection:
        assert tuple(connection.execute(text("SELECT registry_state,registry_revision FROM projects")).one()) == ("trash", 2)
    assert "project_registry_events" in inspect(engine).get_table_names()
    engine.dispose()


def test_incompatible_existing_registry_state_is_rejected():
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.exec_driver_sql("CREATE TABLE projects(project_id TEXT PRIMARY KEY, registry_state TEXT, registry_revision INTEGER)")
        connection.exec_driver_sql("INSERT INTO projects VALUES('old','purged',-1)")
    with pytest.raises(RuntimeError, match="incompatible"):
        migrate_project_registry_schema(engine)
    engine.dispose()
