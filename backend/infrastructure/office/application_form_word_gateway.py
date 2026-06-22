"""Application Form Word write-back helpers for visible Word form fields."""

from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from backend.infrastructure.office.models import (
    WordSection2FieldChange,
    WordSection2WriteResult,
)
from backend.infrastructure.office.office_lifecycle import OfficeAutomationUnavailable
from backend.infrastructure.office.application_form_word_mapping import (
    APPLICATION_FORM_CRITICAL_FIELDS,
    APPLICATION_FORM_FIELD_LABELS,
    APPLICATION_FORM_NEXT_ROW_FIELDS,
)


def write_application_form_fields_with_com(
    path: Path,
    fields: dict[str, str],
) -> WordSection2WriteResult:
    """Write Application Form fields through Word COM and verify visible values."""
    try:
        import pythoncom  # type: ignore[import-not-found]
        import win32com.client  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - depends on Windows host
        raise OfficeAutomationUnavailable("Word COM automation requires pywin32.") from exc

    pythoncom.CoInitialize()
    word = None
    document = None
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        document = word.Documents.Open(
            str(path.resolve()),
            ReadOnly=False,
            AddToRecentFiles=False,
        )
        changed: list[WordSection2FieldChange] = []
        unchanged: list[WordSection2FieldChange] = []
        warnings: list[str] = []

        ltr_value = _field_value(fields, "ltr_number")
        if ltr_value:
            _append_verified_change(
                _write_header_ltr_with_com(document, ltr_value),
                changed,
                unchanged,
            )

        for field_key, new_value in fields.items():
            if field_key == "ltr_number" or not str(new_value).strip():
                continue
            target = _find_application_form_cell_with_com(document, field_key)
            if target is None:
                _handle_missing_field(field_key, warnings)
                continue
            cell, label, location = target
            old_value = _com_clean(getattr(cell.Range, "Text", ""))
            if _body_value_matches(old_value, str(new_value)):
                unchanged.append(
                    WordSection2FieldChange(field_key, label, old_value, str(new_value), location)
                )
                continue
            write_warning = _write_com_cell_value(cell, str(new_value))
            visible_value = _com_clean(getattr(cell.Range, "Text", ""))
            if write_warning:
                _handle_field_warning(field_key, f"{field_key}: {write_warning}", warnings)
                continue
            if not _body_value_matches(visible_value, str(new_value)):
                _handle_field_warning(
                    field_key,
                    (
                        f"Application Form field read-back mismatch for {field_key}: "
                        f"expected {new_value!r}, got {visible_value!r}"
                    ),
                    warnings,
                )
                continue
            changed.append(
                WordSection2FieldChange(field_key, label, old_value, str(new_value), location)
            )

        if changed:
            document.Save()
        return WordSection2WriteResult(
            changed_fields=tuple(changed),
            unchanged_fields=tuple(unchanged),
            warnings=tuple(warnings),
        )
    finally:
        if document is not None:
            document.Close(SaveChanges=False)
        if word is not None:
            word.Quit()
        pythoncom.CoUninitialize()


def drop_duplicate_application_form_aliases(fields: dict[str, str]) -> None:
    """Remove duplicate alias keys once the canonical write key is present."""
    for canonical, aliases in {
        "requested_by": ("requester",),
        "location": ("manufacturing_site",),
        "project_leader": ("assigned_personnel",),
    }.items():
        if fields.get(canonical):
            for alias in aliases:
                fields.pop(alias, None)


def application_form_requires_com(path: Path) -> bool:
    """Return true when a DOCX contains Word form structures requiring COM."""
    try:
        with ZipFile(path) as package:
            for name in package.namelist():
                if not name.startswith("word/") or not name.endswith(".xml"):
                    continue
                content = package.read(name).decode("utf-8", errors="ignore")
                if "<w:sdt" in content or "<w:ffData" in content:
                    return True
                if name.startswith("word/header") and "Lab Test Request Number" in content:
                    return True
    except (BadZipFile, OSError):
        return False
    return False


def label_matches_aliases(value: str, aliases: tuple[str, ...]) -> bool:
    """Return true when a Word label text exactly matches a known alias."""
    normalized = normalize_label(value)
    return normalized in {normalize_label(alias) for alias in aliases}


def normalize_label(value: str) -> str:
    """Normalize Word labels for deterministic matching."""
    text = clean_word_text(value).lower().rstrip(":")
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def clean_word_text(value: object) -> str:
    """Collapse Word whitespace into a single trimmed string."""
    return re.sub(r"\s+", " ", str(value or "").replace("\x07", " ")).strip()


def _write_header_ltr_with_com(document, value: str) -> WordSection2FieldChange:
    """Write and verify the visible Lab Test Request Number in Word headers."""
    for section_index, section in enumerate(_com_iter(document.Sections), start=1):
        for header_index, header in enumerate(_com_iter(section.Headers), start=1):
            tables = getattr(getattr(header, "Range", header), "Tables", None)
            if tables is None:
                continue
            for table_index, table in enumerate(_com_iter(tables), start=1):
                update = _write_header_table_ltr(
                    table,
                    value,
                    f"header[{section_index}:{header_index}].table[{table_index}]",
                )
                if update is not None:
                    return update
    raise ValueError("Application Form header LTR location not found.")


def _write_header_table_ltr(
    table,
    value: str,
    location_prefix: str,
) -> WordSection2FieldChange | None:
    """Write one header table LTR value if the label exists."""
    for row_index, column_index, cell in _iter_com_table_cells(table):
        text = _com_clean(getattr(cell.Range, "Text", ""))
        if "lab test request number" not in normalize_label(text):
            continue
        old_value = _header_ltr_visible_value(cell)
        if _header_value_matches(text, value):
            return WordSection2FieldChange(
                "ltr_number",
                "Lab Test Request Number",
                old_value,
                value,
                f"{location_prefix}.cell[{row_index},{column_index}]",
            )
        _replace_header_ltr_value(cell, value)
        visible = _com_clean(getattr(cell.Range, "Text", ""))
        if not _header_value_matches(visible, value):
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


def _find_application_form_cell_with_com(document, field_key: str):
    """Find a COM table value cell for one Application Form field."""
    aliases = APPLICATION_FORM_FIELD_LABELS.get(field_key)
    if not aliases:
        return None
    for table_index, table in enumerate(_com_iter(document.Tables), start=1):
        target = _find_table_value_cell(table, field_key, aliases, table_index)
        if target is not None:
            return target
    if field_key in {"location", "manufacturing_site"}:
        return _find_location_cell_from_business_unit_row_with_com(document)
    return None


def _find_table_value_cell(table, field_key: str, aliases: tuple[str, ...], table_index: int):
    """Find one value cell in a specific COM table."""
    for row_index, column_index, cell in _iter_com_table_cells(table):
        label_text = _com_clean(getattr(cell.Range, "Text", ""))
        if not label_matches_aliases(label_text, aliases):
            continue
        target_row = row_index + 1 if field_key in APPLICATION_FORM_NEXT_ROW_FIELDS else row_index
        target_column = column_index if field_key in APPLICATION_FORM_NEXT_ROW_FIELDS else column_index + 1
        target_cell = _com_table_cell(table, target_row, target_column)
        if target_cell is None:
            continue
        return (
            target_cell,
            label_text,
            f"table[{table_index}].cell[{target_row},{target_column}]",
        )
    return None


def _find_location_cell_from_business_unit_row_with_com(document):
    """Find site cell in known templates that omit an explicit Mfg. Site label."""
    for table_index, table in enumerate(_com_iter(document.Tables), start=1):
        if _com_column_count(table) != 6:
            continue
        target = _find_location_in_business_unit_table(table, table_index)
        if target is not None:
            return target
    return None


def _find_location_in_business_unit_table(table, table_index: int):
    """Find the last value cell in the observed Business Unit row shape."""
    if _com_column_count(table) != 6:
        return None
    for row_index, column_index, cell in _iter_com_table_cells(table):
        label_text = _com_clean(getattr(cell.Range, "Text", ""))
        if not label_matches_aliases(label_text, ("business unit", "bu")):
            continue
        row_values: list[tuple[int, object, str]] = []
        for target_column in range(column_index + 1, _com_column_count(table) + 1):
            target_cell = _com_table_cell(table, row_index, target_column)
            if target_cell is None:
                continue
            visible = _com_clean(getattr(target_cell.Range, "Text", ""))
            if visible:
                row_values.append((target_column, target_cell, visible))
        if len(row_values) < 2:
            continue
        target_column, target_cell, _visible = row_values[-1]
        return (
            target_cell,
            "Business Unit row site",
            f"table[{table_index}].cell[{row_index},{target_column}]",
        )
    return None


def _write_com_cell_value(cell, value: str) -> str | None:
    """Write a visible value into a COM Word cell."""
    content_controls = getattr(cell.Range, "ContentControls", None)
    if content_controls is not None and int(getattr(content_controls, "Count", 0) or 0):
        return _write_content_control_value(content_controls.Item(1), value)

    form_fields = getattr(cell.Range, "FormFields", None)
    if form_fields is not None and int(getattr(form_fields, "Count", 0) or 0):
        return _write_form_field_value(form_fields.Item(1), value)

    cell.Range.Text = value
    return None


def _write_content_control_value(control, value: str) -> str | None:
    """Write a value into one Word content control."""
    if bool(getattr(control, "LockContentControl", False)) or bool(
        getattr(control, "LockContents", False)
    ):
        return "Word content control is locked."
    control_type = int(getattr(control, "Type", -1))
    if control_type in {0, 1, 6}:
        control.Range.Text = value
        return None
    if control_type == 3:
        if _select_dropdown_value(control, value):
            return None
        control.Range.Text = value
        return None
    if control_type == 4:
        if _select_dropdown_value(control, value):
            return None
        return f"Dropdown value is not available: {value}"
    if control_type == 8:
        boolean = _to_bool(value)
        if boolean is None:
            return f"Checkbox value is not boolean: {value}"
        control.Checked = boolean
        return None
    return f"Unsupported Word content control type: {control_type}"


def _write_form_field_value(field, value: str) -> str | None:
    """Write a value into one legacy Word form field."""
    field_type = int(getattr(field, "Type", -1))
    if field_type == 70:
        field.Result = value
        return None
    if field_type == 71:
        boolean = _to_bool(value)
        if boolean is None:
            return f"Checkbox value is not boolean: {value}"
        field.CheckBox.Value = boolean
        return None
    return f"Unsupported Word form field type: {field_type}"


def _select_dropdown_value(control, value: str) -> bool:
    """Select a dropdown/combobox entry by visible text."""
    entries = getattr(control, "DropdownListEntries", None)
    if entries is None:
        return False
    expected = normalize_label(value)
    for index in range(1, int(getattr(entries, "Count", 0) or 0) + 1):
        entry = entries.Item(index)
        text = str(getattr(entry, "Text", "") or "")
        if normalize_label(text) == expected:
            entry.Select()
            return True
    return False


def _replace_header_ltr_value(cell, value: str) -> None:
    """Replace the header LTR visible value while preserving page text."""
    paragraphs = _com_iter(cell.Range.Paragraphs)
    label_index = None
    page_index = None
    for index, paragraph in enumerate(paragraphs):
        text = _com_clean(getattr(paragraph.Range, "Text", ""))
        normalized = normalize_label(text)
        if label_index is None and "lab test request number" in normalized:
            label_index = index
            continue
        if label_index is not None and normalized.startswith("page"):
            page_index = index
            break
    if label_index is None or page_index is None:
        raise ValueError("Application Form header LTR safe replacement point not found.")
    for index in range(page_index - 1, label_index, -1):
        paragraphs[index].Range.Delete()
    paragraphs[page_index].Range.InsertBefore(f"{value}\r")


def _header_ltr_visible_value(cell) -> str:
    """Return the visible value currently between the LTR label and page text."""
    values: list[str] = []
    seen_label = False
    for paragraph in _com_iter(cell.Range.Paragraphs):
        text = _com_clean(getattr(paragraph.Range, "Text", ""))
        normalized = normalize_label(text)
        if not text:
            continue
        if "lab test request number" in normalized:
            seen_label = True
            continue
        if seen_label and normalized.startswith("page"):
            break
        if seen_label:
            values.append(text)
    return clean_word_text(" ".join(values))


def _append_verified_change(
    update: WordSection2FieldChange,
    changed: list[WordSection2FieldChange],
    unchanged: list[WordSection2FieldChange],
) -> None:
    """Append a verified update to changed or unchanged collections."""
    if _body_value_matches(update.old_value, update.new_value):
        unchanged.append(update)
    else:
        changed.append(update)


def _handle_missing_field(field_key: str, warnings: list[str]) -> None:
    """Record or raise for a missing mapped field."""
    _handle_field_warning(
        field_key,
        f"Application Form field location not found: {field_key}",
        warnings,
    )


def _handle_field_warning(field_key: str, message: str, warnings: list[str]) -> None:
    """Raise for critical fields and warn for optional fields."""
    if field_key in APPLICATION_FORM_CRITICAL_FIELDS:
        raise ValueError(message)
    warnings.append(message)


def _iter_com_table_cells(table) -> Iterable[tuple[int, int, object]]:
    """Yield available COM table cells while tolerating merged-cell errors."""
    row_count = int(getattr(getattr(table, "Rows", None), "Count", 0) or 0)
    for row_index in range(1, row_count + 1):
        for column_index in range(1, _com_column_count(table) + 1):
            cell = _com_table_cell(table, row_index, column_index)
            if cell is not None:
                yield row_index, column_index, cell


def _com_iter(collection) -> list[object]:
    """Return COM collection items using 1-based indexing."""
    count = int(getattr(collection, "Count", 0))
    return [collection.Item(index) for index in range(1, count + 1)]


def _com_table_cell(table, row: int, column: int):
    """Return a COM table cell or None when Word rejects the coordinate."""
    try:
        return table.Cell(row, column)
    except Exception:
        return None


def _com_column_count(table) -> int:
    """Return a COM table column count or zero when unavailable."""
    return int(getattr(getattr(table, "Columns", None), "Count", 0) or 0)


def _field_value(fields: dict[str, str], *keys: str) -> str:
    """Return the first non-empty field value for any key."""
    for key in keys:
        value = str(fields.get(key, "") or "").strip()
        if value:
            return value
    return ""


def _header_value_matches(actual: str, expected: str) -> bool:
    """Compare header text after extracting mixed label/value text."""
    return clean_word_text(expected).casefold() in clean_word_text(actual).casefold()


def _body_value_matches(actual: str, expected: str) -> bool:
    """Compare body target values exactly after Word whitespace cleanup."""
    return clean_word_text(actual).casefold() == clean_word_text(expected).casefold()


def _com_clean(value: object) -> str:
    """Clean COM Word range text into human-visible text."""
    return clean_word_text(str(value or "").replace("\r", " ").replace("\x07", " "))


def _to_bool(value: str) -> bool | None:
    """Normalize common business boolean text."""
    normalized = normalize_label(value)
    if normalized in {"yes", "y", "true", "1", "checked"}:
        return True
    if normalized in {"no", "n", "false", "0", "unchecked"}:
        return False
    return None
