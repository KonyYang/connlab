"""SQLite database foundation for ConnLab."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.shared.config import Settings


class Base(DeclarativeBase):
    """Base class for future SQLAlchemy ORM models."""


def build_sqlite_url(database_path: Path) -> str:
    """Build a SQLAlchemy SQLite URL from a filesystem path."""
    return f"sqlite:///{database_path.as_posix()}"


def create_database_engine(
    settings: Settings | None = None,
    **engine_options: Any,
) -> Engine:
    """Create a SQLAlchemy engine using the configured SQLite database path."""
    resolved_settings = settings or Settings.load()
    resolved_settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(
        build_sqlite_url(resolved_settings.database_path),
        future=True,
        **engine_options,
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create the application session factory for a SQLAlchemy engine."""
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db(engine: Engine) -> None:
    """Create all registered SQLAlchemy tables for the supplied engine."""
    from backend.infrastructure.storage import models  # noqa: F401
    from backend.infrastructure.storage import models_confirmed_matrix_authority  # noqa: F401
    from backend.infrastructure.storage import models_project_matrix_draft  # noqa: F401
    from backend.infrastructure.storage import models_matrix_source  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate_project_no_optional(engine)
    _migrate_project_matrix_draft_lineage_columns_optional(engine)
    _migrate_project_matrix_draft_row_detail_columns(engine)


def _migrate_project_no_optional(engine: Engine) -> None:
    """Relax legacy project_no NOT NULL/UNIQUE constraints in local SQLite DBs."""
    if engine.dialect.name != "sqlite":
        return
    with engine.begin() as connection:
        table_names = {
            row[0]
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        if "projects" not in table_names:
            return
        columns = connection.exec_driver_sql("PRAGMA table_info(projects)").all()
        project_no_column = next((row for row in columns if row[1] == "project_no"), None)
        if project_no_column is None or not bool(project_no_column[3]):
            if not _has_single_column_unique_index(connection, "projects", "project_no"):
                return

        connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
        try:
            connection.exec_driver_sql(
                """
                CREATE TABLE projects_new (
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
                INSERT INTO projects_new (
                    project_id,
                    project_no,
                    product_name,
                    requestor,
                    status,
                    business_unit,
                    created_on
                )
                SELECT
                    project_id,
                    NULLIF(project_no, ''),
                    product_name,
                    requestor,
                    status,
                    business_unit,
                    created_on
                FROM projects
                """
            )
            connection.exec_driver_sql("DROP TABLE projects")
            connection.exec_driver_sql("ALTER TABLE projects_new RENAME TO projects")
        finally:
            connection.exec_driver_sql("PRAGMA foreign_keys=ON")


def _has_single_column_unique_index(connection: Any, table: str, column: str) -> bool:
    """Return whether a table has a unique index only on one named column."""
    for index in connection.exec_driver_sql(f"PRAGMA index_list({table})").all():
        if not bool(index[2]):
            continue
        indexed_columns = [
            row[2]
            for row in connection.exec_driver_sql(f"PRAGMA index_info({index[1]})").all()
        ]
        if indexed_columns == [column]:
            return True
    return False


def _migrate_project_matrix_draft_lineage_columns_optional(engine: Engine) -> None:
    """Relax source lineage columns to nullable for local-added draft rows/groups."""
    if engine.dialect.name != "sqlite":
        return
    with engine.begin() as connection:
        table_names = {
            row[0]
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        if "project_matrix_draft_groups" not in table_names or "project_matrix_draft_rows" not in table_names:
            return
        group_columns = connection.exec_driver_sql(
            "PRAGMA table_info(project_matrix_draft_groups)"
        ).all()
        row_columns = connection.exec_driver_sql(
            "PRAGMA table_info(project_matrix_draft_rows)"
        ).all()
        group_lineage = next(
            (row for row in group_columns if row[1] == "source_group_snapshot_id"),
            None,
        )
        row_lineage = next(
            (row for row in row_columns if row[1] == "source_row_snapshot_id"),
            None,
        )
        if (group_lineage is None or not bool(group_lineage[3])) and (
            row_lineage is None or not bool(row_lineage[3])
        ):
            return

        connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
        try:
            connection.exec_driver_sql(
                """
                CREATE TABLE project_matrix_draft_groups_new (
                    draft_group_id VARCHAR(64) NOT NULL,
                    project_matrix_draft_id VARCHAR(64) NOT NULL,
                    source_group_snapshot_id VARCHAR(64),
                    group_order INTEGER NOT NULL,
                    group_key VARCHAR(255) NOT NULL,
                    group_label VARCHAR(255) NOT NULL,
                    is_selected BOOLEAN NOT NULL,
                    sample_quantity_expression TEXT,
                    sample_note TEXT,
                    PRIMARY KEY (draft_group_id),
                    CONSTRAINT uq_project_matrix_draft_group_order
                        UNIQUE (project_matrix_draft_id, group_order),
                    CONSTRAINT uq_project_matrix_draft_group_source_lineage
                        UNIQUE (project_matrix_draft_id, source_group_snapshot_id),
                    FOREIGN KEY(project_matrix_draft_id)
                        REFERENCES project_matrix_draft_records(project_matrix_draft_id),
                    FOREIGN KEY(source_group_snapshot_id)
                        REFERENCES source_matrix_group_snapshots(group_snapshot_id)
                )
                """
            )
            connection.exec_driver_sql(
                """
                INSERT INTO project_matrix_draft_groups_new (
                    draft_group_id,
                    project_matrix_draft_id,
                    source_group_snapshot_id,
                    group_order,
                    group_key,
                    group_label,
                    is_selected,
                    sample_quantity_expression,
                    sample_note
                )
                SELECT
                    draft_group_id,
                    project_matrix_draft_id,
                    source_group_snapshot_id,
                    group_order,
                    group_key,
                    group_label,
                    is_selected,
                    sample_quantity_expression,
                    sample_note
                FROM project_matrix_draft_groups
                """
            )
            connection.exec_driver_sql("DROP TABLE project_matrix_draft_groups")
            connection.exec_driver_sql(
                "ALTER TABLE project_matrix_draft_groups_new RENAME TO project_matrix_draft_groups"
            )
            connection.exec_driver_sql(
                "CREATE INDEX ix_project_matrix_draft_groups_project_matrix_draft_id "
                "ON project_matrix_draft_groups(project_matrix_draft_id)"
            )

            connection.exec_driver_sql(
                """
                CREATE TABLE project_matrix_draft_rows_new (
                    draft_row_id VARCHAR(64) NOT NULL,
                    project_matrix_draft_id VARCHAR(64) NOT NULL,
                    source_row_snapshot_id VARCHAR(64),
                    row_order INTEGER NOT NULL,
                    test_item TEXT NOT NULL,
                    source_section TEXT,
                    method TEXT,
                    condition TEXT,
                    requirement TEXT,
                    is_sample_row BOOLEAN NOT NULL,
                    PRIMARY KEY (draft_row_id),
                    CONSTRAINT uq_project_matrix_draft_row_order
                        UNIQUE (project_matrix_draft_id, row_order),
                    CONSTRAINT uq_project_matrix_draft_row_source_lineage
                        UNIQUE (project_matrix_draft_id, source_row_snapshot_id),
                    FOREIGN KEY(project_matrix_draft_id)
                        REFERENCES project_matrix_draft_records(project_matrix_draft_id),
                    FOREIGN KEY(source_row_snapshot_id)
                        REFERENCES source_matrix_row_snapshots(row_snapshot_id)
                )
                """
            )
            connection.exec_driver_sql(
                """
                INSERT INTO project_matrix_draft_rows_new (
                    draft_row_id,
                    project_matrix_draft_id,
                    source_row_snapshot_id,
                    row_order,
                    test_item,
                    source_section,
                    method,
                    condition,
                    requirement,
                    is_sample_row
                )
                SELECT
                    draft_row_id,
                    project_matrix_draft_id,
                    source_row_snapshot_id,
                    row_order,
                    test_item,
                    source_section,
                    NULL,
                    NULL,
                    NULL,
                    is_sample_row
                FROM project_matrix_draft_rows
                """
            )
            connection.exec_driver_sql("DROP TABLE project_matrix_draft_rows")
            connection.exec_driver_sql(
                "ALTER TABLE project_matrix_draft_rows_new RENAME TO project_matrix_draft_rows"
            )
            connection.exec_driver_sql(
                "CREATE INDEX ix_project_matrix_draft_rows_project_matrix_draft_id "
                "ON project_matrix_draft_rows(project_matrix_draft_id)"
            )
        finally:
            connection.exec_driver_sql("PRAGMA foreign_keys=ON")


def _migrate_project_matrix_draft_row_detail_columns(engine: Engine) -> None:
    """Add optional row detail columns for method/condition/requirement when missing."""
    if engine.dialect.name != "sqlite":
        return
    with engine.begin() as connection:
        table_names = {
            row[0]
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        if "project_matrix_draft_rows" not in table_names:
            return
        columns = {
            row[1]
            for row in connection.exec_driver_sql(
                "PRAGMA table_info(project_matrix_draft_rows)"
            ).all()
        }
        for missing_column in ["method", "condition", "requirement"]:
            if missing_column in columns:
                continue
            connection.exec_driver_sql(
                f"ALTER TABLE project_matrix_draft_rows ADD COLUMN {missing_column} TEXT"
            )
