from __future__ import annotations

import importlib

import pytest

from backend.modules.ltr import (
    LtrNumberError,
    LtrNumberKind,
    base_ltr_number,
    family_stem,
    format_standard_dl_number,
    is_alphanumeric_ltr_suffix_token,
    next_monthly_dl_number,
    parse_ltr_number,
    validate_new_registration_number,
    validate_ltr_number,
)


def test_parse_standard_dl_number() -> None:
    """A standard monthly DL number parses into year, month, and sequence."""
    parsed = parse_ltr_number("DL-2026-04-001")

    assert parsed.kind is LtrNumberKind.STANDARD_DL
    assert parsed.normalized == "DL-2026-04-001"
    assert parsed.year == 2026
    assert parsed.month == 4
    assert parsed.sequence == 1
    assert parsed.suffix is None
    assert parsed.is_base_monthly_dl
    assert validate_ltr_number("DL-2026-04-001") is True


def test_parse_w_prefix_number() -> None:
    """W-prefix values are accepted for existing or special external numbers."""
    parsed = parse_ltr_number("w123")

    assert parsed.kind is LtrNumberKind.W_PREFIX
    assert parsed.normalized == "W123"
    assert parsed.w_value == "123"
    assert not parsed.is_base_monthly_dl


def test_parse_standard_dl_number_with_suffix() -> None:
    """Standard DL values can carry an alphanumeric association suffix."""
    parsed = parse_ltr_number("DL-2026-04-001A9")

    assert parsed.kind is LtrNumberKind.STANDARD_DL
    assert parsed.year == 2026
    assert parsed.month == 4
    assert parsed.sequence == 1
    assert parsed.suffix == "A9"
    assert not parsed.is_base_monthly_dl
    assert parsed.is_associated_dl
    assert base_ltr_number("DL-2026-04-001A9") == "DL-2026-04-001"
    assert family_stem("DL-2026-04-001A9") == "DL-2026-04-001"


@pytest.mark.parametrize(
    "value, message",
    [
        ("", "LTR number is required"),
        ("DL-26-4-1", "LTR number must match"),
        ("abc", "LTR number must match"),
        ("DL-2026-04-001-A", "LTR number must match"),
        ("DL-2026-13-001", "DL month must be between 01 and 12"),
        ("DL-2026-04-000", "DL sequence must be between 001 and 999"),
    ],
)
def test_invalid_ltr_numbers_return_actionable_errors(
    value: str,
    message: str,
) -> None:
    """Invalid values fail with actionable validation messages."""
    with pytest.raises(LtrNumberError, match=message):
        parse_ltr_number(value)


def test_format_standard_dl_number() -> None:
    """Base monthly DL formatting pads month and sequence."""
    assert format_standard_dl_number(2026, 4, 7) == "DL-2026-04-007"


def test_next_monthly_dl_number_treats_suffix_as_occupied_sequence() -> None:
    """Associated suffix values occupy their base sequence."""
    existing = [
        "DL-2026-04-001",
        "DL-2026-04-002",
        "DL-2026-04-003A",
        "DL-2026-04-004",
        "DL-2026-04-005",
        "DL-2026-03-099",
        "W123",
        "invalid",
    ]

    assert (
        next_monthly_dl_number(year=2026, month=4, existing_numbers=existing)
        == "DL-2026-04-006"
    )


def test_new_registration_number_rejects_non_dl_external_values() -> None:
    """New registration values must be valid DL numbers, not external IDs."""
    assert validate_new_registration_number("DL-2026-04-031") is True

    with pytest.raises(LtrNumberError, match="New LTR registrations"):
        validate_new_registration_number("W123")


def test_next_monthly_dl_number_starts_at_one_for_empty_month() -> None:
    """A new month starts at sequence 001."""
    assert (
        next_monthly_dl_number(year=2026, month=5, existing_numbers=("DL-2026-04-009",))
        == "DL-2026-05-001"
    )


def test_ltr_number_rules_are_pure_python_boundary() -> None:
    """The rules module must not import service, storage, API, Office, or settings."""
    module = importlib.import_module("backend.modules.ltr.ltr_number_rules")
    imported_names = set(module.__dict__)

    forbidden_names = {"Document", "Session", "FastAPI", "Settings", "OfficeFacade"}
    assert not imported_names & forbidden_names


@pytest.mark.parametrize(
    "value, expected",
    [
        ("A9", True),
        ("sample2", True),
        ("123", True),
        ("A-9", False),
        ("A 9", False),
        ("A_9", False),
        ("", False),
    ],
)
def test_suffix_token_validator(value: str, expected: bool) -> None:
    """Suffix-token mode accepts alphanumeric values only."""
    assert is_alphanumeric_ltr_suffix_token(value) is expected
