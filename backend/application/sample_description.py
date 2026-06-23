"""Sample information formatting helpers."""

from __future__ import annotations

from backend.domain import SampleInfo


def format_description_pn(samples: list[SampleInfo]) -> str | None:
    """Return LTR Description P/N text from sample rows in source-table order."""
    rows: list[str] = []
    for sample in samples:
        parts = [
            part.strip()
            for part in (sample.product_name, sample.part_number)
            if part and part.strip()
        ]
        if parts:
            rows.append(":".join(parts))
    return ", ".join(rows) or None
