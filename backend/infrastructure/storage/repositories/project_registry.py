"""Atomic registry transitions; business aggregates and external authorities stay intact."""

from contextlib import contextmanager
from uuid import uuid4

from sqlalchemy import select, func

from backend.application.project_registry_models import ProjectRegistryConflict
from backend.infrastructure.storage.models import ProjectModel, ProjectRegistryEventModel
from backend.infrastructure.storage.repositories.project import ProjectRepository
from backend.infrastructure.storage.database import Base


class ProjectRegistryRepository(ProjectRepository):
    def retained_inventory(self, project_id):
        """Count known associations without touching their files or authority."""
        tables = {
            "Confirmed Matrix versions": "confirmed_matrix_versions",
            "Schedule versions": "project_schedule_revisions",
            "Output records": "project_output_records",
            "LTR records": "ltr_records",
            "Project folders": "project_folder_records",
            "Official workspaces": "project_official_workspace_records",
            "Source file records": "file_assets",
        }
        return {label: self._session.scalar(select(func.count()).select_from(Base.metadata.tables[name]).where(
            Base.metadata.tables[name].c.project_id == project_id)) for label, name in tables.items()}

    @contextmanager
    def atomic(self):
        """Reserve SQLite's writer before inspecting a conflict set.

        Commit belongs to this complete registry operation, so OS generation locks
        can remain held until the state is durable. Callers must not stage unrelated writes.
        """
        if self._session.new or self._session.dirty or self._session.deleted:
            raise RuntimeError("Registry management requires a clean unit of work.")
        connection = self._session.connection()
        if not connection.connection.driver_connection.in_transaction:
            connection.exec_driver_sql("BEGIN IMMEDIATE")
        else:
            # Existing transaction may be a read transaction from a request guard.
            connection.exec_driver_sql("UPDATE projects SET registry_revision = registry_revision WHERE 0")
        self._session.expire_all()
        try:
            yield
        except BaseException:
            self._session.rollback()
            raise

    def commit(self):
        self._session.commit()

    def move(self, project_id, destination, *, expected_revision, reason, actor, changed_at, operation_id):
        if destination not in {"active", "trash", "history"}:
            raise ValueError("Unknown project registry location.")
        row = self._session.get(ProjectModel, project_id)
        if row is None or row.registry_revision != expected_revision:
            raise ProjectRegistryConflict("Project changed. Refresh the preview.", "project_registry_preview_stale")
        previous = row.registry_state
        row.registry_state = destination
        row.registry_revision += 1
        row.registry_changed_at = changed_at
        row.registry_reason = reason
        self._session.add(ProjectRegistryEventModel(
            event_id=uuid4().hex, operation_id=operation_id, project_id=project_id,
            previous_state=previous, new_state=destination, revision=row.registry_revision,
            reason=reason, actor=actor, changed_at=changed_at,
        ))
        self._session.flush()

    def list_events(self, project_id):
        return list(self._session.scalars(select(ProjectRegistryEventModel).where(
            ProjectRegistryEventModel.project_id == project_id
        ).order_by(ProjectRegistryEventModel.revision)))
