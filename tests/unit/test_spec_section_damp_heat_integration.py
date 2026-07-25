from backend.modules.test_plan.spec_section_text_extractor import extract_row_details


def test_extract_row_details_uses_real_damp_heat_parser_for_canonical_condition() -> None:
    detail = extract_row_details(
        section="8.9",
        section_text=(
            "8.9 Long-term damp heat. "
            "Damp Heat Condition: 85℃, 85% RH, 1000h (mated test). After aging: "
            "Insulation resistance, withstand voltage and contact resistance shall meet "
            "the requirements."
        ),
        test_item="Long-term damp heat",
    )

    assert detail.condition == (
        "Damp Heat Condition: 85℃, 85% RH, 1000h (mated test)"
    )
