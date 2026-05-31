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
_EIA_STANDARD_RE = re.compile(r"\b(EIA[-\s]?364[-\s]?\d+(?:[-.]\d+)?[A-Z]?)\b", re.IGNORECASE)
_J_STD_RE = re.compile(r"\b((?:ANSI[-/\s]*)?J[-\s]?STD[-\s]?\d{3}[A-Z]?)\b", re.IGNORECASE)
_USCAR_RE = re.compile(
    r"\b(?:SAE\s*/\s*)?USCAR[-\s_]*(?P<number>\d+)"
    r"(?:\s*(?:section)?\s*[-_ ]?\s*(?P<section>\d+(?:\.\d+)+))?",
    re.IGNORECASE,
)
_IEC_RE = re.compile(
    r"(?<![A-Z0-9])IEC[-\s_]*(?P<number>\d{4,5})"
    r"(?:[-\s_]*(?P<section>\d+(?:[-.]\d+)*))?",
    re.IGNORECASE,
)
_IEC_CLAUSE_RE = re.compile(
    r"\b(?:clause|section)\s+(?P<section>\d+(?:\.\d+)*)\s+of\s+IEC[-\s_]*(?P<number>\d{4,5})\b",
    re.IGNORECASE,
)
_CONDITION_PATTERNS = (
    re.compile(r"(\d+(?:\.\d+)?\s*mV\s*max\s*,\s*\d+(?:\.\d+)?\s*mA\s*max)", re.IGNORECASE),
    re.compile(r"(test\s+condition\s+[A-Z0-9-]+)", re.IGNORECASE),
    re.compile(
        r"((?:\d+(?:\.\d+)?\s*(?:mm/min|cycles?|hours?|minutes?|mins?|A|V|ADC|G|ms|RH|℃|°C|～C)[,;\s]*){1,4})",
        re.IGNORECASE,
    ),
)
_LIMIT_UNITS = r"(?:milliohms?|milli\s+ohms?|mΩ|Ω|ohms?|mV|V|N|℃|°C|C)"
_REQUIREMENT_PATTERNS = (
    re.compile(
        rf"((?:shall\s+not\s+exceed|not\s+exceed)\s+\d+(?:\.\d+)?\s*{_LIMIT_UNITS}(?:\s+(?:initially|maximum|minimum))?)",
        re.IGNORECASE,
    ),
    re.compile(r"(No\s+(?:damage|detrimental\s+condition)[^.]*\.?)", re.IGNORECASE),
    re.compile(r"((?:Initial|After\s+test|maximum\s+change|change)\s*[:：]?\s*[^.;。]+)", re.IGNORECASE),
    re.compile(rf"([<>≤≥]\s*[\d.]+\s*{_LIMIT_UNITS})", re.IGNORECASE),
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
    body = _strip_section_heading(section=section, text=text)
    method = _extract_method(text)
    condition = _extract_condition(body)
    requirement = _extract_requirement(body)
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
    for extractor in (
        _extract_eia_method,
        _extract_j_std_method,
        _extract_uscar_method,
        _extract_iec_method,
    ):
        method = extractor(text)
        if method:
            return method
    return None


def _extract_eia_method(text: str) -> str | None:
    match = _EIA_STANDARD_RE.search(text)
    if not match:
        return None
    normalized = re.sub(r"\s+", "-", match.group(1).strip().upper())
    normalized = re.sub(r"EIA-?364", "EIA-364", normalized)
    return re.sub(r"-+", "-", normalized)


def _extract_j_std_method(text: str) -> str | None:
    match = _J_STD_RE.search(text)
    if not match:
        return None
    normalized = re.sub(r"[-/\s]+", "-", match.group(1).strip().upper())
    normalized = re.sub(r"J-?STD", "J-STD", normalized)
    return re.sub(r"-+", "-", normalized)


def _extract_uscar_method(text: str) -> str | None:
    match = _USCAR_RE.search(text)
    if not match:
        return None
    method = f"USCAR-{match.group('number')}"
    section = match.group("section")
    if section:
        method = f"{method} {section}"
    return method


def _extract_iec_method(text: str) -> str | None:
    clause_match = _IEC_CLAUSE_RE.search(text)
    if clause_match:
        return f"IEC {clause_match.group('number')} {clause_match.group('section')}"
    matches = list(_IEC_RE.finditer(text))
    if not matches:
        return None
    match = next((item for item in matches if item.group("section")), matches[0])
    number = match.group("number")
    section = match.group("section")
    if not section:
        return f"IEC {number}"
    separator = " " if "." in section else "-"
    return f"IEC {number}{separator}{section}"


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


def _strip_section_heading(*, section: str, text: str) -> str:
    """Remove the leading section heading so titles are not parsed as values."""
    marker = re.compile(
        rf"^\s*{re.escape(section)}\s+[A-Za-z][A-Za-z0-9,/()& -]*?"
        r"(?=\s(?:The|Measurements|Voltage|Durability|Unless|After|When|This|As|No|Test|[a-z]\.))"
    )
    stripped = marker.sub("", text, count=1).strip()
    if stripped != text:
        return stripped
    return text


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).replace("\x07", " ")).strip()
