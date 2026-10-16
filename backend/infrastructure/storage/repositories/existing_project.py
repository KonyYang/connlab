"""Persist only approved local project/location links."""
from sqlalchemy import select
from backend.infrastructure.storage.models_existing_project import ExistingProjectLocationModel


class ExistingProjectRepository:
    def __init__(self, session):
        self.session = session

    def list(self):
        return list(self.session.scalars(select(ExistingProjectLocationModel).order_by(
            ExistingProjectLocationModel.management_number, ExistingProjectLocationModel.root_path)))

    def get(self, location_id):
        return self.session.get(ExistingProjectLocationModel, location_id)

    def by_path(self, path):
        return self.session.scalar(select(ExistingProjectLocationModel).where(
            ExistingProjectLocationModel.root_path == path))

    def add(self, **values):
        row = ExistingProjectLocationModel(**values)
        self.session.add(row)
        self.session.flush()
        return row

    def flush(self):
        self.session.flush()

    def numbers(self):
        from backend.infrastructure.storage.models import LtrRecordModel
        return [value for value in self.session.scalars(select(LtrRecordModel.ltr_number)) if value]

