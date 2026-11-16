"""Read existing identities and roots without registering or relocating anything."""
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
import logging
from pathlib import PureWindowsPath
from backend.infrastructure.storage.models import ProjectFolderRecordModel, ProjectModel
from backend.infrastructure.storage.models_legacy_projects import LegacyProjectRecordModel
from backend.infrastructure.storage.repositories.project_library import ProjectLibraryRepository


logger=logging.getLogger(__name__)

class LibrarySearchRepository:
    def __init__(self, session, summaries):
        self.session, self.summaries = session, summaries

    def copy_target_eligible(self, project_id):
        row = self.summaries.get_row(project_id)
        return bool(row and row.registry_state == "active" and row.display_project_id_kind != "temporary")

    def catalog(self):
        store = ProjectLibraryRepository(self.session)
        members = store.members()
        hidden = set(self.session.scalars(select(ProjectModel.project_id).where(ProjectModel.registry_state != "active")))
        workspaces = {row["project_id"]: row for row in store.workspaces()}
        folders = {}
        for row in self.session.scalars(select(ProjectFolderRecordModel).order_by(ProjectFolderRecordModel.created_on, ProjectFolderRecordModel.folder_id)):
            folders[row.project_id] = row.folder_path
        entries, represented = [], set()
        for row in self.summaries.list_rows():
            if row.registry_state != "active":
                continue
            member = next((m for m in members if m["project_id"] == row.project_id and m.get("disposition") != "recovery"), None)
            workspace = workspaces.get(row.project_id)
            root = workspace["local_workspace_path"] if workspace else folders.get(row.project_id) or (member["folder_path"] if member else "")
            entries.append(dict(key=f"project:{row.project_id}", project_id=row.project_id,
                member_id=member["member_id"] if member else None, title=row.sample_description or "Not recorded",
                number=row.display_project_id, test_item=row.test_item or "", source="received" if member else "connlab", folder_path=root))
            if member and PureWindowsPath(root) == PureWindowsPath(member["folder_path"]):
                represented.add(member["member_id"])
        for member in members:
            if member["member_id"] not in represented and member["project_id"] not in hidden:
                entries.append(dict(key=f"member:{member['member_id']}", project_id=member["project_id"], member_id=member["member_id"],
                    title=member["title"], number=member["ltr_number"], test_item="", source="received", folder_path=member["folder_path"]))
        for row in self.session.scalars(select(LegacyProjectRecordModel)):
            entries.append(dict(key=f"linked:{row.record_id}", project_id=None, member_id=None,
                title=row.name, number=row.number, test_item="", source="linked", folder_path=row.folder_path))
        from backend.infrastructure.storage.repositories.material_receipt import MaterialReceiptRepository
        entries.extend(MaterialReceiptRepository(self.session).catalog())
        try:
            from backend.infrastructure.storage.repositories.material_archive import MaterialArchiveRepository,normalized
            represented_paths={normalized(row['folder_path']) for row in entries if row['folder_path']}
            entries.extend(row for row in MaterialArchiveRepository(self.session).catalog() if normalized(row['folder_path']) not in represented_paths)
        except (SQLAlchemyError,ValueError,LookupError):
            logger.exception('Materials archive catalog unavailable')
            self.session.rollback()
            self.archive_index_error=True
        return entries

    def indexed_files(self,key):
        from backend.infrastructure.storage.repositories.material_archive import MaterialArchiveRepository
        return MaterialArchiveRepository(self.session).indexed_files(key)

    def indexed_available(self,path):
        from backend.infrastructure.storage.repositories.material_archive import MaterialArchiveRepository
        try:return MaterialArchiveRepository(self.session).indexed_available(path)
        except SQLAlchemyError:
            logger.exception('Materials archive index unavailable for %s',path)
            self.session.rollback();self.archive_index_error=True;return False

    def cache_index(self,entry,files,available=True):
        from backend.infrastructure.storage.repositories.material_archive import MaterialArchiveRepository
        return MaterialArchiveRepository(self.session).cache(entry,files,available)
