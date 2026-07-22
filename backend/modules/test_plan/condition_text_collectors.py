"""Pure collectors for source-supported Matrix condition text."""

from __future__ import annotations

import re

_CONDITION_TOKEN_RE = re.compile(
    r"\b(\d+(?:\.\d+)?\s*(?:mV|mA|A|ADC|mm/min|cycles?|hours?|minutes?|mins?|G|ms|RH|℃))\b",
    re.IGNORECASE,
)


def collect_condition_segments(text: str, keywords: tuple[str, ...]) -> str | None:
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


def collect_condition_tokens(text: str) -> str | None:
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


def extract_electrical_condition(
    text: str,
    *,
    duration_labels: tuple[str, ...],
) -> str | None:
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


def extract_temperature_rise_current(text: str) -> str | None:
    """Extract the first current value governing a temperature-rise section."""
    current = re.search(
        r"\b(\d+(?:\.\d+)?)\s*(A|amps?|amperes?)\b",
        text,
        re.IGNORECASE,
    )
    if not current:
        return None
    return f"{current.group(1)}A"


def extract_dust_exposure_condition(text: str) -> str:
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


def extract_durability_condition(text: str) -> str | None:
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


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).replace("\x07", " ")).strip()
