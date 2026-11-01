"""Add optional notes without changing existing Matrix completion evidence."""
from sqlalchemy.engine import Engine


def migrate_group_completion_description(engine: Engine) -> None:
    if engine.dialect.name != "sqlite":
        return
    with engine.begin() as connection:
        columns = {row[1] for row in connection.exec_driver_sql("PRAGMA table_info(group_completion_events)")}
        if columns and "description" not in columns:
            connection.exec_driver_sql("ALTER TABLE group_completion_events ADD COLUMN description TEXT")
