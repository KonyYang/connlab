from __future__ import annotations

import pytest

from backend.modules.test_plan.spec_section_text_extractor import (
    collect_section_text_blocks,
    extract_row_details,
    extract_row_details_by_section,
)


def test_extract_row_details_by_section_extracts_llcr_mcr() -> None:
    details = extract_row_details_by_section(
        [
            "6.1 Contact Resistance, Low Level (LLCR)",
            "The low level contact resistance shall not exceed 0.25 milliohms initially and maximum change is 0.17 milliohms after treatment.",
            "Measurements shall be in accordance with EIA 364-23D using 20mV max, 100mA max.",
            "6.2 Contact Resistance, Specified Current",
            "Voltage drop shall not exceed 15mV. Measurements shall be in accordance with EIA-364-06C.",
        ]
    )

    llcr = details["6.1"]
    assert llcr.method == "EIA-364-23D"
    assert llcr.condition == "20mV max, 100mA max"
    assert llcr.requirement == "Initial ≤ 0.25 mΩ; ΔR ≤ 0.17 mΩ"
    assert llcr.status == "matched"
    assert details["6.2"].condition is None
    assert details["6.2"].requirement == "shall not exceed 15mV"


def test_extract_row_details_does_not_parse_section_title_as_condition() -> None:
    details = extract_row_details_by_section(
        [
            "6.1 Contact Resistance, Low Level (LLCR)",
            "Measurements shall be in accordance with EIA 364-23D.",
            "6.2 Contact Resistance, Specified Current",
            "Voltage drop shall not exceed 0.5mV. Measurements shall be in accordance with EIA-364-06C.",
        ]
    )

    assert details["6.1"].condition is None
    assert details["6.2"].condition is None
    assert details["6.2"].requirement == "shall not exceed 0.5mV"


def test_llcr_condition_defaults_when_source_has_no_measurement_condition() -> None:
    detail = extract_row_details(
        section="6.1",
        section_text="6.1 LLCR. Measurements shall be in accordance with EIA 364-23D.",
        test_item="LLCR",
    )

    assert detail.condition == "20 mV, 100 mA"


@pytest.mark.parametrize(
    ("test_item", "section_text", "expected_condition"),
    [
        (
            "INSULATION RESISTANCE",
            (
                "6.2 Insulation Resistance. a. Test Voltage \u6bcf 500 volts DC. "
                "Electrification Time - 2 minutes."
            ),
            "500VDC, 2 minutes",
        ),
        (
            "DIELECTRIC WITHSTANDING VOLTAGE",
            (
                "6.3 Dielectric Withstanding Voltage. "
                "a. Test Voltage - 1500 volts AC for power contact. "
                "Test Duration - 60 seconds. There shall be no evidence of "
                "arc-over or excessive leakage current >1mA."
            ),
            "1500VAC, 60 seconds",
        ),
    ],
)
def test_ir_and_dwv_condition_extracts_test_voltage(
    test_item: str,
    section_text: str,
    expected_condition: str,
) -> None:
    detail = extract_row_details(
        section="6.2",
        section_text=section_text,
        test_item=test_item,
    )

    assert detail.condition == expected_condition


def test_ir_condition_preserves_explicit_voltage_when_duration_is_missing() -> None:
    detail = extract_row_details(
        section="6.2",
        section_text="6.2 Insulation Resistance. Test Voltage - 500 volts DC.",
        test_item="INSULATION RESISTANCE",
    )

    assert detail.condition == "500VDC"


def test_dwv_condition_keeps_leakage_current_in_requirement() -> None:
    detail = extract_row_details(
        section="6.3",
        section_text=(
            "6.3 Dielectric Withstanding Voltage. "
            "Test Voltage - 1500 volts AC. Test Duration - 60 seconds. "
            "There shall be no evidence of arc-over, insulation breakdown, or "
            "excessive leakage current >1mA."
        ),
        test_item="DIELECTRIC WITHSTANDING VOLTAGE",
    )

    assert detail.condition == "1500VAC, 60 seconds"
    assert detail.requirement == (
        "No evidence of arc-over, insulation breakdown, or leakage current >1mA"
    )


def test_extract_row_details_supports_uscar_j_std_and_iec_methods() -> None:
    details = extract_row_details_by_section(
        [
            "7.3 Crimping tensile strength",
            "The force shall be tested per SAE/USCAR-21 section 4.4.5.",
            "7.4 Connector cycling - USCAR-2_5.1.9",
            "Method of connection refers to USCAR-2_5.1.9.",
            "7.5 Dielectric Withstanding Voltage",
            "There shall be no breakdown when tested in accordance USCAR-37_5.5.2.",
            "8.8 Solderability - EIA/IPC/JEDEC J-STD-002E",
            "Use Test Condition A.",
            "8.9 Visual Inspection - IEC 60512-1-1",
            "Visual examination according to IEC 60512-1-1 shall be carried out with 10x magnification.",
            "9.1 Cable clamp resistance to cable pull - IEC61984_6.17",
            "Cable pull is tested with 200N.",
            "9.2 IPX7 - IEC60529 14.2.7",
            "No water shall enter the connector.",
            "9.3 Impulse withstand voltage - IEC61984",
            "Impulse withstand voltage shall be tested according to Clause 7.3.12 of IEC 61984.",
            "9.4 Protection against electric shock - IEC60529",
            "Test according to Clause 5 of IEC 60529.",
            "9.5 Ball pressure test_IEC60695-10-2",
            "Use test temperature 80C.",
        ]
    )

    assert details["7.3"].method == "USCAR-21 4.4.5"
    assert details["7.4"].method == "USCAR-2 5.1.9"
    assert details["7.5"].method == "USCAR-37 5.5.2"
    assert details["8.8"].method == "J-STD-002E"
    assert details["8.9"].method == "IEC 60512-1-1"
    assert details["9.1"].method == "IEC 61984 6.17"
    assert details["9.2"].method == "IEC 60529 14.2.7"
    assert details["9.3"].method == "IEC 61984 7.3.12"
    assert details["9.4"].method == "IEC 60529 5"
    assert details["9.5"].method == "IEC 60695-10-2"


def test_collect_section_text_blocks_uses_exact_section_boundaries() -> None:
    blocks = collect_section_text_blocks(
        [
            "6.1 Contact Resistance",
            "Section 6.1 body.",
            "6.2 Specified Current",
            "Section 6.2 body.",
        ]
    )

    assert blocks["6.1"] == "6.1 Contact Resistance Section 6.1 body."
    assert blocks["6.2"] == "6.2 Specified Current Section 6.2 body."


def test_visual_family_default_is_applied_without_explicit_conflict() -> None:
    detail = extract_row_details(
        section="5.4",
        section_text=(
            "5.4 Design and Construction Connectors shall be of the design and construction "
            "specified on applicable drawings. There shall be no cracks, burrs, or other physical "
            "defects that may impair performance."
        ),
        test_item="Examination of Product",
    )

    assert detail.method == "EIA-364-18B"
    assert detail.condition == "10x min magnification"
    assert detail.requirement == "No detrimental condition"
    assert detail.status == "matched"


def test_visual_family_default_does_not_override_explicit_method() -> None:
    detail = extract_row_details(
        section="5.4",
        section_text=(
            "5.4 Visual Examination. Inspection shall be performed in accordance with IEC 60512-1-1. "
            "There shall be no defects."
        ),
        test_item="Visual Inspection",
    )

    assert detail.method == "IEC 60512-1-1"
    assert detail.condition == "10x min magnification"
    assert detail.requirement == "No detrimental condition"


def test_temperature_humidity_extraction_does_not_emit_numeric_letter_fragment() -> None:
    detail = extract_row_details(
        section="8.2",
        section_text=(
            "8.2 Cyclic Temperature and Humidity –EIA 364-31 and EIA 364-1000. "
            "temperature 25 ± 3 C at 80 ± 5% RH and 65 ± 3 C at 50 ± 5% RH. "
            "Duration 24 cycles. Dwell time 1.0 hour; ramp time 30 minutes. "
            "Maximum Change: 0.17 mΩ."
        ),
        test_item="Cycling Temperature& Humidity",
    )

    assert detail.method == "EIA-364-31"
    assert detail.condition is not None
    assert "31 a" not in (detail.condition or "").lower()
    assert detail.requirement is not None
    assert detail.requirement != "Maximum Change: 0"
    assert detail.requirement == "No damage"


def test_mfg_extraction_does_not_emit_numeric_letter_fragment() -> None:
    detail = extract_row_details(
        section="8.6",
        section_text=(
            "8.6 Mixed Flowing Gas corrosion (MFG) –EIA 364-65 and EIA-364-1000. "
            "Class IIA. Duration - 224 hours unmated, 112 hours mated. "
            "Maximum Change: 0.17 mΩ."
        ),
        test_item="MFG",
    )

    assert detail.method == "EIA-364-65"
    assert detail.condition is not None
    assert "65 a" not in (detail.condition or "").lower()
    assert "Class IIA" in (detail.condition or "")
    assert detail.requirement is not None
    assert detail.requirement != "Maximum Change: 0"
    assert detail.requirement == "No damage"


@pytest.mark.parametrize("test_item", ["Temperature rise (Post MFG Samples)", "T-rise (Post MFG Samples)"])
def test_temperature_rise_condition_extracts_first_test_current(test_item: str) -> None:
    detail = extract_row_details(
        section="6.3.1",
        section_text=(
            "6.3.1 Temperature rise. The temperature rise shall not exceed 30 C "
            "when all contacts are powered at 75A."
        ),
        test_item=test_item,
    )

    assert detail.condition == "75 A"


def test_temperature_rise_uses_current_placeholder_when_current_is_missing() -> None:
    detail = extract_row_details(
        section="6.3.1",
        section_text="6.3.1 Temperature rise. The temperature rise shall not exceed 30 C.",
        test_item="Temperature rise",
    )

    assert detail.condition == "A"


def test_normal_force_extracts_minimum_requirement() -> None:
    detail = extract_row_details(
        section="7.7",
        section_text=(
            "7.7 Normal Force. The minimum normal force is not less than 1.5N "
            "per beam. The following details shall apply: Reference - EIA-364-04."
        ),
        test_item="Normal Force",
    )

    assert detail.method == "EIA-364-04"
    assert detail.condition == "mm/min"
    assert detail.requirement == "≥ 1.5 N per beam"


@pytest.mark.parametrize(
    ("section", "cycles", "speed_text"),
    [
        ("7.2", "20", "Cycling Rate - less than 10 cycles per minute."),
        ("7.3", "200", "Cycling Rate - less than 10 cycles per minute."),
        ("7.3", "200", "Displacement Speed - 25.4 mm/min."),
    ],
)
def test_durability_condition_extracts_cycles_and_reviewable_speed(
    section: str,
    cycles: str,
    speed_text: str,
) -> None:
    detail = extract_row_details(
        section=section,
        section_text=(
            f"{section} Durability. Number Cycles - {cycles} cycles. "
            f"{speed_text} No damage."
        ),
        test_item="Durability",
    )

    expected_speed = "25.4 mm/min" if "25.4" in speed_text else "mm/min"
    assert detail.condition == f"{cycles} cycles, {expected_speed}"
    assert detail.requirement == "No damage"


@pytest.mark.parametrize(
    ("speed_text", "expected_speed"),
    [
        ("Displacement Speed - 25.4±6 mm max per minute.", "25.4 mm/min"),
        ("Displacement Speed - mm max per minute.", "mm/min"),
    ],
)
def test_offset_mating_force_extracts_repetitions_speed_and_requirement(
    speed_text: str,
    expected_speed: str,
) -> None:
    detail = extract_row_details(
        section="7.4",
        section_text=(
            "7.4 Offset mating insertion force into floater. "
            "The offset mating insertion force is no more than 60N. "
            "Mate and un-mate receptacle male power pin 10 times in the offset position. "
            f"{speed_text} Reference EIA-364-37."
        ),
        test_item="Offset mating insertion force into floater",
    )

    assert detail.condition == f"10 times, {expected_speed}"
    assert detail.requirement == "≤ 60 N"


@pytest.mark.parametrize(
    ("section_text", "expected_condition", "expected_requirement"),
    [
        (
            "The displacement force is not less than 10N and no more than 40N. "
            "Displacement Speed - 25.4±6 mm per minute.",
            "25.4 mm/min",
            "10 N ≤ Displacement Force ≤ 40 N",
        ),
        (
            "The displacement force is not less than N and no more than N. "
            "Displacement Speed - mm per minute.",
            "mm/min",
            "N",
        ),
    ],
)
def test_floater_displacement_force_extracts_speed_and_force_limits(
    section_text: str,
    expected_condition: str | None,
    expected_requirement: str | None,
) -> None:
    detail = extract_row_details(
        section="7.4",
        section_text=f"7.4 Floater Displacement Force (Side Force). {section_text}",
        test_item="Floater Displacement Force (Side Force)",
    )

    assert detail.condition == expected_condition
    assert detail.requirement == expected_requirement


@pytest.mark.parametrize(
    ("speed_text", "expected_condition"),
    [
        ("Cross Head Speed - 25.4±6 mm per minute.", "25.4 mm/min"),
        ("Cross Head Speed - mm per minute.", "mm/min"),
    ],
)
def test_mating_force_extracts_numeric_cross_head_speed(
    speed_text: str,
    expected_condition: str | None,
) -> None:
    detail = extract_row_details(
        section="7.1",
        section_text=f"7.1 Mating/Un-mating Force. {speed_text}",
        test_item="Mating/Un-mating Force",
    )

    assert detail.condition == expected_condition


def test_terminal_extraction_force_extracts_speed_and_minimum_force() -> None:
    detail = extract_row_details(
        section="7.6",
        section_text=(
            "7.6 Terminal extraction force. The minimum extraction force of a terminal "
            "from barrel is 150N. Cross Head Speed - 50mm max per minute."
        ),
        test_item="Terminal extraction force",
    )

    assert detail.condition == "50 mm/min"
    assert detail.requirement == "≥ 150 N"


@pytest.mark.parametrize(
    ("speed_text", "expected_condition"),
    [
        ("Displacement Speed - 25.4±6 mm per minute.", "25.4 mm/min"),
        ("Displacement Speed - mm per minute.", "mm/min"),
    ],
)
def test_normal_force_extracts_reviewable_displacement_speed(
    speed_text: str,
    expected_condition: str,
) -> None:
    detail = extract_row_details(
        section="7.7",
        section_text=(
            "7.7 Normal Force. The minimum normal force is not less than 1.5N per beam. "
            f"{speed_text} Reference EIA-364-04."
        ),
        test_item="Normal Force",
    )

    assert detail.condition == expected_condition
    assert detail.requirement == "≥ 1.5 N per beam"


@pytest.mark.parametrize(
    "test_item",
    [
        "Floater Displacement Force (Side Force)",
        "Terminal extraction force",
        "Latch Retention Force",
    ],
)
def test_force_family_uses_review_placeholders_when_values_are_missing(
    test_item: str,
) -> None:
    detail = extract_row_details(
        section="7.9",
        section_text="7.9 Placeholder section without numeric test details.",
        test_item=test_item,
    )

    assert detail.condition == "mm/min"
    assert detail.requirement == "N"


def test_force_family_rejects_label_only_speed_as_a_condition() -> None:
    detail = extract_row_details(
        section="7.5",
        section_text="7.5 Lateral Force. Cross Head Speed -.",
        test_item="Lateral Force",
    )

    assert detail.condition == "mm/min"
    assert detail.requirement == "N"


def test_explicit_mating_unmating_pair_without_force_uses_review_placeholders() -> None:
    detail = extract_row_details(
        section="7.1",
        section_text="7.1 Mating/Un-mating. Test details require operator review.",
        test_item="Mating/Un-mating",
    )

    assert detail.condition == "mm/min"
    assert detail.requirement == "N"


@pytest.mark.parametrize("test_item", ["Mating cycles", "Un-mating cycles", "Unmating cycles"])
def test_single_mating_concept_non_force_family_does_not_receive_force_placeholders(
    test_item: str,
) -> None:
    detail = extract_row_details(
        section="7.3",
        section_text=f"7.3 {test_item}. Test details require operator review.",
        test_item=test_item,
    )

    assert detail.condition is None
    assert detail.requirement is None


def test_force_family_preserves_meaningful_no_damage_requirement() -> None:
    detail = extract_row_details(
        section="7.4",
        section_text="7.4 Lateral Force. Cross Head Speed -. No damage.",
        test_item="Lateral Force",
    )

    assert detail.condition == "mm/min"
    assert detail.requirement == "No damage."


def test_force_family_preserves_specialized_composite_condition() -> None:
    detail = extract_row_details(
        section="7.4",
        section_text=(
            "7.4 Offset mating insertion force into floater. "
            "Mate and un-mate receptacle male power pin 10 times. "
            "Displacement Speed - mm per minute."
        ),
        test_item="Offset mating insertion force into floater",
    )

    assert detail.condition == "10 times, mm/min"
    assert detail.requirement == "N"


@pytest.mark.parametrize(
    ("section_text", "expected_condition"),
    [
        (
            "8.7 Dust exposure - EIA-364-91. Benign Dust Composition. Duration - 1 hour.",
            "Benign dust composition 1#, 1 hour, unmated for both connectors",
        ),
        (
            "8.7 Dust exposure - EIA-364-91. Benign Dust Composition 2#. Duration - 1 hour.",
            "Benign dust composition 2#, 1 hour, unmated for both connectors",
        ),
        (
            "8.7 Dust exposure - EIA-364-91. Benign Dust Composition 2#. "
            "Duration - 1 hour, unmated only Receptacle.",
            "Benign dust composition 2#, 1 hour",
        ),
    ],
)
def test_dust_exposure_condition_uses_report_default_and_preserves_ambiguity(
    section_text: str,
    expected_condition: str,
) -> None:
    detail = extract_row_details(
        section="8.7",
        section_text=section_text,
        test_item="Dust exposure",
    )

    assert detail.condition == expected_condition


def test_current_rating_uses_temperature_rise_defaults() -> None:
    detail = extract_row_details(
        section="6.5",
        section_text=(
            "6.5 Current Rating. The temperature rise shall not exceed 30 C "
            "when all contacts are powered at 75A."
        ),
        test_item="Current Rating",
    )

    assert detail.condition == "75 A"
    assert detail.requirement == "≤ 30 ℃"


def test_current_rating_matches_temperature_rise_when_current_is_missing() -> None:
    detail = extract_row_details(
        section="6.5",
        section_text="6.5 Current Rating. The temperature rise shall not exceed 30 deg C.",
        test_item="Current Rating",
    )

    assert detail.condition == "A"
    assert detail.requirement == "≤ 30 ℃"


def test_family_coverage_safe_outputs() -> None:
    cases = [
        (
            "6.3.1",
            "Temperature rise",
            "6.3.1 Temperature rise. Method 2, 75A. Temperature rise shall not exceed 30 C.",
            "EIA-364-70",
            "≤ 30 ℃",
        ),
        (
            "7.1",
            "Mating/Un-mating Force",
            "7.1 Mating/Un-mating Force. Measurements shall be in accordance with EIA-364-37C. "
            "Cross Head Speed 25.4mm/min. Mating force shall not exceed 20N.",
            "EIA-364-37C",
            None,
        ),
        (
            "7.3",
            "Durability",
            "7.3 Durability. Number Cycles - 200 cycles. Cycling Rate less than 10 cycles per minute.",
            None,
            "No damage",
        ),
        (
            "7.8",
            "Reseating",
            "7.8 Reseating. Manually mating/un-mating the pin and socket, perform 3 such cycles, after mechanical/environmental exposure.",
            "Applicable Specifications 7.8",
            "No damage",
        ),
        (
            "8.1",
            "Thermal Shock",
            "8.1 Thermal Shock –EIA 364-32. Number of cycles - 10 cycles. Temperature range -55 to +85 C.",
            "EIA-364-32",
            "No damage",
        ),
        (
            "8.4",
            "High temperature Life",
            "8.4 High Temperature Life –EIA 364-17. Test Temperature 125 C. Test Duration 114 hours.",
            "EIA-364-17",
            "No damage",
        ),
        (
            "8.5",
            "Thermal Disturbance",
            "8.5 Thermal Disturbance –EIA 364-110. Number of cycles 10. Ramps minimum 2 C per minute.",
            "EIA-364-110",
            "No damage",
        ),
        (
            "8.7",
            "Dust exposure",
            "8.7 Dust exposure –EIA-364-91. Benign Dust Composition. Maximum Change: 0.17 mΩ.",
            "EIA-364-91",
            "No damage",
        ),
        (
            "8.8",
            "Random Vibration",
            "8.8 Vibration (Random) –EIA 364-28. Condition VIID, 15 minutes each axis. "
            "No discontinuities greater than 1 us.",
            "EIA-364-28",
            "No damage, No discontinuity >1us",
        ),
        (
            "8.9",
            "Mechanical Shock",
            "8.9 Mechanical Shock – EIA 364-27. Condition A (50G, 11 millisecond). "
            "3 shocks in both directions along each axis. No discontinuities greater than 1 us.",
            "EIA-364-27",
            "No damage, No discontinuity >1us",
        ),
    ]
    for section, test_item, text, expected_method, expected_requirement in cases:
        detail = extract_row_details(section=section, section_text=text, test_item=test_item)
        if expected_method:
            assert detail.method == expected_method
        # Family coverage minimum: no known malformed fragments.
        condition = (detail.condition or "").lower()
        requirement = detail.requirement or ""
        assert "31 a" not in condition
        assert "65 a" not in condition
        assert requirement != "Maximum Change: 0"
        if expected_requirement:
            assert requirement == expected_requirement


def test_reseating_uses_section_specific_default_details() -> None:
    detail = extract_row_details(
        section="7.8",
        section_text=(
            "7.8 Reseating. Manually mating/un-mating the pin and socket, "
            "perform 3 such cycles, after mechanical/environmental exposure."
        ),
        test_item="Reseating",
    )

    assert detail.method == "Applicable Specifications 7.8"
    assert detail.condition == "Manual 3 cycles"
    assert detail.requirement == "No damage"
    assert detail.status == "matched"


def test_reseating_uses_basic_information_specification_for_method() -> None:
    detail = extract_row_details(
        section="7.8",
        section_text=(
            "7.8 Reseating. Manually mating/un-mating the pin and socket, "
            "perform 3 such cycles, after mechanical/environmental exposure."
        ),
        test_item="Reseating",
        applicable_specifications="EIA-364-37",
    )

    assert detail.method == "EIA-364-37 7.8"
    assert detail.condition == "Manual 3 cycles"
    assert detail.requirement == "No damage"


def test_template_fallback_applies_only_to_empty_fields() -> None:
    fallback = extract_row_details(
        section="7.3",
        section_text="7.3 Durability. Number Cycles - 200 cycles.",
        test_item="Durability",
    )
    assert fallback.method == "EIA-364-09"
    assert "template-fallback-method" in fallback.notes

    non_override = extract_row_details(
        section="5.4",
        section_text=(
            "5.4 Visual Examination. Inspection shall be performed in accordance with IEC 60512-1-1. "
            "No cracks are allowed."
        ),
        test_item="Visual Inspection",
    )
    assert non_override.method == "IEC 60512-1-1"
    assert "template-fallback-method" not in non_override.notes


def test_no_section_fallback_applies_only_to_allowed_empty_fields() -> None:
    visual = extract_row_details(
        section="",
        section_text="",
        test_item="Visual Examination",
    )
    assert visual.method == "EIA-364-18B"
    assert visual.condition == "10x min magnification"
    assert visual.requirement == "No detrimental condition"

    llcr = extract_row_details(
        section="",
        section_text="",
        test_item="Contact Resistance (Low Level)",
    )
    assert llcr.method == "EIA-364-23"
    assert llcr.condition is None
    assert llcr.requirement is None

    unsupported = extract_row_details(
        section="",
        section_text="",
        test_item="Custom Unsupported Test",
    )
    assert unsupported.method is None
    assert unsupported.condition is None
    assert unsupported.requirement is None
