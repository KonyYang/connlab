"""SQLite ensure-column migration for Matrix schedule planning fields."""

from __future__ import annotations

from typing import Any

from sqlalchemy.engine import Engine


def migrate_matrix_schedule_planning_columns(engine: Engine) -> None:
    """Add nullable Matrix planning columns to existing local SQLite databases."""
    if engine.dialect.name != "sqlite":
        return
    with engine.begin() as connection:
        table_names = {
            row[0]
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        _ensure_columns(
            connection,
            table_names=table_names,
            table="project_matrix_draft_records",
            columns={
                "pre_test_buffer_days": "VARCHAR(64)",
                "post_test_buffer_days": "VARCHAR(64)",
                "sample_received_date": "VARCHAR(32)",
                "planned_test_start_date": "VARCHAR(32)",
                "planned_test_complete_date": "VARCHAR(32)",
                "estimated_completion_date": "VARCHAR(32)",
            },
        )
        _ensure_columns(
            connection,
            table_names=table_names,
            table="project_matrix_draft_rows",
            columns={"day_expression": "VARCHAR(64)"},
        )
        _ensure_columns(
            connection,
            table_names=table_names,
            table="confirmed_matrix_versions",
            columns={
                "pre_test_buffer_days": "VARCHAR(64)",
                "post_test_buffer_days": "VARCHAR(64)",
                "sample_received_date": "VARCHAR(32)",
                "planned_test_start_date": "VARCHAR(32)",
                "planned_test_complete_date": "VARCHAR(32)",
                "estimated_completion_date": "VARCHAR(32)",
            },
        )
        _ensure_columns(
            connection,
            table_names=table_names,
            table="confirmed_matrix_rows",
            columns={"day_expression": "VARCHAR(64)"},
        )


def _ensure_columns(
    connection: Any,
    *,
    table_names: set[str],
    table: str,
    columns: dict[str, str],
) -> None:
    """Add missing nullable columns to a SQLite table."""
    if table not in table_names:
        return
    existing = {
        row[1]
        for row in connection.exec_driver_sql(f"PRAGMA table_info({table})").all()
    }
    for column_name, column_type in columns.items():
        if column_name in existing:
            continue
        connection.exec_driver_sql(
            f"ALTER TABLE {table} ADD COLUMN {column_name} {column_type}"
        )
