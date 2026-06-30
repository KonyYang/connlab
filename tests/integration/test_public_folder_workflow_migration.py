from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine

from backend.infrastructure.storage.database import init_db


def test_public_folder_workflow_tables_are_added_without_touching_legacy_upload_data(
    tmp_path: Path,
) -> None:
    engine = create_engine(f"sqlite:///{(tmp_path / 'legacy.sqlite3').as_posix()}", future=True)
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
            CREATE TABLE public_drive_upload_file_records (
                project_id VARCHAR(64) NOT NULL,
                relative_path VARCHAR(1024) NOT NULL,
                public_path VARCHAR(1024) NOT NULL,
                local_fingerprint VARCHAR(128) NOT NULL,
                public_fingerprint VARCHAR(128) NOT NULL,
                uploaded_at VARCHAR(64) NOT NULL,
                operation_id VARCHAR(64) NOT NULL,
                PRIMARY KEY (project_id, relative_path)
            )
            """
        )
        connection.exec_driver_sql(
            """
            INSERT INTO public_drive_upload_file_records (
                project_id,
                relative_path,
                public_path,
                local_fingerprint,
                public_fingerprint,
                uploaded_at,
                operation_id
            )
            VALUES ('P1', 'a.txt', 'D:/public/a.txt', 'local', 'public', '2026', 'op-old')
            """
        )

    init_db(engine)

    with engine.begin() as connection:
        tables = {
            row[0]
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).all()
        }
        assert "project_public_folder_workflow_states" in tables
        assert "project_public_folder_workflow_operations" in tables
        assert "project_public_folder_workflow_file_records" in tables
        legacy = connection.exec_driver_sql(
            "SELECT project_id, relative_path, operation_id FROM public_drive_upload_file_records"
        ).all()
        assert legacy == [("P1", "a.txt", "op-old")]
