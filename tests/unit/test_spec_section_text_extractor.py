from __future__ import annotations

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
