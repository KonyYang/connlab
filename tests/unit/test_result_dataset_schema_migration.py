from sqlalchemy import inspect

from backend.infrastructure.storage.database import (
    create_database_engine,
    init_db,
)
from backend.shared.config import Settings


def test_init_db_bootstraps_result_dataset_and_report_revision_tables(tmp_path) -> None:
    engine = create_database_engine(
        Settings(data_dir=tmp_path, projects_dir=tmp_path, templates_dir=tmp_path, database_path=tmp_path / "db.sqlite3")
    )

    init_db(engine)

    table_names = set(inspect(engine).get_table_names())
    assert "result_dataset_revisions" in table_names
    assert "report_draft_revisions" in table_names
