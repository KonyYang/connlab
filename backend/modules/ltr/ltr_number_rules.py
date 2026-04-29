"""Pure LTR number parsing, validation, and sequence rules."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum


class LtrNumberKind(StrEnum):
    """Supported LTR number families."""

    STANDARD_DL = "standard_dl"
    W_PREFIX = "w_prefix"


class LtrNumberError(ValueError):
    """Raised when an LTR number cannot be parsed or formatted."""


@dataclass(frozen=True, slots=True)
class ParsedLtrNumber:
    """Structured LTR number components."""

    raw: str
    normalized: str
    kind: LtrNumberKind
    year: int | None = None
    month: int | None = None
    sequence: int | None = None
    suffix: str | None = None
    w_value: str | None = None

    @property
    def is_base_monthly_dl(self) -> bool:
        """Return whether this is a standard DL without a suffix."""
        return self.kind is LtrNumberKind.STANDARD_DL and self.suffix is None

    @property
    def is_associated_dl(self) -> bool:
        """Return whether this is a standard DL with an association suffix."""
        return self.kind is LtrNumberKind.STANDARD_DL and self.suffix is not None


_STANDARD_DL_PATTERN = re.compile(
    r"^DL-(?P<year>\d{4})-(?P<month>\d{2})-(?P<sequence>\d{3})(?P<suffix>[A-Z])?$",
    flags=re.IGNORECASE,
)
_W_PREFIX_PATTERN = re.compile(r"^W(?P<value>[A-Z0-9]+)$", flags=re.IGNORECASE)


def parse_ltr_number(value: str) -> ParsedLtrNumber:
    """Parse a supported LTR number into structured components."""
    normalized = _normalize(value)
    match = _STANDARD_DL_PATTERN.fullmatch(normalized)
    if match:
        return _parse_standard_dl(normalized, match)
    match = _W_PREFIX_PATTERN.fullmatch(normalized)
    if match:
        return ParsedLtrNumber(
            raw=value,
            normalized=normalized,
            kind=LtrNumberKind.W_PREFIX,
            w_value=match.group("value"),
        )
    raise LtrNumberError(
        "LTR number must match DL-YYYY-MM-NNN, DL-YYYY-MM-NNN suffix, or W-prefix format."
    )


def validate_ltr_number(value: str) -> bool:
    """Return True when a value is a supported LTR number."""
    parse_ltr_number(value)
    return True


def base_ltr_number(value: str) -> str:
    """Return the base DL number without an association suffix."""
    parsed = parse_ltr_number(value)
    if parsed.kind is not LtrNumberKind.STANDARD_DL:
        raise LtrNumberError("Only standard DL numbers have a base number.")
    return format_standard_dl_number(parsed.year or 0, parsed.month or 0, parsed.sequence or 0)


def family_stem(value: str) -> str:
    """Return the family stem used for associated LTR lookup."""
    return base_ltr_number(value)


def validate_new_registration_number(value: str) -> bool:
    """Validate a new workbook registration number."""
    parsed = parse_ltr_number(value)
    if parsed.kind is not LtrNumberKind.STANDARD_DL:
        raise LtrNumberError("New LTR registrations must use DL-YYYY-MM-NNN format.")
    return True


def format_standard_dl_number(year: int, month: int, sequence: int) -> str:
    """Format a base monthly DL number."""
    _validate_year_month_sequence(year, month, sequence)
    return f"DL-{year:04d}-{month:02d}-{sequence:03d}"


def next_monthly_dl_number(
    *,
    year: int,
    month: int,
    existing_numbers: list[str] | tuple[str, ...],
) -> str:
    """Return the next base monthly DL number from existing plain strings."""
    _validate_year_month_sequence(year, month, 1)
    max_sequence = 0
    for number in existing_numbers:
        parsed = _try_parse_ltr_number(number)
        if not parsed or parsed.kind is not LtrNumberKind.STANDARD_DL:
            continue
        if parsed.year == year and parsed.month == month and parsed.sequence:
            max_sequence = max(max_sequence, parsed.sequence)
    return format_standard_dl_number(year, month, max_sequence + 1)


def _parse_standard_dl(normalized: str, match: re.Match[str]) -> ParsedLtrNumber:
    """Build a parsed standard DL value from a regex match."""
    year = int(match.group("year"))
    month = int(match.group("month"))
    sequence = int(match.group("sequence"))
    suffix = match.group("suffix")
    _validate_year_month_sequence(year, month, sequence)
    return ParsedLtrNumber(
        raw=normalized,
        normalized=normalized,
        kind=LtrNumberKind.STANDARD_DL,
        year=year,
        month=month,
        sequence=sequence,
        suffix=suffix,
    )


def _try_parse_ltr_number(value: str) -> ParsedLtrNumber | None:
    """Parse an LTR number or return None for sequence calculations."""
    try:
        return parse_ltr_number(value)
    except LtrNumberError:
        return None


def _validate_year_month_sequence(year: int, month: int, sequence: int) -> None:
    """Validate standard DL numeric components."""
    if year < 2000 or year > 9999:
        raise LtrNumberError("DL year must be a four-digit year from 2000 onward.")
    if month < 1 or month > 12:
        raise LtrNumberError("DL month must be between 01 and 12.")
    if sequence < 1 or sequence > 999:
        raise LtrNumberError("DL sequence must be between 001 and 999.")


def _normalize(value: str) -> str:
    """Normalize user-entered LTR number text."""
    normalized = re.sub(r"\s+", "", value).upper()
    if not normalized:
        raise LtrNumberError("LTR number is required.")
    return normalized
