import pytest

from backend.application.contact_point_profile_expression import (
    ContactPointExpressionError,
    parse_point_expression,
)


def test_expression_preserves_first_seen_order_while_removing_duplicates() -> None:
    parsed = parse_point_expression(" 3, 1-2, 2, 8 ")
    assert parsed.canonical == "3,1-2,8"
    assert parsed.points == ("3", "1", "2", "8")
    assert parsed.count == 4


def test_expression_accepts_explicit_point_ids_and_prefixed_ranges() -> None:
    parsed = parse_point_expression("HP1-5,PE,P1,P3,P2")

    assert parsed.canonical == "HP1-5,PE,P1,P3,P2"
    assert parsed.points == ("HP1", "HP2", "HP3", "HP4", "HP5", "PE", "P1", "P3", "P2")


def test_expression_preserves_nonascending_numeric_and_named_point_order() -> None:
    assert parse_point_expression("1,24,35,2,7,10").points == (
        "1", "24", "35", "2", "7", "10",
    )
    assert parse_point_expression("P1,PE,P2,P3").points == (
        "P1", "PE", "P2", "P3",
    )


@pytest.mark.parametrize("source", ["", "1,", "0", "-1", "1.5", "1e2", "4-2", "HP5-1"])
def test_expression_rejects_invalid_syntax(source: str) -> None:
    with pytest.raises(ContactPointExpressionError):
        parse_point_expression(source)
