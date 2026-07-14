"""Transactional draft and confirmation commands for project Point Profiles."""

from __future__ import annotations

from uuid import uuid4

from backend.application.contact_point_profile_fingerprint import (
    ContactPointProfileValidationError,
    canonicalize_categories,
    point_profile_fingerprint,
    points_per_sample,
)
from backend.infrastructure.storage.models_contact_point_profile import (
    ContactPointProfileRevisionModel,
    ContactPointProfileRootModel,
)


class ContactPointProfileLifecycleError(ValueError):
    """Raised when a Point Profile command is invalid, stale, or unsafe."""


class ContactPointProfileLifecycleService:
    def __init__(self, repository, clock, id_factory=lambda: uuid4().hex) -> None:
        self._repository = repository
        self._clock = clock
        self._ids = id_factory

    def save_draft(self, project_id: str, expected_revision_id: str | None, expected_fingerprint: str | None, rows, actor: str) -> dict[str, object]:
        try:
            categories = list(canonicalize_categories(rows, resolve_fallback=False))
        except ContactPointProfileValidationError as exc:
            raise ContactPointProfileLifecycleError(str(exc)) from exc
        with self._repository.transaction():
            return self._save_draft(project_id, expected_revision_id, expected_fingerprint, categories, actor)

    def confirm(self, project_id: str, expected_revision_id: str, expected_fingerprint: str, rows, actor: str) -> dict[str, object]:
        try:
            confirm_categories = canonicalize_categories(rows, resolve_fallback=False)
        except ContactPointProfileValidationError as exc:
            raise ContactPointProfileLifecycleError(str(exc)) from exc
        if points_per_sample(confirm_categories) <= 0:
            raise ContactPointProfileLifecycleError("Confirm Point Profile requires an included positive total.")
        with self._repository.transaction():
            saved = self._save_draft(
                project_id, expected_revision_id, expected_fingerprint, list(confirm_categories), actor
            )
            root = self._repository.get_root(project_id)
            revision = self._repository.get_revision(str(saved["revision_id"]))
            assert root is not None and revision is not None
            now = self._clock()
            active = self._repository.active_revision(project_id)
            if active is not None and active.contact_point_profile_revision_id != revision.contact_point_profile_revision_id:
                active.state = "superseded"
                active.superseded_at = now
                active.superseded_reason = "Superseded by confirmed Point Profile revision."
            revision.state = "confirmed"
            revision.confirmed_by = actor
            revision.confirmed_at = now
            revision.updated_at = now
            root.active_confirmed_revision_id = revision.contact_point_profile_revision_id
            root.editable_revision_id = None
            root.updated_at = now
            self._repository.flush()
            return _result(revision, list(canonicalize_categories(saved["categories"])))

    def _save_draft(
        self, project_id: str, expected_revision_id: str | None, expected_fingerprint: str | None,
        categories: list[dict[str, object]], actor: str,
    ) -> dict[str, object]:
        root = self._repository.get_root(project_id)
        revision = self._editable(root)
        self._assert_expected(revision, expected_revision_id, expected_fingerprint)
        now = self._clock()
        if root is None:
            root = ContactPointProfileRootModel(
                contact_point_profile_root_id=f"cppr-{self._ids()}", project_id=project_id,
                active_confirmed_revision_id=None, editable_revision_id=None,
                created_at=now, updated_at=now,
            )
            self._repository.add(root)
            self._repository.flush()
        active = self._repository.active_revision(project_id)
        if revision is None:
            revision = ContactPointProfileRevisionModel(
                contact_point_profile_revision_id=f"cpprv-{self._ids()}",
                contact_point_profile_root_id=root.contact_point_profile_root_id,
                revision_sequence=(active.revision_sequence if active else 0) + 1,
                parent_revision_id=active.contact_point_profile_revision_id if active else None,
                state="draft", revision_fingerprint="pending", bootstrap_provenance=None,
                created_by=actor, created_at=now, updated_at=now, confirmed_by=None,
                confirmed_at=None, superseded_at=None, superseded_reason=None,
            )
            self._repository.add(revision)
            root.editable_revision_id = revision.contact_point_profile_revision_id
            self._repository.flush()
            if active is not None and not categories:
                categories = [
                    {
                        "category_id": row.category_id,
                        "category_ordinal": row.category_ordinal,
                        "label": row.label,
                        "count_per_sample": row.count_per_sample,
                        "record_prefix": row.record_prefix,
                        "included": row.included,
                    }
                    for row in self._repository.categories(active.contact_point_profile_revision_id)
                ]
        retained_ids = {
            row.category_id for row in self._repository.categories(revision.contact_point_profile_revision_id)
        }
        if not retained_ids and active is not None:
            retained_ids = {
                row.category_id for row in self._repository.categories(active.contact_point_profile_revision_id)
            }
        issued = self._issue_category_ids(root.contact_point_profile_root_id, categories, retained_ids)
        issued = list(canonicalize_categories(issued))
        self._repository.replace_categories(revision.contact_point_profile_revision_id, issued, self._ids)
        self._repository.flush()
        revision.revision_fingerprint = point_profile_fingerprint(
            root.contact_point_profile_root_id, revision.contact_point_profile_revision_id, issued
        )
        revision.updated_at = now
        root.updated_at = now
        self._repository.flush()
        return _result(revision, issued)

    def _editable(self, root):
        return self._repository.get_revision(root.editable_revision_id) if root and root.editable_revision_id else None

    def _assert_expected(self, revision, expected_id: str | None, expected_fingerprint: str | None) -> None:
        if revision is None:
            if expected_id is not None or expected_fingerprint is not None:
                raise ContactPointProfileLifecycleError("Point Profile draft is stale.")
            return
        if expected_id != revision.contact_point_profile_revision_id or expected_fingerprint != revision.revision_fingerprint:
            raise ContactPointProfileLifecycleError("Point Profile draft is stale.")

    def _issue_category_ids(
        self, root_id: str, categories: list[dict[str, object]], retained_ids: set[str]
    ) -> list[dict[str, object]]:
        high_water = self._repository.highest_category_number(root_id)
        issued: list[dict[str, object]] = []
        for category in categories:
            item = dict(category)
            category_id = item["category_id"]
            if category_id is None:
                high_water += 1
                item["category_id"] = f"ppc-{high_water}"
            elif not str(category_id).startswith("ppc-"):
                raise ContactPointProfileLifecycleError("Point Profile category id is invalid.")
            elif str(category_id) not in retained_ids:
                raise ContactPointProfileLifecycleError("Point Profile category id is not owned by this project.")
            issued.append(item)
        return issued


def _result(revision, categories: list[dict[str, object]]) -> dict[str, object]:
    return {
        "revision_id": revision.contact_point_profile_revision_id,
        "fingerprint": revision.revision_fingerprint,
        "categories": categories,
        "points_per_sample": points_per_sample(categories),
    }
