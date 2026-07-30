"""Focused regressions for TASK_368A Matrix import selection."""

from pathlib import Path

from backend.application.project_test_plan_matrix_preview_service import (
    _preview_from_snapshot,
    _select_table_index,
)
from backend.infrastructure.office.models import WordTableLocation
from backend.modules.test_plan import ProductSpecMatrixParser


def _qualification_matrix() -> list[list[str]]:
    """Return a GS-12-2186-shaped Matrix with a Word-split Section header."""
    return [
        [
            "TEST GROUP ID:",
            "TEST GROUP ID:",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6a",
            "6b",
            "7",
            "8",
            "9",
            "10",
        ],
        [
            "TEST DESCRIPTION",
            "SECTIO N",
            "Temp Life",
            "Thermal Shock & Humidity",
            "Vibration & Shock",
            "Mixed Flowing Gas",
            "Dust",
            "Durability",
            "DWV",
            "Salt Spray",
            "Current Rating",
            "Contact Retention Force",
            "Solderability",
        ],
        ["VISUAL EXAMINATION", "7.1", *(["1"] * 11)],
        ["SAMPLES QUANTITY (PCS)", "", *(["3"] * 11)],
    ]


def _revision_record() -> list[list[str]]:
    """Return the false-positive Revision Record shape from the diagnosis."""
    return [
        ["Rev", "Page", "Description", "EC#", "Date"],
        ["01", "11", "THE FIRST RELEASE", "", "2024/02/27"],
        ["02", "4, 5, 6", "CORRECT SOME TYPOS", "", "2024/04/24"],
        ["03", "4, 7, 11", "CHANGE GROUP P TEST ITEM", "", "2024/05/14"],
        ["04", "4, 11", "CHANGE SOME CURRENT RATING VALUE", "", "2024/06/17"],
        ["05", "9", "ADD SOLDERABILITY TEST", "", "2024/08/21"],
        ["06", "1, 2", "UPDATE OPERATING VOLTAGE RATING", "", "2024/11/12"],
    ]


def _location(
    table_index: int,
    page_number: int,
    page_table_index: int,
    preceding_paragraph: str,
    text_preview: str,
) -> WordTableLocation:
    """Build one neutral table location for a synthetic document."""
    return WordTableLocation(
        table_index=table_index,
        page_number=page_number,
        page_table_index=page_table_index,
        preceding_paragraph=preceding_paragraph,
        text_preview=text_preview,
        row_count=4,
        column_count=13,
    )


def _preview(
    *,
    tables: list[list[list[str]]],
    locations: tuple[WordTableLocation, ...],
    page_number: int | None,
    page_table_index: int | None,
    table_text_query: str | None,
):
    """Run the neutral application preview boundary."""
    return _preview_from_snapshot(
        project_id="P-task-368a",
        source_path=Path("synthetic.docx"),
        source_format=".docx",
        generated_at="2026-07-31T00:00:00+00:00",
        parser=ProductSpecMatrixParser(),
        tables=tables,
        paragraphs=[],
        table_locations=locations,
        page_number=page_number,
        page_table_index=page_table_index,
        table_text_query=table_text_query,
        preview_pdf_token=None,
        applicable_specifications=None,
    )


def test_auto_selects_split_header_matrix_and_rejects_singular_page_revision() -> None:
    """A Revision Record body must not outrank the real qualification Matrix."""
    parser = ProductSpecMatrixParser()
    tables = [_qualification_matrix(), _revision_record()]

    result = parser.parse_tables(
        tables,
        table_contexts={1: "Qualification Test Table", 2: "REVISION RECORD"},
    )
    selected_revision = parser.parse_tables(tables, selected_table_index=2)

    assert result.blockers == ()
    assert result.selected_table_index == 1
    assert [group.group_label for group in result.groups] == [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6a",
        "6b",
        "7",
        "8",
        "9",
        "10",
    ]
    assert selected_revision.groups == ()
    assert selected_revision.blockers == ("Selected table 2 is not a valid Matrix table.",)


def test_page_and_keyword_match_only_within_the_requested_page() -> None:
    """Page must constrain keyword search before the first match is selected."""
    locations = (
        _location(1, 11, 1, "REVISION RECORD", "CHANGE TEST GROUP ITEM"),
        _location(2, 10, 1, "Qualification Test Table", "TEST GROUP ID"),
    )

    selected = _select_table_index(
        table_locations=locations,
        page_number=10,
        page_table_index=None,
        table_text_query="TEST GROUP",
    )

    assert selected == 2


def test_unmatched_explicit_locator_does_not_fall_back_to_auto_selection() -> None:
    """An explicit locator miss must not authorize global Matrix scoring."""
    preview = _preview(
        tables=[_qualification_matrix()],
        locations=(
            _location(1, 10, 1, "Qualification Test Table", "TEST GROUP ID"),
        ),
        page_number=99,
        page_table_index=None,
        table_text_query=None,
    )

    assert preview.groups == ()
    assert preview.selected_table_index is None
    assert preview.blockers == ("No table matched the requested Matrix locator.",)


def test_selected_invalid_table_keeps_requested_location_for_diagnostics() -> None:
    """A parser blocker must retain the table location that produced it."""
    preview = _preview(
        tables=[[["Not a Matrix"]]],
        locations=(
            _location(1, 10, 1, "Qualification Test Table", "TARGET TABLE"),
        ),
        page_number=10,
        page_table_index=None,
        table_text_query="TARGET",
    )

    assert preview.groups == ()
    assert preview.blockers == ("Selected table 1 is not a valid Matrix table.",)
    assert preview.selected_page_number == 10
    assert preview.selected_page_table_index == 1
