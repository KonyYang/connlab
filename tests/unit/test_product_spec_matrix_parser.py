from __future__ import annotations

from backend.modules.test_plan import ProductSpecMatrixParser


def test_product_spec_matrix_parser_extracts_group_steps() -> None:
    tables = [
        [
            ["unrelated", "table"],
        ],
        [
            ["test Items", "Section", "test sequence", "", ""],
            ["test Items", "Section", "Group 1", "Group 2", "Group 3"],
            ["Examination of Product", "5.4", "1,10", "1,13", ""],
            ["Contact Resistance (Low Level)", "6.1", "2,5,8", "2,5,10", "2"],
        ],
    ]

    result = ProductSpecMatrixParser().parse_tables(tables)

    assert result.selected_table_index == 2
    assert result.blockers == ()
    group_1 = result.groups[0]
    assert group_1.group_key == "group_1"
    assert group_1.group_label == "Group 1"
    assert [step.sequence for step in group_1.steps] == [1, 2, 5, 8, 10]
    assert group_1.steps[0].test_item == "Examination of Product"
    assert group_1.steps[0].source_section == "5.4"
    assert group_1.steps[0].source_table_index == 2
    assert group_1.steps[0].source_row_index == 3
    assert group_1.steps[0].duration_status == "deferred"


def test_product_spec_matrix_parser_reports_missing_matrix() -> None:
    result = ProductSpecMatrixParser().parse_tables(
        [[["Item", "Section"], ["Contact Resistance", "6.1"]]]
    )

    assert result.groups == ()
    assert result.selected_table_index is None
    assert "No Matrix table" in result.blockers[0]


def test_product_spec_matrix_parser_warns_for_malformed_sequence() -> None:
    result = ProductSpecMatrixParser().parse_tables(
        [
            [
                ["test Items", "Section", "Group 1"],
                ["Durability", "7.1", "2,A,5"],
            ]
        ]
    )

    assert [step.sequence for step in result.groups[0].steps] == [2, 5]
    assert "Unrecognized sequence token 'A'" in result.warnings[0]
    assert "Unrecognized sequence token 'A'" in result.groups[0].steps[0].warnings[0]


def test_product_spec_matrix_parser_preserves_duplicate_sequence_warning() -> None:
    result = ProductSpecMatrixParser().parse_tables(
        [
            [
                ["test Items", "Section", "Group 1"],
                ["Examination of Product", "5.4", "1"],
                ["Contact Resistance", "6.1", "1"],
            ]
        ]
    )

    assert [step.sequence for step in result.groups[0].steps] == [1, 1]
    assert "Group 1 has duplicate sequence 1." in result.warnings
