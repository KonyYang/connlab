"""Bounded regressions for TASK_368B prefixed Group P headers."""

from backend.modules.test_plan import ProductSpecMatrixParser


def _coolpower_matrix(group_p_header: str = "Group P") -> list[list[str]]:
    """Return a GS-12-1941-shaped fourteen-column qualification Matrix."""
    return [
        [
            "TEST GROUP ID:",
            "TEST GROUP ID:",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6a",
            "6b",
            "7",
            "8",
            "9",
            "10",
            group_p_header,
        ],
        [
            "TEST DESCRIPTION",
            "SECTION",
            "Temp Life",
            "Thermal Shock & Humidity",
            "Vibration & Shock",
            "Mixed Flowing Gas",
            "Dust",
            "Durability",
            "DWV",
            "Salt Spray",
            "Current Rating",
            "Contact Retention Force",
            "Crimp/Wending Tensile Strength",
            "Current Rating, Durability, Contact Retention Force",
        ],
        ["VISUAL EXAMINATION", "7.1", *(["1"] * 11), "1,10"],
        ["Current Rating", "6.1", *(["2"] * 11), "2"],
        ["SAMPLES QUANTITY (PCS)", "", *(["5(a)"] * 11), "3"],
    ]


def test_parser_extracts_prefixed_group_p_with_its_own_final_column_values() -> None:
    """Removing prefixed-letter recognition must drop this final source column."""
    result = ProductSpecMatrixParser().parse_tables(
        [_coolpower_matrix()],
        table_contexts={1: "Qualification Test Table"},
    )

    assert result.blockers == ()
    assert result.selected_table_index == 1
    assert [group.group_label for group in result.groups] == [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6a",
        "6b",
        "7",
        "8",
        "9",
        "10",
        "Group P",
    ]
    group_p = result.groups[-1]
    assert group_p.group_key == "group_p"
    assert [step.raw_token for step in group_p.steps] == ["1", "2", "10"]
    assert group_p.sample_quantity_expression == "3"
    assert group_p.sample_size == 3


def test_group_header_comparison_rejects_phrase_and_preserves_existing_forms() -> None:
    """Broad Group phrases stay excluded while established group forms remain valid."""
    phrase_result = ProductSpecMatrixParser().parse_tables(
        [_coolpower_matrix(group_p_header="Group Purpose")]
    )
    compatibility_table = [
        ["TEST GROUP ID:", "TEST GROUP ID:", "Group 1", "2", "6a"],
        ["TEST DESCRIPTION", "SECTION", "One", "Two", "Six A"],
        ["VISUAL EXAMINATION", "7.1", "1", "2", "3"],
        ["Current Rating", "6.1", "4", "5", "6"],
        ["SAMPLES QUANTITY (PCS)", "", "3", "4", "5"],
    ]
    compatibility_result = ProductSpecMatrixParser().parse_tables(
        [compatibility_table],
        table_contexts={1: "Qualification Test Table"},
    )

    assert "Group Purpose" not in [
        group.group_label for group in phrase_result.groups
    ]
    assert [group.group_label for group in compatibility_result.groups] == [
        "Group 1",
        "2",
        "6a",
    ]
