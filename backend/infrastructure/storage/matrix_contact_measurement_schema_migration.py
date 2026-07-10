"""Non-destructive SQLite migration for Matrix Step contact plan metadata."""

from __future__ import annotations

from sqlalchemy.engine import Engine


def migrate_matrix_contact_measurement_columns(engine: Engine) -> None:
    """Add structured contact plan payload columns to existing authority tables."""
    if engine.dialect.name != "sqlite":
        return
    with engine.begin() as connection:
        table_names = {
            row[0]
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        for table_name in (
            "project_matrix_draft_step_quantities",
            "confirmed_matrix_step_quantities",
        ):
            if table_name not in table_names:
                continue
            columns = {
                row[1]
                for row in connection.exec_driver_sql(f"PRAGMA table_info({table_name})").all()
            }
            if "contact_plan_json" not in columns:
                connection.exec_driver_sql(
                    f"ALTER TABLE {table_name} ADD COLUMN contact_plan_json TEXT"
                )
