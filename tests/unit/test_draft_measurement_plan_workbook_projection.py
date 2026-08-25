from backend.application.draft_measurement_plan_workbook_projection import (
    build_draft_measurement_plan_workbook_projection,
)


def test_ready_editable_plan_builds_draft_projection_and_fingerprint() -> None:
    projection = build_draft_measurement_plan_workbook_projection(_workspace())

    assert projection.status == "ready"
    assert projection.output_label == "DRAFT"
    assert projection.preview_fingerprint
    assert projection.row_count == 4
    assert projection.sections[0].rows[0].contact_id == "HP1"


def test_review_required_plan_remains_generateable_with_review_label() -> None:
    workspace = _workspace()
    workspace["impacts"] = [{"severity": "review_required", "resolution_state": "open"}]

    projection = build_draft_measurement_plan_workbook_projection(workspace)

    assert projection.status == "review_required"
    assert projection.output_label == "NEEDS REVIEW"
    assert projection.preview_fingerprint


def test_footnoted_sample_quantity_builds_draft_projection() -> None:
    workspace = _workspace()
    workspace["targets"][0]["sample_quantity_expression"] = "3(a)"

    projection = build_draft_measurement_plan_workbook_projection(workspace)

    assert projection.status == "ready"
    assert projection.sections[0].sample_count == 3
    assert projection.row_count == 6


def test_empty_or_invalid_draft_has_no_fingerprint_or_sections() -> None:
    empty = _workspace()
    empty["targets"][0]["included"] = False
    invalid = _workspace()
    invalid["targets"][0]["families"][0]["count_per_sample"] = 1.5

    assert build_draft_measurement_plan_workbook_projection(empty).status == "empty"
    blocked = build_draft_measurement_plan_workbook_projection(invalid)
    assert blocked.status == "blocked"
    assert blocked.preview_fingerprint is None
    assert blocked.sections == ()


def _workspace() -> dict[str, object]:
    return {
        "project_id": "P-1",
        "editable_revision_id": "draft-1",
        "editable_revision_state": "draft",
        "editable_revision_fingerprint": "revision-fingerprint",
        "revision": {"revision_id": "draft-1", "revision_sequence": 2, "state": "draft", "fingerprint": "revision-fingerprint"},
        "matrix_binding": {
            "base_confirmed_matrix_id": "matrix-1",
            "base_matrix_revision": 4,
            "matrix_binding_fingerprint": "matrix-fingerprint",
        },
        "targets": [{
            "stable_target_key": "cmp-target:v1|group:g-1|row:r-1|step:1|suffix:",
            "group_label": "Group A",
            "test_item": "LLCR",
            "contact_kind": "llcr",
            "step_sequence": 1,
            "step_suffix_note": "",
            "sample_quantity_expression": "2",
            "eligible": True,
            "included": True,
            "readings_per_sample": 2,
            "families": [{
                "family_id": "hp",
                "label": "High Power",
                "count_per_sample": 2,
                "record_label": "High Power",
                "record_prefix": "HP",
                "included": True,
            }],
        }],
        "impacts": [],
    }
