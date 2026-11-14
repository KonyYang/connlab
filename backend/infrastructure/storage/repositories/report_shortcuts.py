"""Workstation-local path pointers, outside all portable project data."""
from sqlalchemy import select
from backend.infrastructure.storage.models_project_library import ReportShortcutModel


class ReportShortcutRepository:
    def __init__(self, session):
        self.session = session

    def list(self, key):
        self.session.expire_all()
        return [{"role": row.role, "relative_path": row.relative_path} for row in self.session.scalars(
            select(ReportShortcutModel).where(ReportShortcutModel.catalog_key == key).order_by(ReportShortcutModel.role))]

    def write(self, key, role, path):
        row = self.session.get(ReportShortcutModel, (key, role), populate_existing=True)
        if path is None:
            if row is not None:
                self.session.delete(row)
        elif row is None:
            self.session.add(ReportShortcutModel(catalog_key=key, role=role, relative_path=path))
        else:
            row.relative_path = path
        self.session.commit()
