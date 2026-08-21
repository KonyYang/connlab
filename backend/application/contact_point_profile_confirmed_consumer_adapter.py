"""Read-only confirmed Point Profile facts for Fee consumers."""

from __future__ import annotations

from dataclasses import dataclass

from backend.application.contact_point_profile_fingerprint import (
    point_profile_fingerprint,
    points_per_sample,
)


@dataclass(frozen=True, slots=True)
class EffectiveConfirmedPointProfile:
    """One fail-closed Point Profile projection for downstream consumers."""

    status: str
    readings_per_sample: str | None
    revision_id: str | None
    revision_sequence: int | None
    fingerprint: str | None
    lineage: str | None
    message: str | None
    cr_readings_per_sample: str | None = None

    @property
    def is_usable(self) -> bool:
        return self.status == "confirmed" and self.readings_per_sample is not None

class ContactPointProfileConfirmedConsumerAdapter:
    """Expose only validated active-confirmed Profile authority."""

    def __init__(self, *, repository, enabled: bool = True) -> None:
        self._repository = repository
        self._enabled = enabled

    def get_effective(self, project_id: str) -> EffectiveConfirmedPointProfile:
        if not self._enabled:
            return _result("disabled", "Point Profile authority is disabled.")
        root = self._repository.get_root(project_id)
        if root is None:
            return _result("not_started", "Confirm Point Profile before calculating LLCR units.")
        revision = self._repository.active_revision(project_id)
        if revision is None:
            if self._repository.editable_revision(project_id) is not None:
                return _result("draft", "Confirm Point Profile before calculating LLCR units.")
            return _result("authority_corrupt", "Point Profile authority requires review.")
        if (
            root.active_confirmed_revision_id != revision.contact_point_profile_revision_id
            or revision.contact_point_profile_root_id != root.contact_point_profile_root_id
            or revision.state != "confirmed"
        ):
            return _result("authority_corrupt", "Point Profile authority requires review.")
        categories = self._repository.categories(revision.contact_point_profile_revision_id)
        payload = tuple(_category_payload(category) for category in categories)
        readings = points_per_sample(payload)
        custom_category_ids = tuple(
            self._repository.cr_category_ids(revision.contact_point_profile_revision_id)
        )
        if readings <= 0 or not _fingerprint_matches(
            root,
            revision,
            payload,
            custom_category_ids,
        ):
            return _result("authority_corrupt", "Point Profile authority requires review.")
        latest_root = self._repository.get_root(project_id)
        latest_revision = self._repository.active_revision(project_id)
        if (
            latest_root is None
            or latest_revision is None
            or latest_root.active_confirmed_revision_id != revision.contact_point_profile_revision_id
            or latest_revision.contact_point_profile_revision_id
            != revision.contact_point_profile_revision_id
            or latest_revision.revision_fingerprint != revision.revision_fingerprint
        ):
            return _result("stale", "Point Profile authority changed; reload before calculating LLCR units.")
        lineage = (
            "Confirmed Project Point Profile: revision "
            f"{revision.revision_sequence} ({revision.contact_point_profile_revision_id}; "
            f"{revision.revision_fingerprint})"
        )
        return EffectiveConfirmedPointProfile(
            status="confirmed",
            readings_per_sample=str(readings),
            revision_id=revision.contact_point_profile_revision_id,
            revision_sequence=revision.revision_sequence,
            fingerprint=revision.revision_fingerprint,
            lineage=lineage,
            message=None,
            cr_readings_per_sample=str(
                _cr_points_per_sample(payload, custom_category_ids)
            ),
        )


def _result(status: str, message: str) -> EffectiveConfirmedPointProfile:
    return EffectiveConfirmedPointProfile(
        status=status,
        readings_per_sample=None,
        revision_id=None,
        revision_sequence=None,
        fingerprint=None,
        lineage=None,
        message=message,
    )


def _category_payload(category) -> dict[str, object]:
    label = str(category.label)
    prefix = str(category.record_prefix)
    return {
        "category_id": str(category.category_id),
        "category_ordinal": int(category.category_ordinal),
        "label": label,
        "normalized_label_key": str(
            getattr(category, "normalized_label_key", None) or label.casefold()
        ),
        "count_per_sample": int(category.count_per_sample),
        "record_prefix": prefix,
        "normalized_prefix_key": str(
            getattr(category, "normalized_prefix_key", None) or prefix.casefold()
        ),
        "included": bool(category.included),
        "point_expression": getattr(category, "point_expression", None),
    }


def _cr_points_per_sample(
    categories: tuple[dict[str, object], ...],
    custom_category_ids: tuple[str, ...],
) -> int:
    if not custom_category_ids:
        return points_per_sample(categories)
    selected = set(custom_category_ids)
    return sum(
        int(category["count_per_sample"])
        for category in categories
        if str(category["category_id"]) in selected and bool(category["included"])
    )


def _fingerprint_matches(
    root,
    revision,
    categories: tuple[dict[str, object], ...],
    custom_category_ids: tuple[str, ...] = (),
) -> bool:
    expected = revision.revision_fingerprint
    legacy_categories = tuple(
        {key: value for key, value in category.items() if key != "point_expression"}
        for category in categories
    )
    return expected in {
        point_profile_fingerprint(
            root.contact_point_profile_root_id,
            revision.contact_point_profile_revision_id,
            legacy_categories,
            version="point-profile:v1",
        ),
        point_profile_fingerprint(
            root.contact_point_profile_root_id,
            revision.contact_point_profile_revision_id,
            categories,
            version="point-profile:v2",
        ),
        point_profile_fingerprint(
            root.contact_point_profile_root_id,
            revision.contact_point_profile_revision_id,
            categories,
            version="point-profile:v3",
            cr_coverage_mode="custom" if custom_category_ids else "follow_llcr",
            cr_selected_category_ids=custom_category_ids,
        ),
    }
