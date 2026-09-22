from __future__ import annotations

from backend.application.external_resource_service import legacy_equipment_excel_layout
from backend.infrastructure.office.excel_tabular_layout import map_explicit_layout_rows


def test_legacy_equipment_layout_accepts_annotated_manufacturer_header() -> None:
    """Keep the fixed legacy columns while allowing a Manufacturer annotation."""
    headers, rows = map_explicit_layout_rows(
        [
            [],
            [],
            [],
            [
                "Item (Equipment Name)",
                "Item (Equipment Name)\n中英文",
                "Manufacturer\n（制造商）",
                "ID Number",
                "Last Cal.",
                "Cal. Due",
            ],
            ["Oscilloscope", "", "Keysight", "E-001", "2026-01-01", "2027-01-01"],
        ],
        sheet_name="All Equip.",
        layout=legacy_equipment_excel_layout(),
    )

    assert headers == (
        "Item (Equipment Name)",
        "Manufacturer",
        "ID Number",
        "Last Cal.",
        "Cal. Due",
    )
    assert rows == (
        {
            "Item (Equipment Name)": "Oscilloscope",
            "Manufacturer": "Keysight",
            "ID Number": "E-001",
            "Last Cal.": "2026-01-01",
            "Cal. Due": "2027-01-01",
            "__sheet_name": "All Equip.",
        },
    )
