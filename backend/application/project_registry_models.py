"""Read contracts for recoverable project record management."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProjectRegistryEntry:
    project_id: str
    display_project_id: str
    sample_description: str | None
    test_item: str | None
    requestor: str
    created_on: str | None
    lifecycle_state: str
    close_reason_label: str | None
    registry_state: str
    registry_revision: int
    changed_at: str | None
    reason: str | None


@dataclass(frozen=True, slots=True)
class ProjectRegistryPreview:
    project: ProjectRegistryEntry
    action: str
    token: str
    conflicts: tuple[ProjectRegistryEntry, ...]
    blockers: tuple[str, ...]
    retained_data: tuple[str, ...]
    warnings: tuple[str, ...]


class ProjectRegistryConflict(ValueError):
    """State or preview no longer permits the requested management operation."""

    def __init__(self, message: str, code: str = "project_registry_conflict"):
        super().__init__(message)
        self.code = code


class ProjectRegistryNotFound(LookupError):
    pass
