"""Receipt-only identities and journals; never create or mutate business projects."""
import json
from sqlalchemy import select
from backend.infrastructure.storage.models_project_library import (
    MaterialReceiptSettingsModel, MaterialReceiptEntryModel, MaterialReceiptBatchModel,
)
from backend.domain.project_library import ProjectLibraryConflict


class MaterialReceiptRepository:
    def __init__(self, session):
        self.session = session

    def settings(self):
        row = self.session.get(MaterialReceiptSettingsModel, "default", populate_existing=True)
        return {"root_path": row.root_path, "revision": row.revision} if row else {"root_path": "", "revision": 0}

    def configure(self, root):
        row = self.session.get(MaterialReceiptSettingsModel, "default")
        if row is None:
            self.session.add(MaterialReceiptSettingsModel(settings_id="default", root_path=root, revision=1))
        elif row.root_path != root:
            row.root_path, row.revision = root, row.revision + 1
        self.session.commit()
        return self.settings()

    def catalog(self):
        return [dict(key=f"receipt:{r.receipt_id}", receipt_id=r.receipt_id, project_id=None,
            member_id=None, number=r.number, title=f"{r.product_name} ({r.description})" if r.description else r.product_name, test_item=r.test_keywords,
            folder_path=r.folder_path, source="received", revision=r.revision, description=r.description, material_state=r.material_state)
            for r in self.session.scalars(select(MaterialReceiptEntryModel))]

    def entry(self, receipt_id):
        row = self.session.get(MaterialReceiptEntryModel, receipt_id, populate_existing=True)
        if row is None:
            raise LookupError("Received materials not found.")
        return {column.name: getattr(row, column.name) for column in row.__table__.columns}

    def add_entry(self, data):
        if self.session.get(MaterialReceiptEntryModel, data["receipt_id"]) is None:
            self.session.add(MaterialReceiptEntryModel(**data))
            self.session.commit()
        return self.entry(data["receipt_id"])

    def edit_entry(self, receipt_id, revision, **changes):
        row = self.session.get(MaterialReceiptEntryModel, receipt_id, populate_existing=True)
        if row is None:
            raise LookupError("Received materials not found.")
        if row.revision != revision:
            raise ProjectLibraryConflict("The entry changed. Refresh its details before saving.")
        for key, value in changes.items():
            if key not in {"product_name", "test_keywords", "folder_path", "material_state"}:
                raise ValueError("Unsupported received-materials change.")
            setattr(row, key, value)
        row.revision += 1
        self.session.commit()
        return self.entry(receipt_id)

    def batch(self, batch_id):
        row = self.session.get(MaterialReceiptBatchModel, batch_id, populate_existing=True)
        return json.loads(row.payload_json) if row else None

    def batches_for_target(self, target):
        rows = [json.loads(row.payload_json) for row in self.session.scalars(select(MaterialReceiptBatchModel))]
        return [row for row in rows if row.get("target_path") == target]

    def protected_roots(self, excluding_receipt=None, excluding_member=None):
        from backend.infrastructure.storage.models import ProjectFolderRecordModel, ProjectOfficialWorkspaceRecordModel
        from backend.infrastructure.storage.models_legacy_projects import LegacyProjectRecordModel
        from backend.infrastructure.storage.models_project_library import ProjectLibraryMemberModel
        roots = [row.folder_path for row in self.session.scalars(select(ProjectFolderRecordModel))]
        for row in self.session.scalars(select(ProjectOfficialWorkspaceRecordModel)):
            roots.extend([row.local_workspace_path, row.official_folder_path])
        roots.extend(row.folder_path for row in self.session.scalars(select(LegacyProjectRecordModel)))
        for row in self.session.scalars(select(ProjectLibraryMemberModel)):
            roots.append(row.source_path)
            if row.member_id != excluding_member:
                roots.append(row.folder_path)
        for row in self.session.scalars(select(MaterialReceiptEntryModel)):
            roots.append(row.source_path)
            if row.receipt_id != excluding_receipt:
                roots.append(row.folder_path)
        return [root for root in roots if root]

    def unbound_member(self, member_id):
        from backend.infrastructure.storage.models_project_library import ProjectLibraryMemberModel
        row = self.session.get(ProjectLibraryMemberModel, member_id, populate_existing=True)
        if row is None:
            raise LookupError("Received materials not found.")
        if row.project_id is not None:
            raise ProjectLibraryConflict("This folder belongs to a business project. Use its workspace location controls.")
        return {"key": f"member:{member_id}", "folder_path": row.folder_path,
                "source_path": row.source_path, "revision": row.revision}

    def locate_unbound_member(self, member_id, expected, target):
        from backend.infrastructure.storage.models_project_library import ProjectLibraryMemberModel
        if self.unbound_member(member_id) != expected:
            raise ProjectLibraryConflict("The entry changed. Locate its folder again.")
        row = self.session.get(ProjectLibraryMemberModel, member_id)
        row.folder_path = target
        row.revision += 1
        self.session.commit()
        return self.unbound_member(member_id)

    def refresh(self):
        self.session.expire_all()

    def save_batch(self, value):
        row = self.session.get(MaterialReceiptBatchModel, value["batch_id"])
        if row is None:
            row = MaterialReceiptBatchModel(batch_id=value["batch_id"], payload_json="")
            self.session.add(row)
        row.payload_json = json.dumps(value, ensure_ascii=False)
        self.session.commit()
