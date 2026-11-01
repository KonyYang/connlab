"""Startup upgrades retain existing completion evidence and tolerate repeat runs."""
from sqlalchemy import create_engine

from backend.infrastructure.storage.database import init_db


def test_startup_adds_nullable_description_without_rewriting_completion(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'old.sqlite3'}")
    try:
        with engine.begin() as connection:
            connection.exec_driver_sql("""CREATE TABLE group_completion_events (
                event_id VARCHAR(64) PRIMARY KEY, project_id VARCHAR(64) NOT NULL,
                group_lineage VARCHAR(64) NOT NULL, group_key VARCHAR(255) NOT NULL,
                matrix_revision INTEGER NOT NULL, signature VARCHAR(64) NOT NULL,
                completed BOOLEAN NOT NULL, completed_at VARCHAR(64), recorded_at VARCHAR(64) NOT NULL)""")
            connection.exec_driver_sql("INSERT INTO group_completion_events VALUES ('e1','p1','l1','g1',3,'signature',1,'completed','recorded')")
        init_db(engine)
        with engine.begin() as connection:
            row = connection.exec_driver_sql("SELECT * FROM group_completion_events").mappings().one()
            assert row["description"] is None
            assert (row["signature"], row["completed_at"], row["recorded_at"], row["matrix_revision"]) == ("signature", "completed", "recorded", 3)
            connection.exec_driver_sql("UPDATE group_completion_events SET description='复核说明'")
        init_db(engine)
        with engine.connect() as connection:
            assert connection.exec_driver_sql("SELECT description FROM group_completion_events").scalar_one() == "复核说明"
    finally:
        engine.dispose()
