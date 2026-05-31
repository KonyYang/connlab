from __future__ import annotations

from backend.modules.test_plan.spec_section_text_extractor import (
    collect_section_text_blocks,
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
    assert "shall not exceed 0.25 milliohms" in (llcr.requirement or "")
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
