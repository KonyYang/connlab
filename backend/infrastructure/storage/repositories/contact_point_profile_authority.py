"""SQLite repository for independent project Point Profile authority."""

from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from contextlib import contextmanager

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.infrastructure.storage.models_contact_point_profile import (
    ContactPointProfileCategoryModel,
    ContactPointProfileRevisionModel,
    ContactPointProfileRootModel,
)


_PPC = re.compile(r"ppc-([1-9][0-9]*)$")


class ContactPointProfileAuthorityRepository:
    """Keep Point Profile reads and transactional snapshot writes narrowly scoped."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_root(self, project_id: str) -> ContactPointProfileRootModel | None:
        return self._session.scalar(
            select(ContactPointProfileRootModel).where(ContactPointProfileRootModel.project_id == project_id)
        )

    def get_revision(self, revision_id: str) -> ContactPointProfileRevisionModel | None:
        return self._session.get(ContactPointProfileRevisionModel, revision_id)

    def editable_revision(self, project_id: str) -> ContactPointProfileRevisionModel | None:
        root = self.get_root(project_id)
        return self.get_revision(root.editable_revision_id) if root and root.editable_revision_id else None

    def active_revision(self, project_id: str) -> ContactPointProfileRevisionModel | None:
        root = self.get_root(project_id)
        return self.get_revision(root.active_confirmed_revision_id) if root and root.active_confirmed_revision_id else None

    def categories(self, revision_id: str) -> list[ContactPointProfileCategoryModel]:
        return list(self._session.scalars(
            select(ContactPointProfileCategoryModel)
            .where(ContactPointProfileCategoryModel.contact_point_profile_revision_id == revision_id)
            .order_by(ContactPointProfileCategoryModel.category_ordinal)
        ).all())

    def highest_category_number(self, root_id: str) -> int:
        statement = (
            select(ContactPointProfileCategoryModel.category_id)
            .join(ContactPointProfileRevisionModel)
            .where(ContactPointProfileRevisionModel.contact_point_profile_root_id == root_id)
        )
        return max(
            (int(match.group(1)) for value in self._session.scalars(statement)
             if (match := _PPC.fullmatch(value))),
            default=0,
        )

    def category_ids_for_root(self, root_id: str) -> set[str]:
        statement = (
            select(ContactPointProfileCategoryModel.category_id)
            .join(ContactPointProfileRevisionModel)
            .where(ContactPointProfileRevisionModel.contact_point_profile_root_id == root_id)
        )
        return set(self._session.scalars(statement).all())

    def highest_revision_sequence(self, root_id: str) -> int:
        statement = select(ContactPointProfileRevisionModel.revision_sequence).where(
            ContactPointProfileRevisionModel.contact_point_profile_root_id == root_id
        )
        return max(self._session.scalars(statement).all(), default=0)

    def replace_categories(self, revision_id: str, categories: Sequence[dict[str, object]], id_factory) -> None:
        for row in self.categories(revision_id):
            self._session.delete(row)
        self._session.flush()
        for category in categories:
            self._session.add(ContactPointProfileCategoryModel(
                contact_point_profile_category_snapshot_id=f"cppc-{id_factory()}",
                contact_point_profile_revision_id=revision_id,
                category_id=str(category["category_id"]),
                category_ordinal=int(category["category_ordinal"]),
                label=str(category["label"]),
                normalized_label_key=str(category["normalized_label_key"]),
                count_per_sample=int(category["count_per_sample"]),
                record_prefix=str(category["record_prefix"]),
                normalized_prefix_key=str(category["normalized_prefix_key"]),
                included=bool(category["included"]),
                point_expression=category.get("point_expression"),
            ))

    def add(self, *rows: object) -> None:
        self._session.add_all(rows)

    def flush(self) -> None:
        self._session.flush()

    @contextmanager
    def transaction(self) -> Iterator[None]:
        with self._session.begin_nested():
            yield
