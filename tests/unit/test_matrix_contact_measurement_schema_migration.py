from sqlalchemy import create_engine

from backend.infrastructure.storage.matrix_contact_measurement_schema_migration import (
    migrate_matrix_contact_measurement_columns,
)


def test_contact_measurement_migration_adds_payload_columns_to_legacy_tables() -> None:
    engine = create_engine("sqlite:///:memory:")
    try:
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "CREATE TABLE project_matrix_draft_step_quantities (draft_step_quantity_id TEXT)"
            )
            connection.exec_driver_sql(
                "CREATE TABLE confirmed_matrix_step_quantities (confirmed_step_quantity_id TEXT)"
            )

        migrate_matrix_contact_measurement_columns(engine)

        with engine.connect() as connection:
            draft_columns = {
                row[1]
                for row in connection.exec_driver_sql(
                    "PRAGMA table_info(project_matrix_draft_step_quantities)"
                )
            }
            confirmed_columns = {
                row[1]
                for row in connection.exec_driver_sql(
                    "PRAGMA table_info(confirmed_matrix_step_quantities)"
                )
            }
        assert "contact_plan_json" in draft_columns
        assert "contact_plan_json" in confirmed_columns
    finally:
        engine.dispose()
