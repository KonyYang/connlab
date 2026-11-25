"""Read existing identities and roots without registering or relocating anything."""
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
import logging
from pathlib import Path, PureWindowsPath
from backend.application.basic_project_workspace_service import BasicProjectWorkspaceService
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.storage.repositories.official_workspace import ProjectOfficialWorkspaceRepository
from backend.infrastructure.storage.models import ProjectModel
from backend.infrastructure.storage.models_legacy_projects import LegacyProjectRecordModel
from backend.infrastructure.storage.repositories.project_library import ProjectLibraryRepository


logger=logging.getLogger(__name__)

class LibrarySearchRepository:
    def __init__(self, session, summaries, data_dir):
        self.session, self.summaries = session, summaries
        self.workspaces = ProjectOfficialWorkspaceRepository(session)
        self.journal = GenerationJournal(data_dir / "basic_project_workspace")

    def copy_target_eligible(self, project_id):
        row = self.summaries.get_row(project_id)
        if not row or row.registry_state != "active" or row.display_project_id_kind == "temporary":
            return False
        record = self.workspaces.get_by_project(project_id)
        if record is None:
            raise ValueError("Create the project folder in the Workbench before copying materials.")
        return True

    def check_material_entry(self, entry):
        """Live operations verify the selected project without touching unrelated directories."""
        if not entry["key"].startswith("project:") or not entry["folder_path"]:
            return entry
        record = self.workspaces.get_by_project(entry["project_id"])
        if record is None and entry["source"] == "received":
            return entry
        if record and record.local_workspace_path == Path(entry["folder_path"]):
            try:
                operation = self.journal.read(record.project_id)
            except (OSError, ValueError):
                return {**entry, "workspace_unavailable": True}
            if BasicProjectWorkspaceService.registered_directory_available(record, operation):
                return entry
        return {**entry, "workspace_unavailable": True}

    def catalog(self):
        store = ProjectLibraryRepository(self.session)
        members = store.members()
        hidden = set(self.session.scalars(select(ProjectModel.project_id).where(ProjectModel.registry_state != "active")))
        workspaces = {record["project_id"]: record["local_workspace_path"] for record in store.workspaces()}
        entries, represented = [], set()
        for row in self.summaries.list_rows():
            if row.registry_state != "active":
                continue
            member = next((m for m in members if m["project_id"] == row.project_id and m.get("disposition") != "recovery"), None)
            root = workspaces.get(row.project_id) or (member["folder_path"] if member else "")
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
