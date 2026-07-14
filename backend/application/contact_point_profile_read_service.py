"""Read-only workspace and confirmed summary projections for Point Profiles."""

from __future__ import annotations

from backend.application.contact_point_profile_fingerprint import points_per_sample


class ContactPointProfileReadService:
    def __init__(self, repository, legacy_suggestion_service=None) -> None:
        self._repository = repository
        self._legacy_suggestion = legacy_suggestion_service

    def get_workspace(self, project_id: str) -> dict[str, object]:
        root = self._repository.get_root(project_id)
        if root is None:
            return {
                "status": "not_started", "project_id": project_id,
                "editable_revision": None, "confirmed_revision": None,
                "has_unconfirmed_draft": False,
                "legacy_uniform_suggestion": self._suggest(project_id), "diagnostics": [],
            }
        editable = self._repository.editable_revision(project_id)
        confirmed = self._repository.active_revision(project_id)
        return {
            "status": "draft" if editable else ("confirmed" if confirmed else "authority_corrupt"),
            "project_id": project_id,
            "editable_revision": _revision_payload(editable, self._repository) if editable else None,
            "confirmed_revision": _revision_payload(confirmed, self._repository) if confirmed else None,
            "has_unconfirmed_draft": editable is not None,
            "legacy_uniform_suggestion": None,
            "diagnostics": [],
        }

    def get_summary(self, project_id: str) -> dict[str, object]:
        root = self._repository.get_root(project_id)
        confirmed = self._repository.active_revision(project_id) if root else None
        return {
            "status": "confirmed" if confirmed else "not_started",
            "project_id": project_id,
            "confirmed_revision": _revision_payload(confirmed, self._repository) if confirmed else None,
            "points_per_sample": _total(confirmed, self._repository),
            "has_unconfirmed_draft": bool(root and root.editable_revision_id),
            "diagnostics": [],
        }

    def _suggest(self, project_id: str):
        return self._legacy_suggestion.get_uniform_suggestion(project_id) if self._legacy_suggestion else None


def _revision_payload(revision, repository) -> dict[str, object]:
    categories = [_category_payload(row) for row in repository.categories(revision.contact_point_profile_revision_id)]
    return {
        "revision_id": revision.contact_point_profile_revision_id,
        "revision_sequence": revision.revision_sequence,
        "state": revision.state,
        "fingerprint": revision.revision_fingerprint,
        "created_at": revision.created_at,
        "confirmed_at": revision.confirmed_at,
        "categories": categories,
        "points_per_sample": points_per_sample(categories),
    }


def _category_payload(row) -> dict[str, object]:
    return {
        "category_id": row.category_id, "category_ordinal": row.category_ordinal,
        "label": row.label, "count_per_sample": row.count_per_sample,
        "record_prefix": row.record_prefix, "included": row.included,
    }


def _total(revision, repository) -> int | None:
    return _revision_payload(revision, repository)["points_per_sample"] if revision else None
