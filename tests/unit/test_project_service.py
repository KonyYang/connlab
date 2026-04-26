from backend.application.project_service import (
    CreateProjectCommand,
    ProjectNotFoundError,
    ProjectService,
)
from backend.domain import Project, ProjectStatus


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


def test_project_service_raises_for_missing_project() -> None:
    service = ProjectService(FakeProjectRepository())

    try:
        service.get_project("missing")
    except ProjectNotFoundError as exc:
        assert "missing" in str(exc)
    else:
        raise AssertionError("Expected ProjectNotFoundError")
