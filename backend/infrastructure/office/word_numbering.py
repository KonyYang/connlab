"""Helpers for materializing Word automatic paragraph numbering."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from docx.oxml.ns import qn


@dataclass(frozen=True, slots=True)
class _NumberingLevel:
    start: int
    number_format: str
    level_text: str


def paragraph_texts_with_numbering(document: Any) -> list[str]:
    """Return paragraph texts with supported Word auto-numbering prefixes."""
    definitions = _numbering_definitions(document)
    counters: dict[str, list[int | None]] = {}
    result: list[str] = []
    for paragraph in document.paragraphs:
        text = _clean(paragraph.text)
        label = _paragraph_numbering_label(paragraph, definitions, counters)
        if label and text and not text.startswith(label):
            result.append(f"{label} {text}")
        else:
            result.append(text)
    return result


def _paragraph_numbering_label(
    paragraph: Any,
    definitions: dict[str, dict[int, _NumberingLevel]],
    counters: dict[str, list[int | None]],
) -> str | None:
    num_pr = getattr(getattr(paragraph._p, "pPr", None), "numPr", None)
    if num_pr is None or num_pr.numId is None or num_pr.ilvl is None:
        return None
    num_id = str(num_pr.numId.val)
    ilvl = int(num_pr.ilvl.val)
    levels = definitions.get(num_id)
    if not levels:
        return None
    level = levels.get(ilvl)
    if level is None or level.number_format != "decimal":
        return None

    values = counters.setdefault(num_id, [None] * 9)
    for index in range(ilvl):
        parent = levels.get(index)
        if values[index] is None:
            values[index] = parent.start if parent else 1
    current = values[ilvl]
    values[ilvl] = level.start if current is None else current + 1
    for index in range(ilvl + 1, len(values)):
        values[index] = None
    return _format_level_text(level.level_text, values)


def _numbering_definitions(document: Any) -> dict[str, dict[int, _NumberingLevel]]:
    numbering_part = getattr(document.part, "numbering_part", None)
    if numbering_part is None:
        return {}
    root = numbering_part.element
    abstract_levels = _abstract_levels(root)
    definitions: dict[str, dict[int, _NumberingLevel]] = {}
    for num in root.findall(qn("w:num")):
        num_id = num.get(qn("w:numId"))
        abstract = num.find(qn("w:abstractNumId"))
        abstract_id = abstract.get(qn("w:val")) if abstract is not None else None
        if num_id and abstract_id and abstract_id in abstract_levels:
            definitions[num_id] = abstract_levels[abstract_id]
    return definitions


def _abstract_levels(root: Any) -> dict[str, dict[int, _NumberingLevel]]:
    result: dict[str, dict[int, _NumberingLevel]] = {}
    for abstract in root.findall(qn("w:abstractNum")):
        abstract_id = abstract.get(qn("w:abstractNumId"))
        if not abstract_id:
            continue
        levels: dict[int, _NumberingLevel] = {}
        for level in abstract.findall(qn("w:lvl")):
            ilvl = level.get(qn("w:ilvl"))
            start = _child_value(level, "w:start")
            number_format = _child_value(level, "w:numFmt")
            level_text = _child_value(level, "w:lvlText")
            if ilvl is None or number_format is None or level_text is None:
                continue
            levels[int(ilvl)] = _NumberingLevel(
                start=int(start or "1"),
                number_format=number_format,
                level_text=level_text,
            )
        result[abstract_id] = levels
    return result


def _child_value(element: Any, child_name: str) -> str | None:
    child = element.find(qn(child_name))
    return child.get(qn("w:val")) if child is not None else None


def _format_level_text(level_text: str, values: list[int | None]) -> str | None:
    def replacement(match: re.Match[str]) -> str:
        index = int(match.group(1)) - 1
        value = values[index] if 0 <= index < len(values) else None
        return str(value or 1)

    label = re.sub(r"%([1-9])", replacement, level_text).strip()
    return label or None


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).replace("\x07", " ")).strip()
