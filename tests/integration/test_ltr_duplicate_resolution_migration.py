from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import create_engine

from backend.infrastructure.storage.database import init_db


def test_ltr_duplicate_resolution_migration_replaces_global_ltr_unique(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "legacy.sqlite3"
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
            CREATE TABLE ltr_records (
                ltr_id VARCHAR(64) NOT NULL,
                project_id VARCHAR(64) NOT NULL,
                ltr_number VARCHAR(128) NOT NULL UNIQUE,
                status VARCHAR(64) NOT NULL,
                registered_on DATE,
                requested_by VARCHAR(255),
                requested_date DATE,
                notes TEXT,
                PRIMARY KEY (ltr_id),
                FOREIGN KEY(project_id) REFERENCES projects(project_id)
            )
            """
        )
        connection.exec_driver_sql(
            """
            INSERT INTO projects (
                project_id, project_no, product_name, requestor, status
            ) VALUES ('P1', 'P1', 'Connector', 'Alice', 'ltr_registered')
            """
        )
        connection.exec_driver_sql(
            """
            INSERT INTO ltr_records (
                ltr_id, project_id, ltr_number, status
            ) VALUES ('L1', 'P1', 'DL-2026-05-001', 'registered')
            """
        )

    init_db(engine)

    with engine.begin() as connection:
        columns = {
            row[1] for row in connection.exec_driver_sql("PRAGMA table_info(ltr_records)")
        }
        assert {
            "is_current_owner",
            "superseded_at",
            "superseded_by_ltr_id",
            "superseded_reason",
            "owner_version",
        }.issubset(columns)
        table_names = {
            row[0]
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert "ltr_duplicate_resolution_tokens" in table_names
        assert "ltr_association_events" in table_names

        connection.exec_driver_sql(
            """
            INSERT INTO projects (
                project_id, project_no, product_name, requestor, status, lifecycle_state
            ) VALUES ('P2', 'P2', 'Connector 2', 'Bob', 'ltr_registered', 'active')
            """
        )
        connection.exec_driver_sql(
            """
            INSERT INTO ltr_records (
                ltr_id, project_id, ltr_number, status, is_current_owner, owner_version
            ) VALUES ('L0', 'P2', 'DL-2026-05-001', 'registered', 0, 1)
            """
        )

        with pytest.raises(Exception):
            connection.exec_driver_sql(
                """
                INSERT INTO ltr_records (
                    ltr_id, project_id, ltr_number, status, is_current_owner, owner_version
                ) VALUES ('L2', 'P2', 'DL-2026-05-001', 'registered', 1, 1)
                """
            )
