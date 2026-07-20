"""Additive SQLite compatibility for Standard sheet and Matrix sync metadata."""

from __future__ import annotations


class StandardRecordMethodSyncSchemaError(RuntimeError):
    """Raised when the additive schema cannot be verified safely."""


_COLUMNS = {
    "external_resources": ("worksheet_name", "VARCHAR(31)"),
    "project_matrix_draft_records": ("method_sync_context_json", "TEXT"),
}


def migrate_standard_record_method_sync_schema(engine) -> None:
    """Add missing nullable columns and verify their complete SQLite shape."""
    if engine.dialect.name != "sqlite":
        return
    with engine.connect() as connection:
        try:
            connection.exec_driver_sql("BEGIN IMMEDIATE")
            tables = {
                str(row[0])
                for row in connection.exec_driver_sql(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).all()
            }
            for table, (column, declared_type) in _COLUMNS.items():
                if table not in tables:
                    raise StandardRecordMethodSyncSchemaError(
                        f"authority_corrupt: missing table {table}."
                    )
                existing = _column_shape(connection, table, column)
                if existing is not None and existing != (declared_type, 0, None, 0):
                    raise StandardRecordMethodSyncSchemaError(
                        f"authority_corrupt: incompatible {table}.{column}."
                    )
            for table, (column, declared_type) in _COLUMNS.items():
                if _column_shape(connection, table, column) is None:
                    connection.exec_driver_sql(
                        f"ALTER TABLE {table} ADD COLUMN {column} {declared_type}"
                    )
            for table, (column, declared_type) in _COLUMNS.items():
                if _column_shape(connection, table, column) != (
                    declared_type,
                    0,
                    None,
                    0,
                ):
                    raise StandardRecordMethodSyncSchemaError(
                        f"authority_corrupt: failed to verify {table}.{column}."
                    )
            connection.commit()
        except StandardRecordMethodSyncSchemaError:
            connection.rollback()
            raise
        except Exception as exc:
            connection.rollback()
            raise StandardRecordMethodSyncSchemaError(
                "authority_corrupt: Standard record method sync migration failed."
            ) from exc


def _column_shape(connection, table: str, column: str):
    for row in connection.exec_driver_sql(f"PRAGMA table_info({table})").all():
        if str(row[1]) == column:
            return (str(row[2]).upper(), int(row[3]), row[4], int(row[5]))
    return None
