"""Persistence seam for library membership, never keyed by a display DL."""
from datetime import datetime, timezone, date
import json
from uuid import uuid4
from sqlalchemy import select, or_
from backend.domain.project_library import ProjectLibraryConflict
from backend.infrastructure.storage.models import ProjectModel, LtrRecordModel, ProjectOfficialWorkspaceRecordModel
from backend.infrastructure.storage.models_project_library import ProjectLibraryMemberModel, ProjectLibraryBatchModel


def now():
    return datetime.now(timezone.utc).isoformat()


class ProjectLibraryRepository:
    def __init__(self, session):
        self.session = session

    def members(self, query="", batch_id=None):
        stmt = select(ProjectLibraryMemberModel)
        if batch_id:
            stmt = stmt.where(ProjectLibraryMemberModel.batch_id == batch_id)
        rows = [self._view(row) for row in self.session.scalars(stmt)]
        q = query.strip().casefold()
        return sorted((row for row in rows if not q or q in " ".join(str(row.get(k) or "") for k in ("title", "ltr_number", "folder_path")).casefold()), key=lambda row: (row["created_at"], row["member_id"]), reverse=True)

    def member(self, member_id):
        row = self.session.get(ProjectLibraryMemberModel, member_id)
        if row is None:
            raise LookupError("Project library entry not found.")
        return self._view(row)

    def add_member(self, data):
        row = ProjectLibraryMemberModel(**data)
        self.session.add(row)
        self.session.commit()
        return self._view(row)

    def update_member(self, member_id, changes):
        row = self.session.get(ProjectLibraryMemberModel, member_id)
        if row is None:
            raise LookupError("Project library entry not found.")
        for key, value in changes.items():
            if key not in {"project_id", "ltr_number", "title", "folder_path", "snapshot_fingerprint"}:
                raise ValueError("Unsupported library entry update.")
            setattr(row, key, value)
        row.revision += 1
        self.session.commit()
        return self._view(row)

    def save_batch(self, batch):
        row = self.session.get(ProjectLibraryBatchModel, batch["batch_id"])
        if row is None:
            row = ProjectLibraryBatchModel(batch_id=batch["batch_id"], payload_json="")
            self.session.add(row)
        row.payload_json = json.dumps(batch, ensure_ascii=False)
        self.session.commit()

    def batch(self, batch_id):
        row = self.session.get(ProjectLibraryBatchModel, batch_id)
        if row is None:
            raise LookupError("Intake batch not found.")
        return json.loads(row.payload_json)

    def project_exists(self, project_id):
        return bool(project_id and self.session.get(ProjectModel, project_id))

    def project_context(self, project_id):
        row = self.session.get(ProjectModel, project_id, populate_existing=True)
        if row is None:
            raise ProjectLibraryConflict("The existing project is no longer available.")
        return {"registry_state": row.registry_state, "registry_revision": row.registry_revision,
                "workspace": self.workspace(project_id),
                "numbers": [number for number in self.project_numbers() if number["project_id"] == project_id]}

    def project_numbers(self):
        return [{"project_id": row.project_id, "ltr_number": row.ltr_number, "is_current_owner": row.is_current_owner, "status": row.status}
                for row in self.session.scalars(select(LtrRecordModel))]

    def create_planning_project(self, member):
        project_id = uuid4().hex
        self.session.add(ProjectModel(project_id=project_id, project_no=member.get("ltr_number"),
            product_name=member["title"], requestor="Imported project", status="draft",
            lifecycle_state="active", registry_state="active", registry_revision=0, created_on=date.today()))
        row = self.session.get(ProjectLibraryMemberModel, member["member_id"])
        row.project_id = project_id
        row.revision += 1
        self.session.commit()
        return project_id

    def _view(self, row):
        value = {column.name: getattr(row, column.name) for column in row.__table__.columns}
        project = self.session.get(ProjectModel, row.project_id) if row.project_id else None
        value["is_history"] = row.disposition == "recovery" or bool(project and project.registry_state != "active")
        return value

    def rebind_paths(self, project_id, source, target):
        from backend.infrastructure.project_library.ownership import rebind_project_paths
        rebind_project_paths(self.session, project_id, source, target)
        self.session.commit()

    def link_existing_project(self, member, project_id):
        if self.project_context(project_id)["registry_state"] != "active":
            raise ProjectLibraryConflict("The existing project is retained history or in Trash. Resolve its registry state before takeover.")
        from backend.infrastructure.project_library.ownership import rebind_project_paths
        if any(row["project_id"] == project_id and row["member_id"] != member["member_id"] for row in self.members()):
            raise ProjectLibraryConflict("Another entry already manages this project.")
        workspace = self.workspace(project_id)
        origin = workspace["local_workspace_path"] if workspace else member["source_path"]
        rebind_project_paths(self.session, project_id, origin, member["folder_path"])
        row = self.session.get(ProjectLibraryMemberModel, member["member_id"])
        row.project_id = project_id
        row.revision += 1
        self.session.commit()

    def workspace(self, project_id):
        row = self.session.scalar(select(ProjectOfficialWorkspaceRecordModel).where(ProjectOfficialWorkspaceRecordModel.project_id == project_id))
        return {column.name: getattr(row, column.name) for column in row.__table__.columns} if row else None

    def workspaces(self):
        return [{column.name: getattr(row, column.name) for column in row.__table__.columns}
                for row in self.session.scalars(select(ProjectOfficialWorkspaceRecordModel))]

    def publish_move(self, member, source, target, root, title, business_target):
        from backend.infrastructure.project_library.ownership import rebind_project_paths
        project_id = member["project_id"]
        workspace = self.workspace(project_id) if project_id else None
        extra = [(workspace["official_folder_path"], business_target)] if workspace else []
        if project_id:
            rebind_project_paths(self.session, project_id, source, target, extra)
        row = self.session.get(ProjectLibraryMemberModel, member["member_id"])
        if row.revision != member["revision"]:
            self.session.rollback()
            raise ProjectLibraryConflict("The project entry changed before its location was saved.")
        row.folder_path, row.title = root, title
        row.revision += 1
        self.session.commit()
        return self._view(row)

    def reserve_batch(self, batch):
        self.session.rollback()
        connection = self.session.connection()
        connection.exec_driver_sql("BEGIN IMMEDIATE")
        row = self.session.get(ProjectLibraryBatchModel, batch["batch_id"])
        if row is not None:
            previous = json.loads(row.payload_json)
            if previous.get("intent") != batch.get("intent"):
                self.session.rollback()
                raise ProjectLibraryConflict("This batch identity belongs to a different confirmed request.")
            self.session.commit()
            return previous
        self.session.add(ProjectLibraryBatchModel(batch_id=batch["batch_id"], payload_json=json.dumps(batch, ensure_ascii=False)))
        self.session.commit()
        return batch
