"""Extract row-level Matrix details from product specification sections."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from backend.modules.test_plan.method_template_matcher import (
    apply_fill_empty_fallback,
    normalize_test_item,
)
from backend.modules.test_plan.mcr_text_normalizer import normalize_condition_requirement
from backend.modules.test_plan.mfg_condition_parser import extract_mfg_condition
from backend.modules.test_plan.thermal_shock_condition_parser import (
    extract_thermal_shock_condition,
)
from backend.modules.test_plan.voltage_surge_condition_parser import (
    extract_voltage_surge_condition,
)

@dataclass(frozen=True, slots=True)
class MatrixRowDetailExtraction:
    """Method, condition, and requirement extracted for one Matrix row."""

    method: str | None = None
    condition: str | None = None
    requirement: str | None = None
    status: str = "missing"
    source_section: str | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)


_SECTION_HEADING_RE = re.compile(r"^\s*(?P<section>\d+(?:\.\d+)+)\s+(?P<title>[A-Za-z].*)$")
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
_MAX_CHANGE_RE = re.compile(
    r"(Maximum\s+Change\s*[:\-]?\s*[\d.]+\s*(?:mΩ|mohm|milliohms?|mV|V|N|C|℃))",
    re.IGNORECASE,
)
_NO_DAMAGE_RE = re.compile(r"(No\s+(?:damage|detrimental\s+condition)[^.]*\.?)", re.IGNORECASE)
_NO_DISCONTINUITY_RE = re.compile(r"(No\s+discontinuit(?:y|ies)\s*>?\s*[\d.]+\s*us)", re.IGNORECASE)
_LIMIT_UNITS = r"(?:milliohms?|milli\s+ohms?|mΩ|ohms?|mV|V|N|C|℃)"
_REQUIREMENT_PATTERNS = (
    re.compile(
        rf"((?:shall\s+not\s+exceed|not\s+exceed)\s+\d+(?:\.\d+)?\s*{_LIMIT_UNITS}(?:\s+(?:initially|maximum|minimum))?)",
        re.IGNORECASE,
    ),
    re.compile(r"((?:Initial|After\s+test|maximum\s+change|change)\s*[:]?\s*[^.;]+)", re.IGNORECASE),
    re.compile(rf"([<>≤≥]\s*[\d.]+\s*{_LIMIT_UNITS})", re.IGNORECASE),
)
_CONDITION_TOKEN_RE = re.compile(
    r"\b(\d+(?:\.\d+)?\s*(?:mV|mA|A|ADC|mm/min|cycles?|hours?|minutes?|mins?|G|ms|RH|℃))\b",
    re.IGNORECASE,
)


def extract_row_details_by_section(paragraphs: list[str]) -> dict[str, MatrixRowDetailExtraction]:
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


def extract_row_details(
    *,
    section: str,
    section_text: str,
    test_item: str | None = None,
    applicable_specifications: str | None = None,
) -> MatrixRowDetailExtraction:
    """Extract Method, Condition, and Requirement values from one section block."""
    text = _clean(section_text)
    body = _strip_section_heading(section=section, text=text) if text else ""
    method = _extract_method(text) if text else None
    condition = _extract_condition(body, test_item=test_item) if text else None
    requirement = _extract_requirement(body) if text else None
    notes: list[str] = []

    if method is None and test_item and "temperature rise" in test_item.lower() and "method 2" in body.lower():
        method = "EIA-364-70"
        notes.append("temperature-rise-default-method")

    fallback = apply_fill_empty_fallback(
        test_item=test_item,
        method=method,
        condition=condition,
        requirement=requirement,
    )
    if fallback.method != method:
        notes.append("template-fallback-method")
    if fallback.condition != condition:
        notes.append("template-fallback-condition")
    if fallback.requirement != requirement:
        notes.append("template-fallback-requirement")
    method = fallback.method
    condition = fallback.condition
    requirement = fallback.requirement

    method, condition, requirement = _apply_reseating_default(
        section=section,
        test_item=test_item,
        method=method,
        condition=condition,
        requirement=requirement,
        applicable_specifications=applicable_specifications,
        notes=notes,
    )

    normalized = normalize_condition_requirement(
        test_item=test_item,
        condition=condition,
        requirement=requirement,
        source_text=body or text,
    )
    if normalized.condition != condition:
        notes.append("normalized-condition")
    if normalized.requirement != requirement:
        notes.append("normalized-requirement")
    notes.extend(normalized.notes)
    condition = normalized.condition
    requirement = normalized.requirement

    condition, requirement = _apply_force_review_defaults(
        test_item=test_item,
        condition=condition,
        requirement=requirement,
        notes=notes,
    )

    extracted_count = sum(1 for value in (method, condition, requirement) if value)
    if extracted_count == 0:
        status = "missing"
    elif extracted_count == 3:
        status = "matched"
    else:
        status = "partial"

    notes.extend(
        note
        for value, note in ((method, "method"), (condition, "condition"), (requirement, "requirement"))
        if value
    )
    return MatrixRowDetailExtraction(
        method=method,
        condition=condition,
        requirement=requirement,
        status=status,
        source_section=section,
        notes=tuple(notes),
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
    matches = list(_EIA_STANDARD_RE.finditer(text))
    if not matches:
        return None
    pick = next((match for match in matches if "1000" not in match.group(1)), matches[0])
    normalized = re.sub(r"\s+", "-", pick.group(1).strip().upper())
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


def _extract_condition(text: str, *, test_item: str | None) -> str | None:
    lowered = (test_item or "").lower()
    if "thermal shock" in lowered:
        return extract_thermal_shock_condition(text)
    if "voltage surge" in lowered:
        return extract_voltage_surge_condition(text)
    llcr_generic = re.search(r"(\d+(?:\.\d+)?\s*mV\s*max\s*,\s*\d+(?:\.\d+)?\s*mA\s*max)", text, re.IGNORECASE)
    if llcr_generic:
        return _clean(llcr_generic.group(1))
    if "low level" in lowered or "llcr" in lowered:
        if llcr_generic:
            return _clean(llcr_generic.group(1))
        return "20 mV, 100 mA"
    if "specified current" in lowered:
        current = re.search(r"(?:test\s+current\s*[-:]?\s*|at\s+)(\d+(?:\.\d+)?\s*(?:ADC|A|amperes?))", text, re.IGNORECASE)
        if current:
            return _clean(current.group(1).replace("amperes", "A"))
    if "dielectric withstanding voltage" in lowered or "dwv" in lowered:
        return _extract_electrical_condition(text, duration_labels=("test duration",))
    if "insulation resistance" in lowered:
        return _extract_electrical_condition(text, duration_labels=("electrification time",))
    if "dust exposure" in lowered:
        return _extract_dust_exposure_condition(text)
    if "current rating" in lowered:
        return _extract_temperature_rise_current(text) or "A"
    if "temperature rise" in lowered or re.search(r"\bt[-\s]?rise\b", lowered):
        return _extract_temperature_rise_current(text) or "A"
    if "humidity" in lowered:
        return _collect_condition_segments(text, ("temperature", "humidity", "rh", "duration", "dwell", "ramp", "cycles"))
    if "mfg" in lowered or "mixed flowing gas" in lowered:
        return extract_mfg_condition(text)
    if "thermal disturbance" in lowered:
        return _collect_condition_segments(text, ("temperature", "range", "ramp", "dwell", "cycles"))
    if "high temperature" in lowered:
        return _collect_condition_segments(text, ("temperature", "duration", "hours"))
    if "durability" in lowered:
        return _extract_durability_condition(text)
    if "offset mating insertion force" in lowered:
        return _extract_offset_mating_condition(text)
    if "floater displacement force" in lowered or "side force" in lowered:
        return _extract_floater_displacement_condition(text)
    if "mating" in lowered and "force" in lowered:
        return _extract_mating_force_condition(text)
    if "terminal extraction force" in lowered:
        return _extract_terminal_extraction_condition(text)
    if "normal force" in lowered:
        return _extract_normal_force_condition(text)
    if _is_force_or_mating_pair(test_item):
        return _extract_force_speed_condition(text)
    if "vibration" in lowered:
        return _collect_condition_segments(text, ("condition", "hz", "grms", "axis", "minutes"))
    if "shock" in lowered:
        return _collect_condition_segments(text, ("50g", "11", "shock", "axis"))
    if not test_item:
        return None
    return _collect_condition_tokens(text)


def _extract_electrical_condition(text: str, *, duration_labels: tuple[str, ...]) -> str | None:
    """Build a DWV or IR condition from explicit voltage and duration labels."""
    voltage = re.search(
        r"\btest\s+voltage\b\s*(?:[:\-–—]|\u6bcf)?\s*"
        r"(?P<value>\d+(?:\.\d+)?)\s*(?:volts?|v)\s*(?P<kind>ac|dc)\b",
        text,
        re.IGNORECASE,
    )
    if voltage is None:
        return None
    voltage_text = f"{voltage.group('value')}V{voltage.group('kind').upper()}"
    labels = "|".join(re.escape(label) for label in duration_labels)
    duration = re.search(
        rf"\b(?:{labels})\b\s*[:\-–—]?\s*"
        r"(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>seconds?|minutes?)\b",
        text,
        re.IGNORECASE,
    )
    if duration is None:
        return voltage_text
    duration_text = f"{duration.group('value')} {duration.group('unit').lower()}"
    return f"{voltage_text}, {duration_text}"


def _extract_temperature_rise_current(text: str) -> str | None:
    """Extract the first current value governing a temperature-rise section."""
    current = re.search(
        r"\b(\d+(?:\.\d+)?)\s*(A|amps?|amperes?)\b",
        text,
        re.IGNORECASE,
    )
    if not current:
        return None
    return f"{current.group(1)}A"


def _extract_dust_exposure_condition(text: str) -> str:
    """Build the report-style dust condition while flagging ambiguous states."""
    composition = re.search(
        r"\bbenign\s+dust\s+composition(?:\s*(?P<number>\d+)\s*#?)?",
        text,
        re.IGNORECASE,
    )
    composition_number = composition.group("number") if composition and composition.group("number") else "1"
    duration = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)\b", text, re.IGNORECASE)
    duration_text = f"{duration.group(1)} hour" if duration else "1 hour"
    prefix = f"Benign dust composition {composition_number}#, {duration_text}"

    lowered = text.lower()
    both_unmated = bool(re.search(r"\bunmated\s+for\s+both\s+connectors?\b", lowered))
    ambiguous_state = bool(
        re.search(r"\bmated\b", lowered)
        or re.search(r"\bunmated\b[^.]*\bonly\b", lowered)
        or re.search(r"\bonly\b[^.]*\b(?:receptacle|connector)\b", lowered)
    )
    if both_unmated or not ambiguous_state:
        return f"{prefix}, unmated for both connectors"
    return prefix


def _extract_durability_condition(text: str) -> str | None:
    """Extract cycle count and a reviewable displacement-speed slot."""
    cycles = re.search(
        r"\b(\d+(?:\.\d+)?)\s*\*?\s*(?:mating\s*/\s*un-?mating\s+)?cycles\b",
        text,
        re.IGNORECASE,
    )
    if not cycles:
        return None
    speed = re.search(r"\b(\d+(?:\.\d+)?)\s*mm\s*/\s*min(?:ute)?\b", text, re.IGNORECASE)
    speed_text = f"{speed.group(1)} mm/min" if speed else " mm/min"
    return f"{cycles.group(1)} cycles, {speed_text}"


def _extract_offset_mating_condition(text: str) -> str | None:
    """Extract offset-position repetitions and displacement speed."""
    repetitions = re.search(r"\b(\d+(?:\.\d+)?)\s*times\b", text, re.IGNORECASE)
    speed = _extract_force_speed_condition(text)
    if not repetitions:
        return speed or "mm/min"
    speed_text = speed or "mm/min"
    return f"{repetitions.group(1)} times, {speed_text}"


def _extract_floater_displacement_condition(text: str) -> str | None:
    """Extract numeric displacement speed for the floater side-force test."""
    return _extract_force_speed_condition(text)


def _extract_mating_force_condition(text: str) -> str | None:
    """Extract numeric cross-head speed for mating-force tests."""
    return _extract_force_speed_condition(text)


def _extract_terminal_extraction_condition(text: str) -> str | None:
    """Extract numeric cross-head speed for terminal extraction tests."""
    return _extract_force_speed_condition(text)


def _extract_force_speed_condition(text: str) -> str | None:
    """Return a normalized numeric displacement or cross-head speed."""
    speed = re.search(
        r"\b(\d+(?:\.\d+)?)\s*(?:±\s*\d+(?:\.\d+)?)?\s*"
        r"mm\s*(?:max\s*)?(?:per\s+minute|/\s*min(?:ute)?)\b",
        text,
        re.IGNORECASE,
    )
    if not speed:
        return None
    return f"{speed.group(1)} mm/min"


def _extract_normal_force_condition(text: str) -> str:
    """Extract normal-force displacement speed or its review placeholder."""
    return _extract_force_speed_condition(text) or "mm/min"


def _apply_force_review_defaults(
    *,
    test_item: str | None,
    condition: str | None,
    requirement: str | None,
    notes: list[str],
) -> tuple[str | None, str | None]:
    """Fill operator-review placeholders for Force and mating/un-mating rows."""
    if not _is_force_or_mating_pair(test_item):
        return condition, requirement
    next_condition = condition or "mm/min"
    next_requirement = requirement or "N"
    if next_condition != condition:
        notes.append("force-default-condition")
    if next_requirement != requirement:
        notes.append("force-default-requirement")
    return next_condition, next_requirement


def _is_force_or_mating_pair(test_item: str | None) -> bool:
    """Match Force labels or labels explicitly naming mating and un-mating."""
    normalized = normalize_test_item(test_item)
    if not normalized:
        return False
    tokens = normalized.split()
    if "force" in tokens:
        return True
    has_mating = any(
        token in {"mate", "mating"} and (index == 0 or tokens[index - 1] != "un")
        for index, token in enumerate(tokens)
    )
    has_unmating = any(token in {"unmate", "unmating"} for token in tokens) or any(
        token == "un" and index + 1 < len(tokens) and tokens[index + 1] in {"mate", "mating"}
        for index, token in enumerate(tokens)
    )
    return has_mating and has_unmating


def _extract_requirement(text: str) -> str | None:
    normal_force = re.search(
        r"\bminimum\s+normal\s+force\s+is\s+not\s+less\s+than\s+"
        r"(?P<value>\d+(?:\.\d+)?)\s*N\s+per\s+beam\b",
        text,
        re.IGNORECASE,
    )
    if normal_force:
        return f"≥ {normal_force.group('value')} N per beam"
    offset_force = re.search(
        r"\boffset\s+mating\s+insertion\s+force\s+is\s+no\s+more\s+than\s+"
        r"(?P<value>\d+(?:\.\d+)?)\s*N\b",
        text,
        re.IGNORECASE,
    )
    if offset_force:
        return f"≤ {offset_force.group('value')} N"
    floater_force = re.search(
        r"\bdisplacement\s+force\s+is\s+not\s+less\s+than\s+"
        r"(?P<lower>\d+(?:\.\d+)?)\s*N\s+and\s+no\s+more\s+than\s+"
        r"(?P<upper>\d+(?:\.\d+)?)\s*N\b",
        text,
        re.IGNORECASE,
    )
    if floater_force:
        return (
            f"{floater_force.group('lower')} N ≤ Displacement Force ≤ "
            f"{floater_force.group('upper')} N"
        )
    terminal_force = re.search(
        r"\bminimum\s+extraction\s+force\b.*?\bis\s+"
        r"(?P<value>\d+(?:\.\d+)?)\s*N\b",
        text,
        re.IGNORECASE,
    )
    if terminal_force:
        return f"≥ {terminal_force.group('value')} N"
    no_discontinuity = _NO_DISCONTINUITY_RE.search(text)
    if no_discontinuity:
        return _clean(no_discontinuity.group(1))
    no_damage = _NO_DAMAGE_RE.search(text)
    if no_damage:
        return _clean(no_damage.group(1))
    max_change = _MAX_CHANGE_RE.search(text)
    if max_change:
        return _clean(max_change.group(1))
    for pattern in _REQUIREMENT_PATTERNS:
        match = pattern.search(text)
        if match:
            return _clean(match.group(1).strip(" ,;"))
    return None


def _collect_condition_segments(text: str, keywords: tuple[str, ...]) -> str | None:
    parts: list[str] = []
    for segment in re.split(r"[.;]", text):
        cleaned = _clean(segment)
        if not cleaned:
            continue
        lowered = cleaned.lower()
        if any(keyword in lowered for keyword in keywords):
            if lowered.startswith("eia ") or "in accordance with eia" in lowered:
                continue
            if "eia 364" in lowered or "eia-364" in lowered:
                continue
            parts.append(cleaned)
    if not parts:
        return None
    return "; ".join(parts[:2])


def _collect_condition_tokens(text: str) -> str | None:
    tokens: list[str] = []
    for match in _CONDITION_TOKEN_RE.finditer(text):
        token = _clean(match.group(1))
        if re.fullmatch(r"\d+\s*a", token.lower()):
            continue
        tokens.append(token)
    if not tokens:
        return None
    unique: list[str] = []
    for token in tokens:
        if token not in unique:
            unique.append(token)
    if len(unique) > 3:
        unique = unique[:3]
    return ", ".join(unique)


def _apply_reseating_default(
    *,
    section: str,
    test_item: str | None,
    method: str | None,
    condition: str | None,
    requirement: str | None,
    applicable_specifications: str | None,
    notes: list[str],
) -> tuple[str | None, str | None, str | None]:
    """Fill missing Reseating row details for section 7.8 only."""
    if section.strip() != "7.8" or normalize_test_item(test_item) != "reseating":
        return method, condition, requirement
    specification = _clean(applicable_specifications or "")
    next_method = method or f"{specification or 'Applicable Specifications'} 7.8"
    next_condition = condition or "Manual 3 cycles"
    next_requirement = requirement or "No damage"
    if next_method != method:
        notes.append("reseating-default-method")
    if next_condition != condition:
        notes.append("reseating-default-condition")
    if next_requirement != requirement:
        notes.append("reseating-default-requirement")
    return next_method, next_condition, next_requirement


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
