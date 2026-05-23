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


def test_product_spec_matrix_parser_extracts_marker_note_variants() -> None:
    result = ProductSpecMatrixParser().parse_tables(
        [
            [
                ["test Items", "Section", "Group 1"],
                ["Examination", "5.5", "1(a),2,3(b),4(c),5(d),6#"],
            ]
        ],
        paragraphs=[
            "a) C:\\Users\\White\\Desktop\\AI information\\Spec\\GS-12-2113 CoolPower HDF 3.40mm product specification_20251219_Rev7.doc",
            "（b） line with full-width marker",
            "c. line with dotted marker",
            "Note (d): wrapped note marker",
            "# symbol marker note",
        ],
    )

    step_notes_by_raw = {step.raw_token: step.source_note for step in result.groups[0].steps}
    assert step_notes_by_raw["1(a)"] is not None
    assert "GS-12-2113" in step_notes_by_raw["1(a)"]
    assert "Rev7.doc" in step_notes_by_raw["1(a)"]
    assert step_notes_by_raw["3(b)"] == "(b) line with full-width marker"
    assert step_notes_by_raw["4(c)"] == "(c) line with dotted marker"
    assert step_notes_by_raw["5(d)"] == "(d) wrapped note marker"
    assert step_notes_by_raw["6#"] == "# symbol marker note"


def test_product_spec_matrix_parser_does_not_false_match_normal_sentences() -> None:
    result = ProductSpecMatrixParser().parse_tables(
        [
            [
                ["test Items", "Section", "Group 1"],
                ["Durability", "8.11", "3(a)"],
            ]
        ],
        paragraphs=[
            "The document note (a) is provided in attachment.",
            "This line references C:\\temp\\a.doc but is not marker syntax.",
        ],
    )

    assert result.groups[0].steps[0].source_note is None


def test_product_spec_matrix_parser_extracts_digit_prefixed_parenthesis_marker() -> None:
    result = ProductSpecMatrixParser().parse_tables(
        [
            [
                ["test Items", "Section", "Group 1"],
                ["Samples Quantity (PCS)", "", "5+(5e)"],
                ["Durability", "8.11", "3(a)"],
            ]
        ],
        paragraphs=[
            "(a) Precondition specimens with 20 durability cycles;",
            "(e) Test with different 5 samples for solder ability and Resistance to solder heat, respectively",
        ],
    )

    assert result.groups[0].sample_quantity_expression == "5+(5e)"
    assert result.groups[0].sample_note == "(e) Test with different 5 samples for solder ability and Resistance to solder heat, respectively"


def test_product_spec_matrix_parser_prefers_last_contiguous_note_block() -> None:
    result = ProductSpecMatrixParser().parse_tables(
        [
            [
                ["test Items", "Section", "Group 1"],
                ["Durability", "8.11", "3(a)"],
                ["Vibration Random", "8.9", "10(c)"],
                ["Samples Quantity (PCS)", "", "5+(5e)"],
            ]
        ],
        paragraphs=[
            "(a) Precondition Category E Test",
            "(c) Minimum solder coverage: 95 %",
            "Matrix footer notes:",
            "(a) Precondition specimens with 20 durability cycles;",
            "(b) Precondition specimens with 212 hours high temperature life;",
            "(c) Energize at current for 18℃ temperature rise;",
            "(d) 5pcs for LLCR test another 5pcs loose connector for DWV test.",
            "(e) Test with different 5 samples for solder ability and Resistance to solder heat, respectively",
        ],
    )

    notes_by_token = {step.raw_token: step.source_note for step in result.groups[0].steps}
    assert notes_by_token["3(a)"] == "(a) Precondition specimens with 20 durability cycles;"
    assert notes_by_token["10(c)"] == "(c) Energize at current for 18℃ temperature rise;"
    assert result.groups[0].sample_note == "(e) Test with different 5 samples for solder ability and Resistance to solder heat, respectively"


def test_product_spec_matrix_parser_backfills_dropped_word_list_note_labels() -> None:
    result = ProductSpecMatrixParser().parse_tables(
        [
            [
                ["test Items", "Section", "Group 1", "Group 2", "Group 3"],
                ["Examination", "5.5", "1", "1", "1"],
                ["Durability", "8.11", "3(a)", "", ""],
                ["Vibration Random", "8.9", "10(c)", "", ""],
                ["Samples Quantity (PCS)", "", "5+5(d)", "5+(5e)", "3"],
            ]
        ],
        paragraphs=[
            "a. Precondition Category E Test",
            "b. Steam or dry aging 每 4 hours",
            "c. Minimum solder coverage: 95 %",
            "Table 5: Qualification Test Table",
            "Precondition specimens with 20 durability cycles;",
            "Precondition specimens with 212 hours high temperature life;",
            "Energize at current for 18℃ temperature rise;",
            "5pcs for LLCR test another 5pcs loose connector for DWV test.",
            "(e) Test with different 5 samples for solder ability and Resistance to solder heat, respectively",
        ],
    )

    group_1 = result.groups[0]
    notes_by_token = {step.raw_token: step.source_note for step in group_1.steps}
    assert notes_by_token["3(a)"] == "(a) Precondition specimens with 20 durability cycles;"
    assert notes_by_token["10(c)"] == "(c) Energize at current for 18℃ temperature rise;"
    assert group_1.sample_note == "(d) 5pcs for LLCR test another 5pcs loose connector for DWV test."
    assert result.groups[1].sample_note == "(e) Test with different 5 samples for solder ability and Resistance to solder heat, respectively"


def test_product_spec_matrix_parser_restores_standalone_symbol_section_notes() -> None:
    result = ProductSpecMatrixParser().parse_tables(
        [
            [
                ["test Items", "Section", "Group 9"],
                ["CURRENT RATING - Still Air (Power& Signal)", "6.5*", "2"],
                ["CURRENT RATING - Airflow (Power& Signal)", "6.6*", "5"],
            ]
        ],
        paragraphs=[
            "a. Precondition Category E Test",
            "b. Steam or dry aging 每 4 hours",
            "c. Minimum solder coverage: 95 %",
            "*Simultaneously measure power contact resistance.",
        ],
    )

    notes_by_token = {
        step.raw_token: step.source_item_section_note for step in result.groups[0].steps
    }
    assert notes_by_token["2"] == "Section: 6.5* Simultaneously measure power contact resistance."
    assert notes_by_token["5"] == "Section: 6.6* Simultaneously measure power contact resistance."


def test_product_spec_matrix_parser_rejects_test_record_like_table() -> None:
    result = ProductSpecMatrixParser().parse_tables(
        [
            [
                ["Test Item", "Requirement", "Result", "Judgement", "Record"],
                ["1", "As spec", "Pass", "OK", "notes"],
                ["2", "As spec", "Pass", "OK", "notes"],
                ["3", "As spec", "Pass", "OK", "notes"],
            ]
        ]
    )

    assert result.groups == ()
    assert result.selected_table_index is None
    assert "No Matrix table" in result.blockers[0]


def test_product_spec_matrix_parser_rejects_revision_record_table_with_test_words() -> None:
    revision_record = [
        ["REV", "PAGES", "DESCRIPTION", "EC #", "DATE"],
        ["1", "9", "INITIAL RELEASE", "", "09/26/2019"],
        ["2", "ALL", "UPDATED SECTIONS: 8.10 AND 8.11", "", "10/30/2019"],
        ["3", "9", "CORRECTED TABLE 1 TEST GROUP 8 SAMPLE QTY", "", "11/01/2019"],
        ["4", "9", "ADDED PRODUCT PHOTOGRAPH", "", "12/12/2019"],
    ]

    auto_result = ProductSpecMatrixParser().parse_tables([revision_record])
    selected_result = ProductSpecMatrixParser().parse_tables(
        [revision_record],
        selected_table_index=1,
    )

    assert auto_result.groups == ()
    assert auto_result.selected_table_index is None
    assert "No Matrix table" in auto_result.blockers[0]
    assert selected_result.groups == ()
    assert selected_result.selected_table_index is None
    assert selected_result.blockers == ("Selected table 1 is not a valid Matrix table.",)


def test_product_spec_matrix_parser_accepts_numeric_group_headers_with_sample_tail() -> None:
    result = ProductSpecMatrixParser().parse_tables(
        [
            [
                ["Test Item", "Section", "1", "2A", "B"],
                ["Visual Examination", "5.4", "1,2", "1", "1"],
                ["Contact Resistance", "6.1", "3,4", "3", ""],
                ["Samples Quantity (PCS)", "", "5", "3", "2"],
            ]
        ],
        paragraphs=["Table 5: Qualification Test"],
    )

    assert result.blockers == ()
    assert result.selected_table_index == 1
    assert [group.group_label for group in result.groups] == ["1", "2A"]
