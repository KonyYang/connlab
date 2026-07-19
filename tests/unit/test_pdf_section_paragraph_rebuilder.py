from backend.infrastructure.files.pdf_section_paragraph_rebuilder import (
    rebuild_pdf_paragraphs,
)
from backend.modules.test_plan.spec_section_text_extractor import (
    collect_section_text_blocks,
)


def test_rebuilder_attaches_next_page_prefix_to_active_mfg_section() -> None:
    paragraphs = rebuild_pdf_paragraphs(
        [
            (
                "8.2 MFG Ensure the same receptacle is used. The mixed gas "
                "conditions refer to Clause 4.8 Industrial Mixed Gas. "
                "Test Condition: CLASS IIA"
            ),
            (
                "NUMBER TYPE GENERAL PAGE 7 of 12 Expose the connector in "
                "unmated condition for 224h. Expose the connector in mated "
                "condition for 112h. 8.3 Voltage surge Power Pin 10 kA."
            ),
        ]
    )

    sections = collect_section_text_blocks(list(paragraphs))

    assert "4.8" not in sections
    assert "CLASS IIA" in sections["8.2"]
    assert "unmated condition for 224h" in sections["8.2"]
    assert "mated condition for 112h" in sections["8.2"]
    assert "unmated condition" not in sections["8.3"]


def test_rebuilder_attaches_current_rating_reference_from_next_page() -> None:
    paragraphs = rebuild_pdf_paragraphs(
        [
            "6.4 CURRENT RATING The temperature rise shall not exceed 30C.",
            (
                "NUMBER TYPE GENERAL PAGE 4 of 12 c. Reference - EIA 364-70 "
                "6.5 Contact Resistance The resistance shall meet requirements."
            ),
        ]
    )

    sections = collect_section_text_blocks(list(paragraphs))

    assert "EIA 364-70" in sections["6.4"]
    assert "EIA 364-70" not in sections["6.5"]


def test_rebuilder_keeps_backward_paragraph_references_in_active_section() -> None:
    paragraphs = rebuild_pdf_paragraphs(
        [
            (
                "8.0 Environmental Conditions shall meet paragraphs 6.0 and "
                "7.0 as specified. 8.1 Salt Spray Test Condition: 72 hours."
            )
        ]
    )

    sections = collect_section_text_blocks(list(paragraphs))

    assert "6.0" not in sections
    assert "7.0" not in sections
    assert "paragraphs 6.0 and 7.0" in sections["8.0"]
    assert sections["8.1"].startswith("8.1 Salt Spray")


def test_rebuilder_does_not_treat_inline_measurement_as_forward_section() -> None:
    paragraphs = rebuild_pdf_paragraphs(
        [
            (
                "7.2 Single Pin Mating/Unmating Force\n"
                "b. Current-carrying pin extraction force: 4 N <= F <= 19.5 N\n"
                "7.3 contact retention force\n"
                "Requirement: Power Contact 150N minimum"
            ),
            "8.0 Environmental Conditions\n8.2 MFG Test Condition: CLASS IIA",
        ]
    )

    sections = collect_section_text_blocks(list(paragraphs))

    assert "19.5" not in sections
    assert sections["7.3"].startswith("7.3 contact retention force")
    assert sections["8.2"].startswith("8.2 MFG")


def test_rebuilder_preserves_marker_notes_and_unsectioned_pages() -> None:
    paragraphs = rebuild_pdf_paragraphs(
        ["Cover page", "Notes: a.Male connector. b.Female connector."]
    )

    assert "Cover page" in paragraphs
    assert "Notes: a.Male connector. b.Female connector." in paragraphs
    assert "(a) Male connector." in paragraphs
    assert "(b) Female connector." in paragraphs
