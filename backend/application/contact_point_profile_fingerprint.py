"""Canonical Point Profile category validation and optimistic fingerprints."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections.abc import Iterable, Mapping


class ContactPointProfileValidationError(ValueError):
    """Raised when an editable Point Profile category payload is invalid."""


_PROFILE_ID = re.compile(r"ppc-([1-9][0-9]*)$")


def canonicalize_categories(
    categories: Iterable[Mapping[str, object]], *, resolve_fallback: bool = True,
) -> tuple[dict[str, object], ...]:
    """Validate and canonicalize ordered category input without issuing ids."""
    normalized: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    labels: set[str] = set()
    prefixes: set[str] = set()
    for ordinal, source in enumerate(categories):
        category_id = _optional_category_id(source.get("category_id"))
        if category_id is not None:
            if category_id in seen_ids:
                raise ContactPointProfileValidationError("Point Profile category ids must be unique.")
            seen_ids.add(category_id)
        label = _required_label(source.get("label"))
        included = bool(source.get("included", True))
        count = _count(source.get("count_per_sample"))
        if included and count <= 0:
            raise ContactPointProfileValidationError(
                "Included Point Profile category count must be a positive integer."
            )
        prefix = _resolve_prefix(source.get("record_prefix"), label, _fallback_number(category_id, ordinal)) if resolve_fallback else _explicit_prefix(source.get("record_prefix"), label)
        label_key = _normalized_label(label)
        prefix_key = prefix.casefold()
        if included:
            if label_key in labels:
                raise ContactPointProfileValidationError(
                    "Included Point Profile category labels must be unique."
                )
            if prefix_key and prefix_key in prefixes:
                raise ContactPointProfileValidationError(
                    "Included Point Profile category prefixes must be unique."
                )
            labels.add(label_key)
            if prefix_key:
                prefixes.add(prefix_key)
        normalized.append(
            {
                "category_id": category_id,
                "category_ordinal": ordinal,
                "label": label,
                "normalized_label_key": label_key,
                "count_per_sample": count,
                "record_prefix": prefix,
                "normalized_prefix_key": prefix_key,
                "included": included,
            }
        )
    return tuple(normalized)


def points_per_sample(categories: Iterable[Mapping[str, object]]) -> int:
    """Return the derived sum of included category counts."""
    return sum(
        int(item["count_per_sample"])
        for item in categories
        if bool(item["included"])
    )


def point_profile_fingerprint(
    root_id: str,
    revision_id: str,
    categories: Iterable[Mapping[str, object]],
) -> str:
    """Hash the ordered persisted category snapshot for stale-write detection."""
    payload = {
        "root_id": root_id,
        "revision_id": revision_id,
        "categories": [dict(item) for item in categories],
    }
    encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _optional_category_id(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not _PROFILE_ID.fullmatch(value):
        raise ContactPointProfileValidationError("Point Profile category id is invalid.")
    return value


def _required_label(value: object) -> str:
    if not isinstance(value, str):
        raise ContactPointProfileValidationError("Point Profile category label is required.")
    label = unicodedata.normalize("NFKC", value).strip()
    if not label:
        raise ContactPointProfileValidationError("Point Profile category label is required.")
    return label


def _count(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ContactPointProfileValidationError(
            "Point Profile category count must be a non-negative integer."
        )
    return value


def _resolve_prefix(value: object, label: str, fallback_number: int) -> str:
    raw = value if isinstance(value, str) else ""
    prefix = _ascii_prefix(raw)
    if prefix:
        return prefix
    label_prefix = _ascii_prefix(label)
    return label_prefix or f"C{fallback_number}"


def _ascii_prefix(value: str) -> str:
    prefix = re.sub(r"[^A-Z0-9]", "", unicodedata.normalize("NFKC", value).upper())
    return prefix if 1 <= len(prefix) <= 64 else ""


def _explicit_prefix(value: object, label: str) -> str:
    return _ascii_prefix(value if isinstance(value, str) else "") or _ascii_prefix(label)


def _fallback_number(category_id: str | None, ordinal: int) -> int:
    match = _PROFILE_ID.fullmatch(category_id or "")
    return int(match.group(1)) if match else ordinal + 1


def _normalized_label(value: str) -> str:
    return unicodedata.normalize("NFKC", value).strip().casefold()
