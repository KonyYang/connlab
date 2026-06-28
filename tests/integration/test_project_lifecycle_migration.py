from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine

from backend.infrastructure.storage.database import init_db


def test_init_db_backfills_lifecycle_columns_for_legacy_projects(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "connlab.sqlite3"
    engine = create_engine(f"sqlite:///{database_path.as_posix()}", future=True)
    with engine.begin() as connection:
        connection.exec_driver_sql(
            """
            CREATE TABLE projects (
                project_id VARCHAR(64) NOT NULL,
                project_no VARCHAR(128),
                product_name VARCHAR(255) NOT NULL,
                requestor VARCHAR(255) NOT NULL,
                status VARCHAR(64) NOT NULL,
                business_unit VARCHAR(255),
                created_on DATE,
                PRIMARY KEY (project_id)
            )
            """
        )
        connection.exec_driver_sql(
            """
            INSERT INTO projects (
                project_id,
                project_no,
                product_name,
                requestor,
                status,
                business_unit,
                created_on
            )
            VALUES
                (
                    'P-ACTIVE',
                    'DL-2026-06-001',
                    'Connector A',
                    'Alice',
                    'ltr_registered',
                    NULL,
                    NULL
                ),
                (
                    'P-STOPPED',
                    'DL-2026-06-002',
                    'Connector B',
                    'Bob',
                    'cancelled',
                    NULL,
                    NULL
                ),
                (
                    'P-CLOSED',
                    'DL-2026-06-003',
                    'Connector C',
                    'Cara',
                    'closed',
                    NULL,
                    NULL
                )
            """
        )

    init_db(engine)

    with engine.connect() as connection:
        rows = {
            row.project_id: row
            for row in connection.exec_driver_sql(
                "SELECT project_id, status, lifecycle_state, closure_type, "
                "close_reason_category FROM projects"
            ).all()
        }
        table_names = {
            row[0]
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).all()
        }

    assert rows["P-ACTIVE"].lifecycle_state == "active"
    assert rows["P-ACTIVE"].closure_type is None
    assert rows["P-ACTIVE"].close_reason_category is None
    assert rows["P-STOPPED"].status == "cancelled"
    assert rows["P-STOPPED"].lifecycle_state == "stopped"
    assert rows["P-STOPPED"].closure_type is None
    assert rows["P-STOPPED"].close_reason_category is None
    assert rows["P-CLOSED"].status == "closed"
    assert rows["P-CLOSED"].lifecycle_state == "closed"
    assert rows["P-CLOSED"].closure_type == "administrative"
    assert rows["P-CLOSED"].close_reason_category == "other"
    assert "project_lifecycle_events" in table_names
