from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

from backend.infrastructure.storage.database import init_db
from backend.infrastructure.storage.models import ProjectModel
from backend.infrastructure.storage.models_legacy_projects import LegacyProjectRecordModel


def test_additive_bootstrap_is_idempotent_and_preserves_existing_rows(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'old.db'}")
    init_db(engine)
    with Session(engine) as session:
        session.add(ProjectModel(project_id="existing", project_no="DL-2021-01-001", product_name="Original", requestor="User", status="DRAFT"))
        session.commit()
    LegacyProjectRecordModel.__table__.drop(engine)
    with engine.connect() as connection:
        before = dict(connection.execute(text("select * from projects where project_id='existing'")).mappings().one())
    init_db(engine)
    init_db(engine)
    assert "legacy_project_records" in inspect(engine).get_table_names()
    with engine.connect() as connection:
        assert dict(connection.execute(text("select * from projects where project_id='existing'")).mappings().one()) == before
    engine.dispose()
