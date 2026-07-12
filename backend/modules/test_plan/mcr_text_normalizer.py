"""Deterministic normalizer for row-level Condition/Requirement text."""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True, slots=True)
class McrNormalizationResult:
    condition: str | None
    requirement: str | None
    notes: tuple[str, ...] = ()


LLCR_TEST_ITEM_ALIASES = {
    "llcr",
    "contact resistance (low level)",
    "contact resistance low level",
    "contact resistance at low level signal",
    "low level contact resistance",
    "low-level contact resistance",
}

CR_TEST_ITEM_ALIASES = {
    "cr",
    "contact resistance",
    "contact resistance power",
}

NO_DAMAGE_REQUIREMENT_FAMILIES = {
    "pre durability",
    "pe durability",
    "durability",
    "durability preconditioning 20 cycles",
    "reseating",
    "thermal shock",
    "cycling temperature and humidity",
    "cycling temperature humidity",
    "cyclic temperature and humidity",
    "cyclic temperature humidity",
    "temperature humidity",
    "high temperature life",
    "pre high temperature life",
    "thermal disturbance",
    "mfg",
    "mixed flowing gas corrosion",
    "dust exposure",
}

NO_DAMAGE_DISCONTINUITY_REQUIREMENT_FAMILIES = {
    "random vibration",
    "vibration random",
    "mechanical shock",
}


def normalize_condition_requirement(
    *,
    test_item: str | None,
    condition: str | None,
    requirement: str | None,
    source_text: str,
) -> McrNormalizationResult:
    """Normalize approved MCR families without changing unsupported text."""
    family = _family(test_item, source_text)
    notes: list[str] = []
    normalized_condition = _normalize_condition(condition)
    if family == "cr" and "specified current" in _normalize_family_label(test_item):
        normalized_condition = _normalize_specified_current_condition(normalized_condition)
    normalized_requirement = _normalize_requirement(requirement)
    normalized_requirement = _normalize_initial_voltage_requirement(
        source_text=source_text,
        current_requirement=normalized_requirement,
    )

    if family in {"llcr", "cr"}:
        resistance = _normalize_resistance_requirement(source_text, normalized_requirement)
        if resistance is not None:
            normalized_requirement = resistance
            notes.append("normalized-resistance-requirement")
    elif family == "insulation_resistance":
        normalized = _normalize_ir_requirement(source_text, normalized_requirement)
        if normalized is not None:
            normalized_requirement = normalized
            notes.append("normalized-ir-requirement")
    elif family == "dwv":
        normalized = _normalize_dwv_requirement(source_text, normalized_requirement)
        if normalized is not None:
            normalized_requirement = normalized
            notes.append("normalized-dwv-requirement")
    elif family == "temperature_rise":
        normalized = _normalize_temperature_requirement(source_text, normalized_requirement)
        if normalized is not None:
            normalized_requirement = normalized
            notes.append("normalized-temperature-requirement")
    elif family == "mating_force":
        normalized = _normalize_mating_unmating_requirement(source_text, normalized_requirement)
        if normalized is not None:
            normalized_requirement = normalized
            notes.append("normalized-mating-unmating-requirement")
    else:
        report_style = _normalize_report_style_family_requirement(test_item)
        if report_style is not None:
            normalized_requirement = report_style
            notes.append("normalized-report-style-requirement")

    return McrNormalizationResult(
        condition=normalized_condition,
        requirement=normalized_requirement,
        notes=tuple(notes),
    )


def _normalize_initial_voltage_requirement(*, source_text: str, current_requirement: str | None) -> str | None:
    text = " ".join(part for part in (current_requirement, source_text) if part)
    if not text:
        return current_requirement
    standardized = _standardize_units(text)
    match = re.search(
        r"(?:shall\s+not\s+exceed|must\s+not\s+exceed|not\s+to\s+exceed|not\s+exceed|"
        r"cannot\s+exceed|max(?:imum)?\.?|<=|≤)\s*"
        r"(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>mV|V)\s*(?:initially|initial)\b",
        standardized,
        re.IGNORECASE,
    )
    if not match:
        return current_requirement
    value_text = match.group("value")
    unit = match.group("unit").upper()
    if unit == "MV":
        return f"Initial ≤ {value_text}mV"
    try:
        value_decimal = Decimal(value_text)
    except InvalidOperation:
        return f"Initial ≤ {value_text}V"
    if value_decimal < Decimal("1"):
        mv_value = value_decimal * Decimal("1000")
        mv_text = format(mv_value.normalize(), "f")
        if "." in mv_text:
            mv_text = mv_text.rstrip("0").rstrip(".")
        if not mv_text:
            mv_text = "0"
        return f"Initial ≤ {mv_text}mV"
    return f"Initial ≤ {value_text}V"


def _normalize_condition(condition: str | None) -> str | None:
    if not condition:
        return None
    return _collapse_ws(_standardize_units(condition))


def _normalize_specified_current_condition(condition: str | None) -> str | None:
    """Use the report convention `ADC` for specified-current conditions."""
    if not condition:
        return None
    return re.sub(
        r"(?P<value>\d+(?:\.\d+)?)\s*(?:amperes?\s+DC|amps?\s+DC|A\s*DC|ADC|A)\b",
        r"\g<value> ADC",
        condition,
        flags=re.IGNORECASE,
    )


def _normalize_requirement(requirement: str | None) -> str | None:
    if not requirement:
        return None
    return _collapse_ws(requirement)


def _normalize_resistance_requirement(source_text: str, current_requirement: str | None) -> str | None:
    text = _standardize_units(" ".join(part for part in (source_text, current_requirement) if part))
    initial_match = re.search(
        r"(?:shall\s+not\s+exceed|must\s+not\s+exceed|<=|≤|max(?:imum)?\.?)\s*"
        r"(?P<value>\d+(?:\.\d+)?)\s*(?:mΩ|mohm|milliohms?)\s*(?:initially|initial)?",
        text,
        re.IGNORECASE,
    )
    delta_match = re.search(
        r"(?:maximum\s+change(?:\s+is)?|change)\s*[:=]?\s*"
        r"(?P<value>\d+(?:\.\d+)?)\s*(?:mΩ|mohm|milliohms?)",
        text,
        re.IGNORECASE,
    )
    if delta_match is None:
        delta_match = re.search(
            r"(?:shall\s+also\s+)?(?:shall\s+not\s+exceed|must\s+not\s+exceed|not\s+exceed|<=|≤)\s*"
            r"(?P<value>\d+(?:\.\d+)?)\s*(?:mΩ|mohm|milliohms?)\s*"
            r"(?:maximum\s+)?change(?:\s+in\s+resistance)?",
            text,
            re.IGNORECASE,
        )
    if delta_match is None:
        delta_match = re.search(
            r"(?P<value>\d+(?:\.\d+)?)\s*(?:mΩ|mohm|milliohms?)\s*"
            r"(?:maximum\s+)?change(?:\s+in\s+resistance)?",
            text,
            re.IGNORECASE,
        )
    if initial_match and delta_match:
        return f"Initial ≤ {initial_match.group('value')} mΩ; ΔR ≤ {delta_match.group('value')} mΩ"
    if initial_match and re.search(r"\binitial(?:ly)?\b", text, re.IGNORECASE):
        return f"Initial ≤ {initial_match.group('value')}mΩ"
    if delta_match:
        return f"ΔR ≤ {delta_match.group('value')} mΩ"

    max_only = re.search(
        r"(?:shall\s+not\s+exceed|must\s+not\s+exceed|<=|≤|max(?:imum)?\.?)\s*"
        r"(?P<value>\d+(?:\.\d+)?)\s*(?:mΩ|mohm|milliohms?)",
        text,
        re.IGNORECASE,
    )
    if max_only:
        return f"≤ {max_only.group('value')}mΩ"
    return current_requirement


def _normalize_temperature_requirement(source_text: str, current_requirement: str | None) -> str | None:
    text = _standardize_units(" ".join(part for part in (current_requirement, source_text) if part))
    match = re.search(
        r"(?:shall\s+not\s+exceed|must\s+not\s+exceed|max(?:imum)?\.?|<=|≤)\s*"
        r"(?P<value>\d+(?:\.\d+)?)\s*(?:℃|deg(?:rees?)?\s*C|C)",
        text,
        re.IGNORECASE,
    )
    if not match:
        return current_requirement
    return f"≤ {match.group('value')} ℃"


def _normalize_mating_unmating_requirement(source_text: str, current_requirement: str | None) -> str | None:
    text = _standardize_units(" ".join(part for part in (source_text, current_requirement) if part))
    mating = re.search(
        r"(?:mating|force\s+to\s+mate|mate)[^.;]*?"
        r"(?:shall\s+not\s+exceed|must\s+not\s+exceed|max(?:imum)?\.?|<=|≤)\s*"
        r"(?P<value>\d+(?:\.\d+)?)\s*N\b",
        text,
        re.IGNORECASE,
    )
    unmating = re.search(
        r"(?:un-?mating|unmating)[^.;]*?"
        r"(?:shall\s+not\s+less\s+than|not\s+less\s+than|min(?:imum)?\.?|>=|≥)\s*"
        r"(?P<value>\d+(?:\.\d+)?)\s*N\b",
        text,
        re.IGNORECASE,
    )
    if mating is None:
        mating = re.search(
            r"(?:mating\s+force|force\s+to\s+mate|mating)[^.;,]*?(?:=|-)?\s*"
            r"(?P<value>\d+(?:\.\d+)?)\s*N\b[^.;,]*?\bmax(?:imum)?\b",
            text,
            re.IGNORECASE,
        )
    if unmating is None:
        unmating = re.search(
            r"(?:un-?mating\s+force|unmating\s+force|un-?mating)[^.;,]*?(?:=|-)?\s*"
            r"(?P<value>\d+(?:\.\d+)?)\s*N\b[^.;,]*?\bmin(?:imum)?\b",
            text,
            re.IGNORECASE,
        )
    if mating and unmating:
        return f"Mating Force ≤ {mating.group('value')} N; Un-mating Force ≥ {unmating.group('value')} N"
    return current_requirement


def _normalize_ir_requirement(source_text: str, current_requirement: str | None) -> str | None:
    text = _standardize_units(" ".join(part for part in (source_text, current_requirement) if part))
    match = re.search(
        r"(?:(?:not\s+(?:be\s+)?less\s+than)|min(?:imum)?|>=|≥)\s*"
        r"(?P<value>\d+(?:\.\d+)?)\s*(?:MΩ|mohm|mega\s*ohms?)",
        text,
        re.IGNORECASE,
    )
    if not match:
        reverse = re.search(
            r"(?P<value>\d+(?:\.\d+)?)\s*(?:MΩ|mohm|mega\s*ohms?)\s*(?:min(?:imum)?|>=|≥)",
            text,
            re.IGNORECASE,
        )
        match = reverse
    if not match:
        return None
    value = Decimal(match.group("value"))
    formatted_mohm = f"{int(value):,}" if value == int(value) else f"{value.normalize():f}"
    if value >= Decimal("1000"):
        gohm = value / Decimal("1000")
        gohm_text = f"{int(gohm)}" if gohm == int(gohm) else f"{gohm.normalize():f}"
        return f"≥{formatted_mohm}MΩ ({gohm_text}GΩ)"
    return f"≥{formatted_mohm}MΩ"


def _normalize_dwv_requirement(source_text: str, current_requirement: str | None) -> str | None:
    text = _standardize_units(" ".join(part for part in (source_text, current_requirement) if part))
    has_no_evidence = bool(
        re.search(r"no\s+evidence\s+of\s+arc[-\s]?over", text, re.IGNORECASE)
        and re.search(r"insulation\s+breakdown", text, re.IGNORECASE)
    )
    leakage = re.search(
        r"leakage\s+current\s*(?P<op>>=|>|<=|<|=|≥|≤)\s*(?P<value>\d+(?:\.\d+)?)\s*(?:mA|A)\b",
        text,
        re.IGNORECASE,
    )
    if not has_no_evidence or leakage is None:
        return current_requirement
    op = leakage.group("op")
    value = leakage.group("value")
    return f"No evidence of arc-over, insulation breakdown, or leakage current {op}{value}mA"


def _normalize_report_style_family_requirement(test_item: str | None) -> str | None:
    normalized = _normalize_family_label(test_item)
    if normalized in NO_DAMAGE_DISCONTINUITY_REQUIREMENT_FAMILIES:
        return "No damage, No discontinuity >1us"
    if normalized in NO_DAMAGE_REQUIREMENT_FAMILIES:
        return "No damage"
    return None


def _family(test_item: str | None, source_text: str) -> str:
    text = _collapse_ws((test_item or "").lower())
    source = _collapse_ws(source_text.lower())
    combined = f"{text} {source}".strip()
    if _is_llcr_family(text=text, combined=combined):
        return "llcr"
    if _is_cr_family(text=text, combined=combined):
        return "cr"
    if "insulation resistance" in combined or re.search(r"\bir\b", combined):
        return "insulation_resistance"
    if "dielectric withstanding voltage" in combined or "dwv" in combined:
        return "dwv"
    if "temperature rise" in combined or "current rating" in combined:
        return "temperature_rise"
    if "mating" in combined and "force" in combined:
        return "mating_force"
    return "other"


def _is_llcr_family(*, text: str, combined: str) -> bool:
    normalized_text = text.replace("-", " ").strip()
    if normalized_text in LLCR_TEST_ITEM_ALIASES:
        return True
    if "llcr" in combined:
        return True
    return "contact resistance" in combined and "low level" in combined


def _is_cr_family(*, text: str, combined: str) -> bool:
    normalized_text = text.replace("-", " ").strip()
    if normalized_text in CR_TEST_ITEM_ALIASES:
        return True
    return "contact resistance" in combined


def _normalize_family_label(test_item: str | None) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", (test_item or "").lower())
    return _collapse_ws(normalized)


def _standardize_units(text: str) -> str:
    normalized = text
    normalized = re.sub(r"\bmilliohms?\b", "mΩ", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bmohms?\b", "mΩ", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bmohm\b", "mΩ", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bmega\s*ohms?\b", "MΩ", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bmegohms?\b", "MΩ", normalized, flags=re.IGNORECASE)
    normalized = normalized.replace("≤", "<=").replace("≥", ">=")
    normalized = normalized.replace("μs", "us").replace("µs", "us")
    normalized = re.sub(r"(?<=\d)\s*[cC]\b", " ℃", normalized)
    normalized = re.sub(r"(?<=\d)\s*(?=[NA]\b)", " ", normalized)
    return normalized


def _collapse_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
