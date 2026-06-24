"""Application Form Word COM header LTR helpers."""

from __future__ import annotations

from backend.infrastructure.office.application_form_word_targets import (
    clean_word_text,
    com_clean,
    com_iter,
    iter_com_table_cells,
    normalize_label,
)
from backend.infrastructure.office.models import WordSection2FieldChange


def write_header_ltr_with_com(document: object, value: str) -> WordSection2FieldChange:
    """Write and verify the visible Lab Test Request Number in Word headers."""
    for section_index, section in enumerate(com_iter(document.Sections), start=1):
        for header_index, header in enumerate(com_iter(section.Headers), start=1):
            tables = getattr(getattr(header, "Range", header), "Tables", None)
            if tables is None:
                continue
            for table_index, table in enumerate(com_iter(tables), start=1):
                update = write_header_table_ltr(
                    table,
                    value,
                    f"header[{section_index}:{header_index}].table[{table_index}]",
                )
                if update is not None:
                    return update
    raise ValueError("Application Form header LTR location not found.")


def write_header_table_ltr(
    table: object,
    value: str,
    location_prefix: str,
) -> WordSection2FieldChange | None:
    """Write one header table LTR value if the label exists."""
    for row_index, column_index, cell in iter_com_table_cells(table):
        text = com_clean(getattr(cell.Range, "Text", ""))
        if "lab test request number" not in normalize_label(text):
            continue
        old_value = header_ltr_visible_value(cell)
        if _body_value_matches(old_value, value) and header_ltr_is_normalized(cell, value):
            return WordSection2FieldChange(
                "ltr_number",
                "Lab Test Request Number",
                old_value,
                value,
                f"{location_prefix}.cell[{row_index},{column_index}]",
            )
        replace_header_ltr_value(cell, value)
        visible = header_ltr_visible_value(cell)
        if not _body_value_matches(visible, value):
            raise ValueError(
                "Application Form header LTR read-back mismatch: "
                f"expected {value!r}, got {visible!r}"
            )
        return WordSection2FieldChange(
            "ltr_number",
            "Lab Test Request Number",
            old_value,
            value,
            f"{location_prefix}.cell[{row_index},{column_index}]",
        )
    return None


def replace_header_ltr_value(cell: object, value: str) -> None:
    """Replace the header LTR visible value while preserving page text."""
    paragraphs = com_iter(cell.Range.Paragraphs)
    bounds = header_ltr_bounds(paragraphs)
    if bounds is None:
        raise ValueError("Application Form header LTR safe replacement point not found.")
    label_index, page_index = bounds
    middle = paragraphs[label_index + 1 : page_index]
    non_empty = [
        (index, paragraph)
        for index, paragraph in enumerate(middle, start=label_index + 1)
        if com_clean(getattr(paragraph.Range, "Text", ""))
    ]
    if len(non_empty) > 1:
        raise ValueError("Application Form header LTR value is ambiguous.")
    if middle:
        _replace_ltr_inside_existing_middle(
            paragraphs,
            label_index,
            page_index,
            middle,
            non_empty,
            value,
        )
        remove_blank_paragraphs_after_header_page(cell)
        return
    paragraphs[page_index].Range.InsertBefore(f"\r{value}\r")
    remove_blank_paragraphs_after_header_page(cell)


def _replace_ltr_inside_existing_middle(
    paragraphs: list[object],
    label_index: int,
    page_index: int,
    middle: list[object],
    non_empty: list[tuple[int, object]],
    value: str,
) -> None:
    if non_empty:
        value_index, value_paragraph = non_empty[0]
        before_value = paragraphs[label_index + 1 : value_index]
        if before_value:
            set_paragraph_text(before_value[0], "")
            for paragraph in before_value[1:]:
                if not try_delete_paragraph(paragraph):
                    raise ValueError("Application Form header LTR spacer could not be normalized.")
        else:
            value_paragraph.Range.InsertBefore("\r")
        set_paragraph_text(value_paragraph, value)
        after_value = paragraphs[value_index + 1 : page_index]
    else:
        set_paragraph_text(middle[0], "")
        paragraphs[page_index].Range.InsertBefore(f"{value}\r")
        after_value = middle[1:]
    for paragraph in after_value:
        if not try_delete_paragraph(paragraph):
            raise ValueError("Application Form header LTR value paragraph could not be normalized.")


def header_ltr_visible_value(cell: object) -> str:
    """Return the visible value currently between the LTR label and page text."""
    paragraphs = com_iter(cell.Range.Paragraphs)
    bounds = header_ltr_bounds(paragraphs)
    if bounds is None:
        return ""
    label_index, page_index = bounds
    values = [
        com_clean(getattr(paragraph.Range, "Text", ""))
        for paragraph in paragraphs[label_index + 1 : page_index]
    ]
    non_empty = [value for value in values if value]
    if len(non_empty) != 1:
        return ""
    return clean_word_text(non_empty[0])


def header_ltr_is_normalized(cell: object, value: str) -> bool:
    """Return whether the header LTR cell already has ConnLab's fixed layout."""
    paragraphs = com_iter(cell.Range.Paragraphs)
    bounds = header_ltr_bounds(paragraphs)
    if bounds is None:
        return False
    label_index, page_index = bounds
    middle = paragraphs[label_index + 1 : page_index]
    if (
        len(middle) != 2
        or com_clean(getattr(middle[0].Range, "Text", ""))
        or not _body_value_matches(com_clean(getattr(middle[1].Range, "Text", "")), value)
    ):
        return False
    return not any(
        not com_clean(getattr(paragraph.Range, "Text", ""))
        for paragraph in paragraphs[page_index + 1 :]
    )


def header_ltr_bounds(paragraphs: list[object]) -> tuple[int, int] | None:
    """Return label/page paragraph indexes for the header LTR cell."""
    label_index = None
    for index, paragraph in enumerate(paragraphs):
        normalized = normalize_label(com_clean(getattr(paragraph.Range, "Text", "")))
        if label_index is None and "lab test request number" in normalized:
            label_index = index
            continue
        if label_index is not None and normalized.startswith("page"):
            return label_index, index
    return None


def set_paragraph_text(paragraph: object, value: str) -> None:
    """Replace one Word paragraph text."""
    paragraph.Range.Text = f"{value}\r"


def try_delete_paragraph(paragraph: object) -> bool:
    """Delete a Word paragraph, returning false when Word rejects it."""
    try:
        paragraph.Range.Delete()
    except Exception:
        return False
    return True


def remove_blank_paragraphs_after_header_page(cell: object) -> None:
    """Remove trailing blank paragraphs after the page paragraph."""
    paragraphs = com_iter(cell.Range.Paragraphs)
    bounds = header_ltr_bounds(paragraphs)
    if bounds is None:
        return
    _label_index, page_index = bounds
    for paragraph in paragraphs[page_index + 1 :]:
        if com_clean(getattr(paragraph.Range, "Text", "")):
            continue
        try_delete_paragraph(paragraph)


def _body_value_matches(actual: str, expected: str) -> bool:
    return clean_word_text(actual).casefold() == clean_word_text(expected).casefold()
