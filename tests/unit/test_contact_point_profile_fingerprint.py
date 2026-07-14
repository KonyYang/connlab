import pytest

from backend.application.contact_point_profile_fingerprint import (
    ContactPointProfileValidationError,
    canonicalize_categories,
    point_profile_fingerprint,
)


def test_canonicalize_categories_derives_total_and_persists_resolved_prefix() -> None:
    categories = canonicalize_categories(
        [
            {"category_id": "ppc-1", "label": "High Power", "count_per_sample": 4, "record_prefix": "hp", "included": True},
            {"category_id": "ppc-2", "label": "Low Power", "count_per_sample": 5, "record_prefix": "lp", "included": True},
            {"category_id": "ppc-3", "label": "Signal", "count_per_sample": 24, "record_prefix": "", "included": True},
        ]
    )

    assert [item["record_prefix"] for item in categories] == ["HP", "LP", "SIGNAL"]
    assert sum(item["count_per_sample"] for item in categories if item["included"]) == 33
    assert point_profile_fingerprint("root-1", "revision-1", categories) == point_profile_fingerprint(
        "root-1", "revision-1", categories
    )


def test_canonicalize_categories_rejects_duplicate_included_normalized_labels() -> None:
    with pytest.raises(ContactPointProfileValidationError, match="labels must be unique"):
        canonicalize_categories(
            [
                {"category_id": "ppc-1", "label": "Signal", "count_per_sample": 1, "record_prefix": "S1", "included": True},
                {"category_id": "ppc-2", "label": " SIGNAL ", "count_per_sample": 2, "record_prefix": "S2", "included": True},
            ]
        )


def test_backend_issued_category_id_controls_unparseable_prefix_fallback() -> None:
    category = canonicalize_categories([
        {"category_id": "ppc-24", "label": "***", "count_per_sample": 1, "record_prefix": "", "included": True}
    ])[0]

    assert category["record_prefix"] == "C24"
