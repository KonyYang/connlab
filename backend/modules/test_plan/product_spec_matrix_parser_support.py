"""Support helpers for product specification Matrix parsing."""

from __future__ import annotations

from typing import Any
import re


LETTER_NOTE_RE = re.compile(r"^\s*\(([a-z])\)\s*(.+)\s*$", re.IGNORECASE)
LETTER_NOTE_ALT_PAREN_RE = re.compile(r"^\s*\uff08([a-z])\uff09\s*(.+)\s*$", re.IGNORECASE)
LETTER_NOTE_SUFFIX_DELIM_RE = re.compile(r"^\s*([a-z])[)\.]\s*(.+)\s*$", re.IGNORECASE)
NOTE_WRAPPED_LETTER_RE = re.compile(r"^\s*note\s*\(([a-z])\)\s*:?\s*(.+)\s*$", re.IGNORECASE)
SYMBOL_NOTE_RE = re.compile(r"^\s*([*#])\s*(.+)\s*$")
MARKER_IN_PAREN_RE = re.compile(r"\((?:\d*\s*)?([a-z])\)", re.IGNORECASE)
SYMBOL_MARKER_RE = re.compile(r"([*#])")
NEGATIVE_RECORD_HEADER_RE = re.compile(
    r"\b(result|judg|record|measured|rev|revision|pages|description|date)\b",
    re.IGNORECASE,
)
GROUP_TOKEN_HEADER_RE = re.compile(r"^\s*(?:[A-Za-z]\d+|\d+[A-Za-z]?|[A-Za-z])\s*$")
TEXTUAL_ITEM_RE = re.compile(r"[A-Za-z]{2,}")
PURE_NUMERIC_OR_SYMBOL_RE = re.compile(r"^[\d\W_]+$")
QUALIFICATION_TITLE_RE = re.compile(r"\bqualification\s+test\b", re.IGNORECASE)
REVISION_RECORD_HEADER_TERMS = frozenset({"rev", "revision", "pages", "description", "date"})


def collect_marker_notes(paragraphs: list[str]) -> dict[str, str]:
    """Collect marker notes from the most plausible contiguous note block."""
    note_blocks = [
        *_collect_marker_note_blocks(paragraphs),
        *_collect_backfilled_letter_note_blocks(paragraphs),
    ]
    symbol_notes = _collect_symbol_marker_notes_global(paragraphs)
    if not note_blocks:
        return {**_collect_marker_notes_global(paragraphs), **symbol_notes}
    return {**note_blocks[-1], **symbol_notes}


def extract_marker(token: str | None) -> str | None:
    """Extract a marker key from one token/value."""
    if not token:
        return None
    paren = MARKER_IN_PAREN_RE.search(token)
    if paren:
        return paren.group(1).lower()
    symbol = SYMBOL_MARKER_RE.search(token)
    if symbol:
        return symbol.group(1)
    return None


def row_item_section_note(
    test_item: str | None,
    source_section: str | None,
    marker_notes: dict[str, str],
) -> str | None:
    """Build concise item/section note text from row markers."""
    item_marker = extract_marker(test_item)
    section_marker = extract_marker(source_section)
    if section_marker and section_marker in marker_notes and source_section:
        return f"Section: {source_section} {_note_text_without_marker(marker_notes[section_marker])}".strip()
    if item_marker and item_marker in marker_notes and test_item:
        return f"Test Item: {test_item} {_note_text_without_marker(marker_notes[item_marker])}".strip()
    return None


def table_score(
    *,
    result: Any,
    header: Any,
    table: list[list[str]],
    table_context: str | None,
) -> int:
    """Score one parsed table for matrix likelihood."""
    if not result.groups:
        return 0
    score = 0
    header_row = table[header.row_index - 1] if 0 <= header.row_index - 1 < len(table) else []
    header_text = " ".join(clean(cell) for cell in header_row).lower()
    if "test" in header_text:
        score += 12
    if "group" in header_text:
        score += 15
    if NEGATIVE_RECORD_HEADER_RE.search(header_text):
        score -= 15
    if looks_like_revision_record_table(table):
        return 0
    group_labels = [label for _, label in header.group_columns]
    if group_labels and all(GROUP_TOKEN_HEADER_RE.match(label or "") for label in group_labels):
        score += 12
    non_sample_rows = [row for row in result.rows if not row.is_sample_row]
    if non_sample_rows:
        textual_rows = [
            row
            for row in non_sample_rows
            if TEXTUAL_ITEM_RE.search(row.test_item)
            and not PURE_NUMERIC_OR_SYMBOL_RE.match(row.test_item.strip())
        ]
        ratio = len(textual_rows) / max(1, len(non_sample_rows))
        if ratio >= 0.65:
            score += 16
        elif ratio >= 0.4:
            score += 8
        else:
            score -= 20
        numeric_item_rows = [
            row
            for row in non_sample_rows
            if PURE_NUMERIC_OR_SYMBOL_RE.match(row.test_item.strip())
        ]
        if len(numeric_item_rows) / max(1, len(non_sample_rows)) >= 0.5:
            score -= 35
    if has_sample_tail_row(result.rows):
        score += 10
    if table_context and QUALIFICATION_TITLE_RE.search(table_context):
        score += 20
    group_count = len(result.groups)
    step_count = sum(len(group.steps) for group in result.groups)
    if step_count >= max(2, group_count * 2):
        score += 15
    elif step_count > 0:
        score += 8
    else:
        score -= 20
    return score


def has_sample_tail_row(rows: tuple[Any, ...]) -> bool:
    """Return whether a source row tail contains sample quantity information."""
    if not rows:
        return False
    tail = rows[-3:]
    return any((row.test_item or "").strip().lower().startswith("sample") for row in tail)


def looks_like_revision_record_table(table: list[list[str]]) -> bool:
    """Return true for document revision/history tables, even if cells mention tests."""
    if not table:
        return False
    candidate_rows = table[: min(3, len(table))]
    for row in candidate_rows:
        normalized = {normalize(cell) for cell in row if clean(cell)}
        if "rev" in normalized and {"pages", "description"}.issubset(normalized):
            return True
        if "revision" in normalized and ("description" in normalized or "date" in normalized):
            return True
    leading_text = " ".join(clean(cell) for row in candidate_rows for cell in row).lower()
    term_hits = sum(
        1
        for term in REVISION_RECORD_HEADER_TERMS
        if re.search(rf"\b{re.escape(term)}\b", leading_text)
    )
    return term_hits >= 4


def clean(value: str) -> str:
    """Normalize table cell whitespace."""
    return re.sub(r"\s+", " ", str(value).replace("\x07", " ")).strip()


def normalize(value: str) -> str:
    """Normalize text for header matching."""
    return clean(value).lower()


def _collect_marker_note_blocks(paragraphs: list[str]) -> list[dict[str, str]]:
    blocks: list[dict[str, str]] = []
    current_block: dict[str, str] = {}
    current_marker_count = 0
    for raw in paragraphs:
        text = clean(raw)
        if not text:
            if current_marker_count >= 2:
                blocks.append(current_block)
            current_block = {}
            current_marker_count = 0
            continue
        parsed = _parse_marker_note_line(text)
        if parsed is None:
            if current_marker_count >= 2:
                blocks.append(current_block)
            current_block = {}
            current_marker_count = 0
            continue
        marker, normalized_note = parsed
        current_block[marker] = normalized_note
        current_marker_count += 1
    if current_marker_count >= 2:
        blocks.append(current_block)
    return blocks


def _collect_backfilled_letter_note_blocks(paragraphs: list[str]) -> list[dict[str, str]]:
    blocks: list[dict[str, str]] = []
    cleaned = [clean(raw) for raw in paragraphs]
    for index, text in enumerate(cleaned):
        parsed = _parse_marker_note_line(text)
        if parsed is None:
            continue
        marker, normalized_note = parsed
        if len(marker) != 1 or not marker.isalpha():
            continue
        marker_index = ord(marker.lower()) - ord("a")
        if marker_index <= 0:
            continue
        start = index - marker_index
        if start < 0:
            continue
        previous_lines = cleaned[start:index]
        if len(previous_lines) != marker_index:
            continue
        if any(not line or _parse_marker_note_line(line) is not None for line in previous_lines):
            continue
        if not _looks_like_matrix_note_backfill_context(cleaned, start):
            continue
        block = {
            chr(ord("a") + offset): f"({chr(ord('a') + offset)}) {line.strip()}"
            for offset, line in enumerate(previous_lines)
        }
        block[marker.lower()] = normalized_note
        blocks.append(block)
    return blocks


def _looks_like_matrix_note_backfill_context(paragraphs: list[str], start: int) -> bool:
    context_start = max(0, start - 3)
    context = " ".join(paragraphs[context_start:start]).lower()
    return "table" in context and ("qualification" in context or "test" in context)


def _collect_marker_notes_global(paragraphs: list[str]) -> dict[str, str]:
    notes: dict[str, str] = {}
    for raw in paragraphs:
        parsed = _parse_marker_note_line(clean(raw))
        if parsed is None:
            continue
        marker, normalized_note = parsed
        notes[marker] = normalized_note
    return notes


def _collect_symbol_marker_notes_global(paragraphs: list[str]) -> dict[str, str]:
    notes: dict[str, str] = {}
    for raw in paragraphs:
        text = clean(raw)
        symbol_match = SYMBOL_NOTE_RE.match(text)
        if not symbol_match:
            continue
        marker = symbol_match.group(1)
        notes[marker] = f"{marker} {symbol_match.group(2).strip()}"
    return notes


def _parse_marker_note_line(text: str) -> tuple[str, str] | None:
    letter_match = LETTER_NOTE_RE.match(text)
    if letter_match:
        marker = letter_match.group(1).lower()
        return marker, f"({marker}) {letter_match.group(2).strip()}"
    alt_paren_match = LETTER_NOTE_ALT_PAREN_RE.match(text)
    if alt_paren_match:
        marker = alt_paren_match.group(1).lower()
        return marker, f"({marker}) {alt_paren_match.group(2).strip()}"
    mojibake_match = re.match(r"^\s*锛\S*?([a-z])\S*?\s*(.+)\s*$", text, re.IGNORECASE)
    if mojibake_match:
        marker = mojibake_match.group(1).lower()
        return marker, f"({marker}) {mojibake_match.group(2).strip()}"
    suffix_delim_match = LETTER_NOTE_SUFFIX_DELIM_RE.match(text)
    if suffix_delim_match:
        marker = suffix_delim_match.group(1).lower()
        return marker, f"({marker}) {suffix_delim_match.group(2).strip()}"
    note_wrapped_match = NOTE_WRAPPED_LETTER_RE.match(text)
    if note_wrapped_match:
        marker = note_wrapped_match.group(1).lower()
        return marker, f"({marker}) {note_wrapped_match.group(2).strip()}"
    symbol_match = SYMBOL_NOTE_RE.match(text)
    if symbol_match:
        marker = symbol_match.group(1)
        return marker, f"{marker} {symbol_match.group(2).strip()}"
    return None


def _note_text_without_marker(note: str) -> str:
    text = note.strip()
    text = re.sub(r"^\([a-z]\)\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^[*#]\s*", "", text)
    return text
