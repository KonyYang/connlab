from dataclasses import replace
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.domain.project_schedule_models import ProjectScheduleRevision
from backend.infrastructure.storage.database import init_db
from backend.infrastructure.storage.models import ProjectModel
from backend.infrastructure.storage.repositories.project_schedule import ProjectScheduleRepository


def test_repository_round_trips_active_and_historical_schedule_revisions() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    init_db(engine)
    with Session(engine) as session:
        session.add(ProjectModel(project_id="P1", project_no="DL-1", product_name="Product", requestor="User", status="registered"))
        session.flush()
        repository = ProjectScheduleRepository(session)
        first = _revision("S1", 1, state="superseded")
        second = _revision("S2", 2, state="confirmed")
        repository.add(first)
        repository.add(second)
        repository.flush()

        assert repository.highest_revision_sequence("P1") == 2
        assert repository.active_revision("P1") == second


def test_repository_supersedes_active_revision() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    init_db(engine)
    with Session(engine) as session:
        session.add(ProjectModel(project_id="P1", project_no="DL-1", product_name="Product", requestor="User", status="registered"))
        session.flush()
        repository = ProjectScheduleRepository(session)
        repository.add(_revision("S1", 1, state="confirmed"))
        repository.flush()

        repository.supersede_active("P1", at="2026-09-02T00:00:00Z")
        repository.flush()

        assert repository.active_revision("P1") is None


def test_repository_round_trips_schedule_without_optional_lineage():
    engine = create_engine("sqlite:///:memory:", future=True)
    init_db(engine)
    with Session(engine) as session:
        session.add(ProjectModel(project_id="P1", project_no="DL-1", product_name="Product", requestor="User", status="registered"))
        session.flush()
        revision = replace(_revision("S1", 1, state="confirmed"), based_on_confirmed_matrix_id=None,
            based_on_confirmed_matrix_revision=None, based_on_basic_information_version=None, sample_received_date="")
        repository = ProjectScheduleRepository(session)
        repository.add(revision)
        repository.flush()
        session.expire_all()
        assert repository.active_revision("P1") == revision


def _revision(revision_id: str, sequence: int, *, state: str) -> ProjectScheduleRevision:
    return ProjectScheduleRevision(
        revision_id=revision_id,
        project_id="P1",
        revision_sequence=sequence,
        state=state,
        fingerprint=f"fp-{sequence}",
        matrix_input_fingerprint="matrix-input",
        based_on_confirmed_matrix_id="M1",
        based_on_confirmed_matrix_revision=1,
        based_on_basic_information_version=2,
        sample_received_date="2026-09-01",
        post_test_buffer_days="2",
        test_start_date="2026-09-02",
        test_complete_date="2026-09-05",
        estimated_completion_date="2026-09-07",
        confirmed_by="Lab User",
        confirmed_at="2026-09-01T00:00:00Z",
    )
