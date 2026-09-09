"""Real local journal locks protect registry moves and background dispatch."""

from sqlalchemy import create_engine
import pytest

from backend.application.project_registry_management_service import ProjectRegistryManagementService, ProjectRegistryConflict
from backend.application.project_folder_generation_service import ProjectFolderGenerationService
from backend.application.project_lifecycle_write_guard import ProjectLifecycleWriteGuard, LifecycleWriteOperation
from backend.domain import Project
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.storage.database import init_db, create_session_factory
from backend.infrastructure.storage.repositories.project import ProjectRepository
from backend.infrastructure.storage.repositories.project_registry import ProjectRegistryRepository
from backend.infrastructure.storage.repositories import LtrRecordRepository


@pytest.fixture
def setup(tmp_path):
    engine = create_engine("sqlite:///:memory:")
    init_db(engine)
    with create_session_factory(engine)() as session:
        projects = ProjectRepository(session)
        projects.create(Project(project_id="p1", project_no=None, product_name="Fixture", requestor="User"))
        session.commit()
        journal = GenerationJournal(tmp_path / "journal")
        service = ProjectRegistryManagementService(ProjectRegistryRepository(session), LtrRecordRepository(session), journal)
        yield session, projects, journal, service
    engine.dispose()


@pytest.mark.parametrize("state", ["queued", "running"])
def test_dispatched_generation_blocks_trash_without_changing_project(setup, state):
    _, projects, journal, service = setup
    preview = service.preview("p1", "trash")
    operation = journal.create("p1", None, "test-context")
    operation["status"] = state
    journal.save(operation)
    assert service.preview("p1", "trash").blockers
    with pytest.raises(ProjectRegistryConflict, match="queued or running"):
        service.trash("p1", token=preview.token, reason="Mistake")
    assert projects.get("p1").registry_state == "active"


def test_inflight_write_lock_blocks_registry_transition(setup):
    _, projects, journal, service = setup
    token = service.preview("p1", "trash").token
    with journal.lock("p1"):
        with pytest.raises(ProjectRegistryConflict, match="already running"):
            service.trash("p1", token=token, reason="Mistake")
    assert projects.get("p1").registry_state == "active"


def test_worker_cannot_write_after_project_is_hidden(setup):
    _, projects, journal, service = setup
    service.trash("p1", token=service.preview("p1", "trash").token, reason="Mistake")
    state = journal.create("p1", None, "test-context")
    writes = []
    def context(project_id):
        ProjectLifecycleWriteGuard(projects).require_write_allowed(project_id, LifecycleWriteOperation.REQUIRED_FORMS_GENERATE)
        return "test-context"
    generation = ProjectFolderGenerationService(journal, context, lambda *args: writes.append(args), lambda action: action())
    generation.run("p1", state["operation_id"])
    assert writes == []
    assert journal.read("p1")["status"] == "blocked"


def test_registry_commit_is_durable_before_generation_lock_is_released(setup):
    session, projects, journal, _ = setup
    class CheckingRepository(ProjectRegistryRepository):
        def commit(self):
            with pytest.raises(ValueError, match="already running"):
                with journal.lock("p1"):
                    pass
            super().commit()
    service = ProjectRegistryManagementService(CheckingRepository(session), LtrRecordRepository(session), journal)
    service.trash("p1", token=service.preview("p1", "trash").token, reason="Mistake")
    assert projects.get("p1").registry_state == "trash"
    with journal.lock("p1"):
        pass
