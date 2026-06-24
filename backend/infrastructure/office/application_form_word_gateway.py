"""Application Form Word write-back helpers for visible Word form fields."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from time import perf_counter
from zipfile import BadZipFile, ZipFile

from backend.infrastructure.office.application_form_header_ltr_xml import (
    normalize_header_ltr_layout,
)
from backend.infrastructure.office.application_form_word_session import (
    ApplicationFormWordSession,
)
from backend.infrastructure.office.application_form_word_header import (
    header_ltr_is_normalized as _header_ltr_is_normalized,
    header_ltr_visible_value as _header_ltr_visible_value,
    replace_header_ltr_value as _replace_header_ltr_value,
    write_header_ltr_with_com as _write_header_ltr_with_com,
    write_header_table_ltr as _write_header_table_ltr,
)
from backend.infrastructure.office.models import (
    OfficeTimingSnapshot,
    WordSection2FieldChange,
    WordSection2WriteResult,
)
from backend.infrastructure.office.application_form_word_mapping import (
    APPLICATION_FORM_CRITICAL_FIELDS,
)
from backend.infrastructure.office.application_form_word_targets import (
    ApplicationFormWordTargetIndex,
    clean_word_text,
    com_clean as _com_clean,
    label_matches_aliases,
    normalize_label,
    _find_location_in_business_unit_table as _indexed_location_in_business_unit_table,
)


def write_application_form_fields_with_com(
    path: Path,
    fields: dict[str, str],
    *,
    word_session: ApplicationFormWordSession | None = None,
) -> WordSection2WriteResult:
    """Write Application Form fields through Word COM and verify visible values."""
    gateway_started = perf_counter()
    owns_session = word_session is None
    session = word_session or ApplicationFormWordSession()
    session_entered = False
    document = None
    result: WordSection2WriteResult | None = None
    timings: dict[str, float] = {}
    ltr_value = _field_value(fields, "ltr_number")
    if ltr_value:
        started = perf_counter()
        normalize_header_ltr_layout(path, ltr_value)
        timings["header_xml_pre_normalize"] = perf_counter() - started
    try:
        if owns_session:
            started = perf_counter()
            session.__enter__()
            timings["word_dispatch"] = perf_counter() - started
            session_entered = True
        started = perf_counter()
        document = session.open_document(path)
        timings["document_open"] = perf_counter() - started
        changed: list[WordSection2FieldChange] = []
        unchanged: list[WordSection2FieldChange] = []
        warnings: list[str] = []

        if ltr_value:
            started = perf_counter()
            _append_verified_change(
                _write_header_ltr_with_com(document, ltr_value),
                changed,
                unchanged,
            )
            timings["header_ltr_com_write"] = perf_counter() - started

        field_keys = {key for key, value in fields.items() if key != "ltr_number" and str(value).strip()}
        started = perf_counter()
        target_index = ApplicationFormWordTargetIndex.build(document, field_keys=field_keys)
        timings["target_index_build"] = perf_counter() - started

        started = perf_counter()
        for field_key, new_value in fields.items():
            if field_key == "ltr_number" or not str(new_value).strip():
                continue
            target = target_index.target_for(field_key)
            if target is None:
                _handle_missing_field(field_key, warnings)
                continue
            old_value = target.visible_text()
            if _field_value_matches(field_key, old_value, str(new_value)):
                unchanged.append(
                    WordSection2FieldChange(
                        field_key,
                        target.label,
                        old_value,
                        str(new_value),
                        target.location,
                    )
                )
                continue
            write_warning = _write_com_cell_value(target.cell, str(new_value))
            visible_value = target.visible_text()
            if write_warning:
                _handle_field_warning(field_key, f"{field_key}: {write_warning}", warnings)
                continue
            if not _field_value_matches(field_key, visible_value, str(new_value)):
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
                WordSection2FieldChange(
                    field_key,
                    target.label,
                    old_value,
                    str(new_value),
                    target.location,
                )
            )
        timings["field_write_and_readback"] = perf_counter() - started

        if changed:
            started = perf_counter()
            document.Save()
            timings["document_save"] = perf_counter() - started
        result = WordSection2WriteResult(
            changed_fields=tuple(changed),
            unchanged_fields=tuple(unchanged),
            warnings=tuple(warnings),
            timings=OfficeTimingSnapshot.from_seconds(timings),
        )
    finally:
        close_quit_started = perf_counter()
        close_error: BaseException | None = None
        if document is not None:
            started = perf_counter()
            try:
                session.close_document(document, save=False)
            except BaseException as exc:
                close_error = exc
            finally:
                timings["document_close"] = perf_counter() - started
        if owns_session and session_entered:
            started = perf_counter()
            quit_error: BaseException | None = None
            try:
                session.__exit__(None, None, None)
            except BaseException as exc:
                quit_error = exc
            finally:
                timings["word_quit"] = perf_counter() - started
        if document is not None or (owns_session and session_entered):
            timings["document_close_quit"] = perf_counter() - close_quit_started
        if close_error is not None:
            raise close_error
        if owns_session and session_entered and quit_error is not None:
            raise quit_error
    if ltr_value:
        started = perf_counter()
        normalize_header_ltr_layout(path, ltr_value)
        timings["header_xml_post_normalize"] = perf_counter() - started
    timings["gateway_total"] = perf_counter() - gateway_started
    if result is not None:
        result = WordSection2WriteResult(
            changed_fields=result.changed_fields,
            unchanged_fields=result.unchanged_fields,
            warnings=result.warnings,
            timings=OfficeTimingSnapshot.from_seconds(timings),
        )
    if result is None:  # pragma: no cover - defensive guard
        raise RuntimeError("Application Form Word write-back did not produce a result.")
    return result


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


def _find_location_in_business_unit_table(table, table_index: int):
    """Find the last value cell in the observed Business Unit row shape."""
    target = _indexed_location_in_business_unit_table(table, table_index)
    if target is None:
        return None
    return target.cell, target.label, target.location


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


def _append_verified_change(
    update: WordSection2FieldChange,
    changed: list[WordSection2FieldChange],
    unchanged: list[WordSection2FieldChange],
) -> None:
    if _body_value_matches(update.old_value, update.new_value):
        unchanged.append(update)
    else:
        changed.append(update)


def _handle_missing_field(field_key: str, warnings: list[str]) -> None:
    _handle_field_warning(
        field_key,
        f"Application Form field location not found: {field_key}",
        warnings,
    )


def _handle_field_warning(field_key: str, message: str, warnings: list[str]) -> None:
    if field_key in APPLICATION_FORM_CRITICAL_FIELDS:
        raise ValueError(message)
    warnings.append(message)


def _field_value(fields: dict[str, str], *keys: str) -> str:
    """Return the first non-empty field value for any key."""
    for key in keys:
        value = str(fields.get(key, "") or "").strip()
        if value:
            return value
    return ""


def _header_value_matches(actual: str, expected: str) -> bool:
    return _body_value_matches(actual, expected)


def _field_value_matches(field_key: str, actual: str, expected: str) -> bool:
    """Compare a visible field value, allowing Word date-control display formats."""
    if _body_value_matches(actual, expected):
        return True
    if field_key not in {"received_date", "estimated_completion_date"}:
        return False
    actual_date = _parse_date_value(actual)
    expected_date = _parse_date_value(expected)
    return actual_date is not None and actual_date == expected_date


def _body_value_matches(actual: str, expected: str) -> bool:
    return clean_word_text(actual).casefold() == clean_word_text(expected).casefold()


def _parse_date_value(value: str):
    text = clean_word_text(value)
    for date_format in ("%d %b %Y", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, date_format).date()
        except ValueError:
            continue
    return None


def _to_bool(value: str) -> bool | None:
    """Normalize common business boolean text."""
    normalized = normalize_label(value)
    if normalized in {"yes", "y", "true", "1", "checked"}:
        return True
    if normalized in {"no", "n", "false", "0", "unchecked"}:
        return False
    return None
