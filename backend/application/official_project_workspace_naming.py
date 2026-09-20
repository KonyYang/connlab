"""Official project workspace folder naming helpers."""

from __future__ import annotations

import re


WINDOWS_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*]+')
WHITESPACE = re.compile(r"\s+")


class OfficialWorkspaceNamingError(ValueError):
    """Raised when an official workspace folder name cannot be planned safely."""


def build_official_project_folder_name(
    *,
    dl_number: str,
    product_description: str | None,
    test_description: str | None,
    max_segment_length: int = 150,
) -> str:
    """Return a safe business-readable official project folder name."""
    dl = _clean_part(dl_number)
    if not dl:
        raise OfficialWorkspaceNamingError("DL number is required to name workspace folder.")
    product = _clean_part(product_description) or "Product"
    test = _clean_part(test_description) or "Qualification test"
    name = _normalize_segment(f"{dl} {product} {test}")
    if len(name) <= max_segment_length:
        return name
    return _truncate_preserving_prefix(name=name, prefix=dl, max_length=max_segment_length)


def _clean_part(value: str | None) -> str:
    """Clean one human-readable folder-name part."""
    if value is None:
        return ""
    return _normalize_segment(WINDOWS_INVALID_FILENAME_CHARS.sub(" ", value))


def _normalize_segment(value: str) -> str:
    """Normalize whitespace and trim Windows-problematic trailing punctuation."""
    normalized = WHITESPACE.sub(" ", value).strip().rstrip(". ")
    return normalized


def _truncate_preserving_prefix(*, name: str, prefix: str, max_length: int) -> str:
    """Truncate a folder segment without losing the DL prefix."""
    min_length = len(prefix) + 1
    if max_length < min_length:
        raise OfficialWorkspaceNamingError("Maximum folder name length is too short for DL number.")
    return name[:max_length].rstrip(". ")
