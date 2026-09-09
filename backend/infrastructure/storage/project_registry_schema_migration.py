"""Add recoverable project locations without modifying lifecycle or owned data."""

from sqlalchemy import inspect, text


def migrate_project_registry_schema(engine) -> None:
    """Idempotently extend existing projects; reject invalid retained state."""
    inspector = inspect(engine)
    if not inspector.has_table("projects"):
        return
    columns = {column["name"] for column in inspector.get_columns("projects")}
    additions = {
        "registry_state": "VARCHAR(16) NOT NULL DEFAULT 'active' CHECK (registry_state IN ('active','trash','history'))",
        "registry_revision": "INTEGER NOT NULL DEFAULT 0 CHECK (registry_revision >= 0)",
        "registry_changed_at": "VARCHAR(64)",
        "registry_reason": "TEXT",
    }
    with engine.begin() as connection:
        for name, declaration in additions.items():
            if name not in columns:
                connection.exec_driver_sql(f"ALTER TABLE projects ADD COLUMN {name} {declaration}")
        invalid = connection.execute(text(
            "SELECT project_id FROM projects WHERE registry_state IS NULL OR registry_state NOT IN "
            "('active','trash','history') OR registry_revision IS NULL OR registry_revision < 0 LIMIT 1"
        )).first()
        if invalid:
            raise RuntimeError("Project registry state is incompatible; restore a verified database backup before continuing.")
