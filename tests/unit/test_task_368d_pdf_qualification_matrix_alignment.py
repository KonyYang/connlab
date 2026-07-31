"""Bounded merged-span PDF Matrix regressions for TASK_368D."""

from __future__ import annotations

from backend.infrastructure.files.pdf_matrix_source_gateway import _normalize_table
from backend.modules.test_plan import ProductSpecMatrixParser


_CENTERED_POSITIONS = (1, 4, 7, 10, 13, 16, 19, 21)
_LEFT_EDGE_POSITIONS = (0, 3, 6, 9, 12, 15, 18, 21)


def _spanned_row(values: tuple[str, ...], *, centered: bool) -> list[str]:
    """Place eight logical values in the observed twenty-two-column PDF spans."""
    row = [""] * 22
    positions = _CENTERED_POSITIONS if centered else _LEFT_EDGE_POSITIONS
    for position, value in zip(positions, values, strict=True):
        row[position] = value
    return row


def _qualification_matrix_raw_shape() -> list[list[str]]:
    """Return the observed centered-header and left-edge-body PDF shape."""
    return [
        _spanned_row(("TEST", "PARA", "1", "2", "3", "4", "5", "6"), centered=True),
        _spanned_row(
            ("Examination", "5.5", "1,8", "1,7", "1,9", "1,4", "1", "1,5"),
            centered=False,
        ),
        _spanned_row(
            ("LLCR", "6.1", "2,9", "2,8", "2,10", "2,5", "", "2"),
            centered=False,
        ),
        _spanned_row(
            ("CR at rated current HP/LP Contacts only", "6.2", "3,10", "", "", "", "", "3"),
            centered=False,
        ),
        _spanned_row(
            ("Insulation Resistance", "6.3", "4,11", "3,9", "3,11", "", "", ""),
            centered=False,
        ),
        _spanned_row(
            ("Dielectric Withstanding Voltage", "6.4", "5,12", "4,10", "4,12", "", "", ""),
            centered=False,
        ),
        _spanned_row(
            ("Current Rating", "6.5", "", "", "", "", "", "4"),
            centered=False,
        ),
        _spanned_row(
            ("Sample size", "VT Header", "5", "5", "5", "5", "5", "5"),
            centered=False,
        ),
        _spanned_row(
            ("", "VT Rec.", "5", "5", "5", "5", "5", "5"),
            centered=False,
        ),
    ]


def test_centered_merged_header_spans_align_with_left_edge_matrix_body() -> None:
    """The controlled qualification signature must collapse to eight logical columns."""
    normalized = _normalize_table(_qualification_matrix_raw_shape())

    assert normalized[0] == ("TEST", "PARA", "1", "2", "3", "4", "5", "6")
    assert normalized[1] == (
        "Examination",
        "5.5",
        "1,8",
        "1,7",
        "1,9",
        "1,4",
        "1",
        "1,5",
    )
    assert normalized[-2:] == (
        ("Sample size", "VT Header", "5", "5", "5", "5", "5", "5"),
        ("", "VT Rec.", "5", "5", "5", "5", "5", "5"),
    )
    assert {len(row) for row in normalized} == {8}

    parsed = ProductSpecMatrixParser().parse_tables(
        [[list(row) for row in normalized]]
    )

    assert parsed.blockers == ()
    assert parsed.warnings == ()
    assert [group.group_label for group in parsed.groups] == ["1", "2", "3", "4", "5", "6"]
    assert [[step.raw_token for step in group.steps] for group in parsed.groups] == [
        ["1", "2", "3", "4", "5", "8", "9", "10", "11", "12"],
        ["1", "2", "3", "4", "7", "8", "9", "10"],
        ["1", "2", "3", "4", "9", "10", "11", "12"],
        ["1", "2", "4", "5"],
        ["1"],
        ["1", "2", "3", "4", "5"],
    ]
    assert [group.sample_size for group in parsed.groups] == [5, 5, 5, 5, 5, 5]


def test_unrelated_sparse_merged_table_is_not_collapsed() -> None:
    """Sparse paired extraction without Matrix body/sample evidence stays unchanged."""
    raw_table = [
        _spanned_row(("TEST", "PARA", "1", "2", "3", "4", "5", "6"), centered=True),
        _spanned_row(("Status", "N/A", "open", "", "", "", "", "closed"), centered=False),
    ]

    normalized = _normalize_table(raw_table)

    assert len(normalized[0]) > 8
    assert normalized[0] != ("TEST", "PARA", "1", "2", "3", "4", "5", "6")
