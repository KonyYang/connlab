"""Allow template-free workspace records without replacing existing associations."""

from sqlalchemy.engine import Engine


def migrate_project_folder_schema(engine: Engine) -> None:
    if engine.dialect.name != "sqlite":
        return
    with engine.begin() as connection:
        # sqlite3 legacy mode does not begin a transaction for DDL. Start it before
        # ALTER/CREATE so an interrupted rebuild restores the original table.
        if not connection.connection.driver_connection.in_transaction:
            connection.exec_driver_sql("BEGIN IMMEDIATE")
        rows = connection.exec_driver_sql("PRAGMA table_info(project_official_workspace_records)").all()
        if rows:
            columns = {row[1]: row for row in rows}
            if "creation_kind" not in columns:
                connection.exec_driver_sql("ALTER TABLE project_official_workspace_records ADD COLUMN creation_kind VARCHAR(32) NOT NULL DEFAULT 'template'")
            if columns["template_source_path"][3]:
                # Preserve column order, keys and indexes while removing only this NOT NULL.
                sql = connection.exec_driver_sql("SELECT sql FROM sqlite_master WHERE type='table' AND name='project_official_workspace_records'").scalar_one()
                import re
                new_sql = re.sub(r"(template_source_path\s+VARCHAR\(1024\))\s+NOT NULL", r"\1", sql, flags=re.I)
                if new_sql == sql:
                    raise ValueError("Workspace schema has an unsupported template-origin constraint; migration stopped.")
                indexes = connection.exec_driver_sql("SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='project_official_workspace_records' AND sql IS NOT NULL").scalars().all()
                connection.exec_driver_sql(new_sql.replace("project_official_workspace_records", "_workspace_phase1_migration", 1))
                connection.exec_driver_sql("INSERT INTO _workspace_phase1_migration SELECT * FROM project_official_workspace_records")
                connection.exec_driver_sql("DROP TABLE project_official_workspace_records")
                connection.exec_driver_sql("ALTER TABLE _workspace_phase1_migration RENAME TO project_official_workspace_records")
                for statement in indexes:
                    connection.exec_driver_sql(statement)
        state_columns = {row[1] for row in connection.exec_driver_sql("PRAGMA table_info(project_public_folder_workflow_states)").all()}
        if state_columns and "binding_json" not in state_columns:
            connection.exec_driver_sql("ALTER TABLE project_public_folder_workflow_states ADD COLUMN binding_json TEXT")
