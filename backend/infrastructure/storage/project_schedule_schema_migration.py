"""Fail-closed additive bootstrap for independent Project Schedule authority."""

from __future__ import annotations

import re

from sqlalchemy.schema import CreateIndex, CreateTable

_COLUMNS = {
    "revision_id": ("VARCHAR(64)", 1, 1),
    "project_id": ("VARCHAR(64)", 1, 0),
    "revision_sequence": ("INTEGER", 1, 0),
    "state": ("VARCHAR(32)", 1, 0),
    "fingerprint": ("VARCHAR(128)", 1, 0),
    "matrix_input_fingerprint": ("VARCHAR(128)", 1, 0),
    "based_on_confirmed_matrix_id": ("VARCHAR(64)", 0, 0),
    "based_on_confirmed_matrix_revision": ("INTEGER", 0, 0),
    "based_on_basic_information_version": ("INTEGER", 0, 0),
    "sample_received_date": ("VARCHAR(32)", 1, 0),
    "post_test_buffer_days": ("VARCHAR(64)", 1, 0),
    "test_start_date": ("VARCHAR(32)", 1, 0),
    "test_complete_date": ("VARCHAR(32)", 1, 0),
    "estimated_completion_date": ("VARCHAR(32)", 1, 0),
    "confirmed_by": ("VARCHAR(255)", 1, 0),
    "confirmed_at": ("VARCHAR(64)", 1, 0),
    "superseded_at": ("VARCHAR(64)", 0, 0),
    "superseded_reason": ("TEXT", 0, 0),
}
_LINEAGE_COLUMNS = (
    "based_on_confirmed_matrix_id",
    "based_on_confirmed_matrix_revision",
    "based_on_basic_information_version",
)
_TABLE_NAME = "project_schedule_revisions"
_MIGRATION_TABLE_NAME = "project_schedule_revisions_nullable_lineage"


def bootstrap_project_schedule_schema(engine) -> None:
    """Create or migrate the recognized schedule schema, rejecting unknown variants."""
    if engine.dialect.name != "sqlite":
        return
    # Register FK targets before compiling the dedicated table DDL.
    from backend.infrastructure.storage import models  # noqa: F401
    from backend.infrastructure.storage import models_confirmed_matrix_authority  # noqa: F401
    from backend.infrastructure.storage.models_project_schedule import (
        ProjectScheduleRevisionModel,
    )

    table = ProjectScheduleRevisionModel.__table__
    with engine.connect() as connection:
        try:
            connection.exec_driver_sql("BEGIN IMMEDIATE")
            exists = connection.exec_driver_sql(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table.name,)
            ).scalar_one_or_none()
            if not exists:
                table.create(connection, checkfirst=False)
            elif _validate(connection, table) == "legacy":
                _migrate_nullable_lineage(connection, table)
            _validate(connection, table)
            connection.commit()
        except Exception as exc:
            connection.rollback()
            raise RuntimeError("authority_corrupt: Project Schedule bootstrap failed.") from exc


def _validate(connection, table) -> str:
    legacy_columns = dict(_COLUMNS)
    for name in _LINEAGE_COLUMNS:
        datatype, _, primary_key = legacy_columns[name]
        legacy_columns[name] = datatype, 1, primary_key
    columns = {
        str(row[1]): (str(row[2]).upper(), int(row[3]), int(row[5]))
        for row in connection.exec_driver_sql(
            "PRAGMA table_xinfo(project_schedule_revisions)"
        ).all()
    }
    if columns not in (_COLUMNS, legacy_columns):
        _corrupt()
    kind = "legacy" if columns == legacy_columns else "current"
    sql = connection.exec_driver_sql(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='project_schedule_revisions'"
    ).scalar_one_or_none() or ""
    expected = str(CreateTable(table).compile(dialect=connection.dialect))
    if kind == "legacy":
        for name in _LINEAGE_COLUMNS:
            declaration = f"{name} {_COLUMNS[name][0]}"
            expected = expected.replace(declaration + ",", declaration + " NOT NULL,")
    # Full known DDL protects defaults, checks, FK actions, uniqueness and hidden columns.
    if _compact_sql(sql) != _compact_sql(expected):
        _corrupt()
    indexes = {
        str(row[0]): str(row[1])
        for row in connection.exec_driver_sql(
            "SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name=? AND sql IS NOT NULL",
            (_TABLE_NAME,),
        ).all()
    }
    for index in table.indexes:
        expected_index = str(CreateIndex(index).compile(dialect=connection.dialect))
        if _compact_sql(indexes.get(index.name, "")) != _compact_sql(expected_index):
            _corrupt()
    return kind


def _migrate_nullable_lineage(connection, table) -> None:
    # Unknown dependents can make DROP destructive (including ON DELETE CASCADE).
    if connection.exec_driver_sql(
        "SELECT 1 FROM sqlite_master WHERE type='trigger' AND tbl_name=?", (_TABLE_NAME,)
    ).first():
        _corrupt()
    for name, in connection.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table'").all():
        foreign_keys = connection.exec_driver_sql(
            "SELECT * FROM pragma_foreign_key_list(?)", (name,)
        ).all()
        if any(str(row[2]).lower() == _TABLE_NAME for row in foreign_keys):
            _corrupt()
    indexes = connection.exec_driver_sql(
        "SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name=? AND sql IS NOT NULL", (_TABLE_NAME,)
    ).scalars().all()
    ddl = str(CreateTable(table).compile(dialect=connection.dialect))
    connection.exec_driver_sql(ddl.replace(f"CREATE TABLE {_TABLE_NAME}", f"CREATE TABLE {_MIGRATION_TABLE_NAME}", 1))
    columns = ", ".join(_COLUMNS)
    connection.exec_driver_sql(
        f"INSERT INTO {_MIGRATION_TABLE_NAME} ({columns}) SELECT {columns} FROM {_TABLE_NAME}"
    )
    connection.exec_driver_sql(f"DROP TABLE {_TABLE_NAME}")
    connection.exec_driver_sql(f"ALTER TABLE {_MIGRATION_TABLE_NAME} RENAME TO {_TABLE_NAME}")
    for index_sql in indexes:
        connection.exec_driver_sql(index_sql)


def _compact_sql(sql: str) -> str:
    # SQLite quotes the table identifier after RENAME; no identifier here needs quoting.
    return "".join(
        part if index % 2 else "".join(part.split()).replace('"', "")
        for index, part in enumerate(re.split(r"('(?:''|[^'])*')", sql))
    )


def _corrupt() -> None:
    raise RuntimeError("authority_corrupt: Project Schedule schema is incompatible.")
