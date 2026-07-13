"""Focused freeform family authority validation for TASK_361H."""

from __future__ import annotations

import pytest

from backend.application.contact_measurement_plan_family_validation import (
    ContactMeasurementPlanFamilyValidationError,
    normalize_freeform_prefix,
    validate_contact_measurement_families,
    validate_sibling_freeform_family_authorities,
)


def _family(
    family_id: str,
    prefix: str,
    count: int,
    label: str = "High Power",
) -> dict[str, object]:
    return {
        "family_id": family_id,
        "label": label,
        "count_per_sample": count,
        "record_label": label,
        "record_prefix": prefix,
        "included": True,
        "is_custom": True,
    }


def test_freeform_family_validation_accepts_positive_included_counts() -> None:
    validate_contact_measurement_families(
        (
            _family("ff-llcr-1", "HP", 2),
            _family("ff-llcr-2", "SIG", 1, "Signal"),
        )
    )


@pytest.mark.parametrize(
    ("families", "message"),
    [
        ((_family("ff-llcr-1", "HP", 0),), "positive integer"),
        ((_family("ff-llcr-1", "HP", 1), _family("ff-llcr-2", "hp", 1)), "prefixes must be unique"),
        ((_family("ff-llcr-1", "HP-1", 1),), "uppercase ASCII"),
    ],
)
def test_freeform_family_validation_fails_closed(
    families: tuple[dict[str, object], ...],
    message: str,
) -> None:
    with pytest.raises(ContactMeasurementPlanFamilyValidationError, match=message):
        validate_contact_measurement_families(families)


def test_prefix_normalization_is_ascii_only() -> None:
    assert normalize_freeform_prefix(" hp01 ") == ""
    assert normalize_freeform_prefix("hp01") == "HP01"
    assert normalize_freeform_prefix("ＡＢ12") == "AB12"


@pytest.mark.parametrize(
    ("pending", "siblings", "message"),
    [
        (
            (_family("ff-llcr-4", "HP", 1, "High Power"),),
            [("ff-llcr-4", "High Power", "HPA")],
            "issued family id cannot change",
        ),
        (
            (_family("ff-llcr-5", "SIG", 1, "High Power"),),
            [("ff-llcr-4", " high power ", "HP")],
            "labels must be unique",
        ),
    ],
)
def test_sibling_authority_rejects_semantic_id_and_normalized_label_collisions(
    pending: tuple[dict[str, object], ...],
    siblings: list[tuple[str, str, str]],
    message: str,
) -> None:
    with pytest.raises(ContactMeasurementPlanFamilyValidationError, match=message):
        validate_sibling_freeform_family_authorities(pending, siblings)
