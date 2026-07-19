"""Rebuild page-aware text-PDF content into Word-like paragraphs."""

from __future__ import annotations

import re
from dataclasses import dataclass

_SECTION_PATTERN = re.compile(
    r"(?<![\d.])(?P<section>[1-9]\d*(?:\.\d+)+)\s+(?=[A-Za-z])"
)
_REFERENCE_PREFIX_PATTERN = re.compile(
    r"(?:clause|sections?|paragraphs?|paras?|per)\s*$",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class _SectionMatch:
    start: int
    section: str
    key: tuple[int, ...]


def rebuild_pdf_paragraphs(page_texts: list[str]) -> tuple[str, ...]:
    """Return ordered logical paragraphs while retaining cross-page sections."""
    paragraphs: list[str] = []
    active_index: int | None = None
    active_key: tuple[int, ...] | None = None

    for raw_page in page_texts:
        page = clean_pdf_text(raw_page)
        if not page:
            continue
        matches = _accepted_section_matches(raw_page, active_key=active_key)
        if not matches:
            active_index = _append_continuation(
                paragraphs,
                active_index=active_index,
                text=page,
            )
        else:
            prefix = clean_pdf_text(raw_page[: matches[0].start])
            if prefix:
                active_index = _append_continuation(
                    paragraphs,
                    active_index=active_index,
                    text=prefix,
                )
            for index, match in enumerate(matches):
                end = (
                    matches[index + 1].start
                    if index + 1 < len(matches)
                    else len(raw_page)
                )
                paragraph = clean_pdf_text(raw_page[match.start:end])
                if not paragraph:
                    continue
                paragraphs.append(paragraph)
                active_index = len(paragraphs) - 1
                active_key = match.key

        paragraphs.extend(_inline_note_paragraphs(page))

    return tuple(paragraphs)


def split_pdf_page_paragraphs(page_text: str) -> list[str]:
    """Preserve the legacy page-local paragraphs used by table locators."""
    paragraphs: list[str] = []
    for line in (clean_pdf_text(line) for line in page_text.splitlines()):
        if not line:
            continue
        paragraphs.append(line)
        paragraphs.extend(_inline_section_paragraphs(line))
        paragraphs.extend(_inline_note_paragraphs(line))
    return paragraphs


def clean_pdf_text(value: str) -> str:
    """Normalize whitespace and known extraction artifacts."""
    text = " ".join(value.replace("\x00", " ").replace("\u040e\u045e", "、").split())
    return re.sub(r"\bSECTIO\s+N\b", "SECTION", text, flags=re.IGNORECASE)


def _accepted_section_matches(
    text: str,
    *,
    active_key: tuple[int, ...] | None,
) -> list[_SectionMatch]:
    """Return forward section headings that are valid for this page."""
    accepted: list[_SectionMatch] = []
    latest_key = active_key
    for match in _SECTION_PATTERN.finditer(text):
        if _is_inline_candidate_on_multiline_page(text, start=match.start()):
            continue
        if _has_reference_prefix(text, start=match.start()):
            continue
        key = tuple(int(part) for part in match.group("section").split("."))
        if latest_key is not None and key <= latest_key:
            continue
        accepted.append(
            _SectionMatch(
                start=match.start(),
                section=match.group("section"),
                key=key,
            )
        )
        latest_key = key
    return accepted


def _is_inline_candidate_on_multiline_page(text: str, *, start: int) -> bool:
    """Reject inline decimal measurements when page line boundaries exist."""
    if "\n" not in text and "\r" not in text:
        return False
    line_start = max(text.rfind("\n", 0, start), text.rfind("\r", 0, start)) + 1
    return bool(text[line_start:start].strip())


def _has_reference_prefix(text: str, *, start: int) -> bool:
    """Return whether a candidate follows explicit reference language."""
    context = text[max(0, start - 32) : start]
    return _REFERENCE_PREFIX_PATTERN.search(context) is not None


def _append_continuation(
    paragraphs: list[str],
    *,
    active_index: int | None,
    text: str,
) -> int | None:
    """Append page-leading text to the active section or preserve it alone."""
    cleaned = clean_pdf_text(text)
    if not cleaned:
        return active_index
    if active_index is None:
        paragraphs.append(cleaned)
        return None
    paragraphs[active_index] = clean_pdf_text(f"{paragraphs[active_index]} {cleaned}")
    return active_index


def _inline_section_paragraphs(line: str) -> list[str]:
    """Preserve legacy dense-line section splits for locator context."""
    matches = list(_SECTION_PATTERN.finditer(line))
    paragraphs: list[str] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(line)
        paragraph = clean_pdf_text(line[start:end])
        if paragraph:
            paragraphs.append(paragraph)
    return paragraphs


def _inline_note_paragraphs(line: str) -> list[str]:
    """Extract compact marker notes as standalone parser paragraphs."""
    match = re.search(r"\bnotes?\s*:\s*(.+)", line, flags=re.IGNORECASE)
    if not match:
        return []
    note_text = re.split(
        r"\brevision\s+record\b",
        match.group(1),
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    note_matches = list(
        re.finditer(
            r"(?P<marker>[a-z])[\.)]\s*(?P<body>.*?)(?=(?:\s+[a-z][\.)]\s*)|$)",
            note_text,
            flags=re.IGNORECASE,
        )
    )
    paragraphs: list[str] = []
    for item in note_matches:
        body = clean_pdf_text(item.group("body"))
        if body:
            paragraphs.append(f"({item.group('marker').lower()}) {body}")
    return paragraphs
