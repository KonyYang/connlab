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

    Base.metadata.create_all(bind=engine)
    _migrate_project_no_optional(engine)


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
