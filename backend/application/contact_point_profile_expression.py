"""Bounded canonical point-expression parsing for Point Profile snapshots."""

from __future__ import annotations

import re
from dataclasses import dataclass


class ContactPointExpressionError(ValueError):
    """Raised when a point expression cannot become explicit authority."""


_SINGLE = re.compile(
    r"(?:(?P<prefix>[A-Za-z]{0,64})(?P<number>[1-9][0-9]*))|(?P<label>[A-Za-z]{1,64})"
)
_RANGE = re.compile(
    r"(?P<prefix>[A-Za-z]{0,64})(?P<start>[1-9][0-9]*)"
    r"\s*-\s*(?P<end_prefix>[A-Za-z]{0,64})(?P<end>[1-9][0-9]*)"
)
_MAX_SOURCE = 1024
_MAX_POINT = 9999
_MAX_POINTS = 4096


@dataclass(frozen=True)
class ParsedPointExpression:
    canonical: str
    points: tuple[str, ...]

    @property
    def count(self) -> int:
        return len(self.points)


def parse_point_expression(source: object) -> ParsedPointExpression:
    if not isinstance(source, str) or not source.strip() or len(source) > _MAX_SOURCE:
        raise ContactPointExpressionError("Test points expression is required and must be at most 1024 characters.")
    points: list[str] = []
    seen: set[str] = set()
    for raw in source.split(","):
        token = raw.strip()
        range_match = _RANGE.fullmatch(token)
        if range_match is not None:
            prefix = range_match.group("prefix")
            end_prefix = range_match.group("end_prefix")
            if end_prefix and end_prefix.casefold() != prefix.casefold():
                raise ContactPointExpressionError("A test-point range must use one consistent prefix.")
            start = int(range_match.group("start"))
            end = int(range_match.group("end"))
            if end < start or end > _MAX_POINT:
                raise ContactPointExpressionError("Test points range is invalid or exceeds 9999.")
            expanded = (f"{prefix}{number}" for number in range(start, end + 1))
        else:
            single_match = _SINGLE.fullmatch(token)
            if single_match is None:
                raise ContactPointExpressionError(
                    "Test points must use explicit IDs or ascending ranges such as 1-5 or HP1-5."
                )
            number = single_match.group("number")
            if number is not None and int(number) > _MAX_POINT:
                raise ContactPointExpressionError("Test point numbers may not exceed 9999.")
            expanded = (token,)
        for point in expanded:
            if point in seen:
                continue
            seen.add(point)
            points.append(point)
            if len(points) > _MAX_POINTS:
                raise ContactPointExpressionError("One category may contain at most 4096 test points.")
    result = tuple(points)
    return ParsedPointExpression(_compress(result), result)


def _compress(points: tuple[str, ...]) -> str:
    runs: list[str] = []
    start = previous = _numbered_point(points[0])
    literal_start = points[0]
    for point in points[1:]:
        current = _numbered_point(point)
        if (
            start is not None
            and previous is not None
            and current is not None
            and current[0] == previous[0]
            and current[1] == previous[1] + 1
        ):
            previous = current
            continue
        runs.append(_format_run(literal_start, start, previous))
        literal_start = point
        start = previous = current
    runs.append(_format_run(literal_start, start, previous))
    return ",".join(runs)


def _numbered_point(point: str) -> tuple[str, int] | None:
    match = re.fullmatch(r"([A-Za-z]*)([1-9][0-9]*)", point)
    return (match.group(1), int(match.group(2))) if match else None


def _format_run(
    literal_start: str,
    start: tuple[str, int] | None,
    end: tuple[str, int] | None,
) -> str:
    if start is None or end is None or start == end:
        return literal_start
    return f"{literal_start}-{end[1]}"
