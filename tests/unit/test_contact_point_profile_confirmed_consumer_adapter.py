from types import SimpleNamespace

import pytest

from backend.application.contact_point_profile_fingerprint import point_profile_fingerprint
from backend.application.contact_point_profile_confirmed_consumer_adapter import (
    ContactPointProfileConfirmedConsumerAdapter,
)


def test_adapter_projects_active_confirmed_profile_total_and_lineage() -> None:
    categories = (
        _category("ppc-1", 0, "HP", 4, "HP", "1-4"),
        _category("ppc-2", 1, "LP", 5, "LP", "1-5"),
    )
    revision = _revision("root-1", "revision-1", categories)
    result = ContactPointProfileConfirmedConsumerAdapter(
        repository=_Repository(root=_root("root-1", "revision-1"), revision=revision, categories=categories)
    ).get_effective("P1")

    assert result.status == "confirmed"
    assert result.readings_per_sample == "9"
    assert result.revision_id == "revision-1"
    assert result.revision_sequence == 3
    assert result.fingerprint == revision.revision_fingerprint
    assert result.lineage == (
        "Confirmed Project Point Profile: revision 3 "
        "(revision-1; " + revision.revision_fingerprint + ")"
    )


def test_adapter_accepts_legacy_v1_fingerprint_without_point_expression() -> None:
    categories = (_category("ppc-1", 0, "HP", 4, "HP", "1-4"),)
    revision = _revision("root-1", "revision-1", categories)
    revision.revision_fingerprint = point_profile_fingerprint(
        "root-1",
        "revision-1",
        tuple({key: value for key, value in _payload(item).items() if key != "point_expression"} for item in categories),
    )

    result = ContactPointProfileConfirmedConsumerAdapter(
        repository=_Repository(root=_root("root-1", "revision-1"), revision=revision, categories=categories)
    ).get_effective("P1")

    assert result.status == "confirmed"
    assert result.readings_per_sample == "4"


def test_adapter_accepts_current_v3_fingerprint_with_custom_cr_coverage() -> None:
    categories = (
        _category("ppc-1", 0, "HP", 4, "HP", "1-4"),
        _category("ppc-2", 1, "LP", 5, "LP", "1-5"),
    )
    revision = _revision("root-1", "revision-1", categories)
    revision.revision_fingerprint = point_profile_fingerprint(
        "root-1",
        "revision-1",
        tuple(_payload(item) for item in categories),
        version="point-profile:v3",
        cr_coverage_mode="custom",
        cr_selected_category_ids=("ppc-2",),
    )

    result = ContactPointProfileConfirmedConsumerAdapter(
        repository=_Repository(
            root=_root("root-1", "revision-1"),
            revision=revision,
            categories=categories,
            cr_category_ids=("ppc-2",),
        )
    ).get_effective("P1")

    assert result.status == "confirmed"
    assert result.readings_per_sample == "9"


def test_adapter_reports_draft_without_activating_editable_profile() -> None:
    result = ContactPointProfileConfirmedConsumerAdapter(
        repository=_Repository(
            root=SimpleNamespace(
                contact_point_profile_root_id="root-1",
                project_id="P1",
                active_confirmed_revision_id=None,
                editable_revision_id="draft-1",
            ),
            revision=None,
            categories=(),
            editable=SimpleNamespace(contact_point_profile_revision_id="draft-1"),
        )
    ).get_effective("P1")

    assert result.status == "draft"
    assert result.is_usable is False


@pytest.mark.parametrize("enabled,status", [(False, "disabled"), (True, "authority_corrupt")])
def test_adapter_fails_closed_for_disabled_or_corrupt_authority(enabled: bool, status: str) -> None:
    root = _root("root-1", "revision-1") if enabled else None
    result = ContactPointProfileConfirmedConsumerAdapter(
        repository=_Repository(root=root, revision=None, categories=()),
        enabled=enabled,
    ).get_effective("P1")

    assert result.status == status
    assert result.is_usable is False


def _root(root_id: str, revision_id: str):
    return SimpleNamespace(
        contact_point_profile_root_id=root_id,
        project_id="P1",
        active_confirmed_revision_id=revision_id,
        editable_revision_id=None,
    )


def _revision(root_id: str, revision_id: str, categories):
    payload = tuple(_payload(item) for item in categories)
    return SimpleNamespace(
        contact_point_profile_revision_id=revision_id,
        contact_point_profile_root_id=root_id,
        revision_sequence=3,
        state="confirmed",
        revision_fingerprint=point_profile_fingerprint(root_id, revision_id, payload, version="point-profile:v2"),
    )


def _category(category_id: str, ordinal: int, label: str, count: int, prefix: str, expression: str):
    return SimpleNamespace(
        category_id=category_id,
        category_ordinal=ordinal,
        label=label,
        normalized_label_key=label.casefold(),
        count_per_sample=count,
        record_prefix=prefix,
        normalized_prefix_key=prefix.casefold(),
        included=True,
        point_expression=expression,
    )


def _payload(category):
    return {
        "category_id": category.category_id,
        "category_ordinal": category.category_ordinal,
        "label": category.label,
        "normalized_label_key": category.normalized_label_key,
        "count_per_sample": category.count_per_sample,
        "record_prefix": category.record_prefix,
        "normalized_prefix_key": category.normalized_prefix_key,
        "included": category.included,
        "point_expression": category.point_expression,
    }


class _Repository:
    def __init__(self, *, root, revision, categories, editable=None, cr_category_ids=()) -> None:
        self._root = root
        self._revision = revision
        self._categories = categories
        self._editable = editable
        self._cr_category_ids = cr_category_ids

    def get_root(self, project_id: str):
        return self._root if project_id == "P1" else None

    def active_revision(self, project_id: str):
        return self._revision if project_id == "P1" else None

    def editable_revision(self, project_id: str):
        return self._editable if project_id == "P1" else None

    def categories(self, revision_id: str):
        return list(self._categories) if revision_id == "revision-1" else []

    def cr_category_ids(self, revision_id: str):
        return list(self._cr_category_ids) if revision_id == "revision-1" else []
