from backend.application.project_service import (
    CreateProjectCommand,
    CreateTemporaryProjectCommand,
    ProjectNotFoundError,
    ProjectService,
)
from backend.domain import Project, ProjectStatus, ProjectTemporaryContext


class FakeProjectRepository:
    """In-memory project repository for service tests."""

    def __init__(self) -> None:
        """Create an empty repository."""
        self.projects: dict[str, Project] = {}

    def create(self, project: Project) -> Project:
        """Store a project in memory."""
        self.projects[project.project_id] = project
        return project

    def get(self, project_id: str) -> Project | None:
        """Return a project by ID."""
        return self.projects.get(project_id)

    def list(self) -> list[Project]:
        """Return all projects."""
        return list(self.projects.values())


class FakeTemporaryContextRepository:
    """In-memory temporary context repository for service tests."""

    def __init__(self) -> None:
        """Create an empty repository."""
        self.contexts: dict[str, ProjectTemporaryContext] = {}

    def create(self, context: ProjectTemporaryContext) -> ProjectTemporaryContext:
        """Store temporary context in memory."""
        self.contexts[context.project_id] = context
        return context


def test_project_service_creates_draft_project() -> None:
    repository = FakeProjectRepository()
    service = ProjectService(repository)

    project = service.create_project(
        CreateProjectCommand(
            project_no="PRJ-001",
            product_name="Connector",
            requestor="Alice",
            business_unit="BU-1",
        )
    )

    assert project.project_id
    assert project.status is ProjectStatus.DRAFT
    assert project.created_on is not None
    assert service.get_project(project.project_id) == project


def test_project_service_treats_blank_project_no_as_optional() -> None:
    repository = FakeProjectRepository()
    service = ProjectService(repository)

    project = service.create_project(
        CreateProjectCommand(
            project_no=" ",
            product_name="Connector",
            requestor="Alice",
        )
    )

    assert project.project_no is None


def test_project_service_creates_active_temporary_planning_project_without_ltr() -> None:
    repository = FakeProjectRepository()
    context_repository = FakeTemporaryContextRepository()
    service = ProjectService(repository, context_repository)

    project = service.create_temporary_project(
        CreateTemporaryProjectCommand(
            request_summary="Feasibility discussion",
            sample_description="Connector samples for planning",
            test_item="Durability estimate",
            requestor="Alice",
            source_asset_ids=("A1",),
            notes="Created from request email",
        )
    )

    assert project.project_id
    assert project.project_no is None
    assert project.product_name == "Connector samples for planning"
    assert project.requestor == "Alice"
    assert project.status is ProjectStatus.DRAFT
    assert service.get_project(project.project_id) == project
    context = context_repository.contexts[project.project_id]
    assert context.sample_description == "Connector samples for planning"
    assert context.test_item == "Durability estimate"
    assert context.source_asset_ids == ("A1",)
    assert context.notes == "Created from request email"


def test_project_service_raises_for_missing_project() -> None:
    service = ProjectService(FakeProjectRepository())

    try:
        service.get_project("missing")
    except ProjectNotFoundError as exc:
        assert "missing" in str(exc)
    else:
        raise AssertionError("Expected ProjectNotFoundError")
