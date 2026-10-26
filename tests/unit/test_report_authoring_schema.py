"""Additive report preparation storage must not alter existing project/result authority."""
from sqlalchemy import inspect, text
from backend.infrastructure.storage.database import create_database_engine, create_session_factory, init_db
from backend.infrastructure.storage.models_report_authoring import ReportAuthoringRevisionModel
from backend.infrastructure.storage.repositories.report_authoring import ReportAuthoringRepository
from backend.domain.report_authoring import ReportAuthoringState, ReportAuthoringConflict
from backend.shared.config import Settings
from tests.unit.test_confirmed_matrix_authority_repository import _seed_project
import pytest


def test_additive_bootstrap_preserves_existing_project_and_reopens_revisions(tmp_path):
    settings = Settings(database_path=tmp_path/'old.sqlite3', data_dir=tmp_path/'data', projects_dir=tmp_path/'projects', templates_dir=tmp_path/'templates')
    engine = create_database_engine(settings)
    init_db(engine)
    ReportAuthoringRevisionModel.__table__.drop(engine)
    factory = create_session_factory(engine)
    with factory() as session:
        _seed_project(session); session.commit()
    with engine.connect() as connection:
        before = connection.execute(text('SELECT * FROM projects')).all()
    init_db(engine)
    init_db(engine)
    assert 'report_authoring_revisions' in inspect(engine).get_table_names()
    with engine.connect() as connection:
        assert connection.execute(text('SELECT * FROM projects')).all() == before
    with factory() as session:
        saved = ReportAuthoringRepository(session).save(ReportAuthoringState('P1'), 0)
        session.commit()
        assert saved.revision == 1
    with factory() as session:
        repository = ReportAuthoringRepository(session)
        assert repository.get('P1').revision == 1
        with pytest.raises(ReportAuthoringConflict):
            repository.save(ReportAuthoringState('P1'), 0)
    engine.dispose()
