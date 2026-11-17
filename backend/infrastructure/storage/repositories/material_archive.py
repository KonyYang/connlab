"""Derived archive directory index, separate from durable copy operations."""
from uuid import uuid4
from sqlalchemy import select,delete
from backend.domain.project_library import ProjectLibraryConflict
from backend.infrastructure.storage.models_project_library import MaterialArchiveFolderModel, MaterialArchiveFileModel, MaterialReceiptBatchModel
from backend.infrastructure.storage.repositories.material_receipt import MaterialReceiptRepository
import json
import os

def normalized(path):
    return os.path.normpath(os.path.abspath(str(path))).replace("\\", "/").casefold()

class MaterialArchiveRepository:
    def __init__(self, session):
        self.session=session
        self.receipts=MaterialReceiptRepository(session)

    def operations(self):
        return [value for row in self.session.scalars(select(MaterialReceiptBatchModel).execution_options(populate_existing=True))
                if (value:=json.loads(row.payload_json)).get("operation")=="material_archive"]

    def operation(self, operation_id):
        value=self.receipts.batch(operation_id)
        if not value or value.get("operation")!="material_archive":
            raise LookupError("Archive operation not found.")
        return value

    def save(self, value):
        try: self.receipts.save_batch(value)
        except Exception:
            self.session.rollback()
            raise

    def rollback(self): self.session.rollback()

    def register(self, root, path, number, title, operation_id=None, folder_id=None):
        canonical=normalized(path)
        row=self.session.scalar(select(MaterialArchiveFolderModel).where(MaterialArchiveFolderModel.normalized_path==canonical))
        if row is None:
            row=MaterialArchiveFolderModel(folder_id=folder_id or uuid4().hex,normalized_path=canonical,
                library_root=str(root),folder_path=str(path),number=number,title=title,operation_id=operation_id)
            self.session.add(row)
        elif operation_id and row.operation_id not in {None,operation_id}:
            raise ProjectLibraryConflict("This directory belongs to another archive operation.")
        elif operation_id:
            row.operation_id=operation_id
        # A cached external source may later become a child of the configured library.
        row.library_root=str(root)
        try: self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        return self.folder(row.folder_id)

    def folder(self, folder_id):
        row=self.session.get(MaterialArchiveFolderModel,folder_id,populate_existing=True)
        if row is None: raise LookupError("Archive folder not found. Refresh the library.")
        return dict(key="archive:"+row.folder_id,folder_id=row.folder_id,project_id=None,member_id=None,
            number=row.number,title=row.title,test_item="",source="received",folder_path=row.folder_path,
            library_root=row.library_root,operation_id=row.operation_id)

    def catalog(self):
        rows=[self.folder(row.folder_id) for row in self.session.scalars(select(MaterialArchiveFolderModel).where(MaterialArchiveFolderModel.library_root!=''))]
        for row in rows:
            operation=self.operation(row['operation_id']) if row['operation_id'] else None
            row['intake_status']=operation['status'] if operation else 'completed'
        indexed={row['operation_id'] for row in rows if row['operation_id']}
        for op in self.operations():
            if op['batch_id'] not in indexed and op['status']!='completed':
                rows.append(dict(key='archive:'+op['folder_id'],folder_id=op['folder_id'],project_id=None,member_id=None,
                    number=op['number'],title=op['title'],test_item='',source='received',folder_path=op['target_path'],
                    library_root=op['root_path'],operation_id=op['batch_id'],intake_status=op['status']))
        return rows

    def cache(self, entry, files, available=True):
        path=entry['folder_path'];canonical=normalized(path)
        row=self.session.scalar(select(MaterialArchiveFolderModel).where(MaterialArchiveFolderModel.normalized_path==canonical))
        if row is None:
            row=MaterialArchiveFolderModel(folder_id=uuid4().hex,normalized_path=canonical,library_root='',folder_path=path,
                number=entry.get('number'),title=entry['title'],indexed_available=available)
            self.session.add(row)
        row.indexed_available=available
        self.session.execute(delete(MaterialArchiveFileModel).where(MaterialArchiveFileModel.catalog_key==entry['key']))
        self.session.add_all([MaterialArchiveFileModel(catalog_key=entry['key'],relative_path=file['relative_path'],name=file['name'],modified_at=file.get('modified_at')) for file in files])
        try:self.session.commit()
        except Exception:
            self.session.rollback();raise

    def rebind_directory(self, folder_id, expected_path, target, library_root):
        """Relocate a verified copy without replacing its identity or relative search index."""
        row = self.session.get(MaterialArchiveFolderModel, folder_id, populate_existing=True)
        if row is None or normalized(row.folder_path) not in {normalized(expected_path), normalized(target)}:
            raise ProjectLibraryConflict("The indexed directory changed before its location was saved.")
        conflict = self.session.scalar(select(MaterialArchiveFolderModel).where(
            MaterialArchiveFolderModel.normalized_path == normalized(target),
            MaterialArchiveFolderModel.folder_id != folder_id))
        if conflict is not None:
            raise ProjectLibraryConflict("Another indexed directory already uses the new location.")
        row.folder_path, row.normalized_path, row.library_root = str(target), normalized(target), str(library_root)
        self.session.commit()
        return self.folder(folder_id)

    def indexed_available(self,path):
        row=self.session.scalar(select(MaterialArchiveFolderModel).where(MaterialArchiveFolderModel.normalized_path==normalized(path)))
        return bool(row and row.indexed_available)

    def indexed_files(self,key):
        return [dict(name=row.name,relative_path=row.relative_path,modified_at=row.modified_at) for row in self.session.scalars(
            select(MaterialArchiveFileModel).where(MaterialArchiveFileModel.catalog_key==key))]

    def mark_available(self,path,available):
        row=self.session.scalar(select(MaterialArchiveFolderModel).where(MaterialArchiveFolderModel.normalized_path==normalized(path)))
        if row is not None:
            row.indexed_available=available;self.session.commit()

    def mark_root_unavailable(self,root):
        for row in self.session.scalars(select(MaterialArchiveFolderModel)):
            if row.library_root and normalized(row.library_root)==normalized(root):row.indexed_available=False
        self.session.commit()
