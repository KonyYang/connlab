"""Read-only, uniform legacy target-family suggestion for Point Profile setup."""

from __future__ import annotations


class ContactPointProfileLegacySuggestionService:
    """Offer legacy families only when every included target has the same profile."""

    def __init__(self, legacy_repository) -> None:
        self._legacy_repository = legacy_repository

    def get_uniform_suggestion(self, project_id: str) -> list[dict[str, object]] | None:
        revision = self._legacy_repository.get_active_revision(project_id)
        if revision is None:
            return None
        signatures: list[tuple[tuple[str, int, str, bool], ...]] = []
        for target in self._legacy_repository.targets(revision.measurement_plan_revision_id):
            if not target.eligible or not target.included:
                continue
            families = self._legacy_repository.families(target.measurement_plan_target_snapshot_id)
            signatures.append(tuple(
                (family.label, family.count_per_sample, family.record_prefix, family.included)
                for family in families
            ))
        if not signatures or any(signature != signatures[0] for signature in signatures[1:]):
            return None
        return [
            {
                "category_id": None,
                "category_ordinal": ordinal,
                "label": label,
                "count_per_sample": count,
                "record_prefix": prefix,
                "included": included,
            }
            for ordinal, (label, count, prefix, included) in enumerate(signatures[0])
        ]
