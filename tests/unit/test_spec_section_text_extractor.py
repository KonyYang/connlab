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
