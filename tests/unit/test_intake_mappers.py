from __future__ import annotations

from backend.application.intake_mappers import from_sample, to_sample_infos
from backend.modules.intake import ParsedSampleInfo


def test_sample_mapping_is_lossless_for_report_fields_and_row_order() -> None:
    samples = to_sample_infos(
        "P1",
        (
            ParsedSampleInfo(
                product_name="Pin",
                part_number="PN-PIN",
                lot_or_traceability="LOT-1",
                material="C1100",
                plating="Ag",
                lubricant="No",
                housing_material="NA",
                quantity="2",
            ),
            ParsedSampleInfo(
                product_name="Socket",
                part_number="PN-SOCKET",
                lubricant="Yes",
                quantity="3",
            ),
        ),
        source_form_id="F1",
    )

    assert [sample.row_index for sample in samples] == [0, 1]
    assert [sample.lubricant for sample in samples] == ["No", "Yes"]
    assert all(sample.source_form_id == "F1" for sample in samples)
    assert from_sample(samples[0]).lubricant == "No"
