"""Resolve first-use business output locations without changing configured choices."""
from pathlib import Path
from uuid import uuid4
from backend.domain import ExternalResource, ExternalResourceType

PURPOSES = {ExternalResourceType.PROJECT_OUTPUT_ROOT: "Projects",
            ExternalResourceType.TEMPORARY_MATERIALS_ROOT: "TemporaryMaterials"}

class DefaultStorageLocations:
    def __init__(self, settings, resources, directories):
        self.settings, self.resources, self.directories = settings, resources, directories

    def effective(self, kind) -> Path:
        value = self.resources.get_by_type(kind)
        if value is not None:
            return value.path
        return self.settings.projects_dir if kind == ExternalResourceType.PROJECT_OUTPUT_ROOT else self.settings.output_path(PURPOSES[kind])

    def ensure(self, kind) -> Path:
        configured = self.resources.get_by_type(kind)
        if configured is not None:
            if not configured.active:
                raise ValueError("The folder is disabled. Choose an available location in Settings.")
            return self.directories.existing(configured.path)
        root = self.effective(kind)
        if kind == ExternalResourceType.PROJECT_OUTPUT_ROOT and self.settings.projects_directory_explicit:
            self.directories.existing(root)
        else:
            self.directories.create(root)
        # A concurrent explicit Settings save wins over this first-use default.
        configured = self.resources.get_by_type(kind)
        if configured is None:
            proposed = ExternalResource(resource_id=uuid4().hex, resource_type=kind, path=root, active=True)
            configured = self.resources.create_default_if_absent(proposed)
        if not configured.active:
            raise ValueError("The folder is disabled. Choose an available location in Settings.")
        return self.directories.existing(configured.path)
