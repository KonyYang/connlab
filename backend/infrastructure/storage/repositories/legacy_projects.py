"""Persistence and serialized check/write boundary for historical registrations."""
from contextlib import contextmanager
import json

from sqlalchemy import select

from backend.infrastructure.storage.models_legacy_projects import LegacyProjectRecordModel
from backend.infrastructure.storage.models import (
    ProjectModel, LtrRecordModel, ProjectFolderRecordModel,
    ProjectOfficialWorkspaceRecordModel, ProjectPublicFolderWorkflowOperationModel,
)


class LegacyProjectRepository:
    def __init__(self, session):
        self.session = session

    @contextmanager
    def write(self):
        # SQLite's reserved write lock must precede ownership reads, including on
        # two connections. No business Project rows are written by this repository.
        self.session.connection().exec_driver_sql("BEGIN IMMEDIATE")
        try:
            yield
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def records(self):
        return [self._view(row) for row in self.session.scalars(select(LegacyProjectRecordModel))]

    def get(self, record_id):
        row = self.session.get(LegacyProjectRecordModel, record_id)
        return self._view(row) if row else None

    def references(self):
        refs = {row.project_id: {"id": row.project_id, "kind": "project", "numbers": [], "paths": [],
                               "source_id": row.project_id, "revision": row.registry_revision}
                for row in self.session.scalars(select(ProjectModel))}
        for row in self.session.scalars(select(ProjectModel)):
            if row.project_no:
                refs[row.project_id]["numbers"].append(row.project_no.upper())
        for row in self.session.scalars(select(LtrRecordModel)):
            if row.project_id in refs:
                refs[row.project_id]["numbers"].append(row.ltr_number.upper())
        for model, columns in (
            (ProjectFolderRecordModel, ("folder_path",)),
            (ProjectOfficialWorkspaceRecordModel, ("local_workspace_path", "official_folder_path")),
            (ProjectPublicFolderWorkflowOperationModel, ("local_official_folder_path",)),
        ):
            for row in self.session.scalars(select(model)):
                if row.project_id in refs:
                    refs[row.project_id]["paths"].extend(getattr(row, key) for key in columns if getattr(row, key))
        return list(refs.values()) + [
            {"id": row["record_id"], "kind": "legacy", "numbers": row["number_evidence"],
             "paths": [row["folder_path"]], "source_id": row["source_id"], "revision": row["revision"]}
            for row in self.records()]

    def add(self, record):
        row = LegacyProjectRecordModel(
            record_id=record["record_id"], name=record["name"], number=record["number"],
            evidence_json=json.dumps(record["number_evidence"]), source_id=record["source_id"],
            folder_path=record["folder_path"], normalized_path=record["normalized_path"],
            notes_json=json.dumps(record["notes"]), imported_at=record["imported_at"],
            updated_at=record["updated_at"], revision=1)
        self.session.add(row)
        self.session.flush()
        return self._view(row)

    def relocate(self, record_id, path, normalized, now):
        row = self.session.get(LegacyProjectRecordModel, record_id)
        row.folder_path, row.normalized_path = path, normalized
        row.revision += 1
        row.updated_at = now
        self.session.flush()
        return self._view(row)

    @staticmethod
    def _view(row):
        return {"record_id": row.record_id, "name": row.name, "number": row.number,
                "number_evidence": json.loads(row.evidence_json), "source_id": row.source_id,
                "folder_path": row.folder_path, "normalized_path": row.normalized_path,
                "notes": json.loads(row.notes_json), "revision": row.revision,
                "imported_at": row.imported_at, "updated_at": row.updated_at}
