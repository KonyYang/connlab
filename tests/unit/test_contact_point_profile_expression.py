import pytest

from backend.application.contact_point_profile_expression import (
    ContactPointExpressionError,
    parse_point_expression,
)


def test_expression_canonicalizes_duplicates_overlaps_and_order() -> None:
    parsed = parse_point_expression(" 3, 1-2, 2, 8 ")
    assert parsed.canonical == "1-3,8"
    assert parsed.points == (1, 2, 3, 8)
    assert parsed.count == 4


@pytest.mark.parametrize("source", ["", "1,", "0", "-1", "1.5", "1e2", "one", "4-2"])
def test_expression_rejects_invalid_syntax(source: str) -> None:
    with pytest.raises(ContactPointExpressionError):
        parse_point_expression(source)
