"""Bounded canonical point-expression parsing for Point Profile snapshots."""

from __future__ import annotations

import re
from dataclasses import dataclass


class ContactPointExpressionError(ValueError):
    """Raised when a point expression cannot become explicit authority."""


_TOKEN = re.compile(r"\s*([1-9][0-9]*)(?:\s*-\s*([1-9][0-9]*))?\s*")
_MAX_SOURCE = 1024
_MAX_POINT = 9999
_MAX_POINTS = 4096


@dataclass(frozen=True)
class ParsedPointExpression:
    canonical: str
    points: tuple[int, ...]

    @property
    def count(self) -> int:
        return len(self.points)


def parse_point_expression(source: object) -> ParsedPointExpression:
    if not isinstance(source, str) or not source.strip() or len(source) > _MAX_SOURCE:
        raise ContactPointExpressionError("Test points expression is required and must be at most 1024 characters.")
    values: set[int] = set()
    for raw in source.split(","):
        match = _TOKEN.fullmatch(raw)
        if match is None:
            raise ContactPointExpressionError("Test points must use positive integers and ascending ranges.")
        start = int(match.group(1))
        end = int(match.group(2) or start)
        if end < start or end > _MAX_POINT:
            raise ContactPointExpressionError("Test points range is invalid or exceeds 9999.")
        values.update(range(start, end + 1))
        if len(values) > _MAX_POINTS:
            raise ContactPointExpressionError("One category may contain at most 4096 test points.")
    points = tuple(sorted(values))
    return ParsedPointExpression(_compress(points), points)


def _compress(points: tuple[int, ...]) -> str:
    runs: list[str] = []
    start = previous = points[0]
    for point in points[1:]:
        if point == previous + 1:
            previous = point
            continue
        runs.append(str(start) if start == previous else f"{start}-{previous}")
        start = previous = point
    runs.append(str(start) if start == previous else f"{start}-{previous}")
    return ",".join(runs)
