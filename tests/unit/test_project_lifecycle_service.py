from __future__ import annotations

import pytest

from backend.application.project_lifecycle_service import (
    LifecycleOperation,
    ProjectLifecycleError,
    ProjectLifecycleService,
)
from backend.domain import Project, ProjectStatus


def test_lifecycle_allows_ltr_after_project_data_is_confirmed() -> None:
    service = ProjectLifecycleService(_ProjectRepo(ProjectStatus.CONFIRMED))

    result = service.check_allowed("P1", LifecycleOperation.LTR_PREVIEW)

    assert result.allowed is True
    assert result.reason is None


def test_lifecycle_blocks_ltr_before_confirmed_data() -> None:
    service = ProjectLifecycleService(_ProjectRepo(ProjectStatus.DRAFT))

    with pytest.raises(ProjectLifecycleError, match="confirmed project data"):
        service.require_allowed("P1", LifecycleOperation.LTR_COMMIT)


def test_lifecycle_blocks_folder_before_ltr_registration() -> None:
    service = ProjectLifecycleService(_ProjectRepo(ProjectStatus.CONFIRMED))

    with pytest.raises(ProjectLifecycleError, match="registered LTR"):
        service.require_allowed("P1", LifecycleOperation.FOLDER_GENERATE)


def test_lifecycle_allows_folder_after_ltr_registration() -> None:
    service = ProjectLifecycleService(_ProjectRepo(ProjectStatus.LTR_REGISTERED))

    service.require_allowed("P1", LifecycleOperation.FOLDER_GENERATE)


def test_lifecycle_blocks_evidence_execution_before_folder_creation() -> None:
    service = ProjectLifecycleService(_ProjectRepo(ProjectStatus.LTR_REGISTERED))

    with pytest.raises(ProjectLifecycleError, match="generated project folder"):
        service.require_allowed("P1", LifecycleOperation.EVIDENCE_PLACE)


def test_lifecycle_blocks_mutation_on_closed_project() -> None:
    service = ProjectLifecycleService(_ProjectRepo(ProjectStatus.CLOSED))

    with pytest.raises(ProjectLifecycleError, match="closed"):
        service.require_allowed("P1", LifecycleOperation.LTR_PREVIEW)


class _ProjectRepo:
    """In-memory project repository for lifecycle tests."""

    def __init__(self, status: ProjectStatus) -> None:
        """Create a repository with one fixed project status."""
        self._status = status

    def get(self, project_id: str) -> Project | None:
        """Return a project with the configured status."""
        return Project(
            project_id=project_id,
            project_no="PRJ-1",
            product_name="Connector",
            requestor="Alice",
            status=self._status,
        )
