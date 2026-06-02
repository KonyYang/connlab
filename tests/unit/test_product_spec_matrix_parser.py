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


def test_product_spec_matrix_parser_prefills_row_method_condition_requirement() -> None:
    result = ProductSpecMatrixParser().parse_tables(
        [
            [
                ["test Items", "Section", "Group 1"],
                ["Examination of Product", "5.4", "1"],
                ["Contact Resistance (Low Level)", "6.1", "2,5,8"],
                ["Durability", "7.3", "3"],
            ]
        ],
        paragraphs=[
            "5.4 Design and Construction",
            "There shall be no cracks, burrs, or other physical defects that may impair performance.",
            "6.1 Contact Resistance, Low Level (LLCR)",
            "The low level contact resistance shall not exceed 0.25 milliohms initially.",
            "Measurements shall be in accordance with EIA 364-23D using 20mV max, 100mA max.",
            "7.3 Durability",
            "Durability shall be tested in accordance with EIA-364-09D.",
        ],
    )

    visual = result.rows[0]
    llcr = result.rows[1]
    durability = result.rows[2]
    assert visual.method == "EIA-364-18B"
    assert visual.condition == "10x min magnification"
    assert visual.requirement == "No detrimental condition"
    assert visual.detail_extraction_status == "matched"
    assert llcr.method == "EIA-364-23D"
    assert llcr.condition == "20mV max, 100mA max"
    assert llcr.requirement == "Initial ≤ 0.25mΩ"
    assert llcr.detail_extraction_status == "matched"
    assert durability.method == "EIA-364-09D"
    assert durability.condition is None
    assert durability.requirement == "No damage"
    assert durability.detail_extraction_status == "partial"


def test_product_spec_matrix_parser_applies_family_aware_details_on_real_path() -> None:
    result = ProductSpecMatrixParser().parse_tables(
        [
            [
                ["test Items", "Section", "Group 1"],
                ["Temperature rise", "6.3.1", "1"],
                ["Cycling Temperature& Humidity", "8.2", "2"],
                ["MFG", "8.6", "3"],
                ["Dust exposure", "8.7", "4"],
                ["Random Vibration", "8.8", "5"],
                ["Mechanical Shock", "8.9", "6"],
            ]
        ],
        paragraphs=[
            "6.3.1 Temperature rise",
            "Method 2 is used at 75A. Temperature rise shall not exceed 30 C.",
            "8.2 Cyclic Temperature and Humidity –EIA 364-31 and EIA 364-1000.",
            "temperature 25 ± 3 C at 80 ± 5% RH and 65 ± 3 C at 50 ± 5% RH.",
            "Duration 24 cycles. Dwell time 1.0 hour; ramp time 30 minutes.",
            "Maximum Change: 0.17 mΩ.",
            "8.6 Mixed Flowing Gas corrosion (MFG) –EIA 364-65 and EIA-364-1000.",
            "Class IIA. Duration - 224 hours unmated, 112 hours mated.",
            "8.7 Dust exposure –EIA-364-91.",
            "Benign Dust Composition. Maximum Change: 0.17 mΩ.",
            "8.8 Vibration (Random) –EIA 364-28.",
            "Condition VIID, 15 minutes each axis. No discontinuities greater than 1 us.",
            "8.9 Mechanical Shock – EIA 364-27.",
            "Condition A (50G, 11 millisecond). No discontinuities greater than 1 us.",
        ],
    )

    temperature = result.rows[0]
    humidity = result.rows[1]
    mfg = result.rows[2]
    dust = result.rows[3]
    vibration = result.rows[4]
    shock = result.rows[5]
    assert temperature.method == "EIA-364-70"
    assert temperature.requirement == "≤ 30 ℃"
    assert humidity.method == "EIA-364-31"
    assert "31 a" not in (humidity.condition or "").lower()
    assert humidity.requirement == "No damage"
    assert mfg.method == "EIA-364-65"
    assert "65 a" not in (mfg.condition or "").lower()
    assert "class iia" in (mfg.condition or "").lower()
    assert mfg.requirement == "No damage"
    assert dust.requirement == "No damage"
    assert vibration.requirement == "No damage, No discontinuity >1us"
    assert shock.requirement == "No damage, No discontinuity >1us"


def test_product_spec_matrix_parser_matches_symbol_marked_and_multi_sections() -> None:
    result = ProductSpecMatrixParser().parse_tables(
        [
            [
                ["test Items", "Section", "Group 1"],
                ["Visual Examination", "5.4, 9.2", "1"],
                ["Current Rating Still Air", "6.5*", "2"],
                ["Current Rating Airflow", "#6.6&", "3"],
            ]
        ],
        paragraphs=[
            "5.4 Design and Construction",
            "Connectors shall meet the applicable drawing.",
            "9.2 Inspection Conditions",
            "Inspections shall be performed in accordance with EIA 364-18.",
            "6.5 Current Rating Still Air",
            "The temperature rise shall not exceed 40C with reference to EIA 364-70.",
            "6.6 Current Rating Airflow",
            "The temperature rise shall not exceed 40C with reference to EIA 364-70.",
        ],
    )

    visual = result.rows[0]
    still_air = result.rows[1]
    airflow = result.rows[2]
    assert visual.method == "EIA-364-18"
    assert visual.detail_extraction_source_section == "9.2"
    assert still_air.method == "EIA-364-70"
    assert still_air.detail_extraction_source_section == "6.5"
    assert airflow.method == "EIA-364-70"
    assert airflow.detail_extraction_source_section == "6.6"


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


def test_product_spec_matrix_parser_accepts_uscar_sequence_matrix_layout() -> None:
    result = ProductSpecMatrixParser().parse_tables(
        [
            [
                ["", "Test name", "Test name", "Vibration", "Humidity", "Salt Spray"],
                ["", "Test Sequence ID", "Test Sequence ID", "H", "J", "M"],
                ["", "Sample Size minimum", "Connector", "3", "3", "3"],
                ["", "Applicable Cable Size", "Applicable Cable Size", "2*4-0AWG", "2*4-0AWG", "2*4-0AWG"],
                ["5.5", "Visual Inspection", "Visual Inspection", "1,9", "1,8", "1,6"],
                ["6.1", "Circuit Continuity Monitoring", "Circuit Continuity Monitoring", "5 (1)", "", ""],
                ["8.8&8.9", "Vibration/ Mechanical Shock", "Vibration/ Mechanical Shock", "4 (1)", "", ""],
                ["8.15", "Supplemental salt spray", "Supplemental salt spray", "", "", "4(3)"],
            ],
            [["Rev", "Page", "Description", "Date"], ["1", "all", "release", "2025"]],
        ],
        paragraphs=[
            "9.8 Refer to USCAR-2 , Additional Testing",
            "(1) Circuit continuity monitoring is performed during conditioning.",
            "(2) T-rise 55C max, after treatment.",
            "(3) Frontal end of cable needs to be sealed.",
        ],
    )

    assert result.selected_table_index == 1
    assert [group.group_label for group in result.groups] == ["H", "J", "M"]
    assert result.groups[0].sample_size == 3
    assert result.groups[0].sample_quantity_expression == "3"
    assert [step.raw_token for step in result.groups[0].steps] == ["1", "4 (1)", "5 (1)", "9"]
    assert result.groups[0].steps[0].test_item == "Visual Inspection"
    assert result.groups[0].steps[0].source_section == "5.5"
    notes_by_raw = {step.raw_token: step.source_note for step in result.groups[0].steps}
    assert notes_by_raw["4 (1)"] == "(1) Circuit continuity monitoring is performed during conditioning."


def test_product_spec_matrix_parser_accepts_loose_sequence_matrix_headers() -> None:
    result = ProductSpecMatrixParser().parse_tables(
        [
            [
                ["", "Test Item", "Test Item", "Group A", "Group B"],
                ["", "Test Group", "Test Group", "Alpha", "Beta"],
                ["", "Minimum Sample", "Connector", "4 pcs", "5 pcs"],
                ["5.5", "Visual Inspection", "Visual Inspection", "1", "1"],
                ["6.2", "Voltage Drop", "Voltage Drop", "2", "2"],
            ],
            [
                ["", "Test Item", "Test Item", "Group C", "Group D"],
                ["", "Test Group", "Test Group", "Gamma", "Delta"],
                ["", "Minimum Sample", "Connector", "3 pcs", "3 pcs"],
                ["5.5", "Visual Inspection", "Visual Inspection", "1", "1"],
                ["6.2", "Voltage Drop", "Voltage Drop", "2", "2"],
            ],
        ],
        paragraphs=["9.8 Additional Test Matrix"],
        table_contexts={1: "Reference table", 2: "Additional Test Matrix"},
    )

    assert result.selected_table_index == 2
    assert [group.group_label for group in result.groups] == ["Gamma", "Delta"]
    assert result.groups[0].sample_quantity_expression == "3 pcs"
    assert [step.raw_token for step in result.groups[0].steps] == ["1", "2"]


def test_product_spec_matrix_parser_applies_template_fallback_without_overriding_extracted_method() -> None:
    result = ProductSpecMatrixParser().parse_tables(
        [
            [
                ["test Items", "Section", "Group 1"],
                ["MFG", "8.6", "1"],
                ["Visual Inspection", "5.4", "2"],
            ]
        ],
        paragraphs=[
            "8.6 Mixed Flowing Gas corrosion",
            "Class IIA. Duration - 224 hours unmated, 112 hours mated.",
            "5.4 Design and Construction",
            "Inspection shall be performed in accordance with IEC 60512-1-1.",
        ],
    )

    mfg = result.rows[0]
    visual = result.rows[1]
    assert mfg.method == "EIA-364-65"
    assert "template-fallback-method" in mfg.detail_extraction_notes
    assert visual.method == "IEC 60512-1-1"
    assert "template-fallback-method" not in visual.detail_extraction_notes


def test_product_spec_matrix_parser_applies_no_section_fallback_for_manual_rows() -> None:
    result = ProductSpecMatrixParser().parse_tables(
        [
            [
                ["test Items", "Section", "Group 1"],
                ["Visual Examination", "", "1"],
                ["Contact Resistance (Low Level)", "", "2"],
                ["Mating/Un-mating Force", "", "3"],
            ]
        ],
        paragraphs=["5. TEST METHODS/REQUIREMENTS"],
    )

    visual = result.rows[0]
    llcr = result.rows[1]
    mating = result.rows[2]
    assert visual.method == "EIA-364-18B"
    assert visual.condition == "10x min magnification"
    assert visual.requirement == "No detrimental condition"
    assert llcr.method == "EIA-364-23"
    assert llcr.requirement is None
    assert mating.requirement is None
