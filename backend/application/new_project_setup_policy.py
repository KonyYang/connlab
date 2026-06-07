"""Validation policy for New Project setup confirmation values."""

from __future__ import annotations


LAB_PERFORMING_TESTS_OPTIONS: tuple[str, ...] = ("Dongguan", "Valley Green")


def normalize_lab_performing_tests(value: object, *, required: bool) -> str | None:
    """Return a valid Lab Performing the Tests value, or raise ValueError."""
    if value is None:
        if required:
            raise ValueError("Lab Performing the Tests is required.")
        return None
    text = str(value).strip()
    if not text:
        if required:
            raise ValueError("Lab Performing the Tests is required.")
        return None
    if text not in LAB_PERFORMING_TESTS_OPTIONS:
        allowed = ", ".join(LAB_PERFORMING_TESTS_OPTIONS)
        raise ValueError(f"Lab Performing the Tests must be one of: {allowed}.")
    return text
