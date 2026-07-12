import pytest

from backend.application.contact_measurement_plan_identity import (
    ContactMeasurementPlanIdentityError,
    build_impact_identity_key,
    build_target_key,
    parse_target_key,
)


def test_target_key_round_trips_imported_lineage_with_normalized_suffix() -> None:
    key = build_target_key(
        source_group_snapshot_id="source-group-1",
        manual_group_anchor_id=None,
        source_row_snapshot_id="source-row-1",
        manual_row_anchor_id=None,
        step_sequence=2,
        suffix_note=" (A) ",
    )

    assert key == "cmp-target:v1|group:source-group-1|row:source-row-1|step:2|suffix:(a)"
    assert parse_target_key(key).step_suffix_note == "(a)"


def test_target_key_rejects_missing_or_ambiguous_lineage() -> None:
    with pytest.raises(ContactMeasurementPlanIdentityError):
        build_target_key(None, None, "row", None, 1, None)
    with pytest.raises(ContactMeasurementPlanIdentityError):
        build_target_key("group", "manual-group", "row", None, 1, None)


def test_impact_identity_uses_non_null_none_sentinels() -> None:
    assert build_impact_identity_key("structural_review_required", "cmp-candidate:v1|x", None, None) == (
        "cmp-impact:v1|category:structural_review_required|subject:cmp-candidate:v1|x|before:none|after:none"
    )
