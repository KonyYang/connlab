"""Extract row-level Matrix details from product specification sections."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class MatrixRowDetailExtraction:
    """Method, condition, and requirement extracted for one Matrix row."""

    method: str | None = None
    condition: str | None = None
    requirement: str | None = None
    status: str = "missing"
    source_section: str | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)


_SECTION_HEADING_RE = re.compile(
    r"^\s*(?P<section>\d+(?:\.\d+)+)\s+(?P<title>[A-Za-z].*)$"
)
_STANDARD_RE = re.compile(r"\b(EIA[-\s]?364[-\s]?\d+(?:[-.]\d+)?[A-Z]?)\b", re.IGNORECASE)
_CONDITION_PATTERNS = (
    re.compile(r"(\d+(?:\.\d+)?\s*mV\s*max\s*,\s*\d+(?:\.\d+)?\s*mA\s*max)", re.IGNORECASE),
    re.compile(r"(test\s+condition\s+[A-Z0-9-]+)", re.IGNORECASE),
    re.compile(r"((?:\d+(?:\.\d+)?\s*(?:mm/min|cycles?|hours?|minutes?|mins?|A|V|ADC|G|ms|RH|C|℃|～C|°C)[,;\s]*){1,4})", re.IGNORECASE),
)
_REQUIREMENT_PATTERNS = (
    re.compile(
        r"((?:shall\s+not\s+exceed|not\s+exceed)\s+\d+(?:\.\d+)?\s+[A-Za-zΩμµ]+)",
        re.IGNORECASE,
    ),
    re.compile(
        r"((?:shall\s+not\s+exceed|not\s+exceed)\s+[^.]+)",
        re.IGNORECASE,
    ),
    re.compile(r"(No\s+(?:damage|detrimental\s+condition)[^.]*\.?)", re.IGNORECASE),
    re.compile(r"((?:Initial|After\s+test|maximum\s+change|change)\s*[:：]?\s*[^.。;]+)", re.IGNORECASE),
    re.compile(r"([<>≤≥]\s*[\d.]+\s*(?:m?ohms?|mΩ|Ω|N|mV|°C|℃))", re.IGNORECASE),
)


def extract_row_details_by_section(
    paragraphs: list[str],
) -> dict[str, MatrixRowDetailExtraction]:
    """Return extracted details keyed by exact specification section number."""
    sections = collect_section_text_blocks(paragraphs)
    return {
        section: extract_row_details(section=section, section_text=text)
        for section, text in sections.items()
    }


def collect_section_text_blocks(paragraphs: list[str]) -> dict[str, str]:
    """Collect text blocks for numbered specification sections."""
    blocks: dict[str, list[str]] = {}
    current_section: str | None = None
    for raw in paragraphs:
        text = _clean(raw)
        if not text:
            continue
        match = _SECTION_HEADING_RE.match(text)
        if match:
            current_section = match.group("section")
            blocks.setdefault(current_section, [text])
            continue
        if current_section is not None:
            blocks[current_section].append(text)
    return {
        section: " ".join(lines).strip()
        for section, lines in blocks.items()
        if any(line.strip() for line in lines)
    }


def extract_row_details(*, section: str, section_text: str) -> MatrixRowDetailExtraction:
    """Extract Method, Condition, and Requirement values from one section block."""
    text = _clean(section_text)
    if not text:
        return MatrixRowDetailExtraction(status="missing", source_section=section)
    method = _extract_method(text)
    condition = _extract_condition(text)
    requirement = _extract_requirement(text)
    extracted_count = sum(1 for value in (method, condition, requirement) if value)
    if extracted_count == 0:
        status = "missing"
    elif extracted_count == 3:
        status = "matched"
    else:
        status = "partial"
    notes = tuple(
        note
        for value, note in (
            (method, "method"),
            (condition, "condition"),
            (requirement, "requirement"),
        )
        if value
    )
    return MatrixRowDetailExtraction(
        method=method,
        condition=condition,
        requirement=requirement,
        status=status,
        source_section=section,
        notes=notes,
    )


def _extract_method(text: str) -> str | None:
    match = _STANDARD_RE.search(text)
    if not match:
        return None
    return _normalize_standard(match.group(1))


def _extract_condition(text: str) -> str | None:
    for pattern in _CONDITION_PATTERNS:
        match = pattern.search(text)
        if match:
            return _clean(match.group(1).strip(" ,;"))
    return None


def _extract_requirement(text: str) -> str | None:
    for pattern in _REQUIREMENT_PATTERNS:
        match = pattern.search(text)
        if match:
            return _clean(match.group(1).strip(" ,;"))
    return None


def _normalize_standard(value: str) -> str:
    normalized = re.sub(r"\s+", "-", value.strip().upper())
    normalized = re.sub(r"EIA-?364", "EIA-364", normalized)
    normalized = re.sub(r"-+", "-", normalized)
    return normalized


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).replace("\x07", " ")).strip()
